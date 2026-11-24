# Generate Commands

**Where:** *Model* menu (`src/Generator/Menus.incl`, `EventHandlers.incl`),
`GenerateProjectParts` in `Project Actions.incl`, `AppGenerate` in `App Generator.incl`.

| Command | Key | Writes |
|---|---|---|
| Generate XIBs | ⌘X | every entity's Form and List parts + `Model Tags.incl` |
| Generate XIB for Selected Entity | ⌘E | that entity's two parts |
| Generate Binding Code | ⌘B | `<Entity> Binding.incl` for every entity |
| Generate App | ⌘G | all of the above + `Model.json`, the FB project, `<project>.main`, runtime copies, starting templates |

Output: `~/Library/Application Support/Imagery LogicBank Studio for FutureBasic/workspace/<project>/FBapp/`
(`<project>/` itself holds the project's settings: `Project.json`, `Design.json`) (the workspace — see `docs/design/Generator App Design.md`;
*Model → Show Workspace in Finder* opens it). Every entity's model entry is always built
(tags and sizes are needed by binding code and `Model.json`); only the requested
files are written.

## Generated project

An FB project, laid out like Test_Xib_View:

```
<project>.fbeproj/data.fbproj
// "Runtime" 1      Binding Support, ALS Client, ALS Binding, ALS App .incl
// "Model" 1        Model Tags.incl
// "Bindings" 1     <Entity> Binding.incl ...
// "Resources" 1    Model.json, <Entity>Form.xib, <Entity>List.xib ...
// "Controller" 1   EventHandlers.incl
// "View" 1         Menus.incl, Windows.incl
// "Main" 1         <project>.main
```

| File | Regenerated | Notes |
|---|---|---|
| `<project>.fbeproj/data.fbproj` | yes | build order, groups as above |
| `<project>.fbeproj/Settings2.plist` | only if missing | from `src/Templates/Project` (`-lsqlite3`) |
| `<project>.main` | yes | connection globals, `on …` registration, start-up — kept short |
| `EventHandlers.incl`, `Menus.incl` | only if missing | from `src/Templates/App`; the developer's |
| `Windows.incl` | only if missing | generated: `BuildWindows` = `ALSBuildWindow` + a `nibview` per Form part; the runtime loads parts added later |
| `<Entity>Form.xib`, `<Entity>List.xib` | yes | |
| `<Entity> Binding.incl`, `Model Tags.incl`, `Model.json` | yes | |
| `Credits.rtf` | yes | the About text from Project Settings; the standard About box shows it — `ABOUT_BOX_FEATURE.md` |
| runtime `.incl` files | yes | our own code only — never FB toolbox files |

Start-up: `ALSAppStart` (load `Model.json`) → `BuildMenus` → `BuildWindows` → `ALSAppReady`.
The runtime can't call the app's functions (FB needs definition before use, and the
runtime comes first), so `.main` calls them in order.

FB source is written with classic-Mac CR line endings.
