"""The Flight Planner sample's business rules - the reference, run here by tools/logic_reference.py's engine
(the same engine, function for function, as LogicBank for FutureBasic in a generated app).
Research and regulations: docs/research/Flight Planning Research.md.

    a leg        distance and initial true course by the great circle; magnetic course; the wind triangle
                 (wind correction, true and magnetic heading, ground speed); minutes and fuel; the landing
                 distance at the destination's density altitude; the crosswind on the landing runway; and
                 its Problem: a cruising altitude 91.159 does not allow, the airport closed by a NOTAM, no
                 runway or one too short (x 1.5), no weather briefed, too much crosswind, below the VFR
                 minimums (91.155; tighter for students, 61.89)
    the load     weight and balance: each item's moment from its station; ramp, takeoff and landing
                 weight; the centre of gravity against the envelope (a sloped forward limit)
    the plan     legs added up; fuel = taxi + climb + trip + reserve (30 minutes by day, 45 at night, 91.151);
                 endurance; the takeoff distance at the departure's density altitude and weight; ETA and
                 the time search and rescue begins (ETA + 30)
    the pilot    medical expiry from the exam and the age at it (61.23), or BasicMed; flight review (61.56);
                 landings and night landings in 90 days from the logbook (61.57); a student's endorsements
    the aircraft annual (91.409), transponder (91.413), ELT and its battery (91.207), 100-hour when for hire
    go / no-go   the first reason the flight may not go; filed only on a GO; Draft - Filed - Active - Closed

Rounding is floor(x + 0.5) at a fixed number of places, the same in FB (samples/FlightPlanner/Rules.incl).
"""
import math
from datetime import date

EARTH_NM = 3440.065           # the earth's mean radius in nautical miles
FUEL_LB = 6.0                 # 100LL, pounds a gallon
NEXT_STATUS = {None: 'D', 'D': 'DF', 'F': 'DFA', 'A': 'AC', 'C': 'C'}   # Draft - Filed - Active - Closed


def rounded(x, places=0):
    scale = 10 ** places
    return math.floor(x * scale + 0.5) / scale


def great_circle(lat1, lon1, lat2, lon2):
    """(distance in NM to 0.1, initial true course in whole degrees 0-359)"""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    distance = 2 * EARTH_NM * math.atan2(math.sqrt(h), math.sqrt(1 - h))
    course = math.degrees(math.atan2(math.sin(dl) * math.cos(p2), math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)))
    return rounded(distance, 1), int(math.fmod(rounded(course) + 360, 360))


def wind_triangle(true_course, tas, wind_from, wind_speed):
    """(wind correction angle in whole degrees, ground speed in whole knots); None when the wind is as fast as the aircraft"""
    if tas <= 0 or wind_speed >= tas:
        return None
    angle = math.radians(wind_from - true_course)
    wca = math.asin(wind_speed * math.sin(angle) / tas)
    return int(rounded(math.degrees(wca))), int(rounded(tas * math.cos(wca) - wind_speed * math.cos(angle)))


def crosswind(wind_from, speed, gust, runway_heading, variation):
    """knots across the runway (the gust if there is one); the runway's heading is magnetic, the wind true"""
    strongest = max(speed or 0, gust or 0)
    return int(rounded(abs(strongest * math.sin(math.radians(wind_from - (runway_heading - variation))))))


def density_altitude(elevation, altimeter, temperature):
    pressure = elevation + (29.92 - altimeter) * 1000
    return int(rounded(pressure + 120 * (temperature - (15 - 2 * pressure / 1000))))


def distance_factor(density):
    """takeoff and landing distances grow about 10 % a thousand feet of density altitude"""
    return 1 + 0.10 * max(density or 0, 0) / 1000


def vfr_altitude_ok(altitude, magnetic_course, highest_ground):
    """14 CFR 91.159: more than 3,000 ft above the surface, magnetic course 0-179 cruises at odd thousands
    + 500, 180-359 at even thousands + 500"""
    if altitude - highest_ground <= 3000:
        return True
    if (altitude - 500) % 1000 != 0:
        return False
    return (((altitude - 500) // 1000) % 2 == 1) == (magnetic_course < 180)


def vfr_minimums_ok(airspace, night, student, visibility, ceiling):
    """91.155 at the airport (surface areas B, C, D, E: ceiling 1,000, 3 SM; G: 1 SM by day, 3 at night);
    a student (61.89): 3 SM by day, 5 at night"""
    need = 3.0 if night else 1.0
    if airspace in ('B', 'C', 'D', 'E'):
        need = 3.0
        if ceiling is not None and ceiling < 1000:
            return False
    if student:
        need = max(need, 5.0 if night else 3.0)
    return visibility >= need


def end_of_month_after(iso, months):
    """the last day of the month `months` after the date's month (calendar months)"""
    if not iso:
        return None
    try:
        y, m = int(str(iso)[:4]), int(str(iso)[5:7])
    except ValueError:
        return None
    total = y * 12 + (m - 1) + months
    y2, m2 = total // 12, total % 12 + 1
    days = 31 if m2 in (1, 3, 5, 7, 8, 10, 12) else 30 if m2 != 2 else (29 if (y2 % 4 == 0 and y2 % 100 != 0) or y2 % 400 == 0 else 28)
    return f'{y2:04d}-{m2:02d}-{days:02d}'


def age_on(birth, day):
    if not birth or not day:
        return None
    b, d = str(birth), str(day)
    return int(d[:4]) - int(b[:4]) - (1 if d[5:10] < b[5:10] else 0)


def days_between(first, last):
    try:
        return (date.fromisoformat(str(last)[:10]) - date.fromisoformat(str(first)[:10])).days
    except (TypeError, ValueError):
        return None


def within_90(first, last):
    since = days_between(first, last)
    return since is not None and 0 <= since <= 90


def clock_plus(hhmm, minutes):
    """HH:MM + minutes, around the clock; None without a time"""
    try:
        h, m = int(str(hhmm)[:2]), int(str(hhmm)[3:5])
    except (TypeError, ValueError):
        return None
    total = (h * 60 + m + int(minutes)) % 1440
    return f'{total // 60:02d}:{total % 60:02d}'


def declare(logic):
    from logic_reference import Logic
    n, v = Logic.number, Logic.value

    def parent(lr, role, attr):
        return logic.parent_value(lr, role, attr)

    def pn(lr, role, attr):
        x = parent(lr, role, attr)
        try:
            return 0.0 if x is None else float(x)
        except (TypeError, ValueError):
            return 0.0

    def text(x):
        return '' if x is None else str(x)

    def num(x):
        return f'{x:g}'

    # --- airports and runways ------------------------------------------------------------------------------
    logic.count('Airport', 'ClosedNotams', 'NotamList', lambda lr: n(lr, 'Active') != 0 and v(lr, 'Kind') in ('C', 'T'))
    logic.copy('Runway', 'Variation', 'Airport', 'Variation')
    logic.copy('Runway', 'Airspace', 'Airport', 'Airspace')

    # --- weather --------------------------------------------------------------------------------------------
    logic.formula('Weather', 'DensityAltitude', lambda lr: density_altitude(pn(lr, 'Airport', 'Elevation'), n(lr, 'Altimeter'), n(lr, 'Temperature')),
                  ['AirportId', 'Airport.Elevation', 'Altimeter', 'Temperature'])

    def category(lr):
        vis, ceiling = n(lr, 'Visibility'), v(lr, 'Ceiling')
        c = 99999 if ceiling is None else float(ceiling)
        if c < 500 or vis < 1:
            return 'LIFR'
        if c < 1000 or vis < 3:
            return 'IFR'
        if c <= 3000 or vis <= 5:
            return 'MVFR'
        return 'VFR'
    logic.formula('Weather', 'Category', category, ['Visibility', 'Ceiling'])

    # --- aircraft: this airframe's figures, from its type -----------------------------------------------------
    for attr in ('CruiseKnots', 'FuelBurn', 'UsableFuel', 'MaxCrosswind', 'TakeoffDistance', 'LandingDistance', 'TaxiFuel', 'ClimbFuel'):
        logic.copy('Aircraft', attr, 'AircraftType', attr)
    logic.formula('Aircraft', 'EmptyMoment', lambda lr: rounded(n(lr, 'EmptyWeight') * n(lr, 'EmptyArm'), 1), ['EmptyWeight', 'EmptyArm'])
    logic.formula('Aircraft', 'AnnualDue', lambda lr: end_of_month_after(v(lr, 'LastAnnual'), 12), ['LastAnnual'])
    logic.formula('Aircraft', 'TransponderDue', lambda lr: end_of_month_after(v(lr, 'LastTransponder'), 24), ['LastTransponder'])
    logic.formula('Aircraft', 'EltDue', lambda lr: end_of_month_after(v(lr, 'LastElt'), 12), ['LastElt'])
    logic.formula('Aircraft', 'HoursSince100', lambda lr: rounded(n(lr, 'Hours100Base') + n(lr, 'FlownMinutes') / 60.0, 1), ['Hours100Base', 'FlownMinutes'])
    logic.delete_action('AircraftType', 'AircraftList', 'prevent', '{Model}: aircraft of this type are on file')
    logic.delete_action('Aircraft', 'FlightPlanList', 'prevent', '{TailNumber} has flight plans')
    logic.delete_action('Aircraft', 'AircraftStationList', 'cascade')

    # --- the pilot ------------------------------------------------------------------------------------------
    def medical_expires(lr):
        if v(lr, 'MedicalClass') is None or not v(lr, 'MedicalExam'):
            return None
        age = age_on(v(lr, 'BirthDate'), v(lr, 'MedicalExam'))
        return end_of_month_after(v(lr, 'MedicalExam'), 60 if age is not None and age < 40 else 24)
    logic.formula('Pilot', 'MedicalExpires', medical_expires, ['MedicalClass', 'MedicalExam', 'BirthDate'])

    def basicmed_until(lr):
        course, exam = end_of_month_after(v(lr, 'BasicMedCourse'), 24), end_of_month_after(v(lr, 'BasicMedExam'), 48)
        return None if course is None or exam is None else min(course, exam)
    logic.formula('Pilot', 'BasicMedUntil', basicmed_until, ['BasicMedCourse', 'BasicMedExam'])
    logic.formula('Pilot', 'ReviewDue', lambda lr: end_of_month_after(v(lr, 'FlightReview'), 24), ['FlightReview'])
    logic.formula('LogbookEntry', 'Recent', lambda lr: 1 if within_90(v(lr, 'EntryDate'), parent(lr, 'Pilot', 'AsOf')) else 0,
                  ['EntryDate', 'PilotId', 'Pilot.AsOf'])
    logic.constraint('LogbookEntry', lambda lr: n(lr, 'NightLandings') <= n(lr, 'Landings'), '{NightLandings} night landings, but only {Landings} landings')
    logic.sum('Pilot', 'Landings90', 'LogbookEntryList', 'Landings', lambda lr: n(lr, 'Recent') != 0)
    logic.sum('Pilot', 'NightLandings90', 'LogbookEntryList', 'NightLandings', lambda lr: n(lr, 'Recent') != 0)
    logic.formula('Endorsement', 'Recent', lambda lr: 1 if within_90(v(lr, 'EndorsedDate'), parent(lr, 'Pilot', 'AsOf')) else 0,
                  ['EndorsedDate', 'PilotId', 'Pilot.AsOf'])
    logic.count('Pilot', 'SoloEndorsements', 'EndorsementList', lambda lr: v(lr, 'Kind') == 'S' and n(lr, 'Recent') != 0)
    logic.count('Pilot', 'ClassBEndorsements', 'EndorsementList', lambda lr: v(lr, 'Kind') == 'B' and n(lr, 'Recent') != 0)
    logic.constraint('Endorsement', lambda lr: v(lr, 'Kind') != 'X' or v(lr, 'FlightPlanId') is not None,
                     'A cross-country endorsement is for one flight: choose its flight plan')
    flown = lambda lr: v(lr, 'Status') == 'C'
    logic.count('Pilot', 'FlightCount', 'FlightPlanList', flown)
    logic.sum('Pilot', 'FlownMinutes', 'FlightPlanList', 'Minutes', flown)
    logic.sum('Aircraft', 'FlownMinutes', 'FlightPlanList', 'Minutes', flown)
    logic.delete_action('Pilot', 'FlightPlanList', 'prevent', '{Name} has flight plans')
    logic.delete_action('Pilot', 'LogbookEntryList', 'cascade')
    logic.delete_action('Pilot', 'EndorsementList', 'cascade')

    # --- the plan: what it flies --------------------------------------------------------------------------------
    for attr in ('CruiseKnots', 'FuelBurn', 'MaxCrosswind', 'LandingDistance'):
        logic.copy('FlightPlan', attr, 'Aircraft', attr)
    logic.formula('FlightPlan', 'Student', lambda lr: 1 if parent(lr, 'Pilot', 'Certificate') == 'S' else 0, ['PilotId', 'Pilot.Certificate'])

    # --- a leg ----------------------------------------------------------------------------------------------------
    def leg_circle(lr):
        a = [parent(lr, 'FromAirport', 'Latitude'), parent(lr, 'FromAirport', 'Longitude'),
             parent(lr, 'ToAirport', 'Latitude'), parent(lr, 'ToAirport', 'Longitude')]
        return None if None in a else great_circle(*[float(x) for x in a])
    where = ['FromAirportId', 'FromAirport.Latitude', 'FromAirport.Longitude', 'ToAirportId', 'ToAirport.Latitude', 'ToAirport.Longitude']
    logic.formula('Leg', 'Distance', lambda lr: None if leg_circle(lr) is None else leg_circle(lr)[0], where)
    logic.formula('Leg', 'TrueCourse', lambda lr: None if leg_circle(lr) is None else leg_circle(lr)[1], where)
    logic.formula('Leg', 'MagneticCourse', lambda lr: None if v(lr, 'TrueCourse') is None else int(math.fmod(n(lr, 'TrueCourse') + pn(lr, 'FromAirport', 'Variation') + 360, 360)),
                  ['TrueCourse', 'FromAirport.Variation'])

    def triangle(lr):
        return wind_triangle(n(lr, 'TrueCourse'), pn(lr, 'FlightPlan', 'CruiseKnots'), n(lr, 'WindDirection'), n(lr, 'WindSpeed'))
    wind = ['TrueCourse', 'WindDirection', 'WindSpeed', 'FlightPlanId', 'FlightPlan.CruiseKnots']
    logic.formula('Leg', 'WindCorrection', lambda lr: None if triangle(lr) is None else triangle(lr)[0], wind)
    logic.formula('Leg', 'GroundSpeed', lambda lr: None if triangle(lr) is None else triangle(lr)[1], wind)
    logic.formula('Leg', 'TrueHeading', lambda lr: int(math.fmod(n(lr, 'TrueCourse') + n(lr, 'WindCorrection') + 360, 360)), ['TrueCourse', 'WindCorrection'])
    logic.formula('Leg', 'MagneticHeading', lambda lr: int(math.fmod(n(lr, 'TrueHeading') + pn(lr, 'FromAirport', 'Variation') + 360, 360)),
                  ['TrueHeading', 'FromAirport.Variation'])
    logic.formula('Leg', 'Minutes', lambda lr: int(rounded(n(lr, 'Distance') / n(lr, 'GroundSpeed') * 60)) if n(lr, 'GroundSpeed') > 0 else None,
                  ['Distance', 'GroundSpeed'])
    logic.formula('Leg', 'Fuel', lambda lr: rounded(n(lr, 'Minutes') / 60.0 * pn(lr, 'FlightPlan', 'FuelBurn'), 1), ['Minutes', 'FlightPlanId', 'FlightPlan.FuelBurn'])
    logic.copy('Leg', 'ToAirspace', 'ToAirport', 'Airspace')
    logic.formula('Leg', 'LandingDistance', lambda lr: int(rounded(pn(lr, 'FlightPlan', 'LandingDistance') * distance_factor(parent(lr, 'Weather', 'DensityAltitude')))),
                  ['FlightPlanId', 'FlightPlan.LandingDistance', 'WeatherId', 'Weather.DensityAltitude'])

    def leg_crosswind(lr):
        if v(lr, 'WeatherId') is None or v(lr, 'RunwayId') is None:
            return None
        return crosswind(pn(lr, 'Weather', 'WindDirection'), pn(lr, 'Weather', 'WindSpeed'), pn(lr, 'Weather', 'Gust'), pn(lr, 'Runway', 'Heading'), pn(lr, 'Runway', 'Variation'))
    logic.formula('Leg', 'Crosswind', leg_crosswind,
                  ['WeatherId', 'Weather.WindDirection', 'Weather.WindSpeed', 'Weather.Gust', 'RunwayId', 'Runway.Heading', 'Runway.Variation'])

    def highest_ground(lr):
        return max(pn(lr, 'FromAirport', 'Elevation'), pn(lr, 'ToAirport', 'Elevation'))

    def problem(lr):
        ident = text(parent(lr, 'ToAirport', 'Ident'))
        if not vfr_altitude_ok(int(n(lr, 'Altitude')), n(lr, 'MagneticCourse'), highest_ground(lr)):
            return f'{int(n(lr, "Altitude"))} ft is not a VFR cruising altitude for a magnetic course of {int(n(lr, "MagneticCourse"))}'
        if pn(lr, 'ToAirport', 'ClosedNotams') > 0:
            return f'{ident} is closed (NOTAM)'
        if v(lr, 'RunwayId') is None:
            return f'No landing runway chosen at {ident}'
        if n(lr, 'LandingDistance') * 1.5 > pn(lr, 'Runway', 'Length'):
            return f'Landing needs {int(n(lr, "LandingDistance"))} ft x 1.5: runway {text(parent(lr, "Runway", "Ident"))} at {ident} is {int(pn(lr, "Runway", "Length"))} ft'
        if v(lr, 'WeatherId') is None:
            return f'No weather briefed for {ident}'
        if n(lr, 'Crosswind') > pn(lr, 'FlightPlan', 'MaxCrosswind'):
            return f'{int(n(lr, "Crosswind"))} kt crosswind on runway {text(parent(lr, "Runway", "Ident"))} at {ident}: the aircraft is demonstrated to {int(pn(lr, "FlightPlan", "MaxCrosswind"))}'
        ceiling = parent(lr, 'Weather', 'Ceiling')
        if not vfr_minimums_ok(text(v(lr, 'ToAirspace')), pn(lr, 'FlightPlan', 'Night') != 0, pn(lr, 'FlightPlan', 'Student') != 0,
                               pn(lr, 'Weather', 'Visibility'), None if ceiling is None else float(ceiling)):
            return f'Below VFR minimums at {ident}: {num(pn(lr, "Weather", "Visibility"))} SM' + ('' if ceiling is None else f', ceiling {int(float(ceiling))} ft')
        return None
    logic.formula('Leg', 'Problem', problem,
                  ['Altitude', 'MagneticCourse', 'FromAirport.Elevation', 'ToAirport.Elevation', 'ToAirportId', 'ToAirport.Ident', 'ToAirport.ClosedNotams',
                   'RunwayId', 'Runway.Length', 'Runway.Ident', 'LandingDistance', 'WeatherId', 'Crosswind', 'FlightPlan.MaxCrosswind', 'ToAirspace',
                   'FlightPlan.Night', 'FlightPlan.Student', 'Weather.Visibility', 'Weather.Ceiling'])
    logic.parent_check('Leg', 'FromAirport', 'There is no airport {FromAirportId} to leave from')
    logic.parent_check('Leg', 'ToAirport', 'There is no airport {ToAirportId} to fly to')
    logic.constraint('Leg', lambda lr: v(lr, 'FromAirportId') != v(lr, 'ToAirportId'), 'A leg goes somewhere: it starts and ends at the same airport')
    logic.constraint('Leg', lambda lr: n(lr, 'WindSpeed') < pn(lr, 'FlightPlan', 'CruiseKnots'), 'A {WindSpeed} kt wind: as fast as the aircraft')
    logic.constraint('Leg', lambda lr: n(lr, 'Altitude') >= highest_ground(lr) + 1000, '{Altitude} ft is less than 1,000 ft above the airports')
    logic.constraint('Leg', lambda lr: v(lr, 'RunwayId') is None or parent(lr, 'Runway', 'AirportId') == v(lr, 'ToAirportId'),
                     'Runway {RunwayId} is not at the destination')
    logic.constraint('Leg', lambda lr: v(lr, 'WeatherId') is None or parent(lr, 'Weather', 'AirportId') == v(lr, 'ToAirportId'),
                     'Weather {WeatherId} is not the destination\'s')

    # --- the load: weight and balance --------------------------------------------------------------------------
    logic.copy('LoadItem', 'Arm', 'AircraftStation', 'Arm')
    logic.copy('LoadItem', 'MaxWeight', 'AircraftStation', 'MaxWeight')
    logic.formula('LoadItem', 'Moment', lambda lr: rounded(n(lr, 'Weight') * n(lr, 'Arm'), 1), ['Weight', 'Arm'])
    logic.constraint('LoadItem', lambda lr: n(lr, 'Weight') <= n(lr, 'MaxWeight'), '{Description}: {Weight} lb, the station takes {MaxWeight}')
    logic.constraint('LoadItem', lambda lr: parent(lr, 'AircraftStation', 'AircraftId') == parent(lr, 'FlightPlan', 'AircraftId'),
                     '{Description}: that station is not in this plan\'s aircraft')
    logic.sum('FlightPlan', 'PersonsOnBoard', 'LoadItemList', 'Persons')
    logic.sum('FlightPlan', 'PayloadWeight', 'LoadItemList', 'Weight')
    logic.sum('FlightPlan', 'PayloadMoment', 'LoadItemList', 'Moment')
    logic.formula('FlightPlan', 'RampWeight', lambda lr: rounded(pn(lr, 'Aircraft', 'EmptyWeight') + n(lr, 'PayloadWeight') + n(lr, 'FuelOnBoard') * FUEL_LB, 1),
                  ['AircraftId', 'Aircraft.EmptyWeight', 'PayloadWeight', 'FuelOnBoard'])
    logic.formula('FlightPlan', 'TakeoffWeight', lambda lr: rounded(n(lr, 'RampWeight') - pn(lr, 'Aircraft', 'TaxiFuel') * FUEL_LB, 1),
                  ['RampWeight', 'Aircraft.TaxiFuel'])

    def cg(lr):
        if n(lr, 'TakeoffWeight') <= 0:
            return None
        fuel_moment = (n(lr, 'FuelOnBoard') - pn(lr, 'Aircraft', 'TaxiFuel')) * FUEL_LB * pn(lr, 'Aircraft', 'FuelArm')
        return rounded((pn(lr, 'Aircraft', 'EmptyMoment') + n(lr, 'PayloadMoment') + fuel_moment) / n(lr, 'TakeoffWeight'), 2)
    logic.formula('FlightPlan', 'CG', cg, ['TakeoffWeight', 'PayloadMoment', 'FuelOnBoard', 'Aircraft.TaxiFuel', 'Aircraft.FuelArm', 'Aircraft.EmptyMoment'])

    def forward_limit(lr):
        light, heavy = pn(lr, 'Aircraft', 'FwdLimitLight'), pn(lr, 'Aircraft', 'FwdLimitHeavy')
        brk, top, w = pn(lr, 'Aircraft', 'FwdBreakWeight'), pn(lr, 'Aircraft', 'MaxTakeoff'), n(lr, 'TakeoffWeight')
        if w <= brk or top <= brk:
            return light
        return rounded(light + (heavy - light) * (w - brk) / (top - brk), 2)
    logic.formula('FlightPlan', 'ForwardLimit', forward_limit,
                  ['TakeoffWeight', 'Aircraft.FwdLimitLight', 'Aircraft.FwdLimitHeavy', 'Aircraft.FwdBreakWeight', 'Aircraft.MaxTakeoff'])

    # --- the plan: legs, fuel, departure, times ------------------------------------------------------------------
    logic.count('FlightPlan', 'LegCount', 'LegList')
    logic.sum('FlightPlan', 'Distance', 'LegList', 'Distance')
    logic.sum('FlightPlan', 'Minutes', 'LegList', 'Minutes')
    logic.sum('FlightPlan', 'TripFuel', 'LegList', 'Fuel')
    logic.count('FlightPlan', 'LegProblems', 'LegList', lambda lr: v(lr, 'Problem') not in (None, ''))
    logic.count('FlightPlan', 'ClassBLegs', 'LegList', lambda lr: v(lr, 'ToAirspace') == 'B')
    logic.count('FlightPlan', 'XcEndorsements', 'EndorsementList', lambda lr: v(lr, 'Kind') == 'X')
    logic.formula('FlightPlan', 'LandingWeight', lambda lr: rounded(n(lr, 'TakeoffWeight') - (n(lr, 'TripFuel') + pn(lr, 'Aircraft', 'ClimbFuel')) * FUEL_LB, 1),
                  ['TakeoffWeight', 'TripFuel', 'Aircraft.ClimbFuel'])
    logic.formula('FlightPlan', 'ReserveFuel', lambda lr: rounded(n(lr, 'FuelBurn') * (45 if n(lr, 'Night') else 30) / 60.0, 1), ['FuelBurn', 'Night'])
    logic.formula('FlightPlan', 'FuelRequired',
                  lambda lr: rounded(pn(lr, 'Aircraft', 'TaxiFuel') + pn(lr, 'Aircraft', 'ClimbFuel') + n(lr, 'TripFuel') + n(lr, 'ReserveFuel'), 1),
                  ['Aircraft.TaxiFuel', 'Aircraft.ClimbFuel', 'TripFuel', 'ReserveFuel'])
    logic.formula('FlightPlan', 'FuelMargin', lambda lr: rounded(n(lr, 'FuelOnBoard') - n(lr, 'FuelRequired'), 1), ['FuelOnBoard', 'FuelRequired'])
    logic.formula('FlightPlan', 'Endurance', lambda lr: int(rounded(n(lr, 'FuelOnBoard') / n(lr, 'FuelBurn') * 60)) if n(lr, 'FuelBurn') > 0 else 0,
                  ['FuelOnBoard', 'FuelBurn'])
    logic.constraint('FlightPlan', lambda lr: n(lr, 'FuelOnBoard') <= pn(lr, 'Aircraft', 'UsableFuel'),
                     '{FuelOnBoard} gallons on board: the tanks hold less')
    logic.formula('FlightPlan', 'TakeoffDistance',
                  lambda lr: int(rounded(pn(lr, 'Aircraft', 'TakeoffDistance') * distance_factor(parent(lr, 'Weather', 'DensityAltitude'))
                                         * n(lr, 'TakeoffWeight') / pn(lr, 'Aircraft', 'MaxTakeoff'))) if pn(lr, 'Aircraft', 'MaxTakeoff') > 0 else None,
                  ['Aircraft.TakeoffDistance', 'Aircraft.MaxTakeoff', 'WeatherId', 'Weather.DensityAltitude', 'TakeoffWeight'])

    def departure_crosswind(lr):
        if v(lr, 'WeatherId') is None or v(lr, 'RunwayId') is None:
            return None
        return crosswind(pn(lr, 'Weather', 'WindDirection'), pn(lr, 'Weather', 'WindSpeed'), pn(lr, 'Weather', 'Gust'), pn(lr, 'Runway', 'Heading'), pn(lr, 'Runway', 'Variation'))
    logic.formula('FlightPlan', 'Crosswind', departure_crosswind,
                  ['WeatherId', 'Weather.WindDirection', 'Weather.WindSpeed', 'Weather.Gust', 'RunwayId', 'Runway.Heading', 'Runway.Variation'])
    logic.constraint('FlightPlan', lambda lr: v(lr, 'RunwayId') is None or v(lr, 'WeatherId') is None or parent(lr, 'Runway', 'AirportId') == parent(lr, 'Weather', 'AirportId'),
                     'The departure weather is not for the departure runway\'s airport')
    logic.formula('FlightPlan', 'ETA', lambda lr: clock_plus(v(lr, 'ActualDeparture') or v(lr, 'DepartureTime'), n(lr, 'Minutes')),
                  ['ActualDeparture', 'DepartureTime', 'Minutes'])
    logic.formula('FlightPlan', 'SearchAt', lambda lr: clock_plus(v(lr, 'ETA'), 30), ['ETA'])

    # --- go / no-go -----------------------------------------------------------------------------------------------
    def no_go(lr):
        day = text(v(lr, 'DepartureDate'))
        persons = n(lr, 'PersonsOnBoard')
        if n(lr, 'LegCount') == 0:
            return 'The plan has no legs'
        if persons < 1:
            return 'No one on board: put the pilot in the load'
        basicmed = text(parent(lr, 'Pilot', 'BasicMedUntil')) >= day and persons <= 6 and pn(lr, 'Aircraft', 'MaxTakeoff') <= 6000
        if text(parent(lr, 'Pilot', 'MedicalExpires')) < day and not basicmed:
            return 'The pilot\'s medical is not valid on ' + day
        if n(lr, 'Student'):
            if persons > 1:
                return 'A student pilot carries no passengers'
            if pn(lr, 'Pilot', 'SoloEndorsements') == 0:
                return 'No solo endorsement in the last 90 days'
            if n(lr, 'Distance') > 25 and n(lr, 'XcEndorsements') == 0:
                return 'No cross-country endorsement for this flight'
            if n(lr, 'ClassBLegs') > 0 and pn(lr, 'Pilot', 'ClassBEndorsements') == 0:
                return 'No endorsement for Class B airspace'
        elif text(parent(lr, 'Pilot', 'ReviewDue')) < day:
            return 'The pilot\'s flight review is due'
        if persons > 1 and pn(lr, 'Pilot', 'Landings90') < 3:
            return 'Not current to carry passengers: three landings in the last 90 days'
        if persons > 1 and n(lr, 'Night') and pn(lr, 'Pilot', 'NightLandings90') < 3:
            return 'Not night current to carry passengers: three full-stop night landings in the last 90 days'
        for attr, what in (('AnnualDue', 'annual inspection'), ('TransponderDue', 'transponder check'), ('EltDue', 'ELT inspection'), ('EltBatteryExpires', 'ELT battery')):
            if text(parent(lr, 'Aircraft', attr)) < day:
                return f'The aircraft\'s {what} is not current on {day}'
        if pn(lr, 'Aircraft', 'ForHire') and pn(lr, 'Aircraft', 'HoursSince100') + n(lr, 'Minutes') / 60.0 > 100:
            return 'The flight would run past the 100-hour inspection'
        if n(lr, 'TakeoffWeight') > pn(lr, 'Aircraft', 'MaxTakeoff'):
            return f'{num(n(lr, "TakeoffWeight"))} lb at takeoff: the maximum is {num(pn(lr, "Aircraft", "MaxTakeoff"))}'
        if n(lr, 'CG') < n(lr, 'ForwardLimit') or n(lr, 'CG') > pn(lr, 'Aircraft', 'AftLimit'):
            return f'The centre of gravity, {num(n(lr, "CG"))} in, is outside {num(n(lr, "ForwardLimit"))} to {num(pn(lr, "Aircraft", "AftLimit"))}'
        if v(lr, 'RunwayId') is None or v(lr, 'WeatherId') is None:
            return 'No departure runway or weather'
        if n(lr, 'TakeoffDistance') * 1.5 > pn(lr, 'Runway', 'Length'):
            return f'Takeoff needs {int(n(lr, "TakeoffDistance"))} ft x 1.5: the runway is {int(pn(lr, "Runway", "Length"))} ft'
        if n(lr, 'Crosswind') > n(lr, 'MaxCrosswind'):
            return f'{int(n(lr, "Crosswind"))} kt crosswind on departure: the aircraft is demonstrated to {int(n(lr, "MaxCrosswind"))}'
        ceiling = parent(lr, 'Weather', 'Ceiling')
        if not vfr_minimums_ok(text(parent(lr, 'Runway', 'Airspace')), n(lr, 'Night') != 0, n(lr, 'Student') != 0,
                               pn(lr, 'Weather', 'Visibility'), None if ceiling is None else float(ceiling)):
            return 'Below VFR minimums for departure'
        if n(lr, 'LegProblems') > 0:
            return f'{int(n(lr, "LegProblems"))} leg(s) with a problem: see the legs'
        if n(lr, 'FuelMargin') < 0:
            return f'Not enough fuel: {num(n(lr, "FuelRequired"))} gallons needed with the reserve, {num(n(lr, "FuelOnBoard"))} on board'
        return None
    logic.formula('FlightPlan', 'NoGoReason', no_go,
                  ['LegCount', 'DepartureDate', 'PersonsOnBoard', 'PilotId', 'Pilot.MedicalExpires', 'Pilot.BasicMedUntil', 'Student',
                   'Pilot.SoloEndorsements', 'Distance', 'XcEndorsements', 'ClassBLegs', 'Pilot.ClassBEndorsements', 'Pilot.ReviewDue',
                   'Pilot.Landings90', 'Night', 'Pilot.NightLandings90', 'AircraftId', 'Aircraft.AnnualDue', 'Aircraft.TransponderDue',
                   'Aircraft.EltDue', 'Aircraft.EltBatteryExpires', 'Aircraft.ForHire', 'Aircraft.HoursSince100', 'Minutes', 'TakeoffWeight',
                   'Aircraft.MaxTakeoff', 'CG', 'ForwardLimit', 'Aircraft.AftLimit', 'RunwayId', 'WeatherId', 'TakeoffDistance', 'Runway.Length',
                   'Crosswind', 'MaxCrosswind', 'Runway.Airspace', 'Weather.Visibility', 'Weather.Ceiling', 'LegProblems', 'FuelMargin',
                   'FuelRequired', 'FuelOnBoard'])
    logic.formula('FlightPlan', 'GoNoGo', lambda lr: 'GO' if v(lr, 'NoGoReason') in (None, '') else 'NO-GO', ['NoGoReason'])
    logic.constraint('FlightPlan', lambda lr: v(lr, 'Status') != 'F' or v(lr, 'GoNoGo') == 'GO', 'Not filed - NO-GO: {NoGoReason}')

    def next_status(lr):
        old = None if lr['verb'] == 'insert' else (lr['old'] or {}).get('Status')
        return text(v(lr, 'Status')) in NEXT_STATUS.get(old, '') or v(lr, 'Status') == old
    logic.constraint('FlightPlan', next_status, 'A plan goes Draft - Filed - Active - Closed: it cannot go to {Status} from here')
    logic.constraint('FlightPlan', lambda lr: v(lr, 'Status') not in ('A', 'C') or v(lr, 'ActualDeparture') not in (None, ''),
                     'An active plan needs its actual departure time')
    logic.count('FlightPlan', 'ReportCount', 'PositionReportList')
    # refuse first (a flown flight's track), then cascade
    logic.delete_action('FlightPlan', 'PositionReportList', 'prevent', 'The flight was flown: its track is on file')
    logic.delete_action('FlightPlan', 'LegList', 'cascade')
    logic.delete_action('FlightPlan', 'LoadItemList', 'cascade')
    logic.delete_action('FlightPlan', 'EndorsementList', 'cascade')     # a cross-country endorsement is for that flight

    # --- position reports -------------------------------------------------------------------------------------------
    logic.constraint('PositionReport', lambda lr: -90 <= n(lr, 'Latitude') <= 90 and -180 <= n(lr, 'Longitude') <= 180,
                     'There is no position {Latitude}, {Longitude}')
