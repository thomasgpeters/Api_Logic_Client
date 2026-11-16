# FB Coding Rules

Rules for every FutureBasic file in this repo **and every file the generator
writes** (`<project>.fb`, `Model Tags.incl`, the copied runtime). They target
FB 7.1.x. Each rule cites where it comes from, and each was learned from a
real build failure or the current reference.

Check them with:

```bash
python3 tools/fblint.py --headers ../FutureBasic_Documentation/Toolboxes/Headers Generator Runtime
python3 tools/fblint.py ~/ApiLogicClient/"<project>"     # a generated project
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
10. **`alert` button titles are an array:** `@[@"Delete", @"Cancel"]`.
11. **Don't use `end` to quit a Cocoa app** — it calls `exit(0)` without cleanup.
    *Source: `end.html`.*

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

12. **FB source uses CR line endings**; XIB and JSON use LF. The generator
    converts its FB output to CR (`AppWriteSource`).
