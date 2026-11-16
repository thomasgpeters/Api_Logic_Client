# Binding Code

Readable, generated FB that moves records between data and the XIB parts.

**Where:** `src/Generator/Binding Generator.incl` writes `<Entity> Binding.incl`;
helpers in `src/Runtime/Binding Support.incl` (copied into every generated app).

A **record** is a dictionary keyed by attribute name — a SQLite row or ALS
attributes alike. Per entity:

```
void local fn CustomerRecordToForm( record as CFDictionaryRef )
fn BindingShowText( _customerCompanyName, record, @"CompanyName" )
fn BindingShowNumber( _customerBalance, record, @"Balance" )
…
local fn CustomerFormToRecord as CFMutableDictionaryRef
fn BindingTakeText( record, @"CompanyName", _customerCompanyName )
…
void local fn CustomerRecordsToList( records as CFArrayRef )
```

| Helper | Does |
|---|---|
| `BindingShowText / Number / Date / Check` | value → control; NULL shows empty (date: today) |
| `BindingTakeText / Integer / Decimal / Date / Check` | control → record; empty controls are left out (stored as NULL) |
| `BindingString`, `BindingValue` | read a value; NSNull and missing keys read as NULL |

Numbers are shown with `ControlSetObjectValue` (SQLite REAL/INTEGER and ALS numbers
arrive as NSNumber). Dates are `yyyy-MM-dd`.

## Verified

`Customer Binding.incl` and `Order Binding.incl` rendered from the generator's
templates against Northwind; fblint clean together with `Binding Support.incl`.
