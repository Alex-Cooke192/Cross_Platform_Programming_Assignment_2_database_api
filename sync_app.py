from uuid import uuid4
from datetime import datetime, timezone
from functools import wraps
import sqlite3
import os
from typing import Any, Dict, Optional, List, Tuple
from flask import Flask, jsonify, request


# ----------------------------
# Sync internals
# ----------------------------

API_KEY = "api_warehouse_student_key_1234567890abcdef"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "warehouse.db")

app = Flask(__name__)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = 0")
    connection.row_factory = sqlite3.Row
    return connection


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(row)


def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        header_key = request.headers.get("X-API-Key", "")
        auth_header = request.headers.get("Authorization", "")
        bearer_key = ""
        if auth_header.lower().startswith("bearer "):
            bearer_key = auth_header.split(" ", 1)[1].strip()
        if header_key != API_KEY and bearer_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)

    return wrapper


def _parse_ts(ts: Optional[str]) -> datetime:
    """
    Parse timestamps that may look like:
      - '2026-01-20T12:34:56'
      - '2026-01-20 12:34:56'  (SQLite CURRENT_TIMESTAMP)
      - '2026-01-20T12:34:56Z'
    If parsing fails, return datetime.min (treat as very old).
    """
    if not ts or not isinstance(ts, str):
        return datetime.min
    s = ts.strip().replace("Z", "")
    # sqlite CURRENT_TIMESTAMP uses space - ISO may use 'T'
    if " " in s and "T" not in s:
        s = s.replace(" ", "T", 1)
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return datetime.min


def _now_iso() -> str:
    # Use ISO-ish text; consistent and sortable
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _fetch_row_by_id(table: str, row_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            f"SELECT * FROM {table} WHERE id = ?",
            (row_id,),
        ).fetchone()
    return row_to_dict(row) if row else None


def _fetch_updated_since(table: str, since_ts: Optional[str], limit: int = 5000) -> List[Dict[str, Any]]:
    """
    Return rows updated after `since_ts`. If since_ts is missing, return [] (no pull).
    """
    if not since_ts:
        return []

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT *
            FROM {table}
            WHERE updated_at > ?
            ORDER BY updated_at ASC
            LIMIT ?
            """,
            (since_ts, limit),
        ).fetchall()

    return [row_to_dict(r) for r in rows]


def _mark_conflict(table: str, row_id: str) -> None:
    with get_connection() as connection:
        connection.execute(
            f"""
            UPDATE {table}
            SET sync_status = 'conflict',
                updated_at = ?
            WHERE id = ?
            """,
            (_now_iso(), row_id),
        )


def _upsert_technician(incoming: Dict[str, Any]) -> Tuple[str, str]:
    """
    Returns (result, id) where result in: 'inserted'|'updated'|'skipped'|'conflict'
    Conflict rule: if server.updated_at > client.updated_at => conflict.
    """
    tech_id = incoming.get("id")
    if not tech_id:
        return ("skipped", "")

    server = _fetch_row_by_id("technicians_cache", tech_id)
    client_ts = _parse_ts(incoming.get("updated_at"))

    if server:
        server_ts = _parse_ts(server.get("updated_at"))
        if server_ts > client_ts:
            _mark_conflict("technicians_cache", tech_id)
            return ("conflict", tech_id)

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE technicians_cache
                SET username = ?,
                    display_name = ?,
                    role = ?,
                    updated_at = ?,
                    sync_status = 'synced'
                WHERE id = ?
                """,
                (
                    incoming.get("username", server.get("username")),
                    incoming.get("display_name", server.get("display_name")),
                    incoming.get("role", server.get("role", "technician")),
                    incoming.get("updated_at") or _now_iso(),
                    tech_id,
                ),
            )
        return ("updated", tech_id)

    # insert
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO technicians_cache
                    (id, username, display_name, role, created_at, updated_at, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, 'synced')
                """,
                (
                    tech_id,
                    incoming.get("username"),
                    incoming.get("display_name"),
                    incoming.get("role", "technician"),
                    incoming.get("created_at") or _now_iso(),
                    incoming.get("updated_at") or _now_iso(),
                ),
            )
        return ("inserted", tech_id)
    except sqlite3.IntegrityError:
        # username unique collision etc.
        return ("conflict", tech_id)


def _upsert_inspection(incoming: Dict[str, Any]) -> Tuple[str, str]:
    insp_id = incoming.get("id")
    if not insp_id:
        return ("skipped", "")

    server = _fetch_row_by_id("inspections", insp_id)
    client_ts = _parse_ts(incoming.get("updated_at"))

    if server:
        server_ts = _parse_ts(server.get("updated_at"))
        if server_ts > client_ts:
            _mark_conflict("inspections", insp_id)
            return ("conflict", insp_id)

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE inspections
                SET aircraft_id = ?,
                    status = ?,
                    opened_at = ?,
                    completed_at = ?,
                    technician_id = ?,
                    updated_at = ?,
                    sync_status = 'synced'
                WHERE id = ?
                """,
                (
                    incoming.get("aircraft_id", server.get("aircraft_id")),
                    incoming.get("status", server.get("status")),
                    incoming.get("opened_at", server.get("opened_at")),
                    incoming.get("completed_at", server.get("completed_at")),
                    incoming.get("technician_id", server.get("technician_id")),
                    incoming.get("updated_at") or _now_iso(),
                    insp_id,
                ),
            )
        return ("updated", insp_id)

    # insert
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO inspections
                    (id, aircraft_id, status, opened_at, completed_at, technician_id,
                     created_at, updated_at, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'synced')
                """,
                (
                    insp_id,
                    incoming.get("aircraft_id"),
                    incoming.get("status"),
                    incoming.get("opened_at"),
                    incoming.get("completed_at"),
                    incoming.get("technician_id"),
                    incoming.get("created_at") or _now_iso(),
                    incoming.get("updated_at") or _now_iso(),
                ),
            )
        return ("inserted", insp_id)
    except sqlite3.IntegrityError:
        # FK technician_id missing, invalid status check, etc.
        return ("conflict", insp_id)


def _upsert_task(incoming: Dict[str, Any]) -> Tuple[str, str]:
    task_id = incoming.get("id")
    if not task_id:
        return ("skipped", "")

    server = _fetch_row_by_id("tasks", task_id)
    client_ts = _parse_ts(incoming.get("updated_at"))

    if server:
        server_ts = _parse_ts(server.get("updated_at"))
        if server_ts > client_ts:
            _mark_conflict("tasks", task_id)
            return ("conflict", task_id)

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET inspection_id = ?,
                    title = ?,
                    description = ?,
                    is_complete = ?,
                    result = ?,
                    notes = ?,
                    completed_at = ?,
                    updated_at = ?,
                    sync_status = 'synced'
                WHERE id = ?
                """,
                (
                    incoming.get("inspection_id", server.get("inspection_id")),
                    incoming.get("title", server.get("title")),
                    incoming.get("description", server.get("description")),
                    int(incoming.get("is_complete", server.get("is_complete", 0))),
                    incoming.get("result", server.get("result")),
                    incoming.get("notes", server.get("notes")),
                    incoming.get("completed_at", server.get("completed_at")),
                    incoming.get("updated_at") or _now_iso(),
                    task_id,
                ),
            )
        return ("updated", task_id)

    # insert
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO tasks
                    (id, inspection_id, title, description, is_complete, result, notes, completed_at,
                     created_at, updated_at, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
                """,
                (
                    task_id,
                    incoming.get("inspection_id"),
                    incoming.get("title"),
                    incoming.get("description"),
                    int(incoming.get("is_complete", 0)),
                    incoming.get("result"),
                    incoming.get("notes"),
                    incoming.get("completed_at"),
                    incoming.get("created_at") or _now_iso(),
                    incoming.get("updated_at") or _now_iso(),
                ),
            )
        return ("inserted", task_id)
    except sqlite3.IntegrityError:
        # FK inspection_id missing, etc.
        return ("conflict", task_id)


# ----------------------------
# Sync endpoint: POST /sync/jobs
# ----------------------------

@app.route("/sync/jobs", methods=["POST"])
@require_api_key
def sync_jobs():
    """
    Expected payload (flexible, but recommended):
    {
      "client_id": "device-or-user-id",
      "last_sync_at": "2026-01-19T10:00:00Z",   // optional: used for pulling server changes
      "changes": {
        "technicians_cache": [ {...}, ... ],
        "inspections": [ {...}, ... ],
        "tasks": [ {...}, ... ]
      }
    }

    Response:
    {
      "job_id": "...",
      "server_time": "...",
      "applied": { "technicians_cache": {...}, "inspections": {...}, "tasks": {...} },
      "conflicts": { "technicians_cache": [...], "inspections": [...], "tasks": [...] },
      "server_changes": { "technicians_cache": [...], "inspections": [...], "tasks": [...] }
    }
    """
    payload = request.get_json(silent=True) or {}
    last_sync_at = payload.get("last_sync_at")
    changes = payload.get("changes") or {}

    tech_changes = changes.get("technicians_cache") or []
    insp_changes = changes.get("inspections") or []
    task_changes = changes.get("tasks") or []

    job_id = str(uuid4())
    server_time = _now_iso()

    applied_summary = {
        "technicians_cache": {"inserted": 0, "updated": 0, "skipped": 0, "conflict": 0},
        "inspections": {"inserted": 0, "updated": 0, "skipped": 0, "conflict": 0},
        "tasks": {"inserted": 0, "updated": 0, "skipped": 0, "conflict": 0},
    }

    # NEW: IDs per outcome
    applied_ids = {
        "technicians_cache": {"inserted": [], "updated": [], "skipped": [], "conflict": []},
        "inspections": {"inserted": [], "updated": [], "skipped": [], "conflict": []},
        "tasks": {"inserted": [], "updated": [], "skipped": [], "conflict": []},
    }


    conflicts = {
        "technicians_cache": [],
        "inspections": [],
        "tasks": [],
    }

    # Apply in FK-safe order:
    # technicians -> inspections -> tasks
    for t in tech_changes:
        result, rid = _upsert_technician(t or {})
        applied_summary["technicians_cache"][result] += 1

        if rid:
            applied_ids["technicians_cache"][result].append(rid)

        if result == "conflict" and rid:
            conflicts["technicians_cache"].append(rid)


    for i in insp_changes:
        result, rid = _upsert_inspection(i or {})
        applied_summary["inspections"][result] += 1

        if rid:
            applied_ids["inspections"][result].append(rid)

        if result == "conflict" and rid:
            conflicts["inspections"].append(rid)


    for tk in task_changes:
        result, rid = _upsert_task(tk or {})
        applied_summary["tasks"][result] += 1

        if rid:
            applied_ids["tasks"][result].append(rid)

        if result == "conflict" and rid:
            conflicts["tasks"].append(rid)


    # Pull server-side changes since last_sync_at 
    server_changes = {
        "technicians_cache": _fetch_updated_since("technicians_cache", last_sync_at),
        "inspections": _fetch_updated_since("inspections", last_sync_at),
        "tasks": _fetch_updated_since("tasks", last_sync_at),
    }

    data = request.get_json(silent=True)
    print("RAW JSON:", data)
    print("RAW BODY:", request.data)


    return jsonify(
        {
            "job_id": job_id,
            "server_time": server_time,
            "applied": applied_summary,
            "applied_ids": applied_ids,
            "conflicts": conflicts,
            "server_changes": server_changes,
        }
    ), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)