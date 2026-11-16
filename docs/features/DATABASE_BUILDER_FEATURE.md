# Database Builder

Builds or rebuilds a SQLite database from SQL files or from an ALS model. Lives in
**Test_Xib_View** (`Database/`); the generator will offer the same for generated apps.

```bash
python3 Database/build_db.py --out ~/Desktop/contacts.sqlite            # schema.sql + seed.sql
python3 Database/build_db.py --als http://localhost:5656 --user admin --password p --with-data --out app.sqlite
python3 Database/build_db.py --als metadata.json --out app.sqlite
```

- `schema.sql` / `seed.sql` are the source of truth; `--als` writes the generated
  tables to `schema.als.sql` for review; `--with-data` copies records through the
  JSON:API (login: `/api/auth/login`, then `/api/authentication-User/login`).
- Builds into a temporary file and swaps it in; keeps `<name>.bak`; standard library only.
- ALS `/metadata` has no key information, so ALS-built tables have no primary keys
  unless the metadata marks them.
