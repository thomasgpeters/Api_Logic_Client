# FutureBasic Documentation Map

Where to look things up in
[thomasgpeters/FutureBasic_Documentation](https://github.com/thomasgpeters/FutureBasic_Documentation)
(private): the current FutureBasic reference, toolbox headers and examples.
This is the primary FB reference for this project. It is current (FB 7.1.x,
macOS 26 era) and supersedes `futurebasic-apis`, which predates FB 7.0.35.

Clone it beside this repo (it is ~54 MB, ~3,000 files):

```bash
git clone --depth 1 https://github.com/thomasgpeters/FutureBasic_Documentation
```

Files use CR line endings; read them with `tr '\r' '\n' < file`.

## `FBHelp/` — the language reference (358 pages)

`FBHelp/Resources/English.lproj/pgs/<page>.html`. These are the same pages as
the online manual, so `docs/reference/FB Reference Index.md` (keyword → page) works
here too: use the page name from its links.

| Need | Page |
|---|---|
| Keyword list (index) | `fbindex.html`; also `Toolboxes/Headers/Key Words` |
| Function return types (FB 7.1.4+ rules) | `fn_userfunction.html`, `local_fn.html` |
| Forward declarations | `def_fn_prototype.html` |
| Records | `begin_record.html`, `record.html` |
| Calling toolbox functions | `fn_toolbox.html`, `toolbox.html` |
| Data types | `app_c_data_types.html` |
| Variables / scope | `app_b_variables.html` |
| Numeric / string expressions | `app_d_numeric_expressions.html`, `app_e_string_expressions.html` |
| Events (dialog/app/menu) | `app_n_events.html` |
| Build system, error messages | `app_k_buildsystem.html` |
| Translator (FB → ObjC) | `app_l_translator.html` |
| Build settings | `app_o_build_settings.html` |
| User libraries | `app_p_UserLibs.html` |
| Export to an Xcode project | `app_q_make_Xcode_Proj.html` |
| Conventions used in the manual | `fbconventions.html` |

## `Toolboxes/Headers/` — toolbox declarations (1,669 `.incl`)

The exact `toolbox fn` names and signatures that FB code calls. Check calls here
rather than from memory.

- `CocoaUI/` — 1,397 headers, one per Cocoa class (e.g. `TableView.incl`,
  `URLSession.incl`), plus 60 framework subfolders (AVFoundation, WebKit, …).
  The statement syntax (`tableview`, `nibview`, `button`, …) is in each
  header's opening comment.
- `Tlbx *.incl` (118) — framework and Core Foundation declarations
  (`Tlbx CFArray.incl`, `Tlbx AVFoundation.incl`, …).
- `Subs *.incl`, `Util_*.incl`, `OSX *.incl`, C library headers (`stdio.incl`, …).
- `NSLog.incl` — `NSLog` and its format escapes.
- `Key Words` — every FB keyword, one per line, with macOS-version notes.

## `FBExamples/` — 578 example programs (`.fb`)

By category: Views and Controls (147), Graphics (79), Strings and Text (44),
Collections (43), Files (40), Windows and Panels (38), Processes and Threads (37),
Menus (19), Numbers (18), EventHandling (17), Application (11), Debug (11), and smaller
sets. Relevant to this project:

- `Networking/URLSession/` — URLSession requests.
- `Miscellaneous/SQLite Demo/` — the current `Tlbx SQLite3.incl` (FB 7.0.11+)
  and demos.
- `Views and Controls/` — tableview, nibview and XIB usage.

## Release notes

Not in the repo: <https://www.brilorsoftware.com/fb/pdfs/releasenotes.pdf>.
Breaking changes that matter here:

- **7.1.4:** a function that returns a value must declare a return type
  (`Type local fn Name(...)` or `local fn Name(...) as Type`); untyped functions
  are `void`.
- **7.1.5:** CF types gain NS names (`CFArrayRef` → `ArrayRef`, …); both work for now.
- **7.0.35:** `TextLabel.incl` merged into `TextField.incl`; `TextLabelWithTag` and
  `TextLabelExists` deprecated (the `textlabel` statement remains).
- `globals "file"`, `proc "Name"`, `defint`/`defstr` letter ranges and `index$` arrays are deprecated.
