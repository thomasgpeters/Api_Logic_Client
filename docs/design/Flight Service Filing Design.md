# Flight Service filing - a simulated interface (Enterprise edition, in API Logic Server)

The author (2026-11-26): the Flight Planner sample registers its flight plans with the FAA "however that
process works" - researched, stubbed, **Enterprise only**, the interface inside the ALS project. Status:
design; the stub is not built yet (BACKLOG).

## How filing works today (research, 2026-11-26)

Direct fetches of the Leidos vendor docs (lmfswebservices.atlassian.net) and faa.gov were blocked from the
research session: this comes from search summaries of those pages and ICAO Doc 4444 practice.

- **Leidos Flight Service** (the FAA's contractor: lower 48, Hawaii, Puerto Rico) takes VFR and IFR plans by
  1800wxbrief.com, phone, and **vendor web services**; IFR plans go on to ATC (ERAM), VFR plans stay with
  Flight Service for search and rescue. DUATS is gone.
- **Leidos Flight Service Web Services** (SOAP or REST; documented publicly, access only for reviewed,
  finished products; onboarding through Leidos, then a test lab). HTTP Basic with the vendor's account; filing
  for a pilot adds `webUserName=<the pilot's 1800wxbrief account>`, after the pilot authorizes the vendor
  ("Service Provider Authorization"). `POST .../rest/FP/file` returns a `flightIdentifier`; then
  `.../rest/FP/{flightIdentifier}/activate`, amend, cancel, close, retrieve. Not public: the full schema,
  error codes, agreement terms, production URLs.
- Direct-to-ERAM (ICAO FPL / CHG / DLA / CNL) is for service providers, the military and airlines; FIXM over
  SWIM only publishes ERAM data. Neither is open to an app like ours.

| Operation | Takes | Returns / rules |
|---|---|---|
| File | the ICAO fields, the pilot's account | `flightIdentifier`, state, warnings |
| Amend, Cancel | the identifier (+ fields) | refused within 46 minutes of departure (Leidos) |
| Activate (VFR) | the identifier, actual departure | only within +/- 30 minutes of now |
| Close | the identifier | closed within ETA + 30: no search |
| Retrieve | the identifier, or the pilot | the plan and its state |
| Briefing | route, time | weather and NOTAMs |

Leidos rejects Y / Z flight rules (mixed IFR / VFR). Each landing ends a plan: a multi-leg flight files a
plan per leg.

**Life cycle.** Proposed VFR plans are held 2 hours after the proposed time, then dropped. Activation by
radio, phone, app, or EasyActivate / EasyClose links (30 minutes before departure and arrival); a reminder 20
minutes after ETA. Overdue at **ETA + 30** -> QALQ (communications search) -> INREQ (overdue + 30, or sooner)
-> ALNOT (an hour after the INREQ): search and rescue. SE-SAR (trackers bring the alert forward) and ACAS
(adverse-condition alerts from filing to closing).

**ICAO fields (FAA Form 7233-4, AIM Appendix 4), as the stub validates them.** 7 aircraft ID
`^[A-Z0-9]{2,7}$` (N-number without the dash); 8 rules I/V (Y, Z refused) and type G; 9 type designator
`^[A-Z][A-Z0-9]{1,3}$` / wake L; 10 equipment (10a `N` or letters, 10b surveillance); 13 departure ICAO and
**HHMM UTC**; 15 speed `N\d{4}`, level `A\d{3}` or `VFR`, route `DCT ...`; 16 destination, total EET HHMM > 0,
alternates; 18 `DOF/YYMMDD` (not in the past), `REG/`, `RMK/` ...; 19 `E/` endurance HHMM >= EET, `P/`
persons, `A/` colours (required), `C/` pilot in command (required).

## The stub, in the ALS project

One module, `api/flight_service_sim.py` (a Flask blueprint, registered from ALS's `api/customize_api.py`),
under `/api/flightservice`, authenticated like the rest of ALS; `X-Sim-Now` sets the clock in tests,
`X-Sim-Fail: timeout | reject` simulates an outage.

| Endpoint | Does |
|---|---|
| `POST /plans` `{flight_plan_id}` | reads our FlightPlan, builds the ICAO message (one per leg), validates, files: `201 {flightIdentifier, state: FILED, icao, warnings}`; the row's Status becomes F |
| `PATCH /plans/{fid}` | amend (cutoff: 46 minutes before departure) |
| `DELETE /plans/{fid}` | cancel |
| `POST /plans/{fid}/activate` `{actualDeparture}` | +/- 30 minutes of now; the row becomes A |
| `POST /plans/{fid}/close` | the row becomes C |
| `POST /plans/{fid}/extend` `{newEta}` | resets the overdue clock |
| `GET /plans/{fid}`, `GET /plans?pilot=` | state, worked out on read from the clock: FILED -> EXPIRED (ETD + 2 h); ACTIVE -> OVERDUE (ETA + 30) -> QALQ -> INREQ -> ALNOT |
| `POST /briefing` | canned text |

Errors: `422 {errors: [{code, item, message}]}` - INVALID_FIELD, FLIGHT_RULES_UNSUPPORTED, DEPARTURE_IN_PAST,
DUPLICATE_PLAN, UNKNOWN_AIRCRAFT, UNKNOWN_AIRPORT, ENDURANCE_LT_EET, MISSING_PIC, MISSING_COLOUR; 403
NOT_AUTHORIZED; 409 INVALID_STATE, ACTIVATION_WINDOW, AMEND_CUTOFF.

The rules still decide first: the sample's go / no-go (LogicBank, in ALS's `declare_logic.py`) refuses to
file a NO-GO before the stub is called. The row keeps `FlightServiceId`, `IcaoMessage`, `FiledAt`.

**The mapping.** Item 7 = Aircraft.TailNumber; 8 = `VG`; 9 = the type's ICAO designator (C172, P28A, SR22,
J3) / L; 10 = the aircraft's equipment; 13 = the leg's origin and the departure time in UTC (DOF/ in 18);
15 = `N0120` from the cruise, `A055` from the altitude, `DCT`; 16 = the leg's destination and its minutes as
EET; 19 = endurance from FuelOnBoard / FuelBurn, persons on board from the load, Aircraft.Colors, the pilot.
The sample's tables gain the ICAO type designator, equipment codes, the pilot's phone, and those three columns.

## Sources

- https://www.faa.gov/go/flightservice/
- AIM Appendix 4 (Form 7233-4): https://www.faa.gov/air_traffic/publications/atpubs/aim_html/appendix_4.html
- Leidos web services: https://lmfswebservices.atlassian.net/wiki/spaces/WSS ; filing: https://lmfswebservices.atlassian.net/wiki/x/MoAY ; authorization: https://lmfswebservices.atlassian.net/wiki/x/AQAong ; release note: https://lmfswebservices.atlassian.net/wiki/x/AoDuHw
- ERAS interface: https://www.faa.gov/sites/faa.gov/files/ERAS-Interface-Reference-Guide-9-11-25.pdf
- SFDPS: https://www.faa.gov/air_traffic/technology/swim/sfdps
- JO 7110.10 overdue aircraft: https://www.faa.gov/air_traffic/publications/atpubs/fs_html/chap3_section_4.html
- FAA blog on flight plans: https://www.faa.gov/blog/clearedfortakeoff/weather-plan-you-never-write-down-understanding-flight-plans-flight
- SE-SAR: https://spidertrackshelp.zendesk.com/hc/en-nz/articles/8651530504847-Flight-Services-Surveillance-Enhanced-Search-Rescue
