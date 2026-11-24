#!/usr/bin/env python3
"""
check_erd_page - test only: the model diagram page (src/Templates/ERD/Model ERD.html).

    check_erd_page.py <Northwind db.sqlite> [--keep <folder>]
    check_erd_page.py --help

The generator (ERD Generator.incl, FutureBasic) fills the page with the project's model and
Rules.json and opens it. FB does not run here, so this check does the same filling - the model
from tools/sqlite_model.py (the reference of SQLite Model.incl), the rules from importing
Northwind's declare_logic.py - then loads the page in headless Chromium (Playwright, when
installed; otherwise only the static checks run) and checks that every entity and relationship
is drawn, the rule symbols are there, an entity opens and closes, drags, and selects, and the
page reports no script errors. --keep writes the filled page into a folder to look at.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules_bridge   # noqa: E402
import sqlite_model   # noqa: E402

TEMPLATE = os.path.join(HERE, '..', 'src', 'Templates', 'ERD', 'Model ERD.html')
MARKER = '/*__ERD_DATA__*/null'      # ERD_DATA_MARKER in ERD Generator.incl

BROWSER_CHECK = r"""
const { chromium } = require('playwright');
(async () => {
  const out = { errors: [] };
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  p.on('pageerror', e => out.errors.push(e.message));
  p.on('console', m => { if (m.type() === 'error') out.errors.push(m.text()); });
  await p.goto('file://' + process.argv[2]);
  out.entities = await p.locator('g.entity').count();
  out.edges = await p.locator('g.edge').count();
  out.symbols = await p.locator('g.rule').count();
  out.offSymbols = await p.locator('g.rule.off').count();
  const rows = () => p.locator('g.entity[data-name="Order"] text.attr').count();
  out.orderRows = await rows();
  await p.locator('text.toggle[data-toggle="Order"]').dispatchEvent('pointerdown');
  out.orderRowsClosed = await rows();
  const head = p.locator('g.entity[data-name="Customer"] .head');
  const before = await head.boundingBox();
  await p.mouse.move(before.x + 20, before.y + 5); await p.mouse.down();
  await p.mouse.move(before.x + 20, before.y + 125, { steps: 4 }); await p.mouse.up();
  const after = await p.locator('g.entity[data-name="Customer"] .head').boundingBox();
  out.dragged = Math.round(after.y - before.y);
  const h = await p.locator('g.entity[data-name="OrderDetail"] .head').boundingBox();
  await p.mouse.click(h.x + 10, h.y + 5);
  out.side = await p.locator('#side h2').textContent();
  out.dimmed = await p.locator('g.entity.dim').count();
  console.log(JSON.stringify(out)); await b.close();
})();
"""


def fill(db, rules_path):
    with open(TEMPLATE) as f:
        page = f.read()
    with open(rules_path) as f:
        rules = json.load(f)['rules']
    data = {'title': 'Northwind', 'resources': sqlite_model.read_model(db), 'rules': rules}
    return page.replace(MARKER, json.dumps(data).replace('</', '<\\/')), data


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    db, failures = argv[0], 0

    def check(ok, text):
        nonlocal failures
        print(('PASS  ' if ok else 'FAIL  ') + text)
        failures += 0 if ok else 1
    with tempfile.TemporaryDirectory() as tmp:
        logic, rules = os.path.join(tmp, 'declare_logic.py'), os.path.join(tmp, 'Rules.json')
        with open(logic, 'w') as f:
            f.write(rules_bridge.NORTHWIND_LOGIC)
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):     # the import's own report
            rules_bridge.main(['import', logic, '--model', db, '--rules', rules])
        with open(TEMPLATE) as f:
            template = f.read()
        check(template.count(MARKER) == 1, 'the template has one data marker (ERD_DATA_MARKER)')
        check('https://' not in template and 'http://' not in template.replace('http://www.w3.org/2000/svg', ''),
              'the page needs no network')
        page, data = fill(db, rules)
        path = os.path.join(tmp, 'Model ERD.html')
        with open(path, 'w') as f:
            f.write(page)
        if '--keep' in argv:
            shutil.copy(path, argv[argv.index('--keep') + 1])
        node = shutil.which('node')
        has_pw = node and subprocess.run([node, '-e', "require('playwright')"], capture_output=True).returncode == 0
        if not has_pw:
            print('SKIP  the page in a browser (no node + playwright here)')
        else:
            script = os.path.join(tmp, 'check.js')
            with open(script, 'w') as f:
                f.write(BROWSER_CHECK)
            run = subprocess.run([node, script, path], capture_output=True, text=True)
            out = json.loads(run.stdout.strip().splitlines()[-1]) if run.returncode == 0 else {'errors': [run.stderr[-400:]]}
            toone = sum(1 for r in data['resources'].values() for x in r['relationships'] if x['direction'] == 'toone')
            check(not out['errors'], f'no script errors {out["errors"] or ""}')
            check(out.get('entities') == len(data['resources']), f'every entity drawn ({out.get("entities")})')
            check(out.get('edges') == toone, f'every relationship drawn ({out.get("edges")} of {toone})')
            check(out.get('symbols', 0) >= len(data['rules']), f'rule symbols drawn ({out.get("symbols")})')
            check(out.get('offSymbols', 0) >= 1, 'a switched-off rule is drawn faded')
            check(out.get('orderRows', 0) > 0 and out.get('orderRowsClosed') == 0, 'an entity closes (attributes hidden)')
            check(out.get('dragged', 0) > 20, f'an entity drags ({out.get("dragged")} px)')
            check(out.get('side') == 'OrderDetail' and out.get('dimmed', 0) > 0, 'a click selects an entity: side panel, others dimmed')
    print(f'check_erd_page: {failures} failed')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
