#!/usr/bin/env python3
"""The Telecom sample's business rules, scenario by scenario, and proof that every rule is tested.

    python3 samples/Telecom/test_rules.py           every scenario on a fresh copy of the sample database
    python3 samples/Telecom/test_rules.py --prove   each rule left out in turn: some scenario must fail

The engine is tools/logic_reference.py's (LogicBank for FutureBasic, function for function); the rules are
telecom_rules.py, the data build_db.py's. Nothing is written outside a temporary folder.
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
import telecom_rules                               # noqa: E402
import build_db                                    # noqa: E402


def open_logic(path):
    data = Data(path)
    logic = Logic(data)
    telecom_rules.declare(logic)
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
        except Exception as e:                      # a scenario that breaks is a failure, not a crash
            ok, detail = False, f'{type(e).__name__}: {e}'
        data.db.close()
        results.append((name, bool(ok), detail))

    # --- pricing ------------------------------------------------------------------------------
    run('a country is priced from its preferred agreement: France costs 6.15 a day, sells for 10',
        lambda d, l: (one(d, "select CostPerDay, DayPrice from Country where Code='FR'") == (6.15, 10.0),
                      one(d, "select CostPerDay, DayPrice from Country where Code='FR'")))
    run('the zone markup prices Japan higher: 10.00 a day x 1.8, rounded up to 20',
        lambda d, l: (one(d, "select DayPrice from Country where Code='JP'") == 20.0, one(d, "select DayPrice from Country where Code='JP'")))
    run('a country without a partner network has no price: Kenya',
        lambda d, l: (one(d, "select DayPrice from Country where Code='KE'") is None, one(d, "select CostPerDay from Country where Code='KE'")))

    def agreement_change(d, l):
        ok = l.update('RoamingAgreement', {'Id': 16, 'RatePerGB': 9.0})          # Sakura Signal raises its rate
        price = one(d, "select DayPrice from Country where Code='JP'")
        quoted = one(d, "select DayPrice from TravelPlanCountry where TravelPlanId=3")
        return ok and price == 25.0 and quoted == 20.0, (l.message, price, quoted)
    run('a partner raises its rate: Japan reprices (25), a trip already quoted keeps its price (20)', agreement_change)

    def markup_change(d, l):
        ok = l.update('Zone', {'Id': 2, 'Markup': 2.0})
        return ok and one(d, "select DayPrice from Country where Code='FR'") == 15.0, (l.message, one(d, "select DayPrice from Country where Code='FR'"))
    run('the carrier changes Europe\'s markup: France reprices', markup_change)

    def preferred_change(d, l):
        ok = l.update('Country', {'Code': 'GB', 'RoamingAgreementId': 3})          # back to Albion Mobile, dearer
        return ok and one(d, "select CostPerDay from Country where Code='GB'") == 5.6, (l.message, one(d, "select CostPerDay from Country where Code='GB'"))
    run('the carrier changes the preferred partner in the UK: the cost follows the new agreement', preferred_change)

    # --- a new travel plan ----------------------------------------------------------------------
    def new_trip(d, l, phone=6, legs=(('FR', '2027-05-01', '2027-05-04'), ('CA', '2027-05-05', '2027-05-06')), start='2027-05-01', end='2027-05-06'):
        ok = l.insert('TravelPlan', {'Id': 100, 'PhoneId': phone, 'Name': 'Test trip', 'StartDate': start, 'EndDate': end, 'Status': 'Q'})
        for i, (country, arrive, leave) in enumerate(legs):
            ok = ok and l.insert('TravelPlanCountry', {'Id': 100 + i, 'TravelPlanId': 100, 'CountryCode': country,
                                                       'ArriveDate': arrive, 'LeaveDate': leave})
        return ok

    def quote(d, l):
        ok = new_trip(d, l)
        plan = one(d, 'select Days, CountryCount, Price, ZoneId from TravelPlan where Id=100')
        legs = d.db.execute('select CountryCode, Days, DayPrice, Included, Amount from TravelPlanCountry where TravelPlanId=100 order by Id').fetchall()
        want = [('FR', 4, 10.0, 0, 40.0), ('CA', 2, 5.0, 1, 0.0)]
        return ok and plan == (6, 2, 40.0, 1) and [tuple(x) for x in legs] == want, (l.message, plan, [tuple(x) for x in legs])
    run('a quote: France 4 days x 10, Canada free (home zone), trip 6 days, 2 countries, 40', quote)

    def quote_not_billed(d, l):
        before = one(d, 'select Balance from Account where Id=3')
        ok = new_trip(d, l)
        return ok and one(d, 'select Balance from Account where Id=3') == before, (before, one(d, 'select Balance from Account where Id=3'))
    run('a quote is not billed: the account balance stays', quote_not_billed)

    def purchase(d, l):
        ok = new_trip(d, l) and l.update('TravelPlan', {'Id': 100, 'Status': 'P'})
        got = (one(d, 'select TravelTotal from Phone where Id=6'), one(d, 'select TravelTotal from Plan where Id=3'),
               one(d, 'select TravelCharges, Balance from Account where Id=3'))
        return ok and got == (40.0, 40.0, (40.0, 95.0)), (l.message, got)
    run('buying it bills it: phone, plan and account totals rise by 40', purchase)

    def over_limit(d, l):
        ok = new_trip(d, l, legs=(('AU', '2027-05-01', '2027-05-14'),), start='2027-05-01', end='2027-05-14')   # 14 x 20 = 280
        refused = not l.update('TravelPlan', {'Id': 100, 'Status': 'P'})
        status = one(d, 'select Status from TravelPlan where Id=100')
        return ok and refused and 'credit limit' in l.message and status == 'Q' and one(d, 'select Balance from Account where Id=3') == 55.0, (l.message, status)
    run('buying a trip over the credit limit is refused (55 + 280 > 300); nothing changes', over_limit)

    def cancel(d, l):
        ok = l.update('TravelPlan', {'Id': 5, 'Status': 'X'})
        return ok and one(d, 'select TravelCharges, Balance from Account where Id=5') == (0.0, 75.0), (l.message, one(d, 'select TravelCharges, Balance from Account where Id=5'))
    run('cancelling a bought trip takes it off the bill', cancel)

    def change_dates(d, l):
        ok = l.update('TravelPlanCountry', {'Id': 1, 'LeaveDate': '2026-06-15'})     # Italy: 6 days instead of 11
        return ok and one(d, 'select Price from TravelPlan where Id=1') == 90.0 and one(d, 'select Balance from Account where Id=1') == 165.0, (l.message, one(d, 'select Price from TravelPlan where Id=1'))
    run('shortening a stay reprices the trip and the bill', change_dates)

    def leg_outside(d, l):
        ok = new_trip(d, l, legs=(('FR', '2027-04-28', '2027-05-03'),))
        return not ok and 'outside the trip' in l.message, l.message
    run('a country outside the trip\'s dates is refused', leg_outside)

    def leave_before_arrive(d, l):
        ok = new_trip(d, l, legs=(('FR', '2027-05-04', '2027-05-02'),))
        return not ok and 'before arriving' in l.message, l.message
    run('leaving a country before arriving is refused', leave_before_arrive)

    def trip_backwards(d, l):
        ok = l.insert('TravelPlan', {'Id': 100, 'PhoneId': 6, 'StartDate': '2027-05-06', 'EndDate': '2027-05-01', 'Status': 'Q'})
        return not ok and 'ends' in l.message, l.message
    run('a trip that ends before it starts is refused', trip_backwards)

    def no_service(d, l):
        ok = new_trip(d, l, legs=(('KE', '2027-05-01', '2027-05-03'),))
        return not ok and 'no service' in l.message, l.message
    run('a country without a partner network is refused: Kenya', no_service)

    def unknown_country(d, l):
        ok = new_trip(d, l, legs=(('ZZ', '2027-05-01', '2027-05-03'),))
        return not ok and 'no country' in l.message, l.message
    run('an unknown country is refused', unknown_country)

    def suspended(d, l):
        ok = new_trip(d, l, phone=5, legs=(('FR', '2027-05-01', '2027-05-02'),))
        refused = not l.update('TravelPlan', {'Id': 100, 'Status': 'P'})
        return ok and refused and 'not active' in l.message, l.message
    run('a suspended phone can get a quote but not buy it', suspended)

    # --- plans, phones, usage --------------------------------------------------------------------
    def new_plan(d, l):
        ok = l.insert('Plan', {'Id': 50, 'AccountId': 3, 'PlanOfferId': 4, 'StartDate': '2026-11-26'})
        got = one(d, 'select MonthlyPrice, MaxLines, DataGB, ZoneId from Plan where Id=50')
        return ok and got == (120.0, 5, 50.0, 1) and one(d, 'select MonthlyCharges, Balance from Account where Id=3') == (175.0, 175.0), (l.message, got)
    run('a new plan takes the offer\'s price, lines, data and home zone; the account bills it', new_plan)

    def too_many_lines(d, l):
        ok = l.insert('Phone', {'Id': 50, 'PlanId': 1, 'Number': '512-555-0150', 'Status': 'A'})
        return not ok and 'allows 1 phone' in l.message, l.message
    run('a second phone on a one-line plan is refused', too_many_lines)

    def phone_joins(d, l):
        ok = l.insert('Phone', {'Id': 50, 'PlanId': 9, 'Number': '305-555-0150', 'Status': 'A'})
        return ok and one(d, 'select PhoneCount from Plan where Id=9') == 4 and one(d, 'select ZoneId from Phone where Id=50') == 1, (l.message, one(d, 'select PhoneCount from Plan where Id=9'))
    run('a phone joins a family plan: counted, with the plan\'s home zone', phone_joins)

    def usage(d, l):
        ok = l.insert('Usage', {'Id': 100, 'PhoneId': 6, 'UsageDate': '2026-11-26', 'CountryCode': 'US', 'DataGB': 10.0})
        return ok and one(d, 'select DataUsedGB, DataOverGB from Plan where Id=3') == (37.8, 12.8), (l.message, one(d, 'select DataUsedGB, DataOverGB from Plan where Id=3'))
    run('usage adds up to the plan: 37.8 GB used of 25, 12.8 over', usage)

    run('an unlimited plan is never over', lambda d, l: (one(d, 'select DataOverGB from Plan where Id=1') == 0.0 and one(d, 'select DataUsedGB from Plan where Id=1') == 14.5,
                                                       one(d, 'select DataUsedGB, DataOverGB from Plan where Id=1')))
    run('a shared family plan adds its phones\' data: 54.7 of 50, 4.7 over',
        lambda d, l: (one(d, 'select DataUsedGB, DataOverGB from Plan where Id=2') == (54.7, 4.7), one(d, 'select DataUsedGB, DataOverGB from Plan where Id=2')))

    # --- deleting ---------------------------------------------------------------------------------
    def delete_trip(d, l):
        ok = l.delete('TravelPlan', {'Id': 2})
        return ok and one(d, 'select count(*) from TravelPlanCountry where TravelPlanId=2') == 0 and one(d, 'select TravelCharges from Account where Id=2') == 0.0, l.message
    run('deleting a trip deletes its countries and takes it off the bill', delete_trip)

    def delete_phone(d, l):
        ok = l.delete('Phone', {'Id': 11})
        return ok and one(d, 'select count(*) from Usage where PhoneId=11') == 0 and one(d, 'select count(*) from TravelPlan where PhoneId=11') == 0 \
            and one(d, 'select PhoneCount, DataUsedGB, TravelTotal from Plan where Id=5') == (0, 0.0, 0.0), (l.message, one(d, 'select PhoneCount, DataUsedGB, TravelTotal from Plan where Id=5'))
    run('deleting a phone deletes its usage and trips; the plan\'s totals follow', delete_phone)

    run('an account with plans cannot be deleted',
        lambda d, l: (not l.delete('Account', {'Id': 1}) and 'still has plans' in l.message, l.message))
    run('a plan with phones cannot be deleted',
        lambda d, l: (not l.delete('Plan', {'Id': 1}) and 'still has phones' in l.message, l.message))

    def bad_agreement(d, l):
        a = l.insert('RoamingAgreement', {'Id': 100, 'PartnerNetworkId': 5, 'ValidFrom': '2027-01-01', 'ValidTo': '2026-01-01',
                                          'RatePerGB': 1, 'RatePerMinute': 1, 'RatePerText': 1})
        m1 = l.message
        b = l.insert('RoamingAgreement', {'Id': 101, 'PartnerNetworkId': 5, 'ValidFrom': '2027-01-01', 'ValidTo': '2027-12-31',
                                          'RatePerGB': -1, 'RatePerMinute': 1, 'RatePerText': 1})
        return not a and not b and 'before it starts' in m1 and 'negative' in l.message, (m1, l.message)
    run('an agreement that ends before it starts, or with a negative rate, is refused', bad_agreement)

    shutil.rmtree(folder, ignore_errors=True)
    return results


def run_all():
    folder = tempfile.mkdtemp()
    try:
        base = build_db.build(os.path.join(folder, 'telecom.sqlite'))
    except SystemExit as e:                         # a rule left out can make the seed itself fail
        shutil.rmtree(folder, ignore_errors=True)
        return [('the sample database builds through the rules', False, str(e))]
    results = [('the sample database builds through the rules', True, '')] + scenarios(base)
    shutil.rmtree(folder, ignore_errors=True)
    return results


def main():
    if '--prove' in sys.argv:
        logic_reference.OMIT.clear()
        del logic_reference.DECLARED[:]
        baseline = run_all()
        if any(not ok for _, ok, _ in baseline):
            print('telecom --prove: the scenarios must pass first')
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
        print(f'telecom --prove: {len(rules)} rules, {len(unproven)} not proven')
        return 1 if unproven else 0
    results = run_all()
    for name, ok, detail in results:
        print(('PASS  ' if ok else 'FAIL  ') + name + ('' if ok else f'   ({detail})'))
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f'telecom rules: {len(results)} scenarios, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
