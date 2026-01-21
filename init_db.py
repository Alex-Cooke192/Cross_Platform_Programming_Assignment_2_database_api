from pathlib import Path
import sqlite3

from seed_central_db import seed  # we'll change seed() to accept a path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "warehouse.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def init_db() -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)


if __name__ == "__main__":
    init_db()
    seed(DB_PATH)  # always seed the SAME db file
    print(f"Initialized + seeded database at {DB_PATH}")
