# LogicBank for FutureBasic

Business rules for your FutureBasic app, declared once and enforced on every save. You say what must be
true (an order's total is the sum of its items; a customer's balance never goes over the credit limit) and the
engine keeps it true, whatever changes and in whatever order. A save that would break a rule is refused and
rolled back, with a message you can show.

It's free and open source (MIT). It was inspired by [LogicBank](https://github.com/valhuber/LogicBank) for
API Logic Server, and rewritten for FutureBasic: your rules are FB functions, and the engine is FB too.

## Why "LogicBank"?

*Logic* is your business logic: the things that must always be true about your data, kept in one place instead
of scattered through your windows and buttons.

*Bank* is like your own bank. What you put in is kept safe and exact, and you never work out your own balance:
the bank does the arithmetic on every transaction, by its rules. LogicBank does the same for your data, so every
total, balance and limit is right whenever you read it.

## The example app

Open `LogicBankExample.fbeproj` in FutureBasic and build (FB 7.0.38 or later, macOS 15 or later).

The example keeps three objects in memory, Customer, Order and Item, with no database. The opening page lists
the rules in plain words; then a story of thirteen saves runs a step at a time (Next Step), or all at once
(Run the Whole Story). It places an order and adds items, changes a quantity, refuses a save that would go over
the credit limit, ships an order, keeps the discount an order was placed with, and prevents and cascades
deletes. After each step you see the objects and the values the rules look after.

Help (the ? button) explains every kind of rule with examples and shows the rules diagram; you can open it in
Preview or export it as PDF or Rich Text.

## The rules

| Kind | In the example |
|---|---|
| formula | `Item.Amount = Quantity x UnitPrice x (100 - Order.Discount) / 100` |
| sum, count | `Order.AmountTotal`, `Order.ItemCount`; `Customer.Balance` and `UnshippedOrders` (unshipped orders only) |
| constraint | `Customer.Balance <= CreditLimit`; `Item.Quantity > 0` |
| copy | `Order.Discount` from the Customer, when the order is placed |
| parent check | an Order's Customer must exist |
| delete actions | a Customer with Orders cannot be deleted; deleting an Order deletes its Items |
| events | row and commit events (in the user guide) |

## Use it in your own app

All you need is the FutureBasic editor.

1. Drag the files into your project, in this order: `Data Model.incl`, `Data Memory.incl` (or the SQLite
   files, below), `Logic Rules.incl`, `Logic Row.incl`, `Logic Engine.incl`.
2. Add your `Model.json` to the project's resources.
3. Write your rules in a `Rules.incl` after the module's files.
4. When the app starts, call `fn DeclareRules`, then `fn LogicActivate`.
5. Save with `LogicInsert`, `LogicUpdate` and `LogicDelete`, and show `LogicMessage` when a save is refused.

The user guide (Help) has every call, with examples.

**SQLite instead of memory:** put `Data SQLite.incl`, the SQL Generator's `DataObject` files and
`Data Records.incl` (from App Builder's runtime, or the [SQL Generator](../SQLGeneratorExample/README.md))
in place of `Data Memory.incl`, and add `-lsqlite3` to the compiler options. The engine and your rules stay as
they are.

## The files

| File | What it is |
|---|---|
| `Logic Rules.incl`, `Logic Row.incl`, `Logic Engine.incl` | **the module**: declaring rules, what a rule reads, the engine |
| `Data Model.incl`, `Model.json` | the model: entities, fields, keys, relationships |
| `Data Memory.incl` | the data layer in memory (this example) |
| `Rules.incl` | the example's rules, written by hand |
| `Story.incl`, `Rich Text.incl`, `Help.incl`, `User Guide.txt`, `LogicBank Diagram.png` | the example: the story, styled output, the Help window |
| `About Imagery.incl`, `About Imagery.txt` | the *About Imagery Business Systems* window |

## Rules by hand, or with App Builder

With the module on its own, you write the rules in FB and test them yourself. **App Builder for FutureBasic**
(licensed, from Imagery Business Systems) can write them for you from sentences in your model's own names,
check them against the model, test every rule, and build the whole app around them.

## Licence

MIT; see `LICENSE`. Copyright (c) 2026 Imagery Business Systems, LLC.
