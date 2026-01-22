from functools import wraps
import sqlite3
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

API_KEY = "api_warehouse_student_key_1234567890abcdef"
DB_PATH = "warehouse.db"

app = Flask(__name__)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
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


# ============================================================
# NEW: CRUD for technicians_cache, inspections, tasks (UUID TEXT)
# ============================================================

# ----------------------------
# Technicians Cache helpers
# ----------------------------

def fetch_technician_by_id(tech_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, username, display_name, role, created_at, updated_at, sync_status
            FROM technicians_cache
            WHERE id = ?
            """,
            (tech_id,),
        ).fetchone()
    return row_to_dict(row) if row else None


@app.route("/api/v1/techniciansCache", methods=["GET"])
@require_api_key
def list_technicians_cache():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, username, display_name, role, created_at, updated_at, sync_status
            FROM technicians_cache
            ORDER BY username
            """
        ).fetchall()
    return jsonify([row_to_dict(row) for row in rows]), 200


@app.route("/api/v1/techniciansCache", methods=["POST"])
@require_api_key
def create_technicians_cache():
    payload = request.get_json(silent=True) or {}
    tech_id = payload.get("id")  # UUID TEXT (client-generated)
    username = payload.get("username")
    display_name = payload.get("display_name")
    role = payload.get("role", "technician")
    sync_status = payload.get("sync_status", "synced")

    if not tech_id or not username:
        return jsonify({"error": "id and username are required"}), 400

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO technicians_cache
                    (id, username, display_name, role, created_at, updated_at, sync_status)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
                """,
                (tech_id, username, display_name, role, sync_status),
            )
    except sqlite3.IntegrityError as e:
        # likely username unique conflict or id conflict
        return jsonify({"error": "technician already exists or username already exists"}), 409

    return jsonify(fetch_technician_by_id(tech_id)), 201


@app.route("/api/v1/techniciansCache/<string:tech_id>", methods=["GET"])
@require_api_key
def get_technicians_cache(tech_id: str):
    tech = fetch_technician_by_id(tech_id)
    if not tech:
        return jsonify({"error": "technician not found"}), 404
    return jsonify(tech), 200


@app.route("/api/v1/techniciansCache/<string:tech_id>", methods=["PUT"])
@require_api_key
def update_technicians_cache(tech_id: str):
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    display_name = payload.get("display_name")
    role = payload.get("role")
    sync_status = payload.get("sync_status")

    if not any([username, display_name is not None, role, sync_status]):
        return jsonify({"error": "no fields to update"}), 400

    updates = []
    values = []

    if username:
        updates.append("username = ?")
        values.append(username)
    if display_name is not None:
        updates.append("display_name = ?")
        values.append(display_name)
    if role:
        updates.append("role = ?")
        values.append(role)
    if sync_status:
        updates.append("sync_status = ?")
        values.append(sync_status)

    updates.append("updated_at = CURRENT_TIMESTAMP")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                f"UPDATE technicians_cache SET {', '.join(updates)} WHERE id = ?",
                (*values, tech_id),
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "technician not found"}), 404
    except sqlite3.IntegrityError:
        return jsonify({"error": "username already exists"}), 409

    return jsonify(fetch_technician_by_id(tech_id)), 200


@app.route("/api/v1/techniciansCache/<string:tech_id>", methods=["DELETE"])
@require_api_key
def delete_technicians_cache(tech_id: str):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM technicians_cache WHERE id = ?",
            (tech_id,),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "technician not found"}), 404
    return "", 204


# ----------------------------
# Inspections helpers
# ----------------------------

def fetch_inspection_by_id(inspection_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, aircraft_id, status, opened_at, completed_at,
                   technician_id, created_at, updated_at, sync_status
            FROM inspections
            WHERE id = ?
            """,
            (inspection_id,),
        ).fetchone()
    return row_to_dict(row) if row else None


@app.route("/api/v1/inspections", methods=["GET"])
@require_api_key
def list_inspections():
    # Optional filters: ?status=outstanding|in_progress|completed  and/or ?technician_id=<uuid>
    status = request.args.get("status")
    technician_id = request.args.get("technician_id")

    where = []
    values = []

    if status:
        where.append("status = ?")
        values.append(status)
    if technician_id:
        where.append("technician_id = ?")
        values.append(technician_id)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT id, aircraft_id, status, opened_at, completed_at,
                   technician_id, created_at, updated_at, sync_status
            FROM inspections
            {where_sql}
            ORDER BY updated_at DESC
            """,
            tuple(values),
        ).fetchall()

    return jsonify([row_to_dict(row) for row in rows]), 200


@app.route("/api/v1/inspections", methods=["POST"])
@require_api_key
def create_inspection():
    payload = request.get_json(silent=True) or {}
    inspection_id = payload.get("id")  # UUID TEXT (client-generated)
    aircraft_id = payload.get("aircraft_id")
    status = payload.get("status")
    opened_at = payload.get("opened_at")
    completed_at = payload.get("completed_at")
    technician_id = payload.get("technician_id")
    sync_status = payload.get("sync_status", "synced")

    if not inspection_id or not aircraft_id or not status:
        return jsonify({"error": "id, aircraft_id, and status are required"}), 400

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO inspections
                    (id, aircraft_id, status, opened_at, completed_at, technician_id,
                     created_at, updated_at, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
                """,
                (inspection_id, aircraft_id, status, opened_at, completed_at, technician_id, sync_status),
            )
    except sqlite3.IntegrityError as e:
        # Could be id conflict, status check fail, or technician FK fail
        return jsonify({"error": "invalid data or inspection already exists"}), 409

    return jsonify(fetch_inspection_by_id(inspection_id)), 201


@app.route("/api/v1/inspections/<string:inspection_id>", methods=["GET"])
@require_api_key
def get_inspection(inspection_id: str):
    inspection = fetch_inspection_by_id(inspection_id)
    if not inspection:
        return jsonify({"error": "inspection not found"}), 404
    return jsonify(inspection), 200


@app.route("/api/v1/inspections/<string:inspection_id>", methods=["PUT"])
@require_api_key
def update_inspection(inspection_id: str):
    payload = request.get_json(silent=True) or {}
    aircraft_id = payload.get("aircraft_id")
    status = payload.get("status")
    opened_at = payload.get("opened_at")
    completed_at = payload.get("completed_at")
    technician_id = payload.get("technician_id")
    sync_status = payload.get("sync_status")

    if not any([
        aircraft_id,
        status,
        opened_at is not None,
        completed_at is not None,
        technician_id is not None,
        sync_status,
    ]):
        return jsonify({"error": "no fields to update"}), 400

    updates = []
    values = []

    if aircraft_id:
        updates.append("aircraft_id = ?")
        values.append(aircraft_id)
    if status:
        updates.append("status = ?")
        values.append(status)
    if opened_at is not None:
        updates.append("opened_at = ?")
        values.append(opened_at)
    if completed_at is not None:
        updates.append("completed_at = ?")
        values.append(completed_at)
    if technician_id is not None:
        updates.append("technician_id = ?")
        values.append(technician_id)
    if sync_status:
        updates.append("sync_status = ?")
        values.append(sync_status)

    updates.append("updated_at = CURRENT_TIMESTAMP")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                f"UPDATE inspections SET {', '.join(updates)} WHERE id = ?",
                (*values, inspection_id),
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "inspection not found"}), 404
    except sqlite3.IntegrityError:
        # status check / FK technician check
        return jsonify({"error": "invalid data"}), 400

    return jsonify(fetch_inspection_by_id(inspection_id)), 200


@app.route("/api/v1/inspections/<string:inspection_id>", methods=["DELETE"])
@require_api_key
def delete_inspection(inspection_id: str):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM inspections WHERE id = ?",
            (inspection_id,),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "inspection not found"}), 404
    return "", 204


# ----------------------------
# Tasks helpers
# ----------------------------

def fetch_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, inspection_id, title, description, is_complete,
                   result, notes, completed_at, created_at, updated_at, sync_status
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()
    return row_to_dict(row) if row else None


@app.route("/api/v1/tasks", methods=["GET"])
@require_api_key
def list_tasks():
    # Optional filters: ?inspection_id=<uuid> and/or ?is_complete=0|1
    inspection_id = request.args.get("inspection_id")
    is_complete = request.args.get("is_complete")

    where = []
    values = []

    if inspection_id:
        where.append("inspection_id = ?")
        values.append(inspection_id)
    if is_complete is not None:
        where.append("is_complete = ?")
        values.append(is_complete)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT id, inspection_id, title, description, is_complete,
                   result, notes, completed_at, created_at, updated_at, sync_status
            FROM tasks
            {where_sql}
            ORDER BY updated_at DESC
            """,
            tuple(values),
        ).fetchall()

    return jsonify([row_to_dict(row) for row in rows]), 200


@app.route("/api/v1/tasks", methods=["POST"])
@require_api_key
def create_task():
    payload = request.get_json(silent=True) or {}
    task_id = payload.get("id")  # UUID TEXT (client-generated)
    inspection_id = payload.get("inspection_id")
    title = payload.get("title")
    description = payload.get("description")
    is_complete = payload.get("is_complete", 0)
    result = payload.get("result")
    notes = payload.get("notes")
    completed_at = payload.get("completed_at")
    sync_status = payload.get("sync_status", "synced")

    if not task_id or not inspection_id or not title:
        return jsonify({"error": "id, inspection_id, and title are required"}), 400

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO tasks
                    (id, inspection_id, title, description, is_complete,
                     result, notes, completed_at, created_at, updated_at, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
                """,
                (task_id, inspection_id, title, description, int(is_complete), result, notes, completed_at, sync_status),
            )
    except sqlite3.IntegrityError:
        # FK inspection_id missing or check fail
        return jsonify({"error": "invalid data or task already exists"}), 409

    return jsonify(fetch_task_by_id(task_id)), 201


@app.route("/api/v1/tasks/<string:task_id>", methods=["GET"])
@require_api_key
def get_task(task_id: str):
    task = fetch_task_by_id(task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404
    return jsonify(task), 200


@app.route("/api/v1/tasks/<string:task_id>", methods=["PUT"])
@require_api_key
def update_task(task_id: str):
    payload = request.get_json(silent=True) or {}
    inspection_id = payload.get("inspection_id")
    title = payload.get("title")
    description = payload.get("description")
    is_complete = payload.get("is_complete")
    result = payload.get("result")
    notes = payload.get("notes")
    completed_at = payload.get("completed_at")
    sync_status = payload.get("sync_status")

    if not any([
        inspection_id,
        title,
        description is not None,
        is_complete is not None,
        result is not None,
        notes is not None,
        completed_at is not None,
        sync_status,
    ]):
        return jsonify({"error": "no fields to update"}), 400

    updates = []
    values = []

    if inspection_id:
        updates.append("inspection_id = ?")
        values.append(inspection_id)
    if title:
        updates.append("title = ?")
        values.append(title)
    if description is not None:
        updates.append("description = ?")
        values.append(description)
    if is_complete is not None:
        updates.append("is_complete = ?")
        values.append(int(is_complete))
    if result is not None:
        updates.append("result = ?")
        values.append(result)
    if notes is not None:
        updates.append("notes = ?")
        values.append(notes)
    if completed_at is not None:
        updates.append("completed_at = ?")
        values.append(completed_at)
    if sync_status:
        updates.append("sync_status = ?")
        values.append(sync_status)

    updates.append("updated_at = CURRENT_TIMESTAMP")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
                (*values, task_id),
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "task not found"}), 404
    except sqlite3.IntegrityError:
        return jsonify({"error": "invalid data"}), 400

    return jsonify(fetch_task_by_id(task_id)), 200


@app.route("/api/v1/tasks/<string:task_id>", methods=["DELETE"])
@require_api_key
def delete_task(task_id: str):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "task not found"}), 404
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
