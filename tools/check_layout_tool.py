#!/usr/bin/env python3
"""check_layout_tool.py - test: the Web Toolkit's layout tool (src/WebToolkit/Layout Tool/Layout Tool.html).

In headless Chromium (node + Playwright; skipped without them):
  - its web preview follows the layout rules exactly: the same widget tree as tools/web_layout_reference.py for the
    reference's test layout and every XIB in the repository
  - a layout made in it (palette, Identifier, a move by dragging, undo) saves as a XIB that the reference reads back
    as the widgets that were laid out; an opened XIB keeps what the tool does not edit
  - the preview shows the page with web.css; the FB code loads the layout and connects its buttons

    python3 tools/check_layout_tool.py [--screenshot out.png]
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import web_layout_reference as ref  # noqa: E402
from check_web_layout import normal, first_difference  # noqa: E402

TOOL = os.path.join(ROOT, 'src', 'WebToolkit', 'Layout Tool', 'Layout Tool.html')

SCRIPT = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const [tool, inputPath, outputPath, shot] = process.argv.slice(2);
const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
(async () => {
  const out = { trees: [], errors: [] };
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 820 }, deviceScaleFactor: shot ? 2 : 1, acceptDownloads: true });
  page.on('pageerror', (e) => out.errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') out.errors.push(m.text()); });
  await page.goto('file://' + tool);
  for (const xml of input.xibs) out.trees.push(await page.evaluate((x) => window.fbLayoutTree(x), xml));

  // make a layout: a label and a field side by side, a button; Identifiers; a drag; undo
  await page.click('#newBtn');
  await page.click('#palette button[data-kind="label"]');
  await page.click('#palette button[data-kind="field"]');
  await page.fill('#insIdent', 'customerName'); await page.press('#insIdent', 'Enter');
  const field = await page.$('.ctl.sel');
  const fb = await field.boundingBox();
  // put the field just right of the label (the label is at x 20, 100 wide; same top)
  const label = await page.$('.ctl.k-text');
  const lb = await label.boundingBox();
  await page.mouse.move(fb.x + 20, fb.y + 8); await page.mouse.down();
  await page.mouse.move(lb.x + lb.width + 8 + 20, lb.y - 2 + 8, { steps: 6 }); await page.mouse.up();
  out.movedFrame = await page.evaluate(() => { const d = new DOMParser().parseFromString(window.fbLayoutText(), 'application/xml'); const f = d.querySelector('[identifier="customerName"] > rect'); return [f.getAttribute('x'), f.getAttribute('y')]; });
  await page.click('#palette button[data-kind="button"]');
  await page.fill('#insIdent', 'save'); await page.press('#insIdent', 'Enter');
  await page.click('#palette button[data-kind="checkbox"]');
  const before = await page.$$eval('.ctl', (els) => els.length);
  await page.click('#undoBtn');
  out.undo = [before, await page.$$eval('.ctl', (els) => els.length)];
  out.made = await page.evaluate(() => window.fbLayoutText());

  // save: a download
  const [download] = await Promise.all([page.waitForEvent('download'), page.click('#saveWebBtn')]);
  out.downloadName = download.suggestedFilename();
  out.downloaded = fs.readFileSync(await download.path(), 'utf8');

  // the preview, and the FB code
  await page.click('#webTab');
  const frame = page.frameLocator('#frame');
  await frame.locator('#fb-customerName').waitFor();
  out.preview = {
    label: await frame.locator('#fb-customerName label').textContent(),
    button: await frame.locator('#fb-save').textContent(),
    styled: await frame.locator('#fb-save').evaluate((b) => getComputedStyle(b).borderRadius),
  };
  await page.click('#designTab');
  await page.click('#codeBtn');
  out.code = await page.inputValue('#code');
  await page.click('#closeCode');

  // an opened XIB: drawn, and kept
  await page.evaluate(([x, n]) => window.fbLayoutOpen(x, n), [input.open, 'Opened.xib']);
  out.openedCount = await page.$$eval('.ctl', (els) => els.length);
  out.reopened = await page.evaluate(() => window.fbLayoutText());
  if (shot) {
    await page.evaluate(([x, n]) => window.fbLayoutOpen(x, n), [input.shotXib, 'CustomerPanel.webxib']);
    await page.click('.ctl.k-field');
    await page.screenshot({ path: shot });
    await page.click('#webTab');
    await page.frameLocator('#frame').locator('main').waitFor();
    await page.screenshot({ path: shot.replace(/\.png$/, '-web.png') });
  }
  fs.writeFileSync(outputPath, JSON.stringify(out));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
"""


def main():
    node = shutil.which('node')
    if not node or subprocess.run([node, '-e', "require('playwright')"], capture_output=True).returncode != 0:
        print('SKIP  the layout tool in a browser (no node + playwright here)')
        return 0
    shot = None
    if '--screenshot' in sys.argv:
        shot = os.path.abspath(sys.argv[sys.argv.index('--screenshot') + 1])
    xib_paths = sorted(glob.glob(os.path.join(ROOT, 'src', 'AppBuilder', '*.xib'))) + sorted(glob.glob(os.path.join(ROOT, 'src', 'WebToolkitExample', '*.webxib')))
    xibs = [ref.TEST_XIB] + [open(p, encoding='utf-8').read() for p in xib_paths]
    names = ['the reference test layout'] + [os.path.relpath(p, ROOT) for p in xib_paths]
    open_path = os.path.join(ROOT, 'src', 'AppBuilder', 'NewProjectView.xib')
    shot_paths = glob.glob(os.path.join(ROOT, 'src', 'WebToolkitExample', 'CustomerPanel.webxib'))
    failures = []

    def check(name, ok, detail=''):
        print(('PASS  ' if ok else 'FAIL  ') + name + (f'\n      {detail}' if detail and not ok else ''))
        if not ok:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        inp, outp, script = (os.path.join(tmp, n) for n in ('in.json', 'out.json', 'run.js'))
        json.dump({'xibs': xibs, 'open': open(open_path, encoding='utf-8').read(),
                   'shotXib': open(shot_paths[0], encoding='utf-8').read() if shot_paths else ref.TEST_XIB}, open(inp, 'w'))
        open(script, 'w').write(SCRIPT)
        run = subprocess.run([node, script, TOOL, inp, outp] + ([shot] if shot else []), capture_output=True, text=True, timeout=240)
        if run.returncode != 0:
            print('FAIL  the layout tool runs\n' + run.stderr[-2000:])
            return 1
        out = json.load(open(outp))

    for name, xml, got in zip(names, xibs, out['trees']):
        d = first_difference(normal(got), normal(ref.tree_from_xib(xml)))
        check(f'the web preview follows the layout rules: {name}', d is None, d or '')

    made = ref.tree_from_xib(out['made'])
    flat = {w['id']: w for w in ref.flat(made)}
    check('a field from the palette, with the Identifier typed in', 'customerName' in flat and flat['customerName']['kind'] == 'field')
    check('dragged beside the label, the label becomes its label', flat.get('customerName', {}).get('props', {}).get('label') == 'Label', json.dumps(made)[:400])
    check('a button with its Identifier', flat.get('save', {}).get('kind') == 'button')
    check('undo takes the last control away', out['undo'][1] == out['undo'][0] - 1, str(out['undo']))
    check('saved as .webxib: the file the web app reads', out['downloadName'] == 'Untitled.webxib' or out['downloadName'].endswith('.webxib'), out['downloadName'])
    check('the saved file is the layout made', normal(ref.tree_from_xib(out['downloaded'])) == normal(made))
    check('the preview: the field with its label, the button, web.css applied', out['preview']['label'] == 'Label' and out['preview']['button'] == 'Button'
          and out['preview']['styled'] not in ('', '0px'), json.dumps(out['preview']))
    check('the FB code loads the layout and connects the button', 'fn WebLoadLayout( session, @"page", @"Untitled" )' in out['code']
          and 'fn WebOn( session, @"save", @"clicked", @fn SaveClicked )' in out['code'], out['code'][:300])
    original = ref.tree_from_xib(open(open_path, encoding='utf-8').read())
    check('an opened XIB is drawn (NewProjectView: its controls)', out['openedCount'] >= 9, str(out['openedCount']))
    check('an opened XIB, saved untouched, lays out the same', normal(ref.tree_from_xib(out['reopened'])) == normal(original))
    check('no script errors', not out['errors'], '; '.join(out['errors'])[:500])
    if shot:
        print('screenshots: ' + shot + ', ' + shot.replace('.png', '-web.png'))
    print('layout tool: ' + ('all passed' if not failures else f'{len(failures)} failed'))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
