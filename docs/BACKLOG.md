# Backlog

## Ideas

### LogicBank for FutureBasic
Re-engineer [LogicBank](https://github.com/valhuber/LogicBank), the declarative
rules engine behind API Logic Server, for FutureBasic, and fork LogicBank Studio
so rules can be written and managed in FB syntax.

- **Goal:** rules declared in FB (e.g. sum, count, formula, constraint, copy,
  parent check, events) run in the FB app, whether against SQLite or ALS.
  The SQLite record/view apps (the Test_Xib_View pattern) would gain the same
  declarative behaviour ALS has on the server.
- **LogicBank Studio fork:** author, view and edit rules in FB syntax.
- **Open questions:**
  - Rule declaration syntax in FB.
  - Where rules run: client-side only, or alongside ALS server-side logic.
  - How rule dependencies are tracked and ordered without SQLAlchemy events.
  - Whether the generator emits rule stubs per resource from the ALS model.

## Generator / runtime

- [ ] Paging in the generated records table (currently the first `gALSPageLimit` = 100 records).
- [ ] Relationships: lookups (parent pick lists) and child tables. Needs the
      relationship info that ALS metadata can include.
- [ ] Type overrides, e.g. Northwind `discontinued` is INTEGER but should be a checkbox.
- [ ] Generator's own ALS fetch should use the Create Project form's base URL and
      credentials (it still uses the hardcoded host and `admin`/`p`).
- [ ] Generator's metadata fetch fires before login completes when security is on.
- [ ] Confirm FBE bundles `../Runtime/*.incl` as resources from the Generator project.
- [ ] Move to the FB 7.1.5 NS type names (`ArrayRef`, `DictionaryRef`, …) for CocoaUI calls.

- [ ] SQLite target for generated apps: emit the Test_Xib_View query-builder
      pattern (Select/Insert/Update/Delete dictionaries + `SQLBindValues`) per
      resource, alongside `Database/build_db.py --als` for the schema.

## Tooling

- [ ] Retire or make private `futurebasic-apis`: it is outdated (pre-7.0.35) and
      superseded by FutureBasic_Documentation, and the toolboxes carry no
      redistribution license.
