# Test Scenario Guide

App Builder for FutureBasic, its generated apps, and the free FutureBasic modules

<!--
  The source of docs/TEST_SCENARIOS.pdf: python3 tools/make_test_guide.py
  Format: "## Area" groups scenarios; "### ID Title" starts one; "Purpose:", "Before:" lines; then numbered steps,
  each "action -> expected". Keep it true when a feature changes (CLAUDE.md, Workflow).
-->

## About this guide

This guide walks a tester through every feature, one scenario at a time. Each scenario says what it checks, what to have ready, and then lists steps: what to do, and what you should see. Mark each step Pass or Fail, and write down anything unexpected.

Test on a Mac with macOS 15 or later and FutureBasic 7. Where a scenario says "light and dark", switch the Mac's appearance (System Settings, Appearance) and look again.

When something fails, keep what the Mac shows: the Build Log for build errors, the crash report for a crash, and a screenshot for anything that looks wrong. Note the scenario and step number with it.

Results: Pass (every step as expected), Fail (a step was not), Blocked (could not be run, say why).

## A. Studio for FB: first launch and licence

### A-01 Build and launch the Studio
Purpose: The Studio builds and opens on its Welcome page.
Before: The repository cloned on the Mac; FutureBasic 7 installed.
1. Open src/AppBuilder/Studio for FB.fbeproj in FutureBasic and build it. -> The Build Log ends without errors and the app starts.
2. Look at the Welcome page. -> At the top: the Imagery logo, "App Builder for FutureBasic", and the tag-line under it. There is no second heading above it.
3. Look below the heading. -> A rounded white card on the grey window (in dark mode a step lighter than the window): "Recent Projects", the list in the same style as every other table in the Studio and the generated apps (plain rows, a super-light line between them, no stripes), then Open Project... and Create Project at the right, under the list. The column headings (Project, Model) are semibold, a little larger than the rows.
4. Switch the Mac between light and dark. -> The logo, the card and the text follow; the card still stands out from the window.
5. Resize the window, down to its smallest. -> The card and the list stretch; the buttons stay at the right.

### A-02 No licence, then a Lite licence
Purpose: The Studio runs without a licence, and accepts a Lite licence.
Before: A test Lite licence: in the repository folder, python3 tools/licence_reference.py --issue lite tester@example.com "Test User"
1. With no licence entered, open the App Builder menu, Licence... -> The Licence window says no licence is entered and offers Get a Free Lite Licence.
2. Paste the test Lite licence into the field and enter it. -> The window shows the licence in words: who, Lite, until when, its features.
3. Open the Project menu. -> New Project from API Logic Server... shows "(Professional)" after its title.
4. Choose it. -> A message explains it is Professional and offers the upgrade.

### A-03 Professional licence, then remove it
Purpose: A Professional licence opens everything; removing it is clean.
Before: A test Professional licence: python3 tools/licence_reference.py --issue professional tester@example.com "Test User"
1. Enter the Professional licence (App Builder menu, Enter Licence...). -> The window shows Professional; no command shows "(Professional)" any more.
2. Quit and start the Studio again. -> The licence is still there (it is kept in the Keychain).
3. App Builder menu, Remove Licence..., confirm, then quit and start again. -> No licence is entered; the Studio still opens.

## B. Studio for FB: projects

### B-01 Create a project from a SQLite database
Purpose: A new project from a database, and the project's heading.
Before: A SQLite database, for example Northwind.
1. Click Create Project. -> The New Project page opens.
2. Click Choose... and pick the database. -> The page lists what it found, for example "14 tables, 2 views: Category, Customer, ...", and fills in the Project Name.
3. Click Create. -> The entity list on the left fills in; the crumb trail reads Projects > the project's name.
4. Look at the heading. -> The project's icon (a building, until one is chosen) and the project's name.
5. Help menu, Show Workspace in Finder. -> The workspace folder holds "<name> Project" with Project.json and Database/ (a copy of the database).

### B-02 A project that already exists
Purpose: Creating a project with a name already used.
Before: B-01 done.
1. Create Project again with the same database and name, then Create. -> The Studio asks whether to open the existing project instead.

### B-03 Back to Projects and return
Purpose: The crumb trail and the heading follow the page.
Before: A project open.
1. Click Projects in the crumb trail. -> The Welcome page, with its own heading; the project's name is not shown.
2. Click the toolbar's Entities. -> The project's entity definitions, with its icon and name in the heading.
3. With the project open, click Projects (crumb trail or toolbar). -> The Projects page fills the whole width: the Objects list is hidden. Entities again: the list is back, the entity still selected.

### B-04 Open a project again
Purpose: Recent Projects and Open Project.
Before: A project created earlier; the Studio restarted.
1. On the Welcome page, double-click the project in Recent Projects. -> It opens, with its entities.
2. Close it (Project menu, Close Project), then Open Project... and choose its Project.json. -> It opens the same way.
3. Project menu, Clear Recent Projects. -> The list is empty.

### B-05 A project from an API Logic Server project (Professional)
Purpose: The model read from an ALS project, never run.
Before: A Professional licence; an ALS project folder, or a public GitHub address of one.
1. Project menu, New Project from API Logic Server... -> The API Logic Server Project page opens.
2. Drop the ALS project's folder on the drop zone (or Folder..., or type the GitHub address and Read). -> The page shows what the model holds and where it came from, and fills in the Project Name.
3. Enter the API Server address (http://localhost:5656 by default) and Create. -> The project opens with the model's entities; ALS Model/ in the project folder holds a copy of the model.

### B-06 The running server form
Purpose: The form's layout.
1. On the API Logic Server Project page, click From a Running Server... -> At the top: the logo, the product's name, "A project from a running API Logic Server". Below: a rounded card with the form.
2. Look at the buttons. -> Cancel, then Create, at the right; Create is dimmed until the form is filled in.
3. Cancel. -> Back to where you were.

### B-07 Delete a project
Purpose: A project goes to the Trash, and can come back.
Before: A project you can spare.
1. Select it in Recent Projects, Project menu, Delete Project..., confirm. -> The item reads Delete "<its name>"...; it leaves the list; its folder is in the Trash. The database you started from is untouched.

### B-08 Right-click menus and a Project menu that follows the page
Purpose: The commands act on what you are looking at, as in any Mac app.
Before: Two projects in Recent Projects; one of them open.
1. On the Welcome page, right-click the project that is not open. -> A menu: Open, Show in Finder, Remove from Recent Projects, Delete Project...; the row is selected.
2. Choose Show in Finder. -> Finder shows that project's folder.
3. Open the Project menu. -> Show "<that name>" in Finder and Delete "<that name>"... name the selected project; Close "<open project>" names the open one; Recent Projects has a tick.
4. Right-click it again, Remove from Recent Projects. -> It leaves the list; its folder is still in the workspace.
5. Open the other project, right-click an entity in the Objects list, Generate XIB. -> That entity is selected and its XIB is generated.
6. Open the Project menu. -> Entity Definitions has the tick; Delete and Show in Finder name the open project.

## C. Studio for FB: entity definitions

### C-01 Change a title
Purpose: An adjustment is saved and kept.
Before: A project open.
1. Click an entity, double-click a Title cell, type a new title, Return. -> The row shows a tick under Adjusted.
2. Close the project and open it again. -> The new title is still there (Design.json).
3. Clear the cell and press Return. -> The recommendation comes back; the tick goes.

### C-02 A field's control
Purpose: The Control popup.
1. Select an attribute in the table, then choose Date picker in the Control popup. -> The Form Control cell says Date picker.
2. Choose the first item, "Recommended: ...". -> The control goes back to the generator's choice.

### C-03 A value list
Purpose: Radio buttons and Dropdowns from a value list.
1. In a text attribute's Values cell type "R = Retail, W = Wholesale, O = Online" and choose Radio buttons. -> The cell keeps the list.
2. After generating the app (F-01), open its page. -> Three radio buttons, Retail, Wholesale, Online; saving one stores R, W or O.

### C-04 Form layout and icon
Purpose: The Form's columns and the entity's icon.
1. Choose "Form: 2 columns" for an entity, then Generate XIBs. -> The entity's Form has its fields in two columns.
2. Choose an icon in the Icon popup. -> The preview beside it shows the symbol; the generated app's navigation button uses it.

## D. Studio for FB: project settings

### D-01 About text, tag-line, copyright
Purpose: What the generated app shows beyond the model.
1. Project menu, Project Settings... and type an About text. -> A counter shows how many of the 250 characters are left; it stops at 250.
2. Type a tag-line and a copyright, then Done. -> Back on the entities; the settings are in Project.json.

### D-02 The app icon
Purpose: A picture or a symbol for the app, and for the project's heading.
1. In Project Settings, choose a symbol (without a picture). -> The preview shows it.
2. Click Done. -> The project's heading shows the chosen symbol beside its name.
3. Open Project Settings again and paste a picture into the icon well, then Done. -> The heading shows the picture.
4. Select the picture in the well, press Delete, then Done. -> The heading shows the symbol again.

## E. Studio for FB: the model diagram

### E-01 The diagram in the browser
Purpose: The entity-relationship diagram and its tools.
1. Model menu, Show Model Diagram. -> The browser opens Model ERD.html: every entity, its attributes and keys, and the relationships.
2. Drag an entity by its header; click its triangle. -> It moves; it opens and closes.
3. Click an entity. -> A side panel shows its relationships, rules and attributes; the others dim.
4. Scroll to zoom, drag the background, use Find, switch the theme, Export SVG. -> Each works; the SVG file is saved.

## F. Generating the app

### F-01 Generate App
Purpose: The generated project.
Before: A project open.
1. Generate menu, Generate App. -> A sheet, "Generating <name>", lists nine steps; each is ticked in turn as the bar moves forward; Done is dimmed meanwhile.
2. Wait for the end. -> Every step ticked, the bar full, the message "Generated"; Done is on; Return or a click on Done closes the sheet.
3. Generate menu, Show Generated App in Finder. -> FBapp/ holds <name>.fbeproj, the XIBs, the bindings, App Pages.incl, Model.json, README.md and the runtime files, Record Tiles.incl among them.

### F-02 Build the generated app
Purpose: The generated app builds and runs.
1. Open FBapp/<name>.fbeproj in FutureBasic and build it. -> The Build Log ends without errors and the app opens on its first page.

### F-03 Your files are kept
Purpose: Regenerating never overwrites the files that are yours.
1. Change a colour in the generated app's Theme.incl, then Generate App again in the Studio. -> Theme.incl still has your change; App Pages.incl is rewritten.

## G. The generated app

### G-01 The app's frame
Purpose: Navigation bar, header, footer.
1. Look at the window. -> A dark blue navigation bar with a button and an icon per entity; a header with the app icon, the app's name centred on it and the tag-line under it; a toolbar with Search, New, Save, Delete, Refresh; a footer with the copyright at its left and the record navigator across the rest (First, Previous, the record's number, Next, Last as pill buttons sharing the width).
2. Use the theme menu: Light, Dark, System. -> The whole app follows; in dark mode the navigation bar is darker; the cards stand apart from the area behind them in both.
3. Click each navigation button. -> Each page shows its List card above its Form card, both filling the width.

### G-01b The window's title
Purpose: Company | App.
Before: In Project Settings, the copyright "© 2026 Imagery Business Systems, LLC"; Generate App.
1. Look at the window's title. -> "Imagery Business Systems, LLC | <app name>".
2. Clear the copyright in Project Settings, Generate App, build and run. -> The title is the app's name alone.

### G-01a Many entities
Purpose: The navigation bar scrolls.
Before: The full Northwind database (about twenty tables), Generate App.
1. Look at the navigation bar. -> A button per table under "Business Objects", down to the foot of the bar.
2. Scroll the bar (two fingers or the wheel). -> The buttons scroll; a thin scroller shows while scrolling.
3. Make the window short, then click the last button. -> Its page shows, and the bar scrolls to keep its button in view.

### G-02a The record navigator
Purpose: A page opens on its first record, and the footer moves through them.
1. Open the app, click Customers. -> The first customer is selected in the List (the List has the focus) and shown in the Form; the footer reads "Customer 1 of 91" (your count) between the pill buttons; First and Previous are dimmed (faded).
2. Make the window wider and narrower. -> The five cells of the navigator share the footer's width and stretch with it; the copyright stays at the left.
3. Click Next three times. -> "Customer 4 of 91"; the List's selection and the Form follow; First and Previous are on.
4. Click Last. -> The last customer; Next and Last are dimmed.
5. Press the up arrow key. -> The one before it; the footer follows.
6. Change a field and Save. -> The same customer stays selected and shown.
7. New, fill in the Form, Save. -> The new customer is selected and shown.
8. Delete it. -> The customer that took its place in the list is selected and shown.
9. Click Products. -> "Product 1 of ..." and the first product shown.
10. Click Customers again, then Products again, a few times. -> Each page comes back on its record; the app does not quit (a crash here was fixed on 2026-11-27).

### G-02b The toolbar and the search dialog
Purpose: Search follows the page and the field; New, Save, Delete and Refresh work from the toolbar.
1. On Customers, look at the toolbar. -> Search (a magnifying glass) labelled "Search Customers", a thin separator, then New, Save, Delete, Refresh; Save is dimmed (nothing changed yet), Delete is on (a customer is shown).
2. Click Search. -> A dialog under the item: "Search by" with Any Field, and a text box.
3. Type part of a company name. -> The List narrows as you type; under the window's title, "n of 91 match"; the first match is shown.
4. Search by: Company Name, type a word from a city. -> No match (it searches that field only); type part of a name instead: matches.
5. Search by: a field with few values (a country, a region, a type). -> The text box gives way to a dropdown of that field's values; choose one: only those records.
6. On Orders, Search by: Order Date. -> A small calendar (day, month, year); click a day with orders: only that day's orders; another day: those.
7. Show All. -> Every record; Search by is back on Any Field.
8. Click Products. -> The toolbar reads "Search Products"; the dialog offers Products' fields.
6. Type one letter in a field of the Form. -> Save comes on at once. Save. -> The record is saved; Save is dimmed again.
7. Toolbar New. -> An empty Form; Delete and Save are dimmed. Fill in a field. -> Save comes on; Delete stays dimmed until the new record is saved.
8. Choose a record you can spare, Delete. -> The same as the Records menu's Delete.
9. Right-click the toolbar, Customize Toolbar..., drag Refresh before New, Done; quit and reopen. -> The new order is kept.

### G-02 Records: choose, add, change, delete
Purpose: The Form and the List work together.
1. Click a row in the List. -> Its record fills the Form.
2. Change a field and Save (or Command-S). -> The List shows the change; "Saved." under the window's title.
3. New (Command-N), fill in the Form, Save. -> The new record is in the List.
4. Select it and Delete; confirm. -> It is gone from the List.

### G-03 The business rules
Purpose: A save that breaks a rule is refused, and nothing changes.
Before: Rules in the app's Rules.incl (for example a credit limit).
1. Make a change that breaks a rule, and Save. -> The rule's message is shown; the record is as it was.
2. Make a change the rules allow, and Save. -> It is saved, and the values the rules keep (totals, balances) follow.

### G-04 Lookups and the info button
Purpose: A foreign key's Dropdown and its details.
1. On a page whose Form has a Dropdown for a parent (an Order's Customer), open the Dropdown. -> It lists the parent's records by a readable name.
2. Choose one and click the info button beside it. -> A popover shows that record's fields and values.
3. Click New. -> The Dropdown is empty and the info button is dimmed; clicking it does nothing.
4. Choose a parent again. -> The info button is on again. For an auto-complete: clear the text, and it dims; choose a match, and it comes back on.

### G-05 Records as tiles
Purpose: The tiles view beside the grid.
1. Click the tiles symbol in the switch at the right of the List card's title. -> The grid gives way to tiles: rounded panels with a soft shadow, the record's name as a subheading, up to four other fields under it in smaller text.
2. Make the window wide, then narrow, and click Refresh. -> Four tiles across when the List is wide, three when it is narrower.
3. Look at the first tile. -> It has a ring in the accent colour: the navigator's record ("Customer 1 of 91"), shown in the Form.
4. Click Next in the footer, three times. -> The ring moves tile by tile; the Form follows; "Customer 4 of 91".
5. Click Last. -> The ring is on the last tile, the tiles scrolled to show it; Next and Last are dimmed.
6. Click a tile. -> Its record fills the Form; the ring moves to it; the navigator shows its number.
7. Search for a name (toolbar). -> Only the matching tiles; the ring on the first of them.
8. Switch to the grid. -> The same record is selected in the grid; switch back: the ring is on it.
9. Switch to another page and back. -> The page still shows tiles; switch back to the grid with the list symbol.
10. Switch the theme to dark. -> The tiles still stand out from their card; the ring still shows.

### G-06 Auto-complete for a related record
Purpose: Finding a parent record by typing.
Before: In App Builder, a foreign key (an Address's Person, an Order's Customer) set to Control: Auto-complete, then Generate App.
1. In App Builder, select that attribute. -> A settings row appears under the Control popup: Show (the parent's field), After 1 letter, Up to 8 results.
2. In the generated app, type the first letters of a parent's name into the field. -> A list of matches opens under the field (above it, if the field is low in the window); names that start with the letters come first.
3. Choose one with a click, or with the arrow keys and Return. -> The field shows the name; the list closes.
4. Save, then choose another record and come back. -> The field shows the chosen parent's name.
5. Click the info button beside the field. -> A popover shows the chosen parent's fields.
6. Type, then press Escape. -> The list closes.

### G-07 Auto-complete on local values
Purpose: An auto-complete fed by the attribute's own Values list.
Before: In App Builder, a text attribute with Values "R = Retail, W = Wholesale, O = Online" and Control: Auto-complete; another with a plain list ("Small, Medium, Large"), Auto-complete, Allow other values on. Generate App.
1. In App Builder, select the first attribute. -> The settings row shows "From the Values list"; Allow other values is off (a list of codes).
2. In the generated app, type "wh" in the first field. -> The list offers Wholesale; choosing it shows Wholesale.
3. Save, then look at the record in the List. -> The stored value is W.
4. In the second field, type "Extra large" and Save. -> The value is kept as typed (other values allowed).
5. Quit the app, start it again, and type "ext" in that field. -> Extra large is offered with the list's values.

## H. The free modules

### H-01 SQL Generator: the one-file demo
Purpose: The module in its smallest form.
Before: SQL-Generator-Module.zip from the site (or the files from src/SQLGeneratorExample).
1. Keep the five files together, open "SQL Generator - Smallest Program.fb" in FutureBasic, and run it. -> The NSLog window shows the INSERT it wrote, "3 rows added", the SELECT, its values, and two people: Ada Lovelace and Grace Hopper.

### H-02 SQL Generator: the example app
Purpose: The ten examples.
1. Build and run src/SQLGeneratorExample. -> A window lists the ten examples.
2. Run All. -> Each example shows its FB code, the SQL it wrote, the values and the result.
3. Look at example 9, "Change every balance, with no filter". -> Refused: an UPDATE without a filter is not written.
4. Reset Database, then run example 10. -> Three people added in one INSERT; example 1 then lists them.
5. Help menu, SQL Generator Example Help. -> The user guide opens.

### H-03 LogicBank for FutureBasic: the story
Purpose: The rules engine, step by step.
1. Build and run src/LogicBankExample. -> The opening page: the heading, the tag-line in italics, short paragraphs, "The rules, in plain words" as bullets, and "What you will see".
2. Next Step, thirteen times. -> Each step shows its FB, "Saved." or "Refused" with the rule's message, and the objects: step 3, 180.00 after the discount; step 4, the order is 450.00; step 6 refused (1,080.00 would pass the 1,000.00 limit); step 7 refused; step 8 the order ships and leaves the balance; step 9 the earlier order keeps its 10 %; step 10 a new order at 20 %, 160.00; steps 11 and 12 refused; step 13 the new order and its item deleted.
3. Start Again, then Run the Whole Story. -> The same thirteen steps, all at once.
4. Help (?). -> The user guide, with the rules diagram.

### H-04 Web Toolkit for FutureBasic: the Orders example
Purpose: A web app in FutureBasic, behind nginx.
Before: nginx installed (brew install nginx).
1. Build and run src/WebToolkitExample. -> Its window says it is serving.
2. In that folder: nginx -c "$PWD/nginx.conf" -p "$PWD", then open http://127.0.0.1:8088/ -> The Orders page: customers, their orders and items.
3. Add items until a customer's balance would pass the credit limit. -> The page shows the rule's message; nothing changes.
4. Ship Today on an order. -> The customer's balance comes down, without a reload.
5. Change an item, then switch tabs. -> The item is saved on its own.
6. Open the page in a second browser. -> Both show the same data.

### H-05 The Layout Tool
Purpose: Laying out a web page in a XIB file.
1. Open src/WebToolkit/Layout Tool/Layout Tool.html in Safari, and open CustomerPanel.webxib. -> The panel is shown as the web page will lay it out.
2. Move a field, change a label, save. -> The .webxib file is updated; the example page shows the change after a restart.

### H-06 Record Files for FutureBasic
Purpose: Record files with B-tree indexes, timed against SQLite.
1. Build and run src/RecordFilesExample, choose 10,000 customers, Run. -> A table of seven steps with times for the record files and for SQLite.
2. Read step 2 and step 7. -> Step 2: "0 indexes rebuilt". Step 7: "every index sound, one entry per record".
3. Read step 6. -> Items removed and added; Items.records did not grow (the freed slots were reused).
4. Run again, and Force Quit the app while it runs. Start it and Run once more. -> The run completes; step 7 is sound.
5. Show the Files. -> The Finder shows the record files, the index files and Comparison.sqlite.

## I. Checks without a Mac

### I-01 The repository's tests
Purpose: Every check that runs without a Mac.
Before: A Linux or Mac computer with Python 3.
1. In the repository folder: tools/run_tests.sh -> The last line is "run_tests: all passed".
2. On a Mac: python3 tools/make_logic_test.py <db.sqlite> ~/Desktop/LogicTest, then build and run Logic Test.fbeproj -> All 70 rule scenarios pass, in FutureBasic.
