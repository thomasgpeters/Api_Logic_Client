-- Flight Planner sample: the lookup data - airports and aircraft types. It stays when the sample data
-- is purged (purge_sample.sql). Positions approximate, figures typical: NOT FOR NAVIGATION.

INSERT INTO Airport (Id, Ident, Name, City, Latitude, Longitude, Elevation, RunwayLength, Variation, Fuel, Towered) VALUES
 (1,  'KBED', 'Laurence G. Hanscom Field',        'Bedford, MA',       42.4700, -71.2890,  133,  7011, 15, 1, 1),
 (2,  'KORH', 'Worcester Regional',               'Worcester, MA',     42.2673, -71.8757, 1009,  7001, 15, 1, 1),
 (3,  'KPVD', 'Rhode Island T. F. Green',         'Warwick, RI',       41.7240, -71.4282,   55,  8700, 15, 1, 1),
 (4,  'KHYA', 'Cape Cod Gateway',                 'Hyannis, MA',       41.6693, -70.2804,   54,  5425, 15, 1, 1),
 (5,  'KACK', 'Nantucket Memorial',               'Nantucket, MA',     41.2531, -70.0602,   47,  6000, 15, 1, 1),
 (6,  'KMVY', 'Martha''s Vineyard',               'West Tisbury, MA',  41.3931, -70.6143,   67,  5504, 15, 1, 1),
 (7,  'KPSM', 'Portsmouth International at Pease','Portsmouth, NH',    43.0779, -70.8233,  100, 11321, 16, 1, 1),
 (8,  'KLEB', 'Lebanon Municipal',                'Lebanon, NH',       43.6261, -72.3042,  603,  5496, 15, 1, 1),
 (9,  '1B9',  'Mansfield Municipal',              'Mansfield, MA',     42.0002, -71.1968,  122,  3503, 15, 1, 0),
 (10, '2B2',  'Plum Island',                      'Newburyport, MA',   42.7954, -70.8394,   11,  2105, 16, 0, 0),
 (11, 'KBAF', 'Westfield-Barnes Regional',        'Westfield, MA',     42.1578, -72.7156,  271,  9000, 14, 1, 1);

INSERT INTO AircraftType (Id, Model, CruiseKnots, FuelBurn, UsableFuel, MinRunway) VALUES
 (1, 'Cessna 172S Skyhawk',      120,  8.5, 53, 1700),
 (2, 'Piper PA-28-181 Archer',   125,  9.5, 48, 1800),
 (3, 'Cirrus SR22',              170, 15.0, 81, 2600),
 (4, 'Piper J-3 Cub',             70,  4.5, 12,  900);
