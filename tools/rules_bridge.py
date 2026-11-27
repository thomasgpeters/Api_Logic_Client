#!/usr/bin/env python3
"""
rules_bridge - business rules between ApiLogicServer's declare_logic.py, the project's
Rules.json (App Builder for FutureBasic) and the generated app's FB code.

    rules_bridge.py import   <declare_logic.py> --model <db.sqlite | Model.json> --rules <Rules.json>
    rules_bridge.py export   --rules <Rules.json> --model <...> --out <declare_logic.py>
    rules_bridge.py check    --rules <Rules.json> --model <...>
    rules_bridge.py generate --rules <Rules.json> --model <...> --out <Studio Rules.incl>
    rules_bridge.py --test   <Northwind db.sqlite>
    rules_bridge.py --help

import    reads LogicBank's Rule.sum / count / formula / copy / constraint / parent_check /
          row events with Python's own parser and translates each rule's lambda into the FB
          the engine runs (row.Quantity -> fn LogicDouble( logicRow, @"Quantity" )). A rule it
          cannot translate safely (a Python function, a conditional expression, a library
          call) is imported switched off, its Python kept beside it ("source") to rewrite in
          FB. Existing rules are kept; an imported rule replaces one with the same id.
export    writes LogicBank rules back: an imported rule unchanged since import is written as
          it came; others are translated from their FB; FB the translator cannot read back is
          written as a comment for a person to finish.
check     names (entities, attributes, child lists, roles) against the model, dependencies,
          formula cycles; prints a JSON report and fills each formula's dependsOn.
generate  writes the generated app's Studio Rules.incl: one FB function per rule and
          DeclareStudioRules, which the app's main calls before its own DeclareRules.

Python 3.9+ (the python3 that comes with Xcode's command-line tools, which FB needs anyway).
Writes only the files named on the command line.
"""
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sqlite_model  # noqa: E402

KINDS = ('formula', 'constraint', 'sum', 'count', 'copy', 'parentCheck', 'deleteAction', 'rowEvent', 'commitEvent')
NUMERIC = re.compile(r'(?i)int|real|floa|doub|dec|num|money|bool|bit')


class Untranslatable(Exception):
    pass


# ------------------------------------------------------------------ the model

class Model:
    def __init__(self, path):
        if path.endswith('.json'):
            with open(path) as f:
                entries = json.load(f)['resources']
            self.entities = {e['name']: {'columns': {f['name']: f.get('type', '') for f in e.get('fields', [])},
                                         'relationships': e.get('relationships', [])} for e in entries}
        else:
            self.entities = {name: {'columns': {a['name']: a.get('type', '') for a in r['attributes']},
                                    'relationships': r.get('relationships', [])}
                             for name, r in sqlite_model.read_model(path).items()}

    def has(self, entity, attr=None):
        return entity in self.entities and (attr is None or attr in self.entities[entity]['columns'])

    def numeric(self, entity, attr):
        return bool(NUMERIC.search(self.entities.get(entity, {}).get('columns', {}).get(attr, '') or ''))

    def relationship(self, entity, name):
        return next((r for r in self.entities.get(entity, {}).get('relationships', []) if r['name'] == name), None)

    def roles_to(self, child, parent):
        return [r for r in self.entities.get(child, {}).get('relationships', [])
                if r['direction'] == 'toone' and r['resource'] == parent]

    def lists_to(self, parent, child):
        return [r for r in self.entities.get(parent, {}).get('relationships', [])
                if r['direction'] == 'tomany' and r['resource'] == child]


# ------------------------------------------------------------------ Python lambda -> FB

def fb_string(text):
    return '@"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'


class ToFB:
    """Translate the body of `lambda row: ...` for one entity into an FB expression."""

    def __init__(self, model, entity):
        self.model, self.entity = model, entity

    def attr_ref(self, node):
        # row.X -> ('X', None); row.Role.X -> ('X', 'Role')
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'row':
            return node.attr, None
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute) \
                and isinstance(node.value.value, ast.Name) and node.value.value.id == 'row':
            return node.attr, node.value.attr
        return None

    def parent_entity(self, role):
        rel = self.model.relationship(self.entity, role)
        if rel is None or rel['direction'] != 'toone':
            raise Untranslatable(f'{self.entity} has no parent role {role}')
        return rel['resource']

    def is_numeric(self, node):
        ref = self.attr_ref(node)
        if ref:
            attr, role = ref
            return self.model.numeric(self.parent_entity(role) if role else self.entity, attr)
        if isinstance(node, ast.Constant):
            return isinstance(node.value, (int, float)) and not isinstance(node.value, bool)
        if isinstance(node, ast.BinOp):
            return True
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return True
        return False

    def value(self, node):
        """An expression giving a number (FB double) or text (CFStringRef)."""
        ref = self.attr_ref(node)
        if ref:
            attr, role = ref
            owner = self.parent_entity(role) if role else self.entity
            if not self.model.has(owner, attr):
                raise Untranslatable(f'{owner} has no attribute {attr}')
            numeric = self.model.numeric(owner, attr)
            if role:
                return (f'fn LogicParentDouble( logicRow, {fb_string(role)}, {fb_string(attr)} )' if numeric
                        else f'fn LogicParentString( logicRow, {fb_string(role)}, {fb_string(attr)} )')
            return (f'fn LogicDouble( logicRow, {fb_string(attr)} )' if numeric
                    else f'fn LogicString( logicRow, {fb_string(attr)} )')
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return 'YES' if node.value else 'NO'
            if isinstance(node.value, (int, float)):
                return repr(float(node.value)) if isinstance(node.value, float) else str(node.value)
            if isinstance(node.value, str):
                return fb_string(node.value)
        if isinstance(node, ast.BinOp):
            ops = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/'}
            if type(node.op) not in ops:
                raise Untranslatable(f'operator {type(node.op).__name__}')
            return f'( {self.value(node.left)} {ops[type(node.op)]} {self.value(node.right)} )'
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return f'-{self.value(node.operand)}'
        raise Untranslatable(f'{type(node).__name__} expression')

    def condition(self, node):
        """An FB BOOL expression."""
        if isinstance(node, ast.BoolOp):
            op = ' && ' if isinstance(node.op, ast.And) else ' || '
            return '( ' + op.join(self.condition(v) for v in node.values) + ' )'
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return f'( {self.condition(node.operand)} == NO )'
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            left, op, right = node.left, node.ops[0], node.comparators[0]
            if isinstance(op, (ast.Is, ast.IsNot)) and isinstance(right, ast.Constant) and right.value is None:
                ref = self.attr_ref(left)
                if not ref:
                    raise Untranslatable('"is None" on something other than an attribute')
                attr, role = ref
                if role:
                    owner = self.parent_entity(role)
                    test = f'fn DataIsNull( fn LogicParentValue( logicRow, {fb_string(role)}, {fb_string(attr)} ) )'
                else:
                    owner = self.entity
                    test = f'fn LogicIsEmpty( logicRow, {fb_string(attr)} )'
                if not self.model.has(owner, attr):
                    raise Untranslatable(f'{owner} has no attribute {attr}')
                return test if isinstance(op, ast.Is) else f'( {test} == NO )'
            numeric = self.is_numeric(left) or self.is_numeric(right)
            if numeric:
                ops = {ast.Lt: '<', ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>=', ast.Eq: '==', ast.NotEq: '!='}
                if type(op) not in ops:
                    raise Untranslatable(f'comparison {type(op).__name__}')
                return f'( {self.value(left)} {ops[type(op)]} {self.value(right)} )'
            if isinstance(op, (ast.Eq, ast.NotEq)):
                test = f'fn StringIsEqual( {self.value(left)}, {self.value(right)} )'
                return test if isinstance(op, ast.Eq) else f'( {test} == NO )'
            raise Untranslatable('ordering comparison of text')
        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return 'YES' if node.value else 'NO'
        ref = self.attr_ref(node)
        if ref:      # a bare boolean attribute
            return f'( {self.value(node)} != 0 )'
        raise Untranslatable(f'{type(node).__name__} condition')

    def formula(self, node, target_attr):
        """The value a formula returns, as a Cocoa object (CFTypeRef)."""
        if self.model.numeric(self.entity, target_attr):
            return f'fn NumberWithDouble( {self.value(node)} )'
        return self.value(node)

    def dependencies(self, node):
        deps = []
        for sub in ast.walk(node):
            ref = self.attr_ref(sub)
            if ref and not (isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name) and self.attr_ref(sub)
                            and any(self.attr_ref(p) and p is not sub and getattr(p, 'value', None) is sub for p in ast.walk(node))):
                attr, role = ref
                name = f'{role}.{attr}' if role else attr
                if name not in deps:
                    deps.append(name)
        return deps


# ------------------------------------------------------------------ FB -> dependencies (also for hand-edited rules)

DEP_RE = re.compile(r'fn Logic(?:Value|Double|Long|String|IsEmpty|OldValue|Changed)\(\s*logicRow\s*,\s*@"([^"]+)"\s*\)')
PDEP_RE = re.compile(r'fn LogicParent(?:Value|Double|String)\(\s*logicRow\s*,\s*@"([^"]+)"\s*,\s*@"([^"]+)"\s*\)')


def fb_dependencies(code):
    deps = []
    for m in PDEP_RE.finditer(code or ''):
        name = f'{m.group(1)}.{m.group(2)}'
        if name not in deps:
            deps.append(name)
    for m in DEP_RE.finditer(code or ''):
        if m.group(1) not in deps:
            deps.append(m.group(1))
    return deps


# ------------------------------------------------------------------ FB -> Python (export)

def fb_to_python(code):
    """Read back the FB the importer writes. Raises Untranslatable for anything else."""
    s = code
    s = re.sub(r'fn LogicParent(?:Double|String|Value)\(\s*logicRow\s*,\s*@"([^"]+)"\s*,\s*@"([^"]+)"\s*\)', r'row.\1.\2', s)
    s = re.sub(r'fn DataIsNull\(\s*(row\.\w+\.\w+)\s*\)', r'(\1 is None)', s)
    s = re.sub(r'fn LogicIsEmpty\(\s*logicRow\s*,\s*@"([^"]+)"\s*\)', r'(row.\1 is None)', s)
    s = re.sub(r'fn Logic(?:Double|String|Value|Long)\(\s*logicRow\s*,\s*@"([^"]+)"\s*\)', r'row.\1', s)
    for _ in range(5):
        s = re.sub(r'fn NumberWithDouble\(\s*(.*)\s*\)\s*$', r'\1', s)
        s = re.sub(r'fn StringIsEqual\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)', r'(\1 == \2)', s)
    s = re.sub(r'\(\s*(.+?)\s*==\s*NO\s*\)', r'(not \1)', s)
    s = s.replace('&&', 'and').replace('||', 'or').replace('YES', 'True').replace('NO', 'False')
    s = re.sub(r'@"((?:[^"\\]|\\.)*)"', lambda m: json.dumps(m.group(1).replace('\\"', '"').replace('\\\\', '\\')), s)
    if 'fn ' in s or 'logicRow' in s:
        raise Untranslatable('FB the translator cannot read back')
    ast.parse(s, mode='eval')          # must be a Python expression
    return s


# ------------------------------------------------------------------ declare_logic.py -> rules

def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.insert(0, node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.insert(0, node.id)
    return parts


def class_attr(node):
    """models.Customer.Balance / Customer.Balance -> ('Customer', 'Balance')"""
    parts = [p for p in dotted(node) if p != 'models']
    return (parts[-2], parts[-1]) if len(parts) >= 2 else (None, None)


def class_name(node):
    parts = [p for p in dotted(node) if p != 'models']
    return parts[-1] if parts else None


def lambda_body(node):
    if isinstance(node, ast.Lambda) and len(node.args.args) >= 1 and node.args.args[0].arg == 'row':
        return node.body
    return None


def import_rules(source, model):
    tree = ast.parse(source)
    rules, counter = [], {}

    def new(kind, entity, **fields):
        counter[kind] = counter.get(kind, 0) + 1
        rule = {'id': f'{kind}-{entity}-{fields.get("attr") or fields.get("role") or fields.get("list") or counter[kind]}',
                'kind': kind, 'entity': entity, 'enabled': True}
        rule.update(fields)
        rules.append(rule)
        return rule

    for call in [n for n in ast.walk(tree) if isinstance(n, ast.Call)]:
        func = call.func
        if not (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == 'Rule'):
            continue
        kind, kw = func.attr, {k.arg: k.value for k in call.keywords}
        src = ast.get_source_segment(source, call)
        try:
            if kind in ('sum', 'count'):
                parent, attr = class_attr(kw['derive'])
                if kind == 'sum':
                    child, child_attr = class_attr(kw['as_sum_of'])
                else:
                    child, child_attr = class_name(kw['as_count_of']), None
                lists = model.lists_to(parent, child)
                role_name = kw.get('child_role_name')
                list_name = role_name.value if isinstance(role_name, ast.Constant) and role_name.value else None
                if list_name is None:
                    if len(lists) != 1:
                        raise Untranslatable(f'{parent} has {len(lists)} child lists of {child}: name one (child_role_name)')
                    list_name = lists[0]['name']
                rule = new(kind, parent, attr=attr, list=list_name, childAttr=child_attr, source=src)
                if 'where' in kw:
                    body = lambda_body(kw['where'])
                    if body is None:
                        raise Untranslatable('where is not a lambda')
                    rule['where'] = ToFB(model, child).condition(body)
            elif kind == 'formula':
                entity, attr = class_attr(kw['derive'])
                rule = new('formula', entity, attr=attr, source=src)
                body = lambda_body(kw.get('as_expression'))
                if body is None:
                    raise Untranslatable('the formula calls a Python function (calling=)')
                tr = ToFB(model, entity)
                rule['expression'] = tr.formula(body, attr)
                rule['dependsOn'] = fb_dependencies(rule['expression'])
            elif kind == 'copy':
                entity, attr = class_attr(kw['derive'])
                parent, parent_attr = class_attr(kw['from_parent'])
                roles = model.roles_to(entity, parent)
                if len(roles) != 1:
                    raise Untranslatable(f'{entity} has {len(roles)} roles to {parent}')
                new('copy', entity, attr=attr, role=roles[0]['name'], parentAttr=parent_attr, source=src)
            elif kind == 'constraint':
                entity = class_name(kw['validate'])
                msg = kw.get('error_msg')
                message = msg.value if isinstance(msg, ast.Constant) else f'{entity} constraint failed'
                rule = new('constraint', entity, message=message, source=src)
                body = lambda_body(kw.get('as_condition'))
                if body is None:
                    raise Untranslatable('the constraint calls a Python function (calling=)')
                rule['condition'] = ToFB(model, entity).condition(body)
            elif kind == 'parent_check':
                entity = class_name(kw['validate'])
                msg = kw.get('error_msg')
                for role in [r for r in model.entities.get(entity, {}).get('relationships', []) if r['direction'] == 'toone']:
                    new('parentCheck', entity, role=role['name'],
                        message=msg.value if isinstance(msg, ast.Constant) else f'The {role["name"]} does not exist', source=src)
            elif kind in ('row_event', 'commit_row_event', 'after_flush_row_event', 'early_row_event'):
                entity = class_name(kw['on_class'])
                rule = new('commitEvent' if kind != 'row_event' and kind != 'early_row_event' else 'rowEvent', entity,
                           body='// rewrite in FB', source=src)
                raise Untranslatable('events are Python code: rewrite the body in FB')
            else:
                new('unknown', '?', source=src, enabled=False, note=f'Rule.{kind} is not supported')
        except Untranslatable as e:
            rules[-1]['enabled'] = False
            rules[-1]['note'] = f'Not translated: {e}. Rewrite it in FB, then switch it on.'
            if 'source' not in rules[-1]:
                rules[-1]['source'] = src
        except (KeyError, AttributeError, TypeError) as e:
            new('unknown', '?', source=src, enabled=False, note=f'Could not read this rule ({type(e).__name__}: {e})')
    for r in rules:
        r['imported'] = {k: r.get(k) for k in ('expression', 'condition', 'where')}
    return rules


# ------------------------------------------------------------------ check

def check(rules, model):
    problems = []

    def bad(rule, text):
        problems.append({'id': rule.get('id'), 'message': text})

    formulas = {}
    for r in rules:
        if not r.get('enabled', True):
            continue
        kind, entity = r.get('kind'), r.get('entity')
        if kind not in KINDS:
            bad(r, f'unknown kind {kind}')
            continue
        if not model.has(entity):
            bad(r, f'{entity} is not in the model')
            continue
        if kind in ('formula', 'sum', 'count', 'copy') and not model.has(entity, r.get('attr')):
            bad(r, f'{entity}.{r.get("attr")} is not in the model')
        if kind in ('sum', 'count', 'deleteAction'):
            rel = model.relationship(entity, r.get('list'))
            if rel is None or rel['direction'] != 'tomany':
                bad(r, f'{entity} has no child list {r.get("list")}')
            elif kind == 'sum' and not model.has(rel['resource'], r.get('childAttr')):
                bad(r, f'{rel["resource"]}.{r.get("childAttr")} is not in the model')
        if kind in ('copy', 'parentCheck'):
            rel = model.relationship(entity, r.get('role'))
            if rel is None or rel['direction'] != 'toone':
                bad(r, f'{entity} has no parent role {r.get("role")}')
            elif kind == 'copy' and not model.has(rel['resource'], r.get('parentAttr')):
                bad(r, f'{rel["resource"]}.{r.get("parentAttr")} is not in the model')
        if kind == 'deleteAction' and r.get('action') not in ('prevent', 'cascade', 'nullify'):
            bad(r, f'delete action {r.get("action")}: use prevent, cascade or nullify')
        if kind == 'formula':
            r['dependsOn'] = fb_dependencies(r.get('expression'))
            for d in r['dependsOn']:
                if '.' in d:
                    role, attr = d.split('.', 1)
                    rel = model.relationship(entity, role)
                    if rel is None or not model.has(rel['resource'], attr):
                        bad(r, f'{entity} formula reads {d}, which is not in the model')
                elif not model.has(entity, d):
                    bad(r, f'{entity} formula reads {d}, which is not in the model')
            formulas.setdefault(entity, []).append(r)
        for field in ('expression', 'condition', 'where'):
            if field in r and not (r[field] or '').strip():
                bad(r, f'{field} is empty')
    for entity, fs in formulas.items():       # cycles, as LogicActivate checks them
        derived = [f['attr'] for f in fs]
        progress = True
        ordered = []
        while progress and len(ordered) < len(fs):
            progress = False
            for f in fs:
                if f['attr'] in derived and all(d == f['attr'] or d not in derived for d in f['dependsOn']):
                    ordered.append(f)
                    derived.remove(f['attr'])
                    progress = True
        if derived:
            problems.append({'id': None, 'message': f'{entity} formulas depend on each other in a cycle: {", ".join(derived)}'})
    return problems


# ------------------------------------------------------------------ generate FB

def fb_name(*parts):
    return ''.join(re.sub(r'[^A-Za-z0-9]', '', p[:1].upper() + p[1:]) for p in parts if p)


def generate(rules, title='the project'):
    out = [f'/*\n *   Studio Rules.incl - {title}\n *',
           ' *   Generated by App Builder for FutureBasic from the project\'s Rules.json.',
           ' *   Regenerating overwrites this file: change rules on the Rules page, or write your',
           ' *   own in Rules.incl (DeclareRules), which is never overwritten.\n */\n']
    declare, used = [], set()

    def unique(name):
        base, n = name, 2
        while name in used:
            name, n = f'{base}{n}', n + 1
        used.add(name)
        return name

    for r in rules:
        kind, entity = r['kind'], r['entity']
        title_line = r.get('title') or r['id']
        if not r.get('enabled', True):
            out.append(f'// switched off: {title_line}' + (f' - {r["note"]}' if r.get('note') else '') + '\n')
            continue
        if kind == 'formula':
            fn = unique(fb_name(entity, r['attr'], 'Formula'))
            out.append(f'// {title_line}\nlocal fn {fn}( logicRow as LogicRowRef ) as CFTypeRef\nend fn = {r["expression"]}\n')
            deps = ', '.join(fb_string(d) for d in fb_dependencies(r['expression']))
            declare.append(f'fn LogicFormula( {fb_string(entity)}, {fb_string(r["attr"])}, @fn {fn}, @[ {deps} ] )' if deps
                           else f'fn LogicFormula( {fb_string(entity)}, {fb_string(r["attr"])}, @fn {fn}, @[] )')
        elif kind == 'constraint':
            fn = unique(fb_name(entity, r['id'], 'Constraint'))
            out.append(f'// {title_line}\nlocal fn {fn}( logicRow as LogicRowRef ) as BOOL\nend fn = {r["condition"]}\n')
            declare.append(f'fn LogicConstraint( {fb_string(entity)}, @fn {fn}, {fb_string(r.get("message") or "")} )')
        elif kind in ('sum', 'count'):
            where = 'NULL'
            if r.get('where'):
                fn = unique(fb_name(entity, r['attr'], 'Where'))
                out.append(f'// which children count for {entity}.{r["attr"]}\nlocal fn {fn}( logicRow as LogicRowRef ) as BOOL\nend fn = {r["where"]}\n')
                where = f'@fn {fn}'
            if kind == 'sum':
                declare.append(f'fn LogicSum( {fb_string(entity)}, {fb_string(r["attr"])}, {fb_string(r["list"])}, {fb_string(r["childAttr"])}, {where} )')
            else:
                declare.append(f'fn LogicCount( {fb_string(entity)}, {fb_string(r["attr"])}, {fb_string(r["list"])}, {where} )')
        elif kind == 'copy':
            declare.append(f'fn LogicCopy( {fb_string(entity)}, {fb_string(r["attr"])}, {fb_string(r["role"])}, {fb_string(r["parentAttr"])} )')
        elif kind == 'parentCheck':
            declare.append(f'fn LogicParentCheck( {fb_string(entity)}, {fb_string(r["role"])}, {fb_string(r.get("message") or "")} )')
        elif kind == 'deleteAction':
            declare.append(f'fn LogicDeleteAction( {fb_string(entity)}, {fb_string(r["list"])}, {fb_string(r["action"])}, {fb_string(r["message"]) if r.get("message") else "NULL"} )')
        elif kind in ('rowEvent', 'commitEvent'):
            fn = unique(fb_name(entity, r['id'], 'Event'))
            body = (r.get('body') or '').replace('\r\n', '\n').strip('\n')
            out.append(f'// {title_line}\nvoid local fn {fn}( logicRow as LogicRowRef )\n{body}\nend fn\n')
            declare.append(f'fn Logic{"RowEvent" if kind == "rowEvent" else "CommitEvent"}( {fb_string(entity)}, @fn {fn} )')
    out.append('\nvoid local fn DeclareStudioRules\n' + ''.join(d + '\n' for d in declare) + 'end fn\n')
    return '\n'.join(out)


# ------------------------------------------------------------------ export

def export(rules):
    lines = ['"""', 'Business rules exported by App Builder for FutureBasic.', '"""',
             'from logic_bank.logic_bank import Rule', 'from database import models', '', '',
             'def declare_logic():']
    for r in rules:
        kind, entity = r['kind'], r['entity']
        unchanged = r.get('source') and all(r.get(k) == (r.get('imported') or {}).get(k) for k in ('expression', 'condition', 'where'))
        if unchanged and r.get('enabled', True):
            lines.append('    ' + r['source'].replace('\n', '\n    '))
            continue
        try:
            if not r.get('enabled', True):
                raise Untranslatable(r.get('note') or 'switched off')
            if kind == 'formula':
                lines.append(f'    Rule.formula(derive=models.{entity}.{r["attr"]}, as_expression=lambda row: {fb_to_python(r["expression"])})')
            elif kind == 'constraint':
                lines.append(f'    Rule.constraint(validate=models.{entity}, as_condition=lambda row: {fb_to_python(r["condition"])}, '
                             f'error_msg={json.dumps(r.get("message") or "")})')
            elif kind in ('sum', 'count'):
                where = f', where=lambda row: {fb_to_python(r["where"])}' if r.get('where') else ''
                if kind == 'sum':
                    lines.append(f'    Rule.sum(derive=models.{entity}.{r["attr"]}, as_sum_of={r["list"]}:{r["childAttr"]}{where})')
                else:
                    lines.append(f'    Rule.count(derive=models.{entity}.{r["attr"]}, as_count_of={r["list"]}:{where})')
            elif kind == 'copy':
                lines.append(f'    Rule.copy(derive=models.{entity}.{r["attr"]}, from_parent={r["role"]}:{r["parentAttr"]})')
            elif kind == 'parentCheck':
                lines.append(f'    Rule.parent_check(validate=models.{entity}, error_msg={json.dumps(r.get("message") or "")})')
            else:
                raise Untranslatable(f'{kind} has no LogicBank form here')
        except Untranslatable as e:
            lines.append(f'    # {r.get("id")}: not exported ({e}). FB:')
            for k in ('expression', 'condition', 'where', 'body'):
                if r.get(k):
                    lines.append('    #     ' + r[k].replace('\n', '\n    #     '))
    lines.append('    pass')
    return '\n'.join(lines) + '\n'


def resolve_export(text, rules, model):
    """Replace the List:attr placeholders with models.<Child>.<attr> (export writes them first)."""
    def child_ref(entity, name, attr):
        rel = model.relationship(entity, name)
        if rel is None:
            return f'models.UNKNOWN_{name}'
        return f'models.{rel["resource"]}.{attr}' if attr else f'models.{rel["resource"]}'

    out = []
    for line in text.split('\n'):
        m = re.search(r'Rule\.(sum|count|copy)\(derive=models\.(\w+)\.(\w+), (as_sum_of|as_count_of|from_parent)=(\w+):(\w*)', line)
        if m:
            kind, entity, _, key, name, attr = m.groups()
            if kind == 'copy':      # from_parent names the parent role: the parent class
                rel = model.relationship(entity, name)
                ref = f'models.{rel["resource"]}.{attr}' if rel else f'models.UNKNOWN_{name}'
            else:
                ref = child_ref(entity, name, attr if kind != 'count' else None)
            extra = f', child_role_name="{name}"' if kind in ('sum', 'count') and len(model.lists_to(entity, model.relationship(entity, name)['resource'] if model.relationship(entity, name) else '')) > 1 else ''
            line = line.replace(f'{key}={name}:{attr}', f'{key}={ref}{extra}', 1)
        out.append(line)
    return '\n'.join(out)


# ------------------------------------------------------------------ files

def load_rules(path):
    if not os.path.exists(path):
        return {'version': 1, 'rules': []}
    with open(path) as f:
        return json.load(f)


def save_rules(path, doc):
    with open(path, 'w') as f:
        json.dump(doc, f, indent=2)
        f.write('\n')


def arg(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        return argv[i + 1] if i + 1 < len(argv) else default
    return default


def main(argv):
    if not argv or argv[0] in ('-h', '--help', 'help'):
        print(__doc__)
        return 0
    if argv[0] == '--test':
        return self_test(argv[1])
    command = argv[0]
    model = Model(arg(argv, '--model'))
    rules_path = arg(argv, '--rules')
    doc = load_rules(rules_path)
    if command == 'import':
        with open(argv[1]) as f:
            imported = import_rules(f.read(), model)
        by_id = {r['id']: i for i, r in enumerate(doc['rules'])}
        for r in imported:
            if r['id'] in by_id:
                doc['rules'][by_id[r['id']]] = r
            else:
                doc['rules'].append(r)
        check(doc['rules'], model)
        save_rules(rules_path, doc)
        off = [r for r in imported if not r.get('enabled', True)]
        print(json.dumps({'imported': len(imported), 'switchedOff': len(off),
                          'notes': [{'id': r['id'], 'note': r.get('note')} for r in off]}, indent=2))
        return 0
    if command == 'check':
        problems = check(doc['rules'], model)
        save_rules(rules_path, doc)        # dependsOn filled in
        print(json.dumps({'ok': not problems, 'problems': problems}, indent=2))
        return 0 if not problems else 1
    if command == 'generate':
        problems = check([r for r in doc['rules']], model)
        if problems:
            print(json.dumps({'ok': False, 'problems': problems}, indent=2))
            return 1
        with open(arg(argv, '--out'), 'w', newline='') as f:
            f.write(generate(doc['rules']).replace('\n', '\r'))
        print(json.dumps({'ok': True, 'rules': len(doc['rules'])}))
        return 0
    if command == 'export':
        with open(arg(argv, '--out'), 'w') as f:
            f.write(resolve_export(export(doc['rules']), doc['rules'], model))
        print(json.dumps({'ok': True, 'rules': len(doc['rules'])}))
        return 0
    print(__doc__)
    return 2


# ------------------------------------------------------------------ self test

NORTHWIND_LOGIC = '''
from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """The check-credit use case (ApiLogicServer's Northwind sample, readme_logic.md)."""
    Rule.constraint(validate=models.Customer,
                    as_condition=lambda row: row.Balance <= row.CreditLimit,
                    error_msg="Customer balance ({row.Balance}) exceeds credit limit ({row.CreditLimit})")
    Rule.sum(derive=models.Customer.Balance, as_sum_of=models.Order.AmountTotal,
             where=lambda row: row.ShippedDate is None)
    Rule.count(derive=models.Customer.UnpaidOrderCount, as_count_of=models.Order,
               where=lambda row: row.ShippedDate is None)
    Rule.sum(derive=models.Order.AmountTotal, as_sum_of=models.OrderDetail.Amount)
    Rule.formula(derive=models.OrderDetail.Amount, as_expression=lambda row: row.Quantity * row.UnitPrice)
    Rule.copy(derive=models.OrderDetail.UnitPrice, from_parent=models.Product.UnitPrice)
    Rule.formula(derive=models.OrderDetail.ShippedDate, as_expression=lambda row: row.Order.ShippedDate)
    Rule.constraint(validate=models.Order, as_condition=lambda row: not (row.Country == "x"), error_msg="no x")
    Rule.formula(derive=models.Order.Freight, as_expression=lambda row: 5 if row.AmountTotal > 100 else 10)
    Rule.commit_row_event(on_class=models.Order, calling=congratulate_sales_rep)
'''


def self_test(db):
    import shutil
    import subprocess
    import tempfile
    results = []

    def ok(name, cond, detail=''):
        results.append((name, bool(cond), detail))

    model = Model(db)
    rules = import_rules(NORTHWIND_LOGIC, model)
    by = {(r['kind'], r['entity'], r.get('attr')): r for r in rules}
    ok('import: 10 LogicBank rules read', len(rules) == 10, [r['id'] for r in rules])
    f = by.get(('formula', 'OrderDetail', 'Amount'))
    ok('formula translated to FB', f and f['enabled'] and f['expression'] ==
       'fn NumberWithDouble( ( fn LogicDouble( logicRow, @"Quantity" ) * fn LogicDouble( logicRow, @"UnitPrice" ) ) )', f and f.get('expression'))
    ok('formula dependencies found', f and f['dependsOn'] == ['Quantity', 'UnitPrice'], f and f.get('dependsOn'))
    s = by.get(('sum', 'Customer', 'Balance'))
    ok('sum: child list found from the model, where translated', s and s['list'] == 'OrderList' and s['childAttr'] == 'AmountTotal'
       and s['where'] == 'fn LogicIsEmpty( logicRow, @"ShippedDate" )', s)
    c = by.get(('count', 'Customer', 'UnpaidOrderCount'))
    ok('count read', c and c['list'] == 'OrderList' and c['where'] == 'fn LogicIsEmpty( logicRow, @"ShippedDate" )', c)
    cp = by.get(('copy', 'OrderDetail', 'UnitPrice'))
    ok('copy: parent role found from the model', cp and cp['role'] == 'Product' and cp['parentAttr'] == 'UnitPrice', cp)
    pr = by.get(('formula', 'OrderDetail', 'ShippedDate'))
    ok('parent reference translated, dependency Order.ShippedDate', pr and pr['enabled'] and pr['dependsOn'] == ['Order.ShippedDate'], pr)
    cons = [r for r in rules if r['kind'] == 'constraint' and r['entity'] == 'Customer'][0]
    ok('constraint and its message', cons['condition'] == '( fn LogicDouble( logicRow, @"Balance" ) <= fn LogicDouble( logicRow, @"CreditLimit" ) )'
       and '{row.Balance}' in cons['message'], cons)
    tx = [r for r in rules if r['kind'] == 'constraint' and r['entity'] == 'Order'][0]
    ok('text comparison and not', tx['condition'] == '( fn StringIsEqual( fn LogicString( logicRow, @"Country" ), @"x" ) == NO )', tx['condition'])
    fr = by.get(('formula', 'Order', 'Freight'))
    ok('conditional expression switched off, Python kept', fr and not fr['enabled'] and 'IfExp' in fr['note'] and 'row.AmountTotal' in fr['source'], fr)
    ev = [r for r in rules if r['kind'] == 'commitEvent'][0]
    ok('event switched off with its Python kept', not ev['enabled'] and 'congratulate_sales_rep' in ev['source'], ev)
    ok('check: no problems in the enabled rules', check(rules, model) == [], check(rules, model))

    bad = [dict(f, id='bad', attr='NoSuch'), dict(f, id='cyc1', attr='Discount', expression='fn NumberWithDouble( fn LogicDouble( logicRow, @"Amount" ) )'),
           dict(f, id='cyc2', expression='fn NumberWithDouble( fn LogicDouble( logicRow, @"Discount" ) )')]
    probs = check(bad, model)
    ok('check: unknown attribute and a cycle reported', any('NoSuch' in p['message'] for p in probs) and any('cycle' in p['message'] for p in probs), probs)

    work = tempfile.mkdtemp()
    try:
        fb = generate(rules, 'Northwind')
        path = os.path.join(work, 'Studio Rules.incl')
        with open(path, 'w', newline='') as fh:
            fh.write(fb.replace('\n', '\r'))
        for name in os.listdir(os.path.join(os.path.dirname(HERE), 'src', 'Runtime')):
            shutil.copy(os.path.join(os.path.dirname(HERE), 'src', 'Runtime', name), work)
        headers = os.path.join(os.path.dirname(db), '..', '..', 'Toolboxes', 'Headers')
        lint = subprocess.run([sys.executable, os.path.join(HERE, 'fblint.py')] + (['--headers', headers] if os.path.isdir(headers) else [])
                              + [path] + [os.path.join(work, n) for n in os.listdir(work) if n.startswith(('Logic', 'Data'))],
                              capture_output=True, text=True)
        ok('generate: Studio Rules.incl lints clean with the runtime', lint.returncode == 0, lint.stdout[-400:])
        ok('generate: DeclareStudioRules registers the enabled rules',
           'void local fn DeclareStudioRules' in fb and 'fn LogicSum( @"Customer", @"Balance", @"OrderList", @"AmountTotal", @fn CustomerBalanceWhere )' in fb
           and 'fn LogicCopy( @"OrderDetail", @"UnitPrice", @"Product", @"UnitPrice" )' in fb and '// switched off:' in fb, fb[-900:])

        py = resolve_export(export(rules), rules, model)
        ok('export: unchanged imported rules are written as they came', 'as_expression=lambda row: row.Quantity * row.UnitPrice' in py)
        edited = [dict(r) for r in rules]
        for r in edited:
            if r['kind'] == 'formula' and r['attr'] == 'Amount':
                r['expression'] = 'fn NumberWithDouble( ( fn LogicDouble( logicRow, @"Quantity" ) * ( fn LogicDouble( logicRow, @"UnitPrice" ) - 1.0 ) ) )'
        py2 = resolve_export(export(edited), edited, model)
        ok('export: an edited rule is translated back from its FB', 'lambda row: ( row.Quantity * ( row.UnitPrice - 1.0 ) )' in py2, py2)
        ok('export: sum and count name the child class', 'as_sum_of=models.Order.AmountTotal' in py2 and 'as_count_of=models.Order' in py2, py2)
        ok('export: the file is valid Python', compile(py2, 'declare_logic.py', 'exec') is not None)
        again = import_rules(py2, model)
        a1 = [r for r in again if r['kind'] == 'formula' and r['attr'] == 'Amount'][0]
        ok('round trip: export then import gives the same FB', a1['expression'].replace(' ', '') ==
           [r for r in edited if r['kind'] == 'formula' and r['attr'] == 'Amount'][0]['expression'].replace(' ', ''), a1['expression'])
        ok('round trip: the same enabled rules', sorted((r['kind'], r['entity'], r.get('attr')) for r in again if r['enabled']) ==
           sorted((r['kind'], r['entity'], r.get('attr')) for r in rules if r['enabled']))

        rules_json = os.path.join(work, 'Rules.json')
        logic_py = os.path.join(work, 'declare_logic.py')
        with open(logic_py, 'w') as fh:
            fh.write(NORTHWIND_LOGIC)
        run = subprocess.run([sys.executable, os.path.join(HERE, 'rules_bridge.py'), 'import', logic_py, '--model', db, '--rules', rules_json],
                             capture_output=True, text=True)
        ok('command line: import writes Rules.json', run.returncode == 0 and len(load_rules(rules_json)['rules']) == 10, run.stdout + run.stderr)
        run = subprocess.run([sys.executable, os.path.join(HERE, 'rules_bridge.py'), 'generate', '--rules', rules_json, '--model', db,
                              '--out', os.path.join(work, 'gen.incl')], capture_output=True, text=True)
        ok('command line: generate writes FB with CR line endings', run.returncode == 0 and '\n' not in open(os.path.join(work, 'gen.incl'), newline='').read(),
           run.stdout + run.stderr)
    finally:
        shutil.rmtree(work)

    for name, passed, detail in results:
        print(('PASS  ' if passed else 'FAIL  ') + name + ('' if passed or detail == '' else f'   [{detail}]'))
    failed = sum(1 for _, p, _ in results if not p)
    print(f'rules_bridge: {len(results)} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
