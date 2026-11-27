#!/usr/bin/env python3
"""The Customs sample's business rules, scenario by scenario, and proof that every rule is tested.

    python3 samples/Customs/test_rules.py           every scenario on a fresh copy of the sample database
    python3 samples/Customs/test_rules.py --prove   each rule left out in turn: some scenario must fail

The engine is tools/logic_reference.py's (LogicBank for FutureBasic, function for function); the rules are
customs_rules.py, the data build_db.py's. Nothing is written outside a temporary folder.
"""
import os
import sys
import tempfile
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
sys.path.insert(0, HERE)
import logic_reference                            # noqa: E402
from logic_reference import Data, Logic           # noqa: E402
import customs_rules                               # noqa: E402
import build_db                                    # noqa: E402


def open_logic(path):
    data = Data(path)
    logic = Logic(data)
    customs_rules.declare(logic)
    logic.activate()
    return data, logic


def one(data, sql, *args):
    row = data.db.execute(sql, args).fetchone()
    return None if row is None else (row[0] if len(row) == 1 else tuple(row))


def scenarios(base):
    """(name, ok, detail) for every scenario, each on its own copy of the built database"""
    results = []
    folder = tempfile.mkdtemp()

    def run(name, body):
        path = os.path.join(folder, f'{len(results)}.sqlite')
        shutil.copy(base, path)
        data, logic = open_logic(path)
        try:
            ok, detail = body(data, logic)
        except Exception as e:
            ok, detail = False, f'{type(e).__name__}: {e}'
        data.db.close()
        results.append((name, bool(ok), detail))

    D = lambda d, i, cols: one(d, f'select {cols} from Declaration where Id={i}')
    I = lambda d, i, cols: one(d, f'select {cols} from Importer where Id={i}')
    M = lambda d, i: one(d, f'select Lane, Reason from Movement where Id={i}')
    why = lambda d, i: D(d, i, 'ReleaseReason')

    def steps(*changes):
        """apply (verb, table, record) in turn; returns (ok, message)"""
        def apply(l):
            for verb, table, record in changes:
                if not getattr(l, verb)(table, record):
                    return False, l.message
            return True, ''
        return apply

    def refused(verb, table, record, text):
        def body(d, l):
            ok = getattr(l, verb)(table, record)
            return (not ok) and text in l.message, l.message
        return body

    def reason_after(i, text, *changes):
        """after the changes, the declaration's release reason contains text ('' = releasable)"""
        def body(d, l):
            ok, message = steps(*changes)(l)
            if not ok:
                return False, message
            r = why(d, i)
            return (r is None and D(d, i, 'Releasable') == 1) if text == '' else (text in (r or '')), r
        return body

    fix_d8 = [('update', 'MasterBill', {'Id': 4, 'Packages': 22}), ('update', 'Permit', {'Id': 7, 'Status': 'A'})]
    exam_d8 = ('insert', 'Inspection', {'Id': 100, 'DeclarationId': 8, 'Kind': 'P', 'InspectedDate': '2026-11-27', 'Officer': 'M. Tucker', 'Result': 'P'})
    doc_d5 = ('insert', 'Inspection', {'Id': 100, 'DeclarationId': 5, 'Kind': 'D', 'InspectedDate': '2026-11-26', 'Officer': 'R. Wilson', 'Result': 'P'})

    # --- reference data -------------------------------------------------------------------------------
    run('a negative duty rate is refused', refused('update', 'Tariff', {'Code': '9503.00', 'DutyRate': -5}, 'cannot be negative'))
    run('an exchange rate of 0 is refused', refused('update', 'ExchangeRate', {'Id': 8, 'Rate': 0}, 'more than 0'))
    run('a tariff heading in use cannot be deleted', refused('delete', 'Tariff', {'Code': '0201.10'}, 'used by declarations'))

    # --- value and duty ---------------------------------------------------------------------------------
    run('value is the price paid x the week\'s rate: 2,400 GBP of whisky at 1.27 is 3,048.00',
        lambda d, l: (one(d, 'select Value from DeclarationLine where Id=4') == 3048.0 and D(d, 2, 'Rate') == 1.27, one(d, 'select Value from DeclarationLine where Id=4')))
    run('a rate for another week is refused', refused('update', 'Declaration', {'Id': 2, 'ExchangeRateId': 4}, 'not the week'))

    def rate_corrected(d, l):
        ok = l.update('ExchangeRate', {'Id': 3, 'Rate': 1.30})
        return ok and one(d, 'select Value from DeclarationLine where Id=4') == 3120.0 and D(d, 2, 'TotalValue') == 5070.0, (l.message, D(d, 2, 'TotalValue'))
    run('the week\'s rate is corrected: the values follow', rate_corrected)
    run('ad valorem: beef 8,100 at 5 % = 405.00; grapes 112.50; milk powder free',
        lambda d, l: ([one(d, f'select Duty from DeclarationLine where Id={i}') for i in (1, 2, 3)] == [405.0, 0.0, 112.5], None))
    run('specific: whisky 120 l at 30.00 = 3,600.00; wine 300 l at 8.50 = 2,550.00',
        lambda d, l: ([one(d, f'select Duty from DeclarationLine where Id={i}') for i in (4, 5)] == [3600.0, 2550.0], None))

    def compound(d, l):
        ok = l.insert('DeclarationLine', {'Id': 100, 'DeclarationId': 5, 'TariffCode': '2402.20', 'CountryCode': 'US', 'Quantity': 2, 'InvoiceValue': 200})
        return ok and one(d, 'select Duty from DeclarationLine where Id=100') == 520.0, (l.message, one(d, 'select Duty from DeclarationLine where Id=100'))
    run('compound: cigarettes 10 % of 200 + 2 x 250.00 = 520.00', compound)

    def stepped(d, l):
        ok = l.insert('DeclarationLine', {'Id': 100, 'DeclarationId': 5, 'TariffCode': '8703.23', 'CountryCode': 'JP', 'Quantity': 1, 'InvoiceValue': 25000})
        return ok and one(d, 'select Duty from DeclarationLine where Id=100') == 30000.0, (l.message, one(d, 'select Duty from DeclarationLine where Id=100'))
    run('stepped: a 25,000 car - 75 % of the first 10,000 and 150 % above = 30,000.00', stepped)

    def rate_change(d, l):
        ok = l.update('Tariff', {'Code': '0201.10', 'DutyRate': 10.0})
        ok = ok and l.insert('DeclarationLine', {'Id': 100, 'DeclarationId': 4, 'TariffCode': '0201.10', 'CountryCode': 'US', 'Quantity': 10, 'InvoiceValue': 100})
        return ok and one(d, 'select Duty from DeclarationLine where Id=1') == 405.0 and one(d, 'select Duty from DeclarationLine where Id=100') == 10.0, l.message
    run('a tariff rate changes: lines already declared keep theirs, new lines use the new one', rate_change)
    run('wharfage: 1.25 % of the value - beef 101.25', lambda d, l: (one(d, 'select Wharfage from DeclarationLine where Id=1') == 101.25, None))
    run('no wharfage on personal baggage', lambda d, l: (D(d, 9, 'TotalWharfage') == 0.0, D(d, 9, 'TotalWharfage')))

    def port_rate(d, l):
        ok = l.update('PortOfEntry', {'Id': 1, 'WharfageRate': 1.5})
        ok = ok and l.insert('Arrival', {'Id': 100, 'CarrierId': 1, 'PortOfEntryId': 1, 'VoyageNumber': 'BW-2701', 'ExpectedDate': '2027-01-05'})
        return ok and one(d, 'select WharfageRate from Arrival where Id=1') == 1.25 and one(d, 'select WharfageRate from Arrival where Id=100') == 1.5 and D(d, 1, 'WharfageRate') == 1.25, l.message
    run('the port changes its wharfage: arrivals already in keep theirs', port_rate)
    run('the entry adds up: 11,750.00 value, 517.50 duty, 146.88 wharfage, 664.38 due; CIF 13,670.00 for statistics',
        lambda d, l: (D(d, 1, 'TotalValue, TotalDuty, TotalWharfage, AmountDue, CifValue, LineCount') == (11750.0, 517.5, 146.88, 664.38, 13670.0, 3), D(d, 1, 'TotalValue, TotalDuty, TotalWharfage, AmountDue, CifValue, LineCount')))
    run('a resident\'s allowance: 300 of 570.00 takes 31.18 off 59.25 duty',
        lambda d, l: (D(d, 9, 'Allowance, AllowanceDuty, AmountDue') == (300.0, 31.18, 28.07), D(d, 9, 'Allowance, AllowanceDuty, AmountDue')))
    run('a visitor\'s allowance is 50', lambda d, l: (l.update('Declaration', {'Id': 9, 'Declarant': 'V'}) and D(d, 9, 'Allowance, AllowanceDuty') == (50.0, 5.2), D(d, 9, 'Allowance, AllowanceDuty')))
    run('a personal declaration says resident or visitor', refused('update', 'Declaration', {'Id': 9, 'Declarant': None}, 'resident (R) or visitor (V)'))
    run('relief (CPC 4071): the hospital\'s medicines pay no duty, only wharfage',
        lambda d, l: (D(d, 6, 'TotalDuty, AmountDue, Balance, ReliefApproved') == (0.0, 75.0, 0.0, 1), D(d, 6, 'TotalDuty, AmountDue, Balance, ReliefApproved')))
    run('relief claimed by an importer not approved for it is refused',
        refused('update', 'DeclarationLine', {'Id': 10, 'ReliefClaimed': 1}, 'not approved for duty relief'))
    run('a line with no quantity is refused', refused('update', 'DeclarationLine', {'Id': 10, 'Quantity': 0}, 'more than 0'))
    run('a negative value is refused', refused('update', 'DeclarationLine', {'Id': 10, 'InvoiceValue': -1}, 'cannot be negative'))
    run('an unknown tariff heading is refused', refused('insert', 'DeclarationLine', {'Id': 100, 'DeclarationId': 5, 'TariffCode': '9999.99', 'CountryCode': 'US', 'Quantity': 1, 'InvoiceValue': 5}, 'no tariff heading'))

    # --- payments and statements ------------------------------------------------------------------------
    run('a payment brings the balance down', lambda d, l: (l.insert('Payment', {'Id': 100, 'DeclarationId': 5, 'PaidDate': '2026-11-26', 'Amount': 462.5}) and D(d, 5, 'Paid, Balance') == (462.5, 1000.0), D(d, 5, 'Paid, Balance')))
    run('paying more than is due is refused', refused('insert', 'Payment', {'Id': 100, 'DeclarationId': 5, 'PaidDate': '2026-11-26', 'Amount': 2000}, 'more than the'))
    run('a payment must be more than 0', refused('insert', 'Payment', {'Id': 100, 'DeclarationId': 5, 'PaidDate': '2026-11-26', 'Amount': 0}, 'more than 0'))
    run('a payment is for a declaration or a statement, not both', refused('insert', 'Payment', {'Id': 100, 'DeclarationId': 5, 'StatementId': 1, 'PaidDate': '2026-11-26', 'Amount': 5}, 'declaration or for a statement'))
    run('a statement adds up its released declarations: Harbour Provisions owes 664.38 for November',
        lambda d, l: (one(d, 'select Total, Paid, Balance from Statement where Id=1') == (664.38, 0.0, 664.38) and I(d, 1, 'StatementBalance') == 664.38, one(d, 'select Total, Paid, Balance from Statement where Id=1')))
    run('a statement cannot be closed while it owes', refused('update', 'Statement', {'Id': 1, 'Status': 'C'}, 'still owes'))

    def statement_paid(d, l):
        ok = l.insert('Payment', {'Id': 100, 'StatementId': 1, 'PaidDate': '2026-12-15', 'Amount': 664.38})
        ok = ok and l.update('Statement', {'Id': 1, 'Status': 'C'})
        return ok and I(d, 1, 'StatementBalance') == 0.0, (l.message, I(d, 1, 'StatementBalance'))
    run('the statement is paid and closed: the importer owes nothing on statement', statement_paid)
    run('a statement for an importer who does not pay on statements is refused', refused('insert', 'Statement', {'Id': 100, 'ImporterId': 3, 'Period': '2026-11', 'DueDate': '2026-12-21'}, 'does not pay on statements'))
    run('a declaration on another importer\'s statement is refused', refused('update', 'Declaration', {'Id': 3, 'StatementId': 2}, 'another importer'))
    run('the bond: 10 % of the year\'s duty, at least 10,000; Somers has no bond',
        lambda d, l: (I(d, 2, 'YearDuty, RequiredBond, BondSufficient') == (6150.0, 10000.0, 1) and I(d, 3, 'BondSufficient') == 0, I(d, 2, 'YearDuty, RequiredBond, BondSufficient')))

    def bond_short(d, l):
        ok, message = steps(*fix_d8, exam_d8, ('update', 'Importer', {'Id': 2, 'BondAmount': 8000}), ('update', 'Declaration', {'Id': 8, 'StatementId': 2}))(l)
        released = l.update('Declaration', {'Id': 8, 'Status': 'R'})
        return ok and not released and 'more than its bond' in l.message, (message, l.message)
    run('Island Spirits\' wine on its statement would owe more than its 8,000 bond: release refused - pay first', bond_short)

    def bond_ok(d, l):
        ok, message = steps(*fix_d8, exam_d8, ('update', 'Declaration', {'Id': 8, 'StatementId': 2}), ('update', 'Declaration', {'Id': 8, 'Status': 'R'}))(l)
        return ok and I(d, 2, 'StatementBalance, YearDuty') == (9639.16, 9550.0), (message, I(d, 2, 'StatementBalance, YearDuty'))
    run('within its 10,000 bond: released on the statement; the year\'s duty grows', bond_ok)

    # --- the manifest -------------------------------------------------------------------------------------
    run('a master bill\'s house bills: 25 manifested, 22 in its house bills - the manifest does not add up',
        lambda d, l: (one(d, 'select HouseCount, HousePackages, ManifestMatch from MasterBill where Id=4') == (2, 22, 0) and 'manifest does not add up' in why(d, 8), why(d, 8)))
    run('the manifest is corrected: the next reason shows - a missing permit', reason_after(8, 'need an agency permit', fix_d8[0]))
    run('a house bill knows its arrival', lambda d, l: (one(d, 'select ArrivalId from HouseBill where Id=7') == 4 and D(d, 7, 'MasterBillId') == 4, None))
    run('a house bill of another arrival is refused', refused('update', 'Declaration', {'Id': 5, 'HouseBillId': 1}, 'another arrival'))
    run('the security filing on the day of lading is late: 20 risk points for Somers',
        lambda d, l: (one(d, 'select LateFiling from HouseBill where Id=4') == 1 and D(d, 4, 'RiskScore, Lane') == (35, 'Y'), D(d, 4, 'RiskScore, Lane')))
    run('filed two days ahead after all: 15 points, green', lambda d, l: (l.update('HouseBill', {'Id': 4, 'SecurityFiled': '2026-11-20'}) and D(d, 4, 'RiskScore, Lane') == (15, 'G'), D(d, 4, 'RiskScore, Lane')))
    run('a declared house bill cannot be deleted', refused('delete', 'HouseBill', {'Id': 1}, 'is declared'))

    def master_cascade(d, l):
        ok, message = steps(('insert', 'MasterBill', {'Id': 100, 'ArrivalId': 5, 'Number': 'NIA-120-00092', 'Packages': 1}),
                            ('insert', 'HouseBill', {'Id': 100, 'MasterBillId': 100, 'Number': 'HB-9', 'Consignee': 'X', 'Packages': 1, 'LadingDate': '2026-11-26'}),
                            ('delete', 'MasterBill', {'Id': 100}))(l)
        return ok and one(d, 'select count(*) from HouseBill where Id=100') == 0, message
    run('deleting a master bill takes its house bills', master_cascade)
    run('an arrival with containers cannot be deleted', refused('delete', 'Arrival', {'Id': 1}, 'still has containers'))
    run('an arrival with bills of lading cannot be deleted', refused('delete', 'Arrival', {'Id': 3}, 'bills of lading'))

    # --- risk and lanes ------------------------------------------------------------------------------------
    run('green: Harbour Provisions, a trusted trader (AEO), from the US: risk 0',
        lambda d, l: (D(d, 1, 'RiskScore, Lane') == (0, 'G'), D(d, 1, 'RiskScore, Lane')))
    run('blue: the hospital\'s entry, a trusted trader chosen for audit, released now',
        lambda d, l: (D(d, 6, 'Lane, Status') == ('B', 'R'), D(d, 6, 'Lane, Status')))
    run('not chosen for audit: green', lambda d, l: (l.update('Declaration', {'Id': 6, 'AuditFlag': 0}) and D(d, 6, 'Lane') == 'G', D(d, 6, 'Lane')))
    run('yellow: new this year, from China, phones at 80 each (reference 300) - 15 + 15 + 20 = 50',
        lambda d, l: (D(d, 5, 'RiskScore, Lane, UndervaluedLines') == (50, 'Y', 1), D(d, 5, 'RiskScore, Lane, UndervaluedLines')))
    run('the phones re-valued at 200 each: 30, still yellow; registered over a year: 15, green',
        lambda d, l: (l.update('DeclarationLine', {'Id': 11, 'InvoiceValue': 10000}) and D(d, 5, 'RiskScore') == 30
                      and l.update('Importer', {'Id': 4, 'RegisteredSince': '2025-01-01'}) and D(d, 5, 'RiskScore, Lane') == (15, 'G'), D(d, 5, 'RiskScore, Lane')))
    run('red: unregistered, from Colombia, a broken seal - 30 + 20 + 15 + 40 = 105',
        lambda d, l: (D(d, 7, 'RiskScore, Lane') == (105, 'R'), D(d, 7, 'RiskScore, Lane')))
    run('the importer registers and the seal checks out: 30 + 15 = 45, yellow',
        lambda d, l: (l.update('Importer', {'Id': 5, 'Registered': 1, 'RegisteredSince': '2026-11-20'}) and l.update('Container', {'Id': 5, 'SealIntact': 1}) and D(d, 7, 'RiskScore, Lane') == (45, 'Y'), D(d, 7, 'RiskScore, Lane')))
    run('Colombia\'s risk weight is lowered: the score follows', lambda d, l: (l.update('Country', {'Code': 'CO', 'RiskWeight': 10}) and D(d, 7, 'RiskScore') == 85, D(d, 7, 'RiskScore')))
    run('random selection: Island Spirits\' wine, risk 5, drawn to red',
        lambda d, l: (D(d, 8, 'RiskScore, Lane') == (5, 'R') and l.update('Declaration', {'Id': 8, 'RandomDraw': 0.5}) and D(d, 8, 'Lane') == 'G', D(d, 8, 'Lane')))

    def penalty(d, l):
        ok = l.insert('Inspection', {'Id': 100, 'DeclarationId': 5, 'Kind': 'P', 'InspectedDate': '2026-11-26', 'Officer': 'M. Tucker', 'Result': 'F', 'Notes': 'Phones undervalued'})
        ok = ok and l.insert('Declaration', {'Id': 100, 'ImporterId': 4, 'ArrivalId': 3, 'CountryCode': 'CN', 'ExchangeRateId': 2, 'EntryNumber': 'BDA-26-10490',
                                             'LodgedDate': '2026-11-27', 'Status': 'L'})
        return ok and one(d, 'select Penalty from Inspection where Id=100') == 25 and D(d, 5, 'Penalties, FailedInspections, RiskScore') == (25, 1, 50) \
            and I(d, 4, 'PenaltyPoints, CompliancePoints') == (25, 75) and 'failed an inspection' in why(d, 5) and D(d, 100, 'CompliancePoints, RiskScore') == (75, 43), \
            (l.message, D(d, 5, 'Penalties, FailedInspections, RiskScore'), I(d, 4, 'PenaltyPoints, CompliancePoints'), D(d, 100, 'CompliancePoints, RiskScore'))
    run('a failed examination holds the entry and costs the importer 25 points: its next entry scores 12.5 higher', penalty)

    # --- release ------------------------------------------------------------------------------------------
    def empty(d, l):
        ok = l.insert('Declaration', {'Id': 100, 'ImporterId': 1, 'ArrivalId': 1, 'CountryCode': 'US', 'ExchangeRateId': 2, 'EntryNumber': 'BDA-26-10499', 'LodgedDate': '2026-11-26', 'Status': 'L'})
        return ok and why(d, 100) == 'It declares no goods' and not l.update('Declaration', {'Id': 100, 'Status': 'R'}) and 'not released' in l.message, (l.message, why(d, 100))
    run('an entry that declares no goods cannot be released', empty)
    run('prohibited goods (pistols) are never released', lambda d, l: (why(d, 7).startswith('Prohibited goods') and D(d, 7, 'ProhibitedLines') == 1, why(d, 7)))
    run('the pistols seized and taken off: next, the manifest', reason_after(7, 'manifest does not add up', ('delete', 'DeclarationLine', {'Id': 15})))
    run('manifest corrected: next, the open hold on the broken seal', reason_after(7, '1 hold(s) open', ('delete', 'DeclarationLine', {'Id': 15}), fix_d8[0]))
    run('the hold is lifted: next, the red lane\'s examination',
        reason_after(7, 'Red lane', ('delete', 'DeclarationLine', {'Id': 15}), fix_d8[0], ('update', 'Hold', {'Id': 1, 'Open': 0})))
    run('an agency hold names its agency', refused('insert', 'Hold', {'Id': 100, 'DeclarationId': 5, 'Source': 'A', 'Reason': 'Check'}, 'names its agency'))
    run('a hold of the Ministry of Health on the phones holds the entry',
        reason_after(5, '1 hold(s) open', ('insert', 'Hold', {'Id': 100, 'DeclarationId': 5, 'Source': 'A', 'AgencyCode': 'HLTH', 'Reason': 'Batteries: safety check', 'Open': 1})))
    run('the wine waits for its liquor licence: a permit pending', reason_after(8, 'need an agency permit', fix_d8[0]))
    run('a permit from the wrong agency is refused', refused('insert', 'Permit', {'Id': 100, 'DeclarationLineId': 16, 'AgencyCode': 'ENV', 'Number': 'ENV-1'}, 'another agency'))
    run('the licence is approved; the red lane still needs an examination', reason_after(8, 'Red lane', *fix_d8))
    run('examined and passed: unpaid', reason_after(8, '3427.25 unpaid', *fix_d8, exam_d8))
    run('an X-ray scan counts as an examination',
        reason_after(8, 'unpaid', *fix_d8, ('insert', 'Inspection', {'Id': 100, 'DeclarationId': 8, 'Kind': 'X', 'InspectedDate': '2026-11-27', 'Result': 'P'})))
    run('a document check does not clear the red lane',
        reason_after(8, 'Red lane', *fix_d8, ('insert', 'Inspection', {'Id': 100, 'DeclarationId': 8, 'Kind': 'D', 'InspectedDate': '2026-11-27', 'Result': 'P'})))
    run('yellow: the electronics need a document check', lambda d, l: (why(d, 5) == 'Yellow lane: it must pass a document check', why(d, 5)))
    run('the documents pass: 1,462.50 unpaid', reason_after(5, '1462.50 unpaid', doc_d5))

    def paid_release(d, l):
        ok, message = steps(doc_d5, ('insert', 'Payment', {'Id': 100, 'DeclarationId': 5, 'PaidDate': '2026-11-26', 'Amount': 1462.5}),
                            ('update', 'Declaration', {'Id': 5, 'Status': 'R'}))(l)
        return ok and D(d, 5, 'Status, Releasable, PassedChecks') == ('R', 1, 1), (message, D(d, 5, 'Status, Releasable'))
    run('paid: released', paid_release)
    run('not releasable: release refused, with the reason', refused('update', 'Declaration', {'Id': 5, 'Status': 'R'}, 'not released: Yellow lane'))
    run('lodged before arrival: the goods have not arrived', lambda d, l: (why(d, 3) == 'The goods have not arrived', why(d, 3)))

    def on_arrival(d, l):
        ok, message = steps(('update', 'Arrival', {'Id': 2, 'ArrivedDate': '2026-11-27'}))(l)
        releasable = D(d, 3, 'Releasable')
        ok = ok and l.update('Declaration', {'Id': 3, 'Status': 'R'})
        return ok and releasable == 1 and one(d, 'select Total from Statement where Id=1') == 1486.88, (message, l.message, releasable)
    run('the ship docks: the pre-lodged beef is releasable at once - released, on the November statement', on_arrival)

    # --- deleting -----------------------------------------------------------------------------------------
    run('an entry with payments cannot be deleted', refused('delete', 'Declaration', {'Id': 6}, 'has payments'))
    run('an entry that went through the gate cannot be deleted', refused('delete', 'Declaration', {'Id': 1}, 'moved through the gate'))
    run('an inspected entry cannot be deleted', lambda d, l: (l.insert('Inspection', {'Id': 100, 'DeclarationId': 4, 'Kind': 'D', 'InspectedDate': '2026-11-26', 'Result': 'P'}) and not l.delete('Declaration', {'Id': 4}) and 'was inspected' in l.message, l.message))

    def delete_entry(d, l):
        ok = l.insert('Hold', {'Id': 100, 'DeclarationId': 4, 'Source': 'C', 'Reason': 'Check'}) and l.delete('Declaration', {'Id': 3})
        ok = ok and l.delete('Declaration', {'Id': 4})
        return ok and one(d, 'select count(*) from DeclarationLine where DeclarationId in (3, 4)') == 0 and one(d, 'select count(*) from Permit where Id=5') == 0 \
            and one(d, 'select count(*) from Hold where Id=100') == 0 and I(d, 3, 'DeclarationCount') == 0, l.message
    run('deleting an entry takes its lines, their permits and its holds', delete_entry)
    run('an importer counts its declarations: Harbour Provisions 2, Island Spirits 2, Somers 1',
        lambda d, l: ([I(d, i, 'DeclarationCount') for i in (1, 2, 3)] == [2, 2, 1], [I(d, i, 'DeclarationCount') for i in (1, 2, 3)]))
    run('an importer with declarations cannot be deleted', refused('delete', 'Importer', {'Id': 1}, 'has declarations'))

    def importer_statements(d, l):
        ok = l.insert('Importer', {'Id': 100, 'Name': 'New Co', 'OnStatement': 1, 'BondAmount': 5000})
        ok = ok and l.insert('Statement', {'Id': 100, 'ImporterId': 100, 'Period': '2026-11', 'DueDate': '2026-12-21'})
        return ok and not l.delete('Importer', {'Id': 100}) and 'has statements' in l.message, l.message
    run('an importer with statements cannot be deleted', importer_statements)

    # --- the gate ------------------------------------------------------------------------------------------
    run('released, cleared truck and driver, seal matching, approved route: through the gate', lambda d, l: (M(d, 1) == ('G', None), M(d, 1)))
    run('held goods wait at the gate; it stays closed',
        lambda d, l: (M(d, 3) == ('R', 'The goods are not released yet') and not l.update('Movement', {'Id': 3, 'Status': 'O'}) and 'gate stays closed' in l.message, M(d, 3)))

    def gate_checks(d, l):
        ok = l.insert('Movement', {'Id': 100, 'DeclarationId': 2, 'ContainerId': 2, 'TruckId': 3, 'DriverId': 3, 'RouteId': 5,
                                   'MoveDate': '2026-11-27', 'TransponderRead': 0, 'ObservedSeal': 'BW1182000', 'Status': 'W'})
        seen = [M(d, 100)[1]]
        for table, record in (('Movement', {'Id': 100, 'TransponderRead': 1}), ('Movement', {'Id': 100, 'ObservedSeal': 'BW1182099'}),
                              ('Truck', {'Id': 3, 'ClearedUntil': '2027-11-30'}), ('Driver', {'Id': 3, 'ClearedUntil': '2027-11-30'}), ('Route', {'Id': 5, 'Approved': 1})):
            ok = ok and l.update(table, record)
            seen.append(M(d, 100)[1])
        expect = ["The truck's transponder was not read", 'Seal BW1182000 does not match the declared seal BW1182099', 'The truck is not cleared on 2026-11-27',
                  'The driver is not cleared on 2026-11-27', 'The route is not registered and approved', None]
        return ok and seen == expect and l.update('Movement', {'Id': 100, 'Status': 'O'}), (l.message, seen)
    run('the gate checks in turn - transponder, seal, truck, driver, route - each fixed, the truck goes', gate_checks)
    run('a container the entry does not declare is refused',
        refused('insert', 'Movement', {'Id': 100, 'DeclarationId': 1, 'ContainerId': 2, 'TruckId': 1, 'DriverId': 1, 'RouteId': 1, 'MoveDate': '2026-11-26', 'ObservedSeal': 'BW1182099', 'Status': 'W'}, 'is not the one'))

    shutil.rmtree(folder, ignore_errors=True)
    return results


def run_all():
    folder = tempfile.mkdtemp()
    try:
        base = build_db.build(os.path.join(folder, 'customs.sqlite'))
    except SystemExit as e:                         # a rule left out can make the seed itself fail
        shutil.rmtree(folder, ignore_errors=True)
        return [('the sample database builds through the rules', False, str(e))]
    results = [('the sample database builds through the rules', True, '')] + scenarios(base) + purge_checks(folder, base)
    shutil.rmtree(folder, ignore_errors=True)
    return results


def purge_checks(folder, base):
    """purge_sample.sql removes the demo scenario and keeps the lookup data: the result is the lookup-only build"""
    import sqlite3
    purged = os.path.join(folder, 'purged.sqlite')
    shutil.copy(base, purged)
    db = sqlite3.connect(purged)
    db.executescript(open(os.path.join(HERE, 'purge_sample.sql')).read())
    lookup_only = sqlite3.connect(build_db.build(os.path.join(folder, 'lookup-only.sqlite'), with_sample=False))
    left = [t for t in build_db.SAMPLE if db.execute(f'select count(*) from "{t}"').fetchone()[0]]
    differ = [t for t in build_db.LOOKUP if sorted(db.execute(f'select * from "{t}"')) != sorted(lookup_only.execute(f'select * from "{t}"'))]
    kept = all(db.execute(f'select count(*) from "{t}"').fetchone()[0] for t in build_db.LOOKUP)
    db.close()
    lookup_only.close()
    return [('purge_sample.sql empties every sample table', not left, left),
            ('purge_sample.sql keeps the lookup data, exactly as a lookup-only build makes it', kept and not differ, differ)]


def main():
    if '--prove' in sys.argv:
        logic_reference.OMIT.clear()
        del logic_reference.DECLARED[:]
        baseline = run_all()
        if any(not ok for _, ok, _ in baseline):
            print('customs --prove: the scenarios must pass first')
            return 1
        rules = list(logic_reference.DECLARED)
        unproven = []
        for rule in rules:
            logic_reference.OMIT.clear()
            logic_reference.OMIT.add(rule)
            if all(ok for _, ok, _ in run_all()):
                unproven.append(rule)
                print(f'NOT PROVEN  {rule}')
            else:
                print(f'proven      {rule}')
        logic_reference.OMIT.clear()
        print(f'customs --prove: {len(rules)} rules, {len(unproven)} not proven')
        return 1 if unproven else 0
    results = run_all()
    for name, ok, detail in results:
        print(('PASS  ' if ok else 'FAIL  ') + name + ('' if ok else f'   ({detail})'))
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f'customs rules: {len(results)} scenarios, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
