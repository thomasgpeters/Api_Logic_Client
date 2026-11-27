-- Flight Planner sample: the lookup data - airports, runways, NOTAMs and aircraft types. It stays when the
-- sample data is purged (purge_sample.sql). Positions approximate, figures typical, NOTAMs made up:
-- NOT FOR NAVIGATION.

INSERT INTO Airport (Id, Ident, Name, City, Latitude, Longitude, Elevation, Variation, Airspace, Fuel, Towered) VALUES
 (1,  'KBED', 'Laurence G. Hanscom Field',         'Bedford, MA',      42.4700, -71.2890,  133, 15, 'D', 1, 1),
 (2,  'KORH', 'Worcester Regional',                'Worcester, MA',    42.2673, -71.8757, 1009, 15, 'D', 1, 1),
 (3,  'KPVD', 'Rhode Island T. F. Green',          'Warwick, RI',      41.7240, -71.4282,   55, 15, 'C', 1, 1),
 (4,  'KHYA', 'Cape Cod Gateway',                  'Hyannis, MA',      41.6693, -70.2804,   54, 15, 'D', 1, 1),
 (5,  'KACK', 'Nantucket Memorial',                'Nantucket, MA',    41.2531, -70.0602,   47, 15, 'D', 1, 1),
 (6,  'KMVY', 'Martha''s Vineyard',                'West Tisbury, MA', 41.3931, -70.6143,   67, 15, 'D', 1, 1),
 (7,  'KPSM', 'Portsmouth International at Pease', 'Portsmouth, NH',   43.0779, -70.8233,  100, 16, 'D', 1, 1),
 (8,  'KLEB', 'Lebanon Municipal',                 'Lebanon, NH',      43.6261, -72.3042,  603, 15, 'D', 1, 1),
 (9,  '1B9',  'Mansfield Municipal',               'Mansfield, MA',    42.0002, -71.1968,  122, 15, 'G', 1, 0),
 (10, '2B2',  'Plum Island',                       'Newburyport, MA',  42.7954, -70.8394,   11, 16, 'G', 0, 0),
 (11, 'KBAF', 'Westfield-Barnes Regional',         'Westfield, MA',    42.1578, -72.7156,  271, 14, 'D', 1, 1),
 (12, 'KBOS', 'General Edward Lawrence Logan',     'Boston, MA',       42.3656, -71.0096,   20, 15, 'B', 1, 1);

INSERT INTO Runway (Id, AirportId, Ident, Heading, Length, Surface) VALUES
 (1, 1, '11', 110, 7011, 'Asphalt'), (2, 1, '29', 290, 7011, 'Asphalt'), (3, 1, '05', 50, 5107, 'Asphalt'), (4, 1, '23', 230, 5107, 'Asphalt'),
 (5, 2, '11', 110, 7001, 'Asphalt'), (6, 2, '29', 290, 7001, 'Asphalt'),
 (7, 3, '05', 50, 8700, 'Asphalt'), (8, 3, '23', 230, 8700, 'Asphalt'), (9, 3, '16', 160, 6081, 'Asphalt'), (10, 3, '34', 340, 6081, 'Asphalt'),
 (11, 4, '06', 60, 5252, 'Asphalt'), (12, 4, '24', 240, 5252, 'Asphalt'), (13, 4, '15', 150, 5425, 'Asphalt'), (14, 4, '33', 330, 5425, 'Asphalt'),
 (15, 5, '06', 60, 6303, 'Asphalt'), (16, 5, '24', 240, 6303, 'Asphalt'),
 (17, 6, '06', 60, 5504, 'Asphalt'), (18, 6, '24', 240, 5504, 'Asphalt'), (19, 6, '15', 150, 3297, 'Asphalt'), (20, 6, '33', 330, 3297, 'Asphalt'),
 (21, 7, '16', 160, 11321, 'Asphalt'), (22, 7, '34', 340, 11321, 'Asphalt'),
 (23, 8, '18', 180, 5496, 'Asphalt'), (24, 8, '36', 360, 5496, 'Asphalt'),
 (25, 9, '14', 140, 3503, 'Asphalt'), (26, 9, '32', 320, 3503, 'Asphalt'),
 (27, 10, '10', 100, 2105, 'Turf'), (28, 10, '28', 280, 2105, 'Turf'),
 (29, 11, '15', 150, 5000, 'Asphalt'), (30, 11, '33', 330, 5000, 'Asphalt'), (31, 11, '02', 20, 9000, 'Asphalt'), (32, 11, '20', 200, 9000, 'Asphalt'),
 (33, 12, '04R', 40, 10005, 'Asphalt'), (34, 12, '22L', 220, 10005, 'Asphalt');

INSERT INTO Notam (Id, AirportId, Number, Kind, Text, Active) VALUES
 (1, 11, '11/112', 'C', 'AD AP CLSD - air show', 1),
 (2, 7,  '11/087', 'O', 'OBST CRANE 1 NM SE OF AP, 280 FT AGL', 1),
 (3, 6,  '10/044', 'C', 'AD AP CLSD - runway works (cancelled)', 0);

INSERT INTO AircraftType (Id, Model, IcaoType, CruiseKnots, FuelBurn, UsableFuel, MaxCrosswind, TakeoffDistance, LandingDistance, TaxiFuel, ClimbFuel) VALUES
 (1, 'Cessna 172S Skyhawk',    'C172', 120,  8.5, 53, 15, 1630, 1335, 1.1, 1.5),
 (2, 'Piper PA-28-181 Archer', 'P28A', 125,  9.5, 48, 17, 1625, 1390, 1.0, 1.5),
 (3, 'Cirrus SR22',            'SR22', 170, 15.0, 81, 21, 1600, 2300, 1.5, 3.0),
 (4, 'Piper J-3 Cub',          'J3',    70,  4.5, 12, 10,  730,  885, 0.3, 0.5);
