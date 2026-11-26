# LogicBank for FutureBasic

Business rules for your FutureBasic app, declared once and enforced on every save. You tell it what must be
true (an order's total is the sum of its items, say, or a customer's balance never goes over the credit
limit) and the engine keeps it true however the data changes, and in whatever order. If a save would break a
rule, it's refused and rolled back, with a message you can show.

## Why "LogicBank"?

The *Logic* part is your business logic: the rules of your business, the things that must always be true
about your data. LogicBank looks after them in one place, so they aren't scattered through your windows and
buttons.

The *Bank* part is like your own bank. You trust it to keep what you put in safe and exact, and to give it
back when you ask. You also never have to work out your own balance, interest or charges, because the bank
does that arithmetic for you on every transaction, by its rules. LogicBank does the same for your data. You
put your records in, its rules keep every total, balance and limit correct on every save, and whatever you
take out is right.

It's free and open source (MIT), from Imagery Business Systems. We were inspired by
[LogicBank](https://github.com/valhuber/LogicBank) for API Logic Server (also open source) and rewrote it for
FutureBasic, so the rules are FB functions and the engine is FB too.

## The example app

The example keeps three objects in memory, Customer, Order and Item, with no database. A story of thirteen
saves runs step by step:
- placing an order and adding items;
- changing a quantity;
- a save refused for going over the credit limit, and rolled back;
- shipping;
- a discount copied when the order was placed;
- deletes prevented and cascaded.

After each step you'll see the objects and what the rules keep up to date for them. Help (the ? button)
explains every kind of rule with examples and shows the rules diagram; you can open it in Preview or export
it as PDF or Rich Text. *About Imagery Business Systems…* in the application menu tells you what else we make
for FutureBasic.

Open `LogicBankExample.fbeproj` in the FutureBasic editor and build (FB 7.0.38 or later, macOS 15 or later).

## The rules

| Kind | In the example |
|---|---|
| formula | `Item.Amount = Quantity x UnitPrice x (100 - Order.Discount) / 100` |
| sum, count | `Order.AmountTotal`, `Order.ItemCount`; `Customer.Balance` and `UnshippedOrders` (unshipped orders only) |
| constraint | `Customer.Balance <= CreditLimit`; `Item.Quantity > 0` |
| copy | `Order.Discount` from the Customer, when the order is placed |
| parent check | an Order's Customer must exist |
| delete actions | a Customer with Orders cannot be deleted; deleting an Order deletes its Items |
| events | row and commit events (in the guide) |

## The files

| File | What it is |
|---|---|
| `Logic Rules.incl`, `Logic Row.incl`, `Logic Engine.incl` | **the module**: declaring rules, what a rule reads, the engine |
| `Data Model.incl` + `Model.json` | the model: entities, fields, keys, relationships |
| `Data Memory.incl` | the data layer in memory (this example) |
| `Rules.incl` | the example's rules, written by hand |
| `Story.incl`, `Rich Text.incl`, `Help.incl`, `User Guide.txt`, `LogicBank Diagram.png` | the example: the story, styled output, the Help window |
| `About Imagery.incl`, `About Imagery.txt` | the *About Imagery Business Systems* window |

If you'd rather use SQLite than memory, put `Data SQLite.incl`, the SQL Generator's `DataObject` files and
`Data Records.incl` (from App Builder's runtime, or the SQL Generator example) in place of
`Data Memory.incl`, and add `-lsqlite3` to the compiler options. The engine and your rules stay as they are.

## Using it in your own app

All you need is the plain FutureBasic editor:
1. Drag the files into your project, in this order: `Data Model.incl`, `Data Memory.incl` (or the SQLite
   files), `Logic Rules.incl`, `Logic Row.incl`, `Logic Engine.incl`.
2. Add your `Model.json` to the project's resources.
3. Write your `Rules.incl` after the module's files.
4. When the app starts, call `fn DeclareRules`, then `fn LogicActivate`.
5. Save with `LogicInsert`, `LogicUpdate` and `LogicDelete`, and show `LogicMessage` when a save is refused.

The user guide (Help) has every call, with examples.

## Writing rules by hand, or with App Builder

With the module on its own, you write the rules in FB and test them yourself. If you'd like help with that,
**App Builder for FutureBasic** (licensed, from Imagery) writes them from sentences in your model's own
names, checks them against the model, tests every rule with scenarios, and builds the whole app around them.

## Licence

MIT; see `LICENSE`. Copyright (c) 2026 Imagery Business Systems, LLC.
