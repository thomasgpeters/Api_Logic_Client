#!/usr/bin/env python3
"""Draw the SQL Generator's object model: the dictionaries and arrays a statement is described
with (DataObject_Super.incl), and what the generator makes of them (DataObject.incl).

    python3 tools/make_sql_generator_svg.py
writes docs/design/SQL Generator Object Model.svg and the same file into src/SQLGeneratorExample/.
Edit this script, not the SVG.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = [os.path.join(ROOT, 'docs', 'design', 'SQL Generator Object Model.svg'),
       os.path.join(ROOT, 'src', 'SQLGeneratorExample', 'SQL Generator Object Model.svg')]

ROW = 22          # one key line
HEAD = 30         # a box's title band
W_DICT = 250
W_ENTRY = 300
parts = []


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def box(x, y, w, title, kind, rows, note=None):
    """A collection: kind 'dict' or 'array'; rows are (key, value) pairs. Returns (height, row ys)."""
    h = HEAD + ROW * len(rows) + 10
    cls = 'dict' if kind == 'dict' else 'array'
    parts.append(f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="body"/>')
    parts.append(f'<path d="M{x} {y+8} a8 8 0 0 1 8 -8 h{w-16} a8 8 0 0 1 8 8 v{HEAD-8} h-{w} z" class="band"/>')
    parts.append(f'<text x="{x+12}" y="{y+20}" class="title">{esc(title)}</text>')
    tag = 'NSMutableDictionary' if kind == 'dict' else 'NSMutableArray'
    parts.append(f'<text x="{x+w-12}" y="{y+20}" class="kind" text-anchor="end">{tag}</text>')
    ys = []
    for i, (k, v) in enumerate(rows):
        ry = y + HEAD + 18 + i * ROW
        ys.append(ry - 5)
        parts.append(f'<text x="{x+12}" y="{ry}" class="key">{esc(k)}</text>')
        if v:
            parts.append(f'<text x="{x+w-12}" y="{ry}" class="val" text-anchor="end">{esc(v)}</text>')
    parts.append('</g>')
    if note:
        parts.append(f'<text x="{x}" y="{y+h+16}" class="note">{esc(note)}</text>')
    return h, ys


def arrow(x1, y1, x2, y2, label=None):
    mx = (x1 + x2) / 2
    parts.append(f'<path d="M{x1} {y1} C{mx} {y1} {mx} {y2} {x2-6} {y2}" class="link" marker-end="url(#arrow)"/>')
    if label:
        parts.append(f'<text x="{mx}" y="{(y1+y2)/2 - 6}" class="label" text-anchor="middle">{esc(label)}</text>')


def heading(x, y, t, sub):
    parts.append(f'<text x="{x}" y="{y}" class="h">{esc(t)}</text>')
    parts.append(f'<text x="{x}" y="{y+20}" class="sub">{esc(sub)}</text>')


def flow(x, y, w, text, cls='out'):
    parts.append(f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="34" rx="17" class="pill"/>'
                 f'<text x="{x+w/2}" y="{y+22}" text-anchor="middle" class="pilltext">{esc(text)}</text></g>')


# --- SELECT ---------------------------------------------------------------------------------
X1, X2, X3 = 30, 360, 720
heading(X1, 40, 'SELECT: a query is a dictionary of arrays',
        'fn InitQueryDictionary makes it; each Add... function adds one dictionary to an array')
qy = 80
qh, qrows = box(X1, qy, W_DICT, 'query', 'dict',
                [('selecttables', 'array'), ('selectcols', 'array'), ('associations', 'array'),
                 ('filter', 'array'), ('metadata', 'array'), ('results', 'dictionary')],
                note='fn InitQueryDictionary')
entries = [
    ('selecttables', 'AddTableToQuery', [('tablename', '"person"'), ('aliasname', '"p"')]),
    ('selectcols', 'AddColumnToQuery', [('columnname', '"p.surName"'), ('aliasname', '"Surname"')]),
    ('associations', 'AddAssociationToQuery', [('lefttablealias', '"a"'), ('leftcolumnname', '"personID"'),
                                               ('righttablealias', '"p"'), ('rightcolumnname', '"id"'),
                                               ('operator', '_isEqual')]),
    ('filter', 'AddFilterToQuery', [('tablealias', '"p"'), ('columnname', '"balance"'),
                                    ('value', '100.0  (NSNumber)'), ('type', '_realType'),
                                    ('operator', '_isGreaterThan'), ('logic', '_and | _or (2nd on)')]),
]
ey = qy
for i, (key, fn, rows) in enumerate(entries):
    ah, ays = box(X2, ey, 220, key, 'array', [('[0]', 'dictionary'), ('[1] ...', '')])
    arrow(X1 + W_DICT, qrows[i], X2, ey + HEAD + 13)
    eh, _ = box(X3, ey, W_ENTRY, 'one entry', 'dict', rows, note='fn ' + fn)
    arrow(X2 + 220, ays[0], X3, ey + HEAD + 13)
    ey += max(ah, eh) + 34
sel_bottom = ey

flow(X1, qy + qh + 40, W_DICT, 'fn GenerateSelectSQL( query )')
flow(X1, qy + qh + 84, W_DICT, 'fn QueryParameterValues( query )')
parts.append(f'<text x="{X1}" y="{qy+qh+142}" class="code">SELECT "p"."surName" AS "Surname"</text>')
parts.append(f'<text x="{X1}" y="{qy+qh+160}" class="code">  FROM "person" AS "p"</text>')
parts.append(f'<text x="{X1}" y="{qy+qh+178}" class="code"> WHERE "p"."balance" &gt; ?</text>')
parts.append(f'<text x="{X1}" y="{qy+qh+202}" class="code2">values: [ 100.0 ]</text>')
parts.append(f'<text x="{X1}" y="{qy+qh+232}" class="note">rows come back as an array of</text>')
parts.append(f'<text x="{X1}" y="{qy+qh+248}" class="note">dictionaries: {{ "Surname": "Fischer" }}</text>')

# --- writes ---------------------------------------------------------------------------------
wy = sel_bottom + 20
heading(X1, wy, 'INSERT, UPDATE, DELETE: a dictionary per statement',
        'the table, the column values in SQL order, and the filters (the same entries as a query\'s)')
wy += 40
cw = 230
cols = [
    ('insert', 'InitInsertIntoDictionary', [('insertintotable', '"person"'), ('columnvalues', 'array')],
     'GenerateInsertIntoSQL'),
    ('insert rows', 'InitInsertRowsDictionary', [('insertintotable', '"person"'), ('rows', 'array'),
                                                 ('columnnames', 'array')], 'GenerateInsertRowsSQL'),
    ('update', 'InitUpdateDictionary', [('updatetable', '"person"'), ('columnvalues', 'array'),
                                        ('filter', 'array')], 'GenerateUpdateSQL'),
    ('delete', 'InitDeleteFromDictionary', [('deletefromtable', '"contact"'), ('filter', 'array')],
     'GenerateDeleteFromSQL'),
]
tallest = 0
for i, (title, fn, rows, gen) in enumerate(cols):
    x = X1 + i * (cw + 22)
    h, _ = box(x, wy, cw, title, 'dict', rows, note='fn ' + fn)
    flow(x, wy + h + 30, cw, 'fn ' + gen)
    tallest = max(tallest, h)
ey2 = wy + tallest + 90
box(X1, ey2, cw * 2 + 22, 'a columnvalues entry', 'dict',
    [('columnname', '"surName"'), ('value', '"Lima"  (NULL: SQL NULL)'), ('type', '_textType')],
    note='fn AddColumnToInsert / fn AddColumnToUpdate')
box(X1 + 2 * (cw + 22), ey2, cw * 2 + 22, 'a rows entry: a SELECT row, reversed', 'dict',
    [('"givenName"', '"Kai"'), ('"surName"', '"Nakamura"'), ('"balance"', '15.0  (missing: NULL)')],
    note='fn AddRowsToInsert: an array of these')
total_h = ey2 + HEAD + ROW * 3 + 86
parts.append(f'<text x="{X1}" y="{total_h-30}" class="note">An UPDATE or DELETE with an empty filter array gets NULL from its Generate... function: it never changes a whole table.</text>')
parts.append(f'<text x="{X1}" y="{total_h-12}" class="note">fn QueryParameterValues lists the values in placeholder order: column values, then rows, then filters.</text>')

W = X3 + W_ENTRY + 40
css = '''
:root{--bg:#ffffff;--ink:#1d2433;--muted:#5b6475;--line:#c9d1de;--dict:#112850;--dictInk:#ffffff;
--array:#0f766e;--arrayInk:#ffffff;--body:#f6f8fb;--key:#1d2433;--val:#5b3cc4;--pill:#eef2f8;--code:#1f5fbf}
@media (prefers-color-scheme: dark){:root{--bg:#14171c;--ink:#e7ebf2;--muted:#a3acbb;--line:#3a4250;
--dict:#2b4c8c;--array:#138a80;--body:#1d222a;--key:#e7ebf2;--val:#b9a6ff;--pill:#232a35;--code:#7fb0ff}}
svg{background:var(--bg)}
text{font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;fill:var(--ink)}
.h{font-size:19px;font-weight:700}.sub{font-size:13px;fill:var(--muted)}
.body{fill:var(--body);stroke:var(--line)}
.dict .band{fill:var(--dict)}.array .band{fill:var(--array)}
.title{font-size:13px;font-weight:700;fill:#ffffff}.kind{font-size:10.5px;fill:#ffffff;opacity:.8}
.key{font-size:12.5px;font-family:Menlo,Monaco,monospace;fill:var(--key)}
.val{font-size:12px;font-family:Menlo,Monaco,monospace;fill:var(--val)}
.note{font-size:12px;fill:var(--muted)}.label{font-size:11px;fill:var(--muted)}
.link{fill:none;stroke:var(--muted);stroke-width:1.4}
.pill{fill:var(--pill);stroke:var(--line)}.pilltext{font-size:12.5px;font-family:Menlo,Monaco,monospace}
.code{font-size:12.5px;font-family:Menlo,Monaco,monospace;fill:var(--code)}
.code2{font-size:12.5px;font-family:Menlo,Monaco,monospace;fill:var(--val)}
'''
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {total_h}" width="{W}" height="{total_h}" '
       f'role="img" aria-label="SQL Generator object model">\n<title>SQL Generator object model</title>\n'
       f'<style>{css}</style>\n<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
       f'markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#8a93a3"/></marker></defs>\n'
       + '\n'.join(parts) + '\n</svg>\n')
for path in OUT:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(svg)
    print('wrote', os.path.relpath(path, ROOT))
