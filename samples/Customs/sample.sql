-- Customs sample: sample data - the demo scenario (purge_sample.sql removes it)
-- Plain INSERTs, only the columns people type: the columns the rules derive are left out.
-- build_db.py puts every row in through the business rules.

-- Importer (8)
INSERT INTO "Importer" (Id, Name, CustomsNumber, Registered, BondAmount, Parish) VALUES (1, 'Harbourside Grocers', 'BM-IMP-00412', 1, 5000.0, 'Pembroke');
INSERT INTO "Importer" (Id, Name, CustomsNumber, Registered, BondAmount, Parish) VALUES (2, 'Coral Reef Wines & Spirits', 'BM-IMP-00977', 1, 10000.0, 'Paget');
INSERT INTO "Importer" (Id, Name, CustomsNumber, Registered, BondAmount, Parish) VALUES (3, 'Bermuda Home Furnishings', 'BM-IMP-01208', 1, 0.0, 'Warwick');
INSERT INTO "Importer" (Id, Name, CustomsNumber, Registered, BondAmount, Parish) VALUES (4, 'Island Motors', 'BM-IMP-00031', 1, 20000.0, 'Devonshire');
INSERT INTO "Importer" (Id, Name, CustomsNumber, Registered, BondAmount, Parish) VALUES (5, 'Tech Corner', 'BM-IMP-01555', 1, 0.0, 'Pembroke');
INSERT INTO "Importer" (Id, Name, CustomsNumber, Registered, BondAmount, Parish) VALUES (6, 'J. Outerbridge', NULL, 0, 0.0, 'Sandys');
INSERT INTO "Importer" (Id, Name, CustomsNumber, Registered, BondAmount, Parish) VALUES (7, 'Sunrise Pharmacy', 'BM-IMP-00650', 1, 3000.0, 'Smith''s');
INSERT INTO "Importer" (Id, Name, CustomsNumber, Registered, BondAmount, Parish) VALUES (8, 'St. David''s Builders', 'BM-IMP-00888', 1, 0.0, 'St. George''s');

-- Arrival (5)
INSERT INTO "Arrival" (Id, CarrierId, PortOfEntryId, VoyageNumber, ArrivalDate) VALUES (1, 1, 1, 'BW-2611', '2026-11-20');
INSERT INTO "Arrival" (Id, CarrierId, PortOfEntryId, VoyageNumber, ArrivalDate) VALUES (2, 2, 1, 'CS-1124', '2026-11-24');
INSERT INTO "Arrival" (Id, CarrierId, PortOfEntryId, VoyageNumber, ArrivalDate) VALUES (3, 3, 3, 'NI-805', '2026-11-25');
INSERT INTO "Arrival" (Id, CarrierId, PortOfEntryId, VoyageNumber, ArrivalDate) VALUES (4, 1, 2, 'BW-2612', '2026-11-27');
INSERT INTO "Arrival" (Id, CarrierId, PortOfEntryId, VoyageNumber, ArrivalDate) VALUES (5, 2, 1, 'CS-1201', '2026-12-01');

-- Container (9)
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (1, 1, 'BWLU 482910 7', '40', 'BW1182033');
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (2, 1, 'BWLU 517733 2', '20', 'BW1182034');
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (3, 1, 'BWLU 600215 9', '40', 'BW1182035');
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (4, 2, 'CSQU 300118 4', '40', 'CS0049921');
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (5, 2, 'CSQU 300542 1', '20', 'CS0049922');
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (6, 3, 'AKE 70412 NI', 'AIR', 'NI-77310');
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (7, 4, 'BWLU 701122 5', '40', 'BW1190001');
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (8, 5, 'CSQU 310077 0', '40', 'CS0051150');
INSERT INTO "Container" (Id, ArrivalId, Number, Size, SealNumber) VALUES (9, 2, 'CSQU 300990 6', '20', 'CS0049925');

-- Declaration (10)
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (1, 1, 1, 1, 'BDA-26-10411', '2026-11-17', 'R');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (2, 2, 1, 2, 'BDA-26-10412', '2026-11-18', 'R');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (3, 3, 1, 3, 'BDA-26-10413', '2026-11-21', 'R');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (4, 4, 2, 4, 'BDA-26-10420', '2026-11-20', 'R');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (5, 5, 3, 6, 'BDA-26-10425', '2026-11-24', 'L');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (6, 6, 2, 5, 'BDA-26-10421', '2026-11-23', 'H');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (7, 2, 4, 7, 'BDA-26-10430', '2026-11-25', 'L');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (8, 7, 5, 8, 'BDA-26-10431', '2026-11-26', 'L');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (9, 8, 1, NULL, 'BDA-26-10414', '2026-11-16', 'R');
INSERT INTO "Declaration" (Id, ImporterId, ArrivalId, ContainerId, EntryNumber, LodgedDate, Status) VALUES (10, 1, 2, 9, 'BDA-26-10422', '2026-11-22', 'R');

-- DeclarationLine (18)
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (1, 1, '0201.10', 'US', 'Beef, chilled', 900.0, 8100.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (2, 1, '0806.10', 'US', 'Table grapes', 400.0, 1400.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (3, 1, '0402.10', 'CA', 'Milk powder', 300.0, 2250.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (4, 2, '2204.21', 'FR', 'Bordeaux, 75 cl', 600.0, 7200.0, 'LIQ-2026-118');
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (5, 2, '2208.30', 'GB', 'Single malt, 70 cl', 240.0, 6000.0, 'LIQ-2026-118');
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (6, 3, '9403.60', 'IT', 'Dining sets', 12.0, 14400.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (7, 3, '9403.60', 'CN', 'Bookcases', 30.0, 3600.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (8, 4, '8703.80', 'JP', 'Electric hatchback', 2.0, 64000.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (9, 4, '8708.99', 'JP', 'Brake assemblies', 40.0, 6000.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (10, 5, '8471.30', 'CN', 'Laptops', 40.0, 36000.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (11, 5, '8517.13', 'CN', 'Smartphones', 60.0, 42000.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (12, 6, '9503.00', 'US', 'Toys, assorted', 50.0, 900.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (13, 6, '6403.99', 'US', 'Running shoes', 20.0, 1600.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (14, 7, '2208.30', 'GB', 'Blended whisky, 1 l', 480.0, 9600.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (15, 8, '3004.90', 'US', 'Prescription medicines', 200.0, 18000.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (16, 9, '4407.11', 'CA', 'Pine lumber, bundles', 60.0, 21000.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (17, 9, '2523.29', 'US', 'Portland cement, bags', 800.0, 6400.0, NULL);
INSERT INTO "DeclarationLine" (Id, DeclarationId, TariffCode, CountryCode, Description, Quantity, Value, LicenceNumber) VALUES (18, 10, '1905.90', 'US', 'Frozen pastry', 300.0, 2700.0, NULL);

-- Payment (5)
INSERT INTO "Payment" (Id, DeclarationId, PaidDate, Amount, Reference) VALUES (1, 1, '2026-11-21', 505.0, 'RCPT-9001');
INSERT INTO "Payment" (Id, DeclarationId, PaidDate, Amount, Reference) VALUES (2, 3, '2026-11-21', 4530.0, 'RCPT-9002');
INSERT INTO "Payment" (Id, DeclarationId, PaidDate, Amount, Reference) VALUES (3, 9, '2026-11-21', 3090.0, 'RCPT-9003');
INSERT INTO "Payment" (Id, DeclarationId, PaidDate, Amount, Reference) VALUES (4, 10, '2026-11-21', 435.0, 'RCPT-9004');
INSERT INTO "Payment" (Id, DeclarationId, PaidDate, Amount, Reference) VALUES (5, 2, '2026-11-21', 2000.0, 'RCPT-9005');

-- Inspection (2)
INSERT INTO "Inspection" (Id, DeclarationId, InspectedDate, Officer, Result, Notes) VALUES (1, 3, '2026-11-22', 'M. Tucker', 'P', 'Lodged after arrival: inspected, contents as declared');
INSERT INTO "Inspection" (Id, DeclarationId, InspectedDate, Officer, Result, Notes) VALUES (2, 6, '2026-11-25', 'R. Wilson', 'F', 'Undeclared electronics found in the container');

-- Truck (5)
INSERT INTO "Truck" (Id, CarrierId, Registration, TransponderId, ClearedUntil) VALUES (1, 4, 'TK-1047', 'BX-00451', '2027-06-30');
INSERT INTO "Truck" (Id, CarrierId, Registration, TransponderId, ClearedUntil) VALUES (2, 4, 'TK-2210', 'BX-00452', '2027-03-31');
INSERT INTO "Truck" (Id, CarrierId, Registration, TransponderId, ClearedUntil) VALUES (3, 5, 'SM-330', 'BX-00610', '2026-10-31');
INSERT INTO "Truck" (Id, CarrierId, Registration, TransponderId, ClearedUntil) VALUES (4, 6, 'PS-88', 'BX-00777', '2027-12-31');
INSERT INTO "Truck" (Id, CarrierId, Registration, TransponderId, ClearedUntil) VALUES (5, 6, 'PS-90', 'BX-00778', NULL);

-- Driver (4)
INSERT INTO "Driver" (Id, Name, LicenceNumber, ClearedUntil) VALUES (1, 'Andre Simmons', 'BDA-DL-20411', '2027-05-31');
INSERT INTO "Driver" (Id, Name, LicenceNumber, ClearedUntil) VALUES (2, 'Keisha Robinson', 'BDA-DL-31877', '2027-02-28');
INSERT INTO "Driver" (Id, Name, LicenceNumber, ClearedUntil) VALUES (3, 'Tomas Furtado', 'BDA-DL-11025', '2026-11-15');
INSERT INTO "Driver" (Id, Name, LicenceNumber, ClearedUntil) VALUES (4, 'Priya Nair', 'BDA-DL-40990', '2027-08-31');

-- Movement (7)
INSERT INTO "Movement" (Id, DeclarationId, ContainerId, TruckId, DriverId, RouteId, MoveDate, TransponderRead, ObservedSeal, Status) VALUES (1, 1, 1, 1, 1, 1, '2026-11-21', 1, 'BW1182033', 'O');
INSERT INTO "Movement" (Id, DeclarationId, ContainerId, TruckId, DriverId, RouteId, MoveDate, TransponderRead, ObservedSeal, Status) VALUES (2, 2, 2, 2, 2, 2, '2026-11-21', 1, 'BW1182034', 'O');
INSERT INTO "Movement" (Id, DeclarationId, ContainerId, TruckId, DriverId, RouteId, MoveDate, TransponderRead, ObservedSeal, Status) VALUES (3, 3, 3, 1, 1, 3, '2026-11-23', 1, 'BW1182035', 'O');
INSERT INTO "Movement" (Id, DeclarationId, ContainerId, TruckId, DriverId, RouteId, MoveDate, TransponderRead, ObservedSeal, Status) VALUES (4, 4, 4, 4, 4, 5, '2026-11-25', 1, 'CS0049921', 'S');
INSERT INTO "Movement" (Id, DeclarationId, ContainerId, TruckId, DriverId, RouteId, MoveDate, TransponderRead, ObservedSeal, Status) VALUES (5, 10, 9, 2, 2, 1, '2026-11-25', 1, 'CS0049952', 'S');
INSERT INTO "Movement" (Id, DeclarationId, ContainerId, TruckId, DriverId, RouteId, MoveDate, TransponderRead, ObservedSeal, Status) VALUES (6, 10, 9, 3, 3, 1, '2026-11-26', 1, 'CS0049925', 'S');
INSERT INTO "Movement" (Id, DeclarationId, ContainerId, TruckId, DriverId, RouteId, MoveDate, TransponderRead, ObservedSeal, Status) VALUES (7, 6, 5, 4, 4, 4, '2026-11-26', 1, 'CS0049922', 'W');
