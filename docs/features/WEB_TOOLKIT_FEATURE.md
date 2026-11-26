# Web Toolkit for FutureBasic (working name): web apps written in FB

Status: **built here, lint-clean; not yet compiled on a Mac.** The FastCGI core is compiled and tested here behind a
real nginx; `web.js` is tested in headless Chromium against a Python reference of the protocol. The FB files wait for
their first build. The design and its reasons: `docs/design/Web Toolkit Design.md`.

The author, 2026-11-26: a widget library for every HTML control, with event handlers sent back to FutureBasic and
bound to the database. "FutureBasic would become the middleware and the business application would run in the
FutureBasic code, but we would be serving up a webpage that acts and behaves as any normal webpage does."
In the same session the author also asked for:
- every widget asynchronous (AJAX);
- a page lifecycle, so data is saved back to FB and the database;
- an FB app template for the events in and out of FastCGI;
- a core that is dynamic and tied to no data model, because App Builder will target a desktop app or a web app.

## How it works

```
Browser ──HTTPS──> nginx ──FastCGI──> the FB app (long-running, 127.0.0.1:9000)
  web.js: sends events (fetch, JSON),    Web Events.incl: the page, or an event -> the app's FB function
  applies the updates in place           Web Widgets / Render: what changed, as updates (or HTML)
                                         Web Binding.incl (optional): forms and tables <-> LogicBank <-> data
```

1. **The first GET of the page** creates a session: a random id in an `HttpOnly`, `SameSite=Strict` cookie, and a token in the
   page's `<meta>`. The app's `BuildPage` makes the widget tree once. The whole tree is rendered as HTML (Bootstrap 5's
   class names), with `web.js` and `web.css`.
2. **The user acts:** a click, a change, typing, Enter, a row chosen, a form submitted. `web.js` POSTs
   `{ token, widget, event, value, values }` to `fbweb/event`. `values` holds every field on the page.
3. **The FB app** puts the values into the widgets and calls the function the app connected (`WebOn`). The function
   changes properties, adds or removes widgets, or saves through the rules.
4. **The answer** is `{ updates: [...] }`: only what changed, which `web.js` applies in place. The page never reloads.
   Events are queued, so FB sees them in the order the user made them. A thin bar shows when an answer is slow.

### The files (`src/WebToolkit/`)

| File | Holds | Depends on |
|---|---|---|
| `Web Server.incl` | the FastCGI server: C (sockets, records, GCD on the main queue) + ObjC glue; `FastCGIServerStart` | - |
| `Web Session.incl` | sessions: id, token, widgets, updates, the app's data (`WebSessionData`); `@fn` callers | Server |
| `Web Widgets.incl` | the widgets, their properties, reading values, removing, focus, navigation, theme; `WebOn`, `WebFire` | Session |
| `Web Render.incl` | HTML for every widget (escaped), the page, the updates of an answer | Widgets |
| `Web Events.incl` | requests in, answers out (CGI), the lifecycle, `WebStart`, `WebUseStylesheet`, `WebOnSessionEnd` | Render |
| `Web Layout.incl` | pages laid out in XIB files: `WebLoadLayout` (Objective-C reads the XIB; FB makes the widgets) | Widgets |
| `Web Binding.incl` | **optional**: forms and tables bound to Model.json entities through LogicBank for FutureBasic | Events + LogicBank's Data / Logic |
| `Resources/web.js` | the browser's half: AJAX events, updates, the lifecycle, unsaved-changes guard | - |
| `Resources/web.css` | themes as tokens: light, dark (or the visitor's system), colourful, base; rows in twelfths | - |
| `Layout Tool/Layout Tool.html` | the layout tool: XIBs laid out, previewed as the web shows them, saved | - |

**The core knows no data model.** Server, Session, Widgets, Render and Events have no entity, attribute or database.
`Web Binding.incl` plugs into the core's lifecycle through two hooks, set when a form is first bound. An app that binds
its own way leaves the file out.

### Widgets

| Call | HTML | Events |
|---|---|---|
| `WebContainer( s, parent, id, layout )` | `div` / `form` / `section`; layout: row, column, card, form, section, toolbar | submitted (form) |
| `WebHeading( s, parent, id, text, level )`, `WebText( ..., look )`, `WebLabel`, `WebDivider`, `WebImage` | `h1`-`h6`, `p`, `label`, `hr`, `img` | clicked |
| `WebLink( s, parent, id, text, address )` | `a`; address "" = an action link | clicked |
| `WebMessage( s, parent, id, text, role )` | `.alert` band; empty hides it | - |
| `WebButton( s, parent, id, title, role )` | `button.btn.btn-<role>` | clicked |
| `WebField( s, parent, id, label, type, hint )` | `input`: text, email, password, number, date, time, datetime-local, color, range, search, tel, url | changed, typed, entered |
| `WebTextArea`, `WebCheckbox`, `WebRadioGroup`, `WebSelect` | `textarea`, check box, radio `fieldset`, `select` (choices `{ code, title }`) | changed, typed |
| `WebTable( s, parent, id, columns )`, `WebList` | `table.table-hover` (columns `{ key, title, align }`), `ul.list-group` | selected (row number) |

- **Set:** `WebSetText`, `WebSetValue`, `WebSetChecked`, `WebSetEnabled`, `WebSetVisible`, `WebSetMessage`,
  `WebSetOptions`, `WebSetRows`, `WebSetSelectedRow`, `WebSetProperty`, `WebRemove`, `WebClear`, `WebFocus`,
  `WebNavigate`, `WebSetTheme`.
- **Read:** `WebValue`, `WebDoubleValue`, `WebChecked`, `WebSelectedRow`, `WebSelectedRecord`, `WebProperty`.

An event function: `void local fn Name( session as WebSessionRef, widgetId as CFStringRef, eventValue as CFStringRef )`.

### The page's lifecycle

Events on the widget `page`, plus the app's session-end function:

| Phase | When | The toolkit first | The app (typical) |
|---|---|---|---|
| created | a new session | - | `BuildPage` builds the widgets |
| shown | the page is sent: "first", or "again" on a reload | - | refresh data |
| hidden | tab or window switched away | saves auto-saving forms with unsaved changes | - |
| visible | back again | - | refresh data (other users' changes) |
| leaving | page closed or left (a beacon: no answer awaited) | saves auto-saving forms | keep work in progress |
| ended | idle for `WEB_SESSION_IDLE` (2 hours) | saves auto-saving forms | `WebOnSessionEnd` |

- **Keeping the session:** while the page is visible, `web.js` keeps it alive. A session that has ended anyway shows a
  notice and the page starts again.
- **Unsaved changes:** a bound form is dirty from the first change until it is saved or shown again; it is marked at
  once in the browser. The browser asks before the page is left while a form that does not save itself is dirty.

### Binding (`Web Binding.incl`)

- **Forms:** `WebFormBind( s, form, entity, messageId )` and `WebBindField( s, form, field, attribute )`.
  - Showing and reading: `WebFormShowRecord`, `WebFormNew`, `WebFormRecord` (numbers by the model's column type; an
    empty field is null).
  - Saving: `WebFormSave` (`LogicInsert` / `LogicUpdate`; the rules run, the stored record is read back) and
    `WebFormDelete` (`LogicDelete`). The form fires "saved" or "deleted"; a refusal shows the rule's message and keeps
    what was typed.
  - `WebFormAutoSave`, `WebFormIsDirty`, `WebFormSetRecordValue` (a value no field shows).
- **Tables and choices:** `WebTableShowEntity( s, table, entity, filter, order )`, `WebTableRefresh` (the selection
  kept), and `WebChoicesFromEntity` (a lookup drop-down).

### Security

- **Escaping:** every text is escaped by the server, and `web.js` sets text with `textContent`.
- **No inline script:** the Content-Security-Policy allows only the server's own scripts, so nothing injected can run.
- **Forged events:** each event must carry the session's token; a page on another site has the cookie but not the token.
- **Limits:** nginx limits the body (1 MB); the FastCGI core limits records and parameters.
- **Logging:** every NSLog is gated (`isLoggingOn`).

## The app template (`src/WebToolkit/Template/`)

A project to copy: `Web App.fbeproj` and the toolkit's files.
- **`Pages.incl`** is the one file the developer writes: `AppTitle`, `AppStarting` (open the database, declare the
  rules), the event functions, the lifecycle functions, and `BuildPage`.
- **`Server Window.incl`** is the same in every app: it starts the server and shows requests and sessions; the app
  keeps serving when it is closed.
- **Running it:** `nginx.conf` for testing, and `com.example.webapp.plist` (a LaunchAgent) to keep it running.

## The example (`src/WebToolkitExample/`)

Orders on Customer / Order / Item, in memory, with the LogicBank example's rules. Built from the template.
- **The page:** Customers, Orders and Items tables with forms; a theme menu.
- **The rules on the web:** a balance over the credit limit is refused, and the message is shown; totals and balances
  follow every save.
- **Ship Today** moves the balance.
- **The Item form saves itself** when the page is hidden.
- **Shared data:** every visitor sees the same data; switching tabs refreshes.

## Two targets from one model (App Builder, planned)

The author: App Builder will offer **Desktop app** or **Web app** as the target. Both are compiled by FutureBasic,
over the same model, the same LogicBank for FutureBasic rules and the same data layer; only the UI layer and its
event model differ.

| | Desktop | Web |
|---|---|---|
| UI | XIB windows and views (XIB Generator.incl) | Web widgets (`Pages.incl`, generated) |
| Events | FB's `on dialog` / `on menu` / `on appevent` | FastCGI events through `WebOn` |
| Binding | `<Entity> Binding.incl` | `Web Binding.incl` |
| Runs | on the user's Mac | on a Mac server, behind nginx; any browser |

## XIB layouts and the layout tool (author, 2026-11-26: "go ahead with the XIB templates and layout tool")

A page can be laid out in a XIB: the file Interface Builder edits and a desktop app loads. One layout serves both
targets.

```
fn WebContainer( session, @"page", @"customersPanel", @"section" )
fn WebLoadLayout( session, @"customersPanel", @"CustomerPanel" )      // CustomerPanel.webxib, in Resources
fn WebOn( session, @"customerSave", @"clicked", @fn CustomerSave )     // widgets found by their Identifiers
```

### The rules (`tools/web_layout_reference.py` is the reference)

1. **Controls.** Each XIB element becomes one control. Frames are measured from the top-left (XIBs measure from the
   bottom-left). Plain nested views are see-through: their controls join the parent's.

   | XIB | Widget |
   |---|---|
   | editable text field (number formatter: number), secure, search, combo box | field (text, number, password, search) |
   | wrapping text field taller than 30 pt, a scroll view holding a text view | text area |
   | label (text style largeTitle / title1-3 / headline) | heading 1-4 |
   | label | text (secondary colour: muted) - or a field's label (step 2) |
   | **empty label with an Identifier** | **message band** (where WebSetMessage and bound forms speak) |
   | date picker | date, time or datetime-local field |
   | slider, colour well | range, colour field |
   | check box | check box |
   | radio buttons alone in a view, or one radio button | radio group |
   | pop-up button | drop-down (item tags as codes, else titles) |
   | scroll view holding a table view | table (column identifiers as keys, header titles, right alignment as `end`) |
   | box | card, or a **form** when it holds inputs; its title becomes a heading |
   | separator box, image view | divider, image |
   | push button (Return: primary); an image-only button | button; nothing |

2. **Labels.** A label just left of an input (in the same band, within 40 pt), or just above it (within 12 pt, left
   edges within 16 pt), becomes that input's label, without its colon.
3. **Rows.** Controls whose frames overlap by at least half the smaller height form a row, left to right.
   - A row of buttons is a toolbar, placed at the end when it starts past the middle.
   - Otherwise each control spans its share of 12 columns (`data-fb-span`). On a phone they stack one under another.
4. **Ids.** A widget's id is its Identifier (Interface Builder: Identity > Identifier), else `tag<n>` from its tag,
   else the XIB's own id. Rows are named `<parent>-r<n>`.

### Three implementations, held to one reference

| Where | What | Tested by |
|---|---|---|
| `Web Layout.incl` | Objective-C (`NSXMLDocument`) between the "XIB layout core" markers, plus FB: `WebLoadLayout`, `WebLoadLayoutView`, `WebLayoutBuild` (the tree -> the widget calls) | `tools/check_web_layout.py`: compiles exactly that text with GNUstep and compares its trees with the reference on 16 XIBs |
| `Layout Tool/Layout Tool.html` | JavaScript: the web preview | `tools/check_layout_tool.py`: the same comparison, in Chromium |
| `tools/web_layout_reference.py` | Python: the rules, readable | its own tests (a layout with one of everything; the repository's XIBs) |

**The file name:** FutureBasic compiles a `.xib` resource into a nib, which has no XML left to read. So the web app
carries the same XIB under the name `.webxib`; `WebLoadLayout` also reads a `.xib` that was copied unchanged. The
layout tool saves both names.

### The layout tool (`src/WebToolkit/Layout Tool/Layout Tool.html`)

One HTML file, with no network use: open it in any browser.

- **Design.** Open a `.xib` or `.webxib` (or drop one), or start a new layout.
  - Add controls from the palette: heading, label, message band, text field, number field, password, text area, date
    picker, check box, radio group, pop-up, push button, table, box, separator, image. A control added while a box
    is selected goes inside the box.
  - Drag to move and drag the corner to resize, on a 4 pt grid. Arrow keys nudge (Shift: 10 pt); Delete removes;
    Cmd/Ctrl+D duplicates; Cmd/Ctrl+Z undoes.
  - The inspector edits the Identifier (checked for being unique and valid), text, style (body, muted, headings),
    placeholder, default button, pop-up items (`code=Title`), radio choices, table columns (`Attribute: Title`),
    box title, the frame, hidden and disabled.
- **Web Preview.** The page as the web app will show it, with `web.css`: Desktop or Phone width, any theme.
- **FB Code.** The functions for the layout's buttons, tables and forms; `BuildPage` with `WebLoadLayout` and the
  `WebOn` lines; the `WebFormBind` / `WebBindField` lines to fill in.
- **Save .xib** (Interface Builder, a desktop app) and **Save .webxib** (the web app's Resources).
  - An opened XIB keeps everything the tool does not edit, so Interface Builder still opens it.
  - XIBs the tool writes use Interface Builder's own element forms, the same as App Builder's XIB generator.

The Orders example is laid out this way: `CustomerPanel.webxib`, `OrderPanel.webxib` and `ItemPanel.webxib`, each a
table beside a form, bound in `Pages.incl`.

**Next (BACKLOG):**
- App Builder opens the layout tool on an entity's Form (in a web view, saving into the project);
- the web target generates `.webxib` files from the generated Form XIBs;
- tab views and split views.

## Verification

- **Here** (`tools/run_tests.sh`):
  - fblint on every file (CR line endings, typed fns, keywords, gated NSLog, the toolbox names);
  - the FastCGI core, compiled and run behind nginx (`tools/check_fastcgi_core.py`, which also checks that the
    module's core is the tested one);
  - the copies identical in the module, the template and the example;
  - `tools/web_layout_reference.py --test`, `tools/check_web_layout.py` (the Objective-C, compiled with GNUstep),
    `tools/check_layout_tool.py` (the tool in Chromium: preview = reference on 16 XIBs, editing, undo, saving, FB code);
  - `tools/web_toolkit_reference.py --test`: 30 checks of `web.js` and the protocol in headless Chromium - AJAX
    without reloads, order, values, every event kind, append / redraw / remove, focus, enabled, theme, escaping, the
    lifecycle (shown first / again, hidden with an auto-save, visible, leaving by beacon), the unsaved-changes guard,
    a forged event refused, an ended session restarting, no inline script.
- **On a Mac (pending):**
  1. Build the template and the example in FB.
  2. Start nginx with the project's `nginx.conf` and open http://127.0.0.1:8088/.
  3. Check that FB copies the `.webxib` resources unchanged (the page shows three panels; if not, the log says
     "no layout ...").
  4. Work through the example: a refused credit limit, Ship Today, two browsers, a reload, a switched tab saving the
     Item form.
  5. Open `src/WebToolkit/Layout Tool/Layout Tool.html` in Safari; open `CustomerPanel.webxib`; move a field; save;
     open the saved `.xib` in Xcode (Interface Builder).
  6. Send the Build Log and anything odd.
