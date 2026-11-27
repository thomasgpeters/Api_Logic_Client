"""Load a sample's data files through its business rules - shared by samples/*/build_db.py.

A sample's data is plain SQL in two files (as on the C++ side: schema and data apart):
    lookup.sql   the reference data that stays (tariffs, countries, plan offers ...)
    sample.sql   the demo scenario (customers, declarations, trips ...) - purge_sample.sql removes it
Each holds INSERTs of the columns people type; the columns the rules derive are left out.

The rows are read as written (the SQL runs into an empty copy of the schema, with no rules), then put in
again, table by table, through the rules - so every derived value is the rules' own:
    defer      columns that point at rows loaded later (a country's preferred agreement): set by an
               update once those rows are in
    initial    a status the rules guard (a trip bought, an entry released, a truck out of the gate): the
               row goes in with the first status, and moves to its own status at the end, in the order of
               `finalize` - as it would in the app
"""
import sqlite3


def read_rows(schema_path, sql_path):
    """table -> [ row dicts ] in the file's order"""
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.executescript(open(schema_path).read())
    db.execute('PRAGMA foreign_keys = OFF')
    db.executescript(open(sql_path).read())
    rows = {}
    for (table,) in db.execute("select name from sqlite_master where type='table'"):
        rows[table] = [dict(r) for r in db.execute(f'select * from "{table}" order by rowid')]
    db.close()
    return rows


def replay(logic, data, rows, tables, defer=None, initial=None):
    """insert the rows of these tables through the rules; returns the updates still to make
    ([ (table, record) ] for deferred columns, and { table: [ record ] } for final statuses)"""
    defer, initial = defer or {}, initial or {}
    later, finals = [], {}
    for table in tables:
        keys = data.model[table]['keys']
        for row in rows.get(table, []):
            record = {c: v for c, v in row.items() if v is not None}
            for column in defer.get(table, []):
                if column in record:
                    later.append((table, {**{k: row[k] for k in keys}, column: record.pop(column)}))
            for column, first in initial.get(table, {}).items():
                if record.get(column, first) != first:
                    finals.setdefault(table, []).append({**{k: row[k] for k in keys}, column: record[column]})
                record[column] = first
            if not logic.insert(table, record):
                raise SystemExit(f'build_db: {table} {[row[k] for k in keys]} was refused by the rules: {logic.message}')
    return later, finals


def apply(logic, updates, what):
    for table, record in updates:
        if not logic.update(table, dict(record)):
            raise SystemExit(f'build_db: {what} {table} {record} was refused by the rules: {logic.message}')
