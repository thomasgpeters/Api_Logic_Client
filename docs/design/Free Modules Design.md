# Free Modules Design: SQL Generator and LogicBank for FutureBasic

Status: decided (author, 2026-11-26); the SQL Generator is built, LogicBank for FutureBasic is to be packaged.

## What they are for

Imagery gives two FutureBasic modules away and sells App Builder:

| | Licence | Where | What it shows |
|---|---|---|---|
| **SQL Generator** | free, MIT | its own public repository; downloadable from the GitHub Pages site | statements as dictionaries -> safe, parameterized SQL (`src/SQLGeneratorExample`) |
| **LogicBank for FutureBasic** | free, MIT | its own public repository; downloadable from the GitHub Pages site | business rules declared once and enforced on every save (`AI Assistant Design.md` -> the module) |
| **App Builder for FutureBasic** | licensed: Lite free with registration, Enterprise paid; resold by Imagery | private; downloaded from the Imagery License Server after registering | a complete app from a database, with its rules (`Licensing Design.md`) |

The modules are useful on their own, and they are how FutureBasic programmers meet Imagery. App Builder is built on
both (generated apps carry them), so whoever likes a module has a reason to try App Builder.

## Each module ships with a sample app

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
2. [ ] LogicBank for FutureBasic packaged as a module, with its example app (the About Imagery window included)
3. [ ] The public repositories for both modules; the GitHub Pages site with their downloads, the samples, and
   App Builder's page (registration on the Imagery License Server)
4. [ ] `ABOUT_IMAGERY_SITE` set to the site's address
