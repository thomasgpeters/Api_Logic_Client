# Studio review — what works, what doesn't, and the proposal

Started 2026-11-24 at the author's request: "the toolbar … does not seem to work. We are going to
have to go through the app and see what works, and what doesn't." This page is the inventory
(from the source, before any change) and a proposal. The author marks the open questions; the
changes follow in small steps, each built and tried on a Mac.

## 1. Inventory

Status: **works** (wired and guarded), **unguarded** (works, but runs with no project and
explains itself in an alert instead of being disabled), **dead** (does nothing), **debug** (a
developer's tool, not a user's).

### Toolbar (`Toolbar.xib`, loaded with `nibtoolbar _mainToolbar`)

| Item | Tag | Status | Why |
|---|---|---|---|
| Project (hammer) | 205 | **dead** | nothing handles `_toolbarItemClick`; tag 205 is also the ALS form's Cancel button |
| Object (puzzle piece) | 303 | **dead** | as above; tag 303 is also the Project Settings tag-line field |
| Generate (arrow) | 500 | **dead** | as above |
| Settings (gear) | 501 | **dead** | as above |
| Print | system | **dead** | the Studio has nothing to print |
| Colors, Fonts | system | in the customise palette only | not used by the Studio |

### Menus (`Menus.incl`, handled in `EventHandlers.incl` `DoMenu`)

| Menu | Item | Key | Status |
|---|---|---|---|
| Studio | Preferences… | ⌘, | **dead** (no handler; there are no preferences yet) |
| File | Close | ⌘W | works (closes the window, which quits the Studio) |
| Edit | Undo, Cut, Copy, Paste, Select All | | works (FB's edit menu) |
| Model | Open Project… | ⇧⌘O | works |
| | Recent Projects | | works (shows the Welcome view) |
| | Clear Recent Projects | | works |
| | Project Settings… | ⌘; | unguarded |
| | Delete Project… | | unguarded |
| | Open SQLite Database… | ⌘D | works |
| | Open Metadata JSON… | ⌘J | works |
| | Generate XIBs | ⇧⌘X | unguarded |
| | Generate XIB for Selected Entity | ⌘E | unguarded |
| | Generate Binding Code | ⌘B | unguarded |
| | Generate App | ⌘G | unguarded |
| | Import Rules from declare_logic.py… | | says "coming" (port to FB in the backlog) |
| | Export Rules to declare_logic.py… | | says "coming" |
| | Show Workspace in Finder | | works (the project's folder when one is open) |
| | Show Model Diagram | ⇧⌘D | unguarded |
| | Update Runtime and Templates… | | works |
| | Open One Xib | ⌘O | **debug** (opens a XIB as XML; logs it) |
| Help | (empty) | | **dead** |

There is no **New Project** menu item (only the Welcome view's button) and no **Close Project**.

### Views and their controls

| View | Control | Status |
|---|---|---|
| Main window | Objects list (left) | works: selecting an entity shows its definitions |
| | + / − under the Objects list (tag 106) | **dead** (− disabled, nothing handles either) |
| | Heading ("Northwind Project") | works |
| Welcome | Create Project, Open Project…, Recent Projects (double-click) | works |
| New Project | Choose…, Create, Cancel, Use an API Logic Server… | works |
| ALS form (ProjectCreateView) | Create, Cancel | Create works; **Cancel is dead** (tag 205, unhandled) |
| Entity definitions | Control, Form layout, Icon popups; attribute table (editable cells) | works; Form layout reported to revert (being traced) |
| Project Settings | About text, app icon, symbol, tag-line, copyright, Done | works |

No list has a right-click (context) menu. Nothing is ever disabled: commands that need a project
or a selected entity run and then explain in an alert.

## 2. Proposal

### 2.1 Menu bar

Grouped by what the developer is working on: the project, its model, what it generates.

| Menu | Items |
|---|---|
| **Imagery LogicBank Studio** | About, (Preferences… when there are preferences), Hide, Quit |
| **Project** | New Project… ⌘N · Open Project… ⌘O · Recent Projects · Clear Recent Projects — Close Project ⇧⌘W · Project Settings… ⌘; · Show Project in Finder · Delete Project… |
| **Edit** | FB's standard edit menu |
| **Model** | Open SQLite Database… ⌘D · Open API Logic Server Metadata… ⌘J — Show Model Diagram ⇧⌘D — Import Rules… · Export Rules… |
| **Generate** | Generate App ⌘G — Generate XIBs ⇧⌘X · Generate XIB for *Customer* ⌘E (names the selected entity) · Generate Binding Code ⌘B — Show Generated App in Finder — Update Runtime and Templates… |
| **Window** | Minimize ⌘M · Zoom · Close ⌘W |
| **Help** | Imagery LogicBank Studio Help (the user guide) · Show Workspace in Finder |

"Open One Xib" leaves the menus (a developer's tool; it can stay behind a debug flag).

### 2.2 What is enabled when

The Studio is in one of three states; every command is enabled only where it makes sense.

| Command | No project | Project open | + entity selected |
|---|---|---|---|
| New / Open Project, Recent, Open SQLite / Metadata | ✓ | ✓ | ✓ |
| Close Project, Project Settings, Show Project in Finder, Delete Project | | ✓ | ✓ |
| Show Model Diagram, Import / Export Rules | | ✓ | ✓ |
| Generate App, Generate XIBs, Generate Binding Code, Show Generated App | | ✓ | ✓ |
| Generate XIB for *entity* | | | ✓ |
| Toolbar: Generate, Settings, Entities | | ✓ | ✓ |

One function (`StudioUpdateCommands`) sets menus and toolbar from the state, called whenever it
changes: a project opened, closed or deleted, an entity selected. (Delete Project from the
Welcome view's Recent Projects list stays available there, through its context menu.)

### 2.3 Toolbar

| Item | Does | Enabled |
|---|---|---|
| **Projects** (house) | the Welcome view: New, Open, Recent Projects | always |
| **Entities** (table) | the entity definitions of the open project | project open |
| **Diagram** (rectangle.connected.to.line.below) | Show Model Diagram | project open |
| **Generate** (hammer) | Generate App | project open |
| **Settings** (gear) | Project Settings | project open |

Tags get a range of their own (600–609) so they never collide with a view's controls; Print goes.

### 2.4 Context menus (right-click)

| Where | Items |
|---|---|
| Objects list, on an entity | Generate XIB for *entity* · Show in Model Diagram · Reset *entity*'s Design… |
| Attribute table, on an attribute | Control ▸ (the Control popup's choices) · Hide on Form / Show on Form · Reset Adjustments |
| Recent Projects, on a project | Open · Show in Finder · Remove from List · Delete Project… |

### 2.5 Small fixes found on the way

- The ALS form's Cancel button: handle it (back to the Welcome view) — and give it its own tag.
- The + / − under the Objects list: remove (entities come from the model, not from the Studio).
- File › Close quits the Studio (the main window is the only window): Close Project instead,
  and ⌘W only closes the window.

## 3. Questions for the author

1. The toolbar's **Project** and **Object** items: what did you mean them to do? The proposal
   above makes them Projects (the Welcome view) and Entities (the definitions).
2. Keep **Open One Xib** behind a debug flag, or remove it?
3. **Help**: open `USER_GUIDE.md` in the browser (from the repository), or a bundled copy?
4. Any command missing from the proposal?

## 4. Steps (each built and tried before the next)

1. Menus regrouped (2.1); toolbar tags and handler (2.3); `StudioUpdateCommands` (2.2).
2. Context menus (2.4).
3. Small fixes (2.5); this page's inventory updated to "works" row by row.
