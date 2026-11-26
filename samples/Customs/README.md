# Customs sample: Bermuda customs clearance

A national customs clearance system, set in **Bermuda** - a sample model for App Builder for FutureBasic,
built to show LogicBank for FutureBasic on a real-world case with rules that carry legal weight: duty,
pre-clearance, release, and the decision at the port gate. Bermuda has no land border: goods arrive **by sea**
(containers into the Port of Hamilton and Dockyard) and **by air** (L.F. Wade International), and pre-clearance
happens at the port gate. The duty rates are **sample rates in Bermuda's style** - not the official tariff;
the shipping lines, hauliers, importers and people are made up.

## User stories

- **As an importer**, I lodge my declaration before the ship arrives; with a registered customs number and
  every licence my goods need, it is **pre-cleared** - the green lane.
- **As an importer**, I see the duty on every line (the tariff's rate on the value), the processing fee, what
  I have paid and what I still owe.
- **As a bonded importer**, my goods can be released before I pay, as long as what I owe stays within my
  **deferment bond**.
- **As a customs officer**, a declaration lodged late, by an unregistered importer, or missing a licence is in
  the **red lane**: I must inspect it before it can be released, and a failed inspection holds it.
- **As a customs officer**, when the tariff changes, entries already declared keep the rate they were declared at.
- **As the gate**, a truck goes out only when its goods are released, its **transponder** was read, the **seal**
  read matches the one declared, the **truck and the driver** are cleared on the day, and the **route** is
  registered and approved - otherwise it is stopped, and told why.
- **As a haulier**, as soon as the goods are released (or my clearance is renewed, or my route approved), my
  truck waiting at the gate may go.

## The model

```
Country     Tariff          PortOfEntry ─< Arrival ─< Container          Carrier ─< Arrival
   │           │                 │            │           │                 └──< Truck
   └────< DeclarationLine >──────┼────────────┼───────────┤
                │                │            │           │
Importer ─< Declaration >────────┼────────────┘           │
               │  ├─< Payment     └──< Route              │
               │  ├─< Inspection          │               │
               └──┴─< Movement >──────────┴── Truck, Driver, Container
```

## The rules (35, every one tested)

**Duty.** A line copies its tariff's rate and licence requirement when declared; `Duty` = Value × rate. The
declaration adds its lines up (`TotalValue`, `TotalDuty`, `LineCount`), plus the port's processing fee (copied
from the arrival, which copied it from the port); `Paid` is its payments, `Balance` what is left.

**The lanes.** `MissingLicences` counts the lines that need a licence and have none. `PreCleared` - lodged before
the goods arrived, by a registered importer, with every licence, with goods; `Lane` is G or R. Release needs goods,
the green lane or a passed inspection, and no failed inspection.

**The bond.** `Importer.DeferredBalance` is what its released declarations still owe; it may not exceed the
`BondAmount` - so goods without a bond must be paid before release.

**The gate.** `Movement.Reason` is the first check that fails - goods not released, transponder not read, seal
not matching, truck or driver not cleared on the day, route not approved - and `Lane` is G only without one. A
truck goes out (`Status` O) only in the green lane, with the container its entry declares. Every one of these
recomputes when its source changes: a release, a renewed clearance, an approved route.

**Checks and deletes.** Rates between 0 and 100 %; quantities above 0, values not negative, tariff headings that
exist; payments above 0. An entry with payments cannot be deleted (one without takes its lines with it); nor an
importer with declarations, nor an arrival with containers.

## Files

| | |
|---|---|
| `schema.sql` | the tables (the source of truth) |
| `lookup.sql` | the **lookup data** that stays: countries, the tariff, ports of entry, carriers, registered routes |
| `sample.sql` | the **sample data**, the demo scenario: importers, arrivals and containers, declarations, payments, inspections, trucks, drivers, movements at the gate |
| `purge_sample.sql` | removes the sample data and keeps the lookup data |
| `customs.sqlite` | the database - every row put in through the rules |
| `build_db.py` | makes `customs.sqlite` from the three files; `--lookup-only` for an empty, ready-to-use system |
| `customs_rules.py` | the rules, run here by `tools/logic_reference.py`'s engine (LogicBank for FutureBasic, function for function) |
| `test_rules.py` | 41 scenarios (and the purge); `--prove` leaves each rule out in turn and needs a scenario to fail |
| `Rules.incl` | the same rules in FutureBasic, for the generated app |

## Building the app

1. In Studio for FB: **New Project** → choose `samples/Customs/customs.sqlite` → Create.
2. **Generate App.**
3. Copy `samples/Customs/Rules.incl` over the generated app's `FBapp/Rules.incl` (the starting template; it is never
   overwritten after that).
4. Open the generated project in FutureBasic and build. In the app: release entry BDA-26-10430 (refused: red lane),
   add an inspection, release it; at the gate, correct the seal on the stopped truck and let it out.

## Checking the rules here

```
python3 samples/Customs/build_db.py            # remake customs.sqlite (--lookup-only: without the demo scenario)
python3 samples/Customs/test_rules.py          # 41 scenarios
python3 samples/Customs/test_rules.py --prove  # 35 rules, each tested
```
`tools/run_tests.sh` runs both, and lints `Rules.incl` with the runtime.
