# Telecom sample: Northstar Mobile

This is a second sample model for App Builder for FutureBasic, to sit beside Northwind. It's a mobile carrier
(made up) with its customers, accounts, plans and phones, and with **travel plans** priced from its **roaming
agreements** with partner networks abroad (also made up, though set in real countries). We built it to show
LogicBank for FutureBasic on a real-world case that's quite unlike orders and products.

## User stories

- As a customer going abroad, I describe my trip (the countries, and my dates in each) and see what a travel
  plan costs before I buy it.
- As a customer, I buy the travel plan, and it's billed to my account, unless that would take me over my
  credit limit.
- As a customer, I cancel a trip I bought, and it comes off my bill.
- As a family on a shared plan, we see how much of our data we've used, and how much we're over.
- As the carrier's pricing team, when a partner network changes its rates, or we change a zone's markup,
  every country's day price follows, while the quotes customers already have keep their prices.
- As the carrier, I never sell a trip to a country where we have no partner network, nor to a suspended phone.
- As an account manager, I add a phone to a plan only when the plan has a free line.

## The model

```
Customer ─< Account ─< Plan >─ PlanOffer (the catalog: data, minutes, texts, price, lines, home zone)
                        │
                        └─< Phone ─< Usage
                              └─< TravelPlan ─< TravelPlanCountry >─ Country >─ Zone (markup)
                                                                        │
                              PartnerNetwork ─< RoamingAgreement ───────┘ (the country's preferred agreement)
```

A phone belongs to a plan (a family plan shares its data). A travel plan is a trip: its dates, and the
countries visited with their own dates. Countries are grouped in zones, and the plan's home zone needs no
travel plan.

## The rules (39, every one tested)

The pricing engine is made entirely of rules over data, with no code of its own.
- `Country.CostPerDay` is a typical day abroad (0.5 GB, 30 minutes, 20 texts) at the rates of the country's
  **preferred roaming agreement**, recomputed whenever that agreement's rates change.
- `Country.DayPrice` is CostPerDay × the **zone's markup**, rounded up to the next 5.
- A trip's country **copies** the day price when it's added, so a quote keeps its price when rates change
  later. It's **free in the home zone**, and `Amount` = Days × DayPrice.
- `TravelPlan.Price` = the sum of its countries; `Days` comes from its dates.

**What the account owes.** Purchased travel plans add up from phone to plan to account
(`Phone.TravelTotal`, `Plan.TravelTotal`, `Account.TravelCharges`), alongside the plans' monthly prices
(`Account.MonthlyCharges`, each copied from its offer). `Account.Balance` is their sum and has to stay within
the **credit limit**, which is why buying a trip can be refused.

**Checks.** A trip's countries fall within its dates, and you leave after you arrive. A country abroad needs a
partner network (Kenya has none, so there's no service there). A suspended phone can get a quote but can't buy
it. A plan holds at most its offer's lines, and agreement dates are in order with rates that aren't negative.

**Usage.** Data adds up from usage to phone to the plan's shared allowance, and `Plan.DataOverGB` is how much is
over (never on an unlimited plan).

**Deleting.** A trip takes its countries with it, and a phone takes its usage and trips. An account with plans,
or a plan with phones, can't be deleted.

## Files

| | |
|---|---|
| `schema.sql` | the tables (the source of truth) |
| `lookup.sql` | the **lookup data** that stays: zones, countries, partner networks, roaming agreements, plan offers |
| `sample.sql` | the **sample data**, the demo scenario: customers, accounts, plans, phones, usage, travel plans |
| `purge_sample.sql` | removes the sample data and keeps the lookup data |
| `telecom.sqlite` | the database, with every row put in through the rules |
| `build_db.py` | makes `telecom.sqlite` from the three files; `--lookup-only` for an empty carrier, ready to use |
| `telecom_rules.py` | the rules, run here by `tools/logic_reference.py`'s engine (LogicBank for FutureBasic, function for function) |
| `test_rules.py` | 32 scenarios (and the purge); `--prove` leaves each rule out in turn and needs a scenario to fail |
| `Rules.incl` | the same rules in FutureBasic, for the generated app |

## Building the app

1. In Studio for FB: **New Project** → choose `samples/Telecom/telecom.sqlite` → Create.
2. **Generate App.**
3. Copy `samples/Telecom/Rules.incl` over the generated app's `FBapp/Rules.incl` (it's the starting template,
   and it's never overwritten after that).
4. Open the generated project in FutureBasic and build. In the app, buy a quoted trip (Status Q → P) and watch
   the account's balance, or try one that goes over the credit limit.

## Checking the rules here

```
python3 samples/Telecom/build_db.py            # remake telecom.sqlite (--lookup-only: without the demo scenario)
python3 samples/Telecom/test_rules.py          # 32 scenarios
python3 samples/Telecom/test_rules.py --prove  # 39 rules, each tested
```
`tools/run_tests.sh` runs both, and lints `Rules.incl` with the runtime.
