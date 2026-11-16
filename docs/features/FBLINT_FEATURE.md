# fblint

Checks FutureBasic sources — hand-written and generated — against
`docs/reference/FB Coding Rules.md` before they reach the FB editor.

```bash
python3 tools/fblint.py --headers <FutureBasic_Documentation>/Toolboxes/Headers src
python3 tools/fblint.py ~/Library/Application\ Support/Api_Logic_Client/workspace/<project>      # a generated project
```

| Check | Rule |
|---|---|
| a fn returns a value without a declared type | FB 7.1.4+ translator error |
| `'` comments, `'~'1` divider lines | rejected by the current translator |
| `#build` in a project file | supported only in single-file programs |
| deprecated syntax | `globals "file"`, `proc`, `def*` letter ranges, `index$`, `TextLabelWithTag` |
| a window tag passed to a `View…` function | use `_windowContentViewTag` |
| LF line endings | FB source uses CR |
| `--headers`: every `fn`/toolbox name exists | in FutureBasic_Documentation's headers or the checked code |
| `--headers`: FB keywords used as variable / parameter names | `Key Words` list (350) |
| `--headers`: toolbox argument counts | against the active declaration (`#if 0` blocks skipped; variadic `...` allowed) |
| `for x in` over an expression | needs an array variable |
| `data.fbproj` listing an FB source file as a resource | it would be compiled into the app |

Validated against real failures: it flags the causes of all 67 original Test_Xib_View
build errors, and every error class in the generator's first build (keywords,
`for … in`, argument counts, runtime files compiled as resources). Not yet checked: statement syntax (e.g. `tableview`'s `columnWidths`).

## Block balance

`if`/`end if` (an `if` with no `then` opens a block), `select`/`end select`, `for`/`next`,
`while`/`wend`, `do`/`until` must balance within each fn. A stray closer is reported
with the block it met, e.g. `"end if" closes no open if block (for from line 447)`; an
unclosed opener is reported at its own line. Added after an extra `end if` in
`XIB Generator.incl` stopped the translator ("Unknown variable … 'if'").
