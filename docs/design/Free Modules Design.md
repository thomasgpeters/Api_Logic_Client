# Free Modules Design: SQL Generator, LogicBank for FutureBasic, Web Toolkit for FutureBasic

Status: decided (author, 2026-11-26); all three built (`src/SQLGeneratorExample`, `src/LogicBankExample`,
`src/WebToolkit` with `src/WebToolkitExample`), not yet published. The Web Toolkit joined as the third free module on
2026-11-26 (author: "I'd like to see the web toolkit as a module to make it free").

## What they are for

Imagery gives three FutureBasic modules away and sells App Builder:

| | Licence | Where | What it shows |
|---|---|---|---|
| **SQL Generator** | free, MIT | its own public repository; downloadable from the GitHub Pages site | statements as dictionaries -> safe, parameterized SQL (`src/SQLGeneratorExample`) |
| **LogicBank for FutureBasic** | free, MIT | its own public repository; downloadable from the GitHub Pages site | business rules declared once and enforced on every save (`AI Assistant Design.md` -> the module) |
| **Web Toolkit for FutureBasic** | free, MIT | its own public repository; downloadable from fb.imagery-business-systems.com | web apps in FB behind nginx: widgets, AJAX events, the page lifecycle, XIB layouts and the Layout Tool (`docs/features/WEB_TOOLKIT_FEATURE.md`) |
| **App Builder for FutureBasic** | licensed: Lite free with registration, Enterprise paid; resold by Imagery | private; downloaded from the Imagery License Server after registering | a complete app from a database, with its rules (`Licensing Design.md`) |

The modules are useful on their own, and they are how FutureBasic programmers meet Imagery. Open-sourcing LogicBank for
FutureBasic also keeps faith with LogicBank for Python (author, 2026-11-26): it is open source, and ours is inspired by it.
With the modules alone, rules are written by hand and the programmer is on their own; App Builder adds the AI
assistant, the checks and balances, the tests of every rule, and the generated app. App Builder is built on
both (generated apps carry them), so whoever likes a module has a reason to try App Builder.

**The Web Toolkit, the same way (author, 2026-11-26):** the module and its widgets are free, so anyone can build a web
app in FB - but they write their own pages, one widget, binding and event at a time. App Builder automates that: from
the model it builds the pages (forms, lists, their bindings and rules), as it builds the Mac app's windows. "That's
the incentive to buy the subscription." The pricing is in `Licensing Design.md` -> Pricing.

## Each module ships with a sample app

- **The SQL Generator's** works on a small CRM database in SQLite.
- **LogicBank for FutureBasic's** works on three objects in memory - Customer, Order, Item - with no database
  (`Data Memory.incl`, author's choice). The module ships both data layers: in memory, and SQLite (built on the SQL
  Generator), so the two modules work together when you choose SQLite.
- **The Web Toolkit's** is the Orders example: Customer, Order and Item in memory with LogicBank for FutureBasic's
  rules, served as a web page laid out in three XIB files (`src/WebToolkitExample`). The module also carries its app
  template (`Template/`) and the Layout Tool.
- **Each has a Help window:** the user guide with examples, the diagram, Preview and Export. The Web Toolkit's
  example is a server, so its guide is the module's `User Guide.txt`, published as a web page on the site.


- The module's files, an example app that shows it at work, a README, a user guide (in the app's Help), and the
  MIT licence.
- The example builds in the plain FutureBasic editor (no App Builder needed), and its README says how to drag the
  module's files into your own project.

## About Imagery Business Systems

Both sample apps have **About Imagery Business Systems…** in the application menu, under About. It opens a window
about Imagery's FutureBasic work:
- the free modules;
- App Builder (Lite and Enterprise, and the AI assistant to come);
- the sample applications (Telecom, Customs, Flight Planner);
- a button to the website.

- **One file, identical in every app:** `src/Shared/About Imagery.incl`, with its text in the resource
  `About Imagery.txt`. Changing what Imagery says means editing the text, in `src/Shared`, then copying it to
  each app; `run_tests.sh` checks that the copies are identical.
- **The text's markup:** `# heading`, `## subheading`, `- bullet`, `**bold**`, one paragraph a line. The window
  uses system colours and the Imagery logo that follows light and dark mode.
- **The website address:** `ABOUT_IMAGERY_SITE` in the file. Set it once the GitHub Pages repository is named.
- **Using it in an app:**
  1. Add the file and the three resources (`About Imagery.txt`, `imagery_logo.png`, `imagery_logo_white.png`).
  2. Add a menu item that calls `fn AboutImageryShow`.
  3. In `DoDialog`: `if ( fn AboutImageryHandles( ev, tag ) ) then exit fn`.

## Plan

1. [x] The About Imagery window (`src/Shared`), in the SQL Generator example
2. [x] LogicBank for FutureBasic packaged as a module, with its example app, its Help, and the About Imagery window
   (`docs/features/LOGICBANK_MODULE_FEATURE.md`)
3. [x] The Web Toolkit as the third free module: its user guide, the About Imagery window in its example, its page
   and downloads on the site (2026-11-26)
4. [ ] The public repositories for the three modules; the GitHub Pages site with their downloads, the samples, and
   App Builder's page (registration on the Imagery License Server)
5. [ ] `ABOUT_IMAGERY_SITE` set to the site's address
