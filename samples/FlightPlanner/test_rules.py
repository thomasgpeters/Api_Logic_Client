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
    T = lambda d, i, cols: one(d, f'select {cols} from Pilot where Id={i}')
    A = lambda d, i, cols: one(d, f'select {cols} from Aircraft where Id={i}')
    R = lambda d, i: P(d, i, 'GoNoGo, NoGoReason')

    def go(d, i):
        return R(d, i) == ('GO', None)

    def no_go(i, text):
        return lambda d, l: (R(d, i)[0] == 'NO-GO' and text in (R(d, i)[1] or ''), R(d, i))

    def then(i, text, *changes):
        """apply the changes; the plan's reason must then contain text ('' = GO)"""
        def body(d, l):
            for table, record in changes:
                if not l.update(table, record):
                    return False, l.message
            return (go(d, i) if text == '' else (R(d, i)[0] == 'NO-GO' and text in (R(d, i)[1] or ''))), R(d, i)
        return body

    def refused(action, table, record, text):
        def body(d, l):
            ok = getattr(l, action)(table, record)
            return (not ok) and text in l.message, l.message
        return body

    # --- airports, runways, weather ----------------------------------------------------------------------
    run('a runway takes its airport\'s variation and airspace',
        lambda d, l: (one(d, 'select Variation, Airspace from Runway where Id=27') == (16, 'G'), one(d, 'select Variation, Airspace from Runway where Id=27')))
    run('the weather: density altitude from elevation, altimeter and temperature; fog is LIFR',
        lambda d, l: (one(d, 'select DensityAltitude, Category from Weather where Id=1') == (-1163, 'VFR') and one(d, 'select Category from Weather where Id=23') == 'LIFR',
                      one(d, 'select DensityAltitude, Category from Weather where Id=1')))

    def categories(d, l):
        got = []
        for vis, ceiling in ((4, None), (2, 2000), (0.5, 2000)):
            l.update('Weather', {'Id': 22, 'Visibility': vis, 'Ceiling': ceiling})
            got.append(one(d, 'select Category from Weather where Id=22'))
        return got == ['MVFR', 'IFR', 'LIFR'], got
    run('flight categories: 4 SM is MVFR, 2 SM IFR, half a mile LIFR', categories)

    def hot_day(d, l):
        ok = l.update('Weather', {'Id': 11, 'Temperature': 35, 'Altimeter': 29.80})   # a hot day at Lebanon
        return ok and one(d, 'select DensityAltitude from Weather where Id=11') == 3297 and L(d, 6, 'LandingDistance') == 1177, (l.message, one(d, 'select DensityAltitude from Weather where Id=11'), L(d, 6, 'LandingDistance'))
    run('a hot day at Lebanon: 3,297 ft density altitude, the Cub\'s landing grows to 1,177 ft', hot_day)

    # --- aircraft ---------------------------------------------------------------------------------------
    run('an aircraft takes its type\'s figures',
        lambda d, l: (A(d, 3, 'CruiseKnots, FuelBurn, UsableFuel, MaxCrosswind, TakeoffDistance, LandingDistance, TaxiFuel, ClimbFuel') == (170, 15.0, 81.0, 21, 1600, 2300, 1.5, 3.0),
                      A(d, 3, 'CruiseKnots, FuelBurn, UsableFuel, MaxCrosswind, TakeoffDistance, LandingDistance, TaxiFuel, ClimbFuel')))
    run('inspections fall due at the end of the month: annual 12, transponder 24, ELT 12 months',
        lambda d, l: (A(d, 1, 'AnnualDue, TransponderDue, EltDue') == ('2027-04-30', '2027-05-31', '2027-04-30'), A(d, 1, 'AnnualDue, TransponderDue, EltDue')))
    run('the empty moment is weight x arm', lambda d, l: (A(d, 1, 'EmptyMoment') == 67200.0, A(d, 1, 'EmptyMoment')))
    run('the annual ran out on 31 October: N172TB is NO-GO', no_go(9, 'annual inspection'))
    run('the annual is signed off: GO', then(9, '', ('Aircraft', {'Id': 5, 'LastAnnual': '2026-11-27'})))
    run('the transponder check ran out: NO-GO', then(9, 'transponder check', ('Aircraft', {'Id': 5, 'LastAnnual': '2026-11-27', 'LastTransponder': '2024-09-01'})))
    run('the ELT inspection ran out: NO-GO', then(9, 'ELT inspection', ('Aircraft', {'Id': 5, 'LastAnnual': '2026-11-27', 'LastElt': '2025-09-01'})))
    run('the ELT battery expired: NO-GO', then(9, 'ELT battery', ('Aircraft', {'Id': 5, 'LastAnnual': '2026-11-27', 'EltBatteryExpires': '2026-11-01'})))
    run('the club\'s Archer near its 100-hour: Hannah\'s flight would run past it',
        then(4, '100-hour', ('Pilot', {'Id': 3, 'MedicalExam': '2026-11-20'}), ('Aircraft', {'Id': 2, 'Hours100Base': 99.8})))

    def logbook_hours(d, l):
        ok = l.update('FlightPlan', {'Id': 12, 'Status': 'C'})
        return ok and A(d, 2, 'FlownMinutes, HoursSince100') == (28, 99.5) and T(d, 5, 'FlightCount, FlownMinutes') == (1, 28), (l.message, A(d, 2, 'FlownMinutes, HoursSince100'))
    run('Ray lands and closes: 28 minutes in his logbook and the Archer\'s, now 99.5 hours since its 100-hour', logbook_hours)

    # --- the pilot --------------------------------------------------------------------------------------
    run('medicals: Maria 38 at the exam (60 months), Dev 55 (24 months), Hannah 46 (24 months: 30 November)',
        lambda d, l: ([T(d, i, 'MedicalExpires') for i in (1, 2, 3)] == ['2028-06-30', '2027-03-31', '2026-11-30'], [T(d, i, 'MedicalExpires') for i in (1, 2, 3)]))
    run('Hannah\'s medical runs out on the 30th: the Vineyard on 3 December is NO-GO', no_go(4, 'medical is not valid'))
    run('Hannah sees her examiner: GO, and the plan is filed',
        lambda d, l: (l.update('Pilot', {'Id': 3, 'MedicalExam': '2026-11-20'}) and go(d, 4) and l.update('FlightPlan', {'Id': 4, 'Status': 'F'}), (l.message, R(d, 4))))
    run('BasicMed: Ray\'s course (24 months) and exam (48 months) - the earlier, 31 August 2027',
        lambda d, l: (T(d, 5, 'MedicalExpires, BasicMedUntil') == ('2017-05-31', '2027-08-31') and P(d, 12, 'Status') == 'A', T(d, 5, 'MedicalExpires, BasicMedUntil')))
    run('Ray\'s BasicMed course lapses: no medical, NO-GO', then(12, 'medical', ('FlightPlan', {'Id': 12, 'Status': 'C'}), ('Pilot', {'Id': 5, 'BasicMedCourse': '2024-08-01'})))
    run('the flight review falls due at the end of the 24th month', lambda d, l: (T(d, 1, 'ReviewDue') == '2027-09-30', T(d, 1, 'ReviewDue')))
    run('Dev\'s flight review is due: NO-GO', then(9, 'flight review', ('Aircraft', {'Id': 5, 'LastAnnual': '2026-11-27'}), ('Pilot', {'Id': 2, 'FlightReview': '2024-10-01'})))
    run('the logbook: Maria 7 landings and 3 night landings in the last 90 days; Dev\'s July night landings do not count',
        lambda d, l: (T(d, 1, 'Landings90, NightLandings90') == (7, 3) and T(d, 2, 'Landings90, NightLandings90') == (3, 0), (T(d, 1, 'Landings90, NightLandings90'), T(d, 2, 'Landings90, NightLandings90'))))
    run('a day moves on: counted back from 15 February, Dev\'s November landings drop out',
        lambda d, l: (l.update('Pilot', {'Id': 2, 'AsOf': '2027-02-15'}) and T(d, 2, 'Landings90') == 0, T(d, 2, 'Landings90')))
    run('more night landings than landings is refused',
        refused('insert', 'LogbookEntry', {'Id': 100, 'PilotId': 1, 'EntryDate': '2026-11-25', 'Minutes': 30, 'Landings': 1, 'NightLandings': 3}, 'only 1 landings'))
    run('Dev\'s last night landings were in July: a night flight with a friend is NO-GO', no_go(3, 'Not night current'))
    run('Dev logs three night landings: GO',
        lambda d, l: (l.insert('LogbookEntry', {'Id': 100, 'PilotId': 2, 'EntryDate': '2026-11-25', 'Minutes': 40, 'Landings': 3, 'NightLandings': 3}) and go(d, 3), R(d, 3)))
    run('Dev flies alone: night currency is for passengers - GO',
        lambda d, l: (l.delete('LoadItem', {'Id': 8}) and go(d, 3), R(d, 3)))
    run('Dev carries a friend by day with only 2 recent landings: NO-GO',
        then(9, 'carry passengers', ('Aircraft', {'Id': 5, 'LastAnnual': '2026-11-27'}), ('LogbookEntry', {'Id': 4, 'Landings': 2})) if False else
        (lambda d, l: (l.update('Aircraft', {'Id': 5, 'LastAnnual': '2026-11-27'}) and l.update('LogbookEntry', {'Id': 4, 'Landings': 2})
                       and l.insert('LoadItem', {'Id': 100, 'FlightPlanId': 9, 'AircraftStationId': 14, 'Description': 'Friend', 'Persons': 1, 'Weight': 160})
                       and 'carry passengers' in (R(d, 9)[1] or ''), R(d, 9))))

    # --- students -------------------------------------------------------------------------------------
    run('Tom\'s solo endorsement is recent; his cross-country endorsement is for this flight',
        lambda d, l: (T(d, 4, 'SoloEndorsements') == 1 and P(d, 5, 'Student, XcEndorsements') == (1, 1), (T(d, 4, 'SoloEndorsements'), P(d, 5, 'Student, XcEndorsements'))))
    run('a student carries no passengers',
        lambda d, l: (l.insert('LoadItem', {'Id': 100, 'FlightPlanId': 5, 'AircraftStationId': 11, 'Description': 'Friend', 'Persons': 1, 'Weight': 150})
                      and 'carries no passengers' in (R(d, 5)[1] or ''), R(d, 5)))
    run('Tom\'s solo endorsement is 100 days old: NO-GO', then(5, 'No solo endorsement', ('Endorsement', {'Id': 1, 'EndorsedDate': '2026-08-18'})))
    run('no cross-country endorsement for this flight: NO-GO',
        lambda d, l: (l.delete('Endorsement', {'Id': 2}) and 'cross-country endorsement' in (R(d, 5)[1] or ''), R(d, 5)))
    run('a cross-country endorsement without its flight is refused',
        refused('insert', 'Endorsement', {'Id': 100, 'PilotId': 4, 'Kind': 'X', 'EndorsedDate': '2026-11-26', 'Instructor': 'K. Lindqvist, CFI'}, 'for one flight'))

    def class_b(d, l):
        ok = l.insert('FlightPlan', {'Id': 100, 'PilotId': 4, 'AircraftId': 4, 'RunwayId': 26, 'WeatherId': 10, 'DepartureDate': '2026-11-29', 'FuelOnBoard': 12, 'Status': 'D'})
        ok = ok and l.insert('LoadItem', {'Id': 100, 'FlightPlanId': 100, 'AircraftStationId': 12, 'Description': 'Tom', 'Persons': 1, 'Weight': 165})
        ok = ok and l.insert('Leg', {'Id': 100, 'FlightPlanId': 100, 'FromAirportId': 9, 'ToAirportId': 12, 'RunwayId': 33, 'Altitude': 2500, 'WindDirection': 330, 'WindSpeed': 10})
        first = L(d, 100, 'Problem')
        ok = ok and l.insert('Weather', {'Id': 100, 'AirportId': 12, 'ObservedAt': '2026-11-29T14:00Z', 'WindDirection': 40, 'WindSpeed': 5, 'Visibility': 10, 'Temperature': 5, 'Altimeter': 30.1})
        ok = ok and l.update('Leg', {'Id': 100, 'WeatherId': 100})
        second = R(d, 100)
        ok = ok and l.insert('Endorsement', {'Id': 100, 'PilotId': 4, 'Kind': 'B', 'EndorsedDate': '2026-11-26', 'Instructor': 'K. Lindqvist, CFI'})
        return ok and P(d, 100, 'ClassBLegs') == 1 and first == 'No weather briefed for KBOS' and L(d, 100, 'Problem') is None and 'Class B' in (second[1] or '') and go(d, 100), (l.message, first, second, R(d, 100))
    run('Tom to Boston Logan: no weather briefed for the leg; no Class B endorsement; endorsed - GO', class_b)

    # --- legs: course, wind, time, fuel --------------------------------------------------------------------
    run('Bedford - Hyannis: 65.8 NM, true course 137, magnetic 152',
        lambda d, l: (L(d, 1, 'Distance, TrueCourse, MagneticCourse') == (65.8, 137, 152), L(d, 1, 'Distance, TrueCourse, MagneticCourse')))
    run('the wind triangle: 290 at 20 kt - correct 4 degrees right, heading 141 true / 156 magnetic, 137 kt over the ground',
        lambda d, l: (L(d, 1, 'WindCorrection, TrueHeading, MagneticHeading, GroundSpeed') == (4, 141, 156, 137), L(d, 1, 'WindCorrection, TrueHeading, MagneticHeading, GroundSpeed')))
    run('29 minutes and 4.1 gallons for the leg', lambda d, l: (L(d, 1, 'Minutes, Fuel') == (29, 4.1), L(d, 1, 'Minutes, Fuel')))

    def wind_turns(d, l):
        ok = l.update('Leg', {'Id': 1, 'WindDirection': 137, 'WindSpeed': 30})      # straight on the nose
        return ok and L(d, 1, 'WindCorrection, GroundSpeed, Minutes') == (0, 90, 44) and P(d, 1, 'Minutes') == 57, (l.message, L(d, 1, 'WindCorrection, GroundSpeed, Minutes'))
    run('the wind backs onto the nose: 90 kt over the ground, the leg and the plan take longer', wind_turns)

    def variation(d, l):
        ok = l.update('Airport', {'Id': 1, 'Variation': 14})
        return ok and L(d, 1, 'MagneticCourse, MagneticHeading') == (151, 155), (l.message, L(d, 1, 'MagneticCourse, MagneticHeading'))
    run('the variation at Bedford is updated: magnetic course and heading follow', variation)

    def moved(d, l):
        ok = l.update('Leg', {'Id': 5, 'ToAirportId': 5, 'RunwayId': 16, 'WeatherId': 3})
        return ok and L(d, 5, 'Distance, TrueCourse') == (67.7, 114), (l.message, L(d, 5, 'Distance, TrueCourse'))
    run('a leg goes to another airport: distance and course again', moved)

    def other_aircraft(d, l):
        ok = l.update('FlightPlan', {'Id': 6, 'AircraftId': 1})
        ok = ok and l.update('LoadItem', {'Id': 11, 'AircraftStationId': 1})
        return ok and P(d, 6, 'CruiseKnots, FuelBurn, MaxCrosswind, LandingDistance') == (120, 8.5, 15, 1335) and L(d, 7, 'GroundSpeed, Fuel, Problem') == (130, 1.8, None) and go(d, 6), (l.message, L(d, 7, 'GroundSpeed, Fuel, Problem'), R(d, 6))
    run('Plum Island in the Skyhawk instead: the plan takes its figures, lands in 2,003 ft x 1.5 - GO', other_aircraft)

    run('a leg that starts and ends at the same airport is refused',
        refused('insert', 'Leg', {'Id': 100, 'FlightPlanId': 3, 'FromAirportId': 8, 'ToAirportId': 8, 'Altitude': 4500}, 'same airport'))
    run('a wind as fast as the aircraft is refused', refused('update', 'Leg', {'Id': 6, 'WindSpeed': 70}, 'as fast as the aircraft'))
    run('a cruise less than 1,000 ft above the airports is refused (Worcester is at 1,009 ft)', refused('update', 'Leg', {'Id': 11, 'Altitude': 1500}, '1,000 ft above'))
    run('a leg to an airport that does not exist is refused', refused('insert', 'Leg', {'Id': 100, 'FlightPlanId': 3, 'FromAirportId': 8, 'ToAirportId': 99, 'Altitude': 4500}, 'no airport 99 to fly'))
    run('a leg from an airport that does not exist is refused', refused('insert', 'Leg', {'Id': 100, 'FlightPlanId': 3, 'FromAirportId': 99, 'ToAirportId': 8, 'Altitude': 4500}, 'no airport 99 to leave'))
    run('a landing runway at another airport is refused', refused('update', 'Leg', {'Id': 1, 'RunwayId': 1}, 'not at the destination'))
    run('weather from another airport is refused', refused('update', 'Leg', {'Id': 1, 'WeatherId': 1}, 'not the destination'))

    # --- legs: the problems ---------------------------------------------------------------------------------
    run('westbound at 5,500, an eastbound altitude: the leg\'s problem, the plan NO-GO',
        lambda d, l: (L(d, 10, 'Problem').startswith('5500 ft is not a VFR cruising altitude') and P(d, 8, 'LegProblems') == 1 and 'see the legs' in R(d, 8)[1], (L(d, 10, 'Problem'), R(d, 8))))

    def climb_then_closed(d, l):
        ok = l.update('Leg', {'Id': 10, 'Altitude': 6500})
        first = L(d, 10, 'Problem')
        ok = ok and l.update('Notam', {'Id': 1, 'Active': 0})
        ok = ok and l.update('FlightPlan', {'Id': 8, 'Status': 'F'})
        return ok and first == 'KBAF is closed (NOTAM)' and one(d, 'select ClosedNotams from Airport where Id=11') == 0 and go(d, 8), (l.message, first, R(d, 8))
    run('Hannah climbs to 6,500: Westfield is closed for the air show; the NOTAM ends - GO, filed', climb_then_closed)
    run('an obstacle NOTAM does not close Portsmouth', lambda d, l: (one(d, 'select ClosedNotams from Airport where Id=7') == 0 and one(d, 'select ClosedNotams from Airport where Id=11') == 1, None))
    run('no landing runway chosen', lambda d, l: (l.update('Leg', {'Id': 5, 'RunwayId': None}) and L(d, 5, 'Problem') == 'No landing runway chosen at KMVY', L(d, 5, 'Problem')))
    run('Plum Island\'s 2,105 ft of turf: the SR22 needs 2,300 x 1.5', lambda d, l: (L(d, 7, 'Problem') == 'Landing needs 2300 ft x 1.5: runway 28 at 2B2 is 2105 ft', L(d, 7, 'Problem')))
    run('no weather briefed', lambda d, l: (l.update('Leg', {'Id': 5, 'WeatherId': None}) and L(d, 5, 'Problem') == 'No weather briefed for KMVY', L(d, 5, 'Problem')))
    run('19 kt across runway 24 at the Vineyard: the Skyhawk is demonstrated to 15', no_go(10, 'see the legs'))

    def runway_33(d, l):
        ok = l.update('Leg', {'Id': 12, 'RunwayId': 20})
        return ok and L(d, 12, 'Crosswind, Problem') == (5, None) and go(d, 10), (l.message, L(d, 12, 'Crosswind, Problem'), R(d, 10))
    run('runway 33 instead, into the wind: 5 kt across, 3,297 ft is enough - GO', runway_33)
    run('the crosswind counts the gust',
        lambda d, l: (l.update('Weather', {'Id': 11, 'WindDirection': 70, 'WindSpeed': 5, 'Gust': 12}) and L(d, 6, 'Crosswind') == 12 and 'crosswind' in (L(d, 6, 'Problem') or ''), L(d, 6, 'Crosswind, Problem')))
    run('Nantucket in fog: 1 SM, 300 ft - below the minimums', lambda d, l: (L(d, 13, 'Problem') == 'Below VFR minimums at KACK: 1 SM, ceiling 300 ft', L(d, 13, 'Problem')))

    def fog_lifts(d, l):
        ok = l.update('Weather', {'Id': 23, 'Visibility': 6, 'Ceiling': 2500})
        return ok and go(d, 11), (l.message, R(d, 11))
    run('the fog lifts to 6 SM, 2,500 ft: GO', fog_lifts)
    run('a student needs 5 SM at night',
        lambda d, l: (l.update('Weather', {'Id': 11, 'Visibility': 4}) and l.update('FlightPlan', {'Id': 5, 'Night': 1, 'FuelOnBoard': 12}) and 'Below VFR minimums' in (L(d, 6, 'Problem') or ''), L(d, 6, 'Problem')))
    run('uncontrolled (G) by day: 1 SM is enough, for a private pilot',
        lambda d, l: (l.update('Weather', {'Id': 13, 'Visibility': 1.5}) and l.update('FlightPlan', {'Id': 6, 'AircraftId': 1}) and l.update('LoadItem', {'Id': 11, 'AircraftStationId': 1})
                      and L(d, 7, 'Problem') is None, L(d, 7, 'Problem')))
    run('a landing at Logan is a Class B leg', lambda d, l: (l.update('Leg', {'Id': 8, 'ToAirportId': 12, 'RunwayId': 33, 'WeatherId': None}) and L(d, 8, 'ToAirspace') == 'B' and P(d, 7, 'ClassBLegs') == 1, L(d, 8, 'ToAirspace')))

    # --- weight and balance ------------------------------------------------------------------------------------
    run('the load: a station\'s arm and limit, and each item\'s moment',
        lambda d, l: (one(d, 'select Arm, MaxWeight, Moment from LoadItem where Id=3') == (95.0, 120.0, 3800.0), one(d, 'select Arm, MaxWeight, Moment from LoadItem where Id=3')))
    run('Maria\'s Nantucket trip: 2 aboard, 2,273.4 lb at takeoff, CG 41.37 within 38.23 - 47.3, 2,229 lb landing',
        lambda d, l: (P(d, 1, 'PersonsOnBoard, PayloadWeight, RampWeight, TakeoffWeight, CG, ForwardLimit, LandingWeight') == (2, 360.0, 2280.0, 2273.4, 41.37, 38.23, 2229.0),
                      P(d, 1, 'PersonsOnBoard, PayloadWeight, RampWeight, TakeoffWeight, CG, ForwardLimit, LandingWeight')))

    def heavy(d, l):
        ok = l.insert('LoadItem', {'Id': 100, 'FlightPlanId': 1, 'AircraftStationId': 2, 'Description': 'Two more', 'Persons': 2, 'Weight': 340})
        return ok and 'the maximum is 2550' in (R(d, 1)[1] or '') if False else (ok and R(d, 1)[0] == 'NO-GO' and 'maximum is 2550' in (R(d, 1)[1] or '')), (l.message, R(d, 1))
    run('two more friends in the back: over the maximum takeoff weight - and a filed plan cannot take them', lambda d, l: (not l.insert('LoadItem', {'Id': 100, 'FlightPlanId': 1, 'AircraftStationId': 2, 'Description': 'Two more', 'Persons': 2, 'Weight': 340}) and 'maximum is 2550' in l.message, l.message))
    run('over the maximum takeoff weight: NO-GO',
        lambda d, l: (l.insert('LoadItem', {'Id': 100, 'FlightPlanId': 11, 'AircraftStationId': 2, 'Description': 'Two more', 'Persons': 2, 'Weight': 340}) and 'maximum is 2550' in (R(d, 11)[1] or ''), R(d, 11)))
    run('a heavy load in the baggage B corner: the CG is aft of the limit',
        lambda d, l: (l.insert('LoadItem', {'Id': 100, 'FlightPlanId': 10, 'AircraftStationId': 4, 'Description': 'Tools', 'Persons': 0, 'Weight': 50})
                      and l.insert('LoadItem', {'Id': 101, 'FlightPlanId': 10, 'AircraftStationId': 3, 'Description': 'Cases', 'Persons': 0, 'Weight': 120})
                      and l.insert('LoadItem', {'Id': 102, 'FlightPlanId': 10, 'AircraftStationId': 2, 'Description': 'Two friends', 'Persons': 2, 'Weight': 300})
                      and l.update('Leg', {'Id': 12, 'RunwayId': 20}) and l.update('FlightPlan', {'Id': 10, 'FuelOnBoard': 10})
                      and 'centre of gravity' in (R(d, 10)[1] or ''), (P(d, 10, 'CG'), R(d, 10))))
    run('a heavy pilot in the front of the SR22, no fuel aft: the CG is forward of the limit',
        lambda d, l: (l.update('LoadItem', {'Id': 11, 'Weight': 390}) and l.update('Aircraft', {'Id': 3, 'FwdLimitLight': 141.5}) and 'centre of gravity' in (R(d, 6)[1] or ''), (P(d, 6, 'CG, ForwardLimit'), R(d, 6))))
    run('the forward limit slopes: heavier, further aft',
        lambda d, l: (P(d, 3, 'ForwardLimit') == 139.45 and P(d, 4, 'ForwardLimit') == 82.0, (P(d, 3, 'ForwardLimit'), P(d, 4, 'ForwardLimit'))))
    run('more than a station takes is refused', refused('insert', 'LoadItem', {'Id': 100, 'FlightPlanId': 4, 'AircraftStationId': 7, 'Description': 'Crates', 'Persons': 0, 'Weight': 250}, 'the station takes 200'))
    run('a station of another aircraft is refused', refused('insert', 'LoadItem', {'Id': 100, 'FlightPlanId': 4, 'AircraftStationId': 1, 'Description': 'Bags', 'Persons': 0, 'Weight': 20}, 'not in this plan\'s aircraft'))
    run('no one on board: NO-GO', lambda d, l: (l.delete('LoadItem', {'Id': 9}) and 'No one on board' in (R(d, 4)[1] or ''), R(d, 4)))

    # --- departure ------------------------------------------------------------------------------------------------
    run('the takeoff distance grows with weight and density altitude: 1,453 ft for Nantucket\'s Skyhawk',
        lambda d, l: (P(d, 1, 'TakeoffDistance') == 1453, P(d, 1, 'TakeoffDistance')))
    run('the SR22 off Plum Island on a warm day: 1,600 x weight x density altitude x 1.5 is more than 2,105 ft',
        lambda d, l: (l.update('FlightPlan', {'Id': 6, 'RunwayId': 28, 'WeatherId': 13}) and l.update('Weather', {'Id': 13, 'Temperature': 30}) and 'Takeoff needs' in (R(d, 6)[1] or ''), R(d, 6)))
    run('departure crosswind: Bedford 23 in a 20 kt north-westerly is too much for the Skyhawk',
        lambda d, l: (l.update('Weather', {'Id': 12, 'WindDirection': 310, 'WindSpeed': 20}) and l.update('FlightPlan', {'Id': 6, 'AircraftId': 1}) and l.update('LoadItem', {'Id': 11, 'AircraftStationId': 1})
                      and 'crosswind on departure' in (R(d, 6)[1] or ''), (P(d, 6, 'Crosswind'), R(d, 6))))
    run('departure below VFR minimums', lambda d, l: (l.update('Weather', {'Id': 18, 'Visibility': 2}) and l.update('Aircraft', {'Id': 5, 'LastAnnual': '2026-11-27'}) and R(d, 9)[1] == 'Below VFR minimums for departure', R(d, 9)))
    run('no departure weather: NO-GO', lambda d, l: (l.update('FlightPlan', {'Id': 4, 'WeatherId': None}) and l.update('Pilot', {'Id': 3, 'MedicalExam': '2026-11-20'}) and R(d, 4)[1] == 'No departure runway or weather', R(d, 4)))
    run('departure weather from another airport is refused', refused('update', 'FlightPlan', {'Id': 4, 'WeatherId': 1}, 'departure runway\'s airport'))

    # --- the plan: totals, fuel, times ----------------------------------------------------------------------------------
    run('Bedford - Hyannis - Nantucket: 2 legs, 92.7 NM, 42 minutes, 5.9 gallons',
        lambda d, l: (P(d, 1, 'LegCount, round(Distance, 1), Minutes, round(TripFuel, 1)') == (2, 92.7, 42, 5.9), P(d, 1, 'LegCount, Distance, Minutes, TripFuel')))
    run('fuel: taxi 1.1 + climb 1.5 + trip + reserve 4.3 by day = 12.8; 6.4 reserve at night',
        lambda d, l: (P(d, 1, 'ReserveFuel, FuelRequired, FuelMargin') == (4.3, 12.8, 27.2) and P(d, 2, 'ReserveFuel') == 6.4, P(d, 1, 'ReserveFuel, FuelRequired, FuelMargin')))
    run('home before dark: the reserve and the margin follow',
        lambda d, l: (l.update('FlightPlan', {'Id': 2, 'Night': 0}) and P(d, 2, 'ReserveFuel, FuelRequired') == (4.3, 15.0), P(d, 2, 'ReserveFuel, FuelRequired')))
    run('endurance: 40 gallons at 8.5 an hour is 282 minutes', lambda d, l: (P(d, 1, 'Endurance') == 282, P(d, 1, 'Endurance')))
    run('the Cub to Lebanon needs 11.3 gallons; 9 on board: NO-GO', no_go(5, 'Not enough fuel: 11.3 gallons'))
    run('the Cub is topped up to 12: GO', then(5, '', ('FlightPlan', {'Id': 5, 'FuelOnBoard': 12})))
    run('more fuel than the tanks hold is refused', refused('update', 'FlightPlan', {'Id': 11, 'FuelOnBoard': 60}, 'tanks hold less'))
    run('ETA and the start of search and rescue: departure + 42 minutes, + 30',
        lambda d, l: (P(d, 1, 'ETA, SearchAt') == ('10:12', '10:42') and P(d, 12, 'ETA, SearchAt') == ('10:38', '11:08'), (P(d, 1, 'ETA, SearchAt'), P(d, 12, 'ETA, SearchAt'))))

    # --- go / no-go and the life cycle ---------------------------------------------------------------------------------
    def no_legs(d, l):
        ok = l.insert('FlightPlan', {'Id': 100, 'PilotId': 1, 'AircraftId': 1, 'DepartureDate': '2026-12-12', 'FuelOnBoard': 40, 'Status': 'D'})
        return ok and R(d, 100) == ('NO-GO', 'The plan has no legs') and not l.update('FlightPlan', {'Id': 100, 'Status': 'F'}) and 'Not filed - NO-GO' in l.message, (l.message, R(d, 100))
    run('a plan with no legs is NO-GO and cannot be filed', no_legs)
    run('a filed plan cannot be changed into a NO-GO', refused('update', 'Leg', {'Id': 3, 'Altitude': 5500}, 'Not filed'))
    run('a plan goes Draft - Filed - Active - Closed: a draft cannot be closed', refused('update', 'FlightPlan', {'Id': 3, 'Status': 'C'}, 'cannot go to C'))
    run('a plan cannot be inserted already active',
        refused('insert', 'FlightPlan', {'Id': 100, 'PilotId': 1, 'AircraftId': 1, 'DepartureDate': '2026-12-12', 'ActualDeparture': '10:00', 'FuelOnBoard': 40, 'Status': 'A'}, 'cannot go to A'))
    run('an active plan needs its actual departure time', refused('update', 'FlightPlan', {'Id': 1, 'Status': 'A'}, 'actual departure'))

    def opened(d, l):
        ok = l.update('FlightPlan', {'Id': 1, 'Status': 'A', 'ActualDeparture': '09:50'})
        ok = ok and l.update('FlightPlan', {'Id': 1, 'Status': 'C'})
        return ok and P(d, 1, 'ETA') == '10:32' and T(d, 1, 'FlightCount, FlownMinutes') == (2, 84), (l.message, P(d, 1, 'ETA'), T(d, 1, 'FlightCount, FlownMinutes'))
    run('Maria opens the plan at 09:50 (ETA 10:32), lands, closes: 2 flights, 84 minutes in her logbook', opened)
    run('the flown flight has its track: 11 position reports', lambda d, l: (P(d, 7, 'ReportCount') == 11, P(d, 7, 'ReportCount')))
    run('a position off the globe is refused',
        refused('insert', 'PositionReport', {'Id': 100, 'Callsign': 'N1X', 'ReportTime': '2026-11-26T12:00:00Z', 'Latitude': 95, 'Longitude': -71}, 'no position'))

    # --- deleting ---------------------------------------------------------------------------------------------------------
    run('a flown flight (it has a track) cannot be deleted', refused('delete', 'FlightPlan', {'Id': 7}, 'track is on file'))

    def delete_plan(d, l):
        ok = l.delete('FlightPlan', {'Id': 5})
        return ok and one(d, 'select count(*) from Leg where FlightPlanId=5') == 0 and one(d, 'select count(*) from LoadItem where FlightPlanId=5') == 0 \
            and one(d, 'select count(*) from Endorsement where Id=2') == 0, l.message
    run('deleting a plan deletes its legs, its load and its cross-country endorsement', delete_plan)
    run('a pilot with flight plans cannot be deleted', refused('delete', 'Pilot', {'Id': 2}, 'has flight plans'))

    def delete_pilot(d, l):
        ok = l.insert('Pilot', {'Id': 100, 'Name': 'New Pilot', 'AsOf': '2026-11-26'})
        ok = ok and l.insert('LogbookEntry', {'Id': 100, 'PilotId': 100, 'EntryDate': '2026-11-20', 'Landings': 1})
        ok = ok and l.insert('Endorsement', {'Id': 100, 'PilotId': 100, 'Kind': 'S', 'EndorsedDate': '2026-11-20', 'Instructor': 'K. Lindqvist, CFI'})
        ok = ok and l.delete('Pilot', {'Id': 100})
        return ok and one(d, 'select count(*) from LogbookEntry where PilotId=100') == 0 and one(d, 'select count(*) from Endorsement where PilotId=100') == 0, l.message
    run('deleting a pilot without plans takes the logbook and endorsements', delete_pilot)
    run('an aircraft with flight plans cannot be deleted', refused('delete', 'Aircraft', {'Id': 3}, 'has flight plans'))

    def delete_aircraft(d, l):
        ok = l.insert('Aircraft', {'Id': 100, 'TailNumber': 'N100X', 'AircraftTypeId': 1, 'EmptyWeight': 1600, 'EmptyArm': 40, 'MaxTakeoff': 2550, 'FuelArm': 48,
                                   'FwdLimitLight': 35, 'FwdBreakWeight': 1950, 'FwdLimitHeavy': 41, 'AftLimit': 47.3})
        ok = ok and l.insert('AircraftStation', {'Id': 100, 'AircraftId': 100, 'Name': 'Front seats', 'Arm': 37, 'MaxWeight': 400})
        ok = ok and l.delete('Aircraft', {'Id': 100})
        return ok and one(d, 'select count(*) from AircraftStation where AircraftId=100') == 0, l.message
    run('deleting an aircraft without plans takes its stations', delete_aircraft)
    run('an aircraft type with aircraft on file cannot be deleted', refused('delete', 'AircraftType', {'Id': 4}, 'aircraft of this type'))

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
