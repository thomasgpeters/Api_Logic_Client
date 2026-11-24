# Entity Definitions (designer view)

Shows the model and the generator's recommendations before anything is
generated, and lets the designer adjust them.

**Where:** the attribute table in `src/Generator/ProjectDetailView.xib` (tag 2100);
rules and adjustments in `src/Generator/Type Mapping.incl`; display, editing and
persistence in `Project Actions.incl` (`DisplayObjectAttributeList`,
`DesignCellEdited`, `DesignSave`, `DesignLoad`).

## The view

Selecting an entity shows a summary — `Customer — key Id (assigned) — OrderList ↓`
(↑ toone, ↓ tomany) — and one row per attribute:

| Column | Editable | Source |
|---|---|---|
| Name | | model |
| **Title** | ✓ | field label *and* column heading; default splits CamelCase (`CompanyName` → "Company Name", `customer_id` → "Customer ID") |
| Data Type | | declared SQL type |
| FB Type | ✓ | `CFStringRef`, `NSInteger`, `double`, `CFDateRef`, `BOOL`, `CFDataRef` |
| Size | | `40 chars`, `10,2`, `64-bit`, `variable` |
| Key | | `PK`, `FK → Customer`, `PK, FK → Order` |
| Required, Default | | NOT NULL, column default |
| Form Control | ✓ | Text field, Text area, Integer field, Decimal field, Date picker, Checkbox |
| Form Width, List Width | ✓ | points |
| Adjusted | | which values the designer changed |

## Adjustments

An edit is stored in the attribute's `design` dictionary (`title`, `fbType`,
`formControl`, `formWidth`, `listWidth`); clearing a cell returns to the
recommendation. All adjustments are saved to `~/Library/Application Support/Imagery LogicBank Studio for FutureBasic/workspace/<project>/Design.json`:

```json
{ "Customer": { "CompanyName": { "title": "Company", "listWidth": "180" } } }
```

and re-applied whenever the model is opened. Every generator reads attributes only
through `TypeMapAttribute…` functions, so what the designer sees is what gets generated.

## Notes

- Table column identifiers equal the row-dictionary keys — FB's table data source
  matches by identifier (the previous columns had automatic identifiers).
- Editing uses `_tableViewCellTextDidEndEditing` with `TableViewEventRow`,
  `TableViewEventColumnIdentifier`, `TableViewEventCellString`.
