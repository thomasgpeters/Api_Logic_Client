-- Flight Planner sample: the demo scenario - pilots and their logbooks, aircraft and their loading
-- stations, the day's weather, flight plans (legs, loads, endorsements) and position reports.
-- purge_sample.sql removes it and keeps airports, runways, NOTAMs and aircraft types. "Today" is 2026-11-26.
-- Plans go in as drafts, get their legs and loads, then move on to their status (filed, active, closed),
-- one step at a time, as in the app.

INSERT INTO Pilot (Id, Name, Certificate, Phone, BirthDate, MedicalClass, MedicalExam, BasicMedCourse, BasicMedExam, FlightReview, AsOf) VALUES
 (1, 'Maria Santos',  'P', '781-555-0142', '1985-04-12', 3, '2023-06-15', NULL, NULL, '2025-09-10', '2026-11-26'),  -- current for everything
 (2, 'Dev Patel',     'C', '617-555-0177', '1970-02-02', 2, '2025-03-20', NULL, NULL, '2025-01-15', '2026-11-26'),  -- night landings last July
 (3, 'Hannah Becker', 'P', '401-555-0123', '1978-08-30', 3, '2024-11-05', NULL, NULL, '2025-06-01', '2026-11-26'),  -- 46 at the exam: 24 months, to 30 November
 (4, 'Tom Okafor',    'S', '508-555-0190', '2004-05-20', 3, '2025-09-01', NULL, NULL, NULL,         '2026-11-26'),  -- a student pilot
 (5, 'Ray Moreau',    'P', '401-555-0168', '1958-03-03', 3, '2015-05-01', '2025-08-01', '2024-02-10', '2026-02-01', '2026-11-26');  -- BasicMed

INSERT INTO LogbookEntry (Id, PilotId, EntryDate, Minutes, Landings, NightLandings, Remarks) VALUES
 (1, 1, '2026-10-20', 70, 3, 3, 'Night full-stop landings at Bedford'),
 (2, 1, '2026-11-15', 50, 4, 0, 'Pattern work'),
 (3, 2, '2026-07-15', 90, 3, 3, 'Night cross-country'),
 (4, 2, '2026-11-01', 60, 3, 0, NULL),
 (5, 3, '2026-11-10', 80, 5, 3, NULL),
 (6, 4, '2026-11-20', 60, 6, 0, 'Dual, pattern work'),
 (7, 5, '2026-11-02', 90, 4, 0, NULL);

INSERT INTO Aircraft (Id, TailNumber, AircraftTypeId, HomeAirportId, Colors, Equipment, EmptyWeight, EmptyArm, MaxTakeoff, FuelArm,
                      FwdLimitLight, FwdBreakWeight, FwdLimitHeavy, AftLimit, ForHire, Hours100Base,
                      LastAnnual, LastTransponder, LastElt, EltBatteryExpires) VALUES
 (1, 'N172MS', 1, 1, 'White, blue stripes', 'SG/C',   1680, 40.0,  2550, 48.0,  35.0, 1950,  41.0,  47.3, 0,  0,    '2026-04-12', '2025-05-01', '2026-04-12', '2028-06-30'),
 (2, 'N28AR',  2, 3, 'White, red stripes',  'S/C',    1590, 87.0,  2550, 95.0,  82.0, 2050,  88.6,  93.0, 1, 99.0,  '2025-12-05', '2025-02-10', '2025-12-05', '2027-09-30'),  -- the club's: for hire
 (3, 'N22SR',  3, 1, 'Silver',              'SBG/B1', 2300, 139.0, 3400, 154.9, 137.8, 2694, 141.6, 148.1, 0, 0,   '2026-08-20', '2025-08-20', '2026-08-20', '2029-01-31'),
 (4, 'N3CUB',  4, 9, 'Cub yellow',          'N/N',    765,  13.0,  1220, 9.0,   11.0, 1220,  11.0,  20.0, 0,  0,    '2026-05-20', '2025-05-20', '2026-05-20', '2028-01-31'),
 (5, 'N172TB', 1, 2, 'White, green stripes', 'S/C',   1700, 40.2,  2550, 48.0,  35.0, 1950,  41.0,  47.3, 0,  0,    '2025-10-15', '2025-10-15', '2026-02-10', '2027-12-31');  -- the annual ran out

INSERT INTO AircraftStation (Id, AircraftId, Name, Arm, MaxWeight) VALUES
 (1, 1, 'Front seats', 37.0, 400), (2, 1, 'Rear seats', 73.0, 400), (3, 1, 'Baggage A', 95.0, 120), (4, 1, 'Baggage B', 123.0, 50),
 (5, 2, 'Front seats', 80.5, 400), (6, 2, 'Rear seats', 118.1, 400), (7, 2, 'Baggage', 142.8, 200),
 (8, 3, 'Front seats', 143.5, 400), (9, 3, 'Rear seats', 180.0, 400), (10, 3, 'Baggage', 208.0, 130),
 (11, 4, 'Front seat', 9.0, 200), (12, 4, 'Rear seat (solo)', 36.0, 200), (13, 4, 'Baggage', 50.0, 20),
 (14, 5, 'Front seats', 37.0, 400), (15, 5, 'Rear seats', 73.0, 400), (16, 5, 'Baggage A', 95.0, 120), (17, 5, 'Baggage B', 123.0, 50);

INSERT INTO Weather (Id, AirportId, ObservedAt, WindDirection, WindSpeed, Gust, Visibility, Ceiling, Temperature, Altimeter) VALUES
 (1, 1,  '2026-11-28T14:00Z', 310,  8, NULL, 10, NULL,  6, 30.12),
 (2, 4,  '2026-11-28T14:45Z', 280, 10, NULL, 10, 4500,  7, 30.10),
 (3, 5,  '2026-11-28T15:00Z', 270, 12, NULL, 10, NULL,  8, 30.08),
 (4, 5,  '2026-11-28T22:30Z', 300,  8, NULL, 10, NULL,  5, 30.15),
 (5, 1,  '2026-11-28T23:30Z', 320,  6, NULL, 10, NULL,  3, 30.18),
 (6, 1,  '2026-12-05T23:30Z', 290, 10, NULL, 10, NULL, -2, 30.25),
 (7, 8,  '2026-12-06T00:15Z', 300,  8, NULL, 10, 6000, -5, 30.22),
 (8, 3,  '2026-12-03T15:00Z', 250, 10, NULL, 10, NULL,  8, 30.05),
 (9, 6,  '2026-12-03T15:30Z', 240, 12, NULL, 10, 5000,  9, 30.04),
 (10, 9, '2026-11-29T13:00Z', 330, 14, NULL, 10, NULL,  4, 30.20),
 (11, 8, '2026-11-29T15:00Z', 340, 15, 22,   10, 7000,  1, 30.18),
 (12, 1, '2026-12-01T16:00Z', 200,  8, NULL, 10, NULL,  9, 30.00),
 (13, 10,'2026-12-01T16:15Z', 210,  9, NULL,  7, NULL,  9, 30.00),
 (14, 1, '2026-11-21T19:00Z',  30,  6, NULL, 10, NULL,  8, 30.10),
 (15, 7, '2026-11-21T19:30Z',  30,  8, NULL, 10, NULL,  7, 30.09),
 (16, 3, '2026-11-27T18:00Z', 280, 12, NULL, 10, NULL,  9, 30.02),
 (17, 11,'2026-11-27T18:30Z', 280, 14, NULL, 10, 5500,  7, 30.00),
 (18, 2, '2026-11-30T15:00Z', 320, 10, NULL, 10, NULL,  2, 30.10),
 (19, 3, '2026-11-30T15:30Z', 300, 10, NULL, 10, NULL,  5, 30.08),
 (20, 1, '2026-12-02T15:00Z', 320, 12, NULL, 10, NULL,  6, 30.05),
 (21, 6, '2026-12-02T16:00Z', 330, 20, NULL, 10, NULL,  7, 30.02),   -- a strong north-westerly: across runway 24
 (22, 1, '2026-12-04T14:00Z', 180,  6, NULL, 10, NULL,  8, 30.00),
 (23, 5, '2026-12-04T15:00Z', 180,  6, NULL,  1,  300,  9, 29.98),   -- Nantucket fog
 (24, 3, '2026-11-26T15:00Z',  60,  8, NULL, 10, NULL,  6, 30.20),
 (25, 4, '2026-11-26T15:30Z',  60, 10, NULL, 10, NULL,  7, 30.18);

INSERT INTO FlightPlan (Id, PilotId, AircraftId, RunwayId, WeatherId, DepartureDate, DepartureTime, ActualDeparture, Night, FuelOnBoard, Status, Remarks) VALUES
 (1,  1, 1, 2,  1,  '2026-11-28', '09:30', NULL,    0, 40, 'F', 'Lunch on Nantucket, by way of Hyannis'),
 (2,  1, 1, 16, 4,  '2026-11-28', '17:45', NULL,    1, 35, 'F', 'Home after dark'),
 (3,  2, 3, 2,  6,  '2026-12-05', '18:30', NULL,    1, 60, 'D', 'Dinner in Lebanon, with a friend'),
 (4,  3, 2, 8,  8,  '2026-12-03', '10:00', NULL,    0, 40, 'D', 'The Vineyard'),
 (5,  4, 4, 26, 10, '2026-11-29', '08:00', NULL,    0,  9, 'D', 'Solo cross-country to Lebanon'),
 (6,  2, 3, 4,  12, '2026-12-01', '11:00', NULL,    0, 50, 'D', 'Plum Island beach'),
 (7,  1, 1, 3,  14, '2026-11-21', '14:00', '14:05', 0, 30, 'C', 'Pease and back'),
 (8,  3, 2, 8,  16, '2026-11-27', '13:00', NULL,    0, 40, 'D', 'Westfield for the fly-in'),
 (9,  2, 5, 6,  18, '2026-11-30', '10:00', NULL,    0, 40, 'D', 'Worcester to Providence'),
 (10, 1, 1, 2,  20, '2026-12-02', '10:00', NULL,    0, 40, 'D', 'The Vineyard on a windy day'),
 (11, 1, 1, 4,  22, '2026-12-04', '09:00', NULL,    0, 45, 'D', 'Nantucket with a friend'),
 (12, 5, 2, 7,  24, '2026-11-26', '10:00', '10:10', 0, 45, 'A', 'Hyannis for lunch - in the air now');

INSERT INTO LoadItem (Id, FlightPlanId, AircraftStationId, Description, Persons, Weight) VALUES
 (1, 1, 1, 'Maria', 1, 150), (2, 1, 1, 'Passenger', 1, 170), (3, 1, 3, 'Bags', 0, 40),
 (4, 2, 1, 'Maria', 1, 150), (5, 2, 1, 'Passenger', 1, 170), (6, 2, 3, 'Bags', 0, 40),
 (7, 3, 8, 'Dev', 1, 190), (8, 3, 9, 'Passenger', 1, 160),
 (9, 4, 5, 'Hannah', 1, 140),
 (10, 5, 12, 'Tom', 1, 165),
 (11, 6, 8, 'Dev', 1, 190),
 (12, 7, 1, 'Maria', 1, 150),
 (13, 8, 5, 'Hannah', 1, 140), (14, 8, 7, 'Bags', 0, 30),
 (15, 9, 14, 'Dev', 1, 190),
 (16, 10, 1, 'Maria', 1, 150),
 (17, 11, 1, 'Maria', 1, 150), (18, 11, 1, 'Passenger', 1, 170),
 (19, 12, 5, 'Ray', 1, 185), (20, 12, 5, 'Passenger', 1, 160);

INSERT INTO Endorsement (Id, PilotId, FlightPlanId, Kind, EndorsedDate, Instructor) VALUES
 (1, 4, NULL, 'S', '2026-11-10', 'K. Lindqvist, CFI'),
 (2, 4, 5,    'X', '2026-11-25', 'K. Lindqvist, CFI');

INSERT INTO Leg (Id, FlightPlanId, Sequence, FromAirportId, ToAirportId, RunwayId, WeatherId, Altitude, WindDirection, WindSpeed) VALUES
 (1,  1, 1, 1, 4,  12, 2,  3500, 290, 20),   -- Bedford - Hyannis, MC 152: eastbound, odd + 500
 (2,  1, 2, 4, 5,  16, 3,  2500, 280, 15),   -- Hyannis - Nantucket, low over the water
 (3,  2, 1, 5, 1,  2,  5,  4500, 300, 25),   -- Nantucket - Bedford, MC 338: westbound, even + 500
 (4,  3, 1, 1, 8,  24, 7,  6500, 290, 30),   -- Bedford - Lebanon at night
 (5,  4, 1, 3, 6,  18, 9,  3500, 250, 15),   -- Providence - Martha's Vineyard
 (6,  5, 1, 9, 8,  24, 11, 4500, 340, 10),   -- Mansfield - Lebanon in the Cub, into the wind
 (7,  6, 1, 1, 10, 28, 13, 2500, 210, 10),   -- Bedford - Plum Island: 2,105 ft of turf
 (8,  7, 1, 1, 7,  22, 15, 3500,  30, 10),   -- Bedford - Portsmouth
 (9,  7, 2, 7, 1,  3,  14, 4500,  30, 10),   -- and back
 (10, 8, 1, 3, 11, 30, 17, 5500, 280, 20),   -- Providence - Westfield, MC 310: westbound at an eastbound altitude
 (11, 9, 1, 2, 3,  10, 19, 3500, 320, 15),   -- Worcester - Providence
 (12, 10, 1, 1, 6, 18, 21, 3500, 330, 30),   -- Bedford - Vineyard, runway 24 in a north-westerly
 (13, 11, 1, 1, 5, 16, 23, 5500, 200, 10),   -- Bedford - Nantucket, into the fog
 (14, 12, 1, 3, 4, 11, 25, 3500,  60, 15);   -- Providence - Hyannis

-- flight 7 as flown (Bedford - Portsmouth - Bedford), and other traffic in the area
INSERT INTO PositionReport (Id, FlightPlanId, Callsign, ReportTime, Latitude, Longitude, Altitude, GroundSpeed, Track) VALUES
 (1,  7, 'N172MS', '2026-11-21T19:05:00Z', 42.4700, -71.2890,  133,   0,  29),
 (2,  7, 'N172MS', '2026-11-21T19:10:00Z', 42.5650, -71.2180, 2400,  95,  29),
 (3,  7, 'N172MS', '2026-11-21T19:15:00Z', 42.7000, -71.1150, 3500, 115,  29),
 (4,  7, 'N172MS', '2026-11-21T19:20:00Z', 42.8350, -71.0100, 3500, 115,  29),
 (5,  7, 'N172MS', '2026-11-21T19:25:00Z', 42.9700, -70.9050, 2000, 100,  29),
 (6,  7, 'N172MS', '2026-11-21T19:30:00Z', 43.0779, -70.8233,  100,   0,  29),
 (7,  7, 'N172MS', '2026-11-21T20:00:00Z', 43.0779, -70.8233,  100,   0, 210),
 (8,  7, 'N172MS', '2026-11-21T20:07:00Z', 42.9200, -70.9300, 3200, 120, 210),
 (9,  7, 'N172MS', '2026-11-21T20:14:00Z', 42.7600, -71.0500, 4500, 125, 210),
 (10, 7, 'N172MS', '2026-11-21T20:21:00Z', 42.6000, -71.1700, 3000, 115, 210),
 (11, 7, 'N172MS', '2026-11-21T20:27:00Z', 42.4700, -71.2890,  133,   0, 210),
 (12, NULL, 'N512JT', '2026-11-21T19:15:00Z', 42.6500, -70.9500, 4500, 130, 250),
 (13, NULL, 'N512JT', '2026-11-21T19:20:00Z', 42.6100, -71.1200, 4500, 130, 250),
 (14, NULL, 'N804CP', '2026-11-21T20:10:00Z', 42.8800, -71.2000, 5500, 105,  95),
 (15, NULL, 'N804CP', '2026-11-21T20:16:00Z', 42.8700, -70.9900, 5500, 105,  95);
