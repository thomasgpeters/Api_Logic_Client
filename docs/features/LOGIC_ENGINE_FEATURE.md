# Logic Engine (LogicBank for FutureBasic) — core

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
`LogicUpdate( entity, record, keyValues )`, `LogicDelete( entity, keyValues )`;
`LogicMessage` says why the last one failed.

## What the core does

| Step | Insert | Update | Delete |
|---|---|---|---|
| formulas, in dependency order | all | only those whose `dependsOn` changed (pruned otherwise) | — |
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

## Tests

- **Here (Python):** `python3 tools/logic_reference.py --test <Northwind db.sqlite>` —
  a reference engine that follows the FB code function by function; 17 scenarios on a
  temporary copy: order, compute on insert, recompute on update, pruning, constraint and
  message, rollback (also nested), credit limit, delete, cycle, unknown attribute, inactive.
  All pass.
- **On a Mac (FB):** `python3 tools/make_logic_test.py <Northwind db.sqlite> ~/Desktop/LogicTest`
  builds an FB project from the real runtime files with the same 17 scenarios in FB; open
  `Logic Test.fbeproj`, build, run, read PASS / FAIL in the NSLog window.

## Next (roadmap step 2)
Sums and counts (with where), adjusted by delta; re-parenting; one parent write per role;
chaining (`OrderDetail.Amount` → `Order.AmountTotal` → `Customer.Balance` → credit check);
parent references in formulas (`Role.Attr` dependencies).
