# Api Logic Client

A FutureBasic app that turns an [API Logic Server](https://apilogicserver.github.io/Docs/) project into a native macOS FutureBasic app.

1. Open a SQLite database (**Model → Open SQLite Database…**), or point it at an ALS server / a saved `/metadata?include=attributes` response such as `samples/Northwind/metadata.json`.
2. Browse the resources and attributes.
3. Review and adjust the entity definitions, then **Model → Generate App** writes a complete FB project to `~/ApiLogicClient/<project>/`:
   one XIB per resource, `Model.json`, `Model Tags.incl`, the ALS runtime, and `<project>.fb`.
4. Open `<project>.fb` in FutureBasic and run it: a master-detail app that lists, edits, creates and deletes records through the ALS JSON:API.

| Folder | Contents |
|---|---|
| `src/Generator/` | The FB project for the generator — open `Api Logic Client.fbeproj` in the FB editor |
| `src/Runtime/` | FB code copied into every generated app |
| `docs/` | Design (`design/`), FB reference notes (`reference/`), controls catalog (`controls/`), backlog |
| `tools/` | `fblint.py` (FB coding-rule checks), `sqlite_model.py` (SQLite model reference) |
| `samples/` | Sample ALS metadata (Northwind) |
