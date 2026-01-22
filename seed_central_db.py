# seed_central_db.py
import os
import sqlite3
from uuid import uuid4
from datetime import datetime, timezone, timedelta

DB_FILENAME = "warehouse.db"
WIPE_FIRST = False  # set True to clear tables before seeding


def now_iso_z(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    dt = dt.replace(microsecond=0)
    return dt.isoformat().replace("+00:00", "Z")


def db_path() -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, DB_FILENAME)


def connect() -> sqlite3.Connection:
    path = db_path()
    print("Seeding DB:", path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def seed() -> None:
    conn = connect()
    cur = conn.cursor()

    if WIPE_FIRST:
        # Order matters due to FKs (tasks -> inspections -> technicians_cache)
        cur.execute("DELETE FROM tasks;")
        cur.execute("DELETE FROM inspections;")
        cur.execute("DELETE FROM technicians_cache;")
        conn.commit()

    # Use "now" so changes will be pulled by clients using last_sync_at
    now = datetime.now(timezone.utc).replace(microsecond=0)
    created_at = now_iso_z(now)
    updated_at = created_at

    # ---- Technicians ----
    tech_usernames = ["tech.jane", "tech.ali", "tech.sam", "tech.rory", "tech.mina"]

    for username in tech_usernames:
        tid = str(uuid4())

        display_name = username.replace("tech.", "").capitalize()

        cur.execute(
            """
            INSERT OR IGNORE INTO technicians_cache (
            id, username, display_name, role,
            created_at, updated_at, sync_status
            )
            VALUES (?, ?, ?, 'technician', ?, ?, 'synced')
            """,
            (tid, username, display_name, created_at, updated_at),
        )

    # IMPORTANT: fetch real IDs (source of truth) so FKs never break
    placeholders = ",".join("?" for _ in tech_usernames)
    rows = cur.execute(
        f"SELECT id FROM technicians_cache WHERE username IN ({placeholders}) ORDER BY username",
        tech_usernames,
    ).fetchall()

    tech_ids = [r["id"] for r in rows]

    if len(tech_ids) != len(tech_usernames):
        raise RuntimeError(
            f"Expected {len(tech_usernames)} technicians, found {len(tech_ids)}. "
            "Check seeding or existing DB state."
        )


    # ---- Inspections ----
    # Schema has no "status" column; derive status locally from opened_at/completed_at.
    seeded_inspections = [
        ("G-ABCD", None, None, 0),  # outstanding
        ("G-EFGH", None, None, 0),  # outstanding
        ("G-IJKL", now - timedelta(hours=6), None, 0),  # in_progress
        ("G-MNOP", now - timedelta(hours=4), None, 0),  # in_progress
        ("G-QRST", now - timedelta(hours=2), None, 0),  # in_progress
        ("G-UVWX", now - timedelta(days=1, hours=3), now - timedelta(days=1, hours=1), 1),  # completed
        ("G-YZ12", now - timedelta(days=2, hours=5), now - timedelta(days=2, hours=2), 1),  # completed
    ]

    inspection_ids: list[str] = []
    for i, (aircraft_id, opened_at_dt, completed_at_dt, is_completed) in enumerate(seeded_inspections):
        iid = str(uuid4())
        inspection_ids.append(iid)

        technician_id = tech_ids[i % len(tech_ids)]
        opened_at = None if opened_at_dt is None else now_iso_z(opened_at_dt)
        completed_at = None if completed_at_dt is None else now_iso_z(completed_at_dt)

        cur.execute(
            """
            INSERT INTO inspections (
              id, aircraft_id, opened_at, completed_at,
              technician_id, created_at, updated_at, sync_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'synced')
            """,
            (iid, aircraft_id, opened_at, completed_at, technician_id, created_at, updated_at),
        )

    # ---- Tasks ----
    task_pool = [
        "Check brakes",
        "Check lights",
        "Inspect tires",
        "Check oil level",
        "Inspect flaps",
        "Test radios",
        "Verify instruments",
        "Check hydraulics",
        "Inspect landing gear",
        "Check battery",
        "Inspect fuel lines",
        "Check cabin safety kit",
    ]

    task_cursor = 0
    for i, iid in enumerate(inspection_ids):
        tasks_for_this = 3 if i < 3 else 2
        inspection_is_completed = 1 if seeded_inspections[i][3] == 1 else 0

        for _ in range(tasks_for_this):
            title = task_pool[task_cursor % len(task_pool)]
            task_cursor += 1

            # If the inspection is completed, mark tasks complete and set completed_at.
            # Otherwise leave them incomplete.
            is_complete = inspection_is_completed
            task_completed_at = created_at if is_complete == 1 else None

            cur.execute(
                """
                INSERT INTO tasks (
                  id, inspection_id, title, description,
                  is_complete, result, notes, completed_at,
                  created_at, updated_at, sync_status
                )
                VALUES (?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, 'synced')
                """,
                (
                    str(uuid4()),
                    iid,
                    title,
                    None,               # description (optional)
                    is_complete,
                    task_completed_at,
                    created_at,
                    updated_at,
                ),
            )

    conn.commit()

    tech_count = cur.execute("SELECT COUNT(*) FROM technicians_cache").fetchone()[0]
    insp_count = cur.execute("SELECT COUNT(*) FROM inspections").fetchone()[0]
    task_count = cur.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    print(f"Done. technicians_cache={tech_count}, inspections={insp_count}, tasks={task_count}")

    conn.close()


if __name__ == "__main__":
    seed()
