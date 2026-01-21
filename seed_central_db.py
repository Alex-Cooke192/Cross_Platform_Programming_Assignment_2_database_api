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
        cur.execute("DELETE FROM tasks;")
        cur.execute("DELETE FROM inspections;")
        cur.execute("DELETE FROM technicians_cache;")
        conn.commit()

    # Use "now" so changes will be pulled by clients using last_sync_at
    now = datetime.now(timezone.utc).replace(microsecond=0)
    created_at = now_iso_z(now)
    updated_at = created_at

    # ---- Technicians ----
    tech_names = ["tech.jane", "tech.ali", "tech.sam", "tech.rory", "tech.mina"]
    tech_ids: list[str] = []

    for name in tech_names:
        tid = str(uuid4())
        tech_ids.append(tid)
        cur.execute(
            """
            INSERT INTO technicians_cache (id, name, created_at, updated_at, sync_status)
            VALUES (?, ?, ?, ?, 'synced')
            """,
            (tid, name, created_at, updated_at),
        )

    # ---- Inspections ----
    seeded_inspections = [
        ("G-ABCD", None, None, 0, "outstanding"),
        ("G-EFGH", None, None, 0, "outstanding"),
        ("G-IJKL", now - timedelta(hours=6), None, 0, "in_progress"),
        ("G-MNOP", now - timedelta(hours=4), None, 0, "in_progress"),
        ("G-QRST", now - timedelta(hours=2), None, 0, "in_progress"),
        ("G-UVWX", now - timedelta(days=1, hours=3), now - timedelta(days=1, hours=1), 1, "completed"),
        ("G-YZ12", now - timedelta(days=2, hours=5), now - timedelta(days=2, hours=2), 1, "completed"),
    ]

    inspection_ids: list[str] = []
    for i, (aircraft_id, opened_at_dt, completed_at_dt, is_completed, status) in enumerate(seeded_inspections):
        iid = str(uuid4())
        inspection_ids.append(iid)

        technician_id = tech_ids[i % len(tech_ids)]
        opened_at = None if opened_at_dt is None else now_iso_z(opened_at_dt)
        completed_at = None if completed_at_dt is None else now_iso_z(completed_at_dt)

        # Send sync status to local 
        cur.execute(
            """
            INSERT INTO inspections (
              id, aircraft_id, status, opened_at, completed_at,
              technician_id, created_at, updated_at, sync_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'synced')
            """,
            (iid, aircraft_id, status, opened_at, completed_at, technician_id, created_at, updated_at),
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
        is_completed = 1 if seeded_inspections[i][3] == 1 else 0

        for _ in range(tasks_for_this):
            title = task_pool[task_cursor % len(task_pool)]
            task_cursor += 1
            cur.execute(
                """
                INSERT INTO tasks (
                  id, inspection_id, title, is_completed, result, notes,
                  created_at, updated_at, sync_status
                )
                VALUES (?, ?, ?, ?, NULL, NULL, ?, ?, 'synced')
                """,
                (str(uuid4()), iid, title, is_completed, created_at, updated_at),
            )

    conn.commit()

    tech_count = cur.execute("SELECT COUNT(*) FROM technicians_cache").fetchone()[0]
    insp_count = cur.execute("SELECT COUNT(*) FROM inspections").fetchone()[0]
    task_count = cur.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    print(f"Done. technicians_cache={tech_count}, inspections={insp_count}, tasks={task_count}")

    conn.close()


if __name__ == "__main__":
    seed()
