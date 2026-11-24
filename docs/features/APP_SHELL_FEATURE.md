# App Shell — the generated app's common look

Every app generated from a SQLite project opens in the same frame:

```
┌────────────┬──────────────────────────────────────────────────────────────┐
│            │ [logo]  App Name                        [Theme ▾] [Log In]   │  header
│  ▣ Orders  │         tag-line                                             │
│  ▣ Products├──────────────────────────────────────────────────────────────┤
│  ▣ ...     │                                                              │
│            │   the page: the entity's List part (top) and Form part       │  content
│  dark blue │                                                              │
│  nav bar   ├──────────────────────────────────────────────────────────────┤
│            │ © 2026 Your Company   Saved.     [New][Save][Delete][Refresh]│  footer
└────────────┴──────────────────────────────────────────────────────────────┘
```

- **Navigation bar** (left, dark blue): a white, bold button with an SF Symbol per entity; the
  current page is highlighted.
- **Header:** the business logo, the app name and the tag-line on the left; the theme menu
  (System / Light / Dark) and **Log In** on the right.
- **Footer:** the copyright, a status line ("Saved.", a refused save's reason), and the page
  actions New, Save, Delete, Refresh (also the *Records* menu).
- **Content:** a page per entity, its List above its Form. Choosing a row shows it in the Form.
- **Data:** the pages call the app's data interface (`App Data Lite.incl`: `AppDataList`,
  `AppDataSave`, `AppDataRemove`, answers in `AppDataDone`); saves go through the rules. The
  Enterprise edition will replace only that file (`design/Editions and Licensing.md`).

## Where

| File | In the generated project | Regenerated? |
|---|---|---|
| `src/Runtime/App Shell.incl` | `App Shell.incl` (Runtime group): the frame, the nav buttons, `ShellShowPage`, the theme menu, `ShellDoDialog` | yes |
| `src/Templates/App/Theme.incl` | `Theme.incl` (View group): `ApplyTheme` — the colours and the nav font size | never (yours) |
| `AppPagesSource` in `App Generator.incl` | `App Pages.incl` (Pages group): `APP_TAGLINE`, `APP_COPYRIGHT`, `AppPagesBuild`, `AppPageShown`, `AppPagesDoDialog` | yes |
| `AppWindowsSource` | `Windows.incl`: `ApplyTheme` → `ShellBuildWindow` → `AppPagesBuild` → `ShellShowPage( 0 )` | never (yours) |
| `src/Templates/App/EventHandlers.incl` | `DoDialog` routes: `ShellDoDialog` → `AppPagesDoDialog` → `DoLogin` → `ALSDoDialog` | never (yours) |
| `AppDeveloperReadme` | `README.md`: a developer's tour of the project | yes |

Branding comes from **Project Settings** in the Studio (`ProjectSettingsView.xib`,
`Project Settings.incl`, `Project Workspace.incl`): a logo well (paste or drag; kept as
`<project>/Branding/logo.png`, deployed as `FBapp/AppLogo.png`), the tag-line (≤ 80 characters)
and the copyright, all in `Project.json`. Without a logo the header shows the `building.2` symbol;
without a copyright the footer says `© <app name>`.

## Decisions

- **Built in code, not a XIB.** The frame is boxes (`NSBoxCustom`) and buttons made with FB's
  per-control functions — each Cocoa control has its own setters (`BoxSetFillColor`,
  `ButtonSetContentTintColor`, `TextFieldSetTextColor`, `ImageViewSetImage`, …), every one
  checked against the toolbox headers by `fblint`. The pages stay XIBs, loaded into the content
  view with `nibview …, _shellContent`.
- **Colours in one file you own** (`Theme.incl`): the nav bar's dark blue is a fixed sRGB colour
  (it is the brand, in light and dark mode); everything else uses system colours, so the theme
  menu's Light / Dark / System (`AppSetAppearanceNamed`, `AppSetAppearance( NULL )`) just works.
- **Readable output for the FB community.** Every generated file opens with what it is, whether
  it is regenerated, and developer notes; `README.md` explains the project group by group.
- **ALS projects:** an app over an API Logic Server is the Enterprise edition (roadmap); in Lite,
  Generate App explains how to make the project from the server's SQLite database.
- **Generator Edit menu** (`editmenu`) added so the logo well takes Paste; *Generate XIBs* moved
  from ⌘X (Cut) to ⇧⌘X.

## Verify on a Mac

- [ ] Generator: Project Settings shows the logo well, tag-line and copyright; paste and drag a
      picture; Done; reopen the project — all three come back; ⌘X cuts text, ⇧⌘X generates XIBs.
- [ ] Generate App, build `FBapp/<name>.fbeproj`: the window has the nav bar, header (logo, name,
      tag-line, theme menu, Log In), footer; each nav button shows its page; a List's row fills the Form.
- [ ] Theme menu: Light / Dark / System switch the window's appearance; the nav bar stays dark blue.
- [ ] Resize: the nav bar keeps its width; header and footer stretch; the List grows.
- [ ] New → fill in → Save adds a row; choose a row → change → Save updates it; a constraint's
      message appears when a save is refused; Delete asks, then removes; Refresh re-reads.
