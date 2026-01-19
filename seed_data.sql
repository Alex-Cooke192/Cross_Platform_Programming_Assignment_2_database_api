-- Technician
INSERT INTO technicians_cache (id, username, display_name, role, sync_status)
VALUES ('00000000-0000-0000-0000-000000000001', 'jay', 'Jay', 'admin', 'synced');

-- Inspection
INSERT INTO inspections (id, aircraft_id, status, opened_at, technician_id, sync_status)
VALUES (
  '11111111-1111-1111-1111-111111111111',
  'G-ABCD',
  'in_progress',
  CURRENT_TIMESTAMP,
  '00000000-0000-0000-0000-000000000001',
  'synced'
);

-- Tasks
INSERT INTO tasks (id, inspection_id, title, description, is_complete, sync_status)
VALUES
('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'Check tyres', 'Inspect tyre wear and pressure', 0, 'synced'),
('33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', 'Check lights', 'Verify nav/landing lights operational', 0, 'synced');
