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
│            │ © Company (|< First)(< Previous) Customer 3 of 91 (Next >)(Last >|)│  footer
└────────────┴──────────────────────────────────────────────────────────────┘
```

- **Navigation bar** (left, dark blue): a white, bold button with an SF Symbol per entity; the
  current page is highlighted.
- **Header** (56 points): the app icon (40), the app name and the tag-line on the left; **Log In** on the right
  (Professional). The theme menu (System / Light / Dark) is in the toolbar, at its right (author, 2026-11-27): made in
  `ShellBuildWindow`, moved into a toolbar item (`ToolbarItemSetView`); `ShellFindView` looks in the toolbar's items
  too, and `ShellPopupIndex` reads its choice through Cocoa.
- **Full screen** (`ShellAllowFullScreen`: `NSWindowCollectionBehaviorFullScreenPrimary`): the green button gives the
  app its own space; every part stretches (autoresizing: the cards, the List's columns, the Form's fields, the
  navigator's cells, the toolbar).
- **Footer** (author, 2026-11-27): the copyright on the left, then the **record navigator** across the rest of the
  width: First, Previous, *"Customer 3 of 91"*, Next, Last, as pills in five equal cells that stretch with the window
  (`ShellNavigatorButton`, proportional autoresizing). A dimmed pill is also faded (alpha 0.4: on macOS 15 the layer
  draws the pill and does not grey itself). What just happened ("Saved.", a refused save's reason, "5 of 91 match")
  shows under the window's title, the window's subtitle (`ShellSetStatus`).
- **Window title:** *Company | App* (author, 2026-11-27), the company taken from the copyright (`ShellCompanyName`:
  "© 2026 Imagery Business Systems, LLC" -> "Imagery Business Systems, LLC"); just the app's name when it names none.
- **Splitter** (author, 2026-11-27): a handle in the gap between a page's List card and its Form card
  (`ShellSplitter`, an `ABSplitHandle` view per page, tag `_shellSplitterBase` + the page, shown with its page).
  Dragging it moves the line: the List card, the List and its tiles area give up or take height, the Form card and the
  Form take or give it, the Form's title moves with its card's top; the List keeps at least 140 points, the Form card 90.
  Up-and-down cursor, a short grip line. Its place is kept per page in the app's preferences (`Splitter <page title>`:
  the Form card's height, saved on mouse-up) and put back when the page is built at the next launch.
- **Spacing:** 16 points around the cards, 12 inside them, a 26-point title row (less room above a List: author,
  2026-11-27).
- **Toolbar** (author, 2026-11-27; `App Toolbar.incl`): FB's `toolbar` and `toolbaritem`, so each item has a tag and
  sends `_toolbarItemClick`. **Search** is first (`magnifyingglass`), its label following the page ("Search
  Customers": `AppToolbarShowPage`); then a flexible space and **New**, **Save**, **Delete**, **Refresh**, moved out of the
  footer. The items know the context (`AppToolbarSetEnabled`, autovalidation off): Save only with a change in the Form
  (`AppPageHasChange`: the Form read now differs from the Form as it was shown, `gAppPageClean`, taken after a record
  is shown and after the lookups fill in), Delete only with a record shown. They are updated after every event
  (`AppPagesDoDialog` wraps the handler) and at every keystroke in the Form (`AppToolbarWatchEdits`). A separator follows Search: a vertical `NSBoxSeparator` box as an
  item's view (macOS has had no separator item since 11). FB has no search item, so clicking Search opens our own
  **search dialog**, a Cocoa popover under the item (`AppToolbarSearchPopover`): *Search by* a field (from
  `AppPageSearchFields`, generated: every field shown, its title and kind) or Any Field, then a calendar for a date
  field, a dropdown of the field's distinct values when it has at most 15, each used more than once on average
  (worked out from the page's records), or a text box. Every change sends a query `{ field, mode, text }` to
  `AppPageSearchChanged`, which narrows the List (`Record Search.incl`: `RecordSearchQuery`) and keeps the navigator on
  those. A new page starts a new search. The toolbar can be customised and its arrangement is saved.
- **Navigation bar:** the entity buttons go into a scrolling list (`ShellNavScroll`, the first time a page is shown:
  a flipped document view, an overlay scroller) from the heading to the bar's foot, and the button of the page
  shown is scrolled into view, for models with many entities.
- **Record navigator** (author, 2026-11-27): a page opens on its first record - selected in the List, the List
  given the focus (the arrow keys move through it), the record in the Form. First and Previous are dimmed on the
  first record, Next and Last on the last. After a Save the same record stays selected; after adding one, the new
  one; after a Delete, the one that took its place. Clicking a row or a tile moves the navigator too.
  `AppPageGoTo` / `AppPageChooseRow` (App Pages.incl), `ShellSetNavigator` / `ShellSelectRow` (App Shell.incl,
  through Cocoa).
- **Content:** a page per entity, its List above its Form. Choosing a row shows it in the Form.
- **Data:** the pages call the app's data interface (`App Data Lite.incl`: `AppDataList`,
  `AppDataSave`, `AppDataRemove`, answers in `AppDataDone`); saves go through the rules. The
  Professional edition will replace only that file (`design/Editions Design.md`).

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
without a copyright the footer says `© <app name>` (at its left).

## Decisions

- **Built in code, not a XIB.** The frame is boxes (`NSBoxCustom`) and buttons made with FB's
  per-control functions — each Cocoa control has its own setters (`BoxSetFillColor`,
  `ButtonSetContentTintColor`, `TextFieldSetTextColor`, `ImageViewSetImage`, …), every one
  checked against the toolbox headers by `fblint`. The pages stay XIBs, loaded into the content
  view with `nibview …, _shellContent`.
- **Colours in one file you own** (`Theme.incl`). Everything follows the theme menu's Light / Dark / System
  (`AppSetAppearanceNamed`, `AppSetAppearance( NULL )`) by itself.
  - **Light and dark pairs:** `fn ShellDynamicColor( light, dark )` makes one colour for each mode (`ColorWithName` with a
    provider function; macOS picks as the appearance changes).
  - **The nav bar** is the brand's dark blue, darker in dark mode (author, 2026-11-27: "the blue nav bar should be
    different (darker) in dark mode").
- **Pages as cards on a backdrop** (author, 2026-11-27: the working area "is also not differentiating enough between
  the background and the form layouts").
  - **The backdrop:** the working area is a backdrop (`gThemeContentBackground`): a light grey, or near-black in dark
    mode.
  - **The cards:** each Form and List sits on a rounded card (`gThemeCardBackground`, `gThemeCardBorder`): white, or a
    lifted grey in dark mode.
  - **Spacing:** 24 pt margins around the cards, 16 pt inside them and between them.
  - **The functions:** `ShellCard` draws a card behind a part (called before its `nibview`). `ShellPlacePart` fits the
    part into it. Each card's tag is its part's + `_shellCardTagOffset`, and it is listed with the page's views, so it
    shows and hides with the page.
- **Full width** (author, 2026-11-27: "layouts should stretch across the entire available space, with ample margins.
  Same for grids").
  - **Form and List:** both span the working area's width.
  - **Inside the Form,** labels, fields and drop-downs stretch in proportion (autoresizing `flexibleMinX` +
    `widthSizable` + `flexibleMaxX`), so one, two or three columns spread over the width.
  - **Fixed-width controls** (check boxes, date pickers, radio groups, the lookup info button) keep their width and
    move with their column.
  - **The List's columns** share the table's width (`columnAutoresizingStyle="uniform"`).
- **Each card has a title** (author, 2026-11-27: "a title in slightly larger font size ... a professional look with
  sans-serif fonts").
  - "Customer Details" over the Form (the layout), "Customer List" over the List.
  - The title is set in the system font, San Francisco, semibold at 15 pt (`gThemeCardTitleText`,
    `gThemeCardTitleFontSize`). The fields stay in the system font at 13.
  - The layout's card stands apart from the window's backdrop in both modes.
- **Readable output for the FB community.** Every generated file opens with what it is, whether
  it is regenerated, and developer notes; `README.md` explains the project group by group.
- **ALS projects:** an app over an API Logic Server is the Professional edition (roadmap); in Lite,
  Generate App explains how to make the project from the server's SQLite database.
- **Generator Edit menu** (`editmenu`) added so the logo well takes Paste; *Generate XIBs* moved
  from ⌘X (Cut) to ⇧⌘X.

## Verify on a Mac

- [ ] Generator: Project Settings shows the logo well, tag-line and copyright; paste and drag a
      picture; Done; reopen the project — all three come back; ⌘X cuts text, ⇧⌘X generates XIBs.
- [ ] Generate App, build `FBapp/<name>.fbeproj`: the window has the nav bar, header (logo, name,
      tag-line, theme menu, Log In), footer; each nav button shows its page; a List's row fills the Form.
- [ ] Theme menu (in the toolbar): Light / Dark / System switch the window's appearance; the nav bar is dark blue, darker in Dark.
- [ ] The working area is a grey backdrop (near-black in Dark); the Form and the List sit on rounded cards, white (a
      lifted grey in Dark), with margins around and between them.
- [ ] Resize: the nav bar keeps its width; header and footer stretch; the Form's fields and the List's columns spread
      across the width; the List grows in height.
- [ ] New → fill in → Save adds a row; choose a row → change → Save updates it; a constraint's
      message appears when a save is refused; Delete asks, then removes; Refresh re-reads.

## Header and icons (2026-11-24)

- The app icon (52 points) sits centred in the header's height; the app name, 24-point bold, is
  centred on it, or with a tag-line the two lines are centred together.
- The app icon is the picture from Project Settings (`AppLogo.png`): header, Dock and About box
  (`AppSetIconImage`). Without one, the SF Symbol chosen there (`APP_SYMBOL` in App Pages.incl,
  `ShellSetAppSymbol`), in the header only. A Finder icon (`.icns` with `#plist CFBundleIconFile`)
  is in the BACKLOG.
- Each entity's navigation icon is its Model.json `icon`: the designer's choice in the Studio
  (Icon popup, saved under `"@entity"` in Design.json) or `TypeMapRecommendedIcon` from its name.
- The navigation bar has a "Business Objects" heading (`SHELL_NAV_HEADING`, `gThemeNavHeadingText`).


## Records as tiles (2026-11-27)

Author: "rather than just a grid for multi record results, we also need a grid-bag with records displayed as tiles,
popping style, professional format with subheading name, and other details in the tile in smaller font ... three or
four tiles wide".

- `src/Runtime/Record Tiles.incl`: each List card has a Grid / Tiles switch at the right of its title row. Tiles:
  rounded panels a shade apart from the card, with a soft shadow; the record's name as a subheading (14 pt semibold),
  up to four other fields under it as "Title: value" (11 pt, secondary colour). Four across when the List is at least
  880 points wide, else three; they stretch with the window and are laid out again with the next records. At most
  400 tiles (the grid shows every record). A click picks the record, as a row does, and marks the tile in the
  accent colour.
- The generator (`App Generator.incl`, `AppTilesCall`) chooses the fields from the model: the name field (name,
  title, description or label; else a field with "name" in it; else the first text field), then the first four other
  shown fields that are not keys. `App Pages.incl` calls `RecordTilesBuild` after each List is placed,
  `RecordTilesShow` with each page's records, `RecordTilesPageShown` when a page is shown, `RecordTilesClicked` in
  its dialog handler.
- Tags: 700000 + page x 2000 (the switch, the area, four per tile).
