# Templates

Copied into generated apps by the generator (bundled as the `Templates` folder
resource, so nothing here is compiled into the generator).

| Template | Becomes |
|---|---|
| `Project/Settings2.plist` | `<project>.fbeproj/Settings2.plist` — FB build settings (links `-lsqlite3`). |
| `App/EventHandlers.incl` | `DoAppEvent`, `DoMenu`, `DoDialog` — call the runtime's `ALSDo…`; add your handling around them. |
| `App/Menus.incl` | `BuildMenus` — File, Edit, Records. |

All are copied only when missing, so the developer's edits survive regeneration.
`Windows.incl` (`BuildWindows`: the shell window plus a `nibview` per entity Form part)
follows the same rule but is generated from the model, since its `nibview` lines name the parts.

Generated every time (`src/AppBuilder/App Generator.incl`): `data.fbproj` (groups Runtime,
Model, Bindings, Resources, Controller, View, Main) and `<project>.main`, which stays short:

```
gALS…  connection globals
on appevent fn DoAppEvent / on menu fn DoMenu / on dialog fn DoDialog
if ( fn ALSAppStart )
fn BuildMenus
fn BuildWindows( @"<project>" )
fn ALSAppReady
end if
HandleEvents
```
