PRAGMA foreign_keys = ON;

-- Local-style: UUID primary keys stored as TEXT
-- Sync metadata: updated_at + sync_status
-- Timestamps stored as ISO-8601 TEXT

CREATE TABLE IF NOT EXISTS technicians_cache (
    id TEXT PRIMARY KEY,                 -- UUID (matches client)
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'technician',

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- sync metadata
    sync_status TEXT NOT NULL DEFAULT 'synced',
    CHECK (sync_status IN ('synced', 'pending', 'conflict'))
);

CREATE TABLE IF NOT EXISTS inspections (
    id TEXT PRIMARY KEY,                 -- UUID
    aircraft_id TEXT NOT NULL,           -- e.g. 'G-ABCD'
    opened_at TEXT,                      -- when inspection started
    completed_at TEXT,                   -- when inspection finished

    technician_id TEXT,                  -- who opened/owns it (optional)
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- sync metadata
    sync_status TEXT NOT NULL DEFAULT 'synced',
    CHECK (sync_status IN ('synced', 'pending', 'conflict')),
    FOREIGN KEY (technician_id) REFERENCES technicians_cache(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,                 -- UUID
    inspection_id TEXT NOT NULL,         -- FK to inspections
    title TEXT NOT NULL,
    description TEXT,
    is_complete INTEGER NOT NULL DEFAULT 0, -- 0/1
    result TEXT,                         -- what you entered in UI
    notes TEXT,                          -- additional notes
    completed_at TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- sync metadata
    sync_status TEXT NOT NULL DEFAULT 'synced',
    CHECK (is_complete IN (0, 1)),
    CHECK (sync_status IN ('synced', 'pending', 'conflict')),
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tasks_inspection_id ON tasks(inspection_id);
CREATE INDEX IF NOT EXISTS idx_tasks_complete ON tasks(is_complete);

-- Attachments (1 attachment per task)
-- Stores metadata + server storage key/path (NOT raw bytes)

CREATE TABLE IF NOT EXISTS attachments (
    id TEXT PRIMARY KEY,                 -- UUID (matches client attachment id)
    task_id TEXT NOT NULL UNIQUE,         -- enforce max-1 attachment per task

    file_name TEXT NOT NULL,              -- original name from client
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,

    sha256 TEXT,                          -- optional (if you compute it)
    remote_key TEXT NOT NULL,             -- where the blob is stored on server (path/key)

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- sync metadata (optional for central, but keeps model consistent)
    sync_status TEXT NOT NULL DEFAULT 'synced',
    CHECK (sync_status IN ('synced', 'pending', 'conflict')),

    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_attachments_task_id ON attachments(task_id);
CREATE INDEX IF NOT EXISTS idx_attachments_remote_key ON attachments(remote_key);
