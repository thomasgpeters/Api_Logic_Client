"""The Flight Planner sample's business rules - the reference, run here by tools/logic_reference.py's engine
(the same engine, function for function, as LogicBank for FutureBasic in a generated app).

    a leg       its distance and initial true course from the airports' coordinates (great circle), the
                magnetic course (+ the departure airport's variation), ground speed (the aircraft's cruise
                less the headwind), minutes and fuel; whether its cruising altitude keeps the VFR
                hemispheric rule (14 CFR 91.159) and whether the destination's runway is long enough
    the plan    adds its legs up; the reserve is 30 minutes of fuel by day, 45 at night (14 CFR 91.151);
                the margin is what is on board less trip and reserve
    go / no-go  the first reason the flight may not go - no legs, the pilot's medical, night currency
                (three night landings in the last 90 days, 14 CFR 61.57), the annual inspection, an
                altitude, a runway, the fuel - and a plan is filed only when it is a GO
    the logbook a closed (flown) plan adds its minutes to the pilot and the aircraft

Rounding is floor(x + 0.5) at a fixed number of places, the same in FB (samples/FlightPlanner/Rules.incl).
"""
import math
from datetime import date

EARTH_NM = 3440.065          # the earth's mean radius in nautical miles
NIGHT_CURRENCY_DAYS = 90


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


def vfr_altitude_ok(altitude, magnetic_course, highest_ground):
    """14 CFR 91.159: more than 3,000 ft above the surface, magnetic course 0-179 cruises at odd thousands
    + 500, 180-359 at even thousands + 500"""
    if altitude - highest_ground <= 3000:
        return True
    if (altitude - 500) % 1000 != 0:
        return False
    odd = ((altitude - 500) // 1000) % 2 == 1
    return odd == (magnetic_course < 180)


def days_between(first, last):
    try:
        return (date.fromisoformat(str(last)[:10]) - date.fromisoformat(str(first)[:10])).days
    except (TypeError, ValueError):
        return None


def declare(logic):
    from logic_reference import Logic
    n, v = Logic.number, Logic.value

    def parent(lr, role, attr):
        return logic.parent_value(lr, role, attr)

    def text(x):
        return '' if x is None else str(x)

    # --- aircraft: this airframe's figures, from its type ---------------------------------------------
    for attr in ('CruiseKnots', 'FuelBurn', 'UsableFuel', 'MinRunway'):
        logic.copy('Aircraft', attr, 'AircraftType', attr)
    logic.delete_action('AircraftType', 'AircraftList', 'prevent', '{Model}: aircraft of this type are on file')

    # --- the plan: what it flies ------------------------------------------------------------------------
    for attr in ('CruiseKnots', 'FuelBurn', 'UsableFuel', 'MinRunway'):
        logic.copy('FlightPlan', attr, 'Aircraft', attr)

    # --- a leg ----------------------------------------------------------------------------------------------
    def leg_circle(lr):
        a = [parent(lr, 'FromAirport', 'Latitude'), parent(lr, 'FromAirport', 'Longitude'),
             parent(lr, 'ToAirport', 'Latitude'), parent(lr, 'ToAirport', 'Longitude')]
        return None if None in a else great_circle(*[float(x) for x in a])
    where = ['FromAirportId', 'FromAirport.Latitude', 'FromAirport.Longitude', 'ToAirportId', 'ToAirport.Latitude', 'ToAirport.Longitude']
    logic.formula('Leg', 'Distance', lambda lr: None if leg_circle(lr) is None else leg_circle(lr)[0], where)
    logic.formula('Leg', 'TrueCourse', lambda lr: None if leg_circle(lr) is None else leg_circle(lr)[1], where)
    logic.formula('Leg', 'MagneticCourse',
                  lambda lr: None if v(lr, 'TrueCourse') is None else int(math.fmod(n(lr, 'TrueCourse') + float(parent(lr, 'FromAirport', 'Variation') or 0) + 360, 360)),
                  ['TrueCourse', 'FromAirport.Variation'])
    logic.formula('Leg', 'GroundSpeed', lambda lr: int(float(parent(lr, 'FlightPlan', 'CruiseKnots') or 0) - n(lr, 'Headwind')),
                  ['Headwind', 'FlightPlanId', 'FlightPlan.CruiseKnots'])
    logic.formula('Leg', 'Minutes', lambda lr: int(rounded(n(lr, 'Distance') / n(lr, 'GroundSpeed') * 60)) if n(lr, 'GroundSpeed') > 0 else None,
                  ['Distance', 'GroundSpeed'])
    logic.formula('Leg', 'Fuel', lambda lr: rounded(n(lr, 'Minutes') / 60.0 * float(parent(lr, 'FlightPlan', 'FuelBurn') or 0), 1),
                  ['Minutes', 'FlightPlanId', 'FlightPlan.FuelBurn'])

    def highest_ground(lr):
        return max(float(parent(lr, 'FromAirport', 'Elevation') or 0), float(parent(lr, 'ToAirport', 'Elevation') or 0))
    logic.formula('Leg', 'AltitudeOK', lambda lr: 1 if vfr_altitude_ok(int(n(lr, 'Altitude')), n(lr, 'MagneticCourse'), highest_ground(lr)) else 0,
                  ['Altitude', 'MagneticCourse', 'FromAirport.Elevation', 'ToAirport.Elevation'])
    logic.formula('Leg', 'RunwayOK',
                  lambda lr: 1 if float(parent(lr, 'ToAirport', 'RunwayLength') or 0) >= float(parent(lr, 'FlightPlan', 'MinRunway') or 0) else 0,
                  ['ToAirportId', 'ToAirport.RunwayLength', 'FlightPlanId', 'FlightPlan.MinRunway'])
    logic.parent_check('Leg', 'FromAirport', 'There is no airport {FromAirportId} to leave from')
    logic.parent_check('Leg', 'ToAirport', 'There is no airport {ToAirportId} to fly to')
    logic.constraint('Leg', lambda lr: v(lr, 'FromAirportId') != v(lr, 'ToAirportId'), 'A leg goes somewhere: it starts and ends at the same airport')
    logic.constraint('Leg', lambda lr: n(lr, 'GroundSpeed') > 0, 'A headwind of {Headwind} knots: the aircraft would not move')
    logic.constraint('Leg', lambda lr: n(lr, 'Altitude') >= highest_ground(lr) + 1000,
                     '{Altitude} ft is less than 1,000 ft above the airports')

    # --- the plan: its legs added up -----------------------------------------------------------------------
    logic.count('FlightPlan', 'LegCount', 'LegList')
    logic.sum('FlightPlan', 'Distance', 'LegList', 'Distance')
    logic.sum('FlightPlan', 'Minutes', 'LegList', 'Minutes')
    logic.sum('FlightPlan', 'TripFuel', 'LegList', 'Fuel')
    logic.count('FlightPlan', 'BadAltitudeLegs', 'LegList', lambda lr: n(lr, 'AltitudeOK') == 0)
    logic.count('FlightPlan', 'ShortRunwayLegs', 'LegList', lambda lr: n(lr, 'RunwayOK') == 0)
    logic.formula('FlightPlan', 'ReserveFuel', lambda lr: rounded(n(lr, 'FuelBurn') * (45 if n(lr, 'Night') else 30) / 60.0, 1), ['FuelBurn', 'Night'])
    logic.formula('FlightPlan', 'FuelRequired', lambda lr: rounded(n(lr, 'TripFuel') + n(lr, 'ReserveFuel'), 1), ['TripFuel', 'ReserveFuel'])
    logic.formula('FlightPlan', 'FuelMargin', lambda lr: rounded(n(lr, 'FuelOnBoard') - n(lr, 'FuelRequired'), 1), ['FuelOnBoard', 'FuelRequired'])
    logic.constraint('FlightPlan', lambda lr: n(lr, 'FuelOnBoard') <= n(lr, 'UsableFuel'),
                     '{FuelOnBoard} gallons on board: the tanks hold {UsableFuel}')

    # --- go / no-go -------------------------------------------------------------------------------------------
    def no_go(lr):
        day = text(v(lr, 'DepartureDate'))
        if n(lr, 'LegCount') == 0:
            return 'The plan has no legs'
        if text(parent(lr, 'Pilot', 'MedicalExpires')) < day:
            return 'The pilot\'s medical certificate is not valid on ' + day
        if n(lr, 'Night'):
            since = days_between(parent(lr, 'Pilot', 'LastNightLandings'), day)
            if since is None or since < 0 or since > NIGHT_CURRENCY_DAYS:
                return 'The pilot is not night current: three night landings in the last 90 days'
        if text(parent(lr, 'Aircraft', 'AnnualDue')) < day:
            return 'The aircraft\'s annual inspection is not current on ' + day
        if n(lr, 'BadAltitudeLegs') > 0:
            return f'{int(n(lr, "BadAltitudeLegs"))} leg(s) at a cruising altitude the VFR rule does not allow'
        if n(lr, 'ShortRunwayLegs') > 0:
            return f'{int(n(lr, "ShortRunwayLegs"))} leg(s) end at a runway shorter than the aircraft needs'
        if n(lr, 'FuelMargin') < 0:
            return f'Not enough fuel: {n(lr, "FuelRequired"):g} gallons needed with the reserve, {n(lr, "FuelOnBoard"):g} on board'
        return None
    logic.formula('FlightPlan', 'NoGoReason', no_go,
                  ['LegCount', 'DepartureDate', 'PilotId', 'Pilot.MedicalExpires', 'Night', 'Pilot.LastNightLandings',
                   'AircraftId', 'Aircraft.AnnualDue', 'BadAltitudeLegs', 'ShortRunwayLegs', 'FuelMargin', 'FuelRequired', 'FuelOnBoard'])
    logic.formula('FlightPlan', 'GoNoGo', lambda lr: 'GO' if v(lr, 'NoGoReason') in (None, '') else 'NO-GO', ['NoGoReason'])
    logic.constraint('FlightPlan', lambda lr: v(lr, 'Status') != 'F' or v(lr, 'GoNoGo') == 'GO',
                     'Not filed - NO-GO: {NoGoReason}')
    logic.count('FlightPlan', 'ReportCount', 'PositionReportList')
    # refuse first (a flown flight's track), then cascade (the legs)
    logic.delete_action('FlightPlan', 'PositionReportList', 'prevent', 'The flight was flown: its track is on file')
    logic.delete_action('FlightPlan', 'LegList', 'cascade')

    # --- the logbook ----------------------------------------------------------------------------------------
    flown = lambda lr: v(lr, 'Status') == 'C'
    logic.count('Pilot', 'FlightCount', 'FlightPlanList', flown)
    logic.sum('Pilot', 'FlownMinutes', 'FlightPlanList', 'Minutes', flown)
    logic.sum('Aircraft', 'FlownMinutes', 'FlightPlanList', 'Minutes', flown)
    logic.delete_action('Pilot', 'FlightPlanList', 'prevent', '{Name} has flight plans')
    logic.delete_action('Aircraft', 'FlightPlanList', 'prevent', '{TailNumber} has flight plans')

    # --- position reports -------------------------------------------------------------------------------------
    logic.constraint('PositionReport', lambda lr: -90 <= n(lr, 'Latitude') <= 90 and -180 <= n(lr, 'Longitude') <= 180,
                     'There is no position {Latitude}, {Longitude}')
