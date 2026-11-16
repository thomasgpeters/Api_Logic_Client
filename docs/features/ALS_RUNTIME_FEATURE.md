# ALS Runtime (first generated-app runtime)

The original generated-app runtime: a master-detail window over the API Logic
Server JSON:API. It will be replaced by the app shell (navigator, parts, crumbs —
`docs/design/App Shell Design.md`); its client becomes the ALS data source behind
the same data interface as SQLite.

**Where:** `src/Runtime/ALS Client.incl`, `ALS Binding.incl`, `ALS App.incl`.

- **Client:** `GET /api/<Resource>?page[limit]=n`, `POST`, `PATCH /api/<R>/<id>`,
  `DELETE`; JSON:API bodies; bearer token. Login tries `/api/auth/login`, then
  `/api/authentication-User/login` on 404. Requests are asynchronous; replies hop to
  the main thread (`dispatchmain`).
- **Binding:** `Model.json` field maps; saves send only changed attributes;
  JSON nulls created via `[null]` (no NSNull toolbox wrapper).
- **App:** resource list, records table, form, New / Save / Delete (confirmation) /
  Refresh, login bar.
- Not yet built on a Mac.
