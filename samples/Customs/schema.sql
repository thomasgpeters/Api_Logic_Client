-- Customs sample: a national customs clearance system, set in Bermuda, with automated clearance.
-- Goods arrive by sea (Port of Hamilton, Dockyard, St. George's) and by air (L.F. Wade International) on a
-- manifest: master bills of lading, each with its house bills. An importer (or a broker for one) lodges a
-- declaration, ideally before arrival. Duty is on the price paid (FOB, Public Notice 17), converted at the
-- week's exchange rate: ad valorem, specific (per unit) or both, stepped for cars; wharfage on top.
-- Every declaration is risk-scored into a lane - green (released automatically), yellow (a document check),
-- red (a physical examination), blue (released now, audited later: trusted traders) - with a random
-- selection on top. Release needs the goods arrived, no open hold, no missing agency permit, no prohibited
-- goods, the lane's check passed, and the duty paid or on the importer's monthly statement within its bond.
-- At the port gate a truck goes out only with released goods, a read transponder, the declared seal, a
-- cleared truck and driver, on an approved route.
-- The source of truth for the tables; build_db.py makes customs.sqlite from it.
-- Columns marked (rule) are maintained by the business rules, never typed.
-- Research and sources: docs/research/Customs Clearance Research.md. Sample rates and risk weights in
-- Bermuda's style - NOT the official tariff or risk profile. Companies and people are made up.

PRAGMA foreign_keys = ON;

-- reference data -----------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Country (
    Code        TEXT PRIMARY KEY,           -- ISO 3166 alpha-2
    Name        TEXT NOT NULL,
    RiskWeight  INTEGER NOT NULL DEFAULT 0  -- points a declaration from here starts with (sample weights)
);

CREATE TABLE IF NOT EXISTS Currency (
    Code   TEXT PRIMARY KEY,                -- ISO 4217
    Name   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ExchangeRate (
    Id            INTEGER PRIMARY KEY,
    CurrencyCode  TEXT NOT NULL REFERENCES Currency(Code),
    WeekOf        DATE NOT NULL,            -- the Monday the weekly rate starts
    Rate          REAL NOT NULL             -- Bermuda dollars for one unit
);

CREATE TABLE IF NOT EXISTS Agency (
    Code   TEXT PRIMARY KEY,                -- HLTH, ENV, LIQ, POL
    Name   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Tariff (
    Code            TEXT PRIMARY KEY,       -- an HS-style heading, e.g. 2204.21
    Description     TEXT NOT NULL,
    Unit            TEXT NOT NULL DEFAULT 'u',   -- kg, l, u (units), m3
    DutyRate        REAL NOT NULL DEFAULT 0,     -- percent of the value (ad valorem)
    SpecificRate    REAL NOT NULL DEFAULT 0,     -- Bermuda dollars a unit (specific; both: compound)
    StepAbove       REAL NOT NULL DEFAULT 0,     -- a stepped rate: above this value ...
    RateAbove       REAL NOT NULL DEFAULT 0,     -- ... this percent (cars: 75 % to 10,000, 150 % above)
    AgencyCode      TEXT REFERENCES Agency(Code),   -- a permit from this agency is needed
    Prohibited      BOOLEAN NOT NULL DEFAULT 0,
    ReferencePrice  REAL NOT NULL DEFAULT 0      -- a typical value a unit: far below it is a valuation risk
);

CREATE TABLE IF NOT EXISTS PortOfEntry (
    Id            INTEGER PRIMARY KEY,
    Name          TEXT NOT NULL,
    Mode          TEXT NOT NULL,            -- S = Sea, A = Air
    WharfageRate  REAL NOT NULL DEFAULT 1.25,    -- percent of the customs value
    Latitude      REAL,
    Longitude     REAL
);

CREATE TABLE IF NOT EXISTS Carrier (
    Id      INTEGER PRIMARY KEY,
    Name    TEXT NOT NULL,                  -- shipping line, airline, or haulier (made up)
    Type    TEXT NOT NULL                   -- S = Shipping line, A = Airline, H = Haulier
);

CREATE TABLE IF NOT EXISTS Broker (
    Id             INTEGER PRIMARY KEY,
    Name           TEXT NOT NULL,
    LicenceNumber  TEXT NOT NULL,
    Active         BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Route (
    Id              INTEGER PRIMARY KEY,
    Name            TEXT NOT NULL,
    FromPortId      INTEGER NOT NULL REFERENCES PortOfEntry(Id),
    Destination     TEXT NOT NULL,
    Approved        BOOLEAN NOT NULL DEFAULT 0   -- registered with customs and approved
);

-- importers and their statements ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Importer (
    Id                INTEGER PRIMARY KEY,
    Name              TEXT NOT NULL,
    CustomsNumber     TEXT,                 -- the CAPS ID
    Registered        BOOLEAN NOT NULL DEFAULT 0,
    RegisteredSince   DATE,
    TrustedTrader     TEXT,                 -- AEO (authorized economic operator), or empty
    ComplianceBase    INTEGER NOT NULL DEFAULT 100,
    BondAmount        REAL NOT NULL DEFAULT 0,   -- what its open statements may owe
    OnStatement       BOOLEAN NOT NULL DEFAULT 0,   -- may pay monthly, on a statement
    ReliefApproved    BOOLEAN NOT NULL DEFAULT 0,   -- approved for duty relief (CPC 4071: charities ...)
    Parish            TEXT,
    PenaltyPoints     INTEGER DEFAULT 0,    -- (rule) from failed inspections
    CompliancePoints  INTEGER,              -- (rule) ComplianceBase - PenaltyPoints, not below 0
    DeclarationCount  INTEGER DEFAULT 0,    -- (rule)
    StatementBalance  REAL DEFAULT 0,       -- (rule) what its open statements owe
    YearDuty          REAL DEFAULT 0,       -- (rule) duty on its released declarations
    RequiredBond      REAL,                 -- (rule) 10 % of YearDuty, at least 10,000
    BondSufficient    BOOLEAN               -- (rule)
);

CREATE TABLE IF NOT EXISTS Statement (
    Id          INTEGER PRIMARY KEY,
    ImporterId  INTEGER NOT NULL REFERENCES Importer(Id),
    Period      TEXT NOT NULL,              -- YYYY-MM: the month's released declarations
    DueDate     DATE NOT NULL,              -- the 15th working day of the next month
    Status      TEXT NOT NULL DEFAULT 'O',  -- O = Open, C = Closed (paid)
    Total       REAL DEFAULT 0,             -- (rule) its declarations' amounts due
    Paid        REAL DEFAULT 0,             -- (rule) its payments
    Balance     REAL DEFAULT 0              -- (rule)
);

-- what arrives: the manifest -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Arrival (
    Id              INTEGER PRIMARY KEY,
    CarrierId       INTEGER NOT NULL REFERENCES Carrier(Id),
    PortOfEntryId   INTEGER NOT NULL REFERENCES PortOfEntry(Id),
    VoyageNumber    TEXT NOT NULL,          -- a ship's voyage or a flight
    ExpectedDate    DATE NOT NULL,
    ArrivedDate     DATE,                   -- empty until the ship docks or the aircraft lands
    WharfageRate    REAL                    -- (rule) copied from the port
);

CREATE TABLE IF NOT EXISTS MasterBill (
    Id             INTEGER PRIMARY KEY,
    ArrivalId      INTEGER NOT NULL REFERENCES Arrival(Id),
    Number         TEXT NOT NULL,           -- the ocean bill of lading or master air waybill
    Packages       INTEGER NOT NULL,        -- as manifested
    HouseCount     INTEGER DEFAULT 0,       -- (rule)
    HousePackages  INTEGER DEFAULT 0,       -- (rule) its house bills' packages
    ManifestMatch  BOOLEAN                  -- (rule) no house bills yet, or their packages add up
);

CREATE TABLE IF NOT EXISTS HouseBill (
    Id             INTEGER PRIMARY KEY,
    MasterBillId   INTEGER NOT NULL REFERENCES MasterBill(Id),
    Number         TEXT NOT NULL,
    Consignee      TEXT NOT NULL,
    Packages       INTEGER NOT NULL,
    GrossWeight    REAL,                    -- kg
    LadingDate     DATE NOT NULL,           -- loaded abroad
    SecurityFiled  DATE,                    -- the advance security filing (the "10+2" idea): a day before lading
    ArrivalId      INTEGER,                 -- (rule) copied from the master bill
    LateFiling     BOOLEAN                  -- (rule) filed less than a day before lading, or not at all
);

CREATE TABLE IF NOT EXISTS Container (
    Id           INTEGER PRIMARY KEY,
    ArrivalId    INTEGER NOT NULL REFERENCES Arrival(Id),
    Number       TEXT NOT NULL,
    Size         TEXT NOT NULL DEFAULT '20',
    SealNumber   TEXT NOT NULL,             -- the seal declared on the manifest
    SealIntact   BOOLEAN NOT NULL DEFAULT 1 -- as found on discharge
);

-- declarations ---------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Declaration (
    Id                 INTEGER PRIMARY KEY,
    ImporterId         INTEGER NOT NULL REFERENCES Importer(Id),
    BrokerId           INTEGER REFERENCES Broker(Id),
    ArrivalId          INTEGER NOT NULL REFERENCES Arrival(Id),
    HouseBillId        INTEGER REFERENCES HouseBill(Id),
    ContainerId        INTEGER REFERENCES Container(Id),
    CountryCode        TEXT NOT NULL REFERENCES Country(Code),   -- country of export
    ExchangeRateId     INTEGER NOT NULL REFERENCES ExchangeRate(Id),   -- the week's rate for the invoice currency
    StatementId        INTEGER REFERENCES Statement(Id),   -- paid monthly, on this statement
    MasterBillId       INTEGER REFERENCES MasterBill(Id),  -- (rule) copied from the house bill: the manifest check
    EntryNumber        TEXT NOT NULL,
    Kind               TEXT NOT NULL DEFAULT 'C',   -- C = Commercial, P = Personal (accompanied baggage, courier)
    Declarant          TEXT,               -- a personal declaration: R = Resident, V = Visitor
    Cpc                TEXT NOT NULL DEFAULT '4000',   -- Customs Procedure Code: 4000 home use, 4071 relief
    LodgedDate         DATE NOT NULL,
    Freight            REAL NOT NULL DEFAULT 0,      -- invoice currency: kept for the CIF value (statistics)
    Insurance          REAL NOT NULL DEFAULT 0,
    RandomDraw         REAL NOT NULL DEFAULT 1,      -- drawn when lodged, 0 to 1: under 0.03 sends it to red
    AuditFlag          BOOLEAN NOT NULL DEFAULT 0,   -- a trusted trader's entry chosen for audit after release
    Status             TEXT NOT NULL DEFAULT 'L',    -- L = Lodged, R = Released
    Rate               REAL,               -- (rule) the week's exchange rate
    CompliancePoints   INTEGER,            -- (rule) the importer's, copied when lodged: what it is risk-scored with
    WharfageRate       REAL,               -- (rule) copied from the arrival
    ReliefApproved     BOOLEAN,            -- (rule) the importer's
    LineCount          INTEGER DEFAULT 0,  -- (rule)
    TotalValue         REAL DEFAULT 0,     -- (rule) its lines' values in Bermuda dollars (FOB)
    CifValue           REAL,               -- (rule) + freight and insurance: statistics only
    TotalDuty          REAL DEFAULT 0,     -- (rule)
    TotalWharfage      REAL DEFAULT 0,     -- (rule)
    Allowance          REAL DEFAULT 0,     -- (rule) a personal declaration: 300 for a resident, 50 for a visitor
    AllowanceDuty      REAL DEFAULT 0,     -- (rule) the duty the allowance takes off
    AmountDue          REAL DEFAULT 0,     -- (rule) duty - allowance + wharfage
    Paid               REAL DEFAULT 0,     -- (rule) its own payments
    Balance            REAL DEFAULT 0,     -- (rule)
    ProhibitedLines    INTEGER DEFAULT 0,  -- (rule)
    PermitsMissing     INTEGER DEFAULT 0,  -- (rule) lines needing an agency permit without an approved one
    UndervaluedLines   INTEGER DEFAULT 0,  -- (rule) lines valued under half the reference price
    OpenHolds          INTEGER DEFAULT 0,  -- (rule)
    PassedChecks       INTEGER DEFAULT 0,  -- (rule) documentary checks and examinations passed
    PassedExams        INTEGER DEFAULT 0,  -- (rule) physical examinations passed
    FailedInspections  INTEGER DEFAULT 0,  -- (rule)
    Penalties          INTEGER DEFAULT 0,  -- (rule) compliance points its failed inspections cost
    RiskScore          INTEGER,            -- (rule)
    Lane               TEXT,               -- (rule) G green, Y yellow, R red, B blue
    ReleaseReason      TEXT,               -- (rule) the first reason it cannot be released; empty: releasable
    Releasable         BOOLEAN             -- (rule)
);

CREATE TABLE IF NOT EXISTS DeclarationLine (
    Id               INTEGER PRIMARY KEY,
    DeclarationId    INTEGER NOT NULL REFERENCES Declaration(Id),
    TariffCode       TEXT NOT NULL REFERENCES Tariff(Code),
    CountryCode      TEXT NOT NULL REFERENCES Country(Code),   -- origin
    Description      TEXT,
    Quantity         REAL NOT NULL,        -- in the tariff's unit
    InvoiceValue     REAL NOT NULL,        -- the price paid, in the invoice currency (FOB)
    ReliefClaimed    BOOLEAN NOT NULL DEFAULT 0,
    DutyRate         REAL,                 -- (rule) the tariff's, copied when declared
    SpecificRate     REAL,                 -- (rule) copied
    StepAbove        REAL,                 -- (rule) copied
    RateAbove        REAL,                 -- (rule) copied
    AgencyCode       TEXT,                 -- (rule) copied
    Prohibited       BOOLEAN,              -- (rule) copied
    ReferencePrice   REAL,                 -- (rule) copied
    Value            REAL,                 -- (rule) Bermuda dollars: InvoiceValue x the week's rate, rounded first
    Duty             REAL DEFAULT 0,       -- (rule)
    Wharfage         REAL DEFAULT 0,       -- (rule) none on personal baggage
    Undervalued      BOOLEAN,              -- (rule) under half the reference price a unit
    ApprovedPermits  INTEGER DEFAULT 0,    -- (rule)
    PermitMissing    BOOLEAN               -- (rule)
);

CREATE TABLE IF NOT EXISTS Permit (
    Id                 INTEGER PRIMARY KEY,
    DeclarationLineId  INTEGER NOT NULL REFERENCES DeclarationLine(Id),
    AgencyCode         TEXT NOT NULL REFERENCES Agency(Code),
    Number             TEXT NOT NULL,
    Status             TEXT NOT NULL DEFAULT 'P'   -- P = Pending, A = Approved, R = Refused
);

CREATE TABLE IF NOT EXISTS Hold (
    Id              INTEGER PRIMARY KEY,
    DeclarationId   INTEGER NOT NULL REFERENCES Declaration(Id),
    Source          TEXT NOT NULL DEFAULT 'C',   -- C = Customs, A = Agency
    AgencyCode      TEXT REFERENCES Agency(Code),
    Reason          TEXT NOT NULL,
    Open            BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Inspection (
    Id              INTEGER PRIMARY KEY,
    DeclarationId   INTEGER NOT NULL REFERENCES Declaration(Id),
    Kind            TEXT NOT NULL DEFAULT 'P',   -- D = Documentary check, X = X-ray scan, P = Physical examination
    InspectedDate   DATE NOT NULL,
    Officer         TEXT,
    Result          TEXT NOT NULL DEFAULT 'P',   -- P = Passed, F = Failed
    Notes           TEXT,
    Penalty         INTEGER DEFAULT 0            -- (rule) compliance points a failure costs the importer
);

CREATE TABLE IF NOT EXISTS Payment (
    Id              INTEGER PRIMARY KEY,
    DeclarationId   INTEGER REFERENCES Declaration(Id),   -- a declaration's own payment ...
    StatementId     INTEGER REFERENCES Statement(Id),     -- ... or a statement's
    PaidDate        DATE NOT NULL,
    Amount          REAL NOT NULL,
    Reference       TEXT
);

-- the gate -------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Truck (
    Id              INTEGER PRIMARY KEY,
    CarrierId       INTEGER NOT NULL REFERENCES Carrier(Id),   -- the haulier
    Registration    TEXT NOT NULL,
    TransponderId   TEXT NOT NULL,
    ClearedUntil    DATE
);

CREATE TABLE IF NOT EXISTS Driver (
    Id              INTEGER PRIMARY KEY,
    Name            TEXT NOT NULL,
    LicenceNumber   TEXT NOT NULL,
    ClearedUntil    DATE
);

CREATE TABLE IF NOT EXISTS Movement (
    Id                INTEGER PRIMARY KEY,
    DeclarationId     INTEGER NOT NULL REFERENCES Declaration(Id),
    ContainerId       INTEGER NOT NULL REFERENCES Container(Id),
    TruckId           INTEGER NOT NULL REFERENCES Truck(Id),
    DriverId          INTEGER NOT NULL REFERENCES Driver(Id),
    RouteId           INTEGER NOT NULL REFERENCES Route(Id),
    MoveDate          DATE NOT NULL,
    TransponderRead   BOOLEAN NOT NULL DEFAULT 1,
    ObservedSeal      TEXT,
    Status            TEXT NOT NULL DEFAULT 'W',   -- W = Waiting at the gate, O = Gate out
    Reason            TEXT,                  -- (rule) why it cannot go: the first check that fails
    Lane              TEXT                   -- (rule) G = through the gate, R = stop
);

CREATE INDEX IF NOT EXISTS LineByDeclaration ON DeclarationLine(DeclarationId);
