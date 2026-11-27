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


# Toolbox names in FutureBasic_Documentation's headers (newer) that the author's FutureBasic does not
# have yet - each one found by a Build Log ("Unknown variable, command or Toolbox name"), with the way round
NEWER_THAN_FB = {
    'textviewappendattributedstring': 'append to fn TextViewTextStorage( tag ) with MutableAttributedStringAppendAttributedString (2026-11-25)',
}


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


def lint_file(path, is_project_file, known_toolbox, local_fns, fb_keywords=frozenset(), arity=None, object_params=None, global_names=None):
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
    blocks = []               # open block statements: (kind, line)
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
        # logging is gated: every NSLog on the line that tests isLoggingOn (NO by default, in the app's globals);
        # single-file .fb programs whose output is their log (tests, the smallest example) are exempt
        if re.search(r'\bNSLog\s*\(', code_only) and not re.search(r'\bisLoggingOn\b', code_only) and not path.endswith('.fb'):
            report(no, 'NSLog is not gated - write: if ( isLoggingOn ) then NSLog( ... )  (isLoggingOn is NO by default, in the app\'s globals)')
        # block balance: if/end if, select/end select, for/next, while/wend, do/until
        st = code_only.strip()
        for stmt in [p.strip() for p in st.split(' : ')] if st else []:
            low = stmt.lower()
            opener = None
            if re.match(r'if\b', low) and not re.search(r'\bthen\b', low): opener = 'if'
            elif re.match(r'select\b', low): opener = 'select'
            elif re.match(r'for\b', low): opener = 'for'
            elif re.match(r'while\b', low): opener = 'while'
            elif re.match(r'do\s*$', low): opener = 'do'
            closer = None
            if re.match(r'end\s+if\b', low): closer = 'if'
            elif re.match(r'end\s+select\b', low): closer = 'select'
            elif re.match(r'next\b', low): closer = 'for'
            elif re.match(r'wend\b', low): closer = 'while'
            elif re.match(r'until\b', low): closer = 'do'
            if opener: blocks.append((opener, no))
            if closer:
                if not blocks or blocks[-1][0] != closer:
                    expect = f'{blocks[-1][0]} from line {blocks[-1][1]}' if blocks else 'nothing open'
                    report(no, f'"{stmt}" closes no open {closer} block ({expect})')
                    if blocks and any(b[0] == closer for b in blocks):
                        while blocks and blocks[-1][0] != closer: blocks.pop()
                        blocks.pop()
                else:
                    blocks.pop()
        if re.match(r'\s*end\s+fn\b', line) or FN_DEF.match(line):
            for kind, bno in blocks:
                report(bno, f'{kind} block is not closed before the end of the fn')
            blocks = []
        if re.match(r'\s*for\s+\w+\s+in\s+(\(\s*\w+\s*\)\s*)?(fn\b|@\[)', code_only):
            report(no, 'for ... in needs an array variable, not an expression - assign it first')
        if fb_keywords:
            declared = [d for d in re.findall(r'\b(\w+)\s+as\s+\w', code_only) if d.lower() != 'dim']
            dm = re.match(r'\s*(?:[A-Z]\w*Ref|long|BOOL|double|NSInteger|NSUInteger|SInt64|SInt32|ptr|CGRect|CGFloat|CFRange)\s+(.*)$', code_only)
            if dm and not re.search(r'\blocal\s+fn\b', code_only):
                declared += [re.match(r'\s*(\w+)', part).group(1) for part in split_args(dm.group(1)) if re.match(r'\s*\w+', part)]
            fm = re.match(r'\s*for\s+(\w+)\s+in\b', code_only)
            if fm: declared.append(fm.group(1))
            for name in declared:
                # a local that redeclares a global: "Redefined variable" (FB 7.0.38)
                if current and name.lower() in (global_names or {}).get(os.path.dirname(path), set()) and not re.search(r'\blocal\s+fn\b|^\s*for\b', code_only):
                    report(no, f'"{name}" is a global (begin globals / .glbl) - give the local another name')
                # a parameter named like a global: "Redefined parameter" (FB 7.0.38, ALSProjectKeepCopy's projectName)
                fn_params = re.search(r'\blocal\s+fn\s+\w+\s*\((.*)\)', code_only)
                if fn_params and re.search(r'\b' + re.escape(name) + r'\s+as\b', fn_params.group(1)) and name.lower() in (global_names or {}).get(os.path.dirname(path), set()):
                    report(no, f'parameter "{name}" is a global (begin globals / .glbl) - FB: "Redefined parameter"; rename it')
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
                        # ObjectRef parameters: a CF value needs a cast, or clang warns (discards qualifiers)
                        args = split_args(code_only[cm.end():j - 1])
                        for i in (object_params or {}).get(name, []):
                            if i < len(args) and not re.match(r'\(\s*ObjectRef\s*\)|NULL\b', args[i]):
                                report(no, f'{cm.group(1)}: argument {i + 1} is an ObjectRef - cast it: (ObjectRef){args[i][:30]}')
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

        # an unsigned count minus 1 wraps around when the count is 0: the loop runs ~forever
        if re.search(r'\bto\s+fn\s+(ArrayCount|DictionaryCount|StringLength|DataLength|SetCount)\s*\(', strip_strings_and_comments(line)):
            report(no, 'for ... to fn ArrayCount( x ) - 1: the count is unsigned, so an empty x loops on - write to (long)fn ArrayCount( x ) - 1')
        # FutureBasic 7.0.38 (the author's) does not know the newer type names: use the CF ones
        for tm in re.finditer(r'(?<![A-Za-z_])(StringRef|MutableStringRef|DictionaryRef|MutableDictionaryRef|ArrayRef|MutableArrayRef|DataRef|URLRef|NumberRef)\b', strip_strings_and_comments(line)):
            report(no, f'{tm.group(1)} is unknown in FutureBasic 7.0.38 - use CF{tm.group(1)}')
        if known_toolbox is not None and not re.match(r'(?i)^\s*(toolbox|system|#define)\b', line):
            code = strip_strings_and_comments(line)
            names = re.findall(r'\bfn\s+(\w+)', code)
            call = re.match(r'\s*([A-Z]\w+)\s*\(', code)
            if call: names.append(call.group(1))
            for n in names:
                if n.lower() not in known_toolbox and n.lower() not in local_fns:
                    report(no, f'{n} is not in the toolbox headers or this code')
                elif n.lower() in NEWER_THAN_FB and n.lower() not in local_fns:
                    report(no, f'{n} is in the headers but not in the author\'s FutureBasic: {NEWER_THAN_FB[n.lower()]}')
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
    found = {l.split('//')[0].strip().lower() for l in text.split('\n')
             if re.fullmatch(r'[A-Za-z_]\w*', l.split('//')[0].strip())}
    # keywords the translator rejected as names that the list lacks (author's builds)
    return found | {'width'}


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


def toolbox_object_params(headers):
    """name -> indexes of its ObjectRef parameters (active declaration)."""
    params = {}
    for p in sorted(glob.glob(os.path.join(headers, '**', '*.incl'), recursive=True)):
        s = active_lines(open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n'))
        for m in re.finditer(r'^\s*toolbox\s+(?:fn\s+)?(\w+)\s*\(([^)]*)\)', s, re.M):
            name, plist = m.group(1).lower(), m.group(2).strip()
            if name not in params:
                parts = [] if plist in ('', 'void') else split_args(plist)
                params[name] = [i for i, a in enumerate(parts) if re.match(r'\s*ObjectRef\b', a)]
    return params


def toolbox_names(headers):
    names = set()
    for p in glob.glob(os.path.join(headers, '**', '*.incl'), recursive=True):
        s = open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
        names |= set(re.findall(r'^\s*toolbox\s+(?:fn\s+)?(\w+)', s, re.M))
        names |= set(re.findall(r'^\s*(?:\w+\s+)?local\s+fn\s+(\w+)', s, re.M))
        names |= set(re.findall(r'^\s*#define\s+(\w+)', s, re.M))
    return names


def build_order_problems(proj):
    """FB needs a local fn defined before any line that calls it, in data.fbproj order."""
    folder = os.path.dirname(os.path.dirname(proj))
    text = open(proj, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
    order = [os.path.join(folder, m) for m in re.findall(r'^\s*include\s+"([^"]+)"', text, re.M)]
    order = [f for f in order if os.path.exists(f)]
    sources = {}
    for f in order:
        sources[f] = open(f, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
    project_fns = set()
    for f in order:
        project_fns |= {n.lower() for n in re.findall(r'^\s*(?:\w+\s+)?local\s+fn\s+(\w+)', sources[f], re.M)}
    defined, problems = set(), []
    for f in order:
        for no, line in code_lines(sources[f]):
            m = FN_DEF.match(line)
            if m:
                defined.add(m.group(3).lower()); continue
            proto = re.match(r'^\s*(?:\w+\s+)?def\s+fn\s+(\w+)', line)   # def fn prototype: callable from here on
            if proto and not re.search(r'\busing\b', line):
                defined.add(proto.group(1).lower()); continue
            code = strip_strings_and_comments(line)
            names = re.findall(r'(?:\bfn|@fn)\s+(\w+)', code)
            call = re.match(r'\s*([A-Za-z]\w+)\s*\(', code)
            if call: names.append(call.group(1))
            for n in names:
                if n.lower() in project_fns and n.lower() not in defined:
                    problems.append(f'{f}:{no}: {n} is called before it is defined - move its file earlier in data.fbproj (or the fn up)')
    return problems


def main(argv):
    if argv and argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
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
        # a template may call fns the generator writes beside it: "// generated: Name, Name"
        for g in re.findall(r'^\s*//\s*generated:\s*([\w ,]+)$', s, re.M):
            local_fns |= {n.strip() for n in g.split(',') if n.strip()}
    local_fns = {n.lower() for n in local_fns}
    # global variable names: every declaration in a .glbl file and in begin globals ... end globals
    global_names = {}                       # folder (one project) -> names
    decl = re.compile(r'^\s*(?:[A-Z]\w*Ref|long|BOOL|double|NSInteger|NSUInteger|SInt64|SInt32|ptr|CGRect|CGFloat|CFRange|short|int|float|boolean|Str255)\s+(.*)$')
    for p in files:
        text = open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
        inside = p.endswith('.glbl')
        for line in text.split('\n'):
            code = line.split('//')[0]
            if re.match(r'\s*begin\s+globals\b', code, re.I): inside = True; continue
            if re.match(r'\s*end\s+globals\b', code, re.I): inside = p.endswith('.glbl'); continue
            if inside:
                m = decl.match(code)
                if m and not re.search(r'\bfn\b', code):
                    for part in split_args(m.group(1)):
                        n = re.match(r'\s*(\w+)', part)
                        if n: global_names.setdefault(os.path.dirname(p), set()).add(n.group(1).lower())
    known = {n.lower() for n in toolbox_names(headers)} | {'nslog'} if headers else None
    fb_keywords = keywords(headers) if headers else set()
    arity = toolbox_arity(headers) if headers else None
    object_params = toolbox_object_params(headers) if headers else None
    problems = []
    for p in files:
        # single-file programs (.fb/.bas) may use #build; project files may not
        problems += lint_file(p, not p.endswith(('.fb', '.bas')), known, local_fns, fb_keywords, arity, object_params, global_names)
    for a in argv:
        for proj in glob.glob(os.path.join(a, '**', 'data.fbproj'), recursive=True) if os.path.isdir(a) else []:
            text = open(proj, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
            problems += build_order_problems(proj)
            for no, line in enumerate(text.split('\n'), 1):
                # every file the project lists must be beside it: FB's own headers (NSLog.incl,
                # Tlbx ....incl) listed here crash FutureBasic 7.0.38 - include them from source
                im = re.match(r'\s*(include|resources)\s+"([^"]+)"', line)
                if im and not os.path.exists(os.path.join(os.path.dirname(os.path.dirname(proj)), im.group(2))):
                    problems.append(f'{proj}:{no}: {im.group(2)} is not beside the project - FB headers go in a source file '
                                    f'(include "{im.group(2)}"), never in the project list (FutureBasic crashes)')
                if re.match(r'\s*resources\s+"[^"]*\.(incl|glbl|bas)"', line):
                    problems.append(f'{proj}:{no}: an FB source file listed as a resource is compiled into the app - bundle its folder instead')
    for line in problems: print(line)
    print(f'fblint: {len(files)} files, {len(problems)} problems')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
