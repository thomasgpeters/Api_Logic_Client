-- Customs sample: the demo scenario - importers and their statements, what arrived (arrivals, bills of
-- lading, containers), declarations with their lines, permits, holds, inspections and payments, and the
-- trucks at the gate. purge_sample.sql removes it and keeps the lookup data. "Today" is 2026-11-26.
-- Declarations go in lodged and move to released at the end, as automatic release would; trucks wait at
-- the gate first, then go out.

INSERT INTO Importer (Id, Name, CustomsNumber, Registered, RegisteredSince, TrustedTrader, ComplianceBase, BondAmount, OnStatement, ReliefApproved, Parish) VALUES
 (1, 'Harbour Provisions Ltd',   'BDA-10021', 1, '2015-03-01', 'AEO', 100, 20000, 1, 0, 'Pembroke'),
 (2, 'Island Spirits Co.',       'BDA-10388', 1, '2018-06-01', NULL,  100, 10000, 1, 0, 'Paget'),
 (3, 'Somers Building Supply',   'BDA-11502', 1, '2020-01-15', NULL,  100, 0,     0, 0, 'St. George''s'),
 (4, 'Paget Electronics',        'BDA-12940', 1, '2026-09-01', NULL,  100, 0,     0, 0, 'Paget'),       -- new this year
 (5, 'Coral Reef Imports',       NULL,        0, NULL,         NULL,  100, 0,     0, 0, 'Sandys'),      -- not registered
 (6, 'Bermuda Hospital Trust',   'BDA-10007', 1, '2010-01-01', 'AEO', 100, 0,     0, 1, 'Paget'),       -- a charity: duty relief
 (7, 'Jane Outerbridge',         NULL,        0, NULL,         NULL,  100, 0,     0, 0, 'Smith''s');    -- a resident, home from a trip

INSERT INTO Statement (Id, ImporterId, Period, DueDate, Status) VALUES
 (1, 1, '2026-11', '2026-12-21', 'O'),
 (2, 2, '2026-11', '2026-12-21', 'O');

INSERT INTO Arrival (Id, CarrierId, PortOfEntryId, VoyageNumber, ExpectedDate, ArrivedDate) VALUES
 (1, 1, 1, 'BW-2611', '2026-11-24', '2026-11-24'),
 (2, 2, 1, 'CS-0412', '2026-11-27', NULL),            -- still at sea
 (3, 3, 3, 'NI-118',  '2026-11-25', '2026-11-25'),
 (4, 1, 2, 'BW-2612', '2026-11-26', '2026-11-26'),
 (5, 3, 3, 'NI-120',  '2026-11-26', '2026-11-26');    -- a passenger flight

INSERT INTO MasterBill (Id, ArrivalId, Number, Packages) VALUES
 (1, 1, 'BWL-MB-88120', 30),
 (2, 2, 'CSS-MB-4410', 40),
 (3, 3, 'NIA-118-77001', 12),
 (4, 4, 'BWL-MB-88305', 25),     -- its house bills add up to 22
 (5, 5, 'NIA-120-00091', 2);

INSERT INTO HouseBill (Id, MasterBillId, Number, Consignee, Packages, GrossWeight, LadingDate, SecurityFiled) VALUES
 (1, 1, 'HB-1001', 'Harbour Provisions Ltd',  20, 2400, '2026-11-18', '2026-11-15'),
 (2, 1, 'HB-1002', 'Island Spirits Co.',      10, 900,  '2026-11-18', '2026-11-17'),
 (3, 2, 'HB-2001', 'Harbour Provisions Ltd',  25, 2100, '2026-11-22', '2026-11-20'),
 (4, 2, 'HB-2002', 'Somers Building Supply',  15, 21000, '2026-11-22', '2026-11-22'),   -- filed on the day of lading: late
 (5, 3, 'HB-3001', 'Paget Electronics',       8,  160,  '2026-11-24', '2026-11-22'),
 (6, 3, 'HB-3002', 'Bermuda Hospital Trust',  4,  130,  '2026-11-23', '2026-11-21'),
 (7, 4, 'HB-4001', 'Coral Reef Imports',      12, 900,  '2026-11-21', '2026-11-20'),
 (8, 4, 'HB-4002', 'Island Spirits Co.',      10, 450,  '2026-11-21', '2026-11-19'),
 (9, 5, 'HB-5001', 'Jane Outerbridge',        2,  30,   '2026-11-26', '2026-11-25');

INSERT INTO Container (Id, ArrivalId, Number, Size, SealNumber, SealIntact) VALUES
 (1, 1, 'BWLU 482910 7', '40', 'BW1182034', 1),
 (2, 1, 'BWLU 377120 2', '20', 'BW1182099', 1),
 (3, 2, 'CSSU 910233 4', '40', 'CS0049925', 1),
 (4, 2, 'CSSU 118804 0', '20', 'CS0050112', 1),
 (5, 4, 'BWLU 600481 9', '20', 'BW1190007', 0),     -- the seal was found broken on discharge
 (6, 4, 'BWLU 600510 3', '20', 'BW1190011', 1);

INSERT INTO Declaration (Id, ImporterId, BrokerId, ArrivalId, HouseBillId, ContainerId, CountryCode, ExchangeRateId, StatementId, EntryNumber,
                         Kind, Declarant, Cpc, LodgedDate, Freight, Insurance, RandomDraw, AuditFlag, Status) VALUES
 (1, 1, 1,    1, 1, 1,    'US', 1, 1,    'BDA-26-10411', 'C', NULL, '4000', '2026-11-20', 1800, 120, 0.41, 0, 'R'),   -- lodged before arrival
 (2, 2, 2,    1, 2, 2,    'GB', 3, 2,    'BDA-26-10412', 'C', NULL, '4000', '2026-11-21', 900,  60,  0.55, 0, 'R'),
 (3, 1, 1,    2, 3, 3,    'US', 2, 1,    'BDA-26-10450', 'C', NULL, '4000', '2026-11-24', 2000, 150, 0.72, 0, 'L'),   -- the ship is still at sea
 (4, 3, 1,    2, 4, 4,    'CN', 2, NULL, 'BDA-26-10451', 'C', NULL, '4000', '2026-11-23', 3000, 200, 0.18, 0, 'L'),
 (5, 4, 2,    3, 5, NULL, 'CN', 2, NULL, 'BDA-26-10470', 'C', NULL, '4000', '2026-11-25', 400,  30,  0.66, 0, 'L'),
 (6, 6, 2,    3, 6, NULL, 'US', 2, NULL, 'BDA-26-10471', 'C', NULL, '4071', '2026-11-24', 600,  40,  0.88, 1, 'R'),   -- relief; chosen for audit
 (7, 5, 1,    4, 7, 5,    'CO', 2, NULL, 'BDA-26-10480', 'C', NULL, '4000', '2026-11-26', 1500, 100, 0.30, 0, 'L'),
 (8, 2, 2,    4, 8, 6,    'FR', 6, NULL, 'BDA-26-10481', 'C', NULL, '4000', '2026-11-26', 700,  50,  0.02, 0, 'L'),   -- drawn at random
 (9, 7, NULL, 5, 9, NULL, 'US', 2, NULL, 'BDA-26-P0091', 'P', 'R',  '4000', '2026-11-26', 0,    0,   0.50, 0, 'L');

INSERT INTO DeclarationLine (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, InvoiceValue, ReliefClaimed) VALUES
 (1,  1, '0201.10', 'US', 'Beef sirloin, chilled',         900,   8100, 0),
 (2,  1, '0402.10', 'US', 'Milk powder',                   350,   1400, 0),
 (3,  1, '0806.10', 'US', 'Red grapes',                    750,   2250, 0),
 (4,  2, '2208.30', 'GB', 'Single malt whisky',            120,   2400, 0),
 (5,  2, '2204.21', 'FR', 'Bordeaux, red',                 300,   1500, 0),
 (6,  3, '0201.10', 'US', 'Beef, ground',                  1000,  9000, 0),
 (7,  3, '1905.90', 'US', 'Bread rolls, frozen',           400,   1600, 0),
 (8,  4, '2523.29', 'CN', 'Portland cement',               20000, 3200, 0),
 (9,  4, '4407.11', 'CN', 'Pine boards',                   25,    7500, 0),
 (10, 5, '8471.30', 'CN', 'Laptops',                       20,    9000, 0),
 (11, 5, '8517.13', 'CN', 'Smartphones',                   50,    4000, 0),   -- 80 a phone: under half the reference
 (12, 6, '3004.90', 'US', 'Antibiotics',                   120,   6000, 1),
 (13, 7, '6403.99', 'CO', 'Sandals',                       200,   3000, 0),
 (14, 7, '9503.00', 'CN', 'Plastic toys',                  500,   1500, 0),
 (15, 7, '9302.00', 'CO', 'Pistols',                       2,     800,  0),
 (16, 8, '2204.21', 'FR', 'Rose, Provence',                400,   2000, 0),
 (17, 9, '6109.10', 'US', 'T-shirts',                      15,    450,  0),
 (18, 9, '6403.99', 'US', 'Running shoes',                 2,     120,  0);

INSERT INTO Permit (Id, DeclarationLineId, AgencyCode, Number, Status) VALUES
 (1, 1,  'ENV',  'ENV-26-3301',   'A'),
 (2, 3,  'ENV',  'ENV-26-3302',   'A'),
 (3, 4,  'LIQ',  'LIQ-2026-118',  'A'),
 (4, 5,  'LIQ',  'LIQ-2026-118',  'A'),
 (5, 6,  'ENV',  'ENV-26-3388',   'A'),
 (6, 12, 'HLTH', 'HLTH-26-0712',  'A'),
 (7, 16, 'LIQ',  'LIQ-2026-140',  'P');     -- pending

INSERT INTO Hold (Id, DeclarationId, Source, AgencyCode, Reason, Open) VALUES
 (1, 7, 'C', NULL, 'Seal BW1190007 found broken on discharge', 1);

INSERT INTO Payment (Id, DeclarationId, StatementId, PaidDate, Amount, Reference) VALUES
 (1, 6, NULL, '2026-11-25', 75.00, 'Wharfage, relief entry');

INSERT INTO Truck (Id, CarrierId, Registration, TransponderId, ClearedUntil) VALUES
 (1, 4, 'TK-1047', 'BX-00451', '2027-06-30'),
 (2, 4, 'TK-2210', 'BX-00452', '2027-03-31'),
 (3, 5, 'SM-330',  'BX-00610', '2026-10-31'),    -- its clearance lapsed
 (4, 6, 'PS-88',   'BX-00777', '2027-12-31'),
 (5, 6, 'PS-90',   'BX-00778', NULL);            -- never cleared

INSERT INTO Driver (Id, Name, LicenceNumber, ClearedUntil) VALUES
 (1, 'Andre Simmons',   'BDA-DL-20411', '2027-05-31'),
 (2, 'Keisha Robinson', 'BDA-DL-31877', '2027-02-28'),
 (3, 'Tomas Furtado',   'BDA-DL-11025', '2026-11-15'),
 (4, 'Priya Nair',      'BDA-DL-40990', '2027-08-31');

INSERT INTO Movement (Id, DeclarationId, ContainerId, TruckId, DriverId, RouteId, MoveDate, TransponderRead, ObservedSeal, Status) VALUES
 (1, 1, 1, 1, 1, 1, '2026-11-25', 1, 'BW1182034', 'O'),
 (2, 2, 2, 2, 2, 2, '2026-11-26', 1, 'BW1182099', 'O'),
 (3, 7, 5, 3, 3, 5, '2026-11-26', 1, 'BW1190000', 'W');   -- held goods: it waits
