# Api Logic Client

A **FutureBasic** (FBE, macOS/Cocoa) generator — not C++/Wt. It reads an
API Logic Server (ALS) project's model (`/metadata?include=attributes`) and
generates a complete FutureBasic app for it: XIB screens, an ALS JSON:API
client, and logic binding the API to the UI. Northwind is only the test model.

## Repo layout
- `Generator/` — the FB project (`Api Logic Client.fbeproj`). Self-contained so
  the relative paths in `data.fbproj` keep working.
  - `data.fbproj` is the build order: an `.incl` must come *before* any file
    that calls it (FB needs definition before use).
  - `API Interface.incl` — ALS connectivity for the generator itself (metadata fetch).
  - `Project Actions.incl` — model loading (`InitProject`, `OpenMetadataFile`), `BuildProjectXIBs`.
  - `XIB Generator.incl` — type → control mapping; `<Resource>View.xib`, `Model Tags.incl`, model entries.
  - `App Generator.incl` — the pipeline: `Model.json`, `<project>.fb`, runtime copies.
- `Runtime/` — our FB code copied into every generated app (bundled as
  resources of the generator): `ALS Client.incl` (JSON:API client),
  `ALS Binding.incl` (record ↔ controls via Model.json field maps),
  `ALS App.incl` (master-detail window, requests, events).
- `Samples/Northwind/metadata.json` — sample `/metadata` response.
- `docs/` — `FB Reference Index.md` and other notes.

Generated output goes to `~/ApiLogicClient/<project>/`.

## Conventions
- FB source files use classic-Mac **CR** line endings. Preserve them
  (convert to LF to edit, back to CR before committing). XIB/JSON use LF.
- Logging is gated on `isLoggingOn`.
- Never copy FB toolbox files into generated projects — they are FB-team code
  with no redistribution license; generated apps use the user's FB install.

## References
- **FB language reference**:
  https://www.brilorsoftware.com/fb/documentation/FBHelp/FBHelp.htm.
  `docs/FB Reference Index.md` maps every keyword to its page. Fetch single
  pages on demand (the site has bot protection; don't crawl it). Needs the
  `Api_Logic_Client` cloud environment, which allows brilorsoftware.com.
- Cocoa toolboxes (exact `fn` wrapper names/signatures; statement syntax in the
  header comments) and ~570 examples:
  https://github.com/thomasgpeters/futurebasic-apis (`CocoaUI/*.incl`, `FB Examples/`).
  Verify toolbox calls there rather than from memory.
- https://github.com/thomasgpeters/Test_Xib_View — the author's earlier
  SQLite + XIB app pattern.
