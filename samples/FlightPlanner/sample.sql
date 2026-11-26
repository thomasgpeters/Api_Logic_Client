-- Flight Planner sample: the demo scenario - pilots, aircraft, flight plans and position reports.
-- purge_sample.sql removes it and keeps the airports and aircraft types. "Today" is 2026-11-26.
-- Plans go in as drafts, get their legs, then move to their status (filed or closed), as in the app.

INSERT INTO Pilot (Id, Name, Certificate, MedicalExpires, LastNightLandings) VALUES
 (1, 'Maria Santos',  'P', '2027-06-30', '2026-10-20'),   -- current for everything
 (2, 'Dev Patel',     'C', '2027-03-31', '2026-07-15'),   -- not night current since mid-October
 (3, 'Hannah Becker', 'P', '2026-11-30', '2026-11-10'),   -- the medical runs out on the 30th
 (4, 'Tom Okafor',    'S', '2027-09-30', NULL);           -- a student: no night landings yet

INSERT INTO Aircraft (Id, TailNumber, AircraftTypeId, HomeAirportId, AnnualDue) VALUES
 (1, 'N172MS', 1, 1, '2027-04-30'),
 (2, 'N28AR',  2, 3, '2026-12-10'),
 (3, 'N22SR',  3, 1, '2027-08-31'),
 (4, 'N3CUB',  4, 9, '2027-05-31'),
 (5, 'N172TB', 1, 2, '2026-11-20');    -- the annual inspection is overdue

INSERT INTO FlightPlan (Id, PilotId, AircraftId, DepartureDate, DepartureTime, Night, FuelOnBoard, Status, Remarks) VALUES
 (1, 1, 1, '2026-11-28', '09:30', 0, 40, 'F', 'Lunch on Nantucket, by way of Hyannis'),
 (2, 1, 1, '2026-11-28', '17:45', 1, 35, 'F', 'Home after dark'),
 (3, 2, 3, '2026-12-05', '18:30', 1, 60, 'D', 'Dinner in Lebanon'),
 (4, 3, 2, '2026-12-03', '10:00', 0, 40, 'D', 'The Vineyard'),
 (5, 4, 4, '2026-11-29', '08:00', 0,  9, 'D', 'Cross-country to Lebanon'),
 (6, 2, 3, '2026-12-01', '11:00', 0, 50, 'D', 'Plum Island beach'),
 (7, 1, 1, '2026-11-21', '14:00', 0, 30, 'C', 'Pattern work at Pease and back'),
 (8, 3, 2, '2026-11-27', '13:00', 0, 40, 'D', 'Westfield for the fly-in'),
 (9, 2, 5, '2026-11-30', '10:00', 0, 40, 'D', 'Worcester to Providence');

INSERT INTO Leg (Id, FlightPlanId, Sequence, FromAirportId, ToAirportId, Altitude, Headwind) VALUES
 (1,  1, 1, 1, 4, 3500,  10),     -- Bedford - Hyannis, MC 152: eastbound, odd + 500
 (2,  1, 2, 4, 5, 2500,   5),     -- Hyannis - Nantucket, low over the water: under 3,000 ft above it
 (3,  2, 1, 5, 1, 4500, -15),     -- Nantucket - Bedford, MC 338: westbound, even + 500
 (4,  3, 1, 1, 8, 6500,  20),     -- Bedford - Lebanon at night
 (5,  4, 1, 3, 6, 3500,   0),     -- Providence - Martha's Vineyard
 (6,  5, 1, 9, 8, 4500,  15),     -- Mansfield - Lebanon in the Cub, into the wind
 (7,  6, 1, 1, 10, 2500,  0),     -- Bedford - Plum Island: 2,105 ft of runway
 (8,  7, 1, 1, 7, 3500,   5),     -- Bedford - Portsmouth
 (9,  7, 2, 7, 1, 4500,  -5),     -- and back
 (10, 8, 1, 3, 11, 5500, 10),     -- Providence - Westfield, MC 310: westbound at an eastbound altitude
 (11, 9, 1, 2, 3, 3500,   0);     -- Worcester - Providence

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
