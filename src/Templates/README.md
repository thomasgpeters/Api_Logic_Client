# Templates

Starting files for the apps App Builder generates. The Studio copies this folder into its workspace
(`workspace/Templates`, see `Studio Library.incl`), and *Generate App* copies each file into the app only when
it is missing. Once there, it's yours: regenerating never overwrites it (delete it to get a fresh copy).

| Template | Becomes |
|---|---|
| `Project/Settings2.plist` | the app project's build settings (links `-lsqlite3`) |
| `App/App Globals.glbl` | the app's own globals, first in the build order (`isLoggingOn`) |
| `App/EventHandlers.incl` | `DoAppEvent`, `DoMenu`, `DoDialog` and `DoLogin`: the shell's and the pages' handlers, with room for yours |
| `App/Menus.incl` | `BuildMenus`: File, Edit and Records (New Record, Save, Delete, Refresh) |
| `App/Theme.incl` | `ApplyTheme`: the app's colours |
| `App/Rules.incl` | `DeclareRules`: the app's business rules (LogicBank for FutureBasic) |
| `ERD/Model ERD.html` | not copied into apps: the Studio's model diagram page (*Show Model Diagram*) |

`Windows.incl` (`BuildWindows`: the theme, the shell and the pages) follows the same rule, but it is generated
from the model the first time, since it names the app.

Generated every time (`src/AppBuilder/App Generator.incl`): the project's `data.fbproj` (the groups Headers,
Globals, Runtime, Model, Bindings, Pages, Resources, Rules, Controller, View and Main) and the main program,
which stays short:

```
on appevent fn DoAppEvent
on menu fn DoMenu
on dialog fn DoDialog

fn DataOpen( NULL )                    // the project's SQLite database (Model.json)
fn DeclareStudioRules                  // Studio Rules.incl (generated from Rules.json)
fn DeclareRules                        // Rules.incl (yours)
fn LogicActivate                       // saves go through LogicInsert / LogicUpdate / LogicDelete

fn BuildMenus                          // Menus.incl
fn BuildWindows( @"<project>" )        // Windows.incl

HandleEvents
```
