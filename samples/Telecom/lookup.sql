-- Telecom sample: lookup data - the reference data that stays (purge_sample.sql keeps it)
-- Plain INSERTs, only the columns people type: the columns the rules derive are left out.
-- build_db.py puts every row in through the business rules.

-- Zone (5)
INSERT INTO "Zone" (Id, Name, Markup) VALUES (1, 'North America', 1.0);
INSERT INTO "Zone" (Id, Name, Markup) VALUES (2, 'Europe', 1.6);
INSERT INTO "Zone" (Id, Name, Markup) VALUES (3, 'Asia-Pacific', 1.8);
INSERT INTO "Zone" (Id, Name, Markup) VALUES (4, 'Latin America', 1.7);
INSERT INTO "Zone" (Id, Name, Markup) VALUES (5, 'Middle East & Africa', 2.0);

-- Country (34)
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('US', 'United States', 1, 39.83, -98.58, NULL);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('CA', 'Canada', 1, 56.13, -106.35, 1);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('MX', 'Mexico', 1, 23.63, -102.55, 2);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('GB', 'United Kingdom', 2, 54.0, -2.0, 4);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('FR', 'France', 2, 46.6, 2.2, 5);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('DE', 'Germany', 2, 51.2, 10.4, 6);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('IT', 'Italy', 2, 42.8, 12.6, 7);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('ES', 'Spain', 2, 40.2, -3.7, 8);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('PT', 'Portugal', 2, 39.6, -8.0, 9);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('NL', 'Netherlands', 2, 52.1, 5.3, 10);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('IE', 'Ireland', 2, 53.4, -8.2, 11);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('CH', 'Switzerland', 2, 46.8, 8.2, 12);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('GR', 'Greece', 2, 39.1, 21.8, 13);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('AT', 'Austria', 2, 47.5, 14.6, 14);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('SE', 'Sweden', 2, 60.1, 18.6, 15);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('JP', 'Japan', 3, 36.2, 138.3, 16);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('KR', 'South Korea', 3, 35.9, 127.8, 17);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('AU', 'Australia', 3, -25.3, 133.8, 18);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('NZ', 'New Zealand', 3, -40.9, 174.9, 19);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('SG', 'Singapore', 3, 1.35, 103.8, 20);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('TH', 'Thailand', 3, 15.9, 100.99, 21);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('IN', 'India', 3, 20.6, 78.96, 22);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('BR', 'Brazil', 4, -14.2, -51.9, 23);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('AR', 'Argentina', 4, -38.4, -63.6, 24);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('CL', 'Chile', 4, -35.7, -71.5, 25);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('PE', 'Peru', 4, -9.2, -75.0, 26);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('CO', 'Colombia', 4, 4.6, -74.3, 27);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('CR', 'Costa Rica', 4, 9.75, -83.75, 28);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('AE', 'United Arab Emirates', 5, 23.4, 53.8, 29);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('ZA', 'South Africa', 5, -30.6, 22.9, 30);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('EG', 'Egypt', 5, 26.8, 30.8, 31);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('MA', 'Morocco', 5, 31.8, -7.1, 32);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('IL', 'Israel', 5, 31.0, 34.85, 33);
INSERT INTO "Country" (Code, Name, ZoneId, Latitude, Longitude, RoamingAgreementId) VALUES ('KE', 'Kenya', 5, -0.02, 37.9, NULL);

-- PartnerNetwork (34)
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (1, 'Maple Wave', 'CA', '5G', '302-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (2, 'Azteca Conecta', 'MX', '5G', '334-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (3, 'Albion Mobile', 'GB', '5G', '234-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (4, 'Thames Wireless', 'GB', '4G', '234-902');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (5, 'Mistral Telecom', 'FR', '5G', '208-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (6, 'Rheinfunk', 'DE', '5G', '262-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (7, 'Vesuvio Mobile', 'IT', '5G', '222-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (8, 'Sol Movil', 'ES', '5G', '214-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (9, 'Atlantico Net', 'PT', '4G', '268-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (10, 'Polder Telecom', 'NL', '5G', '204-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (11, 'Shamrock Wireless', 'IE', '5G', '272-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (12, 'Alpenglow Telecom', 'CH', '5G', '228-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (13, 'Aegean Mobile', 'GR', '4G', '202-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (14, 'Danube Connect', 'AT', '5G', '232-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (15, 'Nordljus', 'SE', '5G', '240-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (16, 'Sakura Signal', 'JP', '5G', '440-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (17, 'Hanbit Telecom', 'KR', '5G', '450-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (18, 'Southern Cross Mobile', 'AU', '5G', '505-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (19, 'Kiwi Wave', 'NZ', '4G', '530-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (20, 'Merlion Net', 'SG', '5G', '525-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (21, 'Siam Signal', 'TH', '4G', '520-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (22, 'Monsoon Mobile', 'IN', '4G', '404-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (23, 'Ipanema Telecom', 'BR', '4G', '724-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (24, 'Pampas Movil', 'AR', '4G', '722-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (25, 'Andes Conecta', 'CL', '4G', '730-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (26, 'Inca Net', 'PE', '4G', '716-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (27, 'Cafe Celular', 'CO', '4G', '732-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (28, 'Pura Vida Movil', 'CR', '4G', '712-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (29, 'Falcon Telecom', 'AE', '5G', '424-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (30, 'Protea Mobile', 'ZA', '4G', '655-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (31, 'Nile Connect', 'EG', '4G', '602-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (32, 'Atlas Mobile', 'MA', '4G', '604-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (33, 'Galil Net', 'IL', '5G', '425-901');
INSERT INTO "PartnerNetwork" (Id, Name, CountryCode, Technology, MCCMNC) VALUES (34, 'Sakura Mobile Two', 'JP', '4G', '440-902');

-- RoamingAgreement (35)
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (1, 1, '2026-01-01', '2027-12-31', 2.0, 0.05, 0.01);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (2, 2, '2026-01-01', '2027-12-31', 2.5, 0.06, 0.01);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (3, 3, '2026-01-01', '2027-12-31', 4.0, 0.1, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (4, 4, '2026-01-01', '2027-12-31', 3.2, 0.12, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (5, 5, '2026-01-01', '2027-12-31', 4.5, 0.11, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (6, 6, '2026-01-01', '2027-12-31', 4.2, 0.1, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (7, 7, '2026-01-01', '2027-12-31', 4.8, 0.12, 0.04);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (8, 8, '2026-01-01', '2027-12-31', 4.4, 0.11, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (9, 9, '2026-01-01', '2027-12-31', 4.6, 0.12, 0.04);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (10, 10, '2026-01-01', '2027-12-31', 4.1, 0.1, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (11, 11, '2026-01-01', '2027-12-31', 4.3, 0.11, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (12, 12, '2026-01-01', '2027-12-31', 7.5, 0.25, 0.06);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (13, 13, '2026-01-01', '2027-12-31', 5.2, 0.14, 0.04);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (14, 14, '2026-01-01', '2027-12-31', 4.4, 0.11, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (15, 15, '2026-01-01', '2027-12-31', 4.0, 0.1, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (16, 16, '2026-01-01', '2027-12-31', 6.0, 0.2, 0.05);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (17, 17, '2026-01-01', '2027-12-31', 5.5, 0.18, 0.05);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (18, 18, '2026-01-01', '2027-12-31', 6.5, 0.22, 0.06);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (19, 19, '2026-01-01', '2027-12-31', 7.0, 0.24, 0.06);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (20, 20, '2026-01-01', '2027-12-31', 5.0, 0.15, 0.04);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (21, 21, '2026-01-01', '2027-12-31', 3.8, 0.14, 0.03);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (22, 22, '2026-01-01', '2027-12-31', 3.0, 0.12, 0.02);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (23, 23, '2026-01-01', '2027-12-31', 5.5, 0.2, 0.05);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (24, 24, '2026-01-01', '2027-12-31', 5.8, 0.22, 0.05);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (25, 25, '2026-01-01', '2027-12-31', 5.6, 0.2, 0.05);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (26, 26, '2026-01-01', '2027-12-31', 6.2, 0.24, 0.06);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (27, 27, '2026-01-01', '2027-12-31', 5.4, 0.2, 0.05);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (28, 28, '2026-01-01', '2027-12-31', 6.8, 0.26, 0.06);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (29, 29, '2026-01-01', '2027-12-31', 8.0, 0.3, 0.08);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (30, 30, '2026-01-01', '2027-12-31', 7.2, 0.28, 0.07);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (31, 31, '2026-01-01', '2027-12-31', 6.5, 0.25, 0.06);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (32, 32, '2026-01-01', '2027-12-31', 6.8, 0.26, 0.06);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (33, 33, '2026-01-01', '2027-12-31', 7.5, 0.28, 0.07);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (34, 34, '2026-01-01', '2027-12-31', 6.4, 0.21, 0.05);
INSERT INTO "RoamingAgreement" (Id, PartnerNetworkId, ValidFrom, ValidTo, RatePerGB, RatePerMinute, RatePerText) VALUES (35, 16, '2024-01-01', '2025-12-31', 8.0, 0.3, 0.08);

-- PlanOffer (5)
INSERT INTO "PlanOffer" (Id, Name, DataGB, Minutes, Texts, MonthlyPrice, MaxLines, ZoneId) VALUES (1, 'Essentials', 5.0, 500, NULL, 35.0, 1, 1);
INSERT INTO "PlanOffer" (Id, Name, DataGB, Minutes, Texts, MonthlyPrice, MaxLines, ZoneId) VALUES (2, 'Plus', 25.0, NULL, NULL, 55.0, 1, 1);
INSERT INTO "PlanOffer" (Id, Name, DataGB, Minutes, Texts, MonthlyPrice, MaxLines, ZoneId) VALUES (3, 'Unlimited', NULL, NULL, NULL, 75.0, 1, 1);
INSERT INTO "PlanOffer" (Id, Name, DataGB, Minutes, Texts, MonthlyPrice, MaxLines, ZoneId) VALUES (4, 'Family Share', 50.0, NULL, NULL, 120.0, 5, 1);
INSERT INTO "PlanOffer" (Id, Name, DataGB, Minutes, Texts, MonthlyPrice, MaxLines, ZoneId) VALUES (5, 'Business Pro', 100.0, NULL, NULL, 200.0, 10, 1);
