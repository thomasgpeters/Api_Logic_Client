#!/usr/bin/env python3
"""Where the Studio finds an API Logic Server project's model, and what it makes of it - the
reference for src/AppBuilder/ALS Project.incl (the Open ALS Project screen), function for function.

    python3 tools/als_project_reference.py --test <ALS project folder> [...] [--github]

Checks, on each ALS project folder (made with `ApiLogicServer create`):
  - the folder, its database/ folder, and database/models.py itself all find the same model
  - the Studio model: every resource, attributes with pk in key order, keyKind, relationships
    with the parent's keys, and a lookup on every single-column key to a parent (Employee has two,
    to Department; Order -> Location is composite and has none); display columns that exist
  - GitHub addresses parse into repository, branch and path (no network)
With --github, also reads public repositories over raw.githubusercontent.com, as the Studio does
(main, else master; database/models.py, else ui/app/app_model.yaml, else ui/admin/admin.yaml).
"""
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models_py_reference import read_models_py          # noqa: E402  (ALS Model.incl's reference)
from jsonapi_reference import read_model_yaml            # noqa: E402

MODEL_PATHS = ['database/models.py', 'ui/app/app_model.yaml', 'ui/admin/admin.yaml']
ADMIN = 'ui/admin/admin.yaml'


def is_models_py(text):
    return text is not None and 'Base):' in text


def model_from_text(text):                                # ALSModelFromText
    if not text:
        return {}
    if is_models_py(text):
        return read_models_py(text)
    try:
        return read_model_yaml(text)
    except Exception:
        return {}


def keyed_by_resource(model):                             # ALSPyResolve's last step
    return {e['resource']: e for e in model.values()} if model and 'resource' in next(iter(model.values())) else model


def als_model(text):
    return keyed_by_resource(model_from_text(text))


def is_model(text):                                       # ALSProjectIsModel
    return bool(text) and len(model_from_text(text)) > 0


def kept_name(text):                                      # ALSProjectKeptName
    if is_models_py(text):
        return 'models.py'
    if text.startswith('entities:') or '\nentities:' in text:
        return 'app_model.yaml'
    return 'admin.yaml'


def found(text, admin, source):                           # ALSProjectFound
    name = kept_name(text)
    admin_kept = admin if name != 'admin.yaml' and admin and 'resources:' in admin else None
    return {'text': text, 'name': name, 'admin': admin_kept, 'source': source}


def read_file(path):
    try:
        return open(path).read() if os.path.isfile(path) else None
    except OSError:
        return None


def read_folder(folder):                                  # ALSProjectReadFolder
    folders = [folder]
    name = os.path.basename(folder.rstrip('/')).lower()
    if name in ('database', 'ui'):
        folders.append(os.path.dirname(folder.rstrip('/')))
    if name in ('admin', 'app'):
        folders.append(os.path.dirname(os.path.dirname(folder.rstrip('/'))))
    for f in folders:
        for p in MODEL_PATHS:
            text = read_file(os.path.join(f, p))
            if is_model(text):
                return found(text, read_file(os.path.join(f, ADMIN)), f)
    return None


def read_model_file(path):                                # ALSProjectReadModelFile
    text = read_file(path)
    if not is_model(text):
        return None
    project = os.path.dirname(os.path.dirname(path))
    return found(text, read_file(os.path.join(project, ADMIN)), path)


def github_parts(address):                                # ALSProjectGitHubParts
    a = address.strip()
    for prefix in ('https://', 'http://', 'www.'):
        if a.startswith(prefix):
            a = a[len(prefix):]
    raw = a.startswith('raw.githubusercontent.com/')
    if raw:
        a = a[len('raw.githubusercontent.com/'):]
    elif a.startswith('github.com/'):
        a = a[len('github.com/'):]
    else:
        return None
    parts = [p for p in a.split('/') if p]
    if len(parts) < 2:
        return None
    repo = parts[1][:-4] if parts[1].endswith('.git') else parts[1]
    repo = f'{parts[0]}/{repo}'
    branch, path = '', ''
    if raw:
        branch = parts[2] if len(parts) > 2 else ''
        path = '/'.join(parts[3:])
    else:
        if len(parts) > 3 and parts[2] in ('tree', 'blob'):
            branch = parts[3]
        path = '/'.join(parts[4:]) if len(parts) > 4 else ''
    return [repo, branch, path]


def fetch(repo, branch, path):                            # ALSProjectFetch
    try:
        with urllib.request.urlopen(f'https://raw.githubusercontent.com/{repo}/{branch}/{path}', timeout=20) as r:
            return r.read().decode('utf-8')
    except Exception:
        return None


def read_github(address):                                 # ALSProjectReadGitHub
    parts = github_parts(address)
    if parts is None:
        return None
    repo, given_branch, given = parts
    branches = [given_branch] if given_branch else ['main', 'master']
    prefix = ''
    if given.lower().endswith(('.py', '.yaml', '.yml')):
        paths = [given]
    else:
        prefix = given + '/' if given else ''
        paths = [prefix + p for p in MODEL_PATHS]
    for b in branches:
        for p in paths:
            text = fetch(repo, b, p)
            if is_model(text):
                return found(text, fetch(repo, b, prefix + ADMIN), f'https://github.com/{repo}/blob/{b}/{p}')
    return None


def read(address):                                        # ALSProjectRead
    address = (address or '').strip()
    if not address:
        return None
    if github_parts(address) is not None:
        return read_github(address)
    path = os.path.expanduser(address)
    if not os.path.exists(path):
        return None
    return read_folder(path) or read_model_file(path)


def suggested_name(address, source):                      # ALSProjectSuggestedName
    parts = github_parts(address)
    if parts:
        return parts[0].split('/')[-1]
    if not source:
        return ''
    path, lower = source, source.lower()
    if lower.endswith('.py'):
        path = os.path.dirname(os.path.dirname(path))
    if lower.endswith(('.yaml', '.yml')):
        path = os.path.dirname(os.path.dirname(os.path.dirname(path)))
    name = os.path.basename(path)
    return '' if name in ('', '/') else name


def display_attribute(parent, key):                       # SQLiteModelDisplayAttribute (SQLite Model.incl)
    found_name, first_text = None, None
    for a in parent['attributes']:
        lower = a['name'].lower()
        if lower in ('name', 'title', 'description', 'label'):
            return a['name']
        if found_name is None and 'name' in lower:
            found_name = a['name']
        if first_text is None and a.get('pk', 0) == 0 and ('CHAR' in a['type'].upper() or 'TEXT' in a['type'].upper()):
            first_text = a['name']
    return found_name or first_text or key


def display_column(als, display_model, parent_name, studio_parent, key):   # ALSProjectDisplayColumn
    for m in (display_model or {}, als):
        d = m.get(parent_name, {}).get('display')
        if d:
            return d
    return display_attribute(studio_parent, key)


def studio_resource(als, entity):                         # ALSProjectStudioResource
    keys = entity.get('keys') or []
    attributes, key_kind = [], ('none' if not keys else 'assigned')
    for a in entity.get('attributes') or []:
        t = a.get('type') or 'VARCHAR'
        attr = {'name': a['name'], 'type': t, 'notnull': a['name'] in keys or bool(a.get('required'))}
        if a['name'] in keys:
            attr['pk'] = keys.index(a['name']) + 1
            if len(keys) == 1 and t.upper().startswith('INTEGER'):
                key_kind = 'identity'
                attr['generated'] = True
        else:
            attr['pk'] = 0
        attributes.append(attr)
    rels = []
    for r in entity.get('relationships') or []:
        parent = als.get(r['resource'])
        rels.append({'name': r['name'], 'direction': r['direction'], 'resource': r['resource'],
                     'fks': r.get('fks') or [], 'parentKeys': (parent or {}).get('keys') or []})
    res = {'kind': 'table', 'attributes': attributes, 'keys': keys, 'keyKind': key_kind, 'relationships': rels}
    if entity.get('table'):
        res['table'] = entity['table']
    return res


def studio_model(als, display_model=None):                # ALSProjectStudioModel
    resources = {name: studio_resource(als, e) for name, e in als.items()}
    for name, res in resources.items():
        for r in res['relationships']:
            parent = resources.get(r['resource'])
            if r['direction'] == 'toone' and len(r['fks']) == 1 and len(r['parentKeys']) == 1 and parent:
                for a in res['attributes']:
                    if a['name'] == r['fks'][0]:
                        a['lookup'] = {'entity': r['resource'], 'key': r['parentKeys'][0],
                                       'display': display_column(als, display_model, r['resource'], parent, r['parentKeys'][0])}
    return {'resources': resources}


# --- the test --------------------------------------------------------------------------------
def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--test' not in sys.argv:
        print(__doc__); return 2
    results = []

    def check(name, ok, info=''):
        results.append(bool(ok)); print(('PASS  ' if ok else 'FAIL  ') + name + (f'   ({info})' if info and not ok else ''))

    cases = {'https://github.com/ApiLogicServer/basic_demo': ['ApiLogicServer/basic_demo', '', ''],
             'github.com/o/r.git': ['o/r', '', ''],
             'https://github.com/o/r/tree/dev/projects/nw': ['o/r', 'dev', 'projects/nw'],
             'https://github.com/o/r/blob/main/database/models.py': ['o/r', 'main', 'database/models.py'],
             'https://raw.githubusercontent.com/o/r/main/ui/admin/admin.yaml': ['o/r', 'main', 'ui/admin/admin.yaml'],
             '/Users/me/nw': None, 'github.com/onlyowner': None}
    check('GitHub addresses: repository, branch and path (or not an address)',
          all(github_parts(a) == want for a, want in cases.items()),
          {a: github_parts(a) for a in cases})

    for project in args:
        name = os.path.basename(project.rstrip('/'))
        a = read(project)
        check(f'{name}: the folder finds database/models.py', a and a['name'] == 'models.py', a and a['name'])
        b, c = read(os.path.join(project, 'database')), read(os.path.join(project, 'database', 'models.py'))
        check(f'{name}: its database/ folder and the file itself find the same model',
              b and c and b['text'] == a['text'] == c['text'])
        check(f'{name}: admin.yaml beside it is kept for display columns', a['admin'] and 'resources:' in a['admin'])
        check(f'{name}: the suggested project name is the folder\'s', suggested_name(project, a['source']) == name and
              suggested_name(os.path.join(project, 'database', 'models.py'), c['source']) == name)
        als = als_model(a['text'])
        display = read_model_yaml(a['admin']) if a['admin'] else None
        model = studio_model(als, display)['resources']
        check(f'{name}: a Studio resource for every ALS resource ({len(als)})', set(model) == set(als))
        bad = [f'{r}.{x["name"]}' for r, res in model.items() for x in res['attributes']
               if x['pk'] and res['keys'].index(x['name']) + 1 != x['pk']]
        check(f'{name}: primary keys in key order', not bad, bad)
        bad = []
        for r, res in model.items():
            names = {x['name'] for x in res['attributes']}
            for rel in res['relationships']:
                if not set(rel['fks']) <= (names if rel['direction'] == 'toone' else {x['name'] for x in model[rel['resource']]['attributes']}):
                    bad.append(f'{r}.{rel["name"]}')
                if rel['parentKeys'] != model[rel['resource']]['keys']:
                    bad.append(f'{r}.{rel["name"]} parentKeys')
        check(f'{name}: every relationship\'s key columns exist; parentKeys are the parent\'s keys', not bad, bad)
        lookups = {(r, x['name']): x['lookup'] for r, res in model.items() for x in res['attributes'] if 'lookup' in x}
        bad = [k for k, l in lookups.items() if l['display'] not in {x['name'] for x in model[l['entity']]['attributes']}]
        check(f'{name}: {len(lookups)} lookups, each display column a column of its parent', lookups and not bad, bad)
        if name == 'nw':
            check('nw: Employee has two lookups to Department (WorksFor, OnLoan)',
                  lookups.get(('Employee', 'WorksForDepartmentId'), {}).get('entity') == 'Department' and
                  lookups.get(('Employee', 'OnLoanDepartmentId'), {}).get('entity') == 'Department')
            check('nw: Order -> Location (composite key) has no lookup',
                  ('Order', 'City') not in lookups and ('Order', 'Country') not in lookups)
            check('nw: Customer\'s lookup shows admin.yaml\'s user_key (CompanyName)',
                  lookups.get(('Order', 'CustomerId'), {}).get('display') == 'CompanyName', lookups.get(('Order', 'CustomerId')))
            check('nw: keyKind - Employee identity (INTEGER), Customer assigned (text id)',
                  model['Employee']['keyKind'] == 'identity' and model['Customer']['keyKind'] == 'assigned')
            check('nw: Category keeps its table (CategoryTableNameTest)', model['Category'].get('table') == 'CategoryTableNameTest')

    if '--github' in sys.argv:
        for address in ('https://github.com/ApiLogicServer/basic_demo', 'https://github.com/ApiLogicServer/demo/tree/main'):
            g = read(address)
            check(f'GitHub: {address} -> database/models.py over raw.githubusercontent.com',
                  g and g['name'] == 'models.py' and len(als_model(g['text'])) > 0, g and g['source'])
            if g:
                m = studio_model(als_model(g['text']), read_model_yaml(g['admin']) if g['admin'] else None)['resources']
                print(f'      {len(m)} resources: {", ".join(sorted(m))}; admin.yaml {"kept" if g["admin"] else "not found"}')
        check('GitHub: a repository with no ALS model is refused', read('https://github.com/ApiLogicServer/no-such-repo-here') is None)

    failed = results.count(False)
    print(f'als_project_reference: {len(results)} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
