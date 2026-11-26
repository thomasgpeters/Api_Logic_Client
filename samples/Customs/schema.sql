-- Customs sample: a national customs clearance system, set in Bermuda.
-- Goods arrive by sea (containers, Port of Hamilton / Dockyard) and by air (L.F. Wade International);
-- importers lodge declarations, ideally before arrival (pre-clearance); duty is a percentage of value;
-- at the port gate a truck's transponder is read, its driver and the truck must be cleared, the
-- container's seal must match the declared one, and it must leave on a registered route.
-- The source of truth for the tables; build_db.py makes customs.sqlite from it.
-- Columns marked (rule) are maintained by the business rules, never typed.
-- Sample duty rates in Bermuda's style - NOT the official Bermuda tariff. Companies and people are made up.

PRAGMA foreign_keys = ON;

-- reference data ---------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Country (
    Code       TEXT PRIMARY KEY,           -- ISO 3166 alpha-2: where goods come from
    Name       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Tariff (
    Code              TEXT PRIMARY KEY,    -- an HS-style heading, e.g. 2204.21
    Description       TEXT NOT NULL,
    DutyRate          REAL NOT NULL,       -- percent of the value (sample rates)
    LicenceRequired   BOOLEAN NOT NULL DEFAULT 0   -- an import licence must be declared (e.g. alcohol)
);

CREATE TABLE IF NOT EXISTS PortOfEntry (
    Id              INTEGER PRIMARY KEY,
    Name            TEXT NOT NULL,         -- Port of Hamilton, ...
    Mode            TEXT NOT NULL,         -- S = Sea, A = Air
    ProcessingFee   REAL NOT NULL DEFAULT 25,   -- per declaration
    Latitude        REAL,
    Longitude       REAL
);

CREATE TABLE IF NOT EXISTS Carrier (
    Id      INTEGER PRIMARY KEY,
    Name    TEXT NOT NULL,                 -- shipping line, airline, or haulier (made up)
    Type    TEXT NOT NULL                  -- S = Shipping line, A = Airline, H = Haulier
);

-- importers and what arrives ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Importer (
    Id               INTEGER PRIMARY KEY,
    Name             TEXT NOT NULL,
    CustomsNumber    TEXT,                 -- registration with customs
    Registered       BOOLEAN NOT NULL DEFAULT 0,
    BondAmount       REAL NOT NULL DEFAULT 0,   -- deferment bond: released goods may owe up to this
    Parish           TEXT,
    DeferredBalance  REAL DEFAULT 0,       -- (rule) what its released declarations still owe
    DeclarationCount INTEGER DEFAULT 0     -- (rule)
);

CREATE TABLE IF NOT EXISTS Arrival (
    Id              INTEGER PRIMARY KEY,
    CarrierId       INTEGER NOT NULL REFERENCES Carrier(Id),
    PortOfEntryId   INTEGER NOT NULL REFERENCES PortOfEntry(Id),
    VoyageNumber    TEXT NOT NULL,         -- a ship's voyage or a flight
    ArrivalDate     DATE NOT NULL,
    ProcessingFee   REAL                   -- (rule) the port's fee, copied
);

CREATE TABLE IF NOT EXISTS Container (
    Id           INTEGER PRIMARY KEY,
    ArrivalId    INTEGER NOT NULL REFERENCES Arrival(Id),
    Number       TEXT NOT NULL,            -- e.g. NSLU 482910 7
    Size         TEXT NOT NULL DEFAULT '20',   -- 20 / 40 (feet); 'AIR' for an air cargo unit
    SealNumber   TEXT NOT NULL             -- the seal declared on the manifest
);

-- declarations ------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Declaration (
    Id                 INTEGER PRIMARY KEY,
    ImporterId         INTEGER NOT NULL REFERENCES Importer(Id),
    ArrivalId          INTEGER NOT NULL REFERENCES Arrival(Id),
    ContainerId        INTEGER REFERENCES Container(Id),
    EntryNumber        TEXT NOT NULL,
    LodgedDate         DATE NOT NULL,      -- before arrival: eligible for pre-clearance
    Status             TEXT NOT NULL DEFAULT 'L',   -- L = Lodged, R = Released, H = Held
    ProcessingFee      REAL,               -- (rule) copied from the arrival
    LineCount          INTEGER DEFAULT 0,  -- (rule)
    TotalValue         REAL DEFAULT 0,     -- (rule) its lines' values
    TotalDuty          REAL DEFAULT 0,     -- (rule) its lines' duty
    AmountDue          REAL DEFAULT 0,     -- (rule) duty + processing fee
    Paid               REAL DEFAULT 0,     -- (rule) its payments
    Balance            REAL DEFAULT 0,     -- (rule) AmountDue - Paid
    MissingLicences    INTEGER DEFAULT 0,  -- (rule) lines that need a licence and have none
    PreCleared         BOOLEAN DEFAULT 0,  -- (rule) lodged before arrival, registered importer, licences in order
    Lane               TEXT,               -- (rule) G = green (pre-cleared), R = red (inspect)
    PassedInspections  INTEGER DEFAULT 0,  -- (rule)
    FailedInspections  INTEGER DEFAULT 0   -- (rule)
);

CREATE TABLE IF NOT EXISTS DeclarationLine (
    Id               INTEGER PRIMARY KEY,
    DeclarationId    INTEGER NOT NULL REFERENCES Declaration(Id),
    TariffCode       TEXT NOT NULL REFERENCES Tariff(Code),
    CountryCode      TEXT NOT NULL REFERENCES Country(Code),   -- origin
    Description      TEXT,
    Quantity         REAL NOT NULL,
    Value            REAL NOT NULL,        -- the customs value (CIF), Bermuda dollars
    LicenceNumber    TEXT,
    DutyRate         REAL,                 -- (rule) the tariff's rate, copied
    LicenceRequired  BOOLEAN DEFAULT 0,    -- (rule) copied from the tariff
    Duty             REAL DEFAULT 0        -- (rule) Value x DutyRate / 100
);

CREATE TABLE IF NOT EXISTS Payment (
    Id              INTEGER PRIMARY KEY,
    DeclarationId   INTEGER NOT NULL REFERENCES Declaration(Id),
    PaidDate        DATE NOT NULL,
    Amount          REAL NOT NULL,
    Reference       TEXT
);

CREATE TABLE IF NOT EXISTS Inspection (
    Id              INTEGER PRIMARY KEY,
    DeclarationId   INTEGER NOT NULL REFERENCES Declaration(Id),
    InspectedDate   DATE NOT NULL,
    Officer         TEXT,
    Result          TEXT NOT NULL DEFAULT 'P',   -- P = Passed, F = Failed
    Notes           TEXT
);

-- pre-clearance at the gate -------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Truck (
    Id              INTEGER PRIMARY KEY,
    CarrierId       INTEGER NOT NULL REFERENCES Carrier(Id),   -- the haulier
    Registration    TEXT NOT NULL,
    TransponderId   TEXT NOT NULL,
    ClearedUntil    DATE                   -- pre-clearance of the truck; empty: never cleared
);

CREATE TABLE IF NOT EXISTS Driver (
    Id              INTEGER PRIMARY KEY,
    Name            TEXT NOT NULL,
    LicenceNumber   TEXT NOT NULL,
    ClearedUntil    DATE                   -- pre-clearance of the driver
);

CREATE TABLE IF NOT EXISTS Route (
    Id              INTEGER PRIMARY KEY,
    Name            TEXT NOT NULL,         -- Hamilton docks to Southampton warehouse ...
    FromPortId      INTEGER NOT NULL REFERENCES PortOfEntry(Id),
    Destination     TEXT NOT NULL,         -- the parish / premises
    Approved        BOOLEAN NOT NULL DEFAULT 0   -- registered with customs and approved
);

CREATE TABLE IF NOT EXISTS Movement (
    Id                INTEGER PRIMARY KEY,
    DeclarationId     INTEGER NOT NULL REFERENCES Declaration(Id),
    ContainerId       INTEGER NOT NULL REFERENCES Container(Id),
    TruckId           INTEGER NOT NULL REFERENCES Truck(Id),
    DriverId          INTEGER NOT NULL REFERENCES Driver(Id),
    RouteId           INTEGER NOT NULL REFERENCES Route(Id),
    MoveDate          DATE NOT NULL,
    TransponderRead   BOOLEAN NOT NULL DEFAULT 1,   -- the gate read the truck's transponder
    ObservedSeal      TEXT,                  -- the seal number read at the gate
    Status            TEXT NOT NULL DEFAULT 'W',   -- W = Waiting at the gate, O = Gate out, S = Stopped
    Reason            TEXT,                  -- (rule) why it cannot go: the first check that fails
    Lane              TEXT                   -- (rule) G = through the gate, R = stop
);
