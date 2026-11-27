#!/usr/bin/env python3
"""web_layout_reference.py - a XIB as a web page: the Web Toolkit's layout rules, in Python.

The reference for three implementations that must agree:
  - src/WebToolkit/Web Layout.incl     (Objective-C in an FB module: the web app reads a XIB at run time)
  - the layout tool's preview           (src/WebToolkit/Layout Tool/Layout Tool.html, JavaScript)
  - this file                           (the rules, readable, and the tests)

A XIB (Interface Builder's XML, the same file a desktop app uses) becomes a tree of web widgets:
  1. controls   each element -> one control: kind, id, title ..., and its frame from the top-left (XIBs measure from
                the bottom-left); plain nested views are see-through (their controls join the parent's)
  2. labels     a label just left of an input, or just above it, becomes that input's label ("Name:" -> "Name")
  3. rows       controls whose frames share a band of height form a row, left to right; a row of buttons is a toolbar
                (at the right when it starts past the middle); in a row, each control spans its share of 12 columns
     an empty label with an Identifier is a message band: where the app's messages appear (a rule's refusal ...)
  4. boxes      an NSBox is a card - a form when it holds inputs - with its title as a heading, laid out the same way

Widget ids: the control's identifier (Interface Builder: Identity > Identifier), else "tag<n>" from its tag, else the
XIB's own id. Rows are "<parent>-r<n>".

    python3 tools/web_layout_reference.py --tree some.xib      # the widget tree, as JSON
    python3 tools/web_layout_reference.py --test               # the rules on the repository's XIBs and test layouts
"""
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_KINDS = ('field', 'textarea', 'select', 'radio')
HEADING_STYLES = {'largeTitle': 1, 'title1': 2, 'title2': 2, 'title3': 3, 'headline': 4}


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def frame_of(el):
    for r in el.findall('rect'):
        if r.get('key') == 'frame':
            return num(r.get('x')), num(r.get('y')), num(r.get('width')), num(r.get('height'))
    return 0.0, 0.0, 0.0, 0.0


def child_keyed(el, tag, key):
    for c in el.findall(tag):
        if c.get('key') == key:
            return c
    return None


def cell_of(el):
    for c in el:
        if c.get('key') == 'cell':
            return c
    return None


def subviews_of(el):
    s = el.find('subviews')
    return list(s) if s is not None else []


def half_up(v):
    """rounding as C's floor( v + 0.5 ) and JavaScript's Math.round (Python's round() rounds halves to even)"""
    return int(math.floor(v + 0.5))


def strip_colon(t):
    t = (t or '').strip()
    return t[:-1].rstrip() if t.endswith(':') else t


class Extractor:
    def __init__(self):
        self.used = set()

    def widget_id(self, el, fallback_el=None):
        for e in (el, fallback_el):
            if e is None:
                continue
            if e.get('identifier'):
                return self.unique(e.get('identifier'))
        for e in (el, fallback_el):
            if e is None:
                continue
            if e.get('tag') and e.get('tag') != '0':
                return self.unique('tag' + e.get('tag'))
        return self.unique(el.get('id') or 'control')

    def unique(self, wid):
        base, n = wid, 2
        while wid in self.used:
            wid, n = f'{base}-{n}', n + 1
        self.used.add(wid)
        return wid

    def controls(self, view, height, dx=0.0, dy=0.0):
        """the controls in a view's subviews, frames from the top-left of the view; dx, dy: offsets of a see-through
        nested view (top-left based)"""
        out = []
        for el in subviews_of(view):
            x, y, w, h = frame_of(el)
            top = height - (y + h)
            frame = {'x': x + dx, 'top': top + dy, 'w': w, 'h': h}
            if el.tag in ('customView', 'view'):
                kids = subviews_of(el)
                if kids and all(k.tag == 'button' and (cell_of(k) is not None and cell_of(k).get('type') == 'radio') for k in kids):
                    c = self.radio_group(el, kids, frame)
                    if c:
                        out.append(c)
                else:
                    out += self.controls(el, h, frame['x'], frame['top'])
                continue
            c = self.control(el, frame)
            if c:
                out.append(c)
        return out

    def common(self, el, c):
        cell = cell_of(el)
        if el.get('hidden') == 'YES':
            c['visible'] = False
        if el.get('enabled') == 'NO' or (cell is not None and cell.get('enabled') == 'NO'):
            c['enabled'] = False
        return c

    def control(self, el, frame):
        tag, cell = el.tag, cell_of(el)
        c = dict(frame)
        if tag in ('textField', 'secureTextField', 'searchField', 'comboBox'):
            title = (cell.get('title') if cell is not None else '') or ''
            editable = cell is not None and cell.get('editable') == 'YES'
            if tag != 'textField' or editable:
                if tag == 'textField' and cell.get('lineBreakMode') == 'wordWrapping' and frame['h'] > 30:
                    c.update(kind='textarea', lines=max(2, half_up(frame['h'] / 17)))
                else:
                    itype = {'secureTextField': 'password', 'searchField': 'search'}.get(tag, 'text')
                    if cell is not None and child_keyed(cell, 'numberFormatter', 'formatter') is not None:
                        itype = 'number'
                    c.update(kind='field', type=itype)
                c.update(placeholder=(cell.get('placeholderString') if cell is not None else '') or '', label='')
            else:
                font = child_keyed(cell, 'font', 'font') if cell is not None else None
                style = font.get('textStyle') if font is not None else None
                color = child_keyed(cell, 'color', 'textColor') if cell is not None else None
                if not title.strip() and el.get('identifier'):
                    c.update(kind='message', text='', role='info')     # an empty, named label: where the app speaks
                elif style in HEADING_STYLES:
                    c.update(kind='heading', text=title, level=HEADING_STYLES[style])
                else:
                    look = ''
                    if color is not None and color.get('name') in ('secondaryLabelColor', 'tertiaryLabelColor'):
                        look = 'muted'
                    c.update(kind='text', text=title, look=look, label_candidate=bool(title.strip()))
        elif tag == 'datePicker':
            els = child_keyed(cell, 'datePickerElements', 'datePickerElements') if cell is not None else None
            has_date = els is not None and els.get('day') == 'YES'
            has_time = els is not None and els.get('hour') == 'YES'
            c.update(kind='field', type='datetime-local' if has_date and has_time else ('time' if has_time else 'date'), placeholder='', label='')
        elif tag == 'slider':
            c.update(kind='field', type='range', placeholder='', label='')
        elif tag == 'colorWell':
            c.update(kind='field', type='color', placeholder='', label='')
        elif tag == 'button':
            btype = cell.get('type') if cell is not None else 'push'
            title = (cell.get('title') if cell is not None else '') or ''
            if btype == 'check':
                c.update(kind='checkbox', label=title)
            elif btype == 'radio':
                c.update(kind='radio', label='', options=[{'code': title, 'title': title}])
            else:
                if not title.strip():
                    return None                       # an image-only button (an info button): no web widget
                key = ''
                if cell is not None:
                    k = child_keyed(cell, 'string', 'keyEquivalent')
                    key = (k.text or '').strip() if k is not None else ''
                c.update(kind='button', text=title, role='primary' if key == 'DQ' else 'secondary')
        elif tag == 'popUpButton':
            opts = []
            for item in el.iter('menuItem'):
                t = item.get('title') or ''
                if item.get('isSeparatorItem') == 'YES':
                    continue
                opts.append({'code': item.get('tag') if item.get('tag') not in (None, '0') else t, 'title': t})
            c.update(kind='select', options=opts, label='')
        elif tag == 'scrollView':
            doc = None
            clip = child_keyed(el, 'clipView', 'contentView')
            if clip is not None:
                for k in subviews_of(clip):
                    doc = k
                    break
            if doc is not None and doc.tag in ('tableView', 'outlineView'):
                cols = []
                for col in doc.iter('tableColumn'):
                    head = child_keyed(col, 'tableHeaderCell', 'headerCell')
                    title = (head.get('title') if head is not None else '') or col.get('identifier') or ''
                    align = 'end' if head is not None and head.get('alignment') == 'right' else ''
                    entry = {'key': col.get('identifier') or title, 'title': title}
                    if align:
                        entry['align'] = align
                    cols.append(entry)
                c.update(kind='table', columns=cols)
                c['id'] = self.widget_id(doc, el)
                return self.common(el, c)
            if doc is not None and doc.tag == 'textView':
                c.update(kind='textarea', lines=max(2, half_up(frame['h'] / 17)), label='')
                c['id'] = self.widget_id(doc, el)
                return self.common(el, c)
            return None
        elif tag == 'box':
            if el.get('boxType') == 'separator':
                c.update(kind='divider')
            else:
                content = child_keyed(el, 'view', 'contentView')
                kids = []
                if content is not None:
                    cx, cy, cw, ch = frame_of(content)
                    kids = self.controls(content, ch)
                title = el.get('title') or ''
                if el.get('titlePosition') == 'noTitle':
                    title = ''
                c.update(kind='box', title=title, children=kids)
        elif tag == 'imageView':
            image = (cell.get('image') if cell is not None else '') or ''
            c.update(kind='image', src=(image + '.png') if image and '.' not in image else image, alt='')
        else:
            return None
        c['id'] = self.widget_id(el)
        return self.common(el, c)

    def radio_group(self, view, buttons, frame):
        opts = []
        for b in buttons:
            t = (cell_of(b).get('title') or '')
            opts.append({'code': t, 'title': t})
        c = dict(frame, kind='radio', label='', options=opts)
        c['id'] = self.widget_id(view)
        return self.common(view, c)


def top_view(root, name=None):
    objects = root.find('objects')
    for el in objects:
        if el.tag in ('customView', 'view') and (not name or el.get('identifier') == name or el.get('id') == name):
            return el
        if el.tag == 'window' and not name:
            v = child_keyed(el, 'view', 'contentView')
            if v is not None:
                return v
    return None


# --- step 2: labels ---

def center(c):
    return c['top'] + c['h'] / 2


def pair_labels(controls):
    labels = sorted((c for c in controls if c.get('label_candidate')), key=lambda c: (c['top'], c['x']))
    inputs = [c for c in controls if c['kind'] in INPUT_KINDS]
    taken = set()
    gone = set()
    for lab in labels:
        best, best_gap = None, None
        right = lab['x'] + lab['w']
        for inp in inputs:                                         # a label just left of its input
            if id(inp) in taken:
                continue
            gap = inp['x'] - right
            same_band = abs(center(inp) - center(lab)) <= max(lab['h'], 22) / 2 + 4 or (lab['top'] >= inp['top'] - 4 and lab['top'] <= inp['top'] + 8)
            if same_band and -8 <= gap <= 40 and (best is None or gap < best_gap):
                best, best_gap = inp, gap
        if best is None:
            bottom = lab['top'] + lab['h']
            for inp in inputs:                                     # or just above it
                if id(inp) in taken:
                    continue
                gap = inp['top'] - bottom
                if -4 <= gap <= 12 and abs(inp['x'] - lab['x']) <= 16 and (best is None or gap < best_gap):
                    best, best_gap = inp, gap
            if best is not None:
                best['label'] = strip_colon(lab['text'])
                taken.add(id(best))
                gone.add(id(lab))
            continue
        best['label'] = strip_colon(lab['text'])
        best['w'] = best['x'] + best['w'] - lab['x']                # the pair spans the label too
        best['x'] = lab['x']
        taken.add(id(best))
        gone.add(id(lab))
    return [c for c in controls if id(c) not in gone]


# --- step 3: rows ---

def rows_of(controls):
    rows = []
    for c in sorted(controls, key=lambda c: (c['top'], c['x'])):
        if rows:
            r = rows[-1]
            overlap = min(r['bottom'], c['top'] + c['h']) - max(r['top'], c['top'])
            if overlap >= 0.5 * min(c['h'], r['min_h']):
                r['items'].append(c)
                r['top'], r['bottom'] = min(r['top'], c['top']), max(r['bottom'], c['top'] + c['h'])
                r['min_h'] = min(r['min_h'], c['h'])
                continue
        rows.append({'items': [c], 'top': c['top'], 'bottom': c['top'] + c['h'], 'min_h': c['h']})
    for r in rows:
        r['items'].sort(key=lambda c: c['x'])
    return rows


def widget_of(c, width):
    """one control -> a widget {kind, id, props, children}"""
    k = c['kind']
    props = {}
    if k == 'heading':
        props = {'text': c['text'], 'level': c['level']}
    elif k == 'text':
        props = {'text': c['text'], 'look': c['look']}
    elif k == 'field':
        props = {'label': c.get('label', ''), 'type': c['type'], 'placeholder': c.get('placeholder', '')}
    elif k == 'textarea':
        props = {'label': c.get('label', ''), 'lines': c['lines']}
    elif k == 'checkbox':
        props = {'label': c['label']}
    elif k in ('radio', 'select'):
        props = {'label': c.get('label', ''), 'options': c['options']}
    elif k == 'button':
        props = {'text': c['text'], 'role': c['role']}
    elif k == 'table':
        props = {'columns': c['columns']}
    elif k == 'image':
        props = {'src': c['src'], 'alt': c['alt']}
    elif k == 'message':
        props = {'text': c['text'], 'role': c['role']}
    elif k == 'divider':
        props = {}
    if c.get('visible') is False:
        props['visible'] = False
    if c.get('enabled') is False:
        props['enabled'] = False
    if k == 'box':
        inner = layout(pair_labels(c['children']), c['w'], c['id'])
        has_input = any_input(inner)
        if c['title']:
            inner.insert(0, {'kind': 'heading', 'id': c['id'] + '-title', 'props': {'text': c['title'], 'level': 3}, 'children': []})
        w = {'kind': 'container', 'id': c['id'], 'props': {'layout': 'form' if has_input else 'card'}, 'children': inner}
        if c.get('visible') is False:
            w['props']['visible'] = False
        return w
    return {'kind': k, 'id': c['id'], 'props': props, 'children': []}


def any_input(widgets):
    for w in widgets:
        if w['kind'] in INPUT_KINDS + ('checkbox',) or any_input(w['children']):
            return True
    return False


def span(c, width):
    return max(1, min(12, half_up(12 * c['w'] / width))) if width > 0 else 12


def layout(controls, width, parent_id):
    out = []
    for n, r in enumerate(rows_of(controls), 1):
        items = r['items']
        if len(items) == 1:
            out.append(widget_of(items[0], width))
            continue
        if all(c['kind'] == 'button' for c in items):
            lay = 'toolbar-end' if items[0]['x'] > width / 2 else 'toolbar'
            out.append({'kind': 'container', 'id': f'{parent_id}-r{n}', 'props': {'layout': lay},
                        'children': [widget_of(c, width) for c in items]})
            continue
        kids = []
        for c in items:
            w = widget_of(c, width)
            w['props']['span'] = span(c, width)
            kids.append(w)
        out.append({'kind': 'container', 'id': f'{parent_id}-r{n}', 'props': {'layout': 'row'}, 'children': kids})
    return out


def tree_from_xib(text, parent_id='page', view_name=None):
    root = ET.fromstring(text)
    view = top_view(root, view_name)
    if view is None:
        return []
    x, y, w, h = frame_of(view)
    ex = Extractor()
    controls = ex.controls(view, h)
    return layout(pair_labels(controls), w, parent_id)


# --- tests ---

TEST_XIB = '''<?xml version="1.0" encoding="UTF-8"?>
<document type="com.apple.InterfaceBuilder3.Cocoa.XIB" version="3.0" toolsVersion="22146" targetRuntime="MacOSX.Cocoa" propertyAccessControl="none" useAutolayout="YES">
  <objects>
    <customObject id="-2" userLabel="File's Owner"/>
    <customView id="root" identifier="CustomerPage">
      <rect key="frame" x="0.0" y="0.0" width="600" height="400"/>
      <subviews>
        <textField id="t1"><rect key="frame" x="20" y="350" width="400" height="31"/>
          <textFieldCell key="cell" title="Customer" id="t1c"><font key="font" textStyle="largeTitle"/></textFieldCell></textField>
        <textField id="l1"><rect key="frame" x="20" y="310" width="100" height="16"/>
          <textFieldCell key="cell" title="Name:" id="l1c"><font key="font" usesAppearanceFont="YES"/></textFieldCell></textField>
        <textField identifier="customerName" id="f1"><rect key="frame" x="128" y="307" width="440" height="22"/>
          <textFieldCell key="cell" editable="YES" placeholderString="the name" id="f1c"/></textField>
        <textField id="l2"><rect key="frame" x="20" y="270" width="100" height="16"/>
          <textFieldCell key="cell" title="Credit limit:" id="l2c"/></textField>
        <textField identifier="customerLimit" id="f2"><rect key="frame" x="128" y="267" width="150" height="22"/>
          <textFieldCell key="cell" editable="YES" id="f2c"><numberFormatter key="formatter" id="nf"/></textFieldCell></textField>
        <textField id="l3"><rect key="frame" x="300" y="270" width="80" height="16"/>
          <textFieldCell key="cell" title="Since:" id="l3c"/></textField>
        <datePicker identifier="customerSince" id="d1"><rect key="frame" x="388" y="266" width="150" height="24"/>
          <datePickerCell key="cell" id="d1c"><datePickerElements key="datePickerElements" year="YES" month="YES" day="YES"/></datePickerCell></datePicker>
        <button tag="17" id="c1"><rect key="frame" x="128" y="235" width="200" height="18"/>
          <buttonCell key="cell" type="check" title="Active" id="c1c"/></button>
        <popUpButton identifier="customerTerms" id="p1"><rect key="frame" x="128" y="200" width="200" height="25"/>
          <popUpButtonCell key="cell" id="p1c"><menu key="menu" id="m1"><items>
            <menuItem title="Net 30" tag="30" id="i1"/><menuItem title="Net 60" tag="60" id="i2"/></items></menu></popUpButtonCell></popUpButton>
        <textField id="l4"><rect key="frame" x="20" y="205" width="100" height="16"/>
          <textFieldCell key="cell" title="Terms:" id="l4c"/></textField>
        <customView tag="40" id="rg"><rect key="frame" x="128" y="160" width="300" height="18"/>
          <subviews>
            <button tag="30400" id="r1"><rect key="frame" x="0" y="0" width="80" height="18"/><buttonCell key="cell" type="radio" title="Retail" id="r1c"/></button>
            <button tag="30401" id="r2"><rect key="frame" x="80" y="0" width="80" height="18"/><buttonCell key="cell" type="radio" title="Wholesale" id="r2c"/></button>
          </subviews></customView>
        <textField id="l5"><rect key="frame" x="20" y="161" width="100" height="16"/>
          <textFieldCell key="cell" title="Kind:" id="l5c"/></textField>
        <box title="Notes" id="bx" identifier="notesBox"><rect key="frame" x="17" y="60" width="566" height="90"/>
          <view key="contentView" id="bxv"><rect key="frame" x="3" y="3" width="560" height="70"/>
            <subviews>
              <textField id="bl"><rect key="frame" x="10" y="44" width="100" height="16"/><textFieldCell key="cell" title="Remarks" id="blc"/></textField>
              <textField identifier="remarks" id="bf"><rect key="frame" x="10" y="4" width="540" height="36"/>
                <textFieldCell key="cell" editable="YES" lineBreakMode="wordWrapping" id="bfc"/></textField>
            </subviews></view></box>
        <textField identifier="customerMessage" id="msg"><rect key="frame" x="20" y="44" width="400" height="16"/>
          <textFieldCell key="cell" title="" id="msgc"/></textField>
        <button identifier="save" id="b1"><rect key="frame" x="490" y="13" width="90" height="32"/>
          <buttonCell key="cell" type="push" title="Save" id="b1c"><string key="keyEquivalent" base64-UTF8="YES">
DQ
</string></buttonCell></button>
        <button identifier="cancel" id="b2"><rect key="frame" x="395" y="13" width="90" height="32"/>
          <buttonCell key="cell" type="push" title="Cancel" id="b2c"/></button>
        <button id="info"><rect key="frame" x="580" y="13" width="18" height="22"/>
          <buttonCell key="cell" type="bevel" imagePosition="only" id="infoc"/></button>
      </subviews>
    </customView>
  </objects>
</document>'''

def flat(tree):
    for w in tree:
        yield w
        yield from flat(w['children'])


def run_tests():
    failures = []

    def check(name, ok):
        print(('PASS ' if ok else 'FAIL ') + name)
        if not ok:
            failures.append(name)

    tree = tree_from_xib(TEST_XIB)
    ws = {w['id']: w for w in flat(tree)}
    kinds = [w['kind'] for w in tree]
    check('the heading: a large-title label', tree[0]['kind'] == 'heading' and tree[0]['props'] == {'text': 'Customer', 'level': 1})
    check('a label left of a field becomes its label ("Name:" -> "Name")', ws['customerName']['props']['label'] == 'Name')
    check('the identifier is the widget id', 'customerName' in ws and 'customerLimit' in ws)
    check('a number formatter: a number field', ws['customerLimit']['props']['type'] == 'number')
    check('a date picker: a date field, labelled', ws['customerSince']['props'] == {'label': 'Since', 'type': 'date', 'placeholder': '', 'span': 5})
    check('two fields in one band: a row, spans of 12', ws['page-r3']['kind'] == 'container' and ws['page-r3']['props']['layout'] == 'row'
          and [c['id'] for c in ws['page-r3']['children']] == ['customerLimit', 'customerSince'] and ws['customerLimit']['props']['span'] == 5)
    check('a check box, by its tag (tag17)', ws['tag17']['kind'] == 'checkbox' and ws['tag17']['props']['label'] == 'Active')
    check('a pop-up: a drop-down with its items (codes from tags)', ws['customerTerms']['props']['options'] == [{'code': '30', 'title': 'Net 30'}, {'code': '60', 'title': 'Net 60'}]
          and ws['customerTerms']['props']['label'] == 'Terms')
    check('radio buttons in their own view: one radio group', ws['tag40']['kind'] == 'radio' and [o['title'] for o in ws['tag40']['props']['options']] == ['Retail', 'Wholesale']
          and ws['tag40']['props']['label'] == 'Kind')
    box = ws['notesBox']
    check('a box with inputs: a form, its title a heading', box['props']['layout'] == 'form' and box['children'][0]['props']['text'] == 'Notes')
    check('a label above an input becomes its label', ws['remarks']['props']['label'] == 'Remarks' and ws['remarks']['kind'] == 'textarea')
    check('buttons in a row on the right: a toolbar at the end, Return = primary', tree[-1]['props']['layout'] == 'toolbar-end'
          and [c['id'] for c in tree[-1]['children']] == ['cancel', 'save'] and ws['save']['props']['role'] == 'primary')
    check('an empty label with an Identifier: a message band', ws['customerMessage']['kind'] == 'message' and ws['customerMessage']['props'] == {'text': '', 'role': 'info'})
    check('an image-only button has no web widget', 'info' not in ws)
    check('no label is left over as text', not any(w['kind'] == 'text' for w in flat(tree)))
    check('the order follows the page, top to bottom', kinds == ['heading', 'field', 'container', 'checkbox', 'select', 'radio', 'container', 'message', 'container'])

    # the repository's own XIBs: every one lays out, ids are unique
    xibs = []
    for d in ('src/AppBuilder', 'src/WebToolkitExample'):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            xibs += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.endswith(('.xib', '.webxib'))]
    ok, bad = 0, []
    for x in xibs:
        try:
            t = tree_from_xib(open(x, encoding='utf-8').read())
            ids = [w['id'] for w in flat(t)]
            if len(ids) != len(set(ids)):
                bad.append(os.path.basename(x) + ' (duplicate ids)')
            else:
                ok += 1
        except Exception as e:  # noqa: BLE001
            bad.append(f'{os.path.basename(x)} ({e})')
    check(f'the repository\'s XIBs lay out with unique ids ({ok} of {len(xibs)})', not bad)
    for b in bad:
        print('      ' + b)
    print('web layout: ' + ('all passed' if not failures else f'{len(failures)} failed'))
    return not failures


if __name__ == '__main__':
    if '--tree' in sys.argv:
        path = sys.argv[sys.argv.index('--tree') + 1]
        print(json.dumps(tree_from_xib(open(path, encoding='utf-8').read()), indent=1))
        sys.exit(0)
    sys.exit(0 if run_tests() else 1)
