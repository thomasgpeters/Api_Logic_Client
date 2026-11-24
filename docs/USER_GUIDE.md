# Imagery LogicBank Studio for FutureBasic — User Guide

*Turn a data model into a native Mac app with business rules, written in FutureBasic.*

![Architecture: a SQLite database or an API Logic Server project goes through the generator into the project workspace and out as a FutureBasic project; FutureBasic builds the Mac app, which enforces the business rules on every save](design/architecture.svg)

## Contents

1. [What it does](#1-what-it-does)
2. [What you need](#2-what-you-need)
3. [Getting started](#3-getting-started)
4. [Creating a project](#4-creating-a-project)
5. [The workspace and your project's files](#5-the-workspace-and-your-projects-files)
6. [Entity definitions: reviewing and adjusting](#6-entity-definitions-reviewing-and-adjusting)
7. [Project settings](#7-project-settings)
8. [Generating the app](#8-generating-the-app)
9. [Screens: FutureBasic's nib keywords](#9-screens-futurebasics-nib-keywords)
10. [Business rules](#10-business-rules)
11. [Importing and exporting ALS rules](#11-importing-and-exporting-als-rules-declare_logicpy)
12. [Making the generated app your own](#12-making-the-generated-app-your-own)
13. [Opening projects again](#13-opening-projects-again)
14. [Checking your work](#14-checking-your-work)
15. [Troubleshooting](#15-troubleshooting)
16. [Menus and keyboard shortcuts](#16-menus-and-keyboard-shortcuts)
17. [What is not built yet](#17-what-is-not-built-yet)

---

## 1. What it does

Imagery LogicBank Studio for FutureBasic reads a **data model** — the tables, columns, keys
and relationships of a SQLite database, or the model of an
[API Logic Server](https://apilogicserver.github.io/Docs/) (ALS) project — and generates a
complete **FutureBasic project** for it:

- a **Form** and a **List** screen part (XIB) for every entity, using macOS system colours so
  light and dark mode work without extra code;
- **binding code** that moves a record into a Form and back, and records into a List;
- a **data runtime** that reads and writes the project's SQLite database;
- **LogicBank for FutureBasic**, a rules engine that enforces your **business rules** — totals,
  formulas, checks, copies, what happens on delete — on every save, inside one transaction;
- the **project** itself, built from a template: groups, a short main program, and starting files
  for your own code.

You keep editing the generated app in FutureBasic. Everything the generator writes is plain,
readable FB; your own code lives in files that regeneration never touches.

## 2. What you need

| | |
|---|---|
| A Mac | with FutureBasic's requirements |
| [FutureBasic](https://www.brilorsoftware.com/fb/) 7.1.x | to build the generator and the apps it makes |
| Xcode's command-line tools | FutureBasic needs them to compile; they also provide `python3`, which the rules tools use |
| A data model | a SQLite database file (`.sqlite`, `.db`, `.sqlite3`) — or an ALS project's `/metadata` |

## 3. Getting started

1. Open `src/Generator/Api Logic Client.fbeproj` in the FutureBasic editor and build it.
   (The project file keeps its old name for now; the app shows its new one.)
2. The window opens on the **Welcome** page: **Create Project**, **Open Project…**, and your
   **Recent Projects** (double-click one to open it).

The window resizes freely (down to 1000 × 620). The entity list runs down the left; the page
beside it changes as you work.

## 4. Creating a project

**Create Project** opens the **New Project** page.

1. Click **Choose…** and pick your SQLite database. The page shows what it found:
   *"14 tables, 2 views: Category, Customer, Employee, …"*.
2. The **Project Name** fills in from the file name; change it if you like.
3. Click **Create** (or press Return).

The database is **copied into the project** (`Database/` in the project folder, together with
its `-wal` and `-shm` files when present), and the project works from that copy from now on —
the original is never changed. The entity list fills in, and clicking an entity shows its
definitions.

If a project with that name already exists, you are asked whether to **open it** instead.

*Working with a running API Logic Server instead?* **API Logic Server instead…** on the New
Project page opens the server form (base URL, user name, password). *Model → Open Metadata
JSON…* (⌘J) reads a saved `/metadata?include=attributes` response.

## 5. The workspace and your project's files

Everything lives in your Application Support folder — *Model → Show Workspace in Finder*
opens it (`~/Library` is hidden in Finder):

```
~/Library/Application Support/Api_Logic_Client/
├── Recent Projects.json           the Welcome page's list
└── workspace/
    └── <name> Project/            one folder per project — back it up, and you have it all
        ├── Project.json           name, model source, base URL, user name, About text
        ├── Design.json            your adjustments to the entity definitions
        ├── Rules.json             the project's business rules (Rules page, rules bridge)
        ├── Database/<db>.sqlite   the project's own copy of the database
        └── FBapp/                 the generated FutureBasic project
```

Passwords and tokens are never written to these files.

## 6. Entity definitions: reviewing and adjusting

Click an entity in the list. Its **attribute table** shows, for every column:

| Column | Meaning | You can change it |
|---|---|---|
| Name | the column in the database | |
| **Title** | the field label on the Form and the column heading in the List | ✓ |
| Data Type | the database type | |
| **FB Type** | the FutureBasic type the generator recommends | ✓ |
| Size | text length or numeric size | |
| Key | primary key and how it is made (identity, autoincrement, assigned) | |
| Required / Default | from the database | |
| **Form Control** | text field, checkbox, date picker, … | ✓ |
| **Form Width** / **List Width** | in points | ✓ |
| Adjusted | ✓ when you changed something | |

Edit a cell and press Return: the change is saved to `Design.json` at once and kept every time
you regenerate. Clear a cell to go back to the recommendation.

## 7. Project settings

*Model → Project Settings…* (⌘;) — what is deployed with the generated app beyond the model.
- **About text**, up to 250 characters (a counter shows how many are left). It appears in the
  generated app's **About** box, under its name, icon and version.
- **Branding** for the generated app's header and footer:
  - **Logo** — paste (⌘V) or drag a picture into the well. It is kept as
    `<project>/Branding/logo.png` and deployed as `FBapp/AppLogo.png`. Select it and press Delete to remove it.
  - **Tag-line** — a short description under the app's name, up to 80 characters.
  - **Copyright** — the footer's text (`© <app name>` when empty).

**Done** saves everything in `Project.json`.

### 7.1 The model diagram

*Model → Show Model Diagram* (⇧⌘D) opens the project's **entity-relationship diagram** in your
browser (`<project>/Model ERD.html`): every entity, its attributes and keys, every relationship
(crow's foot = many; dashed = optional), and the **business rules** drawn where they act —
ƒ formula, Σ sum, # count, ⇣ copy, ! parent required on the attributes; ✓ constraint and ⚡ events
in the header; ⊘ delete action on the relationship.

Drag an entity by its header; the triangle opens and closes it. Click an entity to see its
relationships, rules and attributes in the side panel. Scroll to zoom, drag the background to
move, *Find* an entity or attribute, switch the theme, and **Export SVG** to keep a copy.
Details: `features/MODEL_DIAGRAM_FEATURE.md`.

## 8. Generating the app

From the *Model* menu:

**On first launch** (and whenever they are missing), the Studio asks for your
**Api_Logic_Client folder** (the repository) and copies its `src/Runtime` and `src/Templates` into the
workspace (`workspace/Runtime`, `workspace/Templates`): every generated app is made from those.
After pulling a newer version, choose *Model → Update Runtime and Templates…* to copy them again.


| Command | Key | Writes into `FBapp/` |
|---|---|---|
| Generate XIBs | ⇧⌘X | every entity's `<Entity>Form.xib` and `<Entity>List.xib`, and `Model Tags.incl` |
| Generate XIB for Selected Entity | ⌘E | the selected entity's two parts |
| Generate Binding Code | ⌘B | `<Entity> Binding.incl` for every entity |
| Generate App | ⌘G | all of the above, plus the project, the main program, `Model.json`, `Credits.rtf`, the runtime and the starting files |

Then open **`FBapp/<name>.fbeproj`** in FutureBasic and build it. The project is laid out in groups:

| Group | Holds | Regenerated? |
|---|---|---|
| Runtime | the data runtime, the query builder, LogicBank for FutureBasic, the ALS client | yes — copied fresh |
| Model · Bindings · Resources | `Model Tags.incl`, `<Entity> Binding.incl`, `Model.json`, the XIBs, `Credits.rtf` | yes |
| Rules | `Studio Rules.incl` (generated) and **`Rules.incl` (yours)** | `Rules.incl`: never |
| Pages | `App Pages.incl`: a page per entity (its List and Form), its navigation button | yes |
| Controller · View | **`EventHandlers.incl`, `Theme.incl`, `Menus.incl`, `Windows.incl` (yours)** | never |
| Main | `<name>.main`: settings, handlers, start-up | yes |

`README.md` in `FBapp/` is a developer's tour of the generated project, file by file; every
generated file starts with a comment saying what it does and whether it is regenerated.

### 8.1 The app's look

Every generated app has the same frame (`App Shell.incl`):

- a **dark blue navigation bar** on the left, with a white, bold button and an icon per entity;
- a **header** with your logo, the app's name and tag-line, and on the right the **theme menu**
  (System / Light / Dark) and **Log In** (connect it to your sign-in in `EventHandlers.incl`, `DoLogin`);
- a **footer** with the copyright, a status line, and the page actions **New**, **Save**,
  **Delete** and **Refresh** (also in the *Records* menu: ⌘N, ⌘S, ⌘R);
- the **page**: the entity's list on top, its form below — choose a row to see it in the form.

Change the colours in `Theme.incl` (yours). Add pages of your own in `Windows.incl`, after
`AppPagesBuild` (the file shows how).

Choosing a row shows it in the form. **Save** writes the form through the business rules: a
refused save changes nothing and shows the rule's message. **New** empties the form; Save then
adds the record. **Delete** asks first; the rules decide what happens to related records.

### 8.2 Editions

The app is generated as the **Lite** edition: free and open source. It opens the project's SQLite
database itself and runs the business rules inside the app. A paid **Enterprise** edition, a
three-tier app that talks to an API Logic Server, is planned (`design/Editions and Licensing.md`).

A project whose model was read from an API Logic Server (*Open Metadata JSON*, or the ALS form)
can generate XIBs, bindings and the model diagram, but not a Lite app: create the project from the
server's SQLite database instead (*New Project*), which gives the same model.

When it runs, the app opens the project's database (`Data: opened …` in the NSLog window) and
activates its rules (`Logic: rules active for N entities`).

## 9. Screens: FutureBasic's nib keywords

Every screen part the generator writes is a **XIB** — Interface Builder's file, which you can
open and change in Xcode. FutureBasic compiles the XIBs listed in the project to nibs when it
builds, and your FB code puts them on screen with its **nib keywords**. These are the calls to
look for — and to use — in the generated project's `Windows.incl` and in your own code:

| Keyword | What it loads | FutureBasic reference |
|---|---|---|
| `nibwindow tag, nibName [, identifier]` | a window | [nibwindow](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibwindow.html) |
| `nibview tag, nibName [, identifier [, origin [, superviewTag]]]` | a view — a Form or List part — into the window, or into another view | [nibview](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibview.html) |
| `nibtoolbar tag, nibName` | a toolbar | [nibtoolbar](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibtoolbar.html) |
| `nibmenu nibName` | a menu | [nibmenu](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibmenu.html) |
| `nibpopover tag, nibName` | a popover | [nibpopover](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibpopover.html) |

(The same pages are in FutureBasic's own help, and in the FutureBasic_Documentation repository
under `FBHelp/Resources/English.lproj/pgs/`.)

**In the generated app.** `Windows.incl` (yours, written once) builds the window, then loads
each entity's Form part from its XIB with `nibview`, hidden until the entity is chosen:

```
void local fn BuildWindows( title as CFStringRef )
long x = fn ALSPartX
fn ALSBuildWindow( title )
// each entity's Form part, from its generated XIB - hidden until the entity is selected
nibview _CustomerView, @"CustomerForm", , ( x, _alsButtonBarH )
ViewSetHidden( _CustomerView, YES )
nibview _OrderView, @"OrderForm", , ( x, _alsButtonBarH )
ViewSetHidden( _OrderView, YES )
...
end fn
```

**In the generator itself** — the same keywords, one part per XIB:

```
nibwindow _window, @"MainWindow"                    // Windows.incl: BuildWindow
nibview _welcomeView, @"WelcomeView",, ( x, y )      // BuildSubViews: each page
nibview _newProjectView, @"NewProjectView",, ( x, y )
nibtoolbar _mainToolbar, @"Toolbar"
```

**What to know when you use them:**

- **The tag you pass becomes the view's tag.** The controls inside keep the tags the XIB gives
  them — the generated ones are named in `Model Tags.incl` (`_CustomerView`, `_CustomerCompanyName`,
  …), so your code reads and fills them with `ControlStringValue`, `ControlSetObjectValue` and
  the `<Entity> Binding.incl` functions. A tag must not be used by another control in the window.
- **`nibName` is the XIB's name without `.xib`** (`@"CustomerForm"`), and the XIB must be listed
  as a resource in the project (the generator lists every part it writes).
- **`superviewTag`** puts the view inside another one — a tab, a pane, a box — instead of the
  window's content view. This is how parts can be embedded, for example a List part in a tab of
  its parent's Form.
- **`identifier`** picks one view out of a XIB that holds several (the first view is loaded
  without it).
- **`origin`** is in the window's coordinates, measured from the **bottom left**.
- **Load once, then show and hide** (`ViewSetHidden`): every load makes new copies of the views.
  Change a view right after its `nib…` call — size it, fill it, hide it — as the generator does.
- **Changing a part's layout:** open its XIB in Xcode. A regenerated part is rewritten, so
  change the design (the entity definitions, §6) for anything the generator decides, and keep
  hand-made screens in XIBs of your own.

More about XIBs — what is inside one, frames and resizing, checking one with `ibtool` — is in
`reference/XIB Reference.md`.

## 10. Business rules

Business rules are what keeps the data right whoever changes it: an order's total is the sum
of its lines, a customer's balance may not exceed the credit limit, a line takes its price from
the product. You **declare** them once; **LogicBank for FutureBasic** enforces them on every
save.

### 10.1 Where rules live

- **`Rules.incl`** in the generated project is yours: write rules in FB in its `DeclareRules`
  function. It is created once and never overwritten.
- **`Studio Rules.incl`** is generated from the project's `Rules.json` every time you
  *Generate App* (the rules imported from ALS, §11, and later the Rules page) — don't edit it;
  it is rewritten. Without a `Rules.json` it is an empty `DeclareStudioRules`.
- The app's main program calls both, then `LogicActivate`.

### 10.2 Saving through the rules

In your own code, save records with the engine instead of writing them directly:

```
if ( fn LogicInsert( @"OrderDetail", aRecord ) == NO ) then alert 1, NSAlertStyleWarning, fn LogicMessage, @"", @[@"OK"], NO
fn LogicUpdate( @"Order", aRecord, NULL )        // NULL: the record's own key
fn LogicUpsert( @"OrderDetail", aRecord )         // update when the key exists, else insert
fn LogicDelete( @"Customer", @{ @"Id":@"ALFKI" } )
```

A record is a mutable dictionary of column → value. Each save is **one transaction**: if any
rule refuses it, nothing is changed — not the row, not the totals it would have updated — and
`LogicMessage` says why.

### 10.3 The rules you can declare

A rule function takes the row being saved (`logicRow`) and reads it with
`LogicDouble`, `LogicString`, `LogicValue`, `LogicIsEmpty`, `LogicOldValue`, `LogicChanged`,
and for its parent `LogicParentDouble` / `LogicParentString` / `LogicParentValue`.

**Formula** — an attribute computed from the row (and its parents):

```
// OrderDetail.Amount = Quantity * UnitPrice
local fn OrderDetailAmount( logicRow as LogicRowRef ) as CFTypeRef
end fn = fn NumberWithDouble( fn LogicDouble( logicRow, @"Quantity" ) * fn LogicDouble( logicRow, @"UnitPrice" ) )

fn LogicFormula( @"OrderDetail", @"Amount", @fn OrderDetailAmount, @[ @"Quantity", @"UnitPrice" ] )
```

The list names what the formula reads: formulas run in dependency order, and on an update a
formula whose inputs did not change is skipped. A parent's attribute is named `@"Order.ShippedDate"`;
when it changes on the parent, the children recompute.

**Constraint** — a condition that must hold, with a message (`{Attr}` shows the row's value):

```
local fn CustomerCreditCheck( logicRow as LogicRowRef ) as BOOL
end fn = ( fn LogicDouble( logicRow, @"Balance" ) <= fn LogicDouble( logicRow, @"CreditLimit" ) )

fn LogicConstraint( @"Customer", @fn CustomerCreditCheck, @"Balance {Balance} exceeds credit limit {CreditLimit}" )
```

**Sum and count** — a parent's total over a child list (the model's `<Child>List` names), with an
optional condition on the child:

```
local fn OrderIsUnshipped( logicRow as LogicRowRef ) as BOOL
end fn = fn LogicIsEmpty( logicRow, @"ShippedDate" )

fn LogicSum( @"Order", @"AmountTotal", @"OrderDetailList", @"Amount", NULL )
fn LogicSum( @"Customer", @"Balance", @"OrderList", @"AmountTotal", @fn OrderIsUnshipped )
fn LogicCount( @"Customer", @"UnpaidOrderCount", @"OrderList", @fn OrderIsUnshipped )
```

Totals are **adjusted**, never recounted: adding a line adds its amount, changing it adds the
difference, moving an order to another customer takes it off one and adds it to the other. The
parent is then saved through its own rules — so adding a line updates the order's total, the
customer's balance, and checks the credit limit, all in one save. Totals belong to the rules: a
new row starts them at 0, and a save from your code cannot overwrite them.

**Copy** — a parent's value, taken on insert (and when the row moves to another parent), not kept
in step afterwards:

```
fn LogicCopy( @"OrderDetail", @"UnitPrice", @"Product", @"UnitPrice" )
```

**Parent check** — a filled-in foreign key must find its parent:

```
fn LogicParentCheck( @"OrderDetail", @"Product", @"Product {ProductId} does not exist" )
```

**Delete action** — what deleting a parent does to its children: `prevent` (refuse while there
are children), `cascade` (delete them too, through their rules), `nullify` (empty their foreign key):

```
fn LogicDeleteAction( @"Customer", @"OrderList", @"prevent", @"Customer {Id} still has orders" )
fn LogicDeleteAction( @"Order", @"OrderDetailList", @"cascade", NULL )
```

**Events** — your code at a defined moment:

```
void local fn OrderShipped( logicRow as LogicRowRef )
// send a mail, write a log line, ...
end fn

fn LogicRowEvent( @"Order", @fn OrderAudit )        // during the save; must not change the row
fn LogicCommitEvent( @"Order", @fn OrderShipped )   // after the save has committed, once per row
```

A row event that changes the row fails the save (the change would bypass the rules — use a
formula or a copy). Commit events never run for a save that was rolled back.

### 10.4 What happens on a save

```
insert   copy → parent check → formulas → adjust parents → constraints → row events → write
update   the same (formulas whose inputs did not change are skipped) → write → children follow
delete   delete actions → adjust parents → row events → write
commit   commit events, once per row
```

`LogicActivate` checks every rule against the model at start-up — names, child lists, parent
roles, formulas that depend on each other in a circle — and refuses to start the rules (with an
alert, details in NSLog) if something is wrong. With `isLoggingOn`, the NSLog window shows each
rule as it fires, indented by how far the save has chained.

## 11. Importing and exporting ALS rules (`declare_logic.py`)

> **For now:** the Studio contains no Python, so these two commands say "coming" until they are
> rewritten in FutureBasic, and *Generate App* writes an empty `Studio Rules.incl`: put the app's
> rules in `Rules.incl`. The Terminal commands below work today, from this repository's folder.

An ALS project's rules (LogicBank, in Python) can come in, and go back out:

- *Model → Import Rules from declare_logic.py…* — choose the ALS project's `logic/declare_logic.py`.
  The rules go into the project's `Rules.json`; a message says how many came in and how many
  were switched off (see below). *Generate App* then writes them into `Studio Rules.incl`.
- *Model → Export Rules to declare_logic.py…* — writes the project's rules as LogicBank rules.

They will be FutureBasic inside the Studio. The reference is `tools/rules_bridge.py`, which you
can run from Terminal (in this repository's folder):

```bash
python3 tools/rules_bridge.py import path/to/logic/declare_logic.py --model "<project>/Database/<db>.sqlite" --rules "<project>/Rules.json"
```

```bash
python3 tools/rules_bridge.py generate --rules "<project>/Rules.json" --model "<project>/Database/<db>.sqlite" --out "<project>/FBapp/Studio Rules.incl"
```

```bash
python3 tools/rules_bridge.py export --rules "<project>/Rules.json" --model "<project>/Database/<db>.sqlite" --out declare_logic.py
```

- **Import** translates each rule's `lambda row: …` into FB: `row.Quantity * row.UnitPrice`,
  `row.ShippedDate is None`, `row.Order.ShippedDate`, comparisons, `and` / `or` / `not`. Child
  lists and parent roles are found from the model.
- A rule it **cannot translate safely** — a Python function, a conditional expression, an
  event — arrives **switched off**, with its Python kept beside it in `Rules.json` to rewrite in FB.
  Nothing is lost, and nothing is guessed. The import prints which ones.
- **Check** first if you edited `Rules.json` by hand: `python3 tools/rules_bridge.py check --rules … --model …`.
- **Export** writes an unchanged imported rule exactly as it came, and translates edited ones from FB.
- `--help` shows every option.

## 12. Making the generated app your own

- **Yours, never overwritten:** `EventHandlers.incl` (what happens on clicks and menus),
  `Menus.incl`, `Windows.incl` (the window and its pages), `Theme.incl` (the colours), `Rules.incl`, and the
  project's build settings. Delete one to get a fresh copy at the next *Generate App*.
- **Regenerated:** `App Pages.incl`, `README.md`, the XIBs, bindings, `Model.json`, `Model Tags.incl`, `Studio Rules.incl`, the
  runtime and the main program — change the model, your adjustments or the rules instead.
- `Model Tags.incl` names every view and control tag, for your own code.

## 13. Opening projects again

- **Welcome page:** double-click a recent project. *Model → Recent Projects* returns to it;
  *Clear Recent Projects* empties the list.
- **Open Project…** (⇧⌘O): choose a project's `Project.json` in the workspace.
- If the project's database has moved, you are asked to locate it; the new place is remembered.

## 14. Checking your work

- **Without a Mac** (this repository): `tools/run_tests.sh` runs every check — the FB coding rules,
  the rules engine's 70 scenarios, the proof that every rule is needed, the rules bridge.
- **On a Mac:** `python3 tools/make_logic_test.py <db.sqlite> ~/Desktop/LogicTest`, then build and
  run `~/Desktop/LogicTest/Logic Test.fbeproj` — the same 70 scenarios in FutureBasic.
- **XIBs:** `xcrun ibtool --errors --warnings --notices --output-format human-readable-text File.xib`.

`TESTING.md` describes every test.

## 15. Troubleshooting

| What you see | What to do |
|---|---|
| FutureBasic quits (crashes) when you build | a file listed in the project is missing beside it — FB's own headers (`NSLog.incl`, `Tlbx ….incl`) must be `include`d from a source file, not listed in the project (`tools/fblint.py` checks this). Also check *Build Settings*: the SDK must be one your Xcode has (see `src/CleanApp`). |
| Translator or compiler errors after pulling | the FB editor rewrites files when it opens them; `git stash`, pull again, build. If the errors name lines that look already fixed, your copy is behind. |
| `Data: the database is missing` | the project's `Database/` copy is gone; open the project and locate the database when asked. |
| `The business rules are not active` | `LogicActivate` refused the rules: the alert and NSLog name the rule and attribute. |
| A save is refused | `fn LogicMessage` has the reason (a constraint's message, a parent check, a delete that is prevented). |
| `A row event changed …` | an event tried to change the row; use a formula or a copy rule instead. |
| `python3: command not found` | install Xcode's command-line tools (`xcode-select --install`). |
| `statement is NULL` in NSLog | a query does not match the database's tables; the log line shows the SQL. |

Paste a Build Log or NSLog lines into a session when something is unclear.

## 16. Menus and keyboard shortcuts

| Menu | Command | Key |
|---|---|---|
| File | Close | ⌘W |
| Edit | Undo · Cut · Copy · Paste · Select All | ⌘Z ⌘X ⌘C ⌘V ⌘A |
| Model | Open Project… | ⇧⌘O |
| | Recent Projects · Clear Recent Projects | |
| | Project Settings… | ⌘; |
| | Open SQLite Database… | ⌘D |
| | Open Metadata JSON… | ⌘J |
| | Generate XIBs | ⇧⌘X |
| | Generate XIB for Selected Entity | ⌘E |
| | Generate Binding Code | ⌘B |
| | Generate App | ⌘G |
| | Import Rules from declare_logic.py… · Export Rules to declare_logic.py… | |
| | Show Workspace in Finder | |
| | Show Model Diagram | ⇧⌘D |
| | Update Runtime and Templates… | |

*Preferences…* (⌘,) does nothing yet.

## 17. What is not built yet

- **The Rules page** in the generator: the rules of `Rules.json` in a list, an editor with the
  model's entities and attributes to pick from, and checking. Until then, write rules in
  `Rules.incl`, or import them (§11) and edit `Rules.json`.
- **The app shell** for SQLite projects: an entity navigator, Lists and Forms reading and saving
  through the rules engine (the parts, bindings, data runtime and rules are ready).
- **Renaming** the project file, the app bundle and the Application Support folder to the
  product's name.

See `ROADMAP.md` for the plan and `BACKLOG.md` for every open item.

---

© 2026 Imagery Business Systems, LLC.
