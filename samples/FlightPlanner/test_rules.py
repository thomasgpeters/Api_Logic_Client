#!/usr/bin/env python3
"""The Flight Planner sample's business rules, scenario by scenario, and proof that every rule is tested.

    python3 samples/FlightPlanner/test_rules.py           every scenario on a fresh copy of the sample database
    python3 samples/FlightPlanner/test_rules.py --prove   each rule left out in turn: some scenario must fail

The engine is tools/logic_reference.py's (LogicBank for FutureBasic, function for function); the rules are
flight_rules.py, the data build_db.py's. Nothing is written outside a temporary folder.
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
import flight_rules                               # noqa: E402
import build_db                                    # noqa: E402


def open_logic(path):
    data = Data(path)
    logic = Logic(data)
    flight_rules.declare(logic)
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

    P = lambda d, i, cols: one(d, f'select {cols} from FlightPlan where Id={i}')
    L = lambda d, i, cols: one(d, f'select {cols} from Leg where Id={i}')
    R = lambda d, i: P(d, i, 'GoNoGo, NoGoReason')

    def go(d, i):
        return R(d, i) == ('GO', None)

    # --- aircraft and what a plan flies --------------------------------------------------------------
    run('an aircraft takes its type\'s figures: the SR22 cruises at 170 kt, burns 15 gph, holds 81 gal, needs 2,600 ft',
        lambda d, l: (one(d, 'select CruiseKnots, FuelBurn, UsableFuel, MinRunway from Aircraft where Id=3') == (170, 15.0, 81.0, 2600),
                      one(d, 'select CruiseKnots, FuelBurn, UsableFuel, MinRunway from Aircraft where Id=3')))
    run('a plan flies its aircraft\'s figures',
        lambda d, l: (P(d, 3, 'CruiseKnots, FuelBurn, UsableFuel, MinRunway') == (170, 15.0, 81.0, 2600), P(d, 3, 'CruiseKnots, FuelBurn, UsableFuel, MinRunway')))

    def other_aircraft(d, l):
        ok = l.update('FlightPlan', {'Id': 6, 'AircraftId': 1})      # the Skyhawk instead of the SR22: 1,700 ft is enough
        return ok and L(d, 7, 'GroundSpeed, Minutes, Fuel, RunwayOK') == (120, 14, 2.0, 1) and go(d, 6), (l.message, L(d, 7, 'GroundSpeed, Minutes, Fuel, RunwayOK'), R(d, 6))
    run('Plum Island in the Skyhawk instead of the SR22: slower, less fuel, and the runway is long enough - GO', other_aircraft)

    def tanks(d, l):
        return not l.update('FlightPlan', {'Id': 1, 'FuelOnBoard': 60}) and 'tanks hold 53' in l.message, l.message
    run('more fuel than the tanks hold is refused', tanks)

    # --- a leg ------------------------------------------------------------------------------------------
    run('Bedford - Hyannis: 65.8 NM, true course 137, magnetic 152 (15 W)',
        lambda d, l: (L(d, 1, 'Distance, TrueCourse, MagneticCourse') == (65.8, 137, 152), L(d, 1, 'Distance, TrueCourse, MagneticCourse')))
    run('into a 10 kt headwind the Skyhawk makes 110 kt: 36 minutes, 5.1 gallons',
        lambda d, l: (L(d, 1, 'GroundSpeed, Minutes, Fuel') == (110, 36, 5.1), L(d, 1, 'GroundSpeed, Minutes, Fuel')))

    def wind(d, l):
        ok = l.update('Leg', {'Id': 1, 'Headwind': -20})            # a 20 kt tailwind
        return ok and L(d, 1, 'GroundSpeed, Minutes') == (140, 28) and P(d, 1, 'Minutes') == 42, (l.message, L(d, 1, 'GroundSpeed, Minutes'), P(d, 1, 'Minutes'))
    run('the wind turns into a tailwind: the leg and the plan are shorter', wind)

    def variation(d, l):
        ok = l.update('Airport', {'Id': 1, 'Variation': 14})
        return ok and L(d, 1, 'MagneticCourse') == 151, (l.message, L(d, 1, 'MagneticCourse'))
    run('the variation at Bedford is updated: the magnetic course follows', variation)

    def moved(d, l):
        ok = l.update('Leg', {'Id': 5, 'ToAirportId': 5})           # Providence - Nantucket instead of the Vineyard
        return ok and L(d, 5, 'Distance, TrueCourse') == (67.7, 114), (l.message, L(d, 5, 'Distance, TrueCourse'))
    run('a leg goes to another airport: distance and course are worked out again', moved)

    run('a leg that starts and ends at the same airport is refused',
        lambda d, l: (not l.insert('Leg', {'Id': 100, 'FlightPlanId': 3, 'Sequence': 2, 'FromAirportId': 8, 'ToAirportId': 8, 'Altitude': 4500}) and 'same airport' in l.message, l.message))
    run('a headwind stronger than the cruise is refused',
        lambda d, l: (not l.update('Leg', {'Id': 6, 'Headwind': 80}) and 'would not move' in l.message, l.message))
    run('a cruise less than 1,000 ft above the airports is refused (Worcester is at 1,009 ft)',
        lambda d, l: (not l.update('Leg', {'Id': 11, 'Altitude': 1500}) and '1,000 ft above' in l.message, l.message))
    run('a leg to an airport that does not exist is refused',
        lambda d, l: (not l.insert('Leg', {'Id': 100, 'FlightPlanId': 3, 'Sequence': 2, 'FromAirportId': 8, 'ToAirportId': 99, 'Altitude': 4500}) and 'no airport 99' in l.message, l.message))
    run('a leg from an airport that does not exist is refused',
        lambda d, l: (not l.insert('Leg', {'Id': 100, 'FlightPlanId': 3, 'Sequence': 2, 'FromAirportId': 99, 'ToAirportId': 8, 'Altitude': 4500}) and 'no airport 99' in l.message, l.message))

    # --- VFR cruising altitudes ---------------------------------------------------------------------------
    run('eastbound (MC 152) at 3,500 and low over the water at 2,500: both allowed',
        lambda d, l: (L(d, 1, 'AltitudeOK') == 1 and L(d, 2, 'AltitudeOK') == 1, (L(d, 1, 'AltitudeOK'), L(d, 2, 'AltitudeOK'))))
    run('westbound (MC 310) at 5,500, an eastbound altitude: not allowed, the plan is NO-GO',
        lambda d, l: (L(d, 10, 'AltitudeOK') == 0 and P(d, 8, 'BadAltitudeLegs') == 1 and 'altitude' in (R(d, 8)[1] or ''), R(d, 8)))

    def altitude_fixed(d, l):
        ok = l.update('Leg', {'Id': 10, 'Altitude': 6500})
        ok = ok and l.update('FlightPlan', {'Id': 8, 'Status': 'F'})
        return ok and go(d, 8), (l.message, R(d, 8))
    run('the pilot climbs to 6,500: GO, and the plan is filed', altitude_fixed)

    def filed_changed(d, l):
        return not l.update('Leg', {'Id': 3, 'Altitude': 5500}) and 'Not filed' in l.message and 'altitude' in l.message, l.message
    run('a filed plan cannot be changed into a NO-GO: the leg change is refused', filed_changed)

    # --- the plan's totals and fuel -----------------------------------------------------------------------
    run('Bedford - Hyannis - Nantucket: 2 legs, 92.7 NM, 50 minutes, 7.1 gallons',
        lambda d, l: (P(d, 1, 'LegCount, round(Distance, 1), Minutes, TripFuel') == (2, 92.7, 50, 7.1), P(d, 1, 'LegCount, Distance, Minutes, TripFuel')))
    run('the reserve: 30 minutes by day (4.3 gal), 45 at night (6.4 gal)',
        lambda d, l: (P(d, 1, 'ReserveFuel') == 4.3 and P(d, 2, 'ReserveFuel') == 6.4, (P(d, 1, 'ReserveFuel'), P(d, 2, 'ReserveFuel'))))

    def day_return(d, l):
        ok = l.update('FlightPlan', {'Id': 2, 'Night': 0})
        return ok and P(d, 2, 'ReserveFuel, FuelRequired, FuelMargin') == (4.3, 10.1, 24.9), (l.message, P(d, 2, 'ReserveFuel, FuelRequired, FuelMargin'))
    run('home before dark: the reserve, the fuel needed and the margin follow', day_return)
    run('the Cub into the wind to Lebanon needs 11.2 gallons with the reserve; 9 on board: NO-GO',
        lambda d, l: (P(d, 5, 'FuelRequired, FuelMargin') == (11.2, -2.2) and R(d, 5) == ('NO-GO', 'Not enough fuel: 11.2 gallons needed with the reserve, 9 on board'), (P(d, 5, 'FuelRequired, FuelMargin'), R(d, 5))))

    def topped_up(d, l):
        ok = l.update('FlightPlan', {'Id': 5, 'FuelOnBoard': 12})
        return ok and go(d, 5) and P(d, 5, 'FuelMargin') == 0.8, (l.message, R(d, 5))
    run('the Cub is topped up to 12 gallons: GO', topped_up)

    # --- go / no-go ---------------------------------------------------------------------------------------
    def no_legs(d, l):
        ok = l.insert('FlightPlan', {'Id': 100, 'PilotId': 1, 'AircraftId': 1, 'DepartureDate': '2026-12-12', 'FuelOnBoard': 40, 'Status': 'D'})
        return ok and R(d, 100) == ('NO-GO', 'The plan has no legs') and not l.update('FlightPlan', {'Id': 100, 'Status': 'F'}), (l.message, R(d, 100))
    run('a plan with no legs is NO-GO and cannot be filed', no_legs)
    run('Hannah\'s medical runs out on the 30th: the Vineyard on 3 December is NO-GO',
        lambda d, l: (R(d, 4) == ('NO-GO', "The pilot's medical certificate is not valid on 2026-12-03"), R(d, 4)))

    def medical(d, l):
        ok = l.update('Pilot', {'Id': 3, 'MedicalExpires': '2028-11-30'})
        return ok and go(d, 4) and l.update('FlightPlan', {'Id': 4, 'Status': 'F'}), (l.message, R(d, 4))
    run('Hannah renews her medical: GO, and the plan is filed', medical)
    run('Dev\'s last night landings were in July: a night flight in December is NO-GO',
        lambda d, l: (R(d, 3) == ('NO-GO', 'The pilot is not night current: three night landings in the last 90 days'), R(d, 3)))

    def night_current(d, l):
        ok = l.update('Pilot', {'Id': 2, 'LastNightLandings': '2026-11-25'})
        return ok and go(d, 3), (l.message, R(d, 3))
    run('Dev flies three night landings: night current, GO', night_current)

    def by_day(d, l):
        ok = l.update('FlightPlan', {'Id': 3, 'Night': 0})
        return ok and go(d, 3), (l.message, R(d, 3))
    run('Dev goes by day instead: night currency does not apply, GO', by_day)
    run('the annual inspection ran out on 20 November: NO-GO',
        lambda d, l: (R(d, 9) == ('NO-GO', "The aircraft's annual inspection is not current on 2026-11-30"), R(d, 9)))

    def annual(d, l):
        ok = l.update('Aircraft', {'Id': 5, 'AnnualDue': '2027-11-30'})
        return ok and go(d, 9), (l.message, R(d, 9))
    run('the annual is signed off: GO', annual)
    run('Plum Island\'s 2,105 ft is shorter than the SR22 needs: NO-GO',
        lambda d, l: (L(d, 7, 'RunwayOK') == 0 and P(d, 6, 'ShortRunwayLegs') == 1 and R(d, 6) == ('NO-GO', '1 leg(s) end at a runway shorter than the aircraft needs'), R(d, 6)))
    run('a NO-GO plan cannot be filed',
        lambda d, l: (not l.update('FlightPlan', {'Id': 3, 'Status': 'F'}) and 'Not filed - NO-GO: The pilot is not night current' in l.message, l.message))

    # --- the logbook and the track ------------------------------------------------------------------------
    run('the flown flight is in the logbook: Maria 1 flight, 42 minutes; N172MS 42 minutes',
        lambda d, l: (one(d, 'select FlightCount, FlownMinutes from Pilot where Id=1') == (1, 42) and one(d, 'select FlownMinutes from Aircraft where Id=1') == 42,
                      one(d, 'select FlightCount, FlownMinutes from Pilot where Id=1')))

    def closed(d, l):
        ok = l.update('FlightPlan', {'Id': 1, 'Status': 'C'})
        return ok and one(d, 'select FlightCount, FlownMinutes from Pilot where Id=1') == (2, 92) and one(d, 'select FlownMinutes from Aircraft where Id=1') == 92, (l.message, one(d, 'select FlightCount, FlownMinutes from Pilot where Id=1'))
    run('Nantucket is flown and closed: the pilot\'s and the aircraft\'s logbooks add 50 minutes', closed)
    run('the flown flight has its track: 11 position reports',
        lambda d, l: (P(d, 7, 'ReportCount') == 11, P(d, 7, 'ReportCount')))
    run('a position off the globe is refused',
        lambda d, l: (not l.insert('PositionReport', {'Id': 100, 'Callsign': 'N1X', 'ReportTime': '2026-11-26T12:00:00Z', 'Latitude': 95, 'Longitude': -71}) and 'no position' in l.message, l.message))

    # --- deleting -----------------------------------------------------------------------------------------
    run('a flown flight (it has a track) cannot be deleted',
        lambda d, l: (not l.delete('FlightPlan', {'Id': 7}) and 'track is on file' in l.message, l.message))

    def delete_plan(d, l):
        ok = l.delete('FlightPlan', {'Id': 3})
        return ok and one(d, 'select count(*) from Leg where FlightPlanId=3') == 0, l.message
    run('deleting a plan deletes its legs', delete_plan)
    run('a pilot with flight plans cannot be deleted',
        lambda d, l: (not l.delete('Pilot', {'Id': 2}) and 'has flight plans' in l.message, l.message))
    run('an aircraft with flight plans cannot be deleted',
        lambda d, l: (not l.delete('Aircraft', {'Id': 3}) and 'has flight plans' in l.message, l.message))
    run('an aircraft type with aircraft on file cannot be deleted',
        lambda d, l: (not l.delete('AircraftType', {'Id': 4}) and 'aircraft of this type' in l.message, l.message))

    shutil.rmtree(folder, ignore_errors=True)
    return results


def run_all():
    folder = tempfile.mkdtemp()
    try:
        base = build_db.build(os.path.join(folder, 'flightplanner.sqlite'))
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
            print('flightplanner --prove: the scenarios must pass first')
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
        print(f'flightplanner --prove: {len(rules)} rules, {len(unproven)} not proven')
        return 1 if unproven else 0
    results = run_all()
    for name, ok, detail in results:
        print(('PASS  ' if ok else 'FAIL  ') + name + ('' if ok else f'   ({detail})'))
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f'flight planner rules: {len(results)} scenarios, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
