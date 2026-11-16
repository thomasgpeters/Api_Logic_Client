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

Validated against real failures: it flags all 67 original Test_Xib_View build errors'
causes. Not yet checked: statement syntax (e.g. `tableview`'s `columnWidths`).
