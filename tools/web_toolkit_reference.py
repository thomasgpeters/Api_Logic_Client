#!/usr/bin/env python3
"""web_toolkit_reference.py - the Web Toolkit for FutureBasic's protocol, in Python, to test web.js here.

FB cannot run here, so this is a reference of src/WebToolkit's server side - sessions (cookie + token), widgets,
the HTML Web Render.incl writes, events and the updates that answer them, the page's lifecycle and bound forms -
serving the real web.js and web.css. --test drives a page in headless Chromium (Playwright) and checks that:

  - events go out asynchronously (AJAX) and the answers change the page in place, without a reload
  - every field's value travels with each event; events arrive in the order the user made them
  - typed (after a pause), entered, changed, selected, submitted, and clicks on action links
  - added, redrawn and removed widgets; enabled / visible / checked / focus; the theme
  - text a user types is never HTML (escaped by the server, set as text by web.js)
  - the lifecycle: shown (first / again), hidden, visible, leaving; a dirty bound form guards the page; an
    auto-saving one is saved when the page is hidden; an ended session reloads
  - an event without the session's token is refused; the page needs no inline script (Content-Security-Policy)

    python3 tools/web_toolkit_reference.py --test
    python3 tools/web_toolkit_reference.py --serve 8099     # look at the page yourself
"""
import html
import http.server
import json
import os
import secrets
import sys
import threading
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'src', 'WebToolkit', 'Resources')


def esc(v):
    if v is None:
        return ''
    if isinstance(v, bool):
        v = int(v)
    if isinstance(v, float) and v == int(v):
        v = int(v)
    return html.escape(str(v), quote=True).replace('&#x27;', '&#39;')


class Session:
    def __init__(self, build):
        self.id = secrets.token_hex(16)
        self.token = secrets.token_hex(16)
        self.widgets = {'page': {'id': 'page', 'kind': 'page', 'props': {}, 'children': [], 'events': {}}}
        self.updates, self.rendered, self.data, self.log, self.theme = [], False, {}, [], ''
        build(self)

    # --- Web Widgets.incl ---
    def queue(self, u):
        if self.rendered:
            self.updates.append(u)

    def add(self, parent, wid, kind, **props):
        w = {'id': wid, 'kind': kind, 'parent': parent, 'props': props, 'children': [], 'events': {}}
        self.widgets[wid] = w
        self.widgets[parent]['children'].append(wid)
        self.queue({'op': 'append', 'id': wid, 'parent': parent})
        return wid

    def on(self, wid, event, fn):
        self.widgets[wid]['events'][event] = fn
        if wid != 'page':
            self.queue({'op': 'redraw', 'id': wid})

    def change(self, wid, prop, value):
        self.widgets[wid]['props'][prop] = value
        self.queue({'op': prop, 'id': wid, 'value': value})

    def set_property(self, wid, prop, value):
        self.widgets[wid]['props'][prop] = value
        self.queue({'op': 'redraw', 'id': wid})

    def remove(self, wid):
        w = self.widgets.pop(wid)
        self.widgets[w['parent']]['children'].remove(wid)
        for c in list(w['children']):
            self.widgets.pop(c, None)
        self.queue({'op': 'remove', 'id': wid})

    def value(self, wid):
        return str(self.widgets[wid]['props'].get('value', ''))

    def fire(self, wid, event, value):
        fn = self.widgets.get(wid, {}).get('events', {}).get(event)
        if fn:
            fn(self, wid, value)
            return True
        return False

    # --- Web Render.incl ---
    def common(self, w):
        a = f' data-fb-id="{esc(w["id"])}" id="fb-{esc(w["id"])}"'
        if w['events']:
            a += f' data-fb-events="{esc(" ".join(w["events"]))}"'
        p = w['props']
        if p.get('visible') is False:
            a += ' hidden'
        if 'entity' in p and w['kind'] == 'container':
            a += ' data-fb-bound'
            if p.get('dirty'):
                a += ' data-fb-dirty'
            if p.get('autosave'):
                a += ' data-fb-autosave'
        return a

    def render(self, wid):
        w = self.widgets.get(wid)
        if not w:
            return ''
        p, c, k = w['props'], self.common(w), w['kind']
        dis = ' disabled' if p.get('enabled') is False else ''
        label = (f'<label class="form-label" for="fb-in-{esc(wid)}">{esc(p["label"])}</label>' if p.get('label') else '')
        if k == 'container':
            tag = 'form' if p['layout'] == 'form' else 'div'
            inner = ''.join(self.render(ch) for ch in w['children'])
            return f'<{tag} class="fb-container fb-{p["layout"]}"{c}{" novalidate" if tag == "form" else ""}>{inner}</{tag}>'
        if k == 'heading':
            return f'<h{p["level"]} class="fb-heading"{c}>{esc(p["text"])}</h{p["level"]}>'
        if k == 'text':
            return f'<p class="fb-text fb-{p.get("look", "")}"{c}>{esc(p["text"])}</p>'
        if k == 'link':
            return f'<a href="{esc(p.get("href") or "#")}"{c}>{esc(p["text"])}</a>'
        if k == 'message':
            empty = '' if p.get('text') else ' fb-empty'
            return f'<div class="alert alert-{p["role"]}{empty}" role="status" aria-live="polite"{c}>{esc(p.get("text"))}</div>'
        if k == 'button':
            return f'<button type="button" class="btn btn-{p.get("role") or "secondary"}" data-fb-input{c}{dis}>{esc(p["text"])}</button>'
        if k == 'field':
            return (f'<div class="mb-3 fb-field"{c}>{label}<input class="form-control" type="{p["type"]}" id="fb-in-{esc(wid)}" '
                    f'data-fb-input value="{esc(p.get("value"))}" placeholder="{esc(p.get("placeholder"))}"{dis}></div>')
        if k == 'checkbox':
            on = ' checked' if p.get('checked') else ''
            return (f'<div class="form-check mb-3 fb-check"{c}><input class="form-check-input" type="checkbox" id="fb-in-{esc(wid)}" '
                    f'data-fb-input{on}{dis}><label class="form-check-label" for="fb-in-{esc(wid)}">{esc(p["label"])}</label></div>')
        if k == 'select':
            opts = ''.join(f'<option value="{esc(o["code"])}"{" selected" if str(o["code"]) == str(p.get("value", "")) else ""}>{esc(o["title"])}</option>' for o in p['options'])
            return f'<div class="mb-3 fb-field"{c}>{label}<select class="form-select" id="fb-in-{esc(wid)}" data-fb-input{dis}>{opts}</select></div>'
        if k == 'table':
            head = ''.join(f'<th scope="col">{esc(col)}</th>' for col in p['columns'])
            rows = ''.join(
                f'<tr data-fb-row="{i}" tabindex="0"{" class=\"table-active\" aria-selected=\"true\"" if i == p.get("selected", -1) else ""}>'
                + ''.join(f'<td>{esc(r.get(col))}</td>' for col in p['columns']) + '</tr>' for i, r in enumerate(p['rows']))
            return f'<div class="table-responsive fb-table"{c}><table class="table table-hover align-middle"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
        raise ValueError(k)

    def page(self):
        theme = f' data-fb-theme="{self.theme}"' if self.theme else ''
        body = ''.join(self.render(ch) for ch in self.widgets['page']['children'])
        self.rendered, self.updates = True, []
        return (f'<!doctype html><html lang="en"{theme}><head><meta charset="utf-8"><title>Reference</title>'
                f'<meta name="fb-token" content="{self.token}"><meta name="fb-base" content="/">'
                '<link rel="stylesheet" href="/fbweb/web.css"><script src="/fbweb/web.js" defer></script></head>'
                f'<body><main class="fb-page container" data-fb-id="page" id="fb-page">{body}</main><div class="fb-busy" aria-hidden="true"></div></body></html>')

    def take_updates(self):
        out = []
        for u in self.updates:
            u = dict(u)
            if u['op'] in ('append', 'redraw'):
                if u['id'] not in self.widgets:
                    continue
                u['html'] = self.render(u['id'])
            out.append(u)
        self.updates = []
        return out

    # --- Web Binding.incl (the dirty / auto-save part) ---
    def field_edited(self, wid):
        form = self.widgets[wid]['props'].get('form')
        if form and not self.widgets[form]['props'].get('dirty'):
            self.widgets[form]['props']['dirty'] = True
            self.queue({'op': 'dirty', 'id': form, 'value': True})

    def form_save(self, form):
        f = self.widgets[form]['props']
        saved = {self.widgets[w]['props']['attribute']: self.value(w) for w in f['fields']}
        STORE.setdefault(f['entity'], []).append(saved)
        f['dirty'] = False
        self.queue({'op': 'dirty', 'id': form, 'value': False})
        self.fire(form, 'saved', '')

    def save_dirty(self):
        for w in list(self.widgets.values()):
            if w['props'].get('autosave') and w['props'].get('dirty'):
                self.form_save(w['id'])

    # --- Web Events.incl ---
    def apply_values(self, values):
        for wid, v in values.items():
            w = self.widgets.get(wid)
            if not w:
                continue
            if w['kind'] == 'checkbox':
                if bool(w['props'].get('checked')) != bool(v):
                    w['props']['checked'] = bool(v)
                    self.field_edited(wid)
            elif str(w['props'].get('value', '')) != str(v):
                w['props']['value'] = str(v)
                self.field_edited(wid)

    def lifecycle(self, phase, detail):
        if phase in ('hidden', 'leaving', 'ended'):
            self.save_dirty()
        self.fire('page', phase, detail)


SESSIONS, STORE, EVENTS = {}, {}, []


def build_test_page(s):
    """The page the test drives: one of everything web.js must handle."""
    s.add('page', 'title', 'heading', text='Reference', level=1)
    s.add('page', 'count', 'text', text='0', look='')
    s.add('page', 'add', 'button', text='Add One', role='primary')
    s.add('page', 'nameField', 'field', label='Name', type='text', placeholder='', value='')
    s.add('page', 'greet', 'button', text='Greet', role='secondary')
    s.add('page', 'greeting', 'message', text='', role='info')
    s.add('page', 'echo', 'text', text='', look='muted')
    s.add('page', 'agree', 'checkbox', label='I agree', checked=False)
    s.add('page', 'colour', 'select', label='Colour', options=[{'code': '', 'title': 'None'}, {'code': 'r', 'title': 'Red'}, {'code': 'g', 'title': 'Green'}], value='')
    s.add('page', 'people', 'table', columns=['Name', 'Town'], rows=[{'Name': 'Alice', 'Town': 'Hamilton'}, {'Name': 'Bob', 'Town': "St. George's"}], selected=-1)
    s.add('page', 'more', 'link', text='Add a line', href='')
    s.add('page', 'lines', 'container', layout='column')
    s.add('page', 'itemForm', 'container', layout='form', entity='Item', fields=['product'], dirty=False, autosave=True)
    s.add('itemForm', 'product', 'field', label='Product', type='text', placeholder='', value='', attribute='Product', form='itemForm')
    s.add('page', 'noteForm', 'container', layout='form', entity='Note', fields=['note'], dirty=False, autosave=False)
    s.add('noteForm', 'note', 'field', label='Note', type='text', placeholder='', value='', attribute='Note', form='noteForm')
    s.add('page', 'theme', 'select', label='Theme', options=[{'code': '', 'title': 'System'}, {'code': 'dark', 'title': 'Dark'}], value='')

    def add(s, w, v):
        n = int(s.widgets['count']['props']['text']) + 1
        s.change('count', 'text', str(n))
        if n == 3:
            s.change('add', 'enabled', False)

    def greet(s, w, v):
        name = s.value('nameField')
        s.set_property('greeting', 'text', f'Hello, {name}' if name else 'Type a name first.')
        if not name:
            s.queue({'op': 'focus', 'id': 'nameField'})

    def record(s, w, v):
        EVENTS.append((w, v))
        s.change('echo', 'text', f'{w}:{v}')

    def more(s, w, v):
        n = len(s.widgets['lines']['children'])
        s.add('lines', f'line{n}', 'text', text=f'line {n}', look='')
        if n == 1:
            s.remove('line0')

    def theme(s, w, v):
        s.theme = v
        s.queue({'op': 'theme', 'id': 'page', 'value': v})

    s.on('add', 'clicked', add)
    s.on('greet', 'clicked', greet)
    s.on('nameField', 'entered', greet)
    s.on('nameField', 'typed', record)
    s.on('agree', 'changed', record)
    s.on('colour', 'changed', record)
    s.on('people', 'selected', record)
    s.on('more', 'clicked', more)
    s.on('theme', 'changed', theme)
    s.on('itemForm', 'saved', lambda s, w, v: EVENTS.append(('saved', s.widgets['product']['props']['value'])))
    for phase in ('shown', 'hidden', 'visible', 'leaving'):
        s.on('page', phase, lambda s, w, v, phase=phase: EVENTS.append(('page', phase, v)))


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, status, ctype, body, headers=()):
        data = body.encode()
        self.send_response(status)
        self.send_header('Content-Type', ctype + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'")
        for k, v in headers:
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def session(self):
        for part in (self.headers.get('Cookie') or '').split(';'):
            k, _, v = part.strip().partition('=')
            if k == 'fbweb' and v in SESSIONS:
                return SESSIONS[v]
        return None

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == '/__state':          # the test reads what the server saw
            return self.send(200, 'application/json', json.dumps({'events': EVENTS, 'store': STORE}))
        if path == '/__end_sessions':   # the test ends every session, as the idle timer would
            SESSIONS.clear()
            return self.send(200, 'application/json', '{}')
        if path == '/':
            s, headers, detail = self.session(), [], 'again'
            if not s:
                s = Session(build_test_page)
                SESSIONS[s.id] = s
                headers.append(('Set-Cookie', f'fbweb={s.id}; Path=/; HttpOnly; SameSite=Strict'))
                detail = 'first'
            s.lifecycle('shown', detail)
            return self.send(200, 'text/html', s.page(), headers)
        if path in ('/fbweb/web.js', '/fbweb/web.css'):
            name = os.path.basename(path)
            return self.send(200, 'text/javascript' if name.endswith('.js') else 'text/css', open(os.path.join(RES, name)).read())
        self.send(404, 'text/plain', 'not found')

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('Content-Length') or 0)).decode()
        if self.path != '/fbweb/event':
            return self.send(404, 'text/plain', 'not found')
        s = self.session()
        ev = json.loads(body or '{}')
        if not s or ev.get('token') != s.token:
            return self.send(200, 'application/json', json.dumps({'expired': True, 'updates': []}))
        s.apply_values(ev.get('values') or {})
        w, e, v = ev.get('widget', ''), ev.get('event', ''), ev.get('value', '')
        if w == 'page':
            if e != 'alive':
                s.lifecycle(e, v)
        else:
            if e == 'selected':
                s.widgets[w]['props']['selected'] = int(v)
            s.fire(w, e, v)
        self.send(200, 'application/json', json.dumps({'updates': s.take_updates()}))


def serve(port):
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


BROWSER_TEST = r"""
const { chromium } = require('playwright');
const url = process.argv[2];
let failures = 0;
const check = (name, ok) => { console.log((ok ? 'PASS ' : 'FAIL ') + name); if (!ok) failures++; };
const state = async () => (await fetch(url + '__state')).json();
const has = (events, e) => events.some(x => JSON.stringify(x) === JSON.stringify(e));
const beforeUnloadGuarded = (page) => page.evaluate(() => { const e = new Event('beforeunload', { cancelable: true }); window.dispatchEvent(e); return e.defaultPrevented; });
const setVisibility = (page, v) => page.evaluate((v) => { Object.defineProperty(document, 'visibilityState', { value: v, configurable: true }); document.dispatchEvent(new Event('visibilitychange')); }, v);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto(url);
  await page.waitForLoadState('networkidle');
  const cookies = await page.context().cookies();
  check('the page: a session cookie, HttpOnly', cookies.some(c => c.name === 'fbweb' && c.httpOnly));
  check('lifecycle: shown (first)', has((await state()).events, ['page', 'shown', 'first']));
  await page.evaluate(() => { window.__loads = 1; });

  await page.click('#fb-add');
  await page.waitForFunction(() => document.querySelector('#fb-count').textContent === '1');
  await page.click('#fb-add');
  await page.click('#fb-add');
  await page.waitForFunction(() => document.querySelector('#fb-count').textContent === '3');
  check('clicks answered in place, in order (1, 2, 3)', (await page.textContent('#fb-count')) === '3');
  check('enabled: the FB app turned the button off', await page.isDisabled('#fb-add'));
  check('no reload: the page is the same document', (await page.evaluate(() => window.__loads)) === 1);

  await page.click('#fb-greet');
  await page.waitForFunction(() => document.querySelector('#fb-greeting').textContent.startsWith('Type'));
  check('redraw: a message band shown', !(await page.evaluate(() => document.querySelector('#fb-greeting').classList.contains('fb-empty'))));
  await page.waitForFunction(() => document.activeElement && document.activeElement.id === 'fb-in-nameField');
  check('focus: the FB app moved the focus', true);

  const evil = '<img src=x onerror="window.__xss=1">';
  await page.fill('#fb-in-nameField', evil);
  await page.press('#fb-in-nameField', 'Enter');
  await page.waitForFunction(() => document.querySelector('#fb-greeting').textContent.startsWith('Hello'));
  check('entered + values: the field value reached FB with the event', (await page.textContent('#fb-greeting')) === 'Hello, ' + evil);
  check('escaping: typed HTML stays text', (await page.evaluate(() => window.__xss)) === undefined && (await page.$('#fb-greeting img')) === null);
  await page.waitForFunction(() => document.querySelector('#fb-echo').textContent.startsWith('nameField:'));
  check('typed: sent after a pause, with the text', (await page.textContent('#fb-echo')) === 'nameField:' + evil);

  await page.check('#fb-in-agree');
  await page.waitForFunction(() => document.querySelector('#fb-echo').textContent === 'agree:true');
  check('changed: a check box', true);
  await page.selectOption('#fb-in-colour', 'g');
  await page.waitForFunction(() => document.querySelector('#fb-echo').textContent === 'colour:g');
  check('changed: a drop-down', true);
  await page.click('#fb-people tr[data-fb-row="1"]');
  await page.waitForFunction(() => document.querySelector('#fb-echo').textContent === 'people:1');
  check('selected: a table row, marked at once', (await page.getAttribute('#fb-people tr[data-fb-row="1"]', 'aria-selected')) === 'true');

  await page.click('#fb-more');
  await page.waitForSelector('#fb-line0');
  await page.click('#fb-more');
  await page.waitForSelector('#fb-line1');
  await page.waitForFunction(() => !document.querySelector('#fb-line0'));
  check('append and remove: widgets added and taken away', (await page.textContent('#fb-line1')) === 'line 1');
  check('an action link does not navigate', page.url() === url);

  await page.selectOption('#fb-in-theme', 'dark');
  await page.waitForFunction(() => document.documentElement.getAttribute('data-fb-theme') === 'dark');
  check('theme: dark from FB, its colours applied', (await page.evaluate(() => getComputedStyle(document.body).backgroundColor)) === 'rgb(22, 22, 24)');

  await page.fill('#fb-in-note', 'remember the milk');
  check('dirty: a bound form shows unsaved changes at once', await page.evaluate(() => document.querySelector('#fb-noteForm').hasAttribute('data-fb-dirty')));
  check('the page asks before it is left with unsaved changes', await beforeUnloadGuarded(page));
  await page.fill('#fb-in-note', '');
  await page.evaluate(() => document.querySelector('#fb-noteForm').removeAttribute('data-fb-dirty'));
  await page.fill('#fb-in-product', 'Widget');
  check('an auto-saving form does not hold the page', !(await beforeUnloadGuarded(page)));
  await setVisibility(page, 'hidden');
  await page.waitForTimeout(600);
  let st = await state();
  check('hidden: the auto-saving form was saved by the lifecycle', JSON.stringify(st.store.Item) === JSON.stringify([{ Product: 'Widget' }]) && has(st.events, ['saved', 'Widget']));
  check('lifecycle: hidden', has(st.events, ['page', 'hidden', '']));
  await setVisibility(page, 'visible');
  await page.waitForTimeout(600);
  check('lifecycle: visible', has((await state()).events, ['page', 'visible', '']));

  await page.reload();
  await page.waitForLoadState('networkidle');
  check('lifecycle: shown (again) - the same session', has((await state()).events, ['page', 'shown', 'again']) && (await page.textContent('#fb-count')) === '3');
  check('the reloaded page shows the session as it was (theme, fields)', (await page.evaluate(() => document.documentElement.getAttribute('data-fb-theme'))) === 'dark' && (await page.inputValue('#fb-in-colour')) === 'g');
  check('no inline script needed (the CSP allows only web.js)', await page.evaluate(() => [...document.scripts].every(s => s.src)));

  const forged = await page.evaluate(() => fetch('/fbweb/event', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token: 'x', widget: 'add', event: 'clicked', value: '', values: {} }) }).then(r => r.json()));
  check('an event without the token is refused', forged.expired === true);

  await fetch(url + '__end_sessions');
  await page.click('#fb-greet');
  await page.waitForSelector('.fb-banner:not([hidden])');
  check('an ended session: the page says so', true);
  await page.waitForFunction(() => document.querySelector('#fb-count') && document.querySelector('#fb-count').textContent === '0', null, { timeout: 8000 });
  check('... and starts again with a fresh session', true);

  const leavingBefore = (await state()).events.filter(e => e[0] === 'page' && e[1] === 'leaving').length;
  await page.goto('about:blank');
  await new Promise(r => setTimeout(r, 600));
  check('lifecycle: leaving (a beacon as the page goes)', (await state()).events.filter(e => e[0] === 'page' && e[1] === 'leaving').length > leavingBefore);
  check('no script errors', errors.length === 0);
  if (errors.length) console.log(errors.join('\n'));
  await browser.close();
  console.log('web toolkit: ' + (failures ? failures + ' failed' : 'all passed'));
  process.exit(failures ? 1 : 0);
})().catch((e) => { console.log('FAIL ' + e); process.exit(1); });
"""


def run_tests():
    import shutil
    import subprocess
    import tempfile
    node = shutil.which('node')
    if not node or subprocess.run([node, '-e', "require('playwright')"], capture_output=True).returncode != 0:
        print('SKIP  web.js in a browser (no node + playwright here)')
        return True
    srv = serve(0)
    url = f'http://127.0.0.1:{srv.server_address[1]}/'
    with tempfile.TemporaryDirectory() as tmp:
        script = os.path.join(tmp, 'web_toolkit_test.js')
        open(script, 'w').write(BROWSER_TEST)
        run = subprocess.run([node, script, url], capture_output=True, text=True, timeout=180)
    srv.shutdown()
    print(run.stdout.rstrip())
    if run.returncode != 0 and run.stderr:
        print(run.stderr.rstrip())
    return run.returncode == 0


if __name__ == '__main__':
    if '--serve' in sys.argv:
        port = int(sys.argv[sys.argv.index('--serve') + 1])
        serve(port)
        print(f'http://127.0.0.1:{port}/  (Ctrl-C to stop)')
        threading.Event().wait()
    sys.exit(0 if run_tests() else 1)
