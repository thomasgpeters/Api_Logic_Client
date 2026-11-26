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
    M = lambda d, i: one(d, f'select Lane, Reason from Movement where Id={i}')

    # --- duty ---------------------------------------------------------------------------------
    run('duty from the tariff: beef 5%, grapes 5%, milk powder 0% -> 475, plus the 30 fee -> 505',
        lambda d, l: (D(d, 1, 'TotalDuty, ProcessingFee, AmountDue') == (475.0, 30.0, 505.0), D(d, 1, 'TotalDuty, ProcessingFee, AmountDue')))

    def rate_change(d, l):
        ok = l.update('Tariff', {'Code': '0201.10', 'DutyRate': 10.0})
        same = D(d, 1, 'TotalDuty') == 475.0
        ok = ok and l.insert('DeclarationLine', {'Id': 100, 'DeclarationId': 8, 'TariffCode': '0201.10', 'CountryCode': 'US', 'Quantity': 10, 'Value': 1000.0})
        return ok and same and one(d, 'select Duty from DeclarationLine where Id=100') == 100.0, (l.message, D(d, 1, 'TotalDuty'))
    run('a tariff rate changes: lines already declared keep their rate, new lines use the new one', rate_change)

    def value_change(d, l):
        ok = l.update('DeclarationLine', {'Id': 1, 'Value': 9000.0})        # beef: 9000 x 5% = 450
        return ok and D(d, 1, 'TotalDuty, Balance') == (520.0, 45.0) and one(d, 'select DeferredBalance from Importer where Id=1') == 45.0, (l.message, D(d, 1, 'TotalDuty, Balance'))
    run('a value is corrected: the duty, the balance and the importer\'s deferred balance follow', value_change)

    run('the entry\'s value is its lines\' values: 8100 + 1400 + 2250 = 11750',
        lambda d, l: (D(d, 1, 'TotalValue, LineCount') == (11750.0, 3), D(d, 1, 'TotalValue, LineCount')))

    def empty_entry(d, l):
        ok = l.insert('Declaration', {'Id': 100, 'ImporterId': 1, 'ArrivalId': 5, 'EntryNumber': 'BDA-26-10499', 'LodgedDate': '2026-11-26', 'Status': 'L'})
        ok = ok and l.insert('Inspection', {'Id': 100, 'DeclarationId': 100, 'InspectedDate': '2026-12-01', 'Officer': 'R. Wilson', 'Result': 'P'})
        return ok and not l.update('Declaration', {'Id': 100, 'Status': 'R'}) and 'declares no goods' in l.message, l.message
    run('an entry that declares no goods cannot be released, even inspected', empty_entry)

    run('a payment brings the balance down: paid in full, nothing owed',
        lambda d, l: (D(d, 1, 'Paid, Balance') == (505.0, 0.0), D(d, 1, 'Paid, Balance')))
    run('a payment must be more than 0',
        lambda d, l: (not l.insert('Payment', {'Id': 100, 'DeclarationId': 5, 'PaidDate': '2026-11-26', 'Amount': 0}) and 'more than 0' in l.message, l.message))

    # --- the lanes ------------------------------------------------------------------------------
    run('lodged before arrival, registered importer, licences in order: pre-cleared, green lane',
        lambda d, l: (D(d, 1, 'PreCleared, Lane') == (1, 'G'), D(d, 1, 'PreCleared, Lane')))
    run('lodged after the goods arrived: red lane',
        lambda d, l: (D(d, 3, 'PreCleared, Lane') == (0, 'R'), D(d, 3, 'PreCleared, Lane')))
    run('an importer not registered with customs: red lane',
        lambda d, l: (D(d, 6, 'Lane') == 'R' and D(d, 6, 'MissingLicences') == 0, D(d, 6, 'Lane')))
    run('whisky without a liquor licence: a missing licence, red lane',
        lambda d, l: (D(d, 7, 'MissingLicences, Lane') == (1, 'R'), D(d, 7, 'MissingLicences, Lane')))

    def licence_added(d, l):
        line = one(d, 'select Id from DeclarationLine where DeclarationId=7')
        ok = l.update('DeclarationLine', {'Id': line, 'LicenceNumber': 'LIQ-2026-201'})
        return ok and D(d, 7, 'MissingLicences, PreCleared, Lane') == (0, 1, 'G'), (l.message, D(d, 7, 'MissingLicences, PreCleared, Lane'))
    run('the licence is added: the entry is pre-cleared, green lane', licence_added)

    def registered(d, l):
        ok = l.update('Importer', {'Id': 6, 'Registered': 1})
        return ok and D(d, 6, 'Lane') == 'G', (l.message, D(d, 6, 'Lane'))
    run('the importer registers: its entry lodged before arrival turns green', registered)

    def late_arrival(d, l):
        ok = l.update('Arrival', {'Id': 4, 'ArrivalDate': '2026-11-24'})     # the ship came early: entry 7 now lodged after
        line = one(d, 'select Id from DeclarationLine where DeclarationId=7')
        ok = ok and l.update('DeclarationLine', {'Id': line, 'LicenceNumber': 'LIQ-2026-201'})
        return ok and D(d, 7, 'Lane') == 'R', (l.message, D(d, 7, 'PreCleared, Lane'))
    run('the ship arrives before the entry was lodged: no pre-clearance', late_arrival)

    # --- release ----------------------------------------------------------------------------------
    run('a red-lane entry cannot be released without an inspection',
        lambda d, l: (not l.update('Declaration', {'Id': 7, 'Status': 'R'}) and 'must pass an inspection' in l.message, l.message))
    def failed(d, l):
        ok = l.update('Importer', {'Id': 6, 'Registered': 1})        # registered: the green lane ...
        ok = ok and l.insert('Payment', {'Id': 100, 'DeclarationId': 6, 'PaidDate': '2026-11-26', 'Amount': 655.0})   # ... and paid: only the failed inspection is left
        return ok and not l.update('Declaration', {'Id': 6, 'Status': 'R'}) and 'failed an inspection' in l.message, l.message
    run('an entry that failed an inspection cannot be released, even green and paid', failed)

    def inspected(d, l):
        ok = l.insert('Inspection', {'Id': 100, 'DeclarationId': 7, 'InspectedDate': '2026-11-27', 'Officer': 'M. Tucker', 'Result': 'P'})
        ok = ok and l.update('Declaration', {'Id': 7, 'Status': 'R'})
        return ok and one(d, 'select DeferredBalance from Importer where Id=2') == 8740.0, (l.message, one(d, 'select DeferredBalance from Importer where Id=2'))
    run('inspected and passed: released on the importer\'s bond (3910 + 4830 owed, within 10000)', inspected)

    run('released unpaid without a bond is refused: pay first',
        lambda d, l: (not l.update('Declaration', {'Id': 5, 'Status': 'R'}) and 'deferment bond' in l.message, l.message))

    def pay_then_release(d, l):
        ok = l.insert('Payment', {'Id': 100, 'DeclarationId': 5, 'PaidDate': '2026-11-26', 'Amount': 7820.0})
        ok = ok and l.update('Declaration', {'Id': 5, 'Status': 'R'})
        return ok and D(d, 5, 'Status, Balance') == ('R', 0.0), (l.message, D(d, 5, 'Status, Balance'))
    run('paid in full, then released', pay_then_release)

    def over_bond(d, l):
        ok = l.insert('DeclarationLine', {'Id': 100, 'DeclarationId': 4, 'TariffCode': '8708.99', 'CountryCode': 'JP', 'Quantity': 100, 'Value': 50000.0})
        return not ok and 'deferment bond' in l.message, l.message
    run('adding goods to a released entry past the importer\'s bond is refused', over_bond)

    # --- lines and reference data ----------------------------------------------------------------------
    run('a line with no quantity is refused',
        lambda d, l: (not l.insert('DeclarationLine', {'Id': 100, 'DeclarationId': 8, 'TariffCode': '3004.90', 'CountryCode': 'US', 'Quantity': 0, 'Value': 10.0}) and 'Quantity' in l.message, l.message))
    run('a negative value is refused',
        lambda d, l: (not l.insert('DeclarationLine', {'Id': 100, 'DeclarationId': 8, 'TariffCode': '3004.90', 'CountryCode': 'US', 'Quantity': 1, 'Value': -5.0}) and 'negative' in l.message, l.message))
    run('an unknown tariff heading is refused',
        lambda d, l: (not l.insert('DeclarationLine', {'Id': 100, 'DeclarationId': 8, 'TariffCode': '9999.99', 'CountryCode': 'US', 'Quantity': 1, 'Value': 5.0}) and 'no tariff heading' in l.message, l.message))
    run('a duty rate over 100% is refused',
        lambda d, l: (not l.update('Tariff', {'Code': '9503.00', 'DutyRate': 120.0}) and 'between 0 and 100' in l.message, l.message))

    def fee_copy(d, l):
        ok = l.update('PortOfEntry', {'Id': 1, 'ProcessingFee': 45.0})
        ok = ok and l.insert('Arrival', {'Id': 100, 'CarrierId': 1, 'PortOfEntryId': 1, 'VoyageNumber': 'BW-2701', 'ArrivalDate': '2027-01-05'})
        return ok and D(d, 1, 'ProcessingFee') == 30.0 and one(d, 'select ProcessingFee from Arrival where Id=100') == 45.0, l.message
    run('the port raises its fee: new arrivals pay it, entries already lodged keep theirs', fee_copy)

    # --- deleting ---------------------------------------------------------------------------------------
    run('an entry with payments cannot be deleted',
        lambda d, l: (not l.delete('Declaration', {'Id': 1}) and 'has payments' in l.message, l.message))

    def delete_entry(d, l):
        ok = l.delete('Declaration', {'Id': 7})
        return ok and one(d, 'select count(*) from DeclarationLine where DeclarationId=7') == 0 and one(d, 'select DeclarationCount from Importer where Id=2') == 1, l.message
    run('deleting an entry deletes its lines; the importer counts one fewer', delete_entry)
    run('an importer with declarations cannot be deleted',
        lambda d, l: (not l.delete('Importer', {'Id': 1}) and 'has declarations' in l.message, l.message))
    run('an arrival with containers cannot be deleted',
        lambda d, l: (not l.delete('Arrival', {'Id': 5}) and 'still has containers' in l.message, l.message))

    # --- the gate --------------------------------------------------------------------------------------
    run('a released entry, cleared truck and driver, seal matching, approved route: through the gate',
        lambda d, l: (M(d, 1) == ('G', None) and one(d, 'select Status from Movement where Id=1') == 'O', M(d, 1)))
    run('held goods wait at the gate; the gate stays closed',
        lambda d, l: (M(d, 7)[0] == 'R' and not l.update('Movement', {'Id': 7, 'Status': 'O'}) and 'gate stays closed' in l.message, (M(d, 7), l.message)))

    def release_opens(d, l):
        ok = l.insert('Movement', {'Id': 100, 'DeclarationId': 5, 'ContainerId': 6, 'TruckId': 1, 'DriverId': 1, 'RouteId': 6,
                                   'MoveDate': '2026-11-26', 'TransponderRead': 1, 'ObservedSeal': 'NI-77310', 'Status': 'W'})
        before = M(d, 100)
        ok = ok and l.insert('Payment', {'Id': 100, 'DeclarationId': 5, 'PaidDate': '2026-11-26', 'Amount': 7820.0}) and l.update('Declaration', {'Id': 5, 'Status': 'R'})
        return ok and before[0] == 'R' and M(d, 100) == ('G', None) and l.update('Movement', {'Id': 100, 'Status': 'O'}), (l.message, before, M(d, 100))
    run('a truck waiting at the gate goes through as soon as the entry is released', release_opens)

    def seal(d, l):
        before = M(d, 5)
        ok = l.update('Movement', {'Id': 5, 'ObservedSeal': 'CS0049925'})
        return ok and 'does not match' in before[1] and M(d, 5) == ('G', None), (l.message, before, M(d, 5))
    run('a seal that does not match stops the truck; read again correctly, it goes', seal)

    def transponder(d, l):
        ok = l.update('Movement', {'Id': 1, 'TransponderRead': 0, 'Status': 'W'})
        return ok and M(d, 1) == ('R', "The truck's transponder was not read"), (l.message, M(d, 1))
    run('the transponder was not read: the truck is stopped', transponder)

    def clearances(d, l):
        first = M(d, 6)[1]
        ok = l.update('Truck', {'Id': 3, 'ClearedUntil': '2027-11-30'})        # the truck is cleared again ...
        second = M(d, 6)[1]
        ok = ok and l.update('Driver', {'Id': 3, 'ClearedUntil': '2027-11-30'})   # ... and its driver
        return ok and 'truck' in first and 'driver' in second and M(d, 6) == ('G', None), (l.message, first, second, M(d, 6))
    run('a lapsed truck clearance, then a lapsed driver clearance: renewed one by one, the truck goes', clearances)

    def never_cleared(d, l):
        ok = l.update('Movement', {'Id': 1, 'TruckId': 5, 'Status': 'W'})
        return ok and 'truck is not cleared' in M(d, 1)[1], (l.message, M(d, 1))
    run('a truck never cleared is stopped', never_cleared)

    def route(d, l):
        ok = l.update('Route', {'Id': 5, 'Approved': 1})
        return ok and M(d, 4) == ('G', None), (l.message, M(d, 4))
    run('customs approves the route: the truck waiting on it can go', route)

    run('a movement with a container its entry does not declare is refused',
        lambda d, l: (not l.insert('Movement', {'Id': 100, 'DeclarationId': 1, 'ContainerId': 2, 'TruckId': 1, 'DriverId': 1, 'RouteId': 1,
                                                'MoveDate': '2026-11-26', 'TransponderRead': 1, 'ObservedSeal': 'BW1182034', 'Status': 'W'})
                      and 'is not the one' in l.message, l.message))

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
