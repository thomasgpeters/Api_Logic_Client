# Customs sample: Bermuda customs clearance, automated

This sample model for App Builder for FutureBasic is a national customs clearance system with **automated
clearance**, set in **Bermuda**. We chose it to show LogicBank for FutureBasic on rules that carry legal weight:
- valuation and duty;
- the manifest;
- risk scoring into lanes;
- release, the bond;
- the decision at the port gate.

If you'd like to know how modern systems do it (US CBP, the WCO, ASYCUDA, Bermuda's own notices), the research
and its sources are in `docs/research/Customs Clearance Research.md`.

Bermuda has no land border, so goods arrive in one of two ways:
- **by sea**: containers into the Port of Hamilton, Dockyard and St. George's;
- **by air**: L.F. Wade International.

Please keep in mind that the duty rates and risk weights are **sample values in Bermuda's style**. They
aren't the official tariff or risk profile. The companies and people are made up.

## User stories

- As an importer or a broker, I lodge a declaration, ideally before the ship arrives.
  - Each line's value is the price I paid (FOB), converted at the week's exchange rate.
  - Duty is ad valorem, per unit (alcohol), both (cigarettes), or stepped (cars), plus 1.25 % wharfage.
- As a charity approved for relief (CPC 4071), my goods pay no duty, only wharfage.
- As a resident home from a trip, my personal allowance (300; a visitor's 50) comes off, and baggage pays
  no wharfage.
- As customs, I risk-score every declaration, and the lane follows the score:

  | Lane | Meaning |
  |---|---|
  | Green | Released automatically |
  | Yellow | A document check |
  | Red | A physical examination or an X-ray scan |
  | Blue | A trusted trader's entry: released now, audited later |

  The score is the sum of points for:
  - the country;
  - the importer's compliance record;
  - unregistered, or first-time;
  - goods valued far under their reference price;
  - a broken seal;
  - a late security filing.

  A random draw also sends a few entries to red, whatever their score.
- As customs, I release nothing while:
  - the goods have not arrived;
  - the manifest does not add up;
  - a hold is open;
  - an agency's permit is missing (the Ministry of Health, the Environment department, the Liquor Licence
    Authority);
  - an inspection failed;
  - the lane's check has not passed;
  - the duty is unpaid.

  Prohibited goods are never released. Each entry tells you what it's waiting for.
- As automatic release, I make an entry releasable the moment its last reason goes away, whether that's the
  ship docking, a permit approved, an examination passed or a payment landing. A failed examination costs the
  importer compliance points for its next entries.
- As a bonded importer, I pay monthly, on a statement, as long as what my open statements owe stays
  within my bond.
- As the gate, I let a truck out only with:
  - released goods;
  - its transponder read;
  - the declared seal;
  - a cleared truck and driver;
  - an approved route.

## The model

```
Country, Currency ─< ExchangeRate          Agency ─< Tariff ─< DeclarationLine ─< Permit
PortOfEntry ─< Arrival ─< MasterBill ─< HouseBill ─< Declaration ─< DeclarationLine
                  └─< Container ──────────────────────────┤ ├─< Hold, Inspection, Payment
Importer ─< Statement ─< Declaration, Payment               └─< Movement >── Truck, Driver, Route, Container
Broker ─< Declaration
```

## The rules (93, every one tested)

**Value and duty.**
- A line copies its tariff's rates, agency, prohibited flag and reference price when it's declared, and a
  later tariff change leaves it alone.
- `Value` = the invoice value × the week's rate, rounded first.
- `Duty` = ad valorem (stepped above `StepAbove`) + quantity × the specific rate. It's 0 with relief, and
  relief is refused unless the importer is approved.
- `Wharfage` = 1.25 % of the value, except on a personal declaration.
- The declaration adds its lines up and keeps `CifValue` (+ freight and insurance) for statistics.
- `AllowanceDuty` is the allowance's share of the duty, and `AmountDue`, `Paid` and `Balance` follow from it.
- The exchange rate has to be the one for the week of lodging. A payment is for a declaration or for a
  statement, and is never more than what's due.

**The manifest.**
- A master bill counts its house bills' packages, which have to add up to the manifested packages.
- A house bill is late when its security filing came less than a day before lading.

**Risk and lanes.**
- `RiskScore` adds up these points:

  | Factor | Points |
  |---|---|
  | The country's risk weight | as set per country |
  | The importer's compliance points (when lodged) | half of what it is short of 100 |
  | Not registered | +20 |
  | First-time (registered less than a year) | +15 |
  | A trusted trader (AEO) | −30 |
  | Each undervalued line | +20 |
  | A broken seal | +40 |
  | A late filing | +20 |

- `Lane`:
  - red under a random draw of 0.03;
  - otherwise green under 30, yellow under 60, red above;
  - blue for an AEO entry chosen for audit.
- A failed inspection costs 25 compliance points.

**Release.** `ReleaseReason` is the first of these that applies, and `Releasable` is 1 when none of them does:
1. no goods;
2. prohibited goods;
3. not arrived;
4. the manifest;
5. open holds;
6. missing permits;
7. a failed inspection;
8. red without a passed examination;
9. yellow without a passed check;
10. unpaid, and not on a statement.

`Status` R (released) is allowed only when the entry is releasable.

**The bond.**
- `StatementBalance` (the open statements) may not go over the bond.
- `RequiredBond` = 10 % of the year's duty, at least 10,000, with a `BondSufficient` flag.
- A statement closes only once it's paid.

**The gate.**
- `Movement.Reason` is the first check that fails: released, transponder, seal, truck, driver, route.
- `Lane` G lets the truck out, and the container has to be the one the entry declares.

**Deleting.**
- An entry with payments, a gate movement or an inspection stays. Any other entry takes its lines, their
  permits and its holds with it.
- Importers with declarations or statements stay.
- Arrivals with containers or bills of lading stay.
- Declared house bills and tariffs in use stay.

## The demo scenario (`sample.sql`)

| Entry | Importer, goods | Where it stands |
|---|---|---|
| 1 | Harbour Provisions (AEO): beef, milk powder, grapes, lodged before arrival | green, released on its statement, out of the gate |
| 2 | Island Spirits: whisky and wine from the UK, in pounds | green, released on its statement, out of the gate |
| 3 | Harbour Provisions: beef and bread, the ship still at sea | releasable the moment the ship docks |
| 4 | Somers Building Supply: cement and lumber from China, filed late | yellow, not arrived |
| 5 | Paget Electronics (new): laptops, and phones at 80 each | yellow: a document check, then pay |
| 6 | Bermuda Hospital Trust (AEO, relief): medicines | blue: released, audit later |
| 7 | Coral Reef Imports (unregistered, Colombia), broken seal, with pistols | red: prohibited goods, then the manifest, the hold, the examination |
| 8 | Island Spirits: rosé from France, drawn at random | red: the manifest, the licence pending, an examination |
| 9 | Jane Outerbridge, home from a trip | yellow: the resident's 300 allowance |

## Files

- `schema.sql`: the tables.
- `lookup.sql`: countries, currencies and weekly rates, agencies, the tariff, ports, carriers, brokers and
  routes. It stays when you purge the sample data.
- `sample.sql`: the demo scenario, which `purge_sample.sql` removes.
- `build_db.py`: builds `customs.sqlite`, putting every row through the rules. Entries are released, and trucks go
  out, at the end. `--lookup-only` leaves the scenario out.
- `customs_rules.py`: the rules (the reference).
- `test_rules.py`: 88 scenarios. `--prove` leaves each rule out in turn; a scenario must then fail.
- `Rules.incl`: the same rules in FB, for the generated app's `Rules.incl`.

```bash
python3 samples/Customs/build_db.py
python3 samples/Customs/test_rules.py --prove
```
