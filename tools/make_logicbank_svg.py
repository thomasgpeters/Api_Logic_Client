#!/usr/bin/env python3
"""Draws the LogicBank for FutureBasic example's diagram: the three objects, their rules, and one save.

    python3 tools/make_logicbank_svg.py
    node tools/svg_to_png.js "src/LogicBankExample/LogicBank Example Model.svg" "src/LogicBankExample/LogicBank Diagram.png"

Edit this script, not the SVG.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'LogicBankExample', 'LogicBank Example Model.svg')
W, H = 1000, 720
INK, SOFT, LINE = '#1d1d1f', '#5f6368', '#c7c7cc'
BLUE, GREEN, ORANGE, PURPLE = '#0a63c9', '#1e8e3e', '#c26401', '#7b3fb5'

OBJECTS = [
    ('Customer', 'Name, CreditLimit, Discount', [
        (BLUE, 'Balance = sum of unshipped Orders’ AmountTotal'),
        (BLUE, 'UnshippedOrders = count of unshipped Orders'),
        (ORANGE, 'constraint: Balance ≤ CreditLimit'),
        (PURPLE, 'delete: prevented while it has Orders')]),
    ('Order', 'CustomerId, ShippedDate', [
        (GREEN, 'parent check: its Customer exists'),
        (GREEN, 'Discount = copy of Customer.Discount (when placed)'),
        (BLUE, 'AmountTotal = sum of its Items’ Amount'),
        (BLUE, 'ItemCount = count of its Items'),
        (PURPLE, 'delete: its Items go with it')]),
    ('Item', 'OrderId, Product, Quantity, UnitPrice', [
        (BLUE, 'Amount = Quantity × UnitPrice × (100 − Order.Discount) / 100'),
        (ORANGE, 'constraint: Quantity > 0')]),
]
STEPS = ['copies from parents', 'parent checks', 'formulas', 'sums and counts: adjust the parents',
         '… each parent saved by its rules', 'constraints', 'write',
         'a constraint fails: all rolls back']


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system, Helvetica, Arial, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<text x="40" y="52" font-size="26" font-weight="700" fill="{INK}">LogicBank for FutureBasic: the example’s rules</text>',
           f'<text x="40" y="80" font-size="15" fill="{SOFT}">Declared once in Rules.incl; enforced on every LogicInsert, LogicUpdate and LogicDelete.</text>']
    x, w, y = 40, 600, 112
    tops = []
    for name, typed, rules in OBJECTS:
        h = 64 + 24 * len(rules)
        tops.append((y, h))
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#f5f7fa" stroke="{LINE}" stroke-width="1.5"/>')
        out.append(f'<text x="{x + 20}" y="{y + 32}" font-size="20" font-weight="700" fill="{INK}">{name}</text>')
        out.append(f'<text x="{x + 140}" y="{y + 32}" font-size="14" fill="{SOFT}">{esc(typed)}</text>')
        for i, (colour, text) in enumerate(rules):
            ty = y + 60 + 24 * i
            out.append(f'<circle cx="{x + 26}" cy="{ty - 5}" r="4" fill="{colour}"/>')
            out.append(f'<text x="{x + 40}" y="{ty}" font-size="15" fill="{INK}">{esc(text)}</text>')
        y += h + 46
    for (y1, h1), (y2, _) in zip(tops, tops[1:]):
        mid = y1 + h1 + 23
        out.append(f'<line x1="{x + 200}" y1="{y2 - 4}" x2="{x + 200}" y2="{y1 + h1 + 8}" stroke="{BLUE}" stroke-width="2" marker-end="url(#up)"/>')
        out.append(f'<text x="{x + 212}" y="{mid + 5}" font-size="13" fill="{BLUE}">sums and counts adjust the parent</text>')
        out.append(f'<line x1="{x + 440}" y1="{y1 + h1 + 4}" x2="{x + 440}" y2="{y2 - 8}" stroke="{GREEN}" stroke-width="2" marker-end="url(#down)"/>')
        out.append(f'<text x="{x + 452}" y="{mid + 5}" font-size="13" fill="{GREEN}">copies, parent values</text>')
    out.insert(1, f'<defs><marker id="up" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
                  f'<marker id="down" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{GREEN}"/></marker></defs>')
    px, pw, py = 670, 300, 112
    ph = 70 + 30 * len(STEPS)
    out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="#ffffff" stroke="{LINE}" stroke-width="1.5"/>')
    out.append(f'<text x="{px + 20}" y="{py + 34}" font-size="18" font-weight="700" fill="{INK}">One save, in order</text>')
    for i, step in enumerate(STEPS):
        colour = ORANGE if i == len(STEPS) - 1 else INK
        out.append(f'<text x="{px + 20}" y="{py + 70 + 30 * i}" font-size="14" fill="{colour}">{i + 1}. {esc(step)}</text>')
    out.append(f'<text x="{px}" y="{py + ph + 34}" font-size="13" fill="{SOFT}">Data Memory.incl keeps the objects in memory;</text>')
    out.append(f'<text x="{px}" y="{py + ph + 54}" font-size="13" fill="{SOFT}">Data Records.incl keeps them in SQLite.</text>')
    out.append('</svg>')
    with open(OUT, 'w') as f:
        f.write('\n'.join(out) + '\n')
    print('wrote', OUT)


if __name__ == '__main__':
    main()
