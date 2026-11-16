# About Box and Project Settings

**Where:** `src/Generator/ProjectSettingsView.xib`, `Project Settings.incl` (the view),
`Project Workspace.incl` (`ProjectAboutText`, `Project.json` key `about`),
`App Generator.incl` (`AppWriteCredits`, `Model.json` key `about`).

## How it works

**In the generator:** *Model → Project Settings…* (⌘;) shows the Project Settings view
in place of the entity definitions. Its **About text** field (multi-line, wraps) takes at
most **250 characters** (`ABOUT_TEXT_MAX`): typing past the limit cuts the text and
beeps; a counter shows `n / 250`. *Done* saves `Project.json` and returns to the
entity definitions. Opening the project brings the text back.

**In the generated app:** every app gets an About box with no code of its own. FB's
*About <App>* menu item opens the standard macOS About panel, which shows the app's
name, icon and version, and under them the bundle's `Credits.rtf`. Generate App writes
`FBapp/Credits.rtf` from the About text and lists it as a resource in `data.fbproj`.
The text has no colour, so it follows light and dark mode. With no About text the file
is removed and not listed. The text is also in `Model.json` (`"about"`) for the app's
own code.

## Decisions
- The standard About panel over a custom window or alert: it is what macOS users expect,
  and it needs no runtime code.
- RTF made by `AttributedStringRTFFromRange`, not hand-written: Cocoa escapes the text.
- Project Settings is its own view (not a tab of the entity-definition view) so later
  settings (version, copyright, bundle id, icon, theme) have room.

## Verify on a Mac
- [ ] ⌘; shows Project Settings; the counter follows typing; typing past 250 beeps
- [ ] Done → `Project.json` has `"about"`; reopening the project restores it
- [ ] Generate App → `FBapp/Credits.rtf`; the built app's *About* box shows the text, in light and dark mode
