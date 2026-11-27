# Auto-complete (related records, or local values)

Author, 2026-11-27: "a text box that looks up matching related records as the user types. The results are in a
results list right below or above (if the control is too low in the layout) the text field. When the user selects
one, the field is populated with the related value (not the key, that happens in the background) but the Name field
or other field, if there is no name. When the user selects a complex control like this, they'll need a little display
to see the appropriate settings."

## In the generated app (`src/Runtime/Auto Complete.incl`)

- A text field. After the first letters (1 by default) the matching parent records appear in a list under the field,
  or above it when the field is low in the window. Names that start with what was typed come first, then names that
  contain it; at most 8 by default.
- Click a match, or use the arrow keys and Return; Escape closes the list. The field shows the record's name (the
  chosen display field); the key is stored with the record on Save.
- Typing again clears the choice until a new one is made. A record shown in the Form displays its parent's name.
- The info button beside it shows the chosen record's details, as for a Dropdown (`Record Popover.incl`).
- The list is Cocoa (a small panel with a table, a child of the window). Views are found with `ShellFindView`
  (`App Shell.incl`), across the app's windows: FB's `ViewWithTag` only looks in its current output window
  ("View does not exist", tag 40100, 2026-11-27).

## Local values (author, 2026-11-27: "custom auto-complete on other fields that are based on in-memory values (called local values), not just lookups of related tables")

Any attribute with a **Values** list can be an auto-complete: the list is written into the generated code
(`AutoCompleteSetValues`), and the matches come from it. `R = Retail, W = Wholesale` shows the label and stores the
code, as a Dropdown does. **Allow other values** keeps what the user types when it is not in the list (a label typed in
full stores its code); it is on for a plain list and off for a list of codes, unless the designer chooses. A Values list
takes precedence over a related table, as for a Dropdown.

## In App Builder

- **Control: Auto-complete**, for a foreign key or an attribute with a Values list (any other attribute falls back to its normal control). The designer can still choose a Dropdown for either.
- Choosing it shows a settings row under the Control popup: **Show** (the parent's field the user sees and types; the
  lookup's display column by default), **After 1 / 2 / 3 letters**, **Up to 5 / 8 / 12 / 20 results**. Kept in
  `Design.json` (`acDisplay`, `acMinChars`, `acMaxResults`, `acOthers`). With local values, Show reads "From the Values list" and **Allow other values** appears; the attribute table moves down to make room only while
  the row shows.

## The generator

- `Type Mapping.incl`: `_xibKindAutoComplete`, its name, its widths, `TypeMapAutoCompleteDisplay / MinChars / MaxResults`.
- `XIB Generator.incl`: a text field and the info button; the model field carries `lookup` and `autocomplete`.
- `Binding Generator.incl`: `AutoCompleteShow` / `AutoCompleteTake`; `AutoCompleteAttach` in FormSetUp;
  `AutoCompleteSetRecords` when the lookup's rows arrive.

## Verification

On a Mac: an Order's Customer as Auto-complete; Generate App; type, choose, Save; reopen the record; the info button;
a field near the bottom of the window opens its list above. Test scenario G-06.
