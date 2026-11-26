# LogicBank for FutureBasic

Business rules for your FutureBasic app, declared once and enforced on every save. You say what must be true -
an order's total is the sum of its items, a customer's balance never exceeds the credit limit - and the engine
keeps it true however, and in whatever order, the data changes. A save that would break a rule is refused and
rolled back, with a message for the user.

**Why "LogicBank"?** *Logic*: your business logic - the rules of your business, what must always be true about
your data - is handled here, in one place, instead of being scattered through your windows and buttons. *Bank*:
think of your bank. What you put in, you can take out again: you trust the bank to keep it
safe and exact. And you never work out your own balance, interest or charges - the bank does that arithmetic for
you, on every transaction, by its rules. LogicBank does the same for your data: you put your records in, its rules
keep every total, balance and limit correct on every save, and whatever you take out is right.

Free and open source (MIT), from Imagery Business Systems. Inspired by
[LogicBank](https://github.com/valhuber/LogicBank) for API Logic Server (also open source), rewritten for
FutureBasic: rules are FB functions, the engine is FB.

## The example app

Three objects - **Customer**, **Order** and **Item** - kept in memory, with no database. A story of thirteen
saves runs step by step:
- placing an order and adding items;
- changing a quantity;
- a save refused for going over the credit limit, and rolled back;
- shipping;
- a discount copied when the order was placed;
- deletes prevented and cascaded.

After each step the objects are shown, with what the rules maintain. **Help** (the ? button) explains every kind
of rule with examples, shows the rules diagram, and opens in Preview or exports as PDF / Rich Text. *About Imagery
Business Systems…* in the application menu tells what else Imagery makes for FutureBasic.

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

For SQLite instead of memory, use `Data SQLite.incl`, the SQL Generator's `DataObject` files and
`Data Records.incl` (from App Builder's runtime, or the SQL Generator example) in place of `Data Memory.incl`, and
add `-lsqlite3` to the compiler options. The engine and your rules do not change.

## Using it in your own app

With the plain FutureBasic editor:
1. **Drag the files into your project, in this order:** `Data Model.incl`, `Data Memory.incl` (or the SQLite
   files), `Logic Rules.incl`, `Logic Row.incl`, `Logic Engine.incl`.
2. **Add your `Model.json` to the project's resources.**
3. **Write your `Rules.incl`** after the module's files.
4. **When the app starts,** call `fn DeclareRules`, then `fn LogicActivate`.
5. **Save with** `LogicInsert`, `LogicUpdate` and `LogicDelete`, and show `LogicMessage` when a save is refused.

The user guide (Help) has every call, with examples.

## Writing rules by hand, or with App Builder

With the module alone, you write the rules in FB and test them yourself. **App Builder for FutureBasic** (licensed,
from Imagery) writes them from sentences in your model's own names, checks them against the model, tests every
rule with scenarios, and builds the whole app around them.

## Licence

MIT - see `LICENSE`. Copyright (c) 2026 Imagery Business Systems, LLC.
