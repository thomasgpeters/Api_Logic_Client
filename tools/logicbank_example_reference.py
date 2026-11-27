#!/usr/bin/env python3
"""The LogicBank for FutureBasic example app, worked out here first: its model, its rules, and its story.

    python3 tools/logicbank_example_reference.py            run the story; check every value the app shows
    python3 tools/logicbank_example_reference.py --model    write src/LogicBankExample/Model.json

The example app (src/LogicBankExample) keeps three objects in memory - Customer, Order, Item - with no database
(Data Memory.incl). Its rules (Rules.incl) are these, in FB; its story (Story.incl) makes these saves and shows
these values. The reference engine (tools/logic_reference.py) runs them here on SQLite with the same model, so
the numbers the app prints are the numbers checked below.
"""
import json
import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import logic_reference                        # noqa: E402
from logic_reference import Data, Logic       # noqa: E402
import sqlite_model                           # noqa: E402

EXAMPLE = os.path.join(HERE, '..', 'src', 'LogicBankExample')

SCHEMA = '''
CREATE TABLE Customer (
    Id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT NOT NULL, CreditLimit REAL NOT NULL DEFAULT 0,
    Discount REAL NOT NULL DEFAULT 0, Balance REAL DEFAULT 0, UnshippedOrders INTEGER DEFAULT 0);
CREATE TABLE "Order" (
    Id INTEGER PRIMARY KEY AUTOINCREMENT, CustomerId INTEGER NOT NULL REFERENCES Customer(Id), ShippedDate TEXT,
    Discount REAL, AmountTotal REAL DEFAULT 0, ItemCount INTEGER DEFAULT 0);
CREATE TABLE Item (
    Id INTEGER PRIMARY KEY AUTOINCREMENT, OrderId INTEGER NOT NULL REFERENCES "Order"(Id), Product TEXT NOT NULL,
    Quantity REAL NOT NULL, UnitPrice REAL NOT NULL, Amount REAL DEFAULT 0);
'''


def declare(logic):
    n, v = Logic.number, Logic.value
    unshipped = lambda lr: v(lr, 'ShippedDate') in (None, '')
    # an item: its amount, at the order's discount
    logic.formula('Item', 'Amount', lambda lr: round(n(lr, 'Quantity') * n(lr, 'UnitPrice') * (100 - float(logic.parent_value(lr, 'Order', 'Discount') or 0)) / 100, 2),
                  ['Quantity', 'UnitPrice', 'OrderId', 'Order.Discount'])
    logic.constraint('Item', lambda lr: n(lr, 'Quantity') > 0, 'Quantity {Quantity} must be more than 0')
    # an order: the customer's discount when it was placed, and its items added up
    logic.parent_check('Order', 'Customer', 'There is no customer {CustomerId}')
    logic.copy('Order', 'Discount', 'Customer', 'Discount')
    logic.sum('Order', 'AmountTotal', 'ItemList', 'Amount')
    logic.count('Order', 'ItemCount', 'ItemList')
    logic.delete_action('Order', 'ItemList', 'cascade')
    # a customer: what its unshipped orders come to, never more than the credit limit
    logic.sum('Customer', 'Balance', 'OrderList', 'AmountTotal', unshipped)
    logic.count('Customer', 'UnshippedOrders', 'OrderList', unshipped)
    logic.constraint('Customer', lambda lr: n(lr, 'Balance') <= n(lr, 'CreditLimit'),
                     '{Name}\'s balance {Balance} would exceed the credit limit {CreditLimit}')
    logic.delete_action('Customer', 'OrderList', 'prevent', '{Name} still has orders')


def one(data, sql):
    row = data.db.execute(sql).fetchone()
    return None if row is None else (row[0] if len(row) == 1 else tuple(row))


# the story, step by step: (what the app says it does, the save, what must hold afterwards)
def story(data, logic):
    C = lambda cols: one(data, f'select {cols} from Customer where Id=1')
    O = lambda cols: one(data, f'select {cols} from "Order" where Id=1')
    I = lambda i, cols: one(data, f'select {cols} from Item where Id={i}')
    return [
        ('Alice is a customer: a credit limit of 1,000.00 and a 10 % discount',
         lambda: logic.insert('Customer', {'Name': 'Alice', 'CreditLimit': 1000, 'Discount': 10}),
         lambda: C('Balance, UnshippedOrders') == (0.0, 0)),
        ('Alice places an order: it copies her 10 % discount',
         lambda: logic.insert('Order', {'CustomerId': 1}),
         lambda: O('Discount, AmountTotal') == (10.0, 0.0) and C('UnshippedOrders') == 1),
        ('2 widgets at 100.00: 180.00 after the discount; the order and Alice\'s balance follow',
         lambda: logic.insert('Item', {'OrderId': 1, 'Product': 'Widget', 'Quantity': 2, 'UnitPrice': 100}),
         lambda: I(1, 'Amount') == 180.0 and O('AmountTotal, ItemCount') == (180.0, 1) and C('Balance') == 180.0),
        ('1 gadget at 300.00: 270.00; the order is 450.00',
         lambda: logic.insert('Item', {'OrderId': 1, 'Product': 'Gadget', 'Quantity': 1, 'UnitPrice': 300}),
         lambda: I(2, 'Amount') == 270.0 and O('AmountTotal, ItemCount') == (450.0, 2) and C('Balance') == 450.0),
        ('5 widgets instead of 2: the item, the order and the balance change together',
         lambda: logic.update('Item', {'Id': 1, 'Quantity': 5}),
         lambda: I(1, 'Amount') == 450.0 and O('AmountTotal') == 720.0 and C('Balance') == 720.0),
        ('4 more widgets would take Alice to 1,080.00: refused, and nothing changes',
         lambda: not logic.insert('Item', {'OrderId': 1, 'Product': 'Widget', 'Quantity': 4, 'UnitPrice': 100}),
         lambda: 'exceed the credit limit' in logic.message and O('AmountTotal, ItemCount') == (720.0, 2) and C('Balance') == 720.0),
        ('An item with no quantity: refused',
         lambda: not logic.insert('Item', {'OrderId': 1, 'Product': 'Widget', 'Quantity': 0, 'UnitPrice': 100}),
         lambda: 'must be more than 0' in logic.message),
        ('The order ships: it no longer counts against Alice\'s credit',
         lambda: logic.update('Order', {'Id': 1, 'ShippedDate': '2026-11-26'}),
         lambda: C('Balance, UnshippedOrders') == (0.0, 0) and O('AmountTotal') == 720.0),
        ('Alice\'s discount goes up to 20 %: the order placed earlier keeps its 10 %',
         lambda: logic.update('Customer', {'Id': 1, 'Discount': 20}),
         lambda: O('Discount') == 10.0 and I(1, 'Amount') == 450.0),
        ('A new order now copies 20 %: 2 widgets come to 160.00',
         lambda: logic.insert('Order', {'CustomerId': 1}) and logic.insert('Item', {'OrderId': 2, 'Product': 'Widget', 'Quantity': 2, 'UnitPrice': 100}),
         lambda: one(data, 'select Discount, AmountTotal from "Order" where Id=2') == (20.0, 160.0) and C('Balance, UnshippedOrders') == (160.0, 1)),
        ('An order for a customer who does not exist: refused',
         lambda: not logic.insert('Order', {'CustomerId': 99}),
         lambda: 'no customer 99' in logic.message),
        ('Alice cannot be deleted: she still has orders',
         lambda: not logic.delete('Customer', {'Id': 1}),
         lambda: 'still has orders' in logic.message),
        ('The new order is deleted: its item goes with it, and Alice\'s balance comes down',
         lambda: logic.delete('Order', {'Id': 2}),
         lambda: one(data, 'select count(*) from Item where OrderId=2') == 0 and C('Balance, UnshippedOrders') == (0.0, 0)),
    ]


def build():
    path = os.path.join(tempfile.mkdtemp(), 'example.sqlite')
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    db.close()
    data = Data(path)
    logic = Logic(data)
    declare(logic)
    if not logic.activate():
        raise SystemExit('the rules did not activate: ' + '; '.join(logic.log))
    return path, data, logic


def model_json(path):
    resources = []
    for name, r in sorted(sqlite_model.read_model(path).items()):
        resources.append({'name': name, 'kind': r.get('kind', 'table'),
                          'fields': [{'name': a['name'], 'type': a.get('type', ''), 'pk': a.get('pk', 0)} for a in r['attributes']],
                          'keys': r.get('keys', []), 'keyKind': r.get('keyKind', 'none'),
                          'relationships': r.get('relationships', [])})
    return {'project': 'LogicBank for FutureBasic Example', 'database': '', 'resources': resources}


def main():
    path, data, logic = build()
    if '--model' in sys.argv:
        out = os.path.join(EXAMPLE, 'Model.json')
        with open(out, 'w') as f:
            json.dump(model_json(path), f, indent=2)
            f.write('\n')
        print('wrote', out)
        return 0
    failed = 0
    for i, (what, save, check) in enumerate(story(data, logic), 1):
        save()
        ok = check()
        failed += 0 if ok else 1
        print(f'{"PASS" if ok else "FAIL"}  {i:2}. {what}' + ('' if ok else f'   ({logic.message})'))
    print(f'logicbank example: {len(story(data, logic))} steps, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
