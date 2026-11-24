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
