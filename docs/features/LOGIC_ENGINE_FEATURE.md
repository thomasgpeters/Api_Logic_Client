# Logic Engine (LogicBank for FutureBasic) — core and aggregates

**Where:** `src/Runtime/Logic Rules.incl` (declaring and activating rules),
`Logic Row.incl` (what a rule reads), `Logic Engine.incl` (saves), on top of the data
runtime (`DATA_RUNTIME_FEATURE.md`). Generated apps get the starting template
`Rules.incl` (`src/Templates/App/`). Design: `design/Logic Engine Design.md`. Clean-room.

## Rules are FB code

```
// OrderDetail.Amount = Quantity * UnitPrice
local fn OrderDetailAmount( logicRow as LogicRowRef ) as CFTypeRef
end fn = fn NumberWithDouble( fn LogicDouble( logicRow, @"Quantity" ) * fn LogicDouble( logicRow, @"UnitPrice" ) )

// Customer.Balance <= CreditLimit
local fn CustomerCreditCheck( logicRow as LogicRowRef ) as BOOL
end fn = ( fn LogicDouble( logicRow, @"Balance" ) <= fn LogicDouble( logicRow, @"CreditLimit" ) )

void local fn DeclareRules
fn LogicFormula( @"OrderDetail", @"Amount", @fn OrderDetailAmount, @[ @"Quantity", @"UnitPrice" ] )
fn LogicConstraint( @"Customer", @fn CustomerCreditCheck, @"Balance {Balance} exceeds credit limit {CreditLimit}" )
end fn
```

The generated `.main` calls `DeclareRules` (in `Rules.incl`, the developer's file) and
then `LogicActivate`. Saves go through `LogicInsert( entity, record )`,
`LogicUpdate( entity, record, keyValues )`, `LogicDelete( entity, keyValues )`,
`LogicUpsert( entity, record )` (update when a row with the record's key exists, else insert —
Imagery LogicBank Studio's fourth test operation);
`LogicMessage` says why the last one failed.

## What the engine does

| Step | Insert | Update | Delete |
|---|---|---|---|
| formulas, in dependency order | all | only those whose `dependsOn` changed (pruned otherwise) | — |
| adjust parents (sums, counts) — chaining | yes | yes | yes |
| constraints (first failure stops) | yes | yes | — |
| write | `DataInsert` (generated key set in the record) | `DataUpdate` (by stored key) | `DataDelete` |

- **One transaction per save** (`DataBegin` / `DataEnd`); a failed constraint rolls back,
  and nests — an inner failure rolls back the outer work.
- **Activation** checks that every entity and attribute is in the model, puts each entity's
  formulas in dependency order, and refuses cycles — with an alert and the details in NSLog.
  Saves are refused until `LogicActivate` succeeds.
- **Updates see the whole row:** columns missing from the record keep their stored values,
  and `LogicOldValue` / `LogicChanged` compare with what was stored.
- **Messages:** `{Attr}` and `{row.Attr}` (as in ALS's `error_msg`) become the row's values.
- **Rules are called by address**, through a one-line `cln` cast to a C function pointer —
  the calling convention FB already uses when it passes `@fn` callbacks to Cocoa (`@fn` page
  of the reference: "the address of a callback function"). FB's own `def fn … using` needs a
  global pointer variable per call site, which is not safe once saves chain into saves; it
  has no examples in FB's 578.

## Sums and counts (step 2)

```
local fn OrderIsUnshipped( logicRow as LogicRowRef ) as BOOL
end fn = fn LogicIsEmpty( logicRow, @"ShippedDate" )

fn LogicSum( @"Order", @"AmountTotal", @"OrderDetailList", @"Amount", NULL )
fn LogicCount( @"Order", @"OrderDetailCount", @"OrderDetailList", NULL )
fn LogicSum( @"Customer", @"Balance", @"OrderList", @"AmountTotal", @fn OrderIsUnshipped )
fn LogicCount( @"Customer", @"UnpaidOrderCount", @"OrderList", @fn OrderIsUnshipped )
```

- **Declared on the parent, filed under the child.** The child list (the model's tomany
  name, e.g. `OrderList`) gives the child entity and its foreign key; activation files the
  rule under the child, because child saves are what change the parent.
- **Adjusted, never re-queried.** A child save changes the parent by the difference it
  makes: inserted +value (count +1), deleted −value, updated new − old; a where that starts
  holding +new, stops holding −old; moved to another parent (foreign key changed): −old from
  the old parent, +new to the new one. Empty values count as 0.
- **One parent write per parent row**, with all its sums and counts together, made through
  `LogicUpdateRow` — so the parent's formulas, its own parents and its constraints run
  (chaining: `OrderDetail.Amount` → `Order.AmountTotal` → `Customer.Balance` → credit
  check). A failure anywhere rolls the whole save back. A chain deeper than 20 is
  refused as a rule loop.
- **Parent references** in formulas: `fn LogicParentValue( logicRow, @"Order", @"ShippedDate" )`,
  declared as `@"Order.ShippedDate"` in `dependsOn` (checked at activation); the parent is
  read once per save; the formula runs on insert and when the row moves to another parent.
- **Sums and counts belong to the rules** (fix for LogicBank audit LB-41): a new row starts
  them at 0 (it has no children yet), and a save from the app keeps their stored values —
  only the engine's own chained parent saves change them, so adjustments always build on a
  value the rules made.
- Not yet: a parent attribute change cascading to its children's formulas (step 3, with copy).

The adjustment assumes the stored sums are right to begin with (as Northwind's are). A
recompute command for existing data is a backlog item.

## Tests

- **Here (Python):** `python3 tools/logic_reference.py --test <Northwind db.sqlite>` —
  a reference engine that follows the FB code function by function; 36 scenarios on a
  temporary copy, all passing. Core (17): order, compute on insert, recompute on update,
  pruning, constraint and message, rollback (also nested), credit limit, delete, cycle,
  unknown attribute, inactive. Aggregates (19), the canonical check-credit logic: detail
  insert → order total, count, customer balance; quantity change; credit limit failing a
  chained save with nothing changed; ship / unship (where transitions); re-parent over the
  limit (fails), re-parent a shipped order, re-parent with room (both customers adjusted);
  a parent reference on a shipped order; delete back to the start. LB-41 and upsert (10): client
  writes to totals kept out, a new order starting at 0, insert / update / unknown-key insert /
  over-the-limit refusal by upsert, a new order deleted with the customer restored. 46 in all.
- **Every rule is needed:** `python3 tools/logic_reference.py --prove <db.sqlite>` runs the suite
  once per rule with that rule left out; each must make a scenario fail (as Imagery LogicBank
  Studio's rule lifecycle expects of a rule's tests). 10 rules, all proven.
- **On a Mac (FB):** `python3 tools/make_logic_test.py <Northwind db.sqlite> ~/Desktop/LogicTest`
  builds an FB project from the real runtime files with the same 46 scenarios in FB; open
  `Logic Test.fbeproj`, build, run, read PASS / FAIL in the NSLog window.

## Next (roadmap step 3)
Copy from parent (on insert), parent check, cascading parent changes to children
(attributes children copy or reference; delete: cascade / nullify / prevent), row events.
