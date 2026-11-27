# Derived Attributes Design: stored or in memory

Author, 2026-11-27: "for the generated apps, a derived attribute using rules should be able to be stored in the
database, or as in-memory only."

A derived attribute is one a rule computes: a formula (`Amount = Quantity * UnitPrice`), a sum (`Order.AmountTotal`), a
count, a copy. Today every one must be a column in the database: the rules engine refuses a rule on any other name
when the rules are activated (`LogicActivate`; the scenario "unknown attribute is refused at activation").

## The choice, per derived attribute

| | Stored | In memory |
|---|---|---|
| Where it lives | a column in the table | nowhere: computed when the record is read |
| When it is computed | on every save that changes what it depends on (as now) | on every read, and on every save (so constraints can use it) |
| Reading a list | the column, as is | computed for each record shown |
| Good for | sums and counts, values other programs read, reports in SQL | formulas on the row itself (a full name, an age, a line total), values nobody else needs |
| Cost | a column, kept right by the rules | time on every read: small for formulas, larger for sums and counts over many children |

Both behave the same to the user and to the rules: a constraint can use an in-memory attribute, and a parent's sum can
add up a child's in-memory amount.

## How it works

- **The model** marks the attribute: `"derived": "stored"` or `"derived": "memory"` (Model.json, from the project's
  `Design.json`). An in-memory attribute is added to the entity's attributes without a column.
- **LogicActivate** accepts a rule on an in-memory attribute (it is in the model, marked memory) and still refuses a
  name that is neither a column nor a declared in-memory attribute.
- **Data Records** leaves in-memory attributes out of every INSERT and UPDATE, and out of the SELECT's columns.
- **Reading:** after `DataFetch` / `DataFetchOne`, the engine computes each in-memory attribute of each record, in
  rule order: formulas from the row and its parents; sums and counts from the children (one query per parent; a
  list of many parents with in-memory sums is the slow case, and App Builder says so).
- **Saving:** the engine computes them as now, before the constraints; Data Records then writes only the columns.
- **Stored attributes** need their column: App Builder adds it (`ALTER TABLE ... ADD COLUMN`, harmless when it exists)
  to the project's database copy when the attribute is made stored.
- **The generated app:** an in-memory attribute shows read-only on the Form and as a column (or tile detail) in the
  List, like any derived value.

## In App Builder

On the entity page, **Add Derived Attribute...**: its name, its type, its rule, and **Storage: Stored / In memory**. An
existing derived column can be switched to In memory (its column then stays in the database, unused, until removed).
The model diagram marks in-memory attributes (an outline glyph beside the rule's).

## Tests (before it is built in FB)

The Python reference (`tools/logic_reference.py`) first: scenarios with in-memory formulas, sums over in-memory child
attributes, a constraint on an in-memory value, a list read; every rule still proven needed. Then the FB engine, the
FB test project (`make_logic_test.py`), and the generated app on a Mac.

## Open (author)

1. Which rule kinds may be in memory: formulas only, or sums and counts too (slower lists)? Proposed: all, with
   App Builder warning for sums and counts.
2. The default for a new derived attribute: Stored or In memory? Proposed: In memory for formulas, Stored for sums
   and counts.
