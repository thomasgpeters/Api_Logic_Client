#!/usr/bin/env python3
"""The SQL Generator's two back ends, side by side: the same statement dictionaries become SQL
(src/Runtime/DataObject.incl) or a JSON:API request for API Logic Server
(src/Enterprise/DataObject_JSONAPI.incl). This is the reference for the FB code, and its test:

    python3 tools/jsonapi_reference.py --test <ALS project's db.sqlite> [http://localhost:5656 admin p]

Every query is run both ways - SQL on the server's own SQLite database, JSON:API on the running
server - and the rows must be the same. Then INSERT, UPDATE (with S_CheckSum) and DELETE go through
JSON:API and are read back through SQL. Exits 2 when no server answers (run_tests.sh skips).

The dictionaries use the FB builder's keys: selecttables [{tablename, aliasname}], selectcols
[{columnname, aliasname}], associations [{lefttablealias, leftcolumnname, righttablealias,
rightcolumnname, operator}], filter [{tablealias, columnname, value, type, operator, logic}],
orderby [{tablealias, columnname, descending}]; insertintotable / updatetable / deletefromtable,
columnvalues [{columnname, value, type}], rows, columnnames.
"""
import json
import sqlite3
import sys
import urllib.parse
import urllib.request

# operators and logic, as DataObject.glbl numbers them
IS_EQUAL, IS_NOT_EQUAL, IS_LT, IS_GT, IS_LE, IS_GE, IS_IN, IS_NOT_IN, IS_NULL, IS_NOT_NULL, IS_LIKE, IS_NOT_LIKE = range(1, 13)
AND, OR = 1, 2
NULL_T, INTEGER_T, REAL_T, TEXT_T, BLOB_T = range(1, 6)


# --- the builders (DataObject_Super.incl) ---------------------------------------------------
def init_query():
    return {'selecttables': [], 'selectcols': [], 'associations': [], 'filter': [], 'metadata': [], 'results': {}}

def add_table(q, table, alias): q['selecttables'].append({'tablename': table, 'aliasname': alias})
def add_column(q, column, alias): q['selectcols'].append({'columnname': column, 'aliasname': alias})
def add_association(q, la, lc, ra, rc, op=IS_EQUAL):
    q['associations'].append({'lefttablealias': la, 'leftcolumnname': lc, 'righttablealias': ra, 'rightcolumnname': rc, 'operator': op})
def add_filter(q, alias, column, value, typ, op, logic=0):
    f = {'tablealias': alias, 'columnname': column, 'type': typ, 'operator': op}
    if value is not None: f['value'] = value
    if logic: f['logic'] = logic
    q.setdefault('filter', []).append(f)
def add_order(q, alias, column, descending=False):
    q.setdefault('orderby', []).append({'tablealias': alias, 'columnname': column, 'descending': descending})
def init_write(key, with_filter):
    d = {key: '', 'columnvalues': []}
    if with_filter: d['filter'] = []
    return d
def add_column_value(d, column, value, typ):
    e = {'columnname': column, 'type': typ}
    if value is not None: e['value'] = value
    d['columnvalues'].append(e)


# --- the SQL side (DataObject.incl) ---------------------------------------------------------
def quote(name):
    if not name: return '""'
    if name[0] in '"\'[`': return name
    return '.'.join('"' + p.replace('"', '""') + '"' for p in name.split('.'))

SQL_OPS = {IS_NOT_EQUAL: ' != ?', IS_LT: ' < ?', IS_GT: ' > ?', IS_LE: ' <= ?', IS_GE: ' >= ?', IS_IN: ' IN ( ? )',
           IS_NOT_IN: ' NOT IN ( ? )', IS_NULL: ' IS NULL', IS_NOT_NULL: ' IS NOT NULL', IS_LIKE: ' LIKE ?', IS_NOT_LIKE: ' NOT LIKE ?'}

def where_sql(filters, use_alias, connector):
    if not filters: return ''
    s = connector
    for i, f in enumerate(filters):
        if i: s += ' OR ' if f.get('logic') == OR else ' AND '
        if use_alias: s += quote(f['tablealias']) + '.'
        s += quote(f['columnname']) + SQL_OPS.get(f['operator'], ' = ?')
    return s

def generate_select_sql(q):
    s = 'SELECT ' + ', '.join(quote(c['columnname']) + ' AS ' + quote(c['aliasname']) for c in q['selectcols'])
    s += ' FROM ' + ', '.join(quote(t['tablename']) + ' AS ' + quote(t['aliasname']) for t in q['selecttables'])
    if q['associations']:
        s += ' WHERE ' + ' AND '.join(f"{quote(a['lefttablealias'])}.{quote(a['leftcolumnname'])} = {quote(a['righttablealias'])}.{quote(a['rightcolumnname'])}" for a in q['associations'])
    s += where_sql(q.get('filter'), True, ' AND ' if q['associations'] else ' WHERE ')
    for i, o in enumerate(q.get('orderby') or []):
        s += (' ORDER BY ' if i == 0 else ', ') + (quote(o['tablealias']) + '.' if o.get('tablealias') else '') + quote(o['columnname']) + (' DESC' if o['descending'] else '')
    return s

def parameter_values(d):
    vals = [e.get('value') for e in d.get('columnvalues') or []]
    for r in d.get('rows') or []:
        vals += [r.get(c) for c in d.get('columnnames') or []]
    vals += [f.get('value') for f in d.get('filter') or [] if f['operator'] not in (IS_NULL, IS_NOT_NULL)]
    return vals


# --- the JSON:API side (DataObject_JSONAPI.incl) --------------------------------------------
JSONAPI_OPS = {IS_EQUAL: 'eq', IS_NOT_EQUAL: 'ne', IS_LT: 'lt', IS_GT: 'gt', IS_LE: 'le', IS_GE: 'ge',
               IS_LIKE: 'like', IS_NOT_LIKE: 'notilike', IS_IN: 'in', IS_NOT_IN: 'notin', IS_NULL: 'eq', IS_NOT_NULL: 'ne'}

class Refused(Exception):
    """What ALS cannot express - the FB generator returns NULL and says why (JSONAPILastError)."""

def column_parts(column, default_alias):
    """'p.surName' -> ('p', 'surName'); 'surName' -> (default_alias, 'surName')"""
    return tuple(column.split('.', 1)) if '.' in column else (default_alias, column)

def relationship_name(model, child, parent, fk):
    """The child's to-one relationship to parent through fk, from the model (admin.yaml for an
    ALS project, the SQLite model reader otherwise): a child can have several to the same parent
    (Employee: WorksForDepartment, OnLoanDepartment), so it is never guessed."""
    for r in (model.get(child) or {}).get('relationships') or []:
        if r.get('direction') == 'toone' and r.get('resource') == parent and fk in (r.get('fks') or []):
            return r['name']
    raise Refused(f'the model has no relationship from {child} to {parent} through {fk}')

def json_filters(filters, primary):
    """filter list for ALS; consecutive OR filters on one column with = become one 'in'."""
    out = []
    for f in filters or []:
        if f.get('tablealias') not in (None, '', primary):
            raise Refused(f"ALS filters only the main resource: {f['tablealias']}.{f['columnname']}")
        op, val = f['operator'], f.get('value')
        if f.get('logic') == OR:
            prev = out[-1] if out else None
            if prev and prev['name'] == f['columnname'] and op == IS_EQUAL and prev['op'] in ('eq', 'in'):
                prev['val'] = (prev['val'] if prev['op'] == 'in' else [prev['val']]) + [val]
                prev['op'] = 'in'
                continue
            raise Refused('ALS has no OR: only OR between values of one column (it becomes "in")')
        if op in (IS_NULL, IS_NOT_NULL): val = None
        if op in (IS_IN, IS_NOT_IN) and not isinstance(val, list): val = [val]
        out.append({'name': f['columnname'], 'op': JSONAPI_OPS.get(op, 'eq'), 'val': val})
    return out

def generate_jsonapi_select(q, model):
    """-> {method, path, resource, joins: {alias: (relationship, resource)}}; paging is the sender's."""
    tables = q['selecttables']
    primary = tables[0]['aliasname']
    resource = tables[0]['tablename']
    by_alias = {t['aliasname']: t['tablename'] for t in tables}
    joins = {}
    for a in q['associations']:
        la, ra = a['lefttablealias'], a['righttablealias']
        if la == primary and ra != primary:            # main.fk = parent.key: a parent to include
            joins[ra] = (relationship_name(model, resource, by_alias[ra], a['leftcolumnname']), by_alias[ra])
        elif ra == primary and la != primary:
            joins[la] = (relationship_name(model, resource, by_alias[la], a['rightcolumnname']), by_alias[la])
        else:
            raise Refused('a join must link the main resource to a parent')
    if len(joins) != len(tables) - 1:
        raise Refused('every other table needs a join to the main resource')
    params = []
    filters = json_filters(q.get('filter'), primary)
    if filters: params.append('filter=' + urllib.parse.quote(json.dumps(filters, separators=(',', ':'))))
    sort = []
    for o in q.get('orderby') or []:
        if o.get('tablealias') not in (None, '', primary): raise Refused('ALS sorts only by the main resource')
        sort.append(('-' if o['descending'] else '') + o['columnname'])
    if sort: params.append('sort=' + ','.join(sort))
    if joins: params.append('include=' + ','.join(sorted({rel for rel, _ in joins.values()})))
    return {'method': 'GET', 'path': f'/api/{resource}' + ('?' + '&'.join(params) if params else ''),
            'resource': resource, 'primary': primary, 'joins': joins}

def rows_from_answer(q, request, records, included):
    """JSON:API records -> rows keyed by the column aliases (as a SQL SELECT gives them), plus
    'id' and 'S_CheckSum' of the main record. A row whose parent is missing is dropped: the SQL
    side joins inner."""
    index = {(i['type'], i['id']): i['attributes'] for i in included}
    rows = []
    for rec in records:
        parents, keep = {}, True
        for alias, (rel, res) in request['joins'].items():
            link = ((rec.get('relationships') or {}).get(rel) or {}).get('data')
            attrs = index.get((link['type'], link['id'])) if link else None
            if attrs is None: keep = False
            parents[alias] = attrs
        if not keep: continue
        row = {}
        for c in q['selectcols']:
            alias, col = column_parts(c['columnname'], request['primary'])
            src = rec['attributes'] if alias == request['primary'] else parents[alias]
            row[c['aliasname']] = rec['id'] if col == 'id' and alias == request['primary'] else src.get(col)
        row.setdefault('id', rec['id'])
        row.setdefault('S_CheckSum', rec['attributes'].get('S_CheckSum'))
        rows.append(row)
    return rows

def record_id(d):
    """UPDATE / DELETE: exactly one '=' filter - its value is the record's id."""
    f = d.get('filter') or []
    if len(f) != 1 or f[0]['operator'] != IS_EQUAL:
        raise Refused('an UPDATE or DELETE needs one "=" filter on the record\'s key')
    return str(f[0]['value'])

def attributes_of(entries):
    return {e['columnname']: e.get('value') for e in entries}

def generate_jsonapi_insert(d):
    t = d['insertintotable']
    return {'method': 'POST', 'path': f'/api/{t}', 'body': {'data': {'type': t, 'attributes': attributes_of(d['columnvalues'])}}}

def generate_jsonapi_insert_rows(d):
    t = d['insertintotable']
    return [{'method': 'POST', 'path': f'/api/{t}', 'body': {'data': {'type': t, 'attributes': {c: r.get(c) for c in d['columnnames']}}}} for r in d['rows']]

def generate_jsonapi_update(d):
    t, rid = d['updatetable'], record_id(d)
    return {'method': 'PATCH', 'path': f'/api/{t}/' + urllib.parse.quote(rid, safe=''), 'body': {'data': {'type': t, 'id': rid, 'attributes': attributes_of(d['columnvalues'])}}}

def generate_jsonapi_delete(d):
    t, rid = d['deletefromtable'], record_id(d)
    return {'method': 'DELETE', 'path': f'/api/{t}/' + urllib.parse.quote(rid, safe='')}


# --- the model: ALS's admin.yaml ---------------------------------------------------------------
def read_admin_yaml(text):
    """The small YAML subset admin.yaml is written in (ALS generates it): nested maps by
    indentation, '- ' lists of maps or of scalars, plain or quoted scalars, true / false.
    The reference for the FB reader (ALS Model.incl); checked against PyYAML in --test."""
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'): continue
        lines.append((len(raw) - len(raw.lstrip(' ')), raw.strip()))
    pos = 0

    def scalar(t):
        t = t.strip()
        if len(t) >= 2 and t[0] == t[-1] and t[0] in '\'"': return t[1:-1]
        if t == 'true': return True
        if t == 'false': return False
        try: return int(t)
        except ValueError: return t

    def block(indent):
        nonlocal pos
        if pos >= len(lines): return None
        if lines[pos][1].startswith('- '): return seq(lines[pos][0])
        return mapping(indent)

    def mapping(indent, first=None):
        nonlocal pos
        out = {}
        if first is not None:                      # "- key: value" opened this map
            k, _, v = first.partition(':')
            out[k.strip()] = scalar(v) if v.strip() else block(indent + 1)
        while pos < len(lines) and lines[pos][0] == indent and not lines[pos][1].startswith('- '):
            k, _, v = lines[pos][1].partition(':'); pos += 1
            if v.strip(): out[k.strip()] = scalar(v)
            elif pos < len(lines) and (lines[pos][0] > indent or lines[pos][1].startswith('- ')): out[k.strip()] = block(lines[pos][0])
            else: out[k.strip()] = None
        return out

    def seq(indent):
        nonlocal pos
        out = []
        while pos < len(lines) and lines[pos][0] == indent and lines[pos][1].startswith('- '):
            item = lines[pos][1][2:]; pos += 1
            if ':' in item and not item.startswith(('"', "'")):
                out.append(mapping(indent + 2, item))
            else:
                out.append(scalar(item))
        return out

    return block(0)

def model_from_admin_yaml(admin):
    """resource -> {relationships: [{name, direction, resource, fks}], user_key}: the shape the
    Studio's model already has for a SQLite project (SQLite Model.incl)."""
    return {name: {'relationships': r.get('tab_groups') or [], 'user_key': r.get('user_key')}
            for name, r in (admin.get('resources') or {}).items()}


# --- running both -----------------------------------------------------------------------------
BASE, TOKEN, MODEL, DB = 'http://localhost:5656', None, {}, None
results = []

def http(method, path, body=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body is not None else None, method=method)
    req.add_header('Content-Type', 'application/vnd.api+json' if TOKEN else 'application/json')
    if TOKEN: req.add_header('Authorization', 'Bearer ' + TOKEN)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=20) as r:
            raw = r.read(); return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read(); return e.code, json.loads(raw) if raw else None

def run_jsonapi_select(q, limit=200):
    req = generate_jsonapi_select(q, MODEL)
    sep = '&' if '?' in req['path'] else '?'
    records, included, offset, total = [], [], 0, None
    while total is None or offset < total:
        st, pl = http('GET', f"{req['path']}{sep}page%5Blimit%5D={limit}&page%5Boffset%5D={offset}")
        if st != 200: raise RuntimeError(f'{st} {pl}')
        records += pl['data']; included += pl.get('included') or []; total = pl['meta']['total']
        if not pl['data']: break
        offset += limit
    return rows_from_answer(q, req, records, included), req

def run_sql_select(q):
    vals = parameter_values(q)
    cur = DB.execute(generate_select_sql(q), vals)
    names = [c[0] for c in cur.description]
    return [dict(zip(names, r)) for r in cur.fetchall()]

def norm(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool): return round(float(v), 4)
    try: return round(float(v), 4)            # DECIMAL text in SQLite vs a JSON number
    except (TypeError, ValueError): return v

def same_rows(a, b, cols, ordered):
    ka = [tuple(norm(r.get(c)) for c in cols) for r in a]
    kb = [tuple(norm(r.get(c)) for c in cols) for r in b]
    return ka == kb if ordered else sorted(map(str, ka)) == sorted(map(str, kb))

def check(name, ok, info=''):
    results.append(ok); print(('PASS  ' if ok else 'FAIL  ') + name + (f'   ({info})' if info and not ok else ''))

def both(name, q, ordered=False):
    cols = [c['aliasname'] for c in q['selectcols']]
    sql_rows = run_sql_select(q)
    api_rows, req = run_jsonapi_select(q)
    check(f'{name}: {len(sql_rows)} rows, the same both ways', same_rows(sql_rows, api_rows, cols, ordered) and len(sql_rows) > 0,
          f'sql {len(sql_rows)}, json:api {len(api_rows)}; {req["path"][:120]}')

def refused(name, fn):
    try: fn(); check(name, False, 'not refused')
    except Refused as e: check(name + f' -> refused: {e}', True)


def main():
    global BASE, TOKEN, DB
    if len(sys.argv) < 3 or sys.argv[1] != '--test':
        print(__doc__); return 2
    DB = sqlite3.connect(sys.argv[2])
    if len(sys.argv) > 3: BASE = sys.argv[3].rstrip('/')
    user, pw = (sys.argv[4], sys.argv[5]) if len(sys.argv) > 5 else ('admin', 'p')
    try:
        st, pl = http('POST', '/api/auth/login', {'username': user, 'password': pw})
    except OSError:
        print(f'jsonapi_reference: no server at {BASE} - skipped'); return 2
    TOKEN = pl['access_token']
    # the model: relationships from admin.yaml (/metadata leaves them out on purpose)
    req = urllib.request.Request(BASE + '/ui/admin/admin.yaml')
    text = urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=20).read().decode()
    admin = read_admin_yaml(text)
    try:
        import yaml
        check('admin.yaml: the subset reader reads it as PyYAML does', admin == yaml.safe_load(text))
    except ImportError:
        pass
    MODEL.update(model_from_admin_yaml(admin))
    check('admin.yaml: relationships with their names, directions and keys (Employee -> WorksForDepartment)',
          {'direction': 'toone', 'fks': ['WorksForDepartmentId'], 'name': 'WorksForDepartment', 'resource': 'Department'} in MODEL['Employee']['relationships'])

    q = init_query(); add_table(q, 'Customer', 'c'); add_column(q, 'c.Id', 'ID'); add_column(q, 'c.CompanyName', 'Company')
    add_filter(q, 'c', 'Country', 'Germany', TEXT_T, IS_EQUAL); add_order(q, 'c', 'CompanyName')
    both('= and ORDER BY', q, ordered=True)

    q = init_query(); add_table(q, 'Customer', 'c'); add_column(q, 'c.Id', 'ID'); add_column(q, 'c.Balance', 'Balance')
    add_filter(q, 'c', 'Balance', 1000, REAL_T, IS_GT); add_order(q, 'c', 'Balance', True)
    both('> and ORDER BY DESC', q, ordered=True)

    q = init_query(); add_table(q, 'Customer', 'c'); add_column(q, 'c.Id', 'ID'); add_column(q, 'c.CompanyName', 'Company')
    add_filter(q, 'c', 'CompanyName', 'A%', TEXT_T, IS_LIKE)
    both('LIKE', q)

    q = init_query(); add_table(q, 'Customer', 'c'); add_column(q, 'c.Id', 'ID'); add_column(q, 'c.Region', 'Region')
    add_filter(q, 'c', 'Region', None, TEXT_T, IS_NULL)
    both('IS NULL', q)

    q = init_query(); add_table(q, 'Customer', 'c'); add_column(q, 'c.Id', 'ID')
    add_filter(q, 'c', 'Region', None, TEXT_T, IS_NOT_NULL); add_filter(q, 'c', 'Country', 'USA', TEXT_T, IS_EQUAL, AND)
    both('IS NOT NULL AND =', q)

    q = init_query(); add_table(q, 'Customer', 'c'); add_column(q, 'c.Id', 'ID'); add_column(q, 'c.Country', 'Country')
    add_filter(q, 'c', 'Country', 'Mexico', TEXT_T, IS_EQUAL); add_filter(q, 'c', 'Country', 'Spain', TEXT_T, IS_EQUAL, OR)
    both('OR on one column (JSON:API: in)', q)

    q = init_query(); add_table(q, 'Order', 'o'); add_table(q, 'Customer', 'c')
    add_column(q, 'o.Id', 'Order'); add_column(q, 'c.CompanyName', 'Company'); add_column(q, 'o.AmountTotal', 'Total')
    add_association(q, 'o', 'CustomerId', 'c', 'Id'); add_filter(q, 'o', 'ShippedDate', None, TEXT_T, IS_NULL)
    add_order(q, 'o', 'Id')
    both('a join to the parent (JSON:API: include=Customer), unshipped orders', q, ordered=True)

    q = init_query(); add_table(q, 'Employee', 'e'); add_table(q, 'Department', 'd')
    add_column(q, 'e.LastName', 'Employee'); add_column(q, 'd.DepartmentName', 'Works For')
    add_association(q, 'e', 'WorksForDepartmentId', 'd', 'Id'); add_order(q, 'e', 'LastName')
    both('a role-named relationship from the model (include=WorksForDepartment)', q, ordered=True)

    refused('OR across two columns', lambda: generate_jsonapi_select(
        (lambda q: (add_table(q, 'Customer', 'c'), add_column(q, 'c.Id', 'ID'), add_filter(q, 'c', 'Country', 'Spain', TEXT_T, IS_EQUAL),
                    add_filter(q, 'c', 'City', 'Berlin', TEXT_T, IS_EQUAL, OR), q)[-1])(init_query()), MODEL))
    refused('a filter on the joined parent', lambda: generate_jsonapi_select(
        (lambda q: (add_table(q, 'Order', 'o'), add_table(q, 'Customer', 'c'), add_column(q, 'o.Id', 'Order'),
                    add_association(q, 'o', 'CustomerId', 'c', 'Id'), add_filter(q, 'c', 'Country', 'Spain', TEXT_T, IS_EQUAL), q)[-1])(init_query()), MODEL))
    refused('an UPDATE without a filter', lambda: generate_jsonapi_update((lambda d: (d.update(updatetable='Category'), add_column_value(d, 'Description', 'x', TEXT_T), d)[-1])(init_write('updatetable', True))))

    # writes through JSON:API, read back through SQL. The statements name RESOURCES (what an
    # Enterprise app's model holds); the server maps them to tables - Northwind's Category lives
    # in CategoryTableNameTest, on purpose. Only these direct read-backs need the table's name.
    table = 'CategoryTableNameTest'
    d = init_write('insertintotable', False); d['insertintotable'] = 'Category'
    add_column_value(d, 'CategoryName_ColumnName', 'JSON:API reference', TEXT_T); add_column_value(d, 'Description', 'one row', TEXT_T)
    r = generate_jsonapi_insert(d); st, pl = http(r['method'], r['path'], r['body'])
    new_id = pl['data']['id'] if st == 201 else None
    seen = DB.execute(f'SELECT "CategoryName_ColumnName" FROM "{table}" WHERE "Id" = ?', [new_id]).fetchone()
    check('INSERT through JSON:API, read back through SQL', st == 201 and seen == ('JSON:API reference',), (st, seen))

    d = {'insertintotable': 'Category', 'rows': [{'CategoryName_ColumnName': 'rows A'}, {'CategoryName_ColumnName': 'rows B', 'Description': 'b'}], 'columnnames': ['CategoryName_ColumnName', 'Description']}
    made = [http(r['method'], r['path'], r['body']) for r in generate_jsonapi_insert_rows(d)]
    ids = [pl['data']['id'] for st, pl in made if st == 201]
    check('INSERT of an array of dictionaries: one POST per row', len(ids) == 2, [st for st, _ in made])

    st, pl = http('GET', f'/api/Category/{new_id}')
    d = init_write('updatetable', True); d['updatetable'] = 'Category'
    add_column_value(d, 'Description', 'updated', TEXT_T); add_column_value(d, 'S_CheckSum', pl['data']['attributes']['S_CheckSum'], TEXT_T)
    add_filter(d, '', 'Id', new_id, INTEGER_T, IS_EQUAL)
    r = generate_jsonapi_update(d); st, _ = http(r['method'], r['path'], r['body'])
    seen = DB.execute(f'SELECT "Description" FROM "{table}" WHERE "Id" = ?', [new_id]).fetchone()
    check('UPDATE through JSON:API (with S_CheckSum), read back through SQL', st == 200 and seen == ('updated',), (st, seen))

    for rid in [new_id] + ids:
        d = init_write('deletefromtable', True); d['deletefromtable'] = 'Category'; add_filter(d, '', 'Id', rid, INTEGER_T, IS_EQUAL)
        r = generate_jsonapi_delete(d); http(r['method'], r['path'])
    left = DB.execute(f'SELECT count(*) FROM "{table}" WHERE "Id" IN ({",".join("?" * (len(ids) + 1))})', [new_id] + ids).fetchone()[0]
    check('DELETE through JSON:API: gone in SQL', left == 0, left)

    failed = results.count(False)
    print(f'jsonapi_reference: {len(results)} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
