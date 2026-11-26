#!/usr/bin/env python3
"""Builds Imagery's FutureBasic site - https://fb.imagery-business-systems.com/ - as static files, from this repository.

    python3 tools/make_site.py [out-folder]          default: ./site (not kept in git)

Upload the folder to any web server (it is plain HTML, CSS, pictures and zip files). Everything is made from what the
repository already holds, so the site and the apps never disagree:
    /                         the home page: the free modules, App Builder, the samples
    /sql-generator/           the SQL Generator: its README, the download, its Help
    /logicbank/               LogicBank for FutureBasic: the same
    /help/sql-generator/      the example apps' user guides (User Guide.txt), as web pages - what their Help shows
    /help/logicbank/
    /samples/, /samples/<name>/   the sample applications: their READMEs, their downloads
    /app-builder/             App Builder: Lite and Enterprise, registration on the Imagery License Server
    /downloads/*.zip          each module's example app (MIT), each sample
Standard library only (no packages to install). Imagery's name and logos are not licensed for reuse.
"""
import html
import urllib.parse
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
SITE_URL = 'https://fb.imagery-business-systems.com/'
YEAR = '2026'

MODULES = [
    {'slug': 'sql-generator', 'name': 'SQL Generator', 'folder': 'src/SQLGeneratorExample', 'zip': 'SQL-Generator-Example.zip',
     'blurb': 'Describe a SELECT, INSERT, UPDATE or DELETE as a dictionary - tables, columns, filters, joins - and get safe, '
              'parameterized SQL for SQLite. Names are quoted for you; every value is bound, never pasted into the SQL.'},
    {'slug': 'logicbank', 'name': 'LogicBank for FutureBasic', 'folder': 'src/LogicBankExample', 'zip': 'LogicBank-for-FutureBasic-Example.zip',
     'blurb': 'Your business logic, handled in one place: sums, counts, formulas, copies, constraints and delete actions, '
              'declared once and enforced on every save. Like your bank - what you put in, you can take out, and the arithmetic is done for you.'},
    {'slug': 'web-toolkit', 'name': 'Web Toolkit for FutureBasic', 'folder': 'src/WebToolkit', 'zip': 'Web-Toolkit-for-FutureBasic.zip',
     'example': 'src/WebToolkitExample', 'example_zip': 'Web-Toolkit-Orders-Example.zip',
     'blurb': 'Web applications written in FutureBasic: widgets, events answered in the background (AJAX), a page lifecycle, '
              'pages laid out in XIB files with the Layout Tool. Your business logic runs in FB, on the server, behind nginx.'},
]
SAMPLES = [('Telecom', 'A mobile carrier\'s travel plans, priced from its roaming agreements.'),
           ('Customs', 'Automated customs clearance, set in Bermuda: duty, risk lanes, release and the port gate.'),
           ('FlightPlanner', 'VFR flight planning: wind, weight and balance, runways, weather and a go / no-go.')]
SKIP = {'__pycache__', '.DS_Store'}

CSS = """:root { --bg:#ffffff; --fg:#1d1d1f; --soft:#5f6368; --line:#d2d2d7; --card:#f5f5f7; --accent:#0a63c9; --code:#f0f0f3; }
@media (prefers-color-scheme: dark) { :root { --bg:#161618; --fg:#f2f2f4; --soft:#a1a1a6; --line:#3a3a3c; --card:#1f1f22; --accent:#4c9bff; --code:#26262a; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.55 -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; }
header, main, footer { max-width: 960px; margin: 0 auto; padding: 0 20px; }
header { display:flex; align-items:center; gap:16px; padding-top:24px; padding-bottom:12px; border-bottom:1px solid var(--line); flex-wrap:wrap; }
header img { height:44px; } header .site { font-weight:700; font-size:18px; color:var(--fg); text-decoration:none; }
nav { margin-left:auto; display:flex; gap:18px; flex-wrap:wrap; } nav a { color:var(--soft); text-decoration:none; } nav a:hover { color:var(--accent); }
main { padding-top:28px; padding-bottom:48px; } h1 { font-size:34px; line-height:1.2; margin:0 0 12px; } h2 { margin-top:36px; } h3 { margin-top:24px; }
a { color:var(--accent); } p, li { max-width: 760px; } .lead { font-size:19px; color:var(--soft); max-width:760px; }
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:16px; margin-top:20px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:20px; }
.card h3 { margin-top:0; } .tag { display:inline-block; font-size:12px; font-weight:600; padding:2px 8px; border-radius:999px; border:1px solid var(--line); color:var(--soft); }
.button { display:inline-block; background:var(--accent); color:#fff; text-decoration:none; padding:9px 18px; border-radius:999px; font-weight:600; margin:6px 8px 6px 0; }
.button.secondary { background:transparent; color:var(--accent); border:1px solid var(--accent); }
pre { background:var(--code); border:1px solid var(--line); border-radius:10px; padding:14px; overflow-x:auto; font-size:13px; line-height:1.45; }
code { font-family: ui-monospace, Menlo, monospace; font-size:0.92em; } p code, li code, td code { background:var(--code); padding:1px 4px; border-radius:4px; }
table { border-collapse:collapse; margin:16px 0; width:100%; font-size:15px; display:block; overflow-x:auto; } th, td { border:1px solid var(--line); padding:6px 10px; text-align:left; vertical-align:top; } th { background:var(--card); }
img.figure { max-width:100%; border:1px solid var(--line); border-radius:10px; background:#fff; }
footer { border-top:1px solid var(--line); padding-top:16px; padding-bottom:32px; color:var(--soft); font-size:14px; }
"""


def esc(text):
    return html.escape(text, quote=False)


def inline(text):
    """**bold**, *italic*, `code`, [text](url) - links to the web kept, links into the repository shown as text"""
    parts = re.split(r'(`[^`]*`)', text)
    out = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 1:
            out.append('<code>' + esc(part[1:-1]) + '</code>')
            continue
        s = esc(part)
        s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', s)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<em>\1</em>', s)
        out.append(s)
    return ''.join(out)


def markdown_to_html(text):
    """the Markdown our READMEs use: headings, paragraphs, lists (nested by indent), fenced code, tables, quotes"""
    lines = text.replace('\r\n', '\n').split('\n')
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('```'):
                j += 1
            out.append('<pre><code>' + esc('\n'.join(lines[i + 1:j])) + '</code></pre>')
            i = j + 1
            continue
        m = re.match(r'(#{1,6})\s+(.*)', line)
        if m:
            level = min(len(m.group(1)) + (0 if len(m.group(1)) > 1 else 0), 6)
            out.append(f'<h{level}>{inline(m.group(2))}</h{level}>')
            i += 1
            continue
        if line.strip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            body = [r for r in rows if not all(re.fullmatch(r':?-{2,}:?', c) for c in r)]
            out.append('<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in body[0]) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body[1:]) + '</tbody></table>')
            continue
        if re.match(r'\s*([-*]|\d+\.)\s+', line):
            out.append(list_block(lines, i))
            while i < len(lines) and (re.match(r'\s*([-*]|\d+\.)\s+', lines[i]) or (lines[i].startswith('  ') and lines[i].strip() and not lines[i].strip().startswith('|'))):
                i += 1
            continue
        if line.startswith('>'):
            out.append('<blockquote>' + inline(line.lstrip('> ')) + '</blockquote>')
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'(#|```|\s*\||\s*([-*]|\d+\.)\s+|>)', lines[i]):
            para.append(lines[i])
            i += 1
        out.append('<p>' + inline(' '.join(p.strip() for p in para)) + '</p>')
    return '\n'.join(out)


def list_block(lines, i):
    """a list and its nested lists, by indent; a line indented under an item continues it"""
    items, j = [], i
    while j < len(lines):
        m = re.match(r'(\s*)([-*]|\d+\.)\s+(.*)', lines[j])
        if m:
            items.append([len(m.group(1)), m.group(2)[-1] == '.', m.group(3)])
        elif lines[j].startswith('  ') and lines[j].strip() and not lines[j].strip().startswith('|') and items:
            items[-1][2] += ' ' + lines[j].strip()
        else:
            break
        j += 1
    html_out, stack = [], []
    for indent, ordered, content in items:
        while stack and indent < stack[-1][0]:
            html_out.append('</li></' + stack.pop()[1] + '>')
        if not stack or indent > stack[-1][0]:
            tag = 'ol' if ordered else 'ul'
            stack.append((indent, tag))
            html_out.append(f'<{tag}><li>')
        else:
            html_out.append('</li><li>')
        html_out.append(inline(content))
    while stack:
        html_out.append('</li></' + stack.pop()[1] + '>')
    return ''.join(html_out)


def guide_to_html(text, picture_prefix):
    """an example's User Guide.txt (Rich Text.incl's markup) -> HTML: the page the app's Help shows on the web"""
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    out, i, in_list = [], 0, False
    def close_list():
        nonlocal in_list
        if in_list:
            out.append('</ul>')
            in_list = False
    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            close_list()
            j = i + 1
            while j < len(lines) and not lines[j].startswith('```'):
                j += 1
            out.append('<pre><code>' + esc('\n'.join(lines[i + 1:j])) + '</code></pre>')
            i = j + 1
            continue
        if line.startswith('## '):
            close_list()
            out.append('<h2>' + inline(line[3:]) + '</h2>')
        elif line.startswith('# '):
            close_list()
            out.append('<h1>' + inline(line[2:]) + '</h1>')
        elif line.startswith('- '):
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append('<li>' + inline(line[2:]) + '</li>')
        elif re.fullmatch(r'!\[(.+)\]', line.strip()):
            close_list()
            name = re.fullmatch(r'!\[(.+)\]', line.strip()).group(1)
            out.append(f'<p><img class="figure" src="{picture_prefix}{urllib.parse.quote(name)}.png" alt="{html.escape(name)}"></p>')
        elif line.strip():
            close_list()
            out.append('<p>' + inline(line) + '</p>')
        i += 1
    close_list()
    return '\n'.join(out)


def after_title(body_html, insert):
    """insert just after the page's first heading (the README's title)"""
    at = body_html.find('</h1>')
    return body_html[:at + 5] + '\n' + insert + body_html[at + 5:] if at >= 0 else insert + body_html


def page(title, body, depth, description=''):
    up = '../' * depth
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Imagery Business Systems for FutureBasic</title>
<meta name="description" content="{html.escape(description or title)}">
<link rel="stylesheet" href="{up}styles.css"></head>
<body>
<header><a href="{up}index.html"><picture><source srcset="{up}images/imagery_logo_white.png" media="(prefers-color-scheme: dark)"><img src="{up}images/imagery_logo.png" alt="Imagery Business Systems"></picture></a>
<a class="site" href="{up}index.html">FutureBasic tools</a>
<nav><a href="{up}sql-generator/index.html">SQL Generator</a><a href="{up}logicbank/index.html">LogicBank</a><a href="{up}web-toolkit/index.html">Web Toolkit</a><a href="{up}app-builder/index.html">App Builder</a><a href="{up}samples/index.html">Samples</a></nav></header>
<main>
{body}
</main>
<footer>&copy; {YEAR} Imagery Business Systems, LLC. The SQL Generator and LogicBank for FutureBasic are free and open source (MIT).
The Imagery name and logos are not licensed for reuse. FutureBasic is the work of its own authors.</footer>
</body></html>
"""


def write(out, rel, text):
    path = os.path.join(out, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def zip_folder(folder, zip_path, top):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(folder):
            dirs[:] = sorted(d for d in dirs if d not in SKIP)
            for f in sorted(files):
                if f in SKIP:
                    continue
                full = os.path.join(base, f)
                z.write(full, os.path.join(top, os.path.relpath(full, folder)))


def licence_server():
    text = open(os.path.join(ROOT, 'src', 'AppBuilder', 'Licence.incl'), encoding='utf-8').read().replace('\r', '\n')
    server = re.search(r'#define LICENCE_SERVER\s+@"([^"]+)"', text).group(1)
    page_path = re.search(r'#define LICENCE_PAGE\s+@"([^"]+)"', text).group(1)
    return server + page_path


def build(out):
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'images'))
    os.makedirs(os.path.join(out, 'downloads'))
    write(out, 'styles.css', CSS)
    for logo in ('imagery_logo.png', 'imagery_logo_white.png'):
        shutil.copy(os.path.join(ROOT, 'src', 'Shared', logo), os.path.join(out, 'images', logo))

    # the modules: README, download, Help
    for m in MODULES:
        folder = os.path.join(ROOT, m['folder'])
        zip_folder(folder, os.path.join(out, 'downloads', m['zip']), os.path.basename(m['folder']))
        readme = open(os.path.join(folder, 'README.md'), encoding='utf-8').read()
        if m.get('example'):
            # a module with its example apart: the module (its template and tools), and the example
            zip_folder(os.path.join(ROOT, m['example']), os.path.join(out, 'downloads', m['example_zip']), os.path.basename(m['example']))
            buttons = (f'<p><a class="button" href="../downloads/{m["zip"]}">Download the module (zip)</a>'
                       f'<a class="button secondary" href="../downloads/{m["example_zip"]}">Download the example (zip)</a>'
                       f'<a class="button secondary" href="../help/{m["slug"]}/index.html">Read the user guide</a></p>')
        else:
            buttons = (f'<p><a class="button" href="../downloads/{m["zip"]}">Download the example (zip)</a>'
                       f'<a class="button secondary" href="../help/{m["slug"]}/index.html">Read the user guide</a></p>')
        body = after_title(markdown_to_html(readme), buttons)
        write(out, f'{m["slug"]}/index.html', page(m['name'], body, 1, m['blurb']))
        help_dir = os.path.join(out, 'help', m['slug'])
        os.makedirs(help_dir, exist_ok=True)
        for f in os.listdir(folder):
            if f.endswith('.png') and 'logo' not in f:
                shutil.copy(os.path.join(folder, f), os.path.join(help_dir, f))
        guide = open(os.path.join(folder, 'User Guide.txt'), encoding='utf-8').read()
        write(out, f'help/{m["slug"]}/index.html',
              page(m['name'] + ' - User Guide', guide_to_html(guide, '') + f'\n<p><a class="button" href="../../downloads/{m["zip"]}">Download the example (zip)</a></p>', 2))

    # the samples
    cards = []
    for name, blurb in SAMPLES:
        folder = os.path.join(ROOT, 'samples', name)
        zip_name = f'{name}-Sample.zip'
        zip_folder(folder, os.path.join(out, 'downloads', zip_name), name)
        readme = open(os.path.join(folder, 'README.md'), encoding='utf-8').read()
        body = after_title(markdown_to_html(readme), f'<p><a class="button" href="../../downloads/{zip_name}">Download the sample (zip)</a></p>')
        write(out, f'samples/{name.lower()}/index.html', page(name + ' sample', body, 2, blurb))
        cards.append(f'<div class="card"><h3><a href="{name.lower()}/index.html">{esc(name)}</a></h3><p>{esc(blurb)}</p></div>')
    write(out, 'samples/index.html', page('Sample applications', '<h1>Sample applications</h1>\n<p class="lead">Each is a SQLite database with its business rules, '
          'its tests, and the same rules in FutureBasic - built to show what LogicBank for FutureBasic does on a real problem.</p>\n'
          f'<div class="cards">{"".join(cards)}</div>', 1))

    # App Builder
    register = licence_server()
    write(out, 'app-builder/index.html', page('App Builder for FutureBasic', f"""<h1>App Builder for FutureBasic</h1>
<p class="lead">A Mac app that builds a complete FutureBasic application from your database: the windows and forms, the lists,
the data binding, and the business rules - ready to open in the FutureBasic editor and build.</p>
<p><a class="button" href="{register}">Register for a free Lite licence</a><a class="button secondary" href="{register}">Enterprise</a></p>
<table><thead><tr><th></th><th>Lite</th><th>Enterprise</th></tr></thead><tbody>
<tr><td>Licence</td><td>free, with registration</td><td>paid</td></tr>
<tr><td>Start from</td><td>a SQLite database</td><td>a SQLite database, or an API Logic Server project</td></tr>
<tr><td>The app</td><td>runs on your Mac, its rules with it (LogicBank for FutureBasic)</td><td>three tiers: many users, the rules enforced on the server, sign-in and security</td></tr>
<tr><td>Rules</td><td>written, checked and tested in App Builder</td><td>the same, and shared with your Python project (declare_logic.py)</td></tr>
<tr><td>AI assistant (coming)</td><td>rules from sentences in your model's names, with your own key</td><td>also through API Logic Server's genai-logic</td></tr>
</tbody></table>
<p>The free modules are App Builder's foundations: every app it builds carries the SQL Generator and LogicBank for FutureBasic.
With the modules alone you write your rules by hand; App Builder writes them from plain sentences, checks them against your model,
tests every rule, and builds the app around them.</p>
<p>The same goes for the web (coming): with the Web Toolkit alone you write each page yourself; App Builder will build the pages
from your model - forms, lists, bindings and rules - for a web app beside, or instead of, the Mac app.</p>""", 1, 'Build a complete FutureBasic app from your database.'))

    # the home page
    module_cards = ''.join(f'<div class="card"><span class="tag">free &middot; MIT</span><h3><a href="{m["slug"]}/index.html">{esc(m["name"])}</a></h3>'
                           f'<p>{esc(m["blurb"])}</p><p><a href="downloads/{m["zip"]}">Download</a> &middot; <a href="help/{m["slug"]}/index.html">User guide</a></p></div>'
                           for m in MODULES)
    write(out, 'index.html', page('FutureBasic tools', f"""<h1>Tools for FutureBasic programmers</h1>
<p class="lead">From Imagery Business Systems: three free modules for your own apps, sample applications that show them at work,
and App Builder, which builds a whole app from your database.</p>
<h2>Free modules</h2>
<div class="cards">{module_cards}</div>
<h2>App Builder for FutureBasic</h2>
<div class="cards"><div class="card"><span class="tag">Lite free &middot; Enterprise licensed</span><h3><a href="app-builder/index.html">App Builder</a></h3>
<p>Windows, forms, lists, data binding and business rules, generated from your database. Rules from plain sentences, checked and tested.</p>
<p><a href="{register}">Register</a> &middot; <a href="app-builder/index.html">Lite and Enterprise</a></p></div>
<div class="card"><span class="tag">samples</span><h3><a href="samples/index.html">Sample applications</a></h3>
<p>{", ".join(esc(n) for n, _ in SAMPLES)}: real problems, with their databases, rules and tests.</p></div></div>""", 0,
        'Free FutureBasic modules - the SQL Generator, LogicBank for FutureBasic and the Web Toolkit - and App Builder for FutureBasic.'))
    return out


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'site')
    print('built', build(target), 'for', SITE_URL)
