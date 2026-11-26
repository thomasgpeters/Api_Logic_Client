#!/usr/bin/env python3
"""
sqlite_model.py - reference implementation of the generator's SQLite model reader.

Reads a SQLite database's own structure and prints the model the generator builds
from it (the same shape as Model.json "resources"), so the FutureBasic
implementation in src/AppBuilder/SQLite Model.incl can be checked against it.

    python3 tools/sqlite_model.py path/to/db.sqlite              # JSON model
    python3 tools/sqlite_model.py path/to/db.sqlite --summary    # one line per entity

Model per entity (table; views are listed with "kind": "view"):
  attributes     [{name, type, notnull, default, pk}]  in column order
  keys           primary-key columns in key order
  keyKind        identity | autoincrement | assigned | none
                 identity       INTEGER PRIMARY KEY (SQLite assigns the rowid)
                 autoincrement  INTEGER PRIMARY KEY AUTOINCREMENT (never reuses ids)
                 assigned       any other key - the user (or a GUID) supplies it
  relationships  [{name, direction, resource, fks, parentKeys}]
                 toone   on the child:  fks = child columns, parentKeys = parent columns
                 tomany  on the parent: same columns, seen from the parent
Names follow API Logic Server conventions: toone = parent name (or the foreign-key
column without "Id" when a child has several keys to the same parent); tomany =
<Child>List (prefixed the same way when there are several).
Standard library only.
"""
import json, re, sqlite3, sys
from collections import defaultdict


def q(name):
    return '"' + name.replace('"', '""') + '"'


def read_model(path):
    db = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    objects = db.execute("SELECT name, type, sql FROM sqlite_master "
                         "WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    resources, foreign_keys = {}, []

    for name, kind, sql in objects:
        cols = db.execute(f'PRAGMA table_info({q(name)})').fetchall()   # cid, name, type, notnull, dflt, pk
        attributes = [{'name': c[1], 'type': c[2] or '', 'notnull': bool(c[3]),
                       'default': c[4], 'pk': c[5]} for c in cols]
        keys = [c[1] for c in sorted((c for c in cols if c[5]), key=lambda c: c[5])]
        key_kind = 'none'
        if keys:
            key_kind = 'assigned'
            sql_u = (sql or '').upper()
            single_int = len(keys) == 1 and next(a['type'] for a in attributes if a['name'] == keys[0]).upper() == 'INTEGER'
            if kind == 'table' and single_int and 'WITHOUT ROWID' not in sql_u:
                key_kind = 'autoincrement' if 'AUTOINCREMENT' in sql_u else 'identity'
        if key_kind in ('identity', 'autoincrement'):
            for a in attributes:
                if a['pk']:
                    a['generated'] = True                  # the Form shows it read-only
        resources[name] = {'kind': kind, 'attributes': attributes, 'keys': keys,
                           'keyKind': key_kind, 'relationships': []}
        if kind != 'table':
            continue
        groups = defaultdict(list)   # id, seq, table, from, to, on_update, on_delete, match
        for fk in db.execute(f'PRAGMA foreign_key_list({q(name)})').fetchall():
            groups[fk[0]].append(fk)
        for fk_id in sorted(groups):
            rows = sorted(groups[fk_id], key=lambda r: r[1])
            foreign_keys.append({'child': name, 'parent': rows[0][2],
                                 'fks': [r[3] for r in rows], 'to': [r[4] for r in rows]})

    for fk in foreign_keys:                      # a missing "to" means the parent's primary key
        parent = resources.get(fk['parent'])
        if parent is None:
            fk['parentKeys'] = [t for t in fk['to']]
            continue
        fk['parentKeys'] = [t if t else parent['keys'][i] if i < len(parent['keys']) else None
                            for i, t in enumerate(fk['to'])]

    per_pair = defaultdict(int)
    for fk in foreign_keys:
        per_pair[(fk['child'], fk['parent'])] += 1
    for fk in foreign_keys:
        child, parent = fk['child'], fk['parent']
        if per_pair[(child, parent)] > 1:        # e.g. Employee.OnLoanDepartmentId / WorksForDepartmentId
            role = re.sub(r'(?i)_?id$', '', fk['fks'][0]) or parent
            prefix = role[:-len(parent)] if role.endswith(parent) else role
            toone, tomany = role, f'{prefix}{child}List'
        else:
            toone, tomany = parent, f'{child}List'
        resources[child]['relationships'].append({'name': toone, 'direction': 'toone', 'resource': parent,
                                                  'fks': fk['fks'], 'parentKeys': fk['parentKeys']})
        if parent in resources:
            resources[parent]['relationships'].append({'name': tomany, 'direction': 'tomany', 'resource': child,
                                                       'fks': fk['fks'], 'parentKeys': fk['parentKeys']})
    for fk in foreign_keys:                      # a single-column foreign key looks its parent up (Dropdown)
        parent = resources.get(fk['parent'])
        if parent is None or len(fk['fks']) != 1 or not fk['parentKeys'][0]:
            continue
        for a in resources[fk['child']]['attributes']:
            if a['name'] == fk['fks'][0]:
                a['lookup'] = {'entity': fk['parent'], 'key': fk['parentKeys'][0],
                               'display': display_attribute(parent, fk['parentKeys'][0])}
    return resources


def display_attribute(parent, key):
    """The column a lookup shows (SQLiteModelDisplayAttribute): name / title / description / label,
    else one whose name contains "name", else the first text column that is not a key, else the key."""
    found = first_text = None
    for a in parent['attributes']:
        lower = a['name'].lower()
        if lower in ('name', 'title', 'description', 'label'):
            return a['name']
        if found is None and 'name' in lower:
            found = a['name']
        if first_text is None and not a['pk'] and ('CHAR' in a['type'].upper() or 'TEXT' in a['type'].upper()):
            first_text = a['name']
    return found or first_text or key


def main(argv):
    if not argv or argv[0].startswith('-'):
        print(__doc__); return 2
    model = read_model(argv[0])
    if '--summary' in argv:
        for name, r in model.items():
            rels = ', '.join(f"{x['name']}({x['direction'][2:]}→{x['resource']})" for x in r['relationships'])
            print(f"{name:22s} {r['kind']:5s} keys={','.join(r['keys']) or '-':14s} {r['keyKind']:13s} {rels}")
    else:
        print(json.dumps({'resources': model}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
