# Projects: Open Project and Recent Projects

**Where:** `src/AppBuilder/Project Workspace.incl` (folders, `Project.json`),
`Recent Projects.incl` (the list), `Project Actions.incl` (`OpenProject`,
`OpenRecentProject`, `OpenProjectSettingsFile`, `LoadModelFile`), `WelcomeView.xib`
(Open Project… button tag 101, Recent Projects table tag 102), *Model* menu.

## How it works

A project is its folder, `workspace/<project>/`:

| File | Holds |
|---|---|
| `Project.json` | `name`, `source` (the SQLite database or metadata JSON), `baseURL`, `userName` — never passwords |
| `Design.json` | the designer's adjustments |
| `FBapp/` | the generated FutureBasic app |

**Opening a project** reads `Project.json`, sets the project name, clears the
connection fields, then reopens the model from `source`. Loading a model (from
a project or from *Open SQLite Database…* / *Open Metadata JSON…*) always does the
same four things after the model is read: saved connection fields fill the empty
ones, `Design.json` is applied, `Project.json` is saved, and the project moves to
the top of Recent Projects.

**If the model file has moved**, an alert offers *Locate…*; the chosen file becomes the
new `source`.

**Recent Projects** — `~/Library/Application Support/App Builder for FutureBasic/Recent Projects.json`,
newest first, at most 10, one entry per `Project.json` path:

```json
[ { "Project": "Northwind", "Model": "db.sqlite", "path": ".../Northwind Project/Project.json" } ]
```

`Project` and `Model` are the table's column identifiers, so the list is the table's
data as is. Shown on the Welcome view (double-click opens); *Project → Recent Projects*
returns to the Welcome view; *Project → Clear Recent Projects* empties it.

## Commands

| Command | Key | Does |
|---|---|---|
| Open Project… | ⇧⌘O | open panel in the workspace, choose a `Project.json` |
| Recent Projects | | back to the Welcome view |
| Clear Recent Projects | | empties the list |
| Welcome: Open Project… button | | same as the menu |
| Welcome: double-click a recent project | | opens it |

## Decisions
- The project file is `Project.json` (not a document type): KISS; an `.alcproj`
  document type with Finder double-click can come later.
- A project created by fetching `/metadata` from a server has no `source` yet; opening
  it says so. The ALS edition will store the server URL as the source.

## Verify on a Mac
- [ ] Welcome view shows the Open Project… button and the Recent Projects table
- [ ] ⌘D a database → it appears in Recent Projects; quit and relaunch → still listed
- [ ] Double-click it → the model, adjustments and connection fields come back
- [ ] Rename the database → opening asks to locate it; the new path is saved
