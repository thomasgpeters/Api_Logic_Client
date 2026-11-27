# VFR flight planning research (2026-11-26)

Research for elaborating `samples/FlightPlanner`, the author's request. ecfr.gov and faa.gov could not be
fetched from the research session; search confirmed the overdue and expiry times, BasicMed intervals and the
90-day solo endorsement. The rest is standard FAR / AIM / PHAK material: check the wording against the
sources before quoting it.

## The flight plan

FAA Form 7233-4 (ICAO format) is the standard now (the domestic 7233-1 is being retired). Items: 7 aircraft
ID; 8 rules V, type G; 9 type and wake category; 10 equipment; 13 departure and time (UTC); 15 cruise speed
(N0110), level (VFR / A055), route; 16 destination, total EET, alternates; 18 other (DOF/, REG/, RMK/);
19 endurance (E/0430), persons on board, survival equipment, colours, pilot.

Life cycle: Proposed -> Active (the pilot opens it) -> Closed (the pilot closes it; a tower does not).
A proposed plan not activated drops out (AIM 1 hour; Leidos 2 hours). Overdue at ETA + 30 minutes
(QALQ, then INREQ), ALNOT about 1 hour later, then the Rescue Coordination Center.

## Go / no-go (14 CFR)

- 91.103 preflight action; 91.151 fuel: 30 minutes by day, 45 at night (done).
- 91.159 cruising altitudes above 3,000 AGL by magnetic course (done).
- 61.57 currency: 3 takeoffs and landings in 90 days to carry passengers; at night, 3 to a full stop at night.
  **Applies to carrying passengers** - the sample's night-currency rule applies to any night flight: tighten it.
- 61.56 flight review within 24 calendar months.
- 61.23 medical (private privileges): 60 calendar months under 40 at the exam, 24 at 40 and over; or BasicMed
  (CMEC every 48 months, course every 24; at most 6 aboard, 6,000 lb, 18,000 ft, 250 kt).
- 91.409 annual within 12 calendar months (done); 100-hour only for hire or instruction (10 hours' grace).
- 91.413 transponder 24 months; 91.207 ELT inspection 12 months, battery date; 91.411 pitot-static (IFR only).
- 91.155 VFR weather minimums by airspace class (Class B 3 SM clear of clouds; C/D/E below 10,000:
  3 SM, 500 below / 1,000 above / 2,000 horizontal; surface areas: ceiling 1,000, visibility 3 SM).
- Students (61.87, 61.89, 61.93): no passengers; 3 SM by day, 5 at night; solo endorsement 90 days; each
  solo cross-country endorsed; Class B needs its own endorsement.
- Airspace: Class B a clearance, C and D two-way radio; NOTAMs and TFRs on the route.

## Calculations

- Wind triangle (wind from WD at WS, true): WCA = asin(WS sin(WD - TC) / TAS); TH = TC + WCA;
  GS = TAS cos(WCA) - WS cos(WD - TC). MH = TH + W variation; compass heading = MH + deviation.
- Fuel: taxi (about 1.1 gal in a C172) + climb + cruise + reserve; endurance = fuel / burn.
- Density altitude: PA = elevation + (29.92 - altimeter) x 1000; DA = PA + 120 (OAT - (15 - 2 PA/1000)).
- Takeoff and landing distance from the POH by DA and weight, x 1.5 against the runway; crosswind =
  WS |sin(wind - runway)| against the maximum demonstrated (C172: 15 kt).
- Weight and balance: moment = weight x arm; CG = moments / weight; 100LL 6 lb/gal; FAA standard 170 lb a
  person; C172S max takeoff 2,550 lb; landing weight = takeoff - fuel burned; a sloped forward CG limit.

## Candidate additions to the sample

Tables: Runway (heading, length, surface), Waypoint, WeatherObs (METAR: wind, visibility, ceiling,
temperature, altimeter), LogbookEntry (landings, night full-stop landings), Endorsement, AircraftStation and
LoadItem (weight and balance), Notam / TFR.

Rules: the wind triangle per leg (wind direction and speed instead of a headwind); taxi fuel; endurance;
passenger and night currency from logbook entries in the last 90 days; the flight review; medical expiry
from exam date and age, or BasicMed; transponder and ELT dates; weight and balance (ramp, takeoff, landing
weight, CG within limits, station limits); density altitude and takeoff distance x 1.5 against the runway;
crosswind against the maximum; weather minimums at the destination (students tighter); student
endorsements; active NOTAMs / TFRs; the life cycle (Proposed, Active, Closed; ETA; overdue at ETA + 30).

## Sources

- AIM 5-1: https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap5_section_1.html
- JO 7110.10, overdue aircraft: https://www.faa.gov/air_traffic/publications/atpubs/fs_html/chap3_section_4.html
- FAA blog, flight plans: https://www.faa.gov/blog/clearedfortakeoff/weather-plan-you-never-write-down-understanding-flight-plans-flight
- https://www.flyingmag.com/forgetting-to-close/
- AOPA, flight plan technique: https://aopa.org/news-and-media/all-news/2017/july/flight-training-magazine/technique-flight-plan
- 14 CFR: https://www.ecfr.gov/current/title-14
- 61.93: https://www.law.cornell.edu/cfr/text/14/61.93 ; 61.87: https://www.law.cornell.edu/cfr/text/14/61.87
- BasicMed: https://www.aopa.org/advocacy/pilots/medical/basicmed/basicmed-overview-faqs ; AC 68-1: https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_68-1.pdf
- PHAK: https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak
