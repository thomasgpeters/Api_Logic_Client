#!/usr/bin/env python3
"""
make_architecture_svg - draws docs/design/architecture.svg (light and dark mode).

    python3 tools/make_architecture_svg.py

Edit the boxes and arrows here and run it again; the SVG is never edited by hand.
"""
import os
import sys

if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
    print(__doc__)
    sys.exit(0)
import html
W, H = 1560, 960
out = []
def t(x, y, s, cls='txt', anchor='start'):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{html.escape(s)}</text>')
def box(x, y, w, h, cls='box', r=10):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>')
def card(x, y, w, h, title, lines, cls='box', tcls='h3'):
    box(x, y, w, h, cls)
    t(x + 14, y + 24, title, tcls)
    for i, l in enumerate(lines):
        t(x + 14, y + 46 + i * 18, l, 'small')
def arrow(points, cls='arr', label=None, lx=None, ly=None, both=False):
    d = 'M ' + ' L '.join(f'{x} {y}' for x, y in points)
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#head)"' + (' marker-start="url(#tail)"' if both else '') + '/>')
    if label:
        t(lx, ly, label, 'lbl', 'middle')

# --- title
t(30, 44, 'App Builder for FutureBasic — architecture', 'h1')
t(30, 70, 'From a data model to a native Mac app with business rules: SQLite (lite edition) or API Logic Server → XIB parts, binding code, rules → a FutureBasic project built from the template and runtime.', 'sub')

# --- columns: headers
cols = [(30, 'Sources'), (300, 'The generator (FB, macOS)'), (850, 'Workspace: <project>/'), (1150, 'Generated app: FBapp/')]
for x, name in cols:
    t(x, 112, name.upper(), 'col')

# --- sources
card(30, 130, 230, 96, 'SQLite database', ['the lite edition’s catalyst:', 'tables, keys, relationships', 'read straight from the file'], 'src')
card(30, 250, 230, 118, 'API Logic Server project', ['/metadata?include=attributes', 'logic/declare_logic.py', '(LogicBank rules, Python)', 'JSON:API for the ALS edition'], 'src')
card(30, 392, 230, 78, 'The designer', ['Titles, widths, controls,', 'rules, About text, …'], 'person')

# --- generator panel
box(300, 124, 520, 640, 'panel', 14)
gen = [
    (138, 'Read the model', ['SQLite Model.incl  ·  API Interface.incl (ALS /metadata)']),
    (214, 'Entity definitions', ['Type Mapping.incl: FB type, size, control, Title, widths', 'designer’s adjustments → Design.json']),
    (310, None, None),
    (420, 'Rules page', ['Rules.json: formula · constraint · sum · count · copy ·', 'parent check · delete action · row / commit event']),
    (530, 'App Generator.incl', ['the FB project: data.fbproj groups, <project>.main,', 'Model.json, Credits.rtf; runtime + templates copied']),
]
for y, title, lines in gen:
    if title:
        card(316, y, 488, 82 if len(lines) > 1 else 62, title, lines, 'mod')
card(316, 310, 238, 92, 'XIB Generator.incl', ['<Entity>Form.xib', '<Entity>List.xib', 'Model Tags.incl'], 'mod')
card(566, 310, 238, 92, 'Binding Generator.incl', ['<Entity> Binding.incl', 'record ↔ Form', 'records → List'], 'mod')
card(566, 640, 238, 108, 'tools/rules_bridge.py', ['import / export declare_logic.py', 'check (names, cycles)', 'generate Studio Rules.incl', '(python3, run by the generator)'], 'tool')
card(316, 640, 238, 108, 'Bundled with the generator', ['src/Templates/  starting files', 'src/Runtime/  FB runtime', 'Branding.incl  name + logo', '(never written to)'], 'res')
# arrows inside generator
arrow([(560, 200), (560, 214)])
arrow([(435, 296), (435, 310)])
arrow([(685, 296), (685, 310)])
arrow([(560, 402), (560, 420)])
arrow([(560, 502), (560, 530)])
arrow([(804, 470), (812, 470), (812, 694), (804, 694)], 'arr2', both=True)
arrow([(435, 640), (435, 612)])

# sources → generator
arrow([(260, 168), (316, 168)])
arrow([(260, 290), (290, 290), (290, 175), (316, 175)])
arrow([(260, 340), (282, 340), (282, 774), (685, 774), (685, 748)], 'arr2', both=True, label='declare_logic.py: import / export', lx=470, ly=768)
arrow([(260, 430), (296, 430), (296, 250), (316, 250)])

# --- workspace panel
box(850, 124, 270, 640, 'panel', 14)
ws = [
    (140, 'Project.json', ['name, model source, base URL,', 'user name, About text']),
    (222, 'Design.json', ['the designer’s adjustments']),
    (286, 'Rules.json', ['the rules — source of truth', 'for the Rules page']),
    (368, 'Database/<db>.sqlite', ['the project’s own copy', '(+ -wal / -shm); backups:', 'one folder']),
    (466, 'FBapp/', ['the generated FutureBasic', 'project (next column)']),
]
for y, title, lines in ws:
    card(866, y, 238, 30 + 18 * len(lines) + 8, title, lines, 'file')
t(866, 600, 'Recent Projects.json lives in', 'small')
t(866, 618, '~/Library/Application Support/', 'small')
t(866, 636, 'Api_Logic_Client/', 'small')
# generator → workspace
arrow([(804, 236), (866, 175)], label='saves', lx=838, ly=196)
arrow([(804, 250), (866, 245)])
arrow([(804, 455), (866, 320)])
arrow([(260, 150), (272, 150), (272, 92), (838, 92), (838, 400), (866, 400)], 'arr3', label='the database is copied into the project', lx=640, ly=86)
arrow([(804, 570), (866, 500)])

# --- generated app panel
box(1150, 124, 380, 640, 'panel', 14)
t(1166, 150, 'FBapp/<project>.fbeproj — data.fbproj groups', 'h3')
groups = [
    ('Runtime', 'runtime', ['Data SQLite · DataObject query builder (author’s)', 'Data Model · Data Records', 'Logic Rules · Logic Row · Logic Engine', 'ALS Client · ALS Binding · ALS App · Binding Support']),
    ('Model · Bindings · Resources', 'gen', ['Model Tags.incl · <Entity> Binding.incl', 'Model.json · <Entity>Form/List.xib · Credits.rtf']),
    ('Rules', 'gen', ['Studio Rules.incl (generated: DeclareStudioRules)', 'Rules.incl (yours: DeclareRules, never overwritten)']),
    ('Controller · View · Main', 'tmpl', ['EventHandlers.incl · Menus.incl · Windows.incl', '<project>.main: DataOpen → rules → windows']),
]
y = 164
for title, cls, lines in groups:
    h = 30 + 18 * len(lines) + 6
    card(1166, y, 348, h, title, lines, cls)
    y += h + 10
# legend in app panel
lx, ly = 1166, y + 6
for cls, name in [('runtime', 'copied from src/Runtime (regenerated)'), ('gen', 'generated from the model / Rules.json'), ('tmpl', 'starting templates: created once, yours')]:
    box(lx, ly, 14, 14, cls, 3)
    t(lx + 22, ly + 12, name, 'small')
    ly += 22
# generator → app
arrow([(804, 590), (826, 590), (826, 778), (1136, 778), (1136, 300), (1166, 300)], 'arr', label='writes the parts, bindings, project and main', lx=980, ly=772)
arrow([(1104, 490), (1166, 490)])

# --- build & run (bottom right)
card(1150, 790, 380, 62, 'FutureBasic builds it', ['FBtoC → clang, links -lsqlite3 → <project>.app'], 'build')
card(1150, 868, 380, 78, 'The Mac app', ['XIB windows over the project’s SQLite copy;', 'every save: LogicInsert / LogicUpdate / LogicDelete'], 'app')
arrow([(1340, 764), (1340, 790)])
arrow([(1340, 852), (1340, 868)])
arrow([(1104, 410), (1128, 410), (1128, 905), (1150, 905)], 'arr3')

# --- rules flow strip (bottom left)
box(30, 790, 1090, 156, 'panel', 14)
t(46, 816, 'Rules, end to end', 'h3')
steps = [
    ('declare_logic.py', 'LogicBank (Python)'), ('rules_bridge import', 'lambdas → FB'),
    ('Rules.json', 'edited on the Rules page'), ('rules_bridge generate', 'Studio Rules.incl'),
    ('LogicActivate', 'names, order, cycles'), ('every save', 'formulas · sums · checks'),
]
x = 46
for i, (a, b) in enumerate(steps):
    box(x, 832, 160, 58, 'step', 8)
    t(x + 80, 855, a, 'h4', 'middle')
    t(x + 80, 874, b, 'tiny', 'middle')
    if i < len(steps) - 1:
        arrow([(x + 160, 861), (x + 178, 861)])
    x += 178
t(46, 920, 'Tests (tools/run_tests.sh): fblint · logic_reference (70 scenarios; --prove: every rule needed) · rules_bridge (23) · make_logic_test (the same 70 in FB, on a Mac) · ibtool (XIBs, on a Mac)', 'small')

style = '''
<style>
  :root { --bg:#ffffff; --fg:#1d2430; --muted:#5a6473; --panel:#f4f6f9; --line:#c9d1dc; --accent:#2f5d8a;
          --src:#e8f1fb; --mod:#ffffff; --tool:#eef7ef; --res:#f6f1e7; --file:#ffffff; --runtime:#e9eef7; --gen:#eaf6f0; --tmpl:#fbf1e6; --build:#eef0f3; --app:#e7f0fa; --person:#f7eef6; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#16191d; --fg:#e6e9ee; --muted:#9aa3ae; --panel:#1e2329; --line:#3a434e; --accent:#8db6dd;
            --src:#1d2b3a; --mod:#232a32; --tool:#1f2e24; --res:#2d281f; --file:#232a32; --runtime:#222b3a; --gen:#1f2f28; --tmpl:#33291f; --build:#262b31; --app:#1d2a38; --person:#2f2330; }
  }
  .bg { fill: var(--bg); }
  text { font-family: -apple-system, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif; fill: var(--fg); }
  .h1 { font-size: 24px; font-weight: 600; }
  .sub { font-size: 13px; fill: var(--muted); }
  .col { font-size: 12px; font-weight: 600; letter-spacing: .08em; fill: var(--accent); }
  .h3 { font-size: 14px; font-weight: 600; }
  .h4 { font-size: 12.5px; font-weight: 600; }
  .small { font-size: 11.5px; fill: var(--muted); }
  .tiny { font-size: 10.5px; fill: var(--muted); }
  .lbl { font-size: 10.5px; fill: var(--accent); }
  rect { stroke: var(--line); stroke-width: 1; }
  .panel { fill: var(--panel); }
  .box, .mod, .file { fill: var(--mod); }
  .src { fill: var(--src); } .tool { fill: var(--tool); } .res { fill: var(--res); } .person { fill: var(--person); }
  .runtime { fill: var(--runtime); } .gen { fill: var(--gen); } .tmpl { fill: var(--tmpl); }
  .build { fill: var(--build); } .app { fill: var(--app); stroke: var(--accent); stroke-width: 1.5; }
  .step { fill: var(--mod); }
  .arr, .arr2, .arr3 { fill: none; stroke: var(--accent); stroke-width: 1.4; }
  .arr2 { stroke-dasharray: 5 3; }
  .arr3 { stroke: var(--muted); stroke-dasharray: 2 3; }
  .head { fill: var(--accent); }
</style>
<defs>
  <marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" class="head"/></marker>
  <marker id="tail" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" class="head"/></marker>
</defs>'''
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="App Builder for FutureBasic architecture">\n<title>App Builder for FutureBasic — architecture</title>'
       + style + f'\n<rect class="bg" x="0" y="0" width="{W}" height="{H}" style="stroke:none"/>\n' + '\n'.join(out) + '\n</svg>\n')
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'design', 'architecture.svg'), 'w').write(svg)
