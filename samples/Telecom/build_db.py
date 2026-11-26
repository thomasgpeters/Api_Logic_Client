#!/usr/bin/env python3
"""Build the Telecom sample database: samples/Telecom/telecom.sqlite

    python3 samples/Telecom/build_db.py [out.sqlite]

The tables come from schema.sql. Every row goes in through the business rules (telecom_rules.py, run by
tools/logic_reference.py's engine - the same engine as LogicBank for FutureBasic), so every price, total
and count in the file is what the rules computed; a seed row a rule refuses stops the build.

Northstar Mobile and its partner networks are made up; the countries are real. "Today" is 2026-11-26.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
sys.path.insert(0, HERE)
import sqlite3                                   # noqa: E402
from logic_reference import Data, Logic          # noqa: E402
import telecom_rules                              # noqa: E402

ZONES = [  # Id, Name, Markup
    (1, 'North America', 1.0), (2, 'Europe', 1.6), (3, 'Asia-Pacific', 1.8),
    (4, 'Latin America', 1.7), (5, 'Middle East & Africa', 2.0)]

COUNTRIES = [  # Code, Name, Zone, Latitude, Longitude
    ('US', 'United States', 1, 39.83, -98.58), ('CA', 'Canada', 1, 56.13, -106.35), ('MX', 'Mexico', 1, 23.63, -102.55),
    ('GB', 'United Kingdom', 2, 54.0, -2.0), ('FR', 'France', 2, 46.6, 2.2), ('DE', 'Germany', 2, 51.2, 10.4),
    ('IT', 'Italy', 2, 42.8, 12.6), ('ES', 'Spain', 2, 40.2, -3.7), ('PT', 'Portugal', 2, 39.6, -8.0),
    ('NL', 'Netherlands', 2, 52.1, 5.3), ('IE', 'Ireland', 2, 53.4, -8.2), ('CH', 'Switzerland', 2, 46.8, 8.2),
    ('GR', 'Greece', 2, 39.1, 21.8), ('AT', 'Austria', 2, 47.5, 14.6), ('SE', 'Sweden', 2, 60.1, 18.6),
    ('JP', 'Japan', 3, 36.2, 138.3), ('KR', 'South Korea', 3, 35.9, 127.8), ('AU', 'Australia', 3, -25.3, 133.8),
    ('NZ', 'New Zealand', 3, -40.9, 174.9), ('SG', 'Singapore', 3, 1.35, 103.8), ('TH', 'Thailand', 3, 15.9, 100.99),
    ('IN', 'India', 3, 20.6, 78.96),
    ('BR', 'Brazil', 4, -14.2, -51.9), ('AR', 'Argentina', 4, -38.4, -63.6), ('CL', 'Chile', 4, -35.7, -71.5),
    ('PE', 'Peru', 4, -9.2, -75.0), ('CO', 'Colombia', 4, 4.6, -74.3), ('CR', 'Costa Rica', 4, 9.75, -83.75),
    ('AE', 'United Arab Emirates', 5, 23.4, 53.8), ('ZA', 'South Africa', 5, -30.6, 22.9), ('EG', 'Egypt', 5, 26.8, 30.8),
    ('MA', 'Morocco', 5, 31.8, -7.1), ('IL', 'Israel', 5, 31.0, 34.85), ('KE', 'Kenya', 5, -0.02, 37.9)]

NETWORKS = [  # Id, Name (made up), Country, Technology, MCCMNC
    (1, 'Maple Wave', 'CA', '5G', '302-901'), (2, 'Azteca Conecta', 'MX', '5G', '334-901'),
    (3, 'Albion Mobile', 'GB', '5G', '234-901'), (4, 'Thames Wireless', 'GB', '4G', '234-902'),
    (5, 'Mistral Telecom', 'FR', '5G', '208-901'), (6, 'Rheinfunk', 'DE', '5G', '262-901'),
    (7, 'Vesuvio Mobile', 'IT', '5G', '222-901'), (8, 'Sol Movil', 'ES', '5G', '214-901'),
    (9, 'Atlantico Net', 'PT', '4G', '268-901'), (10, 'Polder Telecom', 'NL', '5G', '204-901'),
    (11, 'Shamrock Wireless', 'IE', '5G', '272-901'), (12, 'Alpenglow Telecom', 'CH', '5G', '228-901'),
    (13, 'Aegean Mobile', 'GR', '4G', '202-901'), (14, 'Danube Connect', 'AT', '5G', '232-901'),
    (15, 'Nordljus', 'SE', '5G', '240-901'), (16, 'Sakura Signal', 'JP', '5G', '440-901'),
    (17, 'Hanbit Telecom', 'KR', '5G', '450-901'), (18, 'Southern Cross Mobile', 'AU', '5G', '505-901'),
    (19, 'Kiwi Wave', 'NZ', '4G', '530-901'), (20, 'Merlion Net', 'SG', '5G', '525-901'),
    (21, 'Siam Signal', 'TH', '4G', '520-901'), (22, 'Monsoon Mobile', 'IN', '4G', '404-901'),
    (23, 'Ipanema Telecom', 'BR', '4G', '724-901'), (24, 'Pampas Movil', 'AR', '4G', '722-901'),
    (25, 'Andes Conecta', 'CL', '4G', '730-901'), (26, 'Inca Net', 'PE', '4G', '716-901'),
    (27, 'Cafe Celular', 'CO', '4G', '732-901'), (28, 'Pura Vida Movil', 'CR', '4G', '712-901'),
    (29, 'Falcon Telecom', 'AE', '5G', '424-901'), (30, 'Protea Mobile', 'ZA', '4G', '655-901'),
    (31, 'Nile Connect', 'EG', '4G', '602-901'), (32, 'Atlas Mobile', 'MA', '4G', '604-901'),
    (33, 'Galil Net', 'IL', '5G', '425-901'), (34, 'Sakura Mobile Two', 'JP', '4G', '440-902')]
# Kenya has no partner network: a trip there is refused ("no service")

AGREEMENTS = [  # Id, Network, ValidFrom, ValidTo, per GB, per minute, per text
    (1, 1, '2026-01-01', '2027-12-31', 2.00, 0.05, 0.01), (2, 2, '2026-01-01', '2027-12-31', 2.50, 0.06, 0.01),
    (3, 3, '2026-01-01', '2027-12-31', 4.00, 0.10, 0.03), (4, 4, '2026-01-01', '2027-12-31', 3.20, 0.12, 0.03),
    (5, 5, '2026-01-01', '2027-12-31', 4.50, 0.11, 0.03), (6, 6, '2026-01-01', '2027-12-31', 4.20, 0.10, 0.03),
    (7, 7, '2026-01-01', '2027-12-31', 4.80, 0.12, 0.04), (8, 8, '2026-01-01', '2027-12-31', 4.40, 0.11, 0.03),
    (9, 9, '2026-01-01', '2027-12-31', 4.60, 0.12, 0.04), (10, 10, '2026-01-01', '2027-12-31', 4.10, 0.10, 0.03),
    (11, 11, '2026-01-01', '2027-12-31', 4.30, 0.11, 0.03), (12, 12, '2026-01-01', '2027-12-31', 7.50, 0.25, 0.06),
    (13, 13, '2026-01-01', '2027-12-31', 5.20, 0.14, 0.04), (14, 14, '2026-01-01', '2027-12-31', 4.40, 0.11, 0.03),
    (15, 15, '2026-01-01', '2027-12-31', 4.00, 0.10, 0.03), (16, 16, '2026-01-01', '2027-12-31', 6.00, 0.20, 0.05),
    (17, 17, '2026-01-01', '2027-12-31', 5.50, 0.18, 0.05), (18, 18, '2026-01-01', '2027-12-31', 6.50, 0.22, 0.06),
    (19, 19, '2026-01-01', '2027-12-31', 7.00, 0.24, 0.06), (20, 20, '2026-01-01', '2027-12-31', 5.00, 0.15, 0.04),
    (21, 21, '2026-01-01', '2027-12-31', 3.80, 0.14, 0.03), (22, 22, '2026-01-01', '2027-12-31', 3.00, 0.12, 0.02),
    (23, 23, '2026-01-01', '2027-12-31', 5.50, 0.20, 0.05), (24, 24, '2026-01-01', '2027-12-31', 5.80, 0.22, 0.05),
    (25, 25, '2026-01-01', '2027-12-31', 5.60, 0.20, 0.05), (26, 26, '2026-01-01', '2027-12-31', 6.20, 0.24, 0.06),
    (27, 27, '2026-01-01', '2027-12-31', 5.40, 0.20, 0.05), (28, 28, '2026-01-01', '2027-12-31', 6.80, 0.26, 0.06),
    (29, 29, '2026-01-01', '2027-12-31', 8.00, 0.30, 0.08), (30, 30, '2026-01-01', '2027-12-31', 7.20, 0.28, 0.07),
    (31, 31, '2026-01-01', '2027-12-31', 6.50, 0.25, 0.06), (32, 32, '2026-01-01', '2027-12-31', 6.80, 0.26, 0.06),
    (33, 33, '2026-01-01', '2027-12-31', 7.50, 0.28, 0.07), (34, 34, '2026-01-01', '2027-12-31', 6.40, 0.21, 0.05),
    (35, 16, '2024-01-01', '2025-12-31', 8.00, 0.30, 0.08)]   # Sakura Signal's earlier agreement (ended)

PREFERRED = {  # country -> its preferred (current, cheapest) agreement
    'CA': 1, 'MX': 2, 'GB': 4, 'FR': 5, 'DE': 6, 'IT': 7, 'ES': 8, 'PT': 9, 'NL': 10, 'IE': 11, 'CH': 12, 'GR': 13,
    'AT': 14, 'SE': 15, 'JP': 16, 'KR': 17, 'AU': 18, 'NZ': 19, 'SG': 20, 'TH': 21, 'IN': 22, 'BR': 23, 'AR': 24,
    'CL': 25, 'PE': 26, 'CO': 27, 'CR': 28, 'AE': 29, 'ZA': 30, 'EG': 31, 'MA': 32, 'IL': 33}

OFFERS = [  # Id, Name, DataGB, Minutes, Texts, MonthlyPrice, MaxLines, home Zone  (None = unlimited)
    (1, 'Essentials', 5, 500, None, 35.0, 1, 1), (2, 'Plus', 25, None, None, 55.0, 1, 1),
    (3, 'Unlimited', None, None, None, 75.0, 1, 1), (4, 'Family Share', 50, None, None, 120.0, 5, 1),
    (5, 'Business Pro', 100, None, None, 200.0, 10, 1)]

CUSTOMERS = [  # Id, Name, Type, Email, City, State  (made up)
    (1, 'Maria Delgado', 'P', 'maria.delgado@example.com', 'Austin', 'TX'),
    (2, 'The Okafor Family', 'P', 'okafor.family@example.com', 'Columbus', 'OH'),
    (3, 'Chen Wei', 'P', 'chen.wei@example.com', 'San Jose', 'CA'),
    (4, 'Harbor Freight Logistics', 'B', 'accounts@harborfreight.example.com', 'Seattle', 'WA'),
    (5, 'Priya Raman', 'P', 'priya.raman@example.com', 'Edison', 'NJ'),
    (6, 'Lucas Moreau', 'P', 'lucas.moreau@example.com', 'New Orleans', 'LA'),
    (7, 'Summit Design Studio', 'B', 'office@summitdesign.example.com', 'Denver', 'CO'),
    (8, 'Hannah Becker', 'P', 'hannah.becker@example.com', 'Milwaukee', 'WI'),
    (9, 'The Silva Family', 'P', 'silva.family@example.com', 'Miami', 'FL'),
    (10, 'Kenji Watanabe', 'P', 'kenji.watanabe@example.com', 'Portland', 'OR'),
    (11, 'Grace Mensah', 'P', 'grace.mensah@example.com', 'Atlanta', 'GA'),
    (12, 'Blue Ridge Outfitters', 'B', 'team@blueridge.example.com', 'Asheville', 'NC')]

ACCOUNTS = [  # Id, Customer, AccountNumber, Status, CreditLimit
    (1, 1, 'NS-100101', 'A', 400), (2, 2, 'NS-100102', 'A', 800), (3, 3, 'NS-100103', 'A', 300),
    (4, 4, 'NS-100104', 'A', 3000), (5, 5, 'NS-100105', 'A', 500), (6, 6, 'NS-100106', 'A', 250),
    (7, 7, 'NS-100107', 'A', 2000), (8, 8, 'NS-100108', 'A', 400), (9, 9, 'NS-100109', 'A', 900),
    (10, 10, 'NS-100110', 'A', 600), (11, 11, 'NS-100111', 'A', 150), (12, 12, 'NS-100112', 'S', 1000),
    (13, 3, 'NS-100113', 'A', 200)]   # Chen Wei has a second account for a work phone

PLANS = [  # Id, Account, Offer, StartDate
    (1, 1, 3, '2025-03-01'), (2, 2, 4, '2024-06-15'), (3, 3, 2, '2025-09-01'), (4, 4, 5, '2023-01-10'),
    (5, 5, 3, '2026-02-01'), (6, 6, 1, '2026-05-20'), (7, 7, 5, '2024-11-01'), (8, 8, 2, '2025-07-07'),
    (9, 9, 4, '2025-01-01'), (10, 10, 3, '2026-08-01'), (11, 11, 1, '2026-10-01'), (12, 12, 5, '2022-04-01'),
    (13, 13, 1, '2026-01-15')]

PHONES = [  # Id, Plan, Number, Device, SIM, Status
    (1, 1, '512-555-0101', 'iPhone 17', '8901-0001', 'A'),
    (2, 2, '614-555-0102', 'iPhone 17 Pro', '8901-0002', 'A'), (3, 2, '614-555-0103', 'iPhone 16', '8901-0003', 'A'),
    (4, 2, '614-555-0104', 'Pixel 10', '8901-0004', 'A'), (5, 2, '614-555-0105', 'iPhone SE', '8901-0005', 'S'),
    (6, 3, '408-555-0106', 'Pixel 10 Pro', '8901-0006', 'A'),
    (7, 4, '206-555-0107', 'iPhone 17', '8901-0007', 'A'), (8, 4, '206-555-0108', 'iPhone 17', '8901-0008', 'A'),
    (9, 4, '206-555-0109', 'Galaxy S26', '8901-0009', 'A'), (10, 4, '206-555-0110', 'Galaxy S26', '8901-0010', 'A'),
    (11, 5, '732-555-0111', 'iPhone 17 Pro Max', '8901-0011', 'A'),
    (12, 6, '504-555-0112', 'iPhone 16e', '8901-0012', 'A'),
    (13, 7, '303-555-0113', 'iPhone 17 Pro', '8901-0013', 'A'), (14, 7, '303-555-0114', 'iPhone 17 Pro', '8901-0014', 'A'),
    (15, 7, '303-555-0115', 'iPad Pro', '8901-0015', 'A'),
    (16, 8, '414-555-0116', 'Pixel 10', '8901-0016', 'A'),
    (17, 9, '305-555-0117', 'iPhone 17', '8901-0017', 'A'), (18, 9, '305-555-0118', 'iPhone 16', '8901-0018', 'A'),
    (19, 9, '305-555-0119', 'iPhone 16', '8901-0019', 'A'),
    (20, 10, '503-555-0120', 'iPhone 17 Pro', '8901-0020', 'A'),
    (21, 11, '404-555-0121', 'Galaxy A56', '8901-0021', 'A'),
    (22, 12, '828-555-0122', 'iPhone 15', '8901-0022', 'A'), (23, 12, '828-555-0123', 'iPhone 15', '8901-0023', 'A'),
    (24, 13, '408-555-0124', 'iPhone 16', '8901-0024', 'A')]

USAGE = [  # Id, Phone, Date, Country, Network (None: own network), GB, Minutes, Texts
    (1, 1, '2026-11-01', 'US', None, 12.4, 310, 220), (2, 2, '2026-11-01', 'US', None, 18.0, 120, 450),
    (3, 3, '2026-11-01', 'US', None, 15.5, 80, 900), (4, 4, '2026-11-01', 'US', None, 21.2, 60, 300),
    (5, 6, '2026-11-01', 'US', None, 27.8, 200, 150), (6, 11, '2026-11-01', 'US', None, 40.1, 420, 380),
    (7, 12, '2026-11-01', 'US', None, 4.2, 380, 120), (8, 16, '2026-11-01', 'US', None, 9.9, 140, 260),
    (9, 17, '2026-11-01', 'US', None, 14.0, 95, 510), (10, 18, '2026-11-01', 'US', None, 11.3, 70, 640),
    (11, 19, '2026-11-01', 'US', None, 8.6, 30, 820), (12, 20, '2026-11-01', 'US', None, 33.0, 260, 140),
    (13, 21, '2026-11-01', 'US', None, 3.1, 210, 95), (14, 24, '2026-11-01', 'US', None, 6.2, 150, 60),
    (15, 7, '2026-11-01', 'US', None, 22.5, 600, 200), (16, 13, '2026-11-01', 'US', None, 19.4, 450, 180),
    (17, 1, '2026-06-12', 'IT', 7, 2.1, 25, 40), (18, 11, '2026-11-20', 'JP', 16, 1.8, 15, 22)]

TRAVEL = [  # Id, Phone, Name, Start, End, Status to end in, legs [(Country, Arrive, Leave)]
    (1, 1, 'Italy in June', '2026-06-10', '2026-06-20', 'P', [('IT', '2026-06-10', '2026-06-20')]),
    (2, 2, 'Okafor summer in Europe', '2027-07-01', '2027-07-14', 'P',
     [('GB', '2027-07-01', '2027-07-05'), ('FR', '2027-07-06', '2027-07-10'), ('ES', '2027-07-11', '2027-07-14')]),
    (3, 6, 'Tokyo conference', '2027-03-02', '2027-03-08', 'Q', [('JP', '2027-03-02', '2027-03-08')]),
    (4, 7, 'Rotterdam port visit', '2027-01-12', '2027-01-16', 'P', [('NL', '2027-01-12', '2027-01-16')]),
    (5, 11, 'Japan and Korea', '2026-11-18', '2026-11-30', 'P',
     [('JP', '2026-11-18', '2026-11-25'), ('KR', '2026-11-26', '2026-11-30')]),
    (6, 12, 'Cancun long weekend', '2027-02-13', '2027-02-17', 'P', [('MX', '2027-02-13', '2027-02-17')]),
    (7, 13, 'Milan Design Week', '2027-04-19', '2027-04-25', 'P', [('IT', '2027-04-19', '2027-04-25')]),
    (8, 17, 'Silva family in Portugal and Brazil', '2027-06-20', '2027-07-10', 'Q',
     [('PT', '2027-06-20', '2027-06-30'), ('BR', '2027-07-01', '2027-07-10')]),
    (9, 20, 'Australia and New Zealand', '2027-01-05', '2027-01-25', 'Q',
     [('AU', '2027-01-05', '2027-01-15'), ('NZ', '2027-01-16', '2027-01-25')]),
    (10, 16, 'Oktoberfest', '2026-09-25', '2026-10-03', 'X', [('DE', '2026-09-25', '2026-10-03')])]


def must(ok, logic, what):
    if not ok:
        raise SystemExit(f'build_db: {what} was refused by the rules: {logic.message}')


def build(path):
    if os.path.exists(path):
        os.remove(path)
    db = sqlite3.connect(path)
    db.executescript(open(os.path.join(HERE, 'schema.sql')).read())
    db.close()
    data = Data(path)
    logic = Logic(data)
    telecom_rules.declare(logic)
    if not logic.activate():
        raise SystemExit('build_db: the rules did not activate: ' + '; '.join(logic.log))

    def add(entity, record, what):
        must(logic.insert(entity, dict(record)), logic, what)

    for i, name, markup in ZONES:
        add('Zone', {'Id': i, 'Name': name, 'Markup': markup}, f'zone {name}')
    for code, name, zone, lat, lon in COUNTRIES:
        add('Country', {'Code': code, 'Name': name, 'ZoneId': zone, 'Latitude': lat, 'Longitude': lon}, f'country {code}')
    for i, name, country, tech, mccmnc in NETWORKS:
        add('PartnerNetwork', {'Id': i, 'Name': name, 'CountryCode': country, 'Technology': tech, 'MCCMNC': mccmnc}, f'network {name}')
    for i, net, start, end, gb, minute, text in AGREEMENTS:
        add('RoamingAgreement', {'Id': i, 'PartnerNetworkId': net, 'ValidFrom': start, 'ValidTo': end,
                                 'RatePerGB': gb, 'RatePerMinute': minute, 'RatePerText': text}, f'agreement {i}')
    for code, agreement in PREFERRED.items():          # the rules price each country from its agreement
        must(logic.update('Country', {'Code': code, 'RoamingAgreementId': agreement}), logic, f'preferred agreement for {code}')
    for i, name, gb, minutes, texts, price, lines, zone in OFFERS:
        add('PlanOffer', {'Id': i, 'Name': name, 'DataGB': gb, 'Minutes': minutes, 'Texts': texts,
                          'MonthlyPrice': price, 'MaxLines': lines, 'ZoneId': zone}, f'offer {name}')
    for i, name, kind, email, city, state in CUSTOMERS:
        add('Customer', {'Id': i, 'Name': name, 'Type': kind, 'Email': email, 'City': city, 'State': state}, f'customer {name}')
    for i, customer, number, status, limit in ACCOUNTS:
        add('Account', {'Id': i, 'CustomerId': customer, 'AccountNumber': number, 'Status': status, 'CreditLimit': limit}, f'account {number}')
    for i, account, offer, start in PLANS:
        add('Plan', {'Id': i, 'AccountId': account, 'PlanOfferId': offer, 'StartDate': start}, f'plan {i}')
    for i, plan, number, device, sim, status in PHONES:
        add('Phone', {'Id': i, 'PlanId': plan, 'Number': number, 'Device': device, 'SIM': sim, 'Status': status}, f'phone {number}')
    for i, phone, day, country, net, gb, minutes, texts in USAGE:
        add('Usage', {'Id': i, 'PhoneId': phone, 'UsageDate': day, 'CountryCode': country, 'PartnerNetworkId': net,
                      'DataGB': gb, 'Minutes': minutes, 'Texts': texts}, f'usage {i}')
    leg_id = 0
    for i, phone, name, start, end, status, legs in TRAVEL:   # a quote first, its countries, then bought (or cancelled)
        add('TravelPlan', {'Id': i, 'PhoneId': phone, 'Name': name, 'StartDate': start, 'EndDate': end, 'Status': 'Q'}, f'travel plan {name}')
        for country, arrive, leave in legs:
            leg_id += 1
            add('TravelPlanCountry', {'Id': leg_id, 'TravelPlanId': i, 'CountryCode': country,
                                      'ArriveDate': arrive, 'LeaveDate': leave}, f'{name}: {country}')
        if status != 'Q':
            if status == 'X':
                must(logic.update('TravelPlan', {'Id': i, 'Status': 'P'}), logic, f'buying {name}')
            must(logic.update('TravelPlan', {'Id': i, 'Status': status}), logic, f'{name} -> {status}')
    data.db.close()
    return path


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'telecom.sqlite')
    build(out)
    print(f'build_db: {out}')
