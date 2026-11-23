#!/usr/bin/env python3
"""
Reference implementation of LogicBank for FutureBasic's engine core, for checking the
FB runtime's behaviour: src/Runtime/Logic Rules.incl, Logic Row.incl, Logic Engine.incl.

It follows the FB code function by function (same names, same order of work) on the
same SQLite database, so a scenario that passes here describes what the FB engine must
do. Clean-room: written from LogicBank's documented behaviour, not its code.

    python3 tools/logic_reference.py --test <copy of a Northwind db.sqlite>

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

    def insert(self, entity, record):
        gen, keys = self.key_generated(entity), self.keys(entity)
        cols = [c for c in self.columns(entity) if c in record and not (gen and c in keys and record[c] is None)]
        self.db.execute(f'INSERT INTO {q(entity)} ( {", ".join(q(c) for c in cols)} ) VALUES ( {", ".join("?" * len(cols))} )',
                        [record[c] for c in cols])
        if gen and len(keys) == 1 and record.get(keys[0]) is None:
            record[keys[0]] = self.db.execute('select last_insert_rowid()').fetchone()[0]
        return True

    def update(self, entity, record, key_values):
        cols = [c for c in self.columns(entity) if c in record]
        where = ' AND '.join(f'{q(k)} = ?' for k in key_values)
        cur = self.db.execute(f'UPDATE {q(entity)} SET {", ".join(q(c) + " = ?" for c in cols)} WHERE {where}',
                              [record[c] for c in cols] + list(key_values.values()))
        return cur.rowcount

    def delete(self, entity, key_values):
        where = ' AND '.join(f'{q(k)} = ?' for k in key_values)
        return self.db.execute(f'DELETE FROM {q(entity)} WHERE {where}', list(key_values.values())).rowcount


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
        return self.rules.setdefault(entity, {'formulas': [], 'constraints': []})

    def formula(self, entity, attr, fn, depends_on):
        self.entity_rules(entity)['formulas'].append({'entity': entity, 'attr': attr, 'fn': fn, 'dependsOn': depends_on or []})
        self.active = False

    def constraint(self, entity, fn, message):
        self.entity_rules(entity)['constraints'].append({'entity': entity, 'fn': fn, 'message': message})

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
            if '.' in d or self.changed(lr, d):
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

    def row_logic(self, lr):
        self.run_formulas(lr)
        return self.run_constraints(lr)

    def ready(self):
        if self.active:
            return True
        self.message = 'The business rules are not active (LogicActivate).'
        return False

    def insert(self, entity, record):
        self.message = ''
        if not self.ready() or not self.data.begin():
            return False
        lr = self.new_row(entity, record, None, 'insert', self.nest)
        self.nest += 1
        ok = self.row_logic(lr) and self.data.insert(entity, record)
        self.nest -= 1
        return self.data.end(ok)

    def update(self, entity, record, key_values=None):
        self.message = ''
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
        lr = self.new_row(entity, record, old, 'update', self.nest)
        self.nest += 1
        ok = self.row_logic(lr) and self.data.update(entity, record, key_values) == 1
        self.nest -= 1
        return self.data.end(ok)

    def delete(self, entity, key_values):
        self.message = ''
        if not self.ready():
            return False
        self.data.begin()
        if self.data.fetch_one(entity, key_values) is None:
            self.message = f'The {entity} no longer exists.'
            self.data.end(False)
            return False
        return self.data.end(self.data.delete(entity, key_values) == 1)


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
    return results


def main(argv):
    if len(argv) != 2 or argv[0] != '--test':
        print(__doc__)
        return 2
    work = tempfile.mkdtemp()
    copy = os.path.join(work, 'db.sqlite')
    shutil.copy(argv[1], copy)
    try:
        results = scenarios(copy)
    finally:
        shutil.rmtree(work)
    for name, ok, detail in results:
        print(('PASS  ' if ok else 'FAIL  ') + name + ('' if ok or detail == '' else f'   [{detail}]'))
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f'logic_reference: {len(results)} scenarios, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
