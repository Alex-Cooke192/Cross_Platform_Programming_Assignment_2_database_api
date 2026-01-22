#!/usr/bin/env python3
"""
run_central_api.py

Initialises schema, runs the central DB seeder,
then starts the API.
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

# ---- paths ----
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "warehouse.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

# ---- import your existing seeder ----
from seed_central_db import seed  # ← THIS is the key line


def init_db() -> None:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError("schema.sql not found")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)


def run_api() -> int:
    env = os.environ.copy()
    env["WAREHOUSE_DB_PATH"] = str(DB_PATH)

    return subprocess.call([sys.executable, "sync_app.py"], env=env)

def reset_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Deleted {DB_PATH}")

def main() -> int:
    print("Resetting database...")
    reset_db()
    
    print("Initialising database schema...")
    init_db()

    print("Seeding database...")
    seed()  # ← calls YOUR seeder

    print("Starting API...")
    return run_api()


if __name__ == "__main__":
    raise SystemExit(main())
