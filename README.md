# Api Logic Client

A FutureBasic app that turns an [API Logic Server](https://apilogicserver.github.io/Docs/) project into a native macOS FutureBasic app.

1. Point it at an ALS server (or open a saved `/metadata?include=attributes` response, e.g. `Samples/Northwind/metadata.json`).
2. Browse the resources and attributes.
3. **XIBs → Generate App** writes a complete FB project to `~/ApiLogicClient/<project>/`:
   one XIB per resource, `Model.json`, `Model Tags.incl`, the ALS runtime, and `<project>.fb`.
4. Open `<project>.fb` in FutureBasic and run it: a master-detail app that lists, edits, creates and deletes records through the ALS JSON:API.

| Folder | Contents |
|---|---|
| `Generator/` | The FB project for the generator |
| `Runtime/` | FB code copied into every generated app |
| `Samples/` | Sample ALS metadata |
| `docs/` | Reference notes |
