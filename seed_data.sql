-- =========================
-- Seed data (SQLite)
-- 5 technicians, 20 inspections, 2-4 tasks each
-- =========================

BEGIN TRANSACTION;

-- -------------------------
-- Technicians
-- -------------------------
INSERT INTO technicians_cache (id, username, display_name, role, sync_status) VALUES
('00000000-0000-0000-0000-000000000001', 'tech.jay',   'Jay',   'admin',      'synced'),
('00000000-0000-0000-0000-000000000002', 'tech.sara',  'Sara',  'technician', 'synced'),
('00000000-0000-0000-0000-000000000003', 'tech.liam',  'Liam',  'technician', 'synced'),
('00000000-0000-0000-0000-000000000004', 'tech.emma',  'Emma',  'technician', 'synced'),
('00000000-0000-0000-0000-000000000005', 'tech.noah',  'Noah',  'technician', 'synced');

-- -------------------------
-- Inspections (20) across the 5 technicians
-- -------------------------
INSERT INTO inspections (id, aircraft_id, status, opened_at, technician_id, sync_status) VALUES
('11111111-1111-1111-1111-111111111101', 'G-AB01', 'in_progress', datetime('now','-19 hours'), '00000000-0000-0000-0000-000000000001', 'synced'),
('11111111-1111-1111-1111-111111111102', 'G-AB02', 'open',        datetime('now','-18 hours'), '00000000-0000-0000-0000-000000000002', 'synced'),
('11111111-1111-1111-1111-111111111103', 'G-AB03', 'completed',   datetime('now','-17 hours'), '00000000-0000-0000-0000-000000000003', 'synced'),
('11111111-1111-1111-1111-111111111104', 'G-AB04', 'open',        datetime('now','-16 hours'), '00000000-0000-0000-0000-000000000004', 'synced'),
('11111111-1111-1111-1111-111111111105', 'G-AB05', 'in_progress', datetime('now','-15 hours'), '00000000-0000-0000-0000-000000000005', 'synced'),

('11111111-1111-1111-1111-111111111106', 'G-AB06', 'completed',   datetime('now','-14 hours'), '00000000-0000-0000-0000-000000000001', 'synced'),
('11111111-1111-1111-1111-111111111107', 'G-AB07', 'open',        datetime('now','-13 hours'), '00000000-0000-0000-0000-000000000002', 'synced'),
('11111111-1111-1111-1111-111111111108', 'G-AB08', 'in_progress', datetime('now','-12 hours'), '00000000-0000-0000-0000-000000000003', 'synced'),
('11111111-1111-1111-1111-111111111109', 'G-AB09', 'completed',   datetime('now','-11 hours'), '00000000-0000-0000-0000-000000000004', 'synced'),
('11111111-1111-1111-1111-111111111110', 'G-AB10', 'open',        datetime('now','-10 hours'), '00000000-0000-0000-0000-000000000005', 'synced'),

('11111111-1111-1111-1111-111111111111', 'G-AB11', 'in_progress', datetime('now','-9 hours'),  '00000000-0000-0000-0000-000000000001', 'synced'),
('11111111-1111-1111-1111-111111111112', 'G-AB12', 'completed',   datetime('now','-8 hours'),  '00000000-0000-0000-0000-000000000002', 'synced'),
('11111111-1111-1111-1111-111111111113', 'G-AB13', 'open',        datetime('now','-7 hours'),  '00000000-0000-0000-0000-000000000003', 'synced'),
('11111111-1111-1111-1111-111111111114', 'G-AB14', 'in_progress', datetime('now','-6 hours'),  '00000000-0000-0000-0000-000000000004', 'synced'),
('11111111-1111-1111-1111-111111111115', 'G-AB15', 'completed',   datetime('now','-5 hours'),  '00000000-0000-0000-0000-000000000005', 'synced'),

('11111111-1111-1111-1111-111111111116', 'G-AB16', 'open',        datetime('now','-4 hours'),  '00000000-0000-0000-0000-000000000001', 'synced'),
('11111111-1111-1111-1111-111111111117', 'G-AB17', 'in_progress', datetime('now','-3 hours'),  '00000000-0000-0000-0000-000000000002', 'synced'),
('11111111-1111-1111-1111-111111111118', 'G-AB18', 'completed',   datetime('now','-2 hours'),  '00000000-0000-0000-0000-000000000003', 'synced'),
('11111111-1111-1111-1111-111111111119', 'G-AB19', 'open',        datetime('now','-90 minutes'),'00000000-0000-0000-0000-000000000004', 'synced'),
('11111111-1111-1111-1111-111111111120', 'G-AB20', 'in_progress', datetime('now','-30 minutes'),'00000000-0000-0000-0000-000000000005', 'synced');

-- -------------------------
-- Tasks (2–4 per inspection)
-- -------------------------
INSERT INTO tasks (id, inspection_id, title, description, is_complete, sync_status) VALUES
-- Inspection 101 (3 tasks)
('22222222-2222-2222-2222-222222222101', '11111111-1111-1111-1111-111111111101', 'Check tyres',        'Inspect tyre wear and pressure',                         0, 'synced'),
('22222222-2222-2222-2222-222222222102', '11111111-1111-1111-1111-111111111101', 'Check lights',       'Verify nav/landing lights operational',                  0, 'synced'),
('22222222-2222-2222-2222-222222222103', '11111111-1111-1111-1111-111111111101', 'Fluid leaks',        'Inspect for hydraulic/fuel/oil leaks around bays',        0, 'synced'),

-- Inspection 102 (2 tasks)
('22222222-2222-2222-2222-222222222104', '11111111-1111-1111-1111-111111111102', 'Walkaround',         'General exterior condition check',                       0, 'synced'),
('22222222-2222-2222-2222-222222222105', '11111111-1111-1111-1111-111111111102', 'Pitot/static',       'Check pitot cover removed; inspect ports for blockage',  0, 'synced'),

-- Inspection 103 (4 tasks)
('22222222-2222-2222-2222-222222222106', '11111111-1111-1111-1111-111111111103', 'Battery status',     'Check voltage and secure mounting',                      1, 'synced'),
('22222222-2222-2222-2222-222222222107', '11111111-1111-1111-1111-111111111103', 'Oil level',          'Verify oil quantity within limits',                      1, 'synced'),
('22222222-2222-2222-2222-222222222108', '11111111-1111-1111-1111-111111111103', 'Brake wear',         'Inspect pads/discs and brake line condition',             1, 'synced'),
('22222222-2222-2222-2222-222222222109', '11111111-1111-1111-1111-111111111103', 'Control surfaces',   'Check free movement and security of hinges',             1, 'synced'),

-- Inspection 104 (3 tasks)
('22222222-2222-2222-2222-222222222110', '11111111-1111-1111-1111-111111111104', 'Cabin safety',       'Check belts, seats, and emergency equipment',            0, 'synced'),
('22222222-2222-2222-2222-222222222111', '11111111-1111-1111-1111-111111111104', 'Avionics power-up',  'Verify no faults on power-up test',                      0, 'synced'),
('22222222-2222-2222-2222-222222222112', '11111111-1111-1111-1111-111111111104', 'Compass card',       'Check compass deviation card present/legible',           0, 'synced'),

-- Inspection 105 (2 tasks)
('22222222-2222-2222-2222-222222222113', '11111111-1111-1111-1111-111111111105', 'Fuel caps',          'Inspect caps/seals and ensure secure fit',               0, 'synced'),
('22222222-2222-2222-2222-222222222114', '11111111-1111-1111-1111-111111111105', 'Propeller',          'Inspect for nicks, cracks, and leading edge damage',     0, 'synced'),

-- Inspection 106 (4 tasks)
('22222222-2222-2222-2222-222222222115', '11111111-1111-1111-1111-111111111106', 'ELT check',          'Confirm ELT armed; inspect mounting and antenna',        1, 'synced'),
('22222222-2222-2222-2222-222222222116', '11111111-1111-1111-1111-111111111106', 'Fire extinguisher',  'Check gauge in green and in-date inspection tag',        1, 'synced'),
('22222222-2222-2222-2222-222222222117', '11111111-1111-1111-1111-111111111106', 'Tyre tread depth',   'Measure tread depth and record',                         1, 'synced'),
('22222222-2222-2222-2222-222222222118', '11111111-1111-1111-1111-111111111106', 'Landing gear',       'Inspect struts and linkages for damage/corrosion',       1, 'synced'),

-- Inspection 107 (3 tasks)
('22222222-2222-2222-2222-222222222119', '11111111-1111-1111-1111-111111111107', 'Documents',          'Verify ARC/insurance/logbook availability',              0, 'synced'),
('22222222-2222-2222-2222-222222222120', '11111111-1111-1111-1111-111111111107', 'Radio check',        'Transmit/receive test on primary frequency',             0, 'synced'),
('22222222-2222-2222-2222-222222222121', '11111111-1111-1111-1111-111111111107', 'Transponder',        'Mode S/ALT function test',                                0, 'synced'),

-- Inspection 108 (2 tasks)
('22222222-2222-2222-2222-222222222122', '11111111-1111-1111-1111-111111111108', 'Windshield',         'Inspect for cracks, chips, and seal condition',          0, 'synced'),
('22222222-2222-2222-2222-222222222123', '11111111-1111-1111-1111-111111111108', 'Static wick',        'Inspect wicks and bonding straps',                       0, 'synced'),

-- Inspection 109 (4 tasks)
('22222222-2222-2222-2222-222222222124', '11111111-1111-1111-1111-111111111109', 'Seat rails',         'Inspect rail wear and locking pins',                     1, 'synced'),
('22222222-2222-2222-2222-222222222125', '11111111-1111-1111-1111-111111111109', 'Flap operation',     'Cycle flaps; check symmetry and noises',                 1, 'synced'),
('22222222-2222-2222-2222-222222222126', '11111111-1111-1111-1111-111111111109', 'Engine mount',       'Inspect mount and bushings for cracks',                  1, 'synced'),
('22222222-2222-2222-2222-222222222127', '11111111-1111-1111-1111-111111111109', 'Alternator output',  'Verify charging rate within spec',                       1, 'synced'),

-- Inspection 110 (2 tasks)
('22222222-2222-2222-2222-222222222128', '11111111-1111-1111-1111-111111111110', 'Strobes',            'Verify strobe lights operational',                        0, 'synced'),
('22222222-2222-2222-2222-222222222129', '11111111-1111-1111-1111-111111111110', 'Fuel drain',         'Drain sumps; check for water/contamination',             0, 'synced'),

-- Inspection 111 (3 tasks)
('22222222-2222-2222-2222-222222222130', '11111111-1111-1111-1111-111111111111', 'Oil filter',         'Inspect filter for debris; record findings',             0, 'synced'),
('22222222-2222-2222-2222-222222222131', '11111111-1111-1111-1111-111111111111', 'Magneto check',      'Run-up check; verify rpm drop within limits',            0, 'synced'),
('22222222-2222-2222-2222-222222222132', '11111111-1111-1111-1111-111111111111', 'Cooling baffles',    'Inspect baffles and seals for gaps/tears',               0, 'synced'),

-- Inspection 112 (4 tasks)
('22222222-2222-2222-2222-222222222133', '11111111-1111-1111-1111-111111111112', 'Vacuum system',      'Check suction and lines for leaks',                      1, 'synced'),
('22222222-2222-2222-2222-222222222134', '11111111-1111-1111-1111-111111111112', 'Altimeter',          'Verify calibration sticker and function',                1, 'synced'),
('22222222-2222-2222-2222-222222222135', '11111111-1111-1111-1111-111111111112', 'ADF/VOR',            'Run receiver self-test (if installed)',                  1, 'synced'),
('22222222-2222-2222-2222-222222222136', '11111111-1111-1111-1111-111111111112', 'Cabin lights',       'Check internal lighting and dimmer operation',           1, 'synced'),

-- Inspection 113 (2 tasks)
('22222222-2222-2222-2222-222222222137', '11111111-1111-1111-1111-111111111113', 'Door latches',       'Inspect latch function and seals',                       0, 'synced'),
('22222222-2222-2222-2222-222222222138', '11111111-1111-1111-1111-111111111113', 'Emergency exits',    'Verify markings and operation (if applicable)',          0, 'synced'),

-- Inspection 114 (3 tasks)
('22222222-2222-2222-2222-222222222139', '11111111-1111-1111-1111-111111111114', 'Fuel selector',      'Check operation and detents',                            0, 'synced'),
('22222222-2222-2222-2222-222222222140', '11111111-1111-1111-1111-111111111114', 'Mixture control',    'Verify smooth travel and full range',                    0, 'synced'),
('22222222-2222-2222-2222-222222222141', '11111111-1111-1111-1111-111111111114', 'Throttle cable',     'Inspect cable routing and security',                     0, 'synced'),

-- Inspection 115 (4 tasks)
('22222222-2222-2222-2222-222222222142', '11111111-1111-1111-1111-111111111115', 'Aileron hinges',     'Inspect hinges and safetying',                           1, 'synced'),
('22222222-2222-2222-2222-222222222143', '11111111-1111-1111-1111-111111111115', 'Rudder pedals',      'Inspect linkages and pedal condition',                   1, 'synced'),
('22222222-2222-2222-2222-222222222144', '11111111-1111-1111-1111-111111111115', 'Trim system',        'Check trim wheel and indicator',                         1, 'synced'),
('22222222-2222-2222-2222-222222222145', '11111111-1111-1111-1111-111111111115', 'Beacon',             'Verify rotating/strobe beacon operation',                1, 'synced'),

-- Inspection 116 (2 tasks)
('22222222-2222-2222-2222-222222222146', '11111111-1111-1111-1111-111111111116', 'Anti-collision',     'Verify anti-collision system operational',               0, 'synced'),
('22222222-2222-2222-2222-222222222147', '11111111-1111-1111-1111-111111111116', 'Fuel quantity',      'Cross-check gauges vs. known quantity',                  0, 'synced'),

-- Inspection 117 (3 tasks)
('22222222-2222-2222-2222-222222222148', '11111111-1111-1111-1111-111111111117', 'Nose wheel',         'Inspect shimmy damper and tyre condition',               0, 'synced'),
('22222222-2222-2222-2222-222222222149', '11111111-1111-1111-1111-111111111117', 'Parking brake',      'Verify holds pressure and releases cleanly',             0, 'synced'),
('22222222-2222-2222-2222-222222222150', '11111111-1111-1111-1111-111111111117', 'Horn/annunciators',  'Verify warning lights and annunciators',                 0, 'synced'),

-- Inspection 118 (2 tasks)
('22222222-2222-2222-2222-222222222151', '11111111-1111-1111-1111-111111111118', 'GPS database',       'Verify database current or note out-of-date',            1, 'synced'),
('22222222-2222-2222-2222-222222222152', '11111111-1111-1111-1111-111111111118', 'Headset jacks',      'Check audio jacks and intercom clarity',                 1, 'synced'),

-- Inspection 119 (4 tasks)
('22222222-2222-2222-2222-222222222153', '11111111-1111-1111-1111-111111111119', 'Wing inspection',    'Check leading edge, rivets, and paint condition',        0, 'synced'),
('22222222-2222-2222-2222-222222222154', '11111111-1111-1111-1111-111111111119', 'Fuel vents',         'Inspect vent lines and openings for blockage',           0, 'synced'),
('22222222-2222-2222-2222-222222222155', '11111111-1111-1111-1111-111111111119', 'Exhaust',            'Inspect exhaust for cracks/soot trails',                 0, 'synced'),
('22222222-2222-2222-2222-222222222156', '11111111-1111-1111-1111-111111111119', 'Cowling fasteners',  'Verify cowling secure and fasteners serviceable',        0, 'synced'),

-- Inspection 120 (3 tasks)
('22222222-2222-2222-2222-222222222157', '11111111-1111-1111-1111-111111111120', 'Final walkaround',   'Repeat exterior check before release',                   0, 'synced'),
('22222222-2222-2222-2222-222222222158', '11111111-1111-1111-1111-111111111120', 'Paperwork sign-off', 'Record findings and technician sign-off',                0, 'synced'),
('22222222-2222-2222-2222-222222222159', '11111111-1111-1111-1111-111111111120', 'Clean-up',           'Remove tools/FOD; ensure aircraft left tidy',            0, 'synced');

COMMIT;
