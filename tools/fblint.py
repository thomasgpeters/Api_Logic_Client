#!/usr/bin/env python3
"""
fblint - check FutureBasic sources against the rules in docs/reference/FB Coding Rules.md.

Run it on this repo's FB code and on every generated project before a build:

    python3 tools/fblint.py src
    python3 tools/fblint.py ~/ApiLogicClient/"Northwind Project"
    python3 tools/fblint.py --headers ../FutureBasic_Documentation/Toolboxes/Headers src

Arguments are files or folders (.incl, .glbl, .main, .fb, .bas are checked).
With --headers, every `fn Name` / `Name(` call must exist in the toolbox headers
or be defined in the checked files.  Exit status is 1 when anything is reported.
"""
import glob, os, re, sys

FB_EXT = ('.incl', '.glbl', '.main', '.fb', '.bas')
DEPRECATED = [
    (re.compile(r'^\s*globals\s+"'), 'globals "file" is deprecated - use include (or the project file order)'),
    (re.compile(r'\bproc\s+"'), 'proc "Name" is deprecated - use @fn Name'),
    (re.compile(r'^\s*def(sng|dbl|int|long)\s+[a-z]'), 'defsng/defdbl/defint/deflong letter ranges are deprecated'),
    (re.compile(r'^\s*defstr\s+[a-z](\s*-\s*[a-z])?\s*(,|$)', re.I), 'defstr letter ranges are deprecated'),
    (re.compile(r'\bindex\$'), 'index$ arrays are deprecated - use CFArray or mda'),
    (re.compile(r'\bTextLabel(WithTag|Exists)\b'), 'TextLabelWithTag/TextLabelExists are deprecated - use TextFieldWithTag/TextFieldExists'),
]


def comment_apostrophe(line):
    """Index of a ' that starts a comment (outside strings), or -1."""
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c == '"':
            j = i + 1
            while j < n:
                if line[j] == '\\' and i > 0 and line[i - 1] == '@':
                    j += 2; continue
                if line[j] == '"':
                    if j + 1 < n and line[j + 1] == '"':
                        j += 2; continue
                    break
                j += 1
            i = j + 1; continue
        if line.startswith('//', i) or line.startswith('/*', i):
            return -1
        if c == "'":
            return i
        i += 1
    return -1


def code_lines(text):
    """Yield (line_no, line) for FB code: skips /* */ blocks and BeginC..EndC blocks."""
    in_block = in_c = False
    for no, line in enumerate(text.split('\n'), 1):
        s = line.strip()
        if in_block:
            if '*/' in line: in_block = False
            continue
        if in_c:
            if re.match(r'(?i)^\s*EndC\b', line): in_c = False
            continue
        if re.match(r'(?i)^\s*Begin(CCode|CDeclaration|CFunction)\b', line):
            in_c = True; continue
        if s.startswith('/*'):
            if '*/' not in s: in_block = True
            continue
        yield no, line


def strip_strings_and_comments(line):
    line = re.sub(r'@?"(?:[^"\\]|\\.|"")*"', '""', line)
    return line.split('//')[0]


FN_DEF = re.compile(r'^\s*(?:(void)\s+|(\w+)\s+)?local\s+fn\s+(\w+)(\s*\(.*?\))?(.*)$')


def lint_file(path, is_project_file, known_toolbox, local_fns, fb_keywords=frozenset(), arity=None):
    raw = open(path, 'rb').read()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('mac_roman')
    problems = []
    def report(no, msg): problems.append(f'{path}:{no}: {msg}')

    if '\n' in text.replace('\r\n', ''):
        report(1, 'LF line endings - FB sources use CR')
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    current = None            # (name, returns_type, def_line)
    for no, line in code_lines(text):
        if re.match(r'(?i)^\s*cln\b', line):
            continue
        if re.match(r"^\s*'~'\d*\s*$", line):
            report(no, "'~'1 divider line - delete it (no longer supported)")
            continue
        if comment_apostrophe(line) >= 0:
            report(no, "' comment - use //")
        if is_project_file and re.match(r'^\s*#build\b', line):
            report(no, '#build is not supported in projects - use Build Settings')
        for rx, msg in DEPRECATED:
            if rx.search(line): report(no, msg)
        wm = re.search(r'\b(View\w+)\(\s*(_\w*(?:[Ww]indow|[Ww]nd)\w*)\s*[,)]', strip_strings_and_comments(line))
        if wm and 'ContentView' not in wm.group(2):
            report(no, f'{wm.group(1)} takes a view tag, but {wm.group(2)} looks like a window tag - '
                       f'use _windowContentViewTag for the window\'s content view')

        code_only = strip_strings_and_comments(line)
        if re.match(r'\s*for\s+\w+\s+in\s+(fn\b|@\[)', code_only):
            report(no, 'for ... in needs an array variable, not an expression - assign it first')
        if fb_keywords:
            declared = [d for d in re.findall(r'\b(\w+)\s+as\s+\w', code_only) if d.lower() != 'dim']
            dm = re.match(r'\s*(?:[A-Z]\w*Ref|long|BOOL|double|NSInteger|NSUInteger|SInt64|SInt32|ptr|CGRect|CGFloat|CFRange)\s+(.*)$', code_only)
            if dm and not re.search(r'\blocal\s+fn\b', code_only):
                declared += [re.match(r'\s*(\w+)', part).group(1) for part in dm.group(1).split(',') if re.match(r'\s*\w+', part)]
            fm = re.match(r'\s*for\s+(\w+)\s+in\b', code_only)
            if fm: declared.append(fm.group(1))
            for name in declared:
                if name.lower() in fb_keywords:
                    report(no, f'"{name}" is an FB keyword - rename the variable')
        if arity:
            for cm in re.finditer(r'\bfn\s+(\w+)\s*\(', code_only):
                name = cm.group(1).lower()
                if name in arity and name not in local_fns:
                    depth, j = 1, cm.end()
                    while j < len(code_only) and depth:
                        depth += {'(': 1, ')': -1}.get(code_only[j], 0); j += 1
                    if depth == 0:
                        given = len(split_args(code_only[cm.end():j - 1]))
                        expected, variadic = arity[name]
                        if given != expected and not ( variadic and given >= expected ):
                            report(no, f'{cm.group(1)} takes {expected} argument(s) (per the headers); {given} given')
        m = FN_DEF.match(line)
        if m:
            void, prefix_type, name, _params, tail = m.groups()
            tail = tail.split('//')[0]
            typed = bool(prefix_type) or bool(re.search(r'\bas\s+\w', tail))
            current = (name, typed and not void, no)
            continue
        if current and re.match(r'\s*(end\s+fn|exit\s+fn|return)\s*=?\s*\S', line) \
                and not re.match(r'\s*end\s+fn\s*$', line):
            name, returns, def_no = current
            if not returns:
                report(no, f'fn {name} (line {def_no}) returns a value but declares no return type '
                           f'(FB 7.1.4+: add "as Type" or make it void)')
        if current and re.match(r'\s*end\s+fn\b', line):
            current = None

        if known_toolbox is not None and not re.match(r'(?i)^\s*(toolbox|system|#define)\b', line):
            code = strip_strings_and_comments(line)
            names = re.findall(r'\bfn\s+(\w+)', code)
            call = re.match(r'\s*([A-Z]\w+)\s*\(', code)
            if call: names.append(call.group(1))
            for n in names:
                if n.lower() not in known_toolbox and n.lower() not in local_fns:
                    report(no, f'{n} is not in the toolbox headers or this code')
    return problems


def collect(args):
    files = []
    for a in args:
        if os.path.isdir(a):
            for p in sorted(glob.glob(os.path.join(a, '**', '*'), recursive=True)):
                if p.endswith(FB_EXT) and '/build_temp' not in p: files.append(p)
        elif a.endswith(FB_EXT):
            files.append(a)
    return files


def split_args(text):
    out, depth, cur, quote = [], 0, '', False
    for ch in text:
        if ch == '"': quote = not quote
        if not quote:
            if ch in '([{': depth += 1
            if ch in ')]}': depth -= 1
            if ch == ',' and depth == 0:
                out.append(cur.strip()); cur = ''; continue
        cur += ch
    if cur.strip(): out.append(cur.strip())
    return out


def keywords(headers):
    path = os.path.join(headers, 'Key Words')
    if not os.path.exists(path): return set()
    text = open(path, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
    return {l.split('//')[0].strip().lower() for l in text.split('\n')
            if re.fullmatch(r'[A-Za-z_]\w*', l.split('//')[0].strip())}


def active_lines(text):
    """Drop '#if 0' branches (the headers keep planned signatures there, e.g. ERROR_PARAM)."""
    out, skipping, depth = [], False, 0
    for line in text.split('\n'):
        directive = line.strip()
        if skipping:
            if re.match(r'#if', directive): depth += 1
            elif re.match(r'#endif', directive):
                if depth == 0: skipping = False
                else: depth -= 1
            elif re.match(r'#else', directive) and depth == 0: skipping = False
            continue
        if re.match(r'#if\s+0\b', directive):
            skipping, depth = True, 0
            continue
        out.append(line)
    return '\n'.join(out)


def toolbox_arity(headers):
    """name -> (parameter count, variadic) of the active declaration (outside '#if 0' blocks)."""
    arity = {}
    for p in sorted(glob.glob(os.path.join(headers, '**', '*.incl'), recursive=True)):
        s = active_lines(open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n'))
        for m in re.finditer(r'^\s*toolbox\s+(?:fn\s+)?(\w+)\s*\(([^)]*)\)', s, re.M):
            name, params = m.group(1).lower(), m.group(2).strip()
            if name not in arity:
                parts = [] if params in ('', 'void') else split_args(params)
                variadic = bool(parts) and parts[-1].strip() == '...'
                arity[name] = ( len(parts) - (1 if variadic else 0), variadic )
    return arity


def toolbox_names(headers):
    names = set()
    for p in glob.glob(os.path.join(headers, '**', '*.incl'), recursive=True):
        s = open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
        names |= set(re.findall(r'^\s*toolbox\s+(?:fn\s+)?(\w+)', s, re.M))
        names |= set(re.findall(r'^\s*(?:\w+\s+)?local\s+fn\s+(\w+)', s, re.M))
        names |= set(re.findall(r'^\s*#define\s+(\w+)', s, re.M))
    return names


def main(argv):
    headers = None
    if '--headers' in argv:
        i = argv.index('--headers'); headers = argv[i + 1]; del argv[i:i + 2]
    files = collect(argv)
    if not files:
        print(__doc__); return 2
    local_fns = set()
    for p in files:
        s = open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
        local_fns |= set(re.findall(r'^\s*(?:\w+\s+)?local\s+fn\s+(\w+)', s, re.M))
        local_fns |= set(re.findall(r'^\s*toolbox\s+(?:fn\s+)?(\w+)', s, re.M))
        local_fns |= set(re.findall(r'^\s*#define\s+(\w+)', s, re.M))
    local_fns = {n.lower() for n in local_fns}
    known = {n.lower() for n in toolbox_names(headers)} | {'nslog'} if headers else None
    fb_keywords = keywords(headers) if headers else set()
    arity = toolbox_arity(headers) if headers else None
    problems = []
    for p in files:
        # single-file programs (.fb/.bas) may use #build; project files may not
        problems += lint_file(p, not p.endswith(('.fb', '.bas')), known, local_fns, fb_keywords, arity)
    for a in argv:
        for proj in glob.glob(os.path.join(a, '**', 'data.fbproj'), recursive=True) if os.path.isdir(a) else []:
            text = open(proj, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
            for no, line in enumerate(text.split('\n'), 1):
                if re.match(r'\s*resources\s+"[^"]*\.(incl|glbl|bas)"', line):
                    problems.append(f'{proj}:{no}: an FB source file listed as a resource is compiled into the app - bundle its folder instead')
    for line in problems: print(line)
    print(f'fblint: {len(files)} files, {len(problems)} problems')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
