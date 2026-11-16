# Generate Commands

**Where:** *Model* menu (`src/Generator/Menus.incl`, `EventHandlers.incl`),
`GenerateProjectParts` in `Project Actions.incl`, `AppGenerate` in `App Generator.incl`.

| Command | Key | Writes |
|---|---|---|
| Generate XIBs | ⌘X | every entity's Form and List parts + `Model Tags.incl` |
| Generate XIB for Selected Entity | ⌘E | that entity's two parts |
| Generate Binding Code | ⌘B | `<Entity> Binding.incl` for every entity |
| Generate App | ⌘G | all of the above + `Model.json`, `<project>.fb`, runtime copies |

Output: `~/Library/Application Support/Api_Logic_Client/workspace/<project>/` (the workspace — see `docs/design/Generator App Design.md`;
*Model → Show Workspace in Finder* opens it). Every entity's model entry is always built
(tags and sizes are needed by binding code and `Model.json`); only the requested
files are written.

## Generated project

| File | Regenerated | Notes |
|---|---|---|
| `<project>.fb` | yes | single-file program: `include` runtime + tags + bindings, `include resources` XIBs + `Model.json` |
| `<Entity>Form.xib`, `<Entity>List.xib` | yes | |
| `<Entity> Binding.incl`, `Model Tags.incl`, `Model.json` | yes | |
| runtime `.incl` files | yes | our own code only — never FB toolbox files |
| hook files (planned) | only if missing | hand-written code |

FB source is written with classic-Mac CR line endings.
