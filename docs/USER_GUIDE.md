# App Builder for FutureBasic: User Guide

*Turn your data model into a native Mac app, with business rules, written in FutureBasic.*

![Architecture: a SQLite database or an API Logic Server project goes through the generator into the project workspace and out as a FutureBasic project; FutureBasic builds the Mac app, which enforces the business rules on every save](design/architecture.svg)

## Contents

1. [What it does](#1-what-it-does)
2. [What you need](#2-what-you-need)
3. [Getting started](#3-getting-started)
4. [Creating a project](#4-creating-a-project)
5. [Where your files live](#5-where-your-files-live)
6. [Entity definitions](#6-entity-definitions)
7. [Project settings](#7-project-settings)
8. [Generating the app](#8-generating-the-app)
9. [Screens: FutureBasic's nib keywords](#9-screens-futurebasics-nib-keywords)
10. [Business rules](#10-business-rules)
11. [Importing and exporting ALS rules](#11-importing-and-exporting-als-rules-declare_logicpy)
12. [Making the generated app your own](#12-making-the-generated-app-your-own)
13. [Opening projects again](#13-opening-projects-again)
14. [Checking your work](#14-checking-your-work)
15. [Troubleshooting](#15-troubleshooting)
16. [Menus, toolbar and keyboard shortcuts](#16-menus-toolbar-and-keyboard-shortcuts)
17. [The SQL Generator](#17-the-sql-generator)
18. [What is not built yet](#18-what-is-not-built-yet)

---

## 1. What it does

App Builder for FutureBasic reads a **data model** (the tables, columns, keys and relationships of
a SQLite database, or the model of an [API Logic Server](https://apilogicserver.github.io/Docs/)
project) and writes a complete **FutureBasic project** for it:

- a **Form** and a **List** screen part (XIB) for every entity, in macOS system colours, so light
  and dark mode work with no extra code;
- **binding code** that moves a record into a Form and back, and records into a List;
- a **data runtime** that reads and writes the project's SQLite database;
- **LogicBank for FutureBasic**, a rules engine that enforces your **business rules** (totals,
  formulas, checks, copies, what happens on delete) on every save, in one transaction;
- the **project** itself: groups, a short main program, and starting files for your own code.

You keep working on the app in FutureBasic. Everything the generator writes is plain, readable
FB, and your own code lives in files that regeneration never touches.

## 2. What you need

| | |
|---|---|
| A Mac | with FutureBasic's requirements (macOS 15 or later) |
| [FutureBasic](https://www.brilorsoftware.com/fb/) 7 | to build App Builder and the apps it makes |
| Xcode's command-line tools | FutureBasic compiles with them; they also provide `python3`, which the rules tools use |
| A data model | a SQLite database file (`.sqlite`, `.db`, `.sqlite3`), or an API Logic Server project |
| A licence | **Lite** is free: register on Imagery's App Builder page and enter the licence that comes by email. **Professional** adds API Logic Server projects and the rules exchange with Python. |

Without a licence, App Builder opens and you can look around; generating asks for one. The
licence lives in the App Builder menu: *Licence…*, *Enter Licence…*, *Upgrade to Professional…*,
*Manage Licence Online…* and *Remove Licence…*. It is kept in your Keychain and checked on your Mac,
with no network needed. A command your licence does not include shows "(Professional)" after its
title and explains when you choose it.

## 3. Getting started

1. Open `src/AppBuilder/Studio for FB.fbeproj` in the FutureBasic editor and build it. It builds
   *Studio for FB*, which calls itself App Builder for FutureBasic.
2. The window opens on the **Welcome** page: the Imagery logo and the product's name at the top,
   and below them a card with your **Recent Projects** (double-click one to open it),
   **Open Project…** and **Create Project**.

The window resizes freely, down to 1000 × 620. Once a project is open, its entity list runs down the left and the
page beside it changes as you work; until then, the Welcome page uses the whole window.

## 4. Creating a project

**Create Project** opens the **New Project** page.

1. Click **Choose…** and pick your SQLite database. The page shows what it found, for example
   *"14 tables, 2 views: Category, Customer, Employee, …"*.
2. The **Project Name** fills in from the file name. Change it if you like.
3. Click **Create** (or press Return).

The database is **copied into the project** (its `Database/` folder, with the `-wal` and `-shm`
files when present), and the project works from that copy from now on. Your original is never
changed. The entity list fills in; click an entity to see its definitions.

If a project with that name already exists, App Builder asks whether to **open it** instead.

### From an API Logic Server project (Professional)

*Project → New Project from API Logic Server…* (⇧⌘N), or **API Logic Server Project…** on the New
Project page, starts from the model API Logic Server generated (its resources, attributes, keys and
relationships) instead of a database. Point App Builder at the ALS project:

- **drop** its folder, or its `database/models.py`, on the drop zone;
- click **Folder…** or **Model File…** to choose it; or
- type or paste a path, or a **public GitHub repository's address**
  (`https://github.com/owner/repo`, or `…/tree/<branch>/<subfolder>`), then click **Read**.

The page shows what the model holds and where it came from, and fills in the Project Name. Enter
the **API Server** the generated app will talk to (`http://localhost:5656` by default) and click
**Create**. App Builder keeps a copy of the model in the project (`ALS Model/`), so the project
opens again without the original. It reads the model; it never runs it.

**A running server instead?** **From a Running Server…** on that page opens the server form (base
URL, user name, password). *Model → Open API Logic Server Metadata…* (⌘J) reads a saved
`/metadata?include=attributes` response. Neither gives the relationships.

## 5. Where your files live

Everything lives in your Application Support folder. *Help → Show Workspace in Finder* opens it
(`~/Library` is hidden in Finder):

```
~/Library/Application Support/App Builder for FutureBasic/
├── Recent Projects.json           the Welcome page's list
└── workspace/
    └── <name> Project/            one folder per project: back it up, and you have it all
        ├── Project.json           name, model source, base URL, user name, About text, branding
        ├── Design.json            your adjustments to the entity definitions
        ├── Rules.json             the project's business rules (rules bridge, Rules page)
        ├── Branding/logo.png      the app icon picture, when you add one
        ├── Database/<db>.sqlite   the project's own copy of the database
        └── FBapp/                 the generated FutureBasic project
```

Passwords and tokens are never written to these files; they go in your Keychain.

## 6. Entity definitions

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
| **Form Control** | Text field, Text area, Integer field, Decimal field, Date picker, Time picker, Date and time picker, Checkbox, **Radio buttons**, **Dropdown**, **Auto-complete**, **Read-only text**, **Hidden** | ✓ |
| **Values** | a value list for Radio buttons or a Dropdown (`Retail, Wholesale, Online`, or code = label pairs `R = Retail, W = Wholesale`); for a foreign key, what its Dropdown shows (`→ person.givenName`) | ✓ |
| **Form Width** / **List Width** | in points | ✓ |
| Adjusted | ✓ when you changed something | |

Edit a cell and press Return: the change is saved to `Design.json` straight away and kept every
time you regenerate. Clear a cell to go back to the recommendation.

Under the entity's summary is a row of three popups:

- **Control**: select an attribute in the table, then choose its control. The first item,
  *Recommended: …*, goes back to the generator's choice for the column's type (DATE a date picker,
  DATETIME and TIMESTAMP a date and time picker, TIME a time picker). You can also type a
  control's name in the Form Control cell.
- **Form layout**: how many columns of fields the Form has. *Automatic* gives 1 column up to 10
  fields, 2 up to 24, then 3; or choose 1, 2 or 3. Generate XIBs to see it.
- **Icon**: the SF Symbol on the entity's button in the app's navigation bar, with a preview
  beside the popup. *Icon: recommended* goes back to the generator's choice from the entity's name.

What each control does:

- **Dropdown**: a foreign key gets one by default. It lists the rows of the table it refers to,
  shows a readable column (its *name*, *title* or *description*, a column whose name contains
  "name", else its first text column) and stores the key. Type a value list in **Values** to offer
  those values instead; any attribute can have one, a type or status field for example. The list
  is written into the generated code. `Retail, Wholesale, Online` stores what it shows;
  `R = Retail, W = Wholesale, O = Online` stores the code (`R`) and shows the label (`Retail`).
  The first item is empty: no value. Beside a foreign key's Dropdown, an **info button** (ⓘ)
  shows the chosen record's details in a popover, for example an Order's Customer. It is dimmed
  until a record is chosen.
- **Auto-complete** (for a foreign key, or any attribute with a **Values** list): a text field that finds the related record, or the local value, as you type. The matches open in
  a list under the field (or above it, near the bottom of the window); choosing one shows its name and stores its key.
  When you choose it, a settings row appears under the Control popup: **Show** (the related record's field the user
  sees and types), **After 1, 2 or 3 letters**, **Up to 5, 8, 12 or 20 results**. With a Values list the matches come
  from it (labels shown, codes stored), and **Allow other values** keeps what the user types when it is not in the
  list, and offers it from then on, after a restart too. Generate to apply.
- **Radio buttons**: one per value of the **Values** list, up to 8 (with more, or with no list,
  the attribute gets a Dropdown). Code = label pairs work the same way: the label is the button's
  title, the code is stored. Side by side when they fit, else one under the other.
- **Checkbox**: for yes / no columns (BOOLEAN, BIT), stored as 1 or 0.
- **Read-only text** shows a value without letting the user change it. A key the database makes
  for you (an `INTEGER PRIMARY KEY`, with or without `AUTOINCREMENT`) is read-only by default; a
  key you type yourself, such as a customer code, stays a text field.
- **Hidden** leaves the attribute off the Form and the List. It stays in the database, and a save
  leaves its value as it was.

Dates are stored as `1996-07-04`, times as `14:30:00`, and dates with times as
`1996-07-04 14:30:00`: the forms SQLite's date and time functions read.

## 7. Project settings

*Project → Project Settings…* (⌘;) holds what goes into the generated app beyond the model:

- **About text**, up to 250 characters (a counter shows how many are left). It appears in the
  app's **About** box, under its name, icon and version.
- **App icon**: paste (⌘V) or drag a picture into the well. It is kept as
  `<project>/Branding/logo.png` and deployed as `FBapp/AppLogo.png`; the app shows it in its
  header, its Dock icon and its About box. Select it and press Delete to remove it. **Without a
  picture, the symbol:** an SF Symbol for the header instead, with a preview beside it.
- **Tag-line**: a short description under the app's name, up to 80 characters.
- **Copyright**: at the left of the footer (nothing there when it is empty: the app's name is already in its header). Its company also heads the window's title:
  *Imagery Business Systems, LLC | Northwind* (just the app's name when the copyright names no company).

**Done** saves everything in `Project.json`. The project's heading in App Builder shows the same
icon, the picture or else the symbol.

### 7.1 The model diagram

*Model → Show Model Diagram* (⇧⌘D) opens the project's **entity-relationship diagram** in your
browser (`<project>/Model ERD.html`): every entity, its attributes and keys, and every relationship
(crow's foot = many, dashed = optional). The **business rules** are drawn where they act: ƒ formula,
Σ sum, # count, ⇣ copy and ! parent required on the attributes; ✓ constraint and ⚡ events in the
header; ⊘ delete action on the relationship.

Drag an entity by its header, and use its triangle to open and close it. Click an entity to see
its relationships, rules and attributes in the side panel. Scroll to zoom, drag the background to
move, *Find* an entity or attribute, switch the theme, and **Export SVG** to keep a copy.
Details: `features/MODEL_DIAGRAM_FEATURE.md`.

## 8. Generating the app

Generating needs a licence (the free Lite one is enough, see §2).

**The runtime and templates.** On first launch, and whenever they are missing, App Builder copies
`src/Runtime` and `src/Templates` from the repository it was built in into
`~/Library/Application Support/App Builder for FutureBasic/workspace/Runtime` and `…/Templates`.
It finds the repository from where its own app sits, and asks you to choose your Api_Logic_Client
folder only when it cannot. While it runs from that repository, *Generate App* copies them fresh
every time, so an app always gets the runtime App Builder was built with.
*Generate → Update Runtime and Templates…* does the same on demand.

| Command | Key | Writes into `FBapp/` |
|---|---|---|
| Generate XIBs | ⇧⌘X | every entity's `<Entity>Form.xib` and `<Entity>List.xib`, and `Model Tags.incl` |
| Generate XIB for Selected Entity | ⌘E | the selected entity's two parts |
| Generate Binding Code | ⌘B | `<Entity> Binding.incl` for every entity |
| Generate App | ⌘G | all of the above, plus the project, the main program, `Model.json`, `Credits.rtf`, the runtime and the starting files |

*Generate App* shows its progress in a sheet: each step listed and ticked as it is done, a bar that moves with
them, and at the end **Generated** and a **Done** button that closes the sheet. Done stays dimmed until it has
finished. If a step fails it is marked in red and the sheet says the app was not generated.

Then open **`FBapp/<name>.fbeproj`** in FutureBasic and build it. The project is laid out in groups:

| Group | Holds | Regenerated? |
|---|---|---|
| Runtime | the data runtime, the SQL Generator, LogicBank for FutureBasic, the app shell, records as tiles | yes, copied fresh |
| Model · Bindings · Resources | `Model Tags.incl`, `<Entity> Binding.incl`, `Model.json`, the XIBs, `Credits.rtf` | yes |
| Rules | `Studio Rules.incl` (generated) and **`Rules.incl` (yours)** | `Rules.incl`: never |
| Pages | `App Pages.incl`: a page per entity (its List and Form) and its navigation button | yes |
| Controller · View | **`EventHandlers.incl`, `Theme.incl`, `Menus.incl`, `Windows.incl` (yours)** | never |
| Main | `<name>.main`: settings, handlers, start-up | yes |

`README.md` in `FBapp/` is a developer's tour of the generated project, file by file, and every
generated file starts with a comment saying what it does and whether it is regenerated.

### 8.1 The app's look

Every generated app has the same frame (`App Shell.incl`):

- a **toolbar** at the top: **Search** first (a magnifying glass, labelled for the page: *Search
  Customers*, *Search Products*), a separator, then **New**, **Save**, **Delete** and **Refresh**, and at the far right the **theme menu**. They
  follow what you are doing: **Save** comes on only when you have changed something in the Form,
  **Delete** only when a record is shown (not while you fill in a new one). Like any Mac toolbar you can
  rearrange it (right-click it, *Customize Toolbar…*), and the app remembers how you left it;
- the **search dialog** (click Search): **Search by** a field, or *Any Field*, then the value, in the
  control that suits the field: a **calendar** for a date (the records of that day); a **dropdown of
  the field's values** when it has only a few, such as a type or a status (worked out from the records);
  a **text box** for anything else (the records holding every word you type, any case, any accent).
  The List narrows at once, the navigator counts only those records, and the line under the window's
  title says how many match. *Show All* brings every record back; a new page starts a new search;
- a **dark blue navigation bar** on the left (darker in dark mode), with a button and an icon per
  entity; with many entities (twenty tables, say) the buttons scroll;
- a slim **header** with the app icon, the app's name and the tag-line, and on the right **Log In** where
  the app signs in to a server (connect it to your sign-in in `EventHandlers.incl`, `DoLogin`); the **theme
  menu** (System / Light / Dark) is at the right of the toolbar;
- **full screen:** the green button (or *View → Enter Full Screen*) gives the app its own space; the
  cards, the List and the Form's fields, the navigator and the toolbar all stretch with the window;
- a **footer** with the copyright on the left and the **record navigator** in the middle: four icons, First,
  Previous, Next and Last (circled arrows in the accent colour), round *Customer 3 of 91*. A page
  opens on its first record, selected in the List with the focus there, so the arrow keys move through the
  records too. First and Previous are dimmed on the first record, Next and Last on the last. What just
  happened (*Saved.*, why a save was refused, *5 of 91 match*) shows under the window's title. New, Save,
  Delete and Refresh are in the toolbar, and in the *Records* menu (⌘N, ⌘S, ⌘R);
- a **divider** between the List card and the Form card: drag it (the cursor shows the up-and-down arrows)
  to give the List or the Form more height. Each page keeps its own, and the app remembers it the next time
  it opens;
- the **page**: the entity's List in a card at the top and its Form in a card below, both the
  full width of the window.

Choose a row and its record fills the Form. **Save** writes the Form through the business rules:
a refused save changes nothing and shows the rule's message. **New** empties the Form, and Save
then adds the record. **Delete** asks first; the rules decide what happens to related records.

**Grid or tiles.** A switch at the right of the List card's title shows the records as a grid or
as **tiles**: rounded panels, three or four across depending on the window's width, each with the
record's name as a subheading and up to four other fields in smaller text. Click a tile to see its
record in the Form, as you would a row. The record you are on has a ring round its tile, and the
footer's navigator moves the ring from tile to tile, scrolling to keep it in view. The page remembers
your choice while the app runs.

Change the colours in `Theme.incl` (yours). Add pages of your own in `Windows.incl`, after
`AppPagesBuild`; the file shows how.

### 8.2 Editions

The app is generated as the **Lite** edition, free and open source: it opens the project's SQLite
database itself and runs the business rules inside the app. The **Professional** edition, a
three-tier app that talks to an API Logic Server, is in development (`design/Editions Design.md`).

A project read from an API Logic Server (the ALS page, the server form or a metadata file) can
generate XIBs, bindings and the model diagram, but not a Lite app. For a Lite app, create the
project from the server's SQLite database instead (*New Project*); it gives the same model.

When the app runs, it opens the project's database (`Data: opened …` in the NSLog window) and
activates its rules (`Logic: rules active for N entities`).

## 9. Screens: FutureBasic's nib keywords

Every screen part the generator writes is a **XIB**, Interface Builder's file, which you can open
and change in Xcode. FutureBasic compiles the XIBs listed in the project into nibs when it builds,
and your FB code puts them on screen with its **nib keywords**:

| Keyword | What it loads | FutureBasic reference |
|---|---|---|
| `nibwindow tag, nibName [, identifier]` | a window | [nibwindow](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibwindow.html) |
| `nibview tag, nibName [, identifier [, origin [, superviewTag]]]` | a view (a Form or List part) into the window, or into another view | [nibview](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibview.html) |
| `nibtoolbar tag, nibName` | a toolbar | [nibtoolbar](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibtoolbar.html) |
| `nibmenu nibName` | a menu | [nibmenu](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibmenu.html) |
| `nibpopover tag, nibName` | a popover | [nibpopover](https://www.brilorsoftware.com/fb/documentation/FBHelp/pgs/nibpopover.html) |

The same pages are in FutureBasic's own help, and in the FutureBasic_Documentation repository
under `FBHelp/Resources/English.lproj/pgs/`.

**In the generated app.** `Windows.incl` (yours, written once) builds the window and its pages:

```
void local fn BuildWindows( title as CFStringRef )
fn ApplyTheme                                           // Theme.incl: the colours
fn ShellBuildWindow( title, APP_TAGLINE, APP_COPYRIGHT ) // App Shell.incl: navigation, header, footer
fn AppPagesBuild                                        // App Pages.incl: a page per entity
fn ShellShowPage( 0 )                                   // start on the first page
end fn
```

`AppPagesBuild` (in `App Pages.incl`) loads each entity's parts into the shell's content view:

```
nibview _customerView, @"CustomerForm", , ( 0, 0 ), _shellContent
nibview _customerList, @"CustomerList", , ( 0, listY ), _shellContent
```

**In App Builder itself**, the same keywords load one part per XIB:

```
nibwindow _window, @"MainWindow"                    // Windows.incl: BuildWindow
nibview _welcomeView, @"WelcomeView",, ( x, y )      // BuildSubViews: each page
nibview _newProjectView, @"NewProjectView",, ( x, y )
nibtoolbar _mainToolbar, @"Toolbar"
```

**What to know when you use them:**

- **The tag you pass becomes the view's tag.** The controls inside keep the tags the XIB gives
  them. The generated ones are named in `Model Tags.incl` (`_customerView`, `_customerCompanyName`,
  …), so your code reads and fills them with `ControlStringValue`, `ControlSetObjectValue` and the
  `<Entity> Binding.incl` functions. A tag must not be used by another control in the window.
- **`nibName` is the XIB's name without `.xib`** (`@"CustomerForm"`), and the XIB must be listed
  as a resource in the project. The generator lists every part it writes.
- **`superviewTag`** puts the view inside another one (a tab, a pane, a box) instead of the
  window's content view. This is how the generated pages sit in the shell's content area.
- **`identifier`** picks one view out of a XIB that holds several; without it, the first is loaded.
- **`origin`** is in the superview's coordinates, measured from the **bottom left**.
- **Load once, then show and hide** (`ViewSetHidden`): every load makes new copies of the views.
  Change a view right after its `nib…` call (size it, fill it, hide it), as the generator does.
- **Changing a part's layout:** open its XIB in Xcode. A regenerated part is rewritten, so for
  anything the generator decides, change the entity definitions (§6), and keep hand-made screens
  in XIBs of your own.

More about XIBs (what is inside one, frames and resizing, checking one with `ibtool`) is in
`reference/XIB Reference.md`.

## 10. Business rules

Business rules keep the data right whoever changes it: an order's total is the sum of its lines,
a customer's balance may not exceed the credit limit, a line takes its price from the product.
You **declare** them once, and **LogicBank for FutureBasic** enforces them on every save.

### 10.1 Where rules live

- **`Rules.incl`** in the generated project is yours: write rules in FB in its `DeclareRules`
  function. It is created once and never overwritten.
- **`Studio Rules.incl`** is generated from the project's `Rules.json` every time you
  *Generate App* (the rules imported from ALS, §11, and later the Rules page). Don't edit it;
  it is rewritten. Without a `Rules.json` it holds an empty `DeclareStudioRules`.
- The app's main program calls both, then `LogicActivate`.

### 10.2 Saving through the rules

In your own code, save records through the engine instead of writing them directly:

```
if ( fn LogicInsert( @"OrderDetail", aRecord ) == NO ) then alert 1, NSAlertStyleWarning, fn LogicMessage, @"", @[@"OK"], NO
fn LogicUpdate( @"Order", aRecord, NULL )        // NULL: the record's own key
fn LogicUpsert( @"OrderDetail", aRecord )         // update when the key exists, else insert
fn LogicDelete( @"Customer", @{ @"Id":@"ALFKI" } )
```

A record is a mutable dictionary of column → value. Each save is **one transaction**: if any rule
refuses it, nothing changes (neither the row nor the totals it would have updated), and
`LogicMessage` says why.

### 10.3 The rules you can declare

A rule function takes the row being saved (`logicRow`) and reads it with `LogicDouble`,
`LogicString`, `LogicValue`, `LogicIsEmpty`, `LogicOldValue` and `LogicChanged`, and its parent with
`LogicParentDouble`, `LogicParentString` and `LogicParentValue`.

**Formula**: an attribute computed from the row and its parents.

```
// OrderDetail.Amount = Quantity * UnitPrice
local fn OrderDetailAmount( logicRow as LogicRowRef ) as CFTypeRef
end fn = fn NumberWithDouble( fn LogicDouble( logicRow, @"Quantity" ) * fn LogicDouble( logicRow, @"UnitPrice" ) )

fn LogicFormula( @"OrderDetail", @"Amount", @fn OrderDetailAmount, @[ @"Quantity", @"UnitPrice" ] )
```

The list names what the formula reads. Formulas run in dependency order, and on an update a
formula whose inputs did not change is skipped. A parent's attribute is named
`@"Order.ShippedDate"`; when it changes on the parent, the children recompute.

**Constraint**: a condition that must hold, with a message (`{Attr}` shows the row's value).

```
local fn CustomerCreditCheck( logicRow as LogicRowRef ) as BOOL
end fn = ( fn LogicDouble( logicRow, @"Balance" ) <= fn LogicDouble( logicRow, @"CreditLimit" ) )

fn LogicConstraint( @"Customer", @fn CustomerCreditCheck, @"Balance {Balance} exceeds credit limit {CreditLimit}" )
```

**Sum and count**: a parent's total over a child list (the model's `<Child>List` names), with an
optional condition on the child.

```
local fn OrderIsUnshipped( logicRow as LogicRowRef ) as BOOL
end fn = fn LogicIsEmpty( logicRow, @"ShippedDate" )

fn LogicSum( @"Order", @"AmountTotal", @"OrderDetailList", @"Amount", NULL )
fn LogicSum( @"Customer", @"Balance", @"OrderList", @"AmountTotal", @fn OrderIsUnshipped )
fn LogicCount( @"Customer", @"UnpaidOrderCount", @"OrderList", @fn OrderIsUnshipped )
```

Totals are **adjusted**, never recounted: adding a line adds its amount, changing it adds the
difference, and moving an order to another customer takes it off one and adds it to the other.
The parent is then saved through its own rules, so adding a line updates the order's total and the
customer's balance, and checks the credit limit, in one save. Totals belong to the rules: a new row
starts them at 0, and a save from your code cannot overwrite them.

**Copy**: a parent's value, taken on insert (and when the row moves to another parent), not kept in
step afterwards.

```
fn LogicCopy( @"OrderDetail", @"UnitPrice", @"Product", @"UnitPrice" )
```

**Parent check**: a filled-in foreign key must find its parent.

```
fn LogicParentCheck( @"OrderDetail", @"Product", @"Product {ProductId} does not exist" )
```

**Delete action**: what deleting a parent does to its children. `prevent` refuses while there are
children, `cascade` deletes them too (through their rules), and `nullify` empties their foreign key.

```
fn LogicDeleteAction( @"Customer", @"OrderList", @"prevent", @"Customer {Id} still has orders" )
fn LogicDeleteAction( @"Order", @"OrderDetailList", @"cascade", NULL )
```

**Events**: your code at a set moment.

```
void local fn OrderShipped( logicRow as LogicRowRef )
// send a mail, write a log line, ...
end fn

fn LogicRowEvent( @"Order", @fn OrderAudit )        // during the save; must not change the row
fn LogicCommitEvent( @"Order", @fn OrderShipped )   // after the save has committed, once per row
```

A row event that changes the row fails the save, because the change would bypass the rules (use a
formula or a copy instead). Commit events never run for a save that was rolled back.

### 10.4 What happens on a save

```
insert   copy → parent check → formulas → adjust parents → constraints → row events → write
update   the same (formulas whose inputs did not change are skipped) → write → children follow
delete   delete actions → adjust parents → row events → write
commit   commit events, once per row
```

At start-up, `LogicActivate` checks every rule against the model (names, child lists, parent roles,
formulas that depend on each other in a circle) and refuses to start the rules if something is
wrong, with an alert and the details in NSLog. With `isLoggingOn`, the NSLog window shows each
rule as it fires, indented by how far the save has chained.

## 11. Importing and exporting ALS rules (`declare_logic.py`)

> **For now:** App Builder contains no Python, so these two commands say "coming" until they are
> rewritten in FutureBasic, and *Generate App* writes an empty `Studio Rules.incl`. Put the app's
> rules in `Rules.incl`. The Terminal commands below work today, from this repository's folder.

An ALS project's rules (LogicBank, in Python) can come in, and go back out (Professional):

- *Model → Import Rules from declare_logic.py…* (⌥⌘I): choose the ALS project's
  `logic/declare_logic.py`. The rules go into the project's `Rules.json`, and a message says how
  many came in and how many were switched off (see below). *Generate App* then writes them into
  `Studio Rules.incl`.
- *Model → Export Rules to declare_logic.py…* (⌥⌘E): writes the project's rules as LogicBank rules.

The reference for both is `tools/rules_bridge.py`, which you can run from Terminal in this
repository's folder:

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
  `row.ShippedDate is None`, `row.Order.ShippedDate`, comparisons, and `and` / `or` / `not`. Child
  lists and parent roles are found from the model.
- A rule it **cannot translate safely** (a Python function, a conditional expression, an event)
  arrives **switched off**, with its Python kept beside it in `Rules.json` for you to rewrite in FB.
  Nothing is lost and nothing is guessed; the import lists which rules these are.
- If you edited `Rules.json` by hand, **check** it first:
  `python3 tools/rules_bridge.py check --rules … --model …`.
- **Export** writes an unchanged imported rule exactly as it came, and translates edited ones from FB.
- `--help` shows every option.

## 12. Making the generated app your own

- **Yours, never overwritten:** `EventHandlers.incl` (what happens on clicks and menus),
  `Menus.incl`, `Windows.incl` (the window and its pages), `Theme.incl` (the colours), `Rules.incl`,
  and the project's build settings. Delete one to get a fresh copy at the next *Generate App*.
- **Regenerated:** `App Pages.incl`, `README.md`, the XIBs, bindings, `Model.json`, `Model Tags.incl`,
  `Studio Rules.incl`, the runtime and the main program. To change these, change the model, your
  adjustments or the rules instead.
- `Model Tags.incl` names every view and control tag, for your own code.
- **Buttons** are Mac-style pills (on macOS 26 the system's own capsule; on macOS 15 the same shape
  drawn in system colours): Save in the accent colour, Delete in red. For classic push buttons, set
  `gThemePillButtons = NO` in `Theme.incl`.

## 13. Opening projects again

- **Welcome page:** double-click a project in Recent Projects. *Project → Recent Projects* (⌘1)
  brings you back to the list, and *Clear Recent Projects* empties it.
- **Open Project…** (⌘O): choose a project's `Project.json` in the workspace.
- If the project's database has moved, you are asked to find it, and the new place is remembered.
- **Right-click a project** in Recent Projects for *Open*, *Show in Finder*, *Remove from Recent
  Projects* (the project stays in the workspace) and *Delete Project…*. Right-click an entity in the
  Objects list for *Generate XIB* and *Show Model Diagram*.
- **The Project menu follows what is on screen:** on the Welcome page it acts on the project selected
  in Recent Projects, elsewhere on the open one, and names it (*Delete “Northwind”…*, *Show “Northwind”
  in Finder*, *Close “Northwind”*). A tick marks the page showing, Recent Projects or Entity Definitions.
- **Delete Project…** (*Project* menu): the open project, or on the Welcome page the one selected in
  Recent Projects, goes to the **Trash** after you confirm, with its database copy, settings, rules
  and generated app. The database you started from is not touched. To restore the project, drag its
  folder back out of the Trash.

## 14. Checking your work

- **Without a Mac** (this repository): `tools/run_tests.sh` runs every check: the FB coding rules,
  the rules engine's scenarios, the proof that every rule is needed, and the rules bridge.
- **On a Mac:** `python3 tools/make_logic_test.py <db.sqlite> ~/Desktop/LogicTest`, then build and
  run `~/Desktop/LogicTest/Logic Test.fbeproj`: the same scenarios, in FutureBasic.
- **XIBs:** `xcrun ibtool --errors --warnings --notices --output-format human-readable-text File.xib`.
- **Every feature, by hand:** `TEST_SCENARIOS.pdf` walks you through each one, step by step, with
  what you should see and a box to tick.

`TESTING.md` describes every test.

## 15. Troubleshooting

| What you see | What to do |
|---|---|
| FutureBasic quits (crashes) when you build | A file listed in the project is missing beside it. FB's own headers (`NSLog.incl`, `Tlbx ….incl`) must be `include`d from a source file, not listed in the project (`tools/fblint.py` checks this). Also check *Build Settings*: the SDK must be one your Xcode has (see `src/CleanApp`). |
| Translator or compiler errors after pulling | The FB editor rewrites files when it opens them: `git stash`, pull again, build. If the errors name lines that look already fixed, your copy is behind. |
| `Data: the database is missing` | The project's `Database/` copy is gone: open the project and find the database when asked. |
| `The business rules are not active` | `LogicActivate` refused the rules; the alert and NSLog name the rule and attribute. |
| A save is refused | `fn LogicMessage` has the reason: a constraint's message, a parent check, a delete that is prevented. |
| `A row event changed …` | An event tried to change the row: use a formula or a copy rule instead. |
| `python3: command not found` | Install Xcode's command-line tools (`xcode-select --install`). |
| `statement is NULL` in NSLog | A query does not match the database's tables; the log line shows the SQL. |

When something is unclear, paste the Build Log or the NSLog lines into a session.

## 16. Menus, toolbar and keyboard shortcuts

A command is enabled only when what it works on is there. With no project open, only the commands
that open or create one are. *Generate XIB for …* needs an entity selected in the Objects list (and
names it), and the Control popup needs an attribute selected in the table.

| Menu | Command | Key | Needs |
|---|---|---|---|
| App Builder | Licence… · Enter Licence… · Upgrade to Professional… · Manage Licence Online… · Remove Licence… | | |
| Project | New Project… | ⌘N | |
| | New Project from API Logic Server… | ⇧⌘N | Professional |
| | Open Project… | ⌘O | |
| | Recent Projects | ⌘1 | |
| | Entity Definitions | ⌘2 | a project |
| | Clear Recent Projects | | |
| | Close Project | ⇧⌘W | a project |
| | Project Settings… | ⌘; | a project |
| | Show Project in Finder | ⌥⌘R | a project |
| | Delete Project… | | a project, or one selected in Recent Projects |
| Edit | Undo · Cut · Copy · Paste · Select All | ⌘Z ⌘X ⌘C ⌘V ⌘A | |
| Model | Open SQLite Database… | ⌘D | |
| | Open API Logic Server Metadata… | ⌘J | Professional |
| | Show Model Diagram | ⇧⌘D | a project |
| | Import Rules… · Export Rules… | ⌥⌘I · ⌥⌘E | a project, Professional |
| Generate | Generate App | ⌘G | a project, a licence |
| | Generate XIBs | ⇧⌘X | a project, a licence |
| | Generate XIB for *entity* | ⌘E | an entity selected, a licence |
| | Generate Binding Code | ⌘B | a project, a licence |
| | Show Generated App in Finder | ⌥⌘G | a project |
| | Update Runtime and Templates… | ⌥⌘U | |
| Window | Minimize · Zoom · Close | ⌘M · · ⌘W | |
| Help | App Builder Help (this guide) | ⌘? | |
| | Show Workspace in Finder | ⇧⌘K | |

**Crumb trail:** along the top of the window, it shows where you are, for example
*Projects › Northwind › address* (or *› Settings*, *› New Project*). Click *Projects* to go back to
the Welcome page, or the project's name to go back to its entity definitions.

**Toolbar:** *Projects* (⌘1: the Welcome page), *Entities* (⌘2: the open project's entity
definitions), *Diagram* (Show Model Diagram), *Generate* (Generate App) and *Settings* (Project
Settings). All but Projects need a project.

## 17. The SQL Generator

Every read and write in a generated app goes through the **SQL Generator** (`DataObject.glbl`,
`DataObject_Super.incl` and `DataObject.incl` in the runtime). You describe a statement with Cocoa
dictionaries and arrays; it writes parameterized SQL and lists the values for its `?` placeholders.
Your own code in a generated app can use it the same way.

![The SQL Generator's object model](design/SQL%20Generator%20Object%20Model.svg)

A query is a dictionary (`InitQueryDictionary`) of arrays: `selecttables`, `selectcols`,
`associations` (joins) and `filter`. Each `Add...ToQuery` call adds one small dictionary to one of
them. INSERT (one row, or an array of rows), UPDATE and DELETE each have a dictionary of their own.
`GenerateSelectSQL`, `GenerateInsertIntoSQL`, `GenerateInsertRowsSQL`, `GenerateUpdateSQL` and
`GenerateDeleteFromSQL` write the SQL, and `QueryParameterValues` gives the values in order. An
UPDATE or DELETE without a filter gets no SQL at all.

The module is also shared on its own, MIT-licensed: `src/SQLGeneratorExample/` holds an example
project (ten examples on a small CRM database, with a user guide in its Help window) and a
one-file demo, `SQL Generator - Smallest Program.fb`. Its `README.md` has the whole API.

## 18. What is not built yet

- **The Rules page** in App Builder: the rules of `Rules.json` in a list, an editor with the
  model's entities and attributes to pick from, and checking. Until then, write rules in
  `Rules.incl`, or import them (§11) and edit `Rules.json`.
- **Apps from API Logic Server projects** (Professional): App Builder opens, designs and generates
  screens for them; the data side that talks to the server, and sign-in, come next.
- **More Form controls**: toggle switch, combo box, calendar and colour pickers, formatted date and
  time displays (`BACKLOG.md` → Modern look).
- **Renaming** the project file and the repository to the product's name.

See `ROADMAP.md` for the plan and `BACKLOG.md` for every open item.

---

© 2026 Imagery Business Systems, LLC.
