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
- `docs/` — `FB Documentation Map.md`, `FB Reference Index.md`, `BACKLOG.md`.

Generated output goes to `~/ApiLogicClient/<project>/`.

## Conventions
- FB source files use classic-Mac **CR** line endings. Preserve them
  (convert to LF to edit, back to CR before committing). XIB/JSON use LF.
- Logging is gated on `isLoggingOn`.
- FB 7.1.4+: any fn that returns a value must declare a return type
  (`local fn Name(...) as Type`); untyped functions are `void`.
- Never copy FB toolbox files into generated projects — they are FB-team code
  with no redistribution license; generated apps use the user's FB install.

## References
- **Primary: https://github.com/thomasgpeters/FutureBasic_Documentation**
  (private, ~54 MB): the current FB reference manual (`FBHelp/`), all toolbox
  headers (`Toolboxes/Headers/`) and 578 examples (`FBExamples/`). Clone it
  beside this repo and read it in chunks; `docs/FB Documentation Map.md` says
  where things are. Verify toolbox calls against its headers, not memory.
- `docs/FB Reference Index.md` maps keywords to reference pages (same page names
  locally). The online manual is the fallback:
  https://www.brilorsoftware.com/fb/documentation/FBHelp/FBHelp.htm (bot
  protection; fetch single pages only; needs the `Api_Logic_Client` environment).
- FB release notes (breaking changes):
  https://www.brilorsoftware.com/fb/pdfs/releasenotes.pdf.
- https://github.com/thomasgpeters/Test_Xib_View — the author's earlier
  SQLite + XIB app pattern.
- `futurebasic-apis` is outdated (pre-7.0.35); don't rely on it.
