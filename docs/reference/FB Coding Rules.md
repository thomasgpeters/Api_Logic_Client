# FB Coding Rules

Rules for every FutureBasic file in this repo **and every file the generator
writes** (`<project>.fb`, `Model Tags.incl`, the copied runtime). They target
FB 7.1.x. Each rule cites where it comes from, and each was learned from a
real build failure or the current reference.

Check them with:

```bash
python3 tools/fblint.py --headers ../FutureBasic_Documentation/Toolboxes/Headers src
python3 tools/fblint.py ~/Library/Application\ Support/Api_Logic_Client/workspace/<project>     # a generated project
```

## Functions

1. **A function that returns a value declares its type.**
   `local fn Name( x as long ) as CFStringRef` or `CFStringRef local fn Name( x as long )`.
   Returning a value (`end fn = x`, `exit fn = x`, `return x`) from an untyped
   function is a translator error since FB 7.1.4; untyped functions are `void`,
   and FB no longer adds an implicit `long` / `return 0`.
   *Source: reference `fn_userfunction.html`; release notes 7.1.4.*
2. **A function that returns nothing is `void local fn`** (preferred) or untyped.
   Its result can't be used in an expression ("function is procedure with no return value").
3. **Define before use.** A function must be defined (or prototyped with
   `def fn`) above its first call; in a project, `data.fbproj` order is the source order.
   *Source: `fn_userfunction.html`, `def_fn_prototype.html`.*

## Comments

4. **Comments are `//`, `/* */`, `///` or `rem` — never `'`.**
   `'` comments were deprecated in FB 7.0.25 and the current translator reads
   `'` as a character literal ("Unknown variable … ''").
   *Source: `rem.html`; release notes 7.0.25.*
5. **No `'~'1` divider/bookmark lines.** Dropped in FB 7.0.24. The FB editor
   converts them when it opens a file, so they only fail in files that were
   never opened in the editor — exactly what generated and freshly pulled files are.

## Projects vs single-file programs

6. **`#build` only works in single-file programs** (`.fb`/`.bas`). In a project,
   put compiler options (e.g. `-lsqlite3`) in Build Settings.
7. **Single-file programs bundle resources with `include resources "File.xib"`**
   and other source with `include "File.incl"` (paths relative to the including file).
   *Source: `include.html`.*

## Toolbox calls

8. **Verify every toolbox name and signature in `Toolboxes/Headers`** of
   FutureBasic_Documentation, not from memory. Statement syntax (`tableview`,
   `nibview`, `button`, `alert` …) is in each header's opening comment.
9. **Cast CF types where a header takes `ObjectRef`**, e.g.
   `fn ObjectClassName( (ObjectRef)dta )` — otherwise clang warns
   "incompatible pointer types … to parameter of type 'id'".
10. **`View…` functions take a view tag, never a window tag.** For a window's
    content view use `_windowContentViewTag` (it refers to the current output
    window). Passing `_window` fails at run time: "Invalid tag. Control 1 does
    not exist in window 1. (ViewSetAutoresizesSubviews)".
    *Source: `CocoaUI/Window.incl`.*
11. **`alert` button titles are an array:** `@[@"Delete", @"Cancel"]`.
12. **Don't use `end` to quit a Cocoa app** — it calls `exit(0)` without cleanup.
    *Source: `end.html`.*

## Data access

13. **`sqlite3_open` creates an empty database when the file is missing** and
    still returns OK. Create the schema first (or check the tables exist),
    otherwise every query fails to prepare and the statement is NULL.
14. **Keep queries and schema in step.** A column a query selects but the table
    lacks fails the whole prepare ("no such column"). Upgrade existing
    databases with `ALTER TABLE … ADD COLUMN …` (it fails harmlessly once the
    column exists).
15. **Log the reason when a prepare fails:**
    `NSLog( @"statement is NULL: %@\nSQL: %@", fn SQL3ErrorMsg( db ), sql )`.
16. **Numbers arrive as NSNumber, nulls as NSNull** (SQLite REAL/INTEGER columns,
    ALS JSON). Show them with `ControlSetObjectValue`; `ControlSetStringValue`
    expects a string.

18. **SQL is parameterized.** Build statements as dictionaries and generate SQL
    with `?` placeholders (Test_Xib_View's `DataObject*.incl`: Select / Insert /
    Update / Delete builders); bind values in placeholder order with one binder
    (`SQLBindValues`). Text binds with length `-1` (SQLite counts UTF-8 bytes);
    `IS NULL` filters have no placeholder. UPDATE and DELETE without a filter are refused.

## Language details that bite

19. **`local mode` before a `local fn`** makes the `dim`s that follow local to that
    function and hides globals inside it; executable statements placed between
    `local` and `local fn` never run. *Source: `local.html`.*
20. **A CF dictionary cannot hold NULL** (`CFDictionaryAddValue( d, key, NULL )`
    crashes with CFType callbacks) — pass `@""` or leave the key out.

21. **Never name a variable or parameter after an FB keyword.** `record`, `text`,
    `resources`, `date`, `time`, `mode`, `window`, `button`, `line` are keywords
    (`Toolboxes/Headers/Key Words`, 350 of them); as names they fail with "Bad factor
    in expression" or "Bad name" wherever FB parses them. Use `aRecord`, `textValue`,
    `resourceDict`.
22. **`for x in` needs an array variable.** `for word in fn Split(…)` and
    `for key in @[ … ]` fail ("Arithmetic variable expected"); assign the array first.
23. **Toolbox overloads: use the active declaration.** Headers keep planned
    signatures inside `#if 0` blocks (e.g. `ERROR_PARAM` versions with `@err`);
    only the `#else` branch is compiled. `FileManagerRemoveItemAtURL( url )` and
    `FileManagerCopyItemAtURL( src, dst )` take no error parameter today.
24. **FB source listed as a resource is compiled.** A `.incl` in a project's
    `resources` lines is translated as part of the app — and a `begin globals …
    end globals` in it ends the implicit global scope, so every later global becomes
    "unknown". Bundle such files as a folder (`resources "../Runtime"`).

- **Mutable variables from getters need a cast.** `fn DictionaryObjectForKey` and
  `fn ArrayObjectAtIndex` return `CFTypeRef` (`const void *`); assigning one to a
  `CFMutableArrayRef` / `CFMutableDictionaryRef` variable makes clang warn "discards
  qualifiers". Cast — `list = (CFMutableArrayRef)fn DictionaryObjectForKey( d, @"k" )` —
  or declare the variable `CFArrayRef` when it is only read.
- **`-lsqlite3` in Compiler Options** is passed to every compile step too; add
  `-Wno-unused-command-line-argument` to the same field (as Test_Xib_View does) or each
  source file warns "'linker' input unused".

- **New code uses FB's current type names and Cocoa wrappers.** The headers mark the CF
  type names deprecated (`CFStringRef` → `StringRef`, `CFDictionaryRef` → `DictionaryRef`,
  `CFArrayRef` → `ArrayRef`, `CFNumberRef` → `NumberRef`, `CFURLRef` → `URLRef`,
  `CFDataRef` → `DataRef`, mutable ones alike); they are aliases, so old code still builds.
  Prefer `DictionaryObjectForKey`, `MutableArrayAddObject`, … over `CFDictionaryGetValue`,
  `CFArrayAppendValue`, …; `CFRelease` only what a `CF…Create` call returned.
- **`ObjectRef` parameters need a cast** (`fn ObjectIsEqual( (ObjectRef)a, (ObjectRef)b )`): a CF
  value passed uncast makes clang warn. fblint reads the parameter types from the headers and
  reports every uncast argument.
- **Cocoa collections refuse NULL.** `MutableDictionarySetObjectForKey( d, NULL, k )` raises
  an exception — guard optional values, or store `NSNull` for SQL NULL.

## Deprecated — don't write these

| Don't | Use | Since |
|---|---|---|
| `globals "file"` | `include` / project file order | 7.0.32 |
| `proc "Name"` | `@fn Name` | 7.0.34 |
| `defint`/`defsng`/`defdbl`/`deflong`/`defstr` letter ranges | declared types | 7.0.33 |
| `index$` arrays | CFArray / `mda` | 7.0.32 |
| `TextLabelWithTag`, `TextLabelExists` | `TextFieldWithTag`, `TextFieldExists` | 7.0.35 |
| `CFArrayRef`, `CFDictionaryRef`, … in CocoaUI calls | `ArrayRef`, `DictionaryRef`, … (both work for now) | 7.1.5 |

## Files

17. **FB source uses CR line endings**; XIB and JSON use LF. The generator
    converts its FB output to CR (`AppWriteSource`).
