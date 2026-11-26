# Flight Planner sample: VFR flights in New England

Flight planning for amateur (private) pilots, a sample model for App Builder for FutureBasic. It shows
LogicBank for FutureBasic doing real arithmetic and real regulation:
- great-circle navigation and the wind triangle;
- weight and balance;
- takeoff and landing distances at the day's density altitude;
- crosswind and weather minimums;
- a **go / no-go** decision drawn from the checks a pilot makes before every flight (14 CFR 61 and 91).

The research behind it, with sources, is in `docs/research/Flight Planning Research.md`.

The airports are real, with approximate positions. The aircraft figures are typical for each type. The
pilots, tail numbers, weather and NOTAMs are made up. **Not for navigation.**

## User stories

- **As a pilot**, I plan a flight leg by leg between airports. For each leg I see:
  - distance, true and magnetic course;
  - the wind correction, heading and ground speed in the winds aloft;
  - minutes and fuel, for the aircraft I fly.
- **As a pilot**, I load the aircraft: myself, passengers, bags. I see the weight and the centre of gravity
  against the aircraft's envelope, at takeoff and at landing.
- **As a pilot**, I choose the departure and landing runways and brief the weather. The plan works out:
  - the takeoff and landing distances at the density altitude, with a 1.5 margin;
  - the crosswind against what the aircraft is demonstrated to;
  - the VFR minimums. They are tighter for a student.
- **As a pilot**, the plan tells me **GO** or **NO-GO**, and why. I can file only on a GO, and a filed plan
  cannot be changed into a NO-GO.
- **As a pilot**, my medical (or BasicMed), my flight review and my currency come from my records and my
  logbook. Night currency counts only when I carry passengers.
- **As a student pilot**, my instructor's endorsements decide where I may go solo.
- **As an owner or a club**, the aircraft's inspections ground it when they lapse: annual, transponder, ELT
  and its battery. A rental's 100-hour inspection does too.
- **As a pilot**, the plan goes Draft, Filed, Active (with my actual departure), Closed. It tells me my ETA
  and when search and rescue would begin. A closed flight goes into my logbook and the aircraft's.
- **As a pilot**, a flight I have flown replays on a map from its position reports, with other traffic
  around it (`docs/design/Map View Design.md`).
- **Enterprise:** the plan is filed with Flight Service through a simulated interface in the API Logic
  Server project (`docs/design/Flight Service Filing Design.md`).

## The model

```
AircraftType ─< Aircraft ─< AircraftStation ─< LoadItem >─┐
                   │                                       │
Pilot ─< LogbookEntry          Pilot, Aircraft ─< FlightPlan >── Runway, Weather (departure)
  └──< Endorsement >── FlightPlan                   ├─< Leg >── FromAirport, ToAirport, Runway, Weather (landing)
Airport ─< Runway, Notam, Weather                   └─< PositionReport (and other traffic, no plan)
```

## The rules (104, every one tested)

**Airports and weather.**
- A runway copies its airport's variation and airspace.
- `Airport.ClosedNotams` counts the active NOTAMs that close it: closures and TFRs.
- A weather observation works out its density altitude, from elevation, altimeter and temperature.
- It also works out its flight category: VFR, MVFR, IFR or LIFR.

**The aircraft.**
- An aircraft copies its type's performance.
- Its weight and balance data is its own: empty weight and arm, maximum weight, fuel arm, CG limits.
- Inspections fall due at the end of the month:
  - annual: 12 calendar months;
  - transponder: 24;
  - ELT: 12. The ELT battery has its own expiry date.
- `HoursSince100` adds the closed flights' hours.

**The pilot.**
- The medical expires 60 calendar months after the exam when the pilot was under 40 at the exam, else 24.
- BasicMed runs to the earlier of the course + 24 months and the exam + 48 months.
- The flight review is due 24 months after the last one.
- `Landings90` and `NightLandings90` sum the logbook entries in the 90 days to the pilot's `AsOf` date
  (today in the app).
- A student's solo and Class B endorsements count for 90 days. A cross-country endorsement belongs to one
  flight.

**A leg.**
- Distance and initial true course by the great circle. Magnetic course = true course + the departure
  airport's variation.
- The wind triangle: wind correction angle, true and magnetic heading, ground speed.
- Minutes and fuel.
- The landing distance at the destination's density altitude.
- The crosswind on the landing runway, using the gust if there is one.
- `Problem` is the first of these that applies:
  - a cruising altitude 91.159 does not allow;
  - the airport closed by a NOTAM;
  - no runway chosen, or a runway shorter than the landing distance × 1.5;
  - no weather briefed;
  - too much crosswind;
  - below the VFR minimums.
- A leg must go somewhere, in a wind slower than the aircraft, at least 1,000 ft above both airports. Its
  runway and weather must be the destination's.

**The load.**
- Each item's moment comes from its station's arm. An item may not weigh more than its station's limit, and
  the station must be in the plan's aircraft.
- Persons on board, payload weight and moment add up.
- Ramp weight = empty weight + payload + fuel at 6 lb a gallon. Takeoff weight = ramp weight − taxi fuel.
- Landing weight = takeoff weight − climb and trip fuel.
- The CG at takeoff is checked against the forward limit, which slopes with weight, and the aft limit.

**The plan.**
- Legs, distance, minutes and trip fuel add up.
- Reserve: 30 minutes by day, 45 at night.
- Fuel required = taxi + climb + trip + reserve. Margin = fuel on board − fuel required. Endurance is the
  fuel on board in minutes.
- The takeoff distance scales with density altitude and weight. The departure crosswind is checked too.
- ETA = departure + en-route time. `SearchAt` = ETA + 30, when search and rescue would begin.

**Go / no-go.** `NoGoReason` is the first of these that applies:
1. No legs, or no one on board.
2. The medical, or BasicMed within its limits.
3. For a student: no passengers, the solo endorsement, the cross-country endorsement, the Class B
   endorsement. For anyone else: the flight review.
4. Carrying passengers: three landings in 90 days. At night: three full-stop night landings.
5. The aircraft's annual, transponder, ELT inspection and ELT battery, and the 100-hour if for hire.
6. Weight, then CG.
7. Departure: runway and weather, takeoff distance, crosswind, minimums.
8. A leg with a problem.
9. Fuel.

The plan goes Draft → Filed (only on a GO) → Active (with the actual departure) → Closed. Deleting:
- a flown plan with a track is refused;
- a draft takes its legs, load and cross-country endorsement with it;
- pilots, aircraft and types in use are kept.

## The demo scenario (`sample.sql`)

| Plan | Who, what | Result |
|---|---|---|
| 1, 2 | Maria, N172MS: Bedford, Hyannis, Nantucket, home after dark, with a passenger | filed, GO |
| 3 | Dev, N22SR, at night to Lebanon with a friend | NO-GO: no night landings since July |
| 4 | Hannah, N28AR, to the Vineyard on 3 December | NO-GO: her medical runs out on the 30th |
| 5 | Tom (student, endorsed), the Cub to Lebanon, 9 gallons | NO-GO: needs 11.3 |
| 6 | Dev, the SR22 to Plum Island | NO-GO: 2,105 ft of turf |
| 7 | Maria, Bedford to Portsmouth and back | flown: 11 position reports, other traffic |
| 8 | Hannah to Westfield at 5,500 westbound | NO-GO: the altitude; then the air-show NOTAM |
| 9 | Dev, N172TB | NO-GO: the annual ran out on 31 October |
| 10 | Maria to the Vineyard, runway 24 in a north-westerly | NO-GO: 19 kt crosswind (runway 33 is fine) |
| 11 | Maria to Nantucket in fog | NO-GO: 1 SM, 300 ft |
| 12 | Ray (BasicMed), the club's Archer to Hyannis | Active: in the air now |

## Files

- `schema.sql`: the tables.
- `lookup.sql`: airports, runways, NOTAMs and aircraft types. They stay when the sample data is purged.
- `sample.sql`: the demo scenario. `purge_sample.sql` removes it.
- `build_db.py`: builds `flightplanner.sqlite`, every row through the rules. Plans move Draft, Filed,
  Active, Closed one step at a time. `--lookup-only` leaves the scenario out.
- `flight_rules.py`: the rules (the reference).
- `test_rules.py`: 104 scenarios. `--prove` leaves each rule out in turn; a scenario must then fail.
- `Rules.incl`: the same rules in FB, for the generated app's `Rules.incl`.

```bash
python3 samples/FlightPlanner/build_db.py
python3 samples/FlightPlanner/test_rules.py --prove
```
