-- Customs sample: the lookup data - countries, currencies and the weekly rates, agencies, the tariff,
-- ports, carriers, brokers and approved routes. It stays when the sample data is purged (purge_sample.sql).
-- Sample duty rates and risk weights in Bermuda's style - NOT the official tariff or risk profile.

INSERT INTO Country (Code, Name, RiskWeight) VALUES
 ('US', 'United States', 0), ('CA', 'Canada', 0), ('GB', 'United Kingdom', 0), ('DE', 'Germany', 0),
 ('FR', 'France', 5), ('IT', 'Italy', 5), ('JP', 'Japan', 0), ('CN', 'China', 15),
 ('PA', 'Panama', 20), ('CO', 'Colombia', 30);

INSERT INTO Currency (Code, Name) VALUES ('USD', 'US dollar'), ('GBP', 'Pound sterling'), ('EUR', 'Euro'), ('CAD', 'Canadian dollar');

-- the weekly rates (Bermuda dollars for one unit; the Bermuda dollar is pegged to the US dollar)
INSERT INTO ExchangeRate (Id, CurrencyCode, WeekOf, Rate) VALUES
 (1, 'USD', '2026-11-16', 1.0),  (2, 'USD', '2026-11-23', 1.0),
 (3, 'GBP', '2026-11-16', 1.27), (4, 'GBP', '2026-11-23', 1.28),
 (5, 'EUR', '2026-11-16', 1.08), (6, 'EUR', '2026-11-23', 1.09),
 (7, 'CAD', '2026-11-16', 0.72), (8, 'CAD', '2026-11-23', 0.73);

INSERT INTO Agency (Code, Name) VALUES
 ('HLTH', 'Ministry of Health'),
 ('ENV',  'Department of Environment and Natural Resources'),
 ('LIQ',  'Liquor Licence Authority'),
 ('POL',  'Bermuda Police Service');

INSERT INTO Tariff (Code, Description, Unit, DutyRate, SpecificRate, StepAbove, RateAbove, AgencyCode, Prohibited, ReferencePrice) VALUES
 ('0201.10', 'Beef, fresh or chilled',    'kg', 5.0,   0,     0,     0,   'ENV',  0, 8.00),
 ('0402.10', 'Milk powder',               'kg', 0.0,   0,     0,     0,   NULL,   0, 4.00),
 ('0806.10', 'Grapes, fresh',             'kg', 5.0,   0,     0,     0,   'ENV',  0, 3.00),
 ('1905.90', 'Bread and pastry',          'kg', 15.0,  0,     0,     0,   NULL,   0, 4.00),
 ('2204.21', 'Wine, in bottles',          'l',  0.0,   8.50,  0,     0,   'LIQ',  0, 6.00),
 ('2208.30', 'Whisky',                    'l',  0.0,   30.00, 0,     0,   'LIQ',  0, 20.00),
 ('2402.20', 'Cigarettes (1,000)',        'u',  10.0,  250.00, 0,    0,   NULL,   0, 100.00),
 ('2523.29', 'Cement',                    'kg', 15.0,  0,     0,     0,   NULL,   0, 0.15),
 ('3004.90', 'Medicines',                 'kg', 0.0,   0,     0,     0,   'HLTH', 0, 50.00),
 ('4407.11', 'Lumber, pine',              'm3', 10.0,  0,     0,     0,   NULL,   0, 300.00),
 ('4901.99', 'Books',                     'u',  0.0,   0,     0,     0,   NULL,   0, 10.00),
 ('6109.10', 'T-shirts, cotton',          'u',  6.5,   0,     0,     0,   NULL,   0, 4.00),
 ('6403.99', 'Footwear',                  'u',  25.0,  0,     0,     0,   NULL,   0, 20.00),
 ('8471.30', 'Laptop computers',          'u',  10.0,  0,     0,     0,   NULL,   0, 400.00),
 ('8517.13', 'Smartphones',               'u',  10.0,  0,     0,     0,   NULL,   0, 300.00),
 ('8703.23', 'Cars, petrol',              'u',  75.0,  0,     10000, 150, NULL,   0, 15000.00),
 ('8708.99', 'Car parts',                 'kg', 25.0,  0,     0,     0,   NULL,   0, 10.00),
 ('9302.00', 'Revolvers and pistols',     'u',  0.0,   0,     0,     0,   'POL',  1, 500.00),
 ('9403.60', 'Furniture, wooden',         'u',  25.0,  0,     0,     0,   NULL,   0, 150.00),
 ('9503.00', 'Toys',                      'u',  25.0,  0,     0,     0,   NULL,   0, 5.00);

INSERT INTO PortOfEntry (Id, Name, Mode, WharfageRate, Latitude, Longitude) VALUES
 (1, 'Port of Hamilton',                'S', 1.25, 32.2949, -64.7838),
 (2, 'Royal Naval Dockyard',            'S', 1.25, 32.3275, -64.8333),
 (3, 'L.F. Wade International Airport', 'A', 1.25, 32.3640, -64.6787),
 (4, 'St. George''s Harbour',           'S', 1.25, 32.3810, -64.6770);

INSERT INTO Carrier (Id, Name, Type) VALUES
 (1, 'Bluewater Lines', 'S'), (2, 'Coral Sea Shipping', 'S'), (3, 'Northern Isles Air Cargo', 'A'),
 (4, 'Island Haulage Ltd', 'H'), (5, 'Somerset Transport', 'H'), (6, 'Pink Sand Logistics', 'H');

INSERT INTO Broker (Id, Name, LicenceNumber, Active) VALUES
 (1, 'Front Street Customs Brokers', 'CB-014', 1),
 (2, 'Atlantic Clearing Ltd',        'CB-022', 1),
 (3, 'Ord Road Forwarding',          'CB-031', 0);

INSERT INTO Route (Id, Name, FromPortId, Destination, Approved) VALUES
 (1, 'Hamilton docks to Pembroke warehouses', 1, 'Pembroke', 1),
 (2, 'Hamilton docks to Paget', 1, 'Paget', 1),
 (3, 'Hamilton docks to Warwick', 1, 'Warwick', 1),
 (4, 'Dockyard to Sandys', 2, 'Sandys', 1),
 (5, 'Dockyard to Devonshire via Middle Road', 2, 'Devonshire', 0),
 (6, 'Airport to Pembroke', 3, 'Pembroke', 1);
