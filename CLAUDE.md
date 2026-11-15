# Api Logic Client

A **FutureBasic** (FBE, macOS/Cocoa) app — not C++/Wt. It introspects an
API Logic Server (ALS) app via `/metadata?include=attributes` and generates
a FutureBasic app from that model: an ALS connection layer plus XIB screens.
Northwind (`example_proj.json`) is the first target model.

## Layout
- `Api Logic Client.fbeproj/data.fbproj` — build order. New `.incl` files must
  be added here, *before* any file that calls them (FB needs definition before use).
- `My Globals.glbl` — constants and globals.
- `API Interface.incl` — ALS connectivity (login → bearer token, metadata fetch).
- `Project Actions.incl` — model loading (`InitProject`), browsing, `BuildProjectXIBs`,
  `OpenMetadataFile` (load a saved metadata JSON, no server needed).
- `XIB Generator.incl` — type → control mapping, writes `<Resource>View.xib`
  and `Generated Tags.glbl` to `~/ApiLogicClient/<project>/`.
- `Button/Label/TextField/View/Window.xib` — single-control XIB templates.

## Conventions
- Source files use classic-Mac **CR** line endings. Preserve them
  (convert to LF to edit, back to CR before committing).
- Logging is gated on `isLoggingOn`.

## References
- **FB language reference** (statements, functions, types, directives):
  https://www.brilorsoftware.com/fb/documentation/FBHelp/FBHelp.htm.
  `docs/FB Reference Index.md` maps every keyword to its page. Fetch single
  pages on demand (the site has bot protection; don't crawl it). Needs the
  `Api_Logic_Client` cloud environment, which allows brilorsoftware.com.
- Cocoa toolboxes (exact `fn` wrapper names/signatures) and ~570 examples:
  https://github.com/thomasgpeters/futurebasic-apis (`CocoaUI/*.incl`, `FB Examples/`).
  Verify toolbox calls there rather than from memory.
- A separate SQLite-backed FB app shows the record → view pattern
  (`Get…Record` / `Populate…View`) the generated apps should follow.
