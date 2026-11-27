-- Telecom sample: sample data - the demo scenario (purge_sample.sql removes it)
-- Plain INSERTs, only the columns people type: the columns the rules derive are left out.
-- build_db.py puts every row in through the business rules.

-- Customer (12)
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (1, 'Maria Delgado', 'P', 'maria.delgado@example.com', 'Austin', 'TX');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (2, 'The Okafor Family', 'P', 'okafor.family@example.com', 'Columbus', 'OH');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (3, 'Chen Wei', 'P', 'chen.wei@example.com', 'San Jose', 'CA');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (4, 'Harbor Freight Logistics', 'B', 'accounts@harborfreight.example.com', 'Seattle', 'WA');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (5, 'Priya Raman', 'P', 'priya.raman@example.com', 'Edison', 'NJ');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (6, 'Lucas Moreau', 'P', 'lucas.moreau@example.com', 'New Orleans', 'LA');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (7, 'Summit Design Studio', 'B', 'office@summitdesign.example.com', 'Denver', 'CO');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (8, 'Hannah Becker', 'P', 'hannah.becker@example.com', 'Milwaukee', 'WI');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (9, 'The Silva Family', 'P', 'silva.family@example.com', 'Miami', 'FL');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (10, 'Kenji Watanabe', 'P', 'kenji.watanabe@example.com', 'Portland', 'OR');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (11, 'Grace Mensah', 'P', 'grace.mensah@example.com', 'Atlanta', 'GA');
INSERT INTO "Customer" (Id, Name, Type, Email, City, State) VALUES (12, 'Blue Ridge Outfitters', 'B', 'team@blueridge.example.com', 'Asheville', 'NC');

-- Account (13)
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (1, 1, 'NS-100101', 'A', 400.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (2, 2, 'NS-100102', 'A', 800.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (3, 3, 'NS-100103', 'A', 300.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (4, 4, 'NS-100104', 'A', 3000.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (5, 5, 'NS-100105', 'A', 500.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (6, 6, 'NS-100106', 'A', 250.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (7, 7, 'NS-100107', 'A', 2000.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (8, 8, 'NS-100108', 'A', 400.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (9, 9, 'NS-100109', 'A', 900.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (10, 10, 'NS-100110', 'A', 600.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (11, 11, 'NS-100111', 'A', 150.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (12, 12, 'NS-100112', 'S', 1000.0);
INSERT INTO "Account" (Id, CustomerId, AccountNumber, Status, CreditLimit) VALUES (13, 3, 'NS-100113', 'A', 200.0);

-- Plan (13)
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (1, 1, 3, '2025-03-01');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (2, 2, 4, '2024-06-15');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (3, 3, 2, '2025-09-01');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (4, 4, 5, '2023-01-10');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (5, 5, 3, '2026-02-01');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (6, 6, 1, '2026-05-20');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (7, 7, 5, '2024-11-01');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (8, 8, 2, '2025-07-07');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (9, 9, 4, '2025-01-01');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (10, 10, 3, '2026-08-01');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (11, 11, 1, '2026-10-01');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (12, 12, 5, '2022-04-01');
INSERT INTO "Plan" (Id, AccountId, PlanOfferId, StartDate) VALUES (13, 13, 1, '2026-01-15');

-- Phone (24)
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (1, 1, '512-555-0101', 'iPhone 17', '8901-0001', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (2, 2, '614-555-0102', 'iPhone 17 Pro', '8901-0002', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (3, 2, '614-555-0103', 'iPhone 16', '8901-0003', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (4, 2, '614-555-0104', 'Pixel 10', '8901-0004', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (5, 2, '614-555-0105', 'iPhone SE', '8901-0005', 'S');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (6, 3, '408-555-0106', 'Pixel 10 Pro', '8901-0006', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (7, 4, '206-555-0107', 'iPhone 17', '8901-0007', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (8, 4, '206-555-0108', 'iPhone 17', '8901-0008', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (9, 4, '206-555-0109', 'Galaxy S26', '8901-0009', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (10, 4, '206-555-0110', 'Galaxy S26', '8901-0010', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (11, 5, '732-555-0111', 'iPhone 17 Pro Max', '8901-0011', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (12, 6, '504-555-0112', 'iPhone 16e', '8901-0012', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (13, 7, '303-555-0113', 'iPhone 17 Pro', '8901-0013', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (14, 7, '303-555-0114', 'iPhone 17 Pro', '8901-0014', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (15, 7, '303-555-0115', 'iPad Pro', '8901-0015', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (16, 8, '414-555-0116', 'Pixel 10', '8901-0016', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (17, 9, '305-555-0117', 'iPhone 17', '8901-0017', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (18, 9, '305-555-0118', 'iPhone 16', '8901-0018', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (19, 9, '305-555-0119', 'iPhone 16', '8901-0019', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (20, 10, '503-555-0120', 'iPhone 17 Pro', '8901-0020', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (21, 11, '404-555-0121', 'Galaxy A56', '8901-0021', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (22, 12, '828-555-0122', 'iPhone 15', '8901-0022', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (23, 12, '828-555-0123', 'iPhone 15', '8901-0023', 'A');
INSERT INTO "Phone" (Id, PlanId, Number, Device, SIM, Status) VALUES (24, 13, '408-555-0124', 'iPhone 16', '8901-0024', 'A');

-- Usage (18)
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (1, 1, '2026-11-01', 'US', NULL, 12.4, 310, 220);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (2, 2, '2026-11-01', 'US', NULL, 18.0, 120, 450);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (3, 3, '2026-11-01', 'US', NULL, 15.5, 80, 900);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (4, 4, '2026-11-01', 'US', NULL, 21.2, 60, 300);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (5, 6, '2026-11-01', 'US', NULL, 27.8, 200, 150);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (6, 11, '2026-11-01', 'US', NULL, 40.1, 420, 380);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (7, 12, '2026-11-01', 'US', NULL, 4.2, 380, 120);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (8, 16, '2026-11-01', 'US', NULL, 9.9, 140, 260);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (9, 17, '2026-11-01', 'US', NULL, 14.0, 95, 510);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (10, 18, '2026-11-01', 'US', NULL, 11.3, 70, 640);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (11, 19, '2026-11-01', 'US', NULL, 8.6, 30, 820);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (12, 20, '2026-11-01', 'US', NULL, 33.0, 260, 140);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (13, 21, '2026-11-01', 'US', NULL, 3.1, 210, 95);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (14, 24, '2026-11-01', 'US', NULL, 6.2, 150, 60);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (15, 7, '2026-11-01', 'US', NULL, 22.5, 600, 200);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (16, 13, '2026-11-01', 'US', NULL, 19.4, 450, 180);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (17, 1, '2026-06-12', 'IT', 7, 2.1, 25, 40);
INSERT INTO "Usage" (Id, PhoneId, UsageDate, CountryCode, PartnerNetworkId, DataGB, Minutes, Texts) VALUES (18, 11, '2026-11-20', 'JP', 16, 1.8, 15, 22);

-- TravelPlan (10)
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (1, 1, 'Italy in June', '2026-06-10', '2026-06-20', 'P');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (2, 2, 'Okafor summer in Europe', '2027-07-01', '2027-07-14', 'P');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (3, 6, 'Tokyo conference', '2027-03-02', '2027-03-08', 'Q');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (4, 7, 'Rotterdam port visit', '2027-01-12', '2027-01-16', 'P');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (5, 11, 'Japan and Korea', '2026-11-18', '2026-11-30', 'P');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (6, 12, 'Cancun long weekend', '2027-02-13', '2027-02-17', 'P');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (7, 13, 'Milan Design Week', '2027-04-19', '2027-04-25', 'P');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (8, 17, 'Silva family in Portugal and Brazil', '2027-06-20', '2027-07-10', 'Q');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (9, 20, 'Australia and New Zealand', '2027-01-05', '2027-01-25', 'Q');
INSERT INTO "TravelPlan" (Id, PhoneId, Name, StartDate, EndDate, Status) VALUES (10, 16, 'Oktoberfest', '2026-09-25', '2026-10-03', 'X');

-- TravelPlanCountry (15)
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (1, 1, 'IT', '2026-06-10', '2026-06-20');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (2, 2, 'GB', '2027-07-01', '2027-07-05');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (3, 2, 'FR', '2027-07-06', '2027-07-10');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (4, 2, 'ES', '2027-07-11', '2027-07-14');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (5, 3, 'JP', '2027-03-02', '2027-03-08');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (6, 4, 'NL', '2027-01-12', '2027-01-16');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (7, 5, 'JP', '2026-11-18', '2026-11-25');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (8, 5, 'KR', '2026-11-26', '2026-11-30');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (9, 6, 'MX', '2027-02-13', '2027-02-17');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (10, 7, 'IT', '2027-04-19', '2027-04-25');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (11, 8, 'PT', '2027-06-20', '2027-06-30');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (12, 8, 'BR', '2027-07-01', '2027-07-10');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (13, 9, 'AU', '2027-01-05', '2027-01-15');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (14, 9, 'NZ', '2027-01-16', '2027-01-25');
INSERT INTO "TravelPlanCountry" (Id, TravelPlanId, CountryCode, ArriveDate, LeaveDate) VALUES (15, 10, 'DE', '2026-09-25', '2026-10-03');
