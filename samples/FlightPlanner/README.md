# Flight Planner sample: VFR flights in New England

Flight planning for amateur (private) pilots - a sample model for App Builder for FutureBasic, built to show
LogicBank for FutureBasic doing real arithmetic: great-circle navigation, wind, time and fuel, and a
**go / no-go** decision drawn from the regulations a pilot checks before every flight. The airports are real
(Bedford, Nantucket, Martha's Vineyard, Lebanon, Plum Island ...), their positions approximate; the aircraft
figures are typical for each type; the pilots and tail numbers are made up. **Not for navigation.**

## User stories

- **As a pilot**, I plan a flight leg by leg between airports; each leg shows its distance, true and magnetic
  course, ground speed in the forecast wind, minutes and fuel - for the aircraft I fly.
- **As a pilot**, I see the fuel the flight needs with the legal reserve (30 minutes by day, 45 at night) and
  my margin with what is on board; I cannot put more in than the tanks hold.
- **As a pilot**, the plan tells me **GO** or **NO-GO**, and why: my medical, my night currency, the aircraft's
  annual inspection, a cruising altitude the VFR rule does not allow, a runway too short, not enough fuel.
- **As a pilot**, I can file a plan only when it is a GO - and a filed plan cannot be changed into a NO-GO.
- **As a pilot**, when I renew my medical, fly my night landings, or the annual is signed off, my plans turn GO.
- **As a pilot**, when I switch aircraft, every leg's speed, time, fuel and runway check follow.
- **As a pilot**, a flight I have flown goes into my logbook and the aircraft's; its track (position reports)
  replays on a map with other traffic around it (the Map View, `docs/design/Map View Design.md`).

## The model

```
AircraftType ─< Aircraft ─< FlightPlan >── Pilot
                   │            ├─< Leg >── FromAirport, ToAirport (Airport)
                   └── HomeAirport          └─< PositionReport (and other traffic, no plan)
```

## The rules (44, every one tested)

**Aircraft.** An aircraft copies its type's cruise speed, fuel burn, usable fuel and minimum runway (this
airframe's own figures); a plan copies them from its aircraft - again when it changes aircraft.

**A leg.** `Distance` (NM) and `TrueCourse` by the great circle between the airports' coordinates (haversine,
initial bearing); `MagneticCourse` = true + the departure airport's variation (west positive); `GroundSpeed` =
cruise - headwind; `Minutes`, `Fuel`. `AltitudeOK`: more than 3,000 ft above the ground, magnetic course 0-179
cruises at odd thousands + 500, 180-359 at even thousands + 500 (14 CFR 91.159). `RunwayOK`: the destination's
longest runway is at least the aircraft's minimum. A leg must go somewhere, move (no headwind stronger than the
cruise), cruise at least 1,000 ft above both airports, and use airports that exist.

**The plan.** Legs, distance, minutes and trip fuel add up; `ReserveFuel` is 30 minutes of burn by day, 45 at
night (14 CFR 91.151); `FuelRequired` = trip + reserve; `FuelMargin` = on board - required. Fuel on board may not
exceed the usable fuel.

**Go / no-go.** `NoGoReason` is the first that applies - no legs; the pilot's medical not valid on the day;
at night, no three night landings in the last 90 days (14 CFR 61.57); the annual inspection not current; a leg at
a wrong altitude; a runway too short; not enough fuel - and `GoNoGo` is GO only without one. Status F (filed)
needs a GO.

**The logbook.** Closed (flown) plans add their minutes to the pilot (`FlownMinutes`, `FlightCount`) and the
aircraft. A flown plan with a track cannot be deleted (a draft takes its legs with it); nor a pilot or aircraft
with plans, nor a type with aircraft. Position reports must be on the globe.

## The demo scenario (`sample.sql`)

| Plan | Who, what | Result |
|---|---|---|
| 1, 2 | Maria, N172MS: Bedford - Hyannis - Nantucket, home after dark | filed, GO |
| 3 | Dev, N22SR, at night to Lebanon | NO-GO: last night landings in July |
| 4 | Hannah, N28AR, to the Vineyard on 3 December | NO-GO: her medical runs out on the 30th |
| 5 | Tom, the Cub into the wind to Lebanon, 9 gallons | NO-GO: needs 11.2 with the reserve |
| 6 | Dev, the SR22 to Plum Island | NO-GO: 2,105 ft of runway |
| 7 | Maria, Bedford - Portsmouth and back | flown: 11 position reports, other traffic |
| 8 | Hannah, westbound at 5,500 | NO-GO: an eastbound altitude |
| 9 | Dev, N172TB | NO-GO: the annual ran out on 20 November |

## Files

- `schema.sql` - the tables; `lookup.sql` - airports and aircraft types (they stay); `sample.sql` - the demo
  scenario; `purge_sample.sql` - removes it.
- `build_db.py` - builds `flightplanner.sqlite`, every row through the rules (`--lookup-only` for none of the
  scenario).
- `flight_rules.py` - the rules (the reference); `test_rules.py` - 45 scenarios, and `--prove`: each rule left
  out in turn must fail one.
- `Rules.incl` - the same rules in FB, for the generated app's `Rules.incl`.

```bash
python3 samples/FlightPlanner/build_db.py
python3 samples/FlightPlanner/test_rules.py --prove
```
