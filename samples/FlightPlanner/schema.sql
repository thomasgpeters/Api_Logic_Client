-- Flight Planner sample: VFR flight planning for amateur (private) pilots, set in New England.
-- A pilot plans a flight leg by leg between airports. The rules work out each leg's distance and course
-- (great circle), the wind triangle (heading and ground speed), time and fuel; the weight and balance; the
-- takeoff and landing distances at the day's density altitude against the runways; the crosswind; the
-- weather against the VFR minimums; and whether the flight is a GO: the pilot's medical (or BasicMed),
-- flight review and currency from the logbook, a student's endorsements, the aircraft's inspections.
-- Position reports replay a flown flight on a map, with other traffic around it.
-- The source of truth for the tables; build_db.py makes flightplanner.sqlite from it.
-- Columns marked (rule) are maintained by the business rules, never typed.
-- Research and regulations: docs/research/Flight Planning Research.md.
-- Airport positions are approximate and the aircraft figures typical: NOT FOR NAVIGATION. Pilots,
-- tail numbers, weather and NOTAMs are made up.

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
    Variation      INTEGER NOT NULL DEFAULT 0,   -- magnetic variation, degrees, west positive (MC = TC + W)
    Airspace       TEXT NOT NULL DEFAULT 'G',    -- the class at the surface: B, C, D, E or G
    Fuel           BOOLEAN NOT NULL DEFAULT 1,   -- 100LL sold
    Towered        BOOLEAN NOT NULL DEFAULT 0,
    ClosedNotams   INTEGER DEFAULT 0       -- (rule) active NOTAMs that close it (closure, TFR)
);

CREATE TABLE IF NOT EXISTS Runway (
    Id           INTEGER PRIMARY KEY,
    AirportId    INTEGER NOT NULL REFERENCES Airport(Id),
    Ident        TEXT NOT NULL,            -- one end: 29, 05, 33L
    Heading      INTEGER NOT NULL,         -- magnetic
    Length       INTEGER NOT NULL,         -- feet
    Surface      TEXT NOT NULL DEFAULT 'Asphalt',
    Variation    INTEGER,                  -- (rule) copied from the airport
    Airspace     TEXT                      -- (rule) copied from the airport
);

CREATE TABLE IF NOT EXISTS Notam (
    Id          INTEGER PRIMARY KEY,
    AirportId   INTEGER NOT NULL REFERENCES Airport(Id),
    Number      TEXT NOT NULL,             -- 11/112
    Kind        TEXT NOT NULL,             -- C = Closed, T = TFR, O = Other (obstacle, lighting ...)
    Text        TEXT NOT NULL,
    Active      BOOLEAN NOT NULL DEFAULT 1 -- in effect now (as the NOTAM feed says)
);

CREATE TABLE IF NOT EXISTS AircraftType (
    Id               INTEGER PRIMARY KEY,
    Model            TEXT NOT NULL,        -- Cessna 172S Skyhawk, ...
    IcaoType         TEXT NOT NULL,        -- the type designator on a flight plan: C172, P28A, SR22, J3
    CruiseKnots      INTEGER NOT NULL,     -- true airspeed at cruise
    FuelBurn         REAL NOT NULL,        -- US gallons per hour at cruise
    UsableFuel       REAL NOT NULL,        -- US gallons
    MaxCrosswind     INTEGER NOT NULL,     -- maximum demonstrated crosswind, knots
    TakeoffDistance  INTEGER NOT NULL,     -- feet over a 50 ft obstacle, sea level, standard day, max weight
    LandingDistance  INTEGER NOT NULL,     -- feet over a 50 ft obstacle, sea level, standard day
    TaxiFuel         REAL NOT NULL,        -- gallons for start, taxi and run-up
    ClimbFuel        REAL NOT NULL         -- gallons more than cruise for the climb
);

-- pilots -------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Pilot (
    Id                 INTEGER PRIMARY KEY,
    Name               TEXT NOT NULL,
    Certificate        TEXT NOT NULL DEFAULT 'P',   -- S = Student, P = Private, C = Commercial
    Phone              TEXT,              -- for the flight plan
    BirthDate          DATE,
    MedicalClass       INTEGER,           -- 1, 2 or 3; empty: none
    MedicalExam        DATE,              -- the date of the exam
    BasicMedCourse     DATE,              -- BasicMed: the online course ...
    BasicMedExam       DATE,              -- ... and the physician's exam (CMEC)
    FlightReview       DATE,              -- the last flight review (61.56)
    AsOf               DATE,              -- the day currency is counted back from (today in the app)
    MedicalExpires     DATE,              -- (rule) end of the month, 60 months after the exam under 40, else 24 (61.23)
    BasicMedUntil      DATE,              -- (rule) the earlier of course + 24 months and exam + 48 months
    ReviewDue          DATE,              -- (rule) end of the month, 24 months after the review
    Landings90         INTEGER DEFAULT 0, -- (rule) takeoffs and landings in the 90 days to AsOf
    NightLandings90    INTEGER DEFAULT 0, -- (rule) full-stop night landings in the 90 days to AsOf
    SoloEndorsements   INTEGER DEFAULT 0, -- (rule) solo endorsements in the 90 days to AsOf (students)
    ClassBEndorsements INTEGER DEFAULT 0, -- (rule) Class B endorsements in the 90 days to AsOf (students)
    FlightCount        INTEGER DEFAULT 0, -- (rule) flights flown (closed plans)
    FlownMinutes       INTEGER DEFAULT 0  -- (rule)
);

CREATE TABLE IF NOT EXISTS LogbookEntry (
    Id            INTEGER PRIMARY KEY,
    PilotId       INTEGER NOT NULL REFERENCES Pilot(Id),
    EntryDate     DATE NOT NULL,
    Minutes       INTEGER NOT NULL DEFAULT 0,
    Landings      INTEGER NOT NULL DEFAULT 0,
    NightLandings INTEGER NOT NULL DEFAULT 0,  -- to a full stop, from an hour after sunset to an hour before sunrise
    Remarks       TEXT,
    Recent        BOOLEAN                       -- (rule) within the 90 days to the pilot's AsOf
);

-- aircraft -----------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Aircraft (
    Id                 INTEGER PRIMARY KEY,
    TailNumber         TEXT NOT NULL,     -- N-number (made up)
    AircraftTypeId     INTEGER NOT NULL REFERENCES AircraftType(Id),
    HomeAirportId      INTEGER REFERENCES Airport(Id),
    Colors             TEXT,              -- for the flight plan (search and rescue)
    Equipment          TEXT,              -- the flight plan's item 10: S/C, SG/B1 ...
    EmptyWeight        REAL NOT NULL,     -- pounds, from this airframe's weight and balance record
    EmptyArm           REAL NOT NULL,     -- inches aft of the datum
    MaxTakeoff         REAL NOT NULL,     -- pounds
    FuelArm            REAL NOT NULL,
    FwdLimitLight      REAL NOT NULL,     -- the forward CG limit at and below FwdBreakWeight ...
    FwdBreakWeight     REAL NOT NULL,
    FwdLimitHeavy      REAL NOT NULL,     -- ... rising in a straight line to this at MaxTakeoff
    AftLimit           REAL NOT NULL,
    ForHire            BOOLEAN NOT NULL DEFAULT 0,   -- rented or used for instruction: 100-hour inspections
    Hours100Base       REAL NOT NULL DEFAULT 0,      -- hours since the 100-hour inspection, when entered
    LastAnnual         DATE,
    LastTransponder    DATE,              -- transponder check (91.413)
    LastElt            DATE,              -- ELT inspection (91.207)
    EltBatteryExpires  DATE,
    CruiseKnots        INTEGER,           -- (rule) copied from the type: this airframe's figures
    FuelBurn           REAL,              -- (rule) copied
    UsableFuel         REAL,              -- (rule) copied
    MaxCrosswind       INTEGER,           -- (rule) copied
    TakeoffDistance    INTEGER,           -- (rule) copied
    LandingDistance    INTEGER,           -- (rule) copied
    TaxiFuel           REAL,              -- (rule) copied
    ClimbFuel          REAL,              -- (rule) copied
    EmptyMoment        REAL,              -- (rule) weight x arm
    AnnualDue          DATE,              -- (rule) end of the month, 12 months after (91.409)
    TransponderDue     DATE,              -- (rule) 24 calendar months
    EltDue             DATE,              -- (rule) 12 calendar months
    FlownMinutes       INTEGER DEFAULT 0, -- (rule) closed plans
    HoursSince100      REAL               -- (rule) Hours100Base + hours flown
);

CREATE TABLE IF NOT EXISTS AircraftStation (
    Id          INTEGER PRIMARY KEY,
    AircraftId  INTEGER NOT NULL REFERENCES Aircraft(Id),
    Name        TEXT NOT NULL,             -- Front seats, Rear seats, Baggage A ...
    Arm         REAL NOT NULL,
    MaxWeight   REAL NOT NULL
);

-- the day's weather: an observation (METAR) as briefed ----------------------------------------------

CREATE TABLE IF NOT EXISTS Weather (
    Id              INTEGER PRIMARY KEY,
    AirportId       INTEGER NOT NULL REFERENCES Airport(Id),
    ObservedAt      TEXT NOT NULL,         -- ISO date and time, UTC
    WindDirection   INTEGER NOT NULL DEFAULT 0,   -- from, degrees true
    WindSpeed       INTEGER NOT NULL DEFAULT 0,   -- knots
    Gust            INTEGER,
    Visibility      REAL NOT NULL,         -- statute miles
    Ceiling         INTEGER,               -- feet above the ground, the lowest broken or overcast layer; empty: none
    Temperature     REAL NOT NULL,         -- degrees C
    Altimeter       REAL NOT NULL,         -- inches of mercury
    DensityAltitude INTEGER,               -- (rule) from elevation, altimeter and temperature
    Category        TEXT                   -- (rule) VFR, MVFR, IFR, LIFR
);

-- flight plans ---------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS FlightPlan (
    Id               INTEGER PRIMARY KEY,
    PilotId          INTEGER NOT NULL REFERENCES Pilot(Id),
    AircraftId       INTEGER NOT NULL REFERENCES Aircraft(Id),
    RunwayId         INTEGER REFERENCES Runway(Id),    -- the departure runway
    WeatherId        INTEGER REFERENCES Weather(Id),   -- the departure weather, as briefed
    DepartureDate    DATE NOT NULL,
    DepartureTime    TEXT,                 -- HH:MM (UTC on the filed plan)
    ActualDeparture  TEXT,                 -- HH:MM, when the plan is opened (Active)
    Night            BOOLEAN NOT NULL DEFAULT 0,
    FuelOnBoard      REAL NOT NULL DEFAULT 0,   -- gallons at engine start
    Status           TEXT NOT NULL DEFAULT 'D', -- D = Draft, F = Filed, A = Active (in the air), C = Closed
    Remarks          TEXT,
    FlightServiceId  TEXT,                 -- Professional: the identifier Flight Service gave the filed plan
    FiledAt          TEXT,                 -- Professional: when it was filed (docs/design/Flight Service Filing Design.md)
    CruiseKnots      INTEGER,              -- (rule) copied from the aircraft
    FuelBurn         REAL,                 -- (rule) copied
    MaxCrosswind     INTEGER,              -- (rule) copied
    LandingDistance  INTEGER,              -- (rule) copied
    Student          BOOLEAN,              -- (rule) the pilot is a student
    LegCount         INTEGER DEFAULT 0,    -- (rule)
    Distance         REAL DEFAULT 0,       -- (rule) nautical miles
    Minutes          INTEGER DEFAULT 0,    -- (rule) en-route time
    TripFuel         REAL DEFAULT 0,       -- (rule) gallons for the legs
    ReserveFuel      REAL DEFAULT 0,       -- (rule) 30 minutes by day, 45 at night (91.151)
    FuelRequired     REAL DEFAULT 0,       -- (rule) taxi + climb + trip + reserve
    FuelMargin       REAL DEFAULT 0,       -- (rule) on board - required
    Endurance        INTEGER DEFAULT 0,    -- (rule) minutes of fuel on board (the flight plan's item 19)
    LegProblems      INTEGER DEFAULT 0,    -- (rule) legs with a Problem
    ClassBLegs       INTEGER DEFAULT 0,    -- (rule) legs to a Class B airport
    XcEndorsements   INTEGER DEFAULT 0,    -- (rule) a student's endorsements for this cross-country
    PersonsOnBoard   INTEGER DEFAULT 0,    -- (rule) from the load
    PayloadWeight    REAL DEFAULT 0,       -- (rule) people and baggage
    PayloadMoment    REAL DEFAULT 0,       -- (rule)
    RampWeight       REAL,                 -- (rule) empty + payload + fuel (6 lb a gallon)
    TakeoffWeight    REAL,                 -- (rule) ramp - taxi fuel
    LandingWeight    REAL,                 -- (rule) takeoff - climb and trip fuel
    CG               REAL,                 -- (rule) centre of gravity at takeoff, inches
    ForwardLimit     REAL,                 -- (rule) the forward CG limit at the takeoff weight
    TakeoffDistance  INTEGER,              -- (rule) at the departure's density altitude and the takeoff weight
    Crosswind        INTEGER,              -- (rule) on the departure runway
    ETA              TEXT,                 -- (rule) HH:MM: departure + en-route time
    SearchAt         TEXT,                 -- (rule) HH:MM: overdue, search and rescue begins (ETA + 30)
    NoGoReason       TEXT,                 -- (rule) the first reason the flight may not go; empty: GO
    GoNoGo           TEXT,                 -- (rule) GO or NO-GO
    ReportCount      INTEGER DEFAULT 0     -- (rule) position reports
);

CREATE TABLE IF NOT EXISTS LoadItem (
    Id                 INTEGER PRIMARY KEY,
    FlightPlanId       INTEGER NOT NULL REFERENCES FlightPlan(Id),
    AircraftStationId  INTEGER NOT NULL REFERENCES AircraftStation(Id),
    Description        TEXT NOT NULL,      -- the pilot, a passenger, bags
    Persons            INTEGER NOT NULL DEFAULT 0,
    Weight             REAL NOT NULL,      -- pounds
    Arm                REAL,               -- (rule) copied from the station
    MaxWeight          REAL,               -- (rule) copied from the station
    Moment             REAL                -- (rule) weight x arm
);

CREATE TABLE IF NOT EXISTS Endorsement (
    Id            INTEGER PRIMARY KEY,
    PilotId       INTEGER NOT NULL REFERENCES Pilot(Id),
    FlightPlanId  INTEGER REFERENCES FlightPlan(Id),   -- a cross-country endorsement is for one flight
    Kind          TEXT NOT NULL,           -- S = Solo (61.87), X = Cross-country (61.93), B = Class B (61.95)
    EndorsedDate  DATE NOT NULL,
    Instructor    TEXT NOT NULL,
    Recent        BOOLEAN                  -- (rule) within the 90 days to the pilot's AsOf
);

CREATE TABLE IF NOT EXISTS Leg (
    Id              INTEGER PRIMARY KEY,
    FlightPlanId    INTEGER NOT NULL REFERENCES FlightPlan(Id),
    Sequence        INTEGER NOT NULL DEFAULT 1,
    FromAirportId   INTEGER NOT NULL REFERENCES Airport(Id),
    ToAirportId     INTEGER NOT NULL REFERENCES Airport(Id),
    RunwayId        INTEGER REFERENCES Runway(Id),    -- the landing runway
    WeatherId       INTEGER REFERENCES Weather(Id),   -- the destination weather, as briefed
    Altitude        INTEGER NOT NULL,      -- cruising altitude, feet MSL
    WindDirection   INTEGER NOT NULL DEFAULT 0,   -- the wind aloft, from, degrees true
    WindSpeed       INTEGER NOT NULL DEFAULT 0,   -- knots
    Distance        REAL,                  -- (rule) great circle, nautical miles
    TrueCourse      INTEGER,               -- (rule) initial true course
    MagneticCourse  INTEGER,               -- (rule) true course + the departure airport's variation
    WindCorrection  INTEGER,               -- (rule) degrees, the wind triangle
    TrueHeading     INTEGER,               -- (rule) true course + wind correction
    MagneticHeading INTEGER,               -- (rule) true heading + variation
    GroundSpeed     INTEGER,               -- (rule)
    Minutes         INTEGER,               -- (rule)
    Fuel            REAL,                  -- (rule) gallons
    ToAirspace      TEXT,                  -- (rule) copied from the destination
    LandingDistance INTEGER,               -- (rule) at the destination's density altitude
    Crosswind       INTEGER,               -- (rule) on the landing runway
    Problem         TEXT                   -- (rule) the first thing wrong with the leg; empty: none
);

-- where aircraft were: a flown flight's track, and other traffic (no flight plan of ours) ------------

CREATE TABLE IF NOT EXISTS PositionReport (
    Id              INTEGER PRIMARY KEY,
    FlightPlanId    INTEGER REFERENCES FlightPlan(Id),   -- empty: other traffic
    Callsign        TEXT NOT NULL,
    ReportTime      TEXT NOT NULL,         -- ISO date and time, UTC
    Latitude        REAL NOT NULL,
    Longitude       REAL NOT NULL,
    Altitude        INTEGER,               -- feet MSL
    GroundSpeed     INTEGER,               -- knots
    Track           INTEGER                -- degrees true: the direction the aircraft moves (the map's vector)
);

CREATE INDEX IF NOT EXISTS LegByFlightPlan ON Leg(FlightPlanId);
CREATE INDEX IF NOT EXISTS LoadByFlightPlan ON LoadItem(FlightPlanId);
CREATE INDEX IF NOT EXISTS ReportByFlightPlan ON PositionReport(FlightPlanId);
