-- Customs sample: lookup data - the reference data that stays (purge_sample.sql keeps it)
-- Plain INSERTs, only the columns people type: the columns the rules derive are left out.
-- build_db.py puts every row in through the business rules.

-- Country (8)
INSERT INTO "Country" (Code, Name) VALUES ('US', 'United States');
INSERT INTO "Country" (Code, Name) VALUES ('CA', 'Canada');
INSERT INTO "Country" (Code, Name) VALUES ('GB', 'United Kingdom');
INSERT INTO "Country" (Code, Name) VALUES ('DE', 'Germany');
INSERT INTO "Country" (Code, Name) VALUES ('FR', 'France');
INSERT INTO "Country" (Code, Name) VALUES ('IT', 'Italy');
INSERT INTO "Country" (Code, Name) VALUES ('CN', 'China');
INSERT INTO "Country" (Code, Name) VALUES ('JP', 'Japan');

-- Tariff (18)
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('0201.10', 'Beef, fresh or chilled', 5.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('0402.10', 'Milk powder', 0.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('0806.10', 'Grapes, fresh', 5.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('1905.90', 'Bread and pastry', 15.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('2204.21', 'Wine, in bottles', 40.0, 1);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('2208.30', 'Whisky', 50.0, 1);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('2402.20', 'Cigarettes', 75.0, 1);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('2523.29', 'Cement', 15.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('3004.90', 'Medicines', 0.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('4407.11', 'Lumber, pine', 10.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('6109.10', 'T-shirts, cotton', 25.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('6403.99', 'Footwear', 25.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('8471.30', 'Laptop computers', 10.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('8517.13', 'Smartphones', 10.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('8703.80', 'Cars, electric', 10.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('8708.99', 'Car parts', 25.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('9403.60', 'Furniture, wooden', 25.0, 0);
INSERT INTO "Tariff" (Code, Description, DutyRate, LicenceRequired) VALUES ('9503.00', 'Toys', 25.0, 0);

-- PortOfEntry (4)
INSERT INTO "PortOfEntry" (Id, Name, Mode, ProcessingFee, Latitude, Longitude) VALUES (1, 'Port of Hamilton', 'S', 30.0, 32.2949, -64.7838);
INSERT INTO "PortOfEntry" (Id, Name, Mode, ProcessingFee, Latitude, Longitude) VALUES (2, 'Royal Naval Dockyard', 'S', 30.0, 32.3275, -64.8333);
INSERT INTO "PortOfEntry" (Id, Name, Mode, ProcessingFee, Latitude, Longitude) VALUES (3, 'L.F. Wade International Airport', 'A', 20.0, 32.364, -64.6787);
INSERT INTO "PortOfEntry" (Id, Name, Mode, ProcessingFee, Latitude, Longitude) VALUES (4, 'St. George''s Harbour', 'S', 30.0, 32.381, -64.677);

-- Carrier (6)
INSERT INTO "Carrier" (Id, Name, Type) VALUES (1, 'Bluewater Lines', 'S');
INSERT INTO "Carrier" (Id, Name, Type) VALUES (2, 'Coral Sea Shipping', 'S');
INSERT INTO "Carrier" (Id, Name, Type) VALUES (3, 'Northern Isles Air Cargo', 'A');
INSERT INTO "Carrier" (Id, Name, Type) VALUES (4, 'Island Haulage Ltd', 'H');
INSERT INTO "Carrier" (Id, Name, Type) VALUES (5, 'Somerset Transport', 'H');
INSERT INTO "Carrier" (Id, Name, Type) VALUES (6, 'Pink Sand Logistics', 'H');

-- Route (6)
INSERT INTO "Route" (Id, Name, FromPortId, Destination, Approved) VALUES (1, 'Hamilton docks to Pembroke warehouses', 1, 'Pembroke', 1);
INSERT INTO "Route" (Id, Name, FromPortId, Destination, Approved) VALUES (2, 'Hamilton docks to Paget', 1, 'Paget', 1);
INSERT INTO "Route" (Id, Name, FromPortId, Destination, Approved) VALUES (3, 'Hamilton docks to Warwick', 1, 'Warwick', 1);
INSERT INTO "Route" (Id, Name, FromPortId, Destination, Approved) VALUES (4, 'Dockyard to Sandys', 2, 'Sandys', 1);
INSERT INTO "Route" (Id, Name, FromPortId, Destination, Approved) VALUES (5, 'Hamilton docks to Devonshire via Middle Road', 1, 'Devonshire', 0);
INSERT INTO "Route" (Id, Name, FromPortId, Destination, Approved) VALUES (6, 'Airport to Pembroke', 3, 'Pembroke', 1);
