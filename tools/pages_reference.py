#!/usr/bin/env python3
"""
pages_reference.py - reference for the page designer (docs/design/Page Designer Design.md), Professional edition.

A project's pages are kept in <project>/Pages.json:

    { "pages": [ { "title": "Order Entry", "icon": "doc.text",
                   "parts": [ { "entity": "Orders", "display": "detail", "follows": null },
                              { "entity": "Customers", "display": "detail",
                                "follows": { "part": 0, "how": "parent", "relationship": "Customers",
                                             "fks": ["CustomerID"], "parentKeys": ["CustomerID"] } },
                              ... ] } ] }

    display   detail (one record: the author's "scalar") | list | listDetail (a List and the Form of its row)
    follows   null for the page's driver (part 0: the navigator and the search move it) or a part that is not linked;
              else the earlier part it follows and how:
                children  this part lists the children of that part's current record (its fks = their parentKeys)
                parent    this part shows the parent of that part's current record (their fks = its parentKeys)
                same      the same entity: the row chosen in that part (a List)

What this file is the reference for (the FB port lives in the Studio and the generated app):
    proposed_links( model, parts, entity )   the links offered when an entity is dropped on a page (first = proposed)
    default_pages( model )                   one page per table, List with detail (the Lite edition's pages, always)
    check_pages( model, pages )              what is wrong with a Pages.json ([] when nothing)
    resolve_page( db, model, page, driver )  each part's records for a driver record, as the generated app shows them

    python3 tools/pages_reference.py db.sqlite                 the default pages, and the links between every two entities
    python3 tools/pages_reference.py --test                    the tests (Northwind fixture, the samples)
Standard library only.
"""
import json, os, sqlite3, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sqlite_model import read_model, q   # noqa: E402

DISPLAYS = ('detail', 'list', 'listDetail')


def tables(model):
    return sorted(n for n, r in model.items() if r['kind'] == 'table')


def proposed_links(model, parts, entity):
    """The links an entity dropped on a page can have with the parts already there, the proposed one first.
    Order: the parts in page order (the driver first); for each part, the relationships in the model's order.
    A same-entity link (a Detail of the row chosen in a List) comes before a relationship to the same part.
    An empty list: no link (the part is not linked)."""
    links = []
    rels = model[entity]['relationships']
    for index, part in enumerate(parts):
        other = part['entity']
        if other == entity:
            if part['display'] in ('list', 'listDetail'):
                links.append({'part': index, 'how': 'same', 'relationship': None, 'fks': [], 'parentKeys': []})
            continue                                   # a self-relationship (an employee's manager): later
        for rel in rels:
            if rel['resource'] != other:
                continue
            how = 'children' if rel['direction'] == 'toone' else 'parent'
            links.append({'part': index, 'how': how, 'relationship': rel['name'],
                          'fks': rel['fks'], 'parentKeys': rel['parentKeys']})
    return links


def default_pages(model):
    return {'pages': [{'title': name, 'icon': None,
                       'parts': [{'entity': name, 'display': 'listDetail', 'follows': None}]} for name in tables(model)]}


def check_pages(model, pages):
    problems = []
    titles = set()
    for p, page in enumerate(pages.get('pages', [])):
        where = f'page {p + 1} ({page.get("title")!r})'
        if not page.get('title'):
            problems.append(f'{where}: no title')
        elif page['title'] in titles:
            problems.append(f'{where}: the title is used twice')
        titles.add(page.get('title'))
        parts = page.get('parts', [])
        if not parts:
            problems.append(f'{where}: no parts')
        for i, part in enumerate(parts):
            at = f'{where}, part {i + 1}'
            entity = part.get('entity')
            if entity not in model or model[entity]['kind'] != 'table':
                problems.append(f'{at}: {entity!r} is not a table of the model')
                continue
            if part.get('display') not in DISPLAYS:
                problems.append(f'{at}: display {part.get("display")!r}')
            follows = part.get('follows')
            if follows is None:
                continue
            if i == 0:
                problems.append(f'{at}: the driver follows nothing')
                continue
            target = follows.get('part')
            if not isinstance(target, int) or target < 0 or target >= i:
                problems.append(f'{at}: it follows part {target}, which is not an earlier part')
                continue
            offered = proposed_links(model, parts[:target + 1], entity)
            match = [l for l in offered if l['part'] == target and l['how'] == follows.get('how')
                     and l['relationship'] == follows.get('relationship')]
            if not match:
                problems.append(f'{at}: no relationship "{follows.get("relationship")}" ({follows.get("how")}) '
                                f'between {entity} and {parts[target]["entity"]}')
    return problems


def _rows(db, sql, args):
    cur = db.execute(sql, args)
    names = [d[0] for d in cur.description]
    return [dict(zip(names, r)) for r in cur.fetchall()]


def resolve_page(db, model, page, driver):
    """Each part's records, given the driver's current record (a dict): the driver itself; a part that follows
    another shows, for that part's current record, its children, its parent or the same record. A List's current
    record is its first row (the generated app starts on it), so the parts following it show that row's.
    Returns [ { entity, display, records } ] in page order."""
    out = []
    current = []
    for i, part in enumerate(page['parts']):
        entity = part['entity']
        follows = part.get('follows')
        if i == 0:
            records = [driver] if driver is not None else []
        elif follows is None:
            records = _rows(db, f'SELECT * FROM {q(entity)}', ())
        else:
            source = current[follows['part']]
            if source is None:
                records = []
            elif follows['how'] == 'same':
                records = [source]
            elif follows['how'] == 'children':          # this part's fks = the source's parentKeys
                where = ' AND '.join(f'{q(c)} = ?' for c in follows['fks'])
                records = _rows(db, f'SELECT * FROM {q(entity)} WHERE {where}',
                                [source[k] for k in follows['parentKeys']])
            else:                                        # parent: the source's fks = this part's parentKeys
                where = ' AND '.join(f'{q(c)} = ?' for c in follows['parentKeys'])
                records = _rows(db, f'SELECT * FROM {q(entity)} WHERE {where}', [source[k] for k in follows['fks']])
        out.append({'entity': entity, 'display': part['display'], 'records': records})
        current.append(records[0] if records else None)
    return out


def drop(model, page, entity, display):
    """What the designer does on a drop: the part added with the proposed link (or none)."""
    links = proposed_links(model, page['parts'], entity)
    follows = None
    if page['parts'] and links:
        l = links[0]
        follows = {k: l[k] for k in ('part', 'how', 'relationship', 'fks', 'parentKeys')}
    page['parts'].append({'entity': entity, 'display': display, 'follows': follows})
    return links


# ------------------------------------------------------------------------------------------------------------ tests

def northwind_db():
    path = os.path.join(tempfile.mkdtemp(), 'northwind.sqlite')
    db = sqlite3.connect(path)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'northwind.sql'), encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()
    db.close()
    return path


def run_tests():
    failed = 0

    def check(what, ok, detail=''):
        nonlocal failed
        print(('PASS  ' if ok else 'FAIL  ') + what + ('' if ok else f'   [{detail}]'))
        if not ok:
            failed += 1

    path = northwind_db()
    model = read_model(path)
    db = sqlite3.connect(path)

    # the default pages: one per table, List with detail - the Lite edition's, and the designer's start
    pages = default_pages(model)
    check('default pages: one per table (13), List with detail', len(pages['pages']) == 13
          and all(p['parts'][0]['display'] == 'listDetail' for p in pages['pages']), len(pages['pages']))
    check('default pages pass the check', check_pages(model, pages) == [], check_pages(model, pages))

    # the invoice page, as the designer builds it from drops
    page = {'title': 'Order Entry', 'icon': 'doc.text', 'parts': []}
    links = drop(model, page, 'Orders', 'detail')
    check('Orders dropped on an empty page: the driver, no link', page['parts'][0]['follows'] is None and links == [])
    links = drop(model, page, 'Customers', 'detail')
    f = page['parts'][1]['follows']
    check('Customers on Orders: the parent of the order (Orders.CustomerID)', f and f['part'] == 0 and f['how'] == 'parent'
          and f['fks'] == ['CustomerID'] and len(links) == 1, f)
    drop(model, page, 'Order Details', 'list')
    f = page['parts'][2]['follows']
    check('Order Details on Orders: the order\'s lines', f and f['part'] == 0 and f['how'] == 'children'
          and f['fks'] == ['OrderID'], f)
    links = drop(model, page, 'Products', 'detail')
    f = page['parts'][3]['follows']
    check('Products on that page: the product of the line chosen (no link to Orders, so the lines)',
          f and f['part'] == 2 and f['how'] == 'parent' and f['fks'] == ['ProductID'] and len(links) == 1, links)
    drop(model, page, 'Employees', 'detail')
    f = page['parts'][4]['follows']
    check('Employees on that page: the employee who took the order', f and f['part'] == 0 and f['how'] == 'parent'
          and f['fks'] == ['EmployeeID'], f)
    drop(model, page, 'Shippers', 'detail')
    f = page['parts'][5]['follows']
    check('Shippers: through Orders.ShipVia (a key whose name is not the parent\'s)', f and f['part'] == 0
          and f['how'] == 'parent' and f['fks'] == ['ShipVia'] and f['parentKeys'] == ['ShipperID'], f)
    links = drop(model, page, 'Region', 'list')
    check('Region on that page: no link (nothing relates it)', page['parts'][6]['follows'] is None and links == [])
    check('the invoice page passes the check', check_pages(model, {'pages': [page]}) == [],
          check_pages(model, {'pages': [page]}))

    # the page at run time: order 10248
    order = _rows(db, 'SELECT * FROM "Orders" WHERE "OrderID" = 10248', ())[0]
    shown = resolve_page(db, model, page, order)
    check('10248: its customer is Vins et alcools Chevalier', shown[1]['records'][0]['CompanyName'] == 'Vins et alcools Chevalier')
    check('10248: three lines', len(shown[2]['records']) == 3, len(shown[2]['records']))
    check('10248: the first line\'s product is Queso Cabrales', shown[3]['records'][0]['ProductName'] == 'Queso Cabrales',
          shown[3]['records'])
    check('10248: taken by Buchanan, shipped by Federal Shipping', shown[4]['records'][0]['LastName'] == 'Buchanan'
          and shown[5]['records'][0]['CompanyName'] == 'Federal Shipping')
    order = _rows(db, 'SELECT * FROM "Orders" WHERE "OrderID" = 10249', ())[0]
    shown = resolve_page(db, model, page, order)
    check('10249: a line whose product is missing shows no product (not an error)', shown[3]['records'] == []
          and len(shown[2]['records']) == 2)

    # other pages
    page2 = {'title': 'Customer Orders', 'icon': None, 'parts': []}
    drop(model, page2, 'Customers', 'detail')
    drop(model, page2, 'Orders', 'listDetail')
    drop(model, page2, 'Order Details', 'list')
    f1, f2 = page2['parts'][1]['follows'], page2['parts'][2]['follows']
    check('Customers then Orders: the customer\'s orders', f1['how'] == 'children' and f1['part'] == 0, f1)
    check('then Order Details: the lines of the order chosen in that list', f2['how'] == 'children' and f2['part'] == 1, f2)
    shown = resolve_page(db, model, page2, _rows(db, 'SELECT * FROM "Customers" WHERE "CustomerID" = \'VINET\'', ())[0])
    check('VINET: one order, 10248, and its three lines', [r['OrderID'] for r in shown[1]['records']] == [10248]
          and len(shown[2]['records']) == 3)

    page3 = {'title': 'Orders', 'icon': None, 'parts': []}
    drop(model, page3, 'Orders', 'list')
    links = drop(model, page3, 'Orders', 'detail')
    f = page3['parts'][1]['follows']
    check('Orders (Detail) on Orders (List): the row chosen', f and f['how'] == 'same' and f['part'] == 0, f)

    page4 = {'title': 'Territories', 'icon': None, 'parts': []}
    drop(model, page4, 'Region', 'detail')
    drop(model, page4, 'Territories', 'list')
    links = drop(model, page4, 'Employees', 'list')
    check('Region, Territories: the region\'s territories', page4['parts'][1]['follows']['how'] == 'children')
    check('Employees there: no direct link (only through EmployeeTerritories)', page4['parts'][2]['follows'] is None)

    page5 = {'title': 'Staff', 'icon': None, 'parts': []}
    drop(model, page5, 'Employees', 'detail')
    links = drop(model, page5, 'Employees', 'list')
    check('Employees twice (a manager and their staff): not offered yet (self-relationships later)',
          page5['parts'][1]['follows'] is None and links == [])

    # the check finds what is wrong
    bad = {'pages': [{'title': 'X', 'parts': [
        {'entity': 'Orders', 'display': 'detail', 'follows': None},
        {'entity': 'Nothing', 'display': 'list', 'follows': None},
        {'entity': 'Customers', 'display': 'card', 'follows': {'part': 3, 'how': 'parent', 'relationship': 'Customers'}},
        {'entity': 'Region', 'display': 'list', 'follows': {'part': 0, 'how': 'children', 'relationship': 'Region'}}]},
        {'title': 'X', 'parts': []}]}
    problems = check_pages(model, bad)
    for needle in ("'Nothing' is not a table", "display 'card'", 'not an earlier part', 'no relationship "Region"',
                   'the title is used twice', 'no parts'):
        check(f'the check reports: {needle}', any(needle in p for p in problems), problems)

    # every relationship of every sample model links both ways
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples = [('Northwind', path)] + [(n, os.path.join(root, 'samples', n, f)) for n, f in
                                       (('Customs', 'customs.sqlite'), ('FlightPlanner', 'flightplanner.sqlite'),
                                        ('Telecom', 'telecom.sqlite'))]
    for name, db_path in samples:
        if not os.path.exists(db_path):
            check(f'{name}: the sample database is there', False, db_path)
            continue
        m = read_model(db_path)
        pairs = bad_pairs = 0
        for child in tables(m):
            for rel in m[child]['relationships']:
                if rel['direction'] != 'toone' or rel['resource'] == child or rel['resource'] not in m:
                    continue
                parent = rel['resource']
                pairs += 1
                down = proposed_links(m, [{'entity': parent, 'display': 'detail'}], child)
                up = proposed_links(m, [{'entity': child, 'display': 'detail'}], parent)
                if not any(l['how'] == 'children' and l['relationship'] == rel['name'] for l in down) or \
                   not any(l['how'] == 'parent' and l['fks'] == rel['fks'] for l in up):
                    bad_pairs += 1
        check(f'{name}: every relationship ({pairs}) is offered both ways', pairs > 0 and bad_pairs == 0,
              f'{bad_pairs} of {pairs}')
        check(f'{name}: the default pages pass the check', check_pages(m, default_pages(m)) == [])

    print(f'pages_reference: {failed} failed')
    return failed


def main(argv):
    if '--test' in argv:
        return 1 if run_tests() else 0
    if len(argv) < 2:
        print(__doc__)
        return 2
    model = read_model(argv[1])
    print(json.dumps(default_pages(model), indent=2))
    for a in tables(model):
        for b in tables(model):
            for l in proposed_links(model, [{'entity': a, 'display': 'detail'}], b):
                print(f'{b} on a page with {a}: {l["how"]} ({l["relationship"]}: {l["fks"]} -> {l["parentKeys"]})')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
