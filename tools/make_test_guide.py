#!/usr/bin/env python3
"""make_test_guide.py - docs/TEST_SCENARIOS.pdf, the test scenario guide, from docs/TEST_SCENARIOS.md.

    python3 tools/make_test_guide.py [out.pdf]

The Markdown is the source: areas (##), scenarios (### ID Title), Purpose: and Before: lines, numbered steps written
"action -> expected". The PDF adds a cover, a tester's record, a results summary and, for each scenario, a table of
its steps with a Pass / Fail column. Needs reportlab (pip install reportlab).
"""
import datetime
import os
import re
import subprocess
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'docs', 'TEST_SCENARIOS.md')
LOGO = os.path.join(ROOT, 'src', 'Shared', 'imagery_logo.png')

NAVY = colors.Color(0.067, 0.157, 0.329)
ACCENT = colors.Color(0.04, 0.39, 0.79)
SOFT = colors.Color(0.37, 0.39, 0.41)
LINE = colors.Color(0.82, 0.83, 0.86)
BAND = colors.Color(0.93, 0.95, 0.98)
ZEBRA = colors.Color(0.975, 0.978, 0.985)

BASE = ParagraphStyle('base', fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.black, alignment=TA_LEFT)
BODY = ParagraphStyle('body', parent=BASE, fontSize=10.5, leading=15, spaceAfter=7)
SMALL = ParagraphStyle('small', parent=BASE, fontSize=8.5, leading=11, textColor=SOFT)
CELL = ParagraphStyle('cell', parent=BASE)
CELLHEAD = ParagraphStyle('cellhead', parent=BASE, fontName='Helvetica-Bold', textColor=colors.white, fontSize=9)
AREA = ParagraphStyle('area', parent=BASE, fontName='Helvetica-Bold', fontSize=17, leading=22, textColor=NAVY, spaceBefore=4, spaceAfter=10)
SECTION = ParagraphStyle('section', parent=AREA, fontSize=15)
SCEN = ParagraphStyle('scen', parent=BASE, fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=NAVY)
LABEL = ParagraphStyle('label', parent=BASE, fontSize=9.5, leading=13)


def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rich(text):
    """file names and commands in a monospaced face: a whole command (python3, nginx, tools/...), else file names"""
    m = re.search(r'(python3 |nginx -c |tools/run_tests\.sh|brew install )', text)
    if m:
        cmd = text[m.start():].rstrip()
        tail = ''
        if cmd.endswith(')') and '(' not in cmd:
            cmd, tail = cmd[:-1], ')'
        return rich(text[:m.start()]) + '<font face="Courier" size="8.5">' + esc(cmd) + '</font>' + esc(tail)
    t = esc(text)
    t = re.sub(r'((?:[\w.\-]+/)+[\w.\- ]*?\.(?:fbeproj|fb|incl|html|json|sqlite|records|index|webxib|md|py|sh|zip)|'
               r'[\w\-]+\.(?:fbeproj|fbproj|incl|html|json|sqlite|records|index|webxib|md|zip|plist)|'
               r'tools/[\w_]+\.(?:py|sh)[^.;]*?(?=$|\s->|;|\.\s))',
               r'<font face="Courier" size="8.5">\1</font>', t)
    return t


class CheckBox(Flowable):
    """an empty square to tick by hand"""
    def __init__(self, size=9):
        super().__init__()
        self.size = size
        self.width = self.height = size

    def draw(self):
        self.canv.setStrokeColor(SOFT)
        self.canv.setLineWidth(0.7)
        self.canv.rect(0, 0, self.size, self.size)


def boxes(*labels):
    """a row of check boxes with their labels: [] Pass  [] Fail"""
    cells = []
    for label in labels:
        cells += [CheckBox(), Paragraph(label, SMALL)]
    t = Table([cells], colWidths=[11, None] * len(labels))
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                           ('RIGHTPADDING', (0, 0), (-1, -1), 4), ('TOPPADDING', (0, 0), (-1, -1), 0),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
    return t


def parse(path):
    text = open(path, encoding='utf-8').read()
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    title, subtitle, intro, areas = '', '', [], []
    area = scen = None
    for raw in text.split('\n'):
        line = raw.rstrip()
        if line.startswith('# '):
            title = line[2:]
        elif line.startswith('## '):
            area = {'title': line[3:], 'scenarios': [], 'text': []}
            areas.append(area)
            scen = None
        elif line.startswith('### '):
            sid, name = line[4:].split(' ', 1)
            scen = {'id': sid, 'title': name, 'purpose': '', 'before': '', 'steps': []}
            area['scenarios'].append(scen)
        elif scen is not None and line.startswith('Purpose:'):
            scen['purpose'] = line[8:].strip()
        elif scen is not None and line.startswith('Before:'):
            scen['before'] = line[7:].strip()
        elif scen is not None and re.match(r'\d+\. ', line):
            body = line.split('. ', 1)[1]
            action, _, expected = body.partition(' -> ')
            scen['steps'].append((action.strip(), expected.strip()))
        elif line and area is None and not subtitle:
            subtitle = line
        elif line and area is not None and scen is None:
            area['text'].append(line)
    return title, subtitle, areas


def version():
    try:
        commit = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    except OSError:
        commit = ''
    return datetime.date.today().strftime('%B %-d, %Y'), commit


def build(out):
    title, subtitle, areas = parse(SOURCE)
    today, commit = version()
    scenario_areas = [a for a in areas if a['scenarios']]
    note_areas = [a for a in areas if not a['scenarios']]
    width = letter[0] - 1.5 * inch

    def page_decor(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.6)
        canvas.line(0.75 * inch, letter[1] - 0.6 * inch, letter[0] - 0.75 * inch, letter[1] - 0.6 * inch)
        canvas.setFont('Helvetica-Bold', 8.5)
        canvas.setFillColor(NAVY)
        canvas.drawString(0.75 * inch, letter[1] - 0.5 * inch, title)
        canvas.setFont('Helvetica', 8.5)
        canvas.setFillColor(SOFT)
        canvas.drawRightString(letter[0] - 0.75 * inch, letter[1] - 0.5 * inch, 'App Builder for FutureBasic')
        canvas.line(0.75 * inch, 0.6 * inch, letter[0] - 0.75 * inch, 0.6 * inch)
        canvas.drawString(0.75 * inch, 0.42 * inch, '© 2026 Imagery Business Systems, LLC')
        canvas.drawRightString(letter[0] - 0.75 * inch, 0.42 * inch, f'Page {doc.page}')
        canvas.restoreState()

    def cover_decor(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, letter[1] - 2.6 * inch, letter[0], 2.6 * inch, stroke=0, fill=1)
        canvas.setFillColor(ACCENT)
        canvas.rect(0, letter[1] - 2.68 * inch, letter[0], 0.08 * inch, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 30)
        canvas.drawString(0.75 * inch, letter[1] - 1.45 * inch, title)
        canvas.setFont('Helvetica', 13)
        canvas.drawString(0.75 * inch, letter[1] - 1.9 * inch, subtitle)
        canvas.restoreState()

    doc = BaseDocTemplate(out, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                          topMargin=0.85 * inch, bottomMargin=0.85 * inch, title=title,
                          author='Imagery Business Systems, LLC', subject=subtitle)
    frame = Frame(0.75 * inch, 0.85 * inch, width, letter[1] - 1.7 * inch, id='f')
    cover_frame = Frame(0.75 * inch, 0.85 * inch, width, letter[1] - 3.6 * inch, id='c')
    doc.addPageTemplates([PageTemplate('cover', [cover_frame], onPage=cover_decor),
                          PageTemplate('page', [frame], onPage=page_decor)])

    story = []
    # cover: the logo, what the guide covers, its version, the tester's record
    if os.path.exists(LOGO):
        img = Image(LOGO)
        scale = 1.6 * inch / img.imageWidth
        img.drawWidth, img.drawHeight = img.imageWidth * scale, img.imageHeight * scale
        img.hAlign = 'LEFT'
        story += [img, Spacer(1, 18)]
    count = sum(len(a['scenarios']) for a in scenario_areas)
    steps = sum(len(s['steps']) for a in scenario_areas for s in a['scenarios'])
    story.append(Paragraph(f'{count} scenarios, {steps} steps, in {len(scenario_areas)} areas: '
                           + ', '.join(esc(a['title'].split('. ', 1)[-1]) for a in scenario_areas) + '.', BODY))
    story.append(Paragraph(f'Version of {today}' + (f', from build <font face="Courier">{commit}</font>' if commit else '') + '.', SMALL))
    story.append(Spacer(1, 26))
    story.append(Paragraph('Tester\'s record', SCEN))
    story.append(Spacer(1, 6))
    rec = [[Paragraph(label, LABEL), ''] for label in ('Tester', 'Date', 'Mac model', 'macOS version', 'FutureBasic version',
                                                        'Repository build (commit)', 'Overall result')]
    t = Table(rec, colWidths=[1.9 * inch, width - 1.9 * inch], rowHeights=24)
    t.setStyle(TableStyle([('LINEBELOW', (1, 0), (1, -1), 0.6, LINE), ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                           ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
    story.append(t)
    story.append(NextPageTemplate('page'))
    story.append(PageBreak())

    # the notes before the scenarios
    for a in note_areas:
        story.append(Paragraph(esc(a['title']), SECTION))
        for p in a['text']:
            story.append(Paragraph(rich(p), BODY))
    # the summary
    story.append(Spacer(1, 8))
    story.append(Paragraph('Results summary', SECTION))
    rows = [[Paragraph('ID', CELLHEAD), Paragraph('Scenario', CELLHEAD), Paragraph('Result', CELLHEAD)]]
    for a in scenario_areas:
        rows.append([Paragraph('<b>' + esc(a['title']) + '</b>', CELL), '', ''])
        for s in a['scenarios']:
            rows.append([Paragraph(s['id'], CELL), Paragraph(esc(s['title']), CELL), boxes('Pass', 'Fail', 'Blocked')])
    t = Table(rows, colWidths=[0.65 * inch, width - 0.65 * inch - 2.35 * inch, 2.35 * inch], repeatRows=1)
    style = [('BACKGROUND', (0, 0), (-1, 0), NAVY), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LINEBELOW', (0, 1), (-1, -1), 0.4, LINE), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]
    for i, r in enumerate(rows):
        if i and r[1] == '':
            style += [('SPAN', (0, i), (-1, i)), ('BACKGROUND', (0, i), (-1, i), BAND)]
    t.setStyle(TableStyle(style))
    story.append(t)

    # the scenarios
    for a in scenario_areas:
        story.append(PageBreak())
        story.append(Paragraph(esc(a['title']), AREA))
        for s in a['scenarios']:
            head = Table([[Paragraph(f'{s["id"]}&nbsp;&nbsp;{esc(s["title"])}', SCEN)]], colWidths=[width])
            head.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BAND), ('LINEBEFORE', (0, 0), (0, -1), 3, ACCENT),
                                      ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
            parts = [head, Spacer(1, 6), Paragraph(f'<b>Checks:</b> {rich(s["purpose"])}', LABEL)]
            if s['before']:
                parts.append(Paragraph(f'<b>Have ready:</b> {rich(s["before"])}', LABEL))
            parts.append(Spacer(1, 6))
            rows = [[Paragraph('#', CELLHEAD), Paragraph('Do this', CELLHEAD), Paragraph('You should see', CELLHEAD), Paragraph('Result', CELLHEAD)]]
            for n, (action, expected) in enumerate(s['steps'], 1):
                rows.append([Paragraph(str(n), CELL), Paragraph(rich(action), CELL), Paragraph(rich(expected), CELL), boxes('Pass', 'Fail')])
            cw = [0.3 * inch, 2.45 * inch, width - 0.3 * inch - 2.45 * inch - 1.25 * inch, 1.25 * inch]
            t = Table(rows, colWidths=cw, repeatRows=1)
            style = [('BACKGROUND', (0, 0), (-1, 0), NAVY), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('VALIGN', (3, 1), (3, -1), 'MIDDLE'),
                     ('GRID', (0, 0), (-1, -1), 0.4, LINE), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]
            for i in range(2, len(rows), 2):
                style.append(('BACKGROUND', (0, i), (-1, i), ZEBRA))
            t.setStyle(TableStyle(style))
            parts += [t, Spacer(1, 4), Paragraph('Notes: ' + '_' * 96, SMALL), Spacer(1, 16)]
            story.append(KeepTogether(parts))
    doc.build(story)
    return count, steps


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs', 'TEST_SCENARIOS.pdf')
    n, s = build(out)
    print(f'{out}: {n} scenarios, {s} steps')
