# Telecom sample: Northstar Mobile

A second sample model beside Northwind, for App Builder for FutureBasic: a mobile carrier (made up),
its customers, accounts, plans and phones - and **travel plans** priced from its **roaming agreements**
with partner networks abroad (made up, in real countries). Built to show LogicBank for FutureBasic on
a real-world case quite unlike orders and products.

## The model

```
Customer ─< Account ─< Plan >─ PlanOffer (the catalog: data, minutes, texts, price, lines, home zone)
                        │
                        └─< Phone ─< Usage
                              └─< TravelPlan ─< TravelPlanCountry >─ Country >─ Zone (markup)
                                                                        │
                              PartnerNetwork ─< RoamingAgreement ───────┘ (the country's preferred agreement)
```

A phone is part of a plan (a family plan shares its data). A travel plan is a trip: dates, and the
countries visited with their own dates. Countries are grouped in zones; the plan's home zone needs no
travel plan.

## The rules (39, every one tested)

**The pricing engine is rules over data - no code of its own.**
- `Country.CostPerDay` - a typical day abroad (0.5 GB, 30 minutes, 20 texts) at the rates of the country's
  **preferred roaming agreement**; recomputed whenever that agreement's rates change.
- `Country.DayPrice` - CostPerDay × the **zone's markup**, rounded up to the next 5.
- A trip's country **copies** the day price when it is added - a quote keeps its price when rates change later;
  it is **free in the home zone**; `Amount` = Days × DayPrice.
- `TravelPlan.Price` = the sum of its countries; `Days` from its dates.

**What the account owes.** Purchased travel plans add up from phone to plan to account
(`Phone.TravelTotal`, `Plan.TravelTotal`, `Account.TravelCharges`), with the plans' monthly prices
(`Account.MonthlyCharges`, each copied from its offer); `Account.Balance` is their sum and must stay within
the **credit limit** - so buying a trip can be refused.

**Checks.** A trip's countries within its dates; leaving after arriving; a country abroad needs a partner
network (Kenya has none: no service); a suspended phone can get a quote but not buy it; a plan holds at
most its offer's lines; agreement dates in order and rates not negative.

**Usage.** Data adds up from usage to phone to the plan's shared allowance; `Plan.DataOverGB` is what is over
(never on an unlimited plan).

**Deleting.** A trip takes its countries with it; a phone its usage and trips; an account with plans, or a
plan with phones, cannot be deleted.

## Files

| | |
|---|---|
| `schema.sql` | the tables (the source of truth) |
| `telecom.sqlite` | the database - every row put in through the rules |
| `build_db.py` | makes `telecom.sqlite`: the seed data, inserted through the rules |
| `telecom_rules.py` | the rules, run here by `tools/logic_reference.py`'s engine (LogicBank for FutureBasic, function for function) |
| `test_rules.py` | 30 scenarios; `--prove` leaves each rule out in turn and needs a scenario to fail |
| `Rules.incl` | the same rules in FutureBasic, for the generated app |

## Building the app

1. In Studio for FB: **New Project** → choose `samples/Telecom/telecom.sqlite` → Create.
2. **Generate App.**
3. Copy `samples/Telecom/Rules.incl` over the generated app's `FBapp/Rules.incl` (the starting template; it is
   never overwritten after that).
4. Open the generated project in FutureBasic and build. In the app, buy a quoted trip (Status Q → P) and watch
   the account's balance - or try one over the credit limit.

## Checking the rules here

```
python3 samples/Telecom/build_db.py            # remake telecom.sqlite
python3 samples/Telecom/test_rules.py          # 30 scenarios
python3 samples/Telecom/test_rules.py --prove  # 39 rules, each tested
```
`tools/run_tests.sh` runs both, and lints `Rules.incl` with the runtime.
