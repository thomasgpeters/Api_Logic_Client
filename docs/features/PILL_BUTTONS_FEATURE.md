# Pill buttons: Mac-style capsule push buttons

The author (2026-11-25): a modern look with Mac-style, pill-shaped buttons - the first item of the
UI transformation (`BACKLOG.md`, Modern look).

## How it works

`PillButton( tag, kind )` turns a push button into a pill once it exists - made in code (`button`)
or loaded from a XIB (`nibview`): FB's `Button…` functions find it by its tag either way.

| macOS | How the pill is drawn |
|---|---|
| 26 and later | AppKit's own capsule: `ButtonSetBezelStyle( NSBezelStylePush )` + `ButtonSetBorderShape( NSControlBorderShapeCapsule )`. The system draws pressed, disabled, light and dark; the window's Return button takes the accent colour; Delete gets `ButtonSetHasDestructiveAction` |
| 15 (the minimum) | `borderShape` does not exist there - calling it would stop the app (`PillButtonsNative` checks `ProcessInfoIsOperatingSystemAtLeastVersion` 26). The button becomes borderless, 24 points high inside its frame, and its layer is rounded to half its height and filled: secondary system fill (plain), accent (main action), system red (Delete), with a matching title colour |

Kinds: `_pillPlain`, `_pillDefault` (the page's main action), `_pillDestructive`.

## Where

| | |
|---|---|
| `src/Generator/Pill Buttons.incl`, `src/Runtime/Pill Buttons.incl` | the module; identical copies (`run_tests.sh` checks) |
| `src/Generator/Windows.incl` | `StudioPillButtons`: every push button on the Studio's pages (Create Project / Create / Done as the main action) |
| `src/Runtime/App Shell.incl` | the generated app's footer (New, Save as the main action, Delete in red, Refresh) and Log In, when `gThemePillButtons` (default YES) |
| `src/Templates/App/Theme.incl` | `gThemePillButtons = YES` - NO gives classic push buttons |
| `src/Generator/App Generator.incl` | `Pill Buttons.incl` is copied into every app, before `App Shell.incl` |

## Decisions

- Set in code, not in the XIB: an Xcode 26 XIB could store the border shape, but our XIBs are written
  by hand and by the generator, and macOS 15 needs the drawn fallback anyway.
- The fallback's layer colours are system colours; the translucent secondary fill reads right in
  light and dark. The accent and red fills keep their colour in both modes, as AppKit's own do.
- Borderless controls (the crumb trail, the navigation bar's buttons) stay as they are: they are not
  push buttons.

## Verify

- Here: fblint (toolbox names and argument counts, build order), the copies identical, the generated
  `App Pages.incl` lints with the runtime including `Pill Buttons.incl` (`run_tests.sh`).
- On a Mac (26 and, if possible, 15): the Welcome, New Project, API Logic Server Project and Project
  Settings pages - pill buttons, Create in the accent colour, Return presses it; a generated app's
  footer - Save accent, Delete red, disabled buttons dimmed; switch Light / Dark from the theme menu.
