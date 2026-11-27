-- Telecom sample: a mobile carrier ("Northstar Mobile"), its customers, plans and phones, and
-- travel plans priced from its roaming agreements with partner networks abroad.
-- The source of truth for the tables; build_db.py makes telecom.sqlite from it.
-- Columns marked (rule) are maintained by the business rules (rules.md), never typed.
-- Names: made-up carrier and partner networks, real countries.

PRAGMA foreign_keys = ON;

-- the pricing world ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Zone (
    Id          INTEGER PRIMARY KEY,
    Name        TEXT NOT NULL,               -- North America, Europe, ...
    Markup      REAL NOT NULL DEFAULT 1.6    -- the carrier's markup on what a day costs it there
);

CREATE TABLE IF NOT EXISTS Country (
    Code                 TEXT PRIMARY KEY,   -- ISO 3166 alpha-2
    Name                 TEXT NOT NULL,
    ZoneId               INTEGER NOT NULL REFERENCES Zone(Id),
    Latitude             REAL,               -- for the Map view
    Longitude            REAL,
    RoamingAgreementId   INTEGER REFERENCES RoamingAgreement(Id),   -- the preferred agreement there
    CostPerDay           REAL,               -- (rule) a typical day at the preferred agreement's rates
    DayPrice             REAL                -- (rule) what a travel day there costs the customer
);

CREATE TABLE IF NOT EXISTS PartnerNetwork (
    Id           INTEGER PRIMARY KEY,
    Name         TEXT NOT NULL,              -- made up
    CountryCode  TEXT NOT NULL REFERENCES Country(Code),
    Technology   TEXT NOT NULL DEFAULT '5G', -- 4G / 5G
    MCCMNC       TEXT                        -- the network's code
);

CREATE TABLE IF NOT EXISTS RoamingAgreement (
    Id                INTEGER PRIMARY KEY,
    PartnerNetworkId  INTEGER NOT NULL REFERENCES PartnerNetwork(Id),
    ValidFrom         DATE NOT NULL,
    ValidTo           DATE NOT NULL,
    RatePerGB         REAL NOT NULL,         -- what the partner charges the carrier
    RatePerMinute     REAL NOT NULL,
    RatePerText       REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS PlanOffer (
    Id              INTEGER PRIMARY KEY,
    Name            TEXT NOT NULL,           -- the catalog: Essentials, Unlimited Plus, ...
    DataGB          REAL,                    -- empty: unlimited
    Minutes         INTEGER,                 -- empty: unlimited
    Texts           INTEGER,                 -- empty: unlimited
    MonthlyPrice    REAL NOT NULL,
    MaxLines        INTEGER NOT NULL DEFAULT 1,
    ZoneId          INTEGER NOT NULL REFERENCES Zone(Id)   -- the home zone: no roaming there
);

-- customers, accounts, plans, phones ---------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Customer (
    Id       INTEGER PRIMARY KEY,
    Name     TEXT NOT NULL,
    Type     TEXT NOT NULL DEFAULT 'P',      -- P = Personal, B = Business
    Email    TEXT,
    City     TEXT,
    State    TEXT
);

CREATE TABLE IF NOT EXISTS Account (
    Id              INTEGER PRIMARY KEY,
    CustomerId      INTEGER NOT NULL REFERENCES Customer(Id),
    AccountNumber   TEXT NOT NULL,
    Status          TEXT NOT NULL DEFAULT 'A',   -- A = Active, S = Suspended, C = Closed
    CreditLimit     REAL NOT NULL DEFAULT 500,
    MonthlyCharges  REAL DEFAULT 0,          -- (rule) its plans' monthly prices
    TravelCharges   REAL DEFAULT 0,          -- (rule) its phones' purchased travel plans
    Balance         REAL DEFAULT 0           -- (rule) MonthlyCharges + TravelCharges
);

CREATE TABLE IF NOT EXISTS Plan (
    Id              INTEGER PRIMARY KEY,
    AccountId       INTEGER NOT NULL REFERENCES Account(Id),
    PlanOfferId     INTEGER NOT NULL REFERENCES PlanOffer(Id),
    StartDate       DATE,
    MonthlyPrice    REAL,                    -- (rule) copied from the offer when the plan starts
    MaxLines        INTEGER,                 -- (rule) copied from the offer
    DataGB          REAL,                    -- (rule) copied from the offer: the shared allowance
    ZoneId          INTEGER REFERENCES Zone(Id),   -- (rule) the home zone, copied from the offer
    PhoneCount      INTEGER DEFAULT 0,       -- (rule) its phones
    DataUsedGB      REAL DEFAULT 0,          -- (rule) its phones' data
    DataOverGB      REAL DEFAULT 0,          -- (rule) data over the allowance
    TravelTotal     REAL DEFAULT 0           -- (rule) its phones' purchased travel plans
);

CREATE TABLE IF NOT EXISTS Phone (
    Id            INTEGER PRIMARY KEY,
    PlanId        INTEGER NOT NULL REFERENCES Plan(Id),   -- a phone is part of a plan
    Number        TEXT NOT NULL,
    Device        TEXT,
    SIM           TEXT,
    Status        TEXT NOT NULL DEFAULT 'A', -- A = Active, S = Suspended
    ZoneId        INTEGER REFERENCES Zone(Id),   -- (rule) the home zone, copied from the plan
    DataUsedGB    REAL DEFAULT 0,            -- (rule) its usage
    TravelTotal   REAL DEFAULT 0             -- (rule) its purchased travel plans
);

CREATE TABLE IF NOT EXISTS Usage (
    Id                INTEGER PRIMARY KEY,
    PhoneId           INTEGER NOT NULL REFERENCES Phone(Id),
    UsageDate         DATE NOT NULL,
    CountryCode       TEXT NOT NULL REFERENCES Country(Code),
    PartnerNetworkId  INTEGER REFERENCES PartnerNetwork(Id),   -- empty: the carrier's own network
    DataGB            REAL DEFAULT 0,
    Minutes           INTEGER DEFAULT 0,
    Texts             INTEGER DEFAULT 0
);

-- travel plans -------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS TravelPlan (
    Id            INTEGER PRIMARY KEY,
    PhoneId       INTEGER NOT NULL REFERENCES Phone(Id),
    Name          TEXT,                      -- "Italy in June"
    StartDate     DATE NOT NULL,
    EndDate       DATE NOT NULL,
    Status        TEXT NOT NULL DEFAULT 'Q', -- Q = Quote, P = Purchased, X = Cancelled
    ZoneId        INTEGER REFERENCES Zone(Id),   -- (rule) the phone's home zone, copied
    Days          INTEGER,                   -- (rule) EndDate - StartDate + 1
    CountryCount  INTEGER DEFAULT 0,         -- (rule) its countries
    Price         REAL DEFAULT 0             -- (rule) its countries' amounts
);

CREATE TABLE IF NOT EXISTS TravelPlanCountry (
    Id            INTEGER PRIMARY KEY,
    TravelPlanId  INTEGER NOT NULL REFERENCES TravelPlan(Id),
    CountryCode   TEXT NOT NULL REFERENCES Country(Code),
    ArriveDate    DATE NOT NULL,
    LeaveDate     DATE NOT NULL,
    Days          INTEGER,                   -- (rule) LeaveDate - ArriveDate + 1
    DayPrice      REAL,                      -- (rule) the country's day price, copied when the leg is added
    Included      BOOLEAN DEFAULT 0,         -- (rule) the country is in the plan's home zone
    Amount        REAL DEFAULT 0             -- (rule) 0 when included, else Days * DayPrice
);
