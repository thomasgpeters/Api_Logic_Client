#!/usr/bin/env python3
"""
pages_reference.py - reference for the page designer (docs/design/Page Designer Design.md), Professional edition.

A project's pages are kept in <project>/Pages.json:

    { "pages": [ { "title": "Order Entry", "icon": "doc.text",
                   "parts": [ { "entity": "Orders", "display": "detail", "follows": null },
                              { "entity": "Customers", "display": "detail",
                                "follows": { "part": 0, "how": "parent", "relationship": "Customers",
                                             "fks": ["CustomerID"], "parentKeys": ["CustomerID"] } },
                              ... ],
                   "links": [ { "page": "Customer Orders", "fromPart": 1, "how": "parent", "relationship": "Customers",
                                "name": "Customers to Customer Orders", "cardinality": "oneToMany",
                                "fks": ["CustomerID"], "parentKeys": ["CustomerID"], "through": null } ] } ] }

    display   detail (one record: the author's "scalar") | list | listDetail (a List and the Form of its row)
    follows   null for the page's driver (part 0: the navigator and the search move it) or a part that is not linked;
              else the earlier part it follows and how:
                children  this part lists the children of that part's current record (its fks = their parentKeys)
                parent    this part shows the parent of that part's current record (their fks = its parentKeys)
                same      the same entity: the row chosen in that part (a List)
                through   many to many, through a join table (Employees and Territories, through EmployeeTerritories)

    Associations (author, 2026-11-27): a part's follows and a page's links are the same object - a name (proposed,
    the developer's to change), the direction (from the part or page it starts at, to the one that receives), the
    cardinality and the relationship it rides on:
                oneToMany   children (a customer's orders)
                manyToOne   parent (an order's customer)
                oneToOne    the same record, or a key that is the child's whole primary key
                manyToMany  through a join table

    links     (author, 2026-11-27) drill-in from this page to another: a page dragged onto another in the designer shows
              the relationships between the two pages' entities; the one chosen becomes a link. At run time the
              current record of the part fromPart opens the other page, whose driver shows, for it:
                children  its children (Customers -> Orders: that customer's orders)
                parent    its parent (Orders -> Customers: the order's customer)
                same      the same record (a Customers part -> the Customers page)

What this file is the reference for (the FB port lives in the Studio and the generated app):
    proposed_links( model, parts, entity )   the links offered when an entity is dropped on a page (first = proposed)
    default_pages( model )                   one page per table, List with detail (the Lite edition's pages, always)
    page_associations( model, a, b )         the links a page dragged onto another can have (first = proposed)
    check_pages( model, pages )              what is wrong with a Pages.json ([] when nothing)
    resolve_link( db, link, record )         the other page's driver records, for the current record of fromPart
    resolve_page( db, model, page, driver )  each part's records for a driver record, as the generated app shows them
    page_flow_svg( pages )                   the page flow diagram: pages, their parts, the associations between them

    python3 tools/pages_reference.py db.sqlite                 the default pages, and the links between every two entities
    python3 tools/pages_reference.py --flow Pages.json         the page flow diagram (SVG) of a project's pages
    python3 tools/pages_reference.py --flow-example            the example in docs/design/Page Flow Example.svg
    python3 tools/pages_reference.py --test                    the tests (Northwind fixture, the samples)
Standard library only.
"""
import json, os, sqlite3, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sqlite_model import read_model, q   # noqa: E402

DISPLAYS = ('detail', 'list', 'listDetail')


def tables(model):
    return sorted(n for n, r in model.items() if r['kind'] == 'table')


def join_tables(model):
    """Tables that only join two others (EmployeeTerritories, CustomerCustomerDemo): two foreign keys to two different
    tables whose columns are, together, the table's whole primary key. {table: (relationship to A, to B)}."""
    found = {}
    for name in tables(model):
        r = model[name]
        rels = [x for x in r['relationships'] if x['direction'] == 'toone']
        if len(rels) != 2 or rels[0]['resource'] == rels[1]['resource']:
            continue
        if set(rels[0]['fks'] + rels[1]['fks']) == set(r['keys']) and r['keys']:
            found[name] = (rels[0], rels[1])
    return found


def cardinality(model, how, source, target, fks):
    """An association's cardinality, from the source's current record to the target's records."""
    if how == 'same':
        return 'oneToOne'
    if how == 'through':
        return 'manyToMany'
    if how == 'children':                              # target holds the foreign key: one source, many targets ...
        return 'oneToOne' if set(fks) == set(model[target]['keys']) else 'oneToMany'   # ... unless it is its whole key
    return 'oneToOne' if set(fks) == set(model[source]['keys']) else 'manyToOne'      # parent: the source holds it


def association_name(source, target, how, relationship, fks=(), parent_keys=()):
    if how == 'same':
        return f'{source}, the same record'
    name = f'{source} to {target}'
    if how in ('parent', 'children') and len(fks) == 1 and parent_keys and fks[0] != parent_keys[0]:
        name += f' ({fks[0]})'                         # a role: Orders.ShipVia -> Shippers.ShipperID
    if how == 'through':
        name += f' (through {relationship})'
    return name


def proposed_links(model, parts, entity):
    """The links an entity dropped on a page can have with the parts already there, the proposed one first.
    Order: the parts in page order (the driver first); for each part, the same entity (a Detail of the row chosen in a
    List), then the model's relationships in its order; then, after every direct one, many to many through a join
    table (Order Details joins Orders and Products: "the orders that include this product").
    Each link is an association: { part, name, how, cardinality, relationship, fks, parentKeys, through }.
    An empty list: no link (the part is not linked)."""
    links, indirect = [], []
    rels = model[entity]['relationships']
    joins = join_tables(model)

    def add(index, other, how, relationship, fks, parent_keys, through=None):
        (indirect if how == 'through' else links).append({'part': index, 'name': association_name(other, entity, how, relationship, fks, parent_keys), 'how': how,
                      'cardinality': cardinality(model, how, other, entity, fks), 'relationship': relationship,
                      'fks': fks, 'parentKeys': parent_keys, 'through': through})

    for index, part in enumerate(parts):
        other = part['entity']
        if other == entity:
            if part['display'] in ('list', 'listDetail'):
                add(index, other, 'same', None, [], [])
            continue                                   # a self-relationship (an employee's manager): later
        for rel in rels:
            if rel['resource'] == other:
                add(index, other, 'children' if rel['direction'] == 'toone' else 'parent', rel['name'],
                    rel['fks'], rel['parentKeys'])
        for join, (r1, r2) in joins.items():
            for from_rel, to_rel in ((r1, r2), (r2, r1)):
                if from_rel['resource'] == other and to_rel['resource'] == entity:
                    add(index, other, 'through', join, [], [],
                        {'table': join, 'fromFks': from_rel['fks'], 'fromKeys': from_rel['parentKeys'],
                         'toFks': to_rel['fks'], 'toKeys': to_rel['parentKeys']})
    return links + indirect                           # direct relationships first, then many to many


def page_associations(model, source, target):
    """The associations from page source to page target (a page dragged onto another): the relationships between any
    part of source and target's driver (the part that receives the record), the proposed one first - source's parts
    in page order, then as proposed_links orders them. Each: { name, fromPart, page, how, cardinality, relationship,
    fks, parentKeys, through }. Empty: the two pages have nothing in common."""
    found = []
    receiver = target['parts'][0]['entity'] if target.get('parts') else None
    if receiver is None:
        return found
    for index, part in enumerate(source.get('parts', [])):
        for l in proposed_links(model, [{'entity': part['entity'], 'display': 'list'}], receiver):
            a = dict(l)
            del a['part']
            a.update({'fromPart': index, 'page': target['title']})
            found.append(a)
    return sorted(found, key=lambda a: a['how'] == 'through')   # direct ones first (stable: page order kept)


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
        by_title = {pg.get('title'): pg for pg in pages.get('pages', [])}
        for k, link in enumerate(page.get('links', [])):
            at = f'{where}, link {k + 1}'
            target = by_title.get(link.get('page'))
            if target is None:
                problems.append(f'{at}: no page {link.get("page")!r}')
                continue
            if target is page:
                problems.append(f'{at}: a link to its own page')
                continue
            ok = [l for l in page_associations(model, page, target) if l['fromPart'] == link.get('fromPart')
                  and l['how'] == link.get('how') and l['relationship'] == link.get('relationship')]
            if not ok:
                problems.append(f'{at}: no relationship "{link.get("relationship")}" ({link.get("how")}) from part '
                                f'{link.get("fromPart")} to {link.get("page")!r}')
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
            elif follows['how'] == 'through':
                records = _through(db, entity, follows['through'], source)
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


def _through(db, entity, t, record):
    """many to many: the entity's rows joined to record through the join table"""
    on = ' AND '.join(f'j.{q(f)} = e.{q(k)}' for f, k in zip(t['toFks'], t['toKeys']))
    where = ' AND '.join(f'j.{q(f)} = ?' for f in t['fromFks'])
    return _rows(db, f'SELECT e.* FROM {q(entity)} e JOIN {q(t["table"])} j ON {on} WHERE {where}',
                 [record[k] for k in t['fromKeys']])


def resolve_link(db, link, record, receiver):
    """The other page's driver records when the link is followed from record (the current record of fromPart)."""
    if link['how'] == 'same':
        return [record]                                 # the same entity: the same row
    if link['how'] == 'through':
        return _through(db, receiver, link['through'], record)
    if link['how'] == 'children':
        where = ' AND '.join(f'{q(c)} = ?' for c in link['fks'])
        return _rows(db, f'SELECT * FROM {q(receiver)} WHERE {where}', [record[k] for k in link['parentKeys']])
    where = ' AND '.join(f'{q(c)} = ?' for c in link['parentKeys'])
    return _rows(db, f'SELECT * FROM {q(receiver)} WHERE {where}', [record[k] for k in link['fks']])


def drop(model, page, entity, display):
    """What the designer does on a drop: the part added with the proposed link (or none)."""
    links = proposed_links(model, page['parts'], entity)
    follows = None
    if page['parts'] and links:
        l = links[0]
        follows = {k: l[k] for k in ('part', 'name', 'how', 'cardinality', 'relationship', 'fks', 'parentKeys', 'through')}
    page['parts'].append({'entity': entity, 'display': display, 'follows': follows})
    return links


# ------------------------------------------------------------------------------------------------- the page flow

CARD_NOTATION = {'oneToMany': '1 : n', 'manyToOne': 'n : 1', 'oneToOne': '1 : 1', 'manyToMany': 'n : n'}
DISPLAY_NAMES = {'detail': 'Detail', 'list': 'List', 'listDetail': 'List with detail'}


def _esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))


def page_flow_svg(pages):
    """The page flow diagram (author, 2026-11-27: "Show Page Flow Diagram"): each page a card - its title, then its
    parts (entity, display, what each follows); an arrow for each link between pages, from the part it starts at to
    the page it opens, labelled with the association's name and cardinality. Pages in columns by how far they are
    from the first page along the links; pages no link reaches in the last column. Light and dark (the viewer's)."""
    plist = pages.get('pages', [])
    index = {pg['title']: i for i, pg in enumerate(plist)}
    level = {}
    if plist:
        queue = [0]
        level[0] = 0
        while queue:
            i = queue.pop(0)
            for link in plist[i].get('links', []):
                j = index.get(link['page'])
                if j is not None and j not in level:
                    level[j] = level[i] + 1
                    queue.append(j)
        last = max(level.values()) + 1 if level else 0
        for i in range(len(plist)):
            level.setdefault(i, last)                     # no link reaches it: the last column
    W, HEAD, ROW, PAD, GAPX, GAPY, M = 250, 32, 20, 10, 190, 36, 40
    boxes, col_y = {}, {}
    for i, pg in enumerate(plist):
        col = level[i]
        h = HEAD + ROW * max(1, len(pg.get('parts', []))) + PAD
        x = M + col * (W + GAPX)
        y = col_y.get(col, M + 30)
        boxes[i] = (x, y, W, h)
        col_y[col] = y + h + GAPY
    # the arrows: forward ones (to a later column) from the part's row to the page's left edge, the ends spread out;
    # the others in lanes under the cards, one lane each, up into the page's bottom edge
    flows = []
    for i, pg in enumerate(plist):
        for link in pg.get('links', []):
            j = index.get(link['page'])
            if j is not None:
                flows.append((i, j, link))
    incoming = {}
    for i, j, link in flows:
        if boxes[j][0] > boxes[i][0]:
            incoming.setdefault(j, []).append(id(link))
    back = [(i, j, link) for i, j, link in flows if boxes[j][0] <= boxes[i][0]]
    cards_bottom = max((b[1] + b[3] for b in boxes.values()), default=M)
    LANE0, LANE = cards_bottom + 46, 34
    width = max((b[0] + b[2] for b in boxes.values()), default=M) + M
    height = (LANE0 + LANE * len(back) if back else cards_bottom) + M + 30
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
           f'font-family="-apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif">',
           '<style>'
           '.bg{fill:#f5f6f8}.card{fill:#fff;stroke:rgba(0,0,0,.12)}.head{fill:#113;}.title{fill:#fff;font-weight:600;font-size:14px}'
           '.part{fill:#333;font-size:12px}.note{fill:#777;font-size:11px}.link{fill:none;stroke:#2f6fde;stroke-width:1.6}'
           '.label,.card-n{paint-order:stroke;stroke:#f5f6f8;stroke-width:5px;stroke-linejoin:round}'
           '.label{fill:#2f6fde;font-size:11px;font-weight:600}.card-n{fill:#555;font-size:11px}.heading{fill:#222;font-size:16px;font-weight:600}'
           '@media (prefers-color-scheme: dark){.bg{fill:#1e1f22}.card{fill:#2b2c30;stroke:rgba(255,255,255,.12)}.head{fill:#0b1a3a}'
           '.part{fill:#ddd}.note{fill:#999}.link{stroke:#6aa0ff}.label{fill:#6aa0ff}.card-n{fill:#aaa}.heading{fill:#eee}'
           '.label,.card-n{stroke:#1e1f22}#arrow path{fill:#6aa0ff}}'
           '</style>',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
           '<path d="M0,0 L10,5 L0,10 z" fill="#2f6fde"/></marker></defs>',
           f'<rect class="bg" x="0" y="0" width="{width}" height="{height}"/>',
           f'<text class="heading" x="{M}" y="{M}">Page flow</text>']
    paths = []
    lane = 0
    for i, j, link in flows:
        sx, sy, sw, sh = boxes[i]
        tx, ty, tw, th = boxes[j]
        y1 = sy + HEAD + ROW * link.get('fromPart', 0) + 10
        if tx > sx:                                       # forward
            ends = incoming[j]
            k = ends.index(id(link))
            y2 = ty + 12 + k * (min(18, (th - 20) / max(1, len(ends))))
            x1, x2 = sx + sw, tx
            mid = (x1 + x2) / 2
            d = f'M{x1},{y1} C{mid},{y1} {mid},{y2} {x2},{y2}'
            lx, ly = mid, min(y1, y2) + abs(y2 - y1) / 2 - 8
        else:                                             # back, or the same column: a lane under the cards
            ly_lane = LANE0 + LANE * lane
            lane += 1
            x1 = sx + sw * 0.75
            x2 = tx + tw * 0.25 + (8 * lane if tx == sx else 0)
            r = 8
            down = sy + sh
            d = (f'M{x1},{down} V{ly_lane - r} Q{x1},{ly_lane} {x1 - r},{ly_lane} H{x2 + r} '
                 f'Q{x2},{ly_lane} {x2},{ly_lane - r} V{ty + th}')
            lx, ly = (x1 + x2) / 2, ly_lane - 6
        paths.append(f'<g class="flow" data-from="{_esc(plist[i]["title"])}" data-to="{_esc(link["page"])}">'
                     f'<path class="link" d="{d}" marker-end="url(#arrow)"/>'
                     f'<text class="label" x="{lx}" y="{ly}" text-anchor="middle">{_esc(link.get("name", ""))}'
                     f'<tspan class="card-n" dx="6">{CARD_NOTATION.get(link.get("cardinality"), "")}</tspan></text></g>')
    for i, pg in enumerate(plist):
        x, y, w, h = boxes[i]
        out.append(f'<g class="page" data-page="{_esc(pg["title"])}">')
        out.append(f'<rect class="card" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>')
        out.append(f'<path class="head" d="M{x},{y + HEAD} v-{HEAD - 10} a10,10 0 0 1 10,-10 h{w - 20} a10,10 0 0 1 10,10 v{HEAD - 10} z"/>')
        out.append(f'<text class="title" x="{x + 12}" y="{y + 21}">{_esc(pg["title"])}</text>')
        for k, part in enumerate(pg.get('parts', [])):
            ty = y + HEAD + ROW * k + 15
            f = part.get('follows')
            note = 'driver' if k == 0 else (f'{CARD_NOTATION.get(f.get("cardinality"), "")} from {pg["parts"][f["part"]]["entity"]}'
                                             if f else 'not linked')
            out.append(f'<text class="part" x="{x + 12}" y="{ty}">{_esc(part["entity"])} '
                       f'<tspan class="note">{_esc(DISPLAY_NAMES.get(part["display"], part["display"]))} · {_esc(note)}</tspan></text>')
        out.append('</g>')
    out.extend(paths)                                     # the arrows over the cards' edges, their labels readable
    out.append(f'<text class="note" x="{M}" y="{height - 16}">1 : n one to many · n : 1 many to one · 1 : 1 one to one · '
               f'n : n many to many (through a join table)</text>')
    out.append('</svg>')
    return '\n'.join(out)


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
    check('Products on that page: the product of the line chosen (direct, proposed first)',
          f and f['part'] == 2 and f['how'] == 'parent' and f['fks'] == ['ProductID'] and f['cardinality'] == 'manyToOne', links)
    check('... and, offered after it, the order\'s products through Order Details (many to many)',
          [(l['part'], l['how'], l['cardinality']) for l in links] == [(2, 'parent', 'manyToOne'), (0, 'through', 'manyToMany')], links)
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
    f = page4['parts'][2]['follows']
    check('Employees there: the territory\'s employees, through EmployeeTerritories (many to many)',
          f and f['how'] == 'through' and f['part'] == 1 and f['cardinality'] == 'manyToMany'
          and f['through']['table'] == 'EmployeeTerritories', f)
    shown = resolve_page(db, model, page4, _rows(db, 'SELECT * FROM "Region" WHERE "RegionID" = 1', ())[0])
    check('Eastern: Westboro, and its employee Buchanan', [r['TerritoryDescription'] for r in shown[1]['records']] == ['Westboro']
          and [r['LastName'] for r in shown[2]['records']] == ['Buchanan'], shown)

    page5 = {'title': 'Staff', 'icon': None, 'parts': []}
    drop(model, page5, 'Employees', 'detail')
    links = drop(model, page5, 'Employees', 'list')
    check('Employees twice (a manager and their staff): not offered yet (self-relationships later)',
          page5['parts'][1]['follows'] is None and links == [])

    # links between pages: a page dragged onto another shows the relationships between them
    customers = {'title': 'Customers', 'icon': None, 'parts': [{'entity': 'Customers', 'display': 'listDetail', 'follows': None}]}
    orders = {'title': 'Orders', 'icon': None, 'parts': [{'entity': 'Orders', 'display': 'listDetail', 'follows': None}]}
    products = {'title': 'Products', 'icon': None, 'parts': [{'entity': 'Products', 'display': 'listDetail', 'follows': None}]}
    categories = {'title': 'Categories', 'icon': None, 'parts': [{'entity': 'Categories', 'display': 'listDetail', 'follows': None}]}
    links = page_associations(model, customers, orders)
    check('Customers -> Orders: the customer\'s orders, one to many, named', len(links) == 1 and links[0]['how'] == 'children'
          and links[0]['fks'] == ['CustomerID'] and links[0]['cardinality'] == 'oneToMany'
          and links[0]['name'] == 'Customers to Orders', links)
    vinet = _rows(db, 'SELECT * FROM "Customers" WHERE "CustomerID" = \'VINET\'', ())[0]
    check('followed from VINET: order 10248', [r['OrderID'] for r in resolve_link(db, links[0], vinet, 'Orders')] == [10248])
    links = page_associations(model, orders, customers)
    check('Orders -> Customers: the order\'s customer, many to one', len(links) == 1 and links[0]['how'] == 'parent'
          and links[0]['cardinality'] == 'manyToOne', links)
    shippers = {'title': 'Shippers', 'icon': None, 'parts': [{'entity': 'Shippers', 'display': 'listDetail', 'follows': None}]}
    slinks = page_associations(model, orders, shippers)
    check('Orders -> Shippers: named with its role', slinks and slinks[0]['name'] == 'Orders to Shippers (ShipVia)', slinks)
    order = _rows(db, 'SELECT * FROM "Orders" WHERE "OrderID" = 10249', ())[0]
    check('followed from 10249: Toms Spezialitäten', [r['CompanyName'] for r in resolve_link(db, links[0], order, 'Customers')]
          == ['Toms Spezialitäten'])
    links = page_associations(model, page, customers)       # the invoice page -> Customers
    check('Order Entry -> Customers: from the order (its customer) and from its Customers part (the same record)',
          [(l['fromPart'], l['how']) for l in links] == [(0, 'parent'), (1, 'same')], links)
    links = page_associations(model, page, products)
    check('Order Entry -> Products: from the line chosen, its Products part, then the order\'s products (many to many)',
          [(l['fromPart'], l['how'], l['cardinality']) for l in links] == [(2, 'parent', 'manyToOne'), (3, 'same', 'oneToOne'),
                                                                          (0, 'through', 'manyToMany')], links)
    links = page_associations(model, products, page)
    check('Products -> Order Entry: the orders that include the product (many to many, through Order Details)',
          len(links) == 1 and links[0]['how'] == 'through' and links[0]['name'] == 'Products to Orders (through Order Details)', links)
    queso = _rows(db, 'SELECT * FROM "Products" WHERE "ProductID" = 11', ())[0]
    check('followed from Queso Cabrales: order 10248', [r['OrderID'] for r in resolve_link(db, links[0], queso, 'Orders')] == [10248])
    links = page_associations(model, categories, products)
    check('Categories -> Products: the category\'s products', len(links) == 1 and links[0]['how'] == 'children', links)
    check('Categories -> Orders: nothing in common', page_associations(model, categories, orders) == [])
    customers['links'] = [page_associations(model, customers, orders)[0]]
    page['links'] = [page_associations(model, page, products)[0]]
    allp = {'pages': [customers, orders, products, page]}
    check('pages with links pass the check', check_pages(model, allp) == [], check_pages(model, allp))
    orders['links'] = [{'page': 'Nowhere', 'fromPart': 0, 'how': 'parent', 'relationship': 'Customers'},
                       {'page': 'Orders', 'fromPart': 0, 'how': 'same', 'relationship': None},
                       {'page': 'Products', 'fromPart': 0, 'how': 'parent', 'relationship': 'Products'}]
    problems = check_pages(model, allp)
    for needle in ("no page 'Nowhere'", 'a link to its own page', 'no relationship "Products" (parent) from part 0'):
        check(f'the check reports: {needle}', any(needle in p for p in problems), problems)
    del orders['links'], customers['links'], page['links']

    # the page flow diagram
    import xml.etree.ElementTree as ET
    flow_pages = {'pages': [customers, orders, page, products]}
    customers['links'] = [page_associations(model, customers, orders)[0]]
    orders['links'] = [page_associations(model, orders, page)[0]] if page_associations(model, orders, page) else []
    page['links'] = [page_associations(model, page, customers)[0], page_associations(model, page, products)[0]]
    products['links'] = [page_associations(model, products, page)[0]]
    svg = page_flow_svg(flow_pages)
    try:
        root_el = ET.fromstring(svg)
        ok = True
    except ET.ParseError as e:
        ok, root_el = False, None
    check('page flow: well-formed SVG', ok)
    ns = '{http://www.w3.org/2000/svg}'
    groups = root_el.findall(f'{ns}g') if root_el is not None else []
    titles = [g.get('data-page') for g in groups if g.get('class') == 'page']
    flows = [(g.get('data-from'), g.get('data-to')) for g in groups if g.get('class') == 'flow']
    check('page flow: a card for each page', titles == ['Customers', 'Orders', 'Order Entry', 'Products'], titles)
    check('page flow: an arrow for each link, from page to page', sorted(flows) == sorted(
        [('Customers', 'Orders'), ('Order Entry', 'Customers'), ('Order Entry', 'Products'), ('Products', 'Order Entry')]
        + ([('Orders', 'Order Entry')] if orders['links'] else [])), flows)
    check('page flow: each arrow labelled with its name and cardinality', 'Customers to Orders' in svg and '1 : n' in svg
          and 'n : 1' in svg and 'n : n' in svg)
    check('page flow: the parts with what they follow', 'Customers <tspan class="note">Detail · n : 1 from Orders' in svg, svg[:0])
    with open(os.path.join(tempfile.gettempdir(), 'page_flow_test.svg'), 'w') as f:
        f.write(svg)
    for pg in (customers, orders, page, products):
        pg.pop('links', None)

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


def flow_example():
    """The example diagram: Northwind's Customers, Orders, the invoice page (Order Entry) and Products, linked."""
    model = read_model(northwind_db())
    customers = {'title': 'Customers', 'icon': None, 'parts': [{'entity': 'Customers', 'display': 'listDetail', 'follows': None}]}
    orders = {'title': 'Orders', 'icon': None, 'parts': [{'entity': 'Orders', 'display': 'listDetail', 'follows': None}]}
    products = {'title': 'Products', 'icon': None, 'parts': [{'entity': 'Products', 'display': 'listDetail', 'follows': None}]}
    entry = {'title': 'Order Entry', 'icon': 'doc.text', 'parts': []}
    for entity, display in (('Orders', 'detail'), ('Customers', 'detail'), ('Order Details', 'list'), ('Products', 'detail'),
                            ('Employees', 'detail'), ('Shippers', 'detail')):
        drop(model, entry, entity, display)
    customers['links'] = [page_associations(model, customers, orders)[0]]
    orders['links'] = [page_associations(model, orders, entry)[0]]
    entry['links'] = [page_associations(model, entry, customers)[0], page_associations(model, entry, products)[0]]
    products['links'] = [page_associations(model, products, entry)[0]]
    return page_flow_svg({'pages': [customers, orders, entry, products]})


def main(argv):
    if '--test' in argv:
        return 1 if run_tests() else 0
    if '--flow-example' in argv:
        print(flow_example())
        return 0
    if '--flow' in argv and len(argv) > argv.index('--flow') + 1:
        with open(argv[argv.index('--flow') + 1], encoding='utf-8') as f:
            print(page_flow_svg(json.load(f)))
        return 0
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
