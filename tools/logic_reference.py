#!/usr/bin/env python3
"""
Reference implementation of LogicBank for FutureBasic's engine core, for checking the
FB runtime's behaviour: src/Runtime/Logic Rules.incl, Logic Row.incl, Logic Engine.incl.

It follows the FB code function by function (same names, same order of work) on the
same SQLite database, so a scenario that passes here describes what the FB engine must
do. Clean-room: written from LogicBank's documented behaviour, not its code.

    python3 tools/logic_reference.py --test  <copy of a Northwind db.sqlite>
    python3 tools/logic_reference.py --prove <copy of a Northwind db.sqlite>

--prove runs the scenarios once per rule with that one rule left out: each rule must make
at least one scenario fail (otherwise nothing tests it). Imagery LogicBank Studio's rule
lifecycle asks the same of a rule's insert / update / delete / upsert cases.

The test works on a temporary copy and never changes the given file.
"""
import os
import shutil
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite_model  # noqa: E402

NULL = None
OMIT = set()        # --prove: rules left out ("formula OrderDetail.Amount", ...)
DECLARED = []       # every rule declared, in order (for --prove)


def declared(label):
    if label not in DECLARED:
        DECLARED.append(label)
    return label not in OMIT


def q(name):  # QuoteSQLName (DataObject_Super.incl)
    if not name:
        return '""'
    if name[0] in '"\'[`':
        return name
    return '.'.join('"' + p.replace('"', '""') + '"' for p in name.split('.'))


class Data:
    """Data SQLite.incl + Data Model.incl + Data Records.incl"""

    def __init__(self, path):
        self.model = sqlite_model.read_model(path)
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.depth = 0            # gDataTransactionDepth
        self.rollback_only = False  # gDataRollbackOnly

    # Data SQLite.incl
    def begin(self):
        if self.depth == 0:
            self.db.execute('BEGIN IMMEDIATE')
            self.rollback_only = False
        self.depth += 1
        return True

    def end(self, keep):
        if self.depth == 0:
            return False
        if not keep:
            self.rollback_only = True
        self.depth -= 1
        if self.depth > 0:
            return not self.rollback_only
        if self.rollback_only:
            self.db.execute('ROLLBACK')
            return False
        self.db.execute('COMMIT')
        return True

    # Data Model.incl
    def columns(self, entity):
        return [a['name'] for a in self.model[entity]['attributes']] if entity in self.model else []

    def keys(self, entity):
        return self.model[entity].get('keys', [])

    def key_generated(self, entity):
        return self.model[entity].get('keyKind') in ('identity', 'autoincrement')

    # Data Records.incl
    def key_values(self, entity, record):
        return {k: record.get(k) for k in self.keys(entity)}

    def fetch(self, entity, flt=None):
        sql = 'SELECT ' + ', '.join(f'{q(c)} AS {q(c)}' for c in self.columns(entity)) + f' FROM {q(entity)} AS {q("t")}'
        params = []
        for i, (c, v) in enumerate((flt or {}).items()):
            sql += (' WHERE ' if i == 0 else ' AND ') + f'{q("t")}.{q(c)}' + (' IS NULL' if v is None else ' = ?')
            if v is not None:
                params.append(v)
        return [dict(r) for r in self.db.execute(sql, params)]

    def fetch_one(self, entity, flt):
        rows = self.fetch(entity, flt)
        return rows[0] if rows else None

    def relationship(self, entity, name):
        return next((r for r in self.model[entity]['relationships'] if r['name'] == name), None) if entity in self.model else None

    def parent(self, entity, record, role):
        rel = self.relationship(entity, role)
        if rel is None:
            return None
        flt = {}
        for fk, pk in zip(rel['fks'], rel['parentKeys']):
            if record.get(fk) is None:
                return None
            flt[pk] = record[fk]
        return self.fetch_one(rel['resource'], flt)

    def insert(self, entity, record):
        gen, keys = self.key_generated(entity), self.keys(entity)
        cols = [c for c in self.columns(entity) if c in record and not (gen and c in keys and record[c] is None)]
        try:
            self.db.execute(f'INSERT INTO {q(entity)} ( {", ".join(q(c) for c in cols)} ) VALUES ( {", ".join("?" * len(cols))} )',
                            [record[c] for c in cols])
        except sqlite3.Error:      # as DataExecute: the statement failed, DataInsert returns NO
            return False
        if gen and len(keys) == 1 and record.get(keys[0]) is None:
            record[keys[0]] = self.db.execute('select last_insert_rowid()').fetchone()[0]
        return True

    def update(self, entity, record, key_values):
        cols = [c for c in self.columns(entity) if c in record]
        where = ' AND '.join(f'{q(k)} = ?' for k in key_values)
        try:
            cur = self.db.execute(f'UPDATE {q(entity)} SET {", ".join(q(c) + " = ?" for c in cols)} WHERE {where}',
                                  [record[c] for c in cols] + list(key_values.values()))
        except sqlite3.Error:
            return -1
        return cur.rowcount

    def delete(self, entity, key_values):
        where = ' AND '.join(f'{q(k)} = ?' for k in key_values)
        try:
            return self.db.execute(f'DELETE FROM {q(entity)} WHERE {where}', list(key_values.values())).rowcount
        except sqlite3.Error:
            return -1


class Logic:
    """Logic Rules.incl + Logic Row.incl + Logic Engine.incl"""

    def __init__(self, data):
        self.data = data
        self.rules = {}        # gLogicRules
        self.active = False    # gLogicActive
        self.message = ''      # gLogicMessage
        self.nest = 0          # gLogicNest
        self.log = []

    # Logic Rules.incl
    def entity_rules(self, entity):
        return self.rules.setdefault(entity, {'formulas': [], 'constraints': [], 'aggregates': []})

    def formula(self, entity, attr, fn, depends_on):
        if not declared(f'formula {entity}.{attr}'):
            return
        self.entity_rules(entity)['formulas'].append({'entity': entity, 'attr': attr, 'fn': fn, 'dependsOn': depends_on or []})
        self.active = False

    def constraint(self, entity, fn, message):
        if not declared(f'constraint {entity}: {message}'):
            return
        self.entity_rules(entity)['constraints'].append({'entity': entity, 'fn': fn, 'message': message})

    def aggregate(self, kind, parent, parent_attr, list_name, child_attr, where):
        if not declared(f'{kind} {parent}.{parent_attr}'):
            return
        # declared on the parent; activation files it under the child (LogicResolveAggregate)
        self.entity_rules(parent).setdefault('declared', []).append(
            {'kind': kind, 'entity': parent, 'attr': parent_attr, 'list': list_name, 'childAttr': child_attr, 'where': where})
        self.active = False

    def sum(self, parent, parent_attr, list_name, child_attr, where=None):
        self.aggregate('sum', parent, parent_attr, list_name, child_attr, where)

    def count(self, parent, parent_attr, list_name, where=None):
        self.aggregate('count', parent, parent_attr, list_name, None, where)

    def resolve_aggregate(self, agg):
        rel = self.data.relationship(agg['entity'], agg['list'])
        if rel is None or rel['direction'] != 'tomany':
            self.log.append(f"{agg['entity']} has no child list {agg['list']}")
            return False
        child = rel['resource']
        role = next((r['name'] for r in self.data.model[child]['relationships']
                     if r['direction'] == 'toone' and r['resource'] == agg['entity'] and r['fks'] == rel['fks']), None)
        if agg['attr'] not in self.data.columns(agg['entity']) or (agg['childAttr'] and agg['childAttr'] not in self.data.columns(child)):
            self.log.append(f"unknown attribute in {agg['kind']} {agg['entity']}.{agg['attr']}")
            return False
        resolved = dict(agg, child=child, role=role, fks=rel['fks'], parentKeys=rel['parentKeys'])
        self.entity_rules(child)['aggregates'].append(resolved)
        return True

    def derived(self, entity):
        # the entity's sum / count attributes: maintained by the engine only (LB-41)
        return {a['attr']: a['kind'] for a in self.rules.get(entity, {}).get('declared', [])}

    def protect_derived(self, entity, record, old, chained):
        for attr, kind in self.derived(entity).items():
            if old is None:                       # a new parent has no children yet
                record[attr] = 0 if kind == 'count' else 0.0
            elif not chained and record.get(attr) != old.get(attr):
                record[attr] = old.get(attr)      # a client may not write a derived total
                self.log.append(f'{entity}.{attr} is derived by the rules: kept the stored value')

    def rules_of(self, entity, kind):
        return self.rules.get(entity, {}).get(kind, [])

    def check_names(self, rule):
        cols = self.data.columns(rule['entity'])
        if not cols:
            return False
        if 'attr' in rule and rule['attr'] not in cols:
            return False
        return all('.' in d or d in cols for d in rule.get('dependsOn', []))

    def order_formulas(self, entity):
        formulas = self.entity_rules(entity)['formulas']
        derived = [f['attr'] for f in formulas]
        ordered, progress = [], True
        while progress and len(ordered) < len(formulas):
            progress = False
            for f in formulas:
                if f['attr'] in derived:
                    if all(d == f['attr'] or d not in derived for d in f['dependsOn']):
                        ordered.append(f)
                        derived.remove(f['attr'])
                        progress = True
        if len(ordered) < len(formulas):
            self.log.append(f'cycle in {entity}: {", ".join(derived)}')
            return False
        self.entity_rules(entity)['formulas'] = ordered
        return True

    def activate(self):
        ok = True
        for entity in list(self.rules):
            self.entity_rules(entity)['aggregates'] = []
        for entity in list(self.rules):
            for agg in self.rules[entity].get('declared', []):
                ok = self.resolve_aggregate(agg) and ok
        for entity in list(self.rules):
            for kind in ('formulas', 'constraints'):
                ok = all(self.check_names(r) for r in self.rules_of(entity, kind)) and ok
            ok = self.order_formulas(entity) and ok
        self.active = ok
        return ok

    # Logic Row.incl
    @staticmethod
    def new_row(entity, record, old, verb, nest):
        return {'entity': entity, 'row': record, 'old': old, 'verb': verb, 'nest': nest}

    @staticmethod
    def value(lr, attr):
        return lr['row'].get(attr)

    @staticmethod
    def number(lr, attr):
        v = lr['row'].get(attr)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def changed(lr, attr):
        if lr['verb'] == 'insert':
            return True
        return lr['row'].get(attr) != (lr['old'] or {}).get(attr)

    def parent_value(self, lr, role, attr):
        cache = lr.setdefault('parents', {})
        if role not in cache:
            cache[role] = self.data.parent(lr['entity'], lr['row'], role)
        p = cache[role]
        return None if p is None else p.get(attr)

    def role_changed(self, lr, role):
        if lr['verb'] == 'insert':
            return True
        rel = self.data.relationship(lr['entity'], role)
        return rel is not None and any(lr['row'].get(fk) != (lr['old'] or {}).get(fk) for fk in rel['fks'])

    def format_message(self, lr, template):
        for c in self.data.columns(lr['entity']):
            v = lr['row'].get(c)
            text = '' if v is None else str(v)
            template = template.replace('{row.%s}' % c, text).replace('{%s}' % c, text)
        return template

    # Logic Engine.incl
    def logline(self, lr, text):
        self.log.append('    ' * lr['nest'] + f"{lr['verb']} {lr['entity']} - {text}")

    def formula_pruned(self, lr, f):
        if lr['verb'] != 'update' or not f['dependsOn']:
            return False
        for d in f['dependsOn']:
            if '.' in d:
                if self.role_changed(lr, d.split('.')[0]):
                    return False
            elif self.changed(lr, d):
                return False
        return True

    def run_formulas(self, lr):
        for f in self.rules_of(lr['entity'], 'formulas'):
            if self.formula_pruned(lr, f):
                self.logline(lr, f"formula {f['attr']} pruned (inputs unchanged)")
                continue
            v = f['fn'](lr)
            if v != lr['row'].get(f['attr']):
                lr['row'][f['attr']] = v
                self.logline(lr, f"formula {f['attr']} = {v}")

    def run_constraints(self, lr):
        for c in self.rules_of(lr['entity'], 'constraints'):
            if not c['fn'](lr):
                self.message = self.format_message(lr, c['message'])
                self.logline(lr, f'constraint failed: {self.message}')
                return False
        return True

    @staticmethod
    def parent_key(agg, record):
        if record is None:
            return None
        values = tuple(record.get(fk) for fk in agg['fks'])
        return None if any(v is None for v in values) else values

    def contribution(self, agg, view):
        # what one child row adds to the parent's aggregate (0 when it does not qualify)
        if view is None:
            return 0
        if agg['where'] is not None and not agg['where'](view):
            return 0
        if agg['kind'] == 'count':
            return 1
        v = view['row'].get(agg['childAttr'])
        return 0 if v is None else float(v)

    def adjust_parents(self, lr):
        # delta adjustment: never re-query a sum; one parent write per parent row
        deltas = {}   # (parent entity, parent key) -> {attr: delta}
        new_view = None if lr['verb'] == 'delete' else lr
        old_view = None if lr['verb'] == 'insert' else self.new_row(lr['entity'], dict(lr['old']), None, lr['verb'], lr['nest'])

        def add(parent, key, attr, delta):
            if key is not None and delta:
                d = deltas.setdefault((parent, key), {})
                d[attr] = d.get(attr, 0) + delta

        for agg in self.rules_of(lr['entity'], 'aggregates'):
            new_key = self.parent_key(agg, None if new_view is None else new_view['row'])
            old_key = self.parent_key(agg, None if old_view is None else old_view['row'])
            new_c, old_c = self.contribution(agg, new_view), self.contribution(agg, old_view)
            if new_key is not None and new_key == old_key:
                add(agg['entity'], new_key, agg['attr'], new_c - old_c)
            else:   # inserted, deleted, or moved to another parent (re-parenting adjusts both)
                add(agg['entity'], new_key, agg['attr'], new_c)
                add(agg['entity'], old_key, agg['attr'], -old_c)
        for (parent, key), changes in deltas.items():
            agg = next(a for a in self.rules_of(lr['entity'], 'aggregates') if a['entity'] == parent)
            flt = dict(zip(agg['parentKeys'], key))
            stored = self.data.fetch_one(parent, flt)
            if stored is None:
                continue
            record = dict(flt)
            for attr, delta in changes.items():
                record[attr] = (stored.get(attr) or 0) + delta
            self.logline(lr, f'adjust {parent} {key}: {changes}')
            if not self.update(parent, record, flt, chained=True):
                return False
        return True

    def row_logic(self, lr):
        self.run_formulas(lr)
        return self.adjust_parents(lr) and self.run_constraints(lr)

    def ready(self):
        if self.active:
            return True
        self.message = 'The business rules are not active (LogicActivate).'
        return False

    def insert(self, entity, record):
        self.message = ''
        if not self.ready() or not self.data.begin():
            return False
        self.protect_derived(entity, record, None, False)
        lr = self.new_row(entity, record, None, 'insert', self.nest)
        self.nest += 1
        ok = self.row_logic(lr) and self.data.insert(entity, record)
        self.nest -= 1
        return self.data.end(ok)

    def update(self, entity, record, key_values=None, chained=False):
        if not chained:
            self.message = ''
        if self.nest > 20:
            self.message = 'The rules chain too deeply (more than 20 levels).'
            return False
        if not self.ready():
            return False
        key_values = key_values or self.data.key_values(entity, record)
        self.data.begin()
        old = self.data.fetch_one(entity, key_values)
        if old is None:
            self.message = f'The {entity} no longer exists.'
            self.data.end(False)
            return False
        for c in self.data.columns(entity):
            record.setdefault(c, old[c])
        self.protect_derived(entity, record, old, chained)
        lr = self.new_row(entity, record, old, 'update', self.nest)
        self.nest += 1
        ok = self.row_logic(lr) and self.data.update(entity, record, key_values) == 1
        self.nest -= 1
        return self.data.end(ok)

    def upsert(self, entity, record):
        # update when a row with the record's key exists, else insert (an empty generated key inserts)
        key_values = self.data.key_values(entity, record)
        if key_values and all(v is not None for v in key_values.values()) and self.data.fetch_one(entity, key_values) is not None:
            return self.update(entity, record, key_values)
        return self.insert(entity, record)

    def delete(self, entity, key_values):
        self.message = ''
        if not self.ready():
            return False
        self.data.begin()
        old = self.data.fetch_one(entity, key_values)
        if old is None:
            self.message = f'The {entity} no longer exists.'
            self.data.end(False)
            return False
        lr = self.new_row(entity, dict(old), old, 'delete', self.nest)
        self.nest += 1
        ok = self.adjust_parents(lr) and self.data.delete(entity, key_values) == 1
        self.nest -= 1
        return self.data.end(ok)


# ---------------------------------------------------------------- acceptance scenarios

def scenarios(path):
    results = []

    def check(name, cond, detail=''):
        results.append((name, bool(cond), detail))

    data = Data(path)
    logic = Logic(data)
    amount = lambda lr: Logic.number(lr, 'Quantity') * Logic.number(lr, 'UnitPrice')           # noqa: E731
    discount = lambda lr: 0.05 if Logic.number(lr, 'Amount') > 1000 else 0.0                    # noqa: E731
    # declared in the "wrong" order on purpose: Discount reads Amount
    logic.formula('OrderDetail', 'Discount', discount, ['Amount'])
    logic.formula('OrderDetail', 'Amount', amount, ['Quantity', 'UnitPrice'])
    logic.constraint('OrderDetail', lambda lr: Logic.number(lr, 'Quantity') > 0, 'Quantity {Quantity} must be more than 0')
    logic.constraint('Customer', lambda lr: Logic.number(lr, 'Balance') <= Logic.number(lr, 'CreditLimit'),
                     'Customer balance ({row.Balance}) exceeds credit limit ({row.CreditLimit})')
    check('activate', logic.activate())
    check('formula order: Amount before Discount', [f['attr'] for f in logic.rules_of('OrderDetail', 'formulas')] == ['Amount', 'Discount'])

    before = len(data.fetch('OrderDetail', {'OrderId': 10248}))
    item = {'OrderId': 10248, 'ProductId': 11, 'UnitPrice': 14.0, 'Quantity': 3, 'Discount': 0.0, 'Amount': None}
    check('insert computes Amount', logic.insert('OrderDetail', item) and item['Amount'] == 42.0, item.get('Amount'))
    stored = data.fetch_one('OrderDetail', {'Id': item['Id']})
    check('insert stores Amount and the generated key', stored and stored['Amount'] == 42.0, stored)

    upd = {'Id': item['Id'], 'Quantity': 100}
    check('update recomputes Amount, then Discount (dependency order)', logic.update('OrderDetail', upd) and upd['Amount'] == 1400.0 and upd['Discount'] == 0.05, upd)

    # Quantity and UnitPrice unchanged: Amount's formula is pruned, so a value set by hand stays
    upd = {'Id': item['Id'], 'ShippedDate': '2026-11-23', 'Amount': 1.0}
    check('update of an unrelated column prunes the formulas', logic.update('OrderDetail', upd)
          and data.fetch_one('OrderDetail', {'Id': item['Id']})['Amount'] == 1.0, upd)

    bad = {'OrderId': 10248, 'ProductId': 11, 'UnitPrice': 14.0, 'Quantity': 0, 'Discount': 0.0}
    check('constraint fails the insert', not logic.insert('OrderDetail', bad))
    check('constraint message names the value', logic.message == 'Quantity 0 must be more than 0', logic.message)
    check('failed insert is rolled back', len(data.fetch('OrderDetail', {'OrderId': 10248})) == before + 1)

    cust = data.fetch_one('Customer', {'Id': 'ALFKI'})
    upd = {'Id': 'ALFKI', 'Balance': (cust['CreditLimit'] or 0) + 1}
    check('credit-limit constraint fails the update', not logic.update('Customer', upd))
    check('credit-limit message', logic.message.startswith('Customer balance (') and 'exceeds credit limit' in logic.message, logic.message)
    check('failed update leaves the stored row', data.fetch_one('Customer', {'Id': 'ALFKI'})['Balance'] == cust['Balance'])

    # nested transaction: an inner failure rolls back the outer work
    data.begin()
    data.insert('OrderDetail', {'OrderId': 10248, 'ProductId': 42, 'UnitPrice': 1.0, 'Quantity': 1, 'Discount': 0.0, 'Amount': 1.0})
    inner = logic.insert('OrderDetail', dict(bad))
    outer = data.end(True)
    check('inner failure rolls back the outer transaction', not inner and not outer
          and len(data.fetch('OrderDetail', {'OrderId': 10248})) == before + 1)

    check('delete', logic.delete('OrderDetail', {'Id': item['Id']}) and data.fetch_one('OrderDetail', {'Id': item['Id']}) is None)

    cyc = Logic(data)
    cyc.formula('OrderDetail', 'Amount', amount, ['Discount'])
    cyc.formula('OrderDetail', 'Discount', discount, ['Amount'])
    check('cycle is refused at activation', not cyc.activate() and any('cycle' in line for line in cyc.log), cyc.log)

    unknown = Logic(data)
    unknown.formula('OrderDetail', 'NoSuchColumn', amount, ['Quantity'])
    check('unknown attribute is refused at activation', not unknown.activate())

    inactive = Logic(data)
    check('saves refuse until rules are active', not inactive.insert('OrderDetail', dict(item)) and 'not active' in inactive.message)
    results += aggregate_scenarios(path)
    return results


def aggregate_scenarios(path):
    # the canonical check-credit logic (nw/logic/readme_logic.md), plus counts and a parent reference
    results = []

    def check(name, cond, detail=''):
        results.append(('aggregates: ' + name, bool(cond), detail))

    data = Data(path)
    logic = Logic(data)
    n = Logic.number
    unshipped = lambda lr: lr['row'].get('ShippedDate') is None                                   # noqa: E731
    logic.formula('OrderDetail', 'Amount', lambda lr: n(lr, 'Quantity') * n(lr, 'UnitPrice'), ['Quantity', 'UnitPrice'])
    logic.formula('OrderDetail', 'ShippedDate', lambda lr: logic.parent_value(lr, 'Order', 'ShippedDate'), ['Order.ShippedDate'])
    logic.sum('Order', 'AmountTotal', 'OrderDetailList', 'Amount')
    logic.count('Order', 'OrderDetailCount', 'OrderDetailList')
    logic.sum('Customer', 'Balance', 'OrderList', 'AmountTotal', unshipped)
    logic.count('Customer', 'UnpaidOrderCount', 'OrderList', unshipped)
    logic.constraint('Customer', lambda lr: n(lr, 'Balance') <= n(lr, 'CreditLimit'),
                     'Customer balance ({row.Balance}) exceeds credit limit ({row.CreditLimit})')
    check('activate', logic.activate(), logic.log)
    check('aggregates filed under the child', [a['attr'] for a in logic.rules_of('Order', 'aggregates')] == ['Balance', 'UnpaidOrderCount'])

    order = lambda oid: data.fetch_one('Order', {'Id': oid})                                     # noqa: E731
    cust = lambda cid: data.fetch_one('Customer', {'Id': cid})                                   # noqa: E731
    o0, c0, a0 = order(10643), cust('ALFKI'), cust('ANATR')

    item = {'OrderId': 10643, 'ProductId': 11, 'UnitPrice': 10.0, 'Quantity': 2, 'Discount': 0.0}
    ok = logic.insert('OrderDetail', item)
    o1, c1 = order(10643), cust('ALFKI')
    check('insert detail: Order.AmountTotal +20', ok and o1['AmountTotal'] == o0['AmountTotal'] + 20, (o0['AmountTotal'], o1['AmountTotal'], logic.message))
    check('insert detail: Order.OrderDetailCount +1', o1['OrderDetailCount'] == o0['OrderDetailCount'] + 1)
    check('insert detail: chained to Customer.Balance +20', c1['Balance'] == c0['Balance'] + 20, (c0['Balance'], c1['Balance']))
    check('insert detail: parent reference (the order is unshipped)', item.get('ShippedDate') is None)

    ok = logic.update('OrderDetail', {'Id': item['Id'], 'Quantity': 5})
    o2, c2 = order(10643), cust('ALFKI')
    check('change quantity: Order +30, Balance +30', ok and o2['AmountTotal'] == o1['AmountTotal'] + 30 and c2['Balance'] == c1['Balance'] + 30)

    big = {'OrderId': 10643, 'ProductId': 11, 'UnitPrice': 10.0, 'Quantity': 1000, 'Discount': 0.0}
    ok = logic.insert('OrderDetail', big)
    check('credit limit: the chained constraint fails the detail insert', not ok and 'exceeds credit limit' in logic.message, logic.message)
    check('credit limit: nothing changed', order(10643) == o2 and cust('ALFKI') == c2)

    ok = logic.update('Order', {'Id': 10643, 'ShippedDate': '2026-11-24'})
    c3 = cust('ALFKI')
    check('ship the order: Balance - AmountTotal, UnpaidOrderCount -1 (where no longer met)',
          ok and c3['Balance'] == c2['Balance'] - o2['AmountTotal'] and c3['UnpaidOrderCount'] == c2['UnpaidOrderCount'] - 1, (c2, c3))
    ok = logic.update('Order', {'Id': 10643, 'ShippedDate': None})
    check('unship: back again', ok and cust('ALFKI') == c2)

    ok = logic.update('Order', {'Id': 10643, 'CustomerId': 'ANATR'})
    check('re-parent over the new customer\'s credit limit fails (ANATR limit 1000)', not ok and cust('ALFKI') == c2 and cust('ANATR') == a0, logic.message)

    shipped = logic.update('Order', {'Id': 10643, 'ShippedDate': '2026-11-24'})
    moved = logic.update('Order', {'Id': 10643, 'CustomerId': 'ANATR'})
    check('re-parent a shipped order: both balances unchanged (where not met), counts unchanged',
          shipped and moved and cust('ANATR')['Balance'] == a0['Balance'] and cust('ANATR')['UnpaidOrderCount'] == a0['UnpaidOrderCount'], logic.message)
    back = logic.update('Order', {'Id': 10643, 'CustomerId': 'ALFKI'}) and logic.update('Order', {'Id': 10643, 'ShippedDate': None})
    check('re-parent back and unship', back and cust('ALFKI') == c2, logic.message)

    roomy = 'ANATR'   # test setup on the copy, outside the rules: room for the order
    data.db.execute('UPDATE "Customer" SET "CreditLimit" = 5000 WHERE "Id" = ?', [roomy])
    r0 = cust(roomy)
    ok = logic.update('Order', {'Id': 10643, 'CustomerId': roomy})
    check(f're-parent to {roomy} (room under its limit): ALFKI -, {roomy} +, counts move',
          ok and cust('ALFKI')['Balance'] == c2['Balance'] - o2['AmountTotal'] and cust(roomy)['Balance'] == (r0['Balance'] or 0) + o2['AmountTotal']
          and cust(roomy)['UnpaidOrderCount'] == (r0['UnpaidOrderCount'] or 0) + 1, logic.message)
    ok = logic.update('Order', {'Id': 10643, 'CustomerId': 'ALFKI'})
    check(f're-parent back from {roomy}', ok and cust('ALFKI') == c2 and cust(roomy)['Balance'] == (r0['Balance'] or 0), logic.message)

    o9 = order(10692)
    shipped_item = {'OrderId': 10692, 'ProductId': 11, 'UnitPrice': 10.0, 'Quantity': 1, 'Discount': 0.0}
    ok = logic.insert('OrderDetail', shipped_item)
    check('parent reference: a detail on a shipped order takes its ShippedDate', ok and shipped_item.get('ShippedDate') == o9['ShippedDate'], shipped_item.get('ShippedDate'))
    check('detail on a shipped order: AmountTotal +10, Balance unchanged (where not met)',
          order(10692)['AmountTotal'] == o9['AmountTotal'] + 10 and cust('ALFKI') == c2, logic.message)
    logic.delete('OrderDetail', {'Id': shipped_item['Id']})

    # LB-41: derived totals belong to the rules
    ok = logic.update('Order', {'Id': 10643, 'AmountTotal': 99999, 'ShipName': 'x'})
    check('LB-41: a client write to Order.AmountTotal keeps the stored value', ok and order(10643)['AmountTotal'] == o2['AmountTotal']
          and order(10643)['ShipName'] == 'x' and cust('ALFKI') == c2, order(10643)['AmountTotal'])
    logic.update('Order', {'Id': 10643, 'ShipName': o2['ShipName']})
    ok = logic.update('Customer', {'Id': 'ALFKI', 'Balance': 0, 'UnpaidOrderCount': 0})
    check('LB-41: a client write to Customer.Balance / UnpaidOrderCount keeps the stored values', ok and cust('ALFKI') == c2, cust('ALFKI'))

    new_order = {'CustomerId': 'ALFKI', 'EmployeeId': 1, 'AmountTotal': 500, 'OrderDetailCount': 7}
    ok = logic.insert('Order', new_order)
    no = order(new_order['Id']) if ok else None
    check('LB-41: a new order starts with AmountTotal 0 and OrderDetailCount 0', ok and no['AmountTotal'] == 0 and no['OrderDetailCount'] == 0, no or logic.message)
    if not ok:
        check('new order: the rest of its scenarios could not run', False, logic.message)
    else:
        check('new unshipped order: Customer.UnpaidOrderCount +1, Balance unchanged',
              cust('ALFKI')['UnpaidOrderCount'] == c2['UnpaidOrderCount'] + 1 and cust('ALFKI')['Balance'] == c2['Balance'])
        first = {'OrderId': new_order['Id'], 'ProductId': 11, 'UnitPrice': 10.0, 'Quantity': 3, 'Discount': 0.0}
        ok = logic.insert('OrderDetail', first)
        check('first detail of the new order: AmountTotal 30, Balance +30', ok and order(new_order['Id'])['AmountTotal'] == 30
              and cust('ALFKI')['Balance'] == c2['Balance'] + 30, logic.message)

        # upsert: Studio's fourth operation
        up = {'OrderId': new_order['Id'], 'ProductId': 42, 'UnitPrice': 5.0, 'Quantity': 2, 'Discount': 0.0}
        ok = logic.upsert('OrderDetail', up)
        check('upsert without a key inserts (Amount 10, order 40)', ok and up.get('Id') is not None and order(new_order['Id'])['AmountTotal'] == 40, logic.message)
        ok = logic.upsert('OrderDetail', {'Id': up['Id'], 'Quantity': 4})
        check('upsert with an existing key updates (Amount 20, order 50)', ok and order(new_order['Id'])['AmountTotal'] == 50
              and len(data.fetch('OrderDetail', {'OrderId': new_order['Id']})) == 2, logic.message)
        ok = logic.upsert('OrderDetail', {'Id': 999999, 'OrderId': new_order['Id'], 'ProductId': 42, 'UnitPrice': 1.0, 'Quantity': 1, 'Discount': 0.0})
        check('upsert with an unknown key inserts it (order 51)', ok and data.fetch_one('OrderDetail', {'Id': 999999}) is not None
              and order(new_order['Id'])['AmountTotal'] == 51, logic.message)
        ok = logic.upsert('OrderDetail', {'Id': up['Id'], 'Quantity': 10000})
        check('upsert update over the credit limit is refused, nothing changed', not ok and 'exceeds credit limit' in logic.message
              and order(new_order['Id'])['AmountTotal'] == 51, logic.message)

        for detail_id in (999999, up['Id'], first['Id']):
            logic.delete('OrderDetail', {'Id': detail_id})
        ok = logic.delete('Order', {'Id': new_order['Id']})
        check('delete the new order: the customer is back as before', ok and cust('ALFKI') == c2, (cust('ALFKI'), c2))

    ok = logic.delete('OrderDetail', {'Id': item['Id']})
    check('delete detail: Order and Balance back to the start', ok and order(10643) == o0 and cust('ALFKI') == c0, (order(10643), cust('ALFKI')))
    return results


def run(db):
    work = tempfile.mkdtemp()
    copy = os.path.join(work, 'db.sqlite')
    shutil.copy(db, copy)
    try:
        return scenarios(copy)
    finally:
        shutil.rmtree(work)


def prove(db):
    # every rule must be needed: leave each one out in turn and expect a scenario to fail
    OMIT.clear()
    DECLARED.clear()
    baseline = [name for name, ok, _ in run(db) if not ok]
    if baseline:
        print('the full rule set fails first:', baseline)
        return 1
    unproven = 0
    for label in list(DECLARED):
        OMIT.clear()
        OMIT.add(label)
        failed = [name for name, ok, _ in run(db) if not ok]
        if failed:
            print(f'PROVEN    {label}   ({len(failed)} scenarios fail without it, e.g. {failed[0]})')
        else:
            unproven += 1
            print(f'UNPROVEN  {label}   (every scenario still passes without it)')
    OMIT.clear()
    print(f'logic_reference --prove: {len(DECLARED)} rules, {unproven} not proven by any scenario')
    return 1 if unproven else 0


def main(argv):
    if argv and argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    if len(argv) != 2 or argv[0] not in ('--test', '--prove'):
        print(__doc__)
        return 2
    if argv[0] == '--prove':
        return prove(argv[1])
    results = run(argv[1])
    for name, ok, detail in results:
        print(('PASS  ' if ok else 'FAIL  ') + name + ('' if ok or detail == '' else f'   [{detail}]'))
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f'logic_reference: {len(results)} scenarios, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
