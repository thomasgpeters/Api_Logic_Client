# New Project from a SQLite Database

**Where:** `src/AppBuilder/NewProjectView.xib`, `New Project.incl`; Welcome view
*Create Project* button (`EventHandlers.incl`).

## How it works

The lite edition starts from a SQLite database, not a server. *Create Project* on the
Welcome view opens the **New Project** view:

| Control | Tag | Does |
|---|---|---|
| Project Name | 400 | defaults to the database's file name |
| Database (read-only path) | 401 | the chosen file |
| Choose… | 402 | open panel (`.sqlite`, `.db`, `.sqlite3`); reads the model and shows what it holds |
| summary label | 403 | e.g. `8 tables, 2 views: Category, Customer, …` (first 12 names) |
| Create (↩) | 404 | enabled once a database with tables is chosen |
| Cancel (⎋) | 405 | back to the Welcome view |
| API Logic Server instead… | 406 | the server form (`ProjectCreateView.xib`) — the ALS route |

**Create** starts clean: the new name, and no base URL, user name or About text carried
over from the previous project. Then it loads the database the same way every model is
loaded (`LoadSQLiteModel` → `ProjectModelLoaded`): `Project.json` saved with the
database as `source`, `Design.json` applied, project added to Recent Projects, and the
entity definitions shown. If a project with that name already exists in the workspace,
an alert offers *Open It* or *Cancel*.

The chosen path is kept in the database field, not a global: nothing has to stay alive
between Choose and Create (the open panel's URL would need retaining); the model is
read again on Create.

## The project's own database

The chosen database is **copied** into `workspace/<project>/Database/` (with its `-wal`
and `-shm` files when present: uncommitted pages live in the `-wal`), and the project
works from the copy: the model is read from it and `Project.json`'s `source` names it.
The project folder is then self-contained, ready for backup and restore. This happens in
`LoadSQLiteModel` (`ProjectLocalDatabase` in `Project Workspace.incl`), so every route
does it: New Project, *Open SQLite Database…*, and Open Project for older projects whose
source is still outside the workspace. Choosing a file when the project already has a
copy asks: *Keep Project's Copy* (default), *Replace*, or *Cancel*.

## Verify on a Mac
- [ ] Create Project → New Project view; Create is disabled
- [ ] Choose… `nw/database/db.sqlite` → path, summary and suggested name appear
- [ ] Create → entity definitions; the project is in Recent Projects
- [ ] `<project>/Database/db.sqlite` exists; `Project.json` `source` points to it
- [ ] Choose the same database again for that project → Keep / Replace / Cancel
- [ ] Create with an existing name → *Open It* / *Cancel*
- [ ] API Logic Server instead… → the server form
