# XIB Parts (Form and List)

Two embeddable parts per entity, each a self-contained custom view.

**Where:** `src/Generator/XIB Generator.incl` (`XibViewDocument`, `XibListDocument`);
layout rules in `Type Mapping.incl`.

| Part | File | Contents | Tags |
|---|---|---|---|
| Form (scalar) | `<Entity>Form.xib` | Title + control per attribute, one or two columns (two above 10 fields) | view = index·100, fields = index·100 + n |
| List | `<Entity>List.xib` | scroll view + view-based table, one column per attribute | view = 20000 + index·10, scroll +1, table +2 |

`index` is the entity's position in name order, so tags are stable across
regenerations. Constants for every tag go to `Model Tags.incl`
(`_customerCompanyName`, `_customerListTable`); names keep CamelCase.

## Decisions

- **Form layout:** 1, 2 or 3 columns (`TypeMapFormColumns`): the designer's choice (entity
  `design.formColumns`, saved under `"@entity"` in `Design.json`), else 1 up to 10 shown fields,
  2 up to 24, then 3. Rows are split evenly (ceil(fields / columns) per column); the label width is
  the longest title (at most 150), the column width the widest field (fields capped at 200 in a
  three-column Form). Tags follow the model's attribute order, so hiding a field renumbers nothing.
- **Hidden** attributes are on neither the Form nor the List and have no tag; they stay in
  `Model.json` (`"hidden": true`, tag 0) because the data runtime reads every column. Their
  binding is not generated, so a save leaves them unchanged (`DataUpdate` sets only the columns
  it is given).
- **Read-only text:** a selectable, non-editable field without a bezel. The default for a key
  the database generates (`SQLite Model.incl` marks it `"generated"`: keyKind identity or
  autoincrement); `<Entity>FormToRecord` does not read it back (the key travels in `gAppPageKeys`).
- **Dates and times:** DATE → date picker (year, month, day); DATETIME / TIMESTAMP → date and time
  picker (also hours and minutes); TIME → time picker (hours, minutes, seconds). One
  `XibDatePickerElement` writes all three, with the matching `datePickerElements`. Bindings
  (`Binding Support.incl`) store `yyyy-MM-dd`, `HH:mm:ss`, `yyyy-MM-dd HH:mm:ss` through an
  en_US_POSIX formatter; a stored ISO `T` separator and a date-only value are read too.
- **Choices:** a Dropdown is an empty `popUpButton`, filled when the app runs: a value list in
  `<Entity>FormSetUp` (`BindingFillChoices`), a lookup table's rows in `<Entity>FillLookup`
  (`BindingFillLookup`, after `AppDataLookup` answers `_appDataLookup`). Item 0 is empty (NULL);
  each item's value is kept per tag (`gBindingChoiceKeys`) and the value a record wants is kept
  too (`gBindingChoiceWanted`), so rows that arrive after the record (a server) still select it.
  Radio buttons sit in a `customView` with the field's tag; button n has tag
  30000 + field tag × 10 + n (`BindingRadioTag`); `BindingRadioClicked` turns the others off.
  Model.json carries a choice's `values` or `lookup` ({ entity, key, display }), which
  `SQLite Model.incl` sets on a single-column foreign key.
- **Type → control:** VARCHAR/CHAR → text field (width from length, capped);
  TEXT → one-line field, 280 wide (SQLite declares every string TEXT; the designer can choose Text
  area); CLOB / MEDIUMTEXT / LONGTEXT → text area; integer types → right-aligned field with integer formatter;
  FLOAT/DECIMAL/DOUBLE → 2-decimal formatter; DATE/TIMESTAMP → date picker;
  BOOL/BIT → checkbox. Long VARCHARs are *not* text areas (Northwind declares
  nearly everything `VARCHAR(8000)`).
- **List XML follows FB's own example** (`FBExamples/Strings and Text/LinguisticTagger`):
  column `identifier` = attribute name = row-dictionary key; each column's prototype
  `tableCellView` has the same identifier and a text field wired to its
  `textField` outlet.
- **Colors** are system catalog colors, so light and dark mode work unchanged.
- Generated XIB ids are `gen-NNNN`, unique per document.

## Verified

Form and List documents rendered from the FB templates for Customer, Order,
OrderDetail and Location: well-formed XML, unique ids, all references resolve,
cell identifiers = column identifiers.
