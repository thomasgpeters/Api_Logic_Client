-- Flight Planner sample: VFR flight planning for amateur (private) pilots, set in New England.
-- A pilot plans a flight leg by leg between airports; the rules work out each leg's distance and course
-- (great circle, from the airports' coordinates), the ground speed, time and fuel for the aircraft flown,
-- the fuel the flight needs with the reserve, and whether the flight is a GO: the pilot's medical and
-- night currency, the aircraft's annual inspection, VFR cruising altitudes and runway lengths.
-- Position reports replay a flown flight on a map, with other traffic around it.
-- The source of truth for the tables; build_db.py makes flightplanner.sqlite from it.
-- Columns marked (rule) are maintained by the business rules, never typed.
-- Airport positions are approximate and the aircraft figures typical: NOT FOR NAVIGATION. Pilots and
-- tail numbers are made up.

PRAGMA foreign_keys = ON;

-- reference data ---------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Airport (
    Id             INTEGER PRIMARY KEY,
    Ident          TEXT NOT NULL,          -- ICAO or FAA identifier: KBED, 1B9
    Name           TEXT NOT NULL,
    City           TEXT,
    Latitude       REAL NOT NULL,          -- degrees, north positive
    Longitude      REAL NOT NULL,          -- degrees, east positive (New England is negative)
    Elevation      INTEGER NOT NULL DEFAULT 0,   -- feet above sea level
    RunwayLength   INTEGER NOT NULL,       -- the longest runway, feet
    Variation      INTEGER NOT NULL DEFAULT 0,   -- magnetic variation, degrees, west positive (MC = TC + W)
    Fuel           BOOLEAN NOT NULL DEFAULT 1,   -- 100LL sold
    Towered        BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS AircraftType (
    Id            INTEGER PRIMARY KEY,
    Model         TEXT NOT NULL,           -- Cessna 172S Skyhawk, ...
    CruiseKnots   INTEGER NOT NULL,        -- true airspeed at cruise
    FuelBurn      REAL NOT NULL,           -- US gallons per hour at cruise
    UsableFuel    REAL NOT NULL,           -- US gallons
    MinRunway     INTEGER NOT NULL         -- feet: the shortest runway this type lands on, with margin
);

-- pilots and aircraft ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Pilot (
    Id                 INTEGER PRIMARY KEY,
    Name               TEXT NOT NULL,
    Certificate        TEXT NOT NULL DEFAULT 'P',   -- S = Student, P = Private, C = Commercial
    MedicalExpires     DATE,              -- the last day the medical certificate is valid
    LastNightLandings  DATE,              -- the day of the third of the last three night landings
    FlightCount        INTEGER DEFAULT 0, -- (rule) flights flown
    FlownMinutes       INTEGER DEFAULT 0  -- (rule) the logbook: minutes flown
);

CREATE TABLE IF NOT EXISTS Aircraft (
    Id              INTEGER PRIMARY KEY,
    TailNumber      TEXT NOT NULL,        -- N-number (made up)
    AircraftTypeId  INTEGER NOT NULL REFERENCES AircraftType(Id),
    HomeAirportId   INTEGER REFERENCES Airport(Id),
    AnnualDue       DATE,                 -- the annual inspection is valid until this day
    CruiseKnots     INTEGER,              -- (rule) copied from the type: this airframe's own figures
    FuelBurn        REAL,                 -- (rule) copied
    UsableFuel      REAL,                 -- (rule) copied
    MinRunway       INTEGER,              -- (rule) copied
    FlownMinutes    INTEGER DEFAULT 0     -- (rule) minutes flown
);

-- flight plans -----------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS FlightPlan (
    Id              INTEGER PRIMARY KEY,
    PilotId         INTEGER NOT NULL REFERENCES Pilot(Id),
    AircraftId      INTEGER NOT NULL REFERENCES Aircraft(Id),
    DepartureDate   DATE NOT NULL,
    DepartureTime   TEXT,                 -- local, HH:MM
    Night           BOOLEAN NOT NULL DEFAULT 0,
    FuelOnBoard     REAL NOT NULL DEFAULT 0,   -- gallons at engine start
    Status          TEXT NOT NULL DEFAULT 'D', -- D = Draft, F = Filed, C = Closed (flown)
    Remarks         TEXT,
    CruiseKnots     INTEGER,              -- (rule) copied from the aircraft
    FuelBurn        REAL,                 -- (rule) copied
    UsableFuel      REAL,                 -- (rule) copied
    MinRunway       INTEGER,              -- (rule) copied
    LegCount        INTEGER DEFAULT 0,    -- (rule)
    Distance        REAL DEFAULT 0,       -- (rule) nautical miles
    Minutes         INTEGER DEFAULT 0,    -- (rule) en-route time
    TripFuel        REAL DEFAULT 0,       -- (rule) gallons for the legs
    ReserveFuel     REAL DEFAULT 0,       -- (rule) 30 minutes by day, 45 at night (14 CFR 91.151)
    FuelRequired    REAL DEFAULT 0,       -- (rule) trip + reserve
    FuelMargin      REAL DEFAULT 0,       -- (rule) on board - required
    BadAltitudeLegs INTEGER DEFAULT 0,    -- (rule) legs at a cruising altitude 14 CFR 91.159 does not allow
    ShortRunwayLegs INTEGER DEFAULT 0,    -- (rule) legs ending at a runway shorter than the aircraft needs
    NoGoReason      TEXT,                 -- (rule) the first reason the flight may not go; empty: GO
    GoNoGo          TEXT,                 -- (rule) GO or NO-GO
    ReportCount     INTEGER DEFAULT 0     -- (rule) position reports
);

CREATE TABLE IF NOT EXISTS Leg (
    Id              INTEGER PRIMARY KEY,
    FlightPlanId    INTEGER NOT NULL REFERENCES FlightPlan(Id),
    Sequence        INTEGER NOT NULL DEFAULT 1,
    FromAirportId   INTEGER NOT NULL REFERENCES Airport(Id),
    ToAirportId     INTEGER NOT NULL REFERENCES Airport(Id),
    Altitude        INTEGER NOT NULL,     -- cruising altitude, feet MSL
    Headwind        INTEGER NOT NULL DEFAULT 0,   -- knots along the course; a tailwind is negative
    Distance        REAL,                 -- (rule) great-circle, nautical miles
    TrueCourse      INTEGER,              -- (rule) initial true course, degrees
    MagneticCourse  INTEGER,              -- (rule) true course + the departure airport's variation
    GroundSpeed     INTEGER,              -- (rule) cruise - headwind
    Minutes         INTEGER,              -- (rule)
    Fuel            REAL,                 -- (rule) gallons
    AltitudeOK      BOOLEAN,              -- (rule) the hemispheric rule, above 3,000 ft over the ground
    RunwayOK        BOOLEAN               -- (rule) the destination's runway is long enough
);

-- where aircraft were: a flown flight's track, and other traffic (no flight plan of ours) ----------

CREATE TABLE IF NOT EXISTS PositionReport (
    Id              INTEGER PRIMARY KEY,
    FlightPlanId    INTEGER REFERENCES FlightPlan(Id),   -- empty: other traffic
    Callsign        TEXT NOT NULL,
    ReportTime      TEXT NOT NULL,        -- ISO date and time, UTC
    Latitude        REAL NOT NULL,
    Longitude       REAL NOT NULL,
    Altitude        INTEGER,              -- feet MSL
    GroundSpeed     INTEGER,              -- knots
    Track           INTEGER               -- degrees true: the direction the aircraft moves (the map's vector)
);

CREATE INDEX IF NOT EXISTS LegByFlightPlan ON Leg(FlightPlanId);
CREATE INDEX IF NOT EXISTS ReportByFlightPlan ON PositionReport(FlightPlanId);
