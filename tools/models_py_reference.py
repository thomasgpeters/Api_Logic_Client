#!/usr/bin/env python3
"""Read an API Logic Server project's model, database/models.py, AS TEXT - the reference for the
FB reader (ALSModelFromModelsPy in src/Enterprise/ALS Model.incl) and its test.

    python3 tools/models_py_reference.py <ALS project folder> [<ALS venv python>]

Current ALS (17.04 and later) writes the model only to database/models.py, in the same place for
any database (checked with `ApiLogicServer create` on Northwind and on the CRM's contacts.sqlite).
The file is generated (sqlacodegen + ALS), regular enough to read line by line - the design of
the C++ Studio's Model::fromModelsPy - and is never run by the Studio.

With the project's Python (the ALS venv), the test also imports the same models with SQLAlchemy
and compares: every class, attribute, primary key and relationship (name, direction, the related
class, its key columns) must be what SQLAlchemy itself sees.

Model shape (the same as ALSModelFromYAML's, plus resource and table):
  { "Employee": { "resource": "Employee", "table": "Employee",
                  "attributes": [ {"name": "Id", "type": "INTEGER", "pk": true}, ... ],
                  "keys": ["Id"],
                  "relationships": [ {"name": "WorksForDepartment", "direction": "toone",
                                      "resource": "Department", "fks": ["WorksForDepartmentId"]}, ... ] } }
"""
import json
import os
import re
import subprocess
import sys

TYPE_NAMES = {'String': 'VARCHAR', 'Text': 'TEXT', 'Integer': 'INTEGER', 'BigInteger': 'BIGINT',
              'SmallInteger': 'SMALLINT', 'Float': 'FLOAT', 'Double': 'DOUBLE', 'DECIMAL': 'DECIMAL',
              'Numeric': 'NUMERIC', 'Boolean': 'BOOLEAN', 'Date': 'DATE', 'DateTime': 'DATETIME',
              'Time': 'TIME', 'LargeBinary': 'BLOB', 'Unicode': 'VARCHAR', 'UnicodeText': 'TEXT'}


def quoted_items(text):
    """every '...' or "..." in text, in order"""
    return re.findall(r"""['"]([^'"]*)['"]""", text)


def read_models_py(text):
    """models.py -> the model. Lines it reads:
         class Order(Base):                         a resource (a class)
             __tablename__ = 'Order'                its table
             _s_collection_name = 'Order'           its API name
             ForeignKeyConstraint(['Country', 'City'], ['Location.country', 'Location.city'])
             Id = Column(Integer, primary_key=True)                 an attribute (type, key)
             Freight : DECIMAL = Column(DECIMAL, ...)               an annotated one
             CustomerId = Column(ForeignKey('Customer.Id'), ...)    a foreign key, in line
             Customer : Mapped["Customer"] = relationship(...)      to one
             OrderList : Mapped[List["Order"]] = relationship(...)  to many
       foreign_keys='[Employee.WorksForDepartmentId]' names a relationship's key columns; else they
       are the child's foreign keys to the parent's table. Table(...) blocks (views) are skipped."""
    model, cls, fk_columns, constraints = {}, None, {}, {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        m = re.match(r'class\s+(\w+)\s*\(\s*Base\b', line)
        if m:
            cls = m.group(1)
            model[cls] = {'resource': cls, 'table': cls, 'attributes': [], 'keys': [], 'relationships': []}
            fk_columns[cls], constraints[cls] = {}, []
            continue
        if raw[:1] not in (' ', '\t'):          # back at the left margin: the class has ended
            cls = None
            continue
        if cls is None:
            continue
        entity = model[cls]
        m = re.match(r'__tablename__\s*=\s*[\'"](.+?)[\'"]', line)
        if m:
            entity['table'] = m.group(1); continue
        m = re.match(r'_s_collection_name\s*=\s*[\'"](.+?)[\'"]', line)
        if m:
            entity['resource'] = m.group(1); continue
        if line.startswith('ForeignKeyConstraint('):
            inner = line[line.index('(') + 1:]
            local_part, _, remote_part = inner.partition('],')
            remote = quoted_items(remote_part)
            constraints[cls].append((quoted_items(local_part), remote[0].split('.')[0] if remote else ''))
            continue
        m = re.match(r'(\w+)\s*(?::\s*[^=]+?)?\s*=\s*relationship\((.*)\)\s*$', line)
        if m:
            name, args = m.group(1), m.group(2)
            target = re.search(r'Mapped\[\s*(List\[)?\s*["\'](\w+)["\']', line)
            rel = {'name': name, 'direction': 'tomany' if target and target.group(1) else 'toone',
                   'resource': target.group(2) if target else ''}
            fk = re.search(r"foreign_keys\s*=\s*['\"]\[([^\]]*)\]['\"]", args)
            if fk:
                rel['fks'] = [c.strip().split('.')[-1] for c in fk.group(1).split(',') if c.strip()]
            back = re.search(r'back_populates\s*=\s*\(?\s*["\'](\w+)["\']', args)
            if back:
                rel['_back'] = back.group(1)
            entity['relationships'].append(rel)
            continue
        m = re.match(r'(\w+)\s*(?::\s*\w+)?\s*=\s*Column\((.*)\)\s*$', line)
        if m:
            name, args = m.group(1), m.group(2)
            attr = {'name': name}
            fk = re.search(r"ForeignKey\(\s*['\"]([^'\"]+)['\"]", args)
            first = args.split(',')[0].strip()
            if first.startswith(("'", '"')):     # Column('db_name', Type, ...): the type comes second
                first = args.split(',')[1].strip() if ',' in args else ''
            tm = re.match(r'(\w+)', first)
            if tm and tm.group(1) in TYPE_NAMES:
                attr['type'] = TYPE_NAMES[tm.group(1)]
            if 'primary_key=True' in args:
                attr['pk'] = True
                entity['keys'].append(name)
            if 'nullable=False' in args:
                attr['required'] = True
            entity['attributes'].append(attr)
            if fk:
                fk_columns[cls][name] = fk.group(1).split('.')[0]      # the column -> the parent's table
            continue

    # the key columns of relationships that did not name them
    table_to_class = {e['table']: c for c, e in model.items()}
    for cls, entity in model.items():
        for rel in entity['relationships']:
            if 'fks' in rel or rel['direction'] != 'toone':
                continue
            parent_table = model.get(rel['resource'], {}).get('table')
            single = [c for c, t in fk_columns[cls].items() if t == parent_table]
            composite = [cols for cols, t in constraints[cls] if t == parent_table]
            rel['fks'] = composite[0] if composite and not single else single
    for cls, entity in model.items():                  # to many: the child's to-one, through back_populates
        for rel in entity['relationships']:
            if rel['direction'] != 'tomany' or 'fks' in rel:
                continue
            child = model.get(rel['resource'], {})
            for crel in child.get('relationships', []):
                # the name alone is not enough: Customer, Employee and Location all have an OrderList
                if crel['direction'] == 'toone' and crel.get('_back') == rel['name'] and crel['resource'] == cls:
                    rel['fks'] = crel.get('fks', [])
            rel.setdefault('fks', [])
    for entity in model.values():
        for rel in entity['relationships']:
            rel.pop('_back', None)
            rel['resource'] = model.get(rel['resource'], {}).get('resource', rel['resource'])
    del table_to_class
    return model


# --- the test: SQLAlchemy's own view of the same models ---------------------------------------
INTROSPECT = r'''
import json, sys
sys.path.insert(0, '.')
from database import models
from sqlalchemy import inspect
out = {}
for mapper in models.Base.registry.mappers:
    cls = mapper.class_
    if cls.__module__ != 'database.models':
        continue
    col_key = {c: p.key for p in mapper.column_attrs for c in p.columns}
    rels = []
    for r in mapper.relationships:
        if r.direction.name == 'MANYTOONE':
            fks = [col_key[c] for c in r.local_columns if c in col_key]
            direction = 'toone'
        else:
            child_keys = {c: p.key for p in r.mapper.column_attrs for c in p.columns}
            fks = [child_keys[c] for c in r.remote_side if c in child_keys]
            direction = 'tomany'
        rels.append({'name': r.key, 'direction': direction, 'resource': getattr(r.mapper.class_, '_s_collection_name', r.mapper.class_.__name__), 'fks': sorted(fks)})
    out[cls.__name__] = {'table': cls.__table__.name, 'attributes': sorted(p.key for p in mapper.column_attrs),
                         'keys': sorted(col_key[c] for c in mapper.primary_key), 'relationships': sorted(rels, key=lambda x: x['name'])}
print(json.dumps(out))
'''


def comparable(model):
    return {c: {'table': e['table'], 'attributes': sorted(a['name'] for a in e['attributes']), 'keys': sorted(e['keys']),
                'relationships': sorted(({**r, 'fks': sorted(r['fks'])} for r in e['relationships']), key=lambda x: x['name'])}
            for c, e in model.items()}


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith('-'):
        print(__doc__); return 2
    project = os.path.abspath(sys.argv[1])
    path = os.path.join(project, 'database', 'models.py')
    if not os.path.exists(path):
        print(f'models_py_reference: no database/models.py in {project}'); return 2
    model = read_models_py(open(path).read())
    if len(sys.argv) < 3:
        print(json.dumps(model, indent=1)); return 0
    truth = json.loads(subprocess.run([sys.argv[2], '-c', INTROSPECT], cwd=project, capture_output=True, text=True, check=True).stdout)
    mine = comparable(model)
    results = []
    def check(name, ok, info=''):
        results.append(ok); print(('PASS  ' if ok else 'FAIL  ') + name + (f'   ({info})' if info and not ok else ''))
    name = os.path.basename(project)
    check(f'{name}: the same classes as SQLAlchemy ({len(truth)})', set(mine) == set(truth), sorted(set(mine) ^ set(truth)))
    for cls in sorted(truth):
        m, t = mine.get(cls, {}), truth[cls]
        for part in ('table', 'attributes', 'keys', 'relationships'):
            if m.get(part) != t[part]:
                check(f'{name}: {cls} {part}', False, f'read {m.get(part)} / SQLAlchemy {t[part]}')
    check(f'{name}: every table, attribute, primary key and relationship (name, direction, resource, key columns) as SQLAlchemy sees them',
          mine == truth)
    failed = results.count(False)
    print(f'models_py_reference ({name}): {len(results)} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
