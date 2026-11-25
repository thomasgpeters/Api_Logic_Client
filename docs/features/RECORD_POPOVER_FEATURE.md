# Record popover: a related record's details beside its Dropdown

The author (2026-11-25, Lite): when a Form has a relationship - an Order's Customer in its Dropdown -
a small icon next to it shows a popup with that Customer's details. The pattern applies to every
relationship, not one entity.

## What the user sees

Every Dropdown that picks a parent record (a lookup: Order → Customer, Order → Employee, Employee →
Department, Address → Person) has an **info button** (ⓘ) at its right. Clicking it opens a popover
beside the button: the heading *"Customer: Alfreds Futterkiste"*, then the parent's fields - each
Title and its value (values can be selected and copied). A click anywhere else closes it. With no
parent chosen, the popover says *"No Customer chosen"*. Value-list Dropdowns have no info button.

## How it works

- **XIB** (`XIB Generator.incl`): for a Dropdown on a lookup (`XibIsLookupDropdown`) the Dropdown is
  `_xibLookupInfoWidth` (24) narrower and a borderless button follows it, tag
  `_xibLookupInfoTagBase` (40000) + the field's tag; `Model Tags.incl` names it `<Field>Info`.
- **Binding** (`Binding Generator.incl`): `<Entity>FormSetUp` registers each lookup:
  `fn RecordPopoverRegister( _orderCustomerId, @"Customer", @[ names ], @[ titles ] )` - the parent's
  shown fields (not Hidden) in the model's order, with the Titles the designer gave them.
- **The rows** (`Binding Support.incl`): `BindingFillLookup` keeps the lookup's whole rows with the
  Dropdown; `BindingChosenRecord( tag )` is the row its selected item stands for. Nothing is read
  again, so the popover is instant and the same in both editions (Lite: SQLite; Enterprise: the
  server's lookup rows).
- **The popover** (`src/Runtime/Record Popover.incl`): made once (FB's `popover` statement, a heading
  and 16 title / value rows), filled and sized for the record, shown with `PopoverShow` at the info
  button's right edge; transient. The button gets its `info.circle` symbol, no border and a tool tip
  when registered.
- **Events** (`App Pages.incl`): `AppPagesDoDialog` passes a button click to `RecordPopoverClicked`
  first, after the radio buttons.

## Decisions

- The details come from the rows the Dropdown already has, not a new query: fresh enough (they are
  read each time the page is shown) and no extra round trip to a server.
- At most 16 fields; long values are cut by the label.
- The info button is part of the generated Form XIB (not added in code) so its place follows the
  Form layout (1 / 2 / 3 columns) like every other control.

## Verify

- Here: fblint on the Studio and the runtime (67 files), the generated `App Pages.incl` lints with the
  runtime including `Record Popover.incl` (`run_tests.sh`).
- On a Mac: generate Northwind; on Order, choose a Customer and click ⓘ beside it - the Customer's
  fields; Employee → Department (two Dropdowns, two buttons); an empty Dropdown -> "No … chosen";
  a value-list Dropdown has no button; light and dark.
