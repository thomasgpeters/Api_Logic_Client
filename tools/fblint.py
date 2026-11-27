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


# the house style (docs/reference/FB Coding Rules.md, "Style"): the same in hand-written and generated code
STYLE_CALL = re.compile(r'\b[A-Za-z_]\w*\((?=[^ )])')
STYLE_COND = re.compile(r'\b(?:if|elseif|while|until|select)\s+\((?=[^ ])')
STYLE_FN_SPACE = re.compile(r'\bfn\s+\w+\s+\(')


def mask_strings(line):
    """the line with every string literal's contents blanked (same length), so a rule never looks inside one"""
    return re.sub(r'"(?:[^"\\]|\\.)*"', lambda m: '"' + ' ' * (len(m.group(0)) - 2) + '"', line)


def style_problems(path, text):
    """the house style: a header comment; no tabs; spaces inside a call's and a condition's parentheses
    ( fn X( a ), if ( x ) ); no space before a call's parenthesis; a space after //; no trailing spaces"""
    problems = []
    if 'CleanApp' in path.split(os.sep):                  # the FB editor's own starting project, kept as it made it
        return problems
    if os.path.basename(path).startswith('Tlbx '):         # FutureBasic's own toolbox files: the FB team's code, not ours
        return problems
    lines = text.split('\n')
    first = next((l.strip() for l in lines if l.strip()), '')
    if not first.startswith(('/*', '//')):
        problems.append(f'{path}:1: style: start the file with a header comment: its name, and what it holds')
    for no, line in code_lines(text):
        s = line.strip()
        if s.startswith('cln ') or s.startswith('#'):
            continue
        masked = mask_strings(line)
        code, _, comment = masked.partition('//')
        if line != line.rstrip():
            problems.append(f'{path}:{no}: style: trailing spaces')
        if '\t' in code:
            problems.append(f'{path}:{no}: style: a tab - use spaces')
        if STYLE_FN_SPACE.search(code):
            problems.append(f'{path}:{no}: style: no space between a function\'s name and its "(": fn Name( a )')
        if STYLE_COND.search(code):
            problems.append(f'{path}:{no}: style: a space inside a condition\'s parentheses: if ( x )')
        elif STYLE_CALL.search(code):
            problems.append(f'{path}:{no}: style: a space inside a call\'s parentheses: fn Name( a )')
        if '//' in masked and comment and comment[0] not in ' /-=*!~' and not code.endswith(':'):
            problems.append(f'{path}:{no}: style: a space after //')
    return problems


FN_DEF = re.compile(r'^\s*(?:(void)\s+|(\w+)\s+)?local\s+fn\s+(\w+)(\s*\(.*?\))?(.*)$')


def lint_file(path, is_project_file, known_toolbox, local_fns, fb_keywords=frozenset(), arity=None, object_params=None, global_names=None, object_globals=None):
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
    unkept = None             # (line, global): an object global just set from a fn, not yet seen kept
    kept_globals = (object_globals or {}).get(os.path.dirname(path), set())
    # a file may say once who keeps some globals: "// kept by ShellKeepTheme (App Shell.incl): gTheme*"
    kept_elsewhere = [n.lower() for m in re.finditer(r'//\s*kept by [^:\n]*:\s*([\w*, ]+)$', text, re.M | re.I)
                      for n in re.split(r'[,\s]+', m.group(1)) if n]
    def kept_by_file(name):
        return any(name.lower() == k or (k.endswith('*') and name.lower().startswith(k[:-1])) for k in kept_elsewhere)
    blocks = []               # open block statements: (kind, line)
    for no, line in code_lines(text):
        # FB's globals hold plain pointers and do not retain: an object made for the moment (fn MutableArrayNew,
        # a parsed file, a formatted string) is freed under the global when the event ends, and a later read
        # crashes (2026-11-27: the Studio's licence, LogicBankExample's Data Memory). Keep it: fn <Module>Kept( new, old ),
        # or fn CFRetain( global ) on the next line; "// within one event" on the line says it is not needed.
        if unkept and not re.match(r'\s*fn\s+CFRetain\(\s*' + re.escape(unkept[1]) + r'\s*\)', line, re.I):
            report(unkept[0], f'global {unkept[1]} is set from a fn but not kept: FB globals do not retain - use the module\'s Kept fn, '
                              f'or fn CFRetain( {unkept[1]} ) on the next line (or mark the line "// within one event", or "// kept by <who>")')
        unkept = None
        km = re.search(r'(?:^\s*|\bthen\s+)(\w+)\s*=\s*(?:\(\s*\w+\s*\)\s*)?fn\s+\w+', strip_strings_and_comments(line))
        if km and km.group(1).lower() in kept_globals and 'Kept(' not in line and 'within one event' not in line and 'kept by' not in line and not kept_by_file(km.group(1)):
            unkept = (no, km.group(1))
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
        # a record declared with a global record as its value: FB passes the global by address ("CGRect r = &gFrame":
        # clang error, 2026-11-27) - keep the global's parts as numbers
        rm = re.match(r'\s*(CGRect|CGPoint|CGSize|CFRange|NSRange|\w+Record)\s+\w+\s*=\s*(\w+)\s*$', strip_strings_and_comments(line))
        if rm and rm.group(2).lower() in (global_names or {}).get(os.path.dirname(path), set()):
            report(no, f'a {rm.group(1)} declared with the global {rm.group(2)} as its value: FB writes &{rm.group(2)} (clang error) - keep the global\'s parts as numbers (CGFloat), or read the value where it lives (fn ViewFrame)')
        # FutureBasic 7.0.38 (the author's) does not know the newer type names: use the CF ones
        # (before the fn-definition check below, which ends the line's checks: the parameters count too)
        for tm in re.finditer(r'(?<![A-Za-z_])(StringRef|MutableStringRef|DictionaryRef|MutableDictionaryRef|ArrayRef|MutableArrayRef|DataRef|URLRef|NumberRef)\b', strip_strings_and_comments(line)):
            report(no, f'{tm.group(1)} is unknown in FutureBasic 7.0.38 - use CF{tm.group(1)}')
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


def opt_in_names(headers):
    """Names FutureBasic knows only when a project includes the header: NSLog.incl and each Tlbx *.incl (with the files it
    includes). A name also in a header every project gets (CocoaUI ...) is left out. -> {name.lower(): header}"""
    if not headers or not os.path.isdir(headers): return {}
    def names_in(text):
        text = text.replace('\r', '\n')
        found = set(re.findall(r'^\s*#define\s+(\w+)\s+as\b', text, re.M))
        found |= set(re.findall(r'^\s*toolbox\s+(?:fn\s+)?(\w+)', text, re.M))
        found |= set(re.findall(r'^\s*system\s+\w+\s+(\w+)', text, re.M))
        return found
    def read(path):
        try: return open(path, 'rb').read().decode('utf-8', 'replace')
        except OSError: return ''
    def with_includes(path, seen):
        if path in seen: return ''
        seen.add(path)
        text = read(path)
        for inc in re.findall(r'^\s*include\s+"([^"]+)"', text.replace('\r', '\n'), re.M):
            text += '\n' + with_includes(os.path.join(headers, inc), seen)
        return text
    opt = {}
    # opt-in: the headers FutureBasic's own examples include by hand (FBExamples, beside Toolboxes), and two the author's
    # builds showed need it (2026-11-27); every other header is loaded for every project
    tops = {'NSLog.incl', 'Tlbx Security.incl', 'Tlbx CFDateFormatter.incl'}
    examples = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(headers))), 'FBExamples')
    for root, _dirs, fs in os.walk(examples):
        for f in fs:
            tops |= {h for h in re.findall(r'include\s+"(Tlbx [^"]+\.incl)"', read(os.path.join(root, f)).replace('\r', '\n'))}
    tops = sorted(t for t in tops if os.path.exists(os.path.join(headers, t)))
    every = set()
    for root, _dirs, fs in os.walk(headers):
        for f in fs:
            path = os.path.join(root, f)
            if f.endswith('.incl') and not any(path == os.path.join(headers, t) for t in tops):
                if os.path.dirname(path) == headers or 'CocoaUI' in path:
                    every |= {n.lower() for n in names_in(read(path))}
    for top in tops:
        for n in names_in(with_includes(os.path.join(headers, top), set())):
            if n.lower() not in every: opt.setdefault(n.lower(), top)
    return opt


def opt_in_problems(project_files, opt):
    """a name from an opt-in header (NSLog, a Tlbx header's) used where the project never includes that header"""
    problems, included, declared = [], set(), set()
    texts = {}
    for p in project_files:
        t = open(p, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n')
        texts[p] = t
        included |= set(re.findall(r'^\s*include\s+"([^"]+)"', t, re.M))
        # a file it includes from beside it brings that file's includes too (the SQL Generator's files bring NSLog.incl)
        for inc in re.findall(r'^\s*include\s+"([^"]+)"', t, re.M):
            near = os.path.join(os.path.dirname(p), inc)
            if os.path.isfile(near) and near not in project_files:
                included |= set(re.findall(r'^\s*include\s+"([^"]+)"', open(near, 'rb').read().decode('utf-8', 'replace').replace('\r', '\n'), re.M))
        declared |= {n.lower() for n in re.findall(r'^\s*(?:#define\s+(\w+)|toolbox\s+(?:fn\s+)?(\w+)|system\s+\w+\s+(\w+))', t, re.M) for n in n if n}
    reported = set()
    for p, t in texts.items():
        in_c = in_block = False
        for no, line in enumerate(t.split('\n'), 1):
            if re.match(r'\s*Begin(CDeclaration|CFunction|CCode)', line): in_c = True
            if in_c:
                if re.match(r'\s*EndC', line): in_c = False
                continue
            if re.match(r'\s*cln\b', line): continue
            # /* ... */ comments, over one line or many
            if in_block:
                if '*/' not in line: continue
                line, in_block = line.split('*/', 1)[1], False
            while '/*' in line:
                before, after = line.split('/*', 1)
                if '*/' in after: line = before + after.split('*/', 1)[1]
                else: line, in_block = before, True
            code = strip_strings_and_comments(line)
            for w in re.findall(r'\b([A-Za-z_]\w*)\b', code):
                h = opt.get(w.lower())
                if h and h not in included and w.lower() not in declared and (w.lower(), h) not in reported:
                    reported.add((w.lower(), h))
                    problems.append(f'{p}:{no}: {w} comes from FutureBasic\'s "{h}", which this project never includes - '
                                    f'include it in the globals (FB stops at "Unknown statement" / "Unknown variable")')
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
    object_globals = {}                     # folder -> the names of globals holding objects (CF / Cocoa refs)
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
                        if n and re.match(r'\s*(CF\w+Ref|ColorRef|ImageRef|FontRef|CFTypeRef)\b', code) and not re.match(r'\s*CFRange\b', code):
                            object_globals.setdefault(os.path.dirname(p), set()).add(n.group(1).lower())
    known = {n.lower() for n in toolbox_names(headers)} | {'nslog'} if headers else None
    fb_keywords = keywords(headers) if headers else set()
    arity = toolbox_arity(headers) if headers else None
    object_params = toolbox_object_params(headers) if headers else None
    problems = []
    for p in files:
        # single-file programs (.fb/.bas) may use #build; project files may not
        problems += lint_file(p, not p.endswith(('.fb', '.bas')), known, local_fns, fb_keywords, arity, object_params, global_names, object_globals)
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
    # a C function FB calls (toolbox) is defined in BeginCFunction and must also be declared in BeginCDeclaration: FB
    # compiles a project in several chunks, and only the declarations (the shared header) reach them all ("call to
    # undeclared function 'StudioFindView'", 2026-11-27)
    by_folder = {}
    for p in files:
        by_folder.setdefault(os.path.dirname(p), []).append(p)
    for folder, members in by_folder.items():
        defined, declared, called = {}, set(), {}
        for p in members:
            text = open(p, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
            for m in re.finditer(r'(?ms)^\s*BeginCFunction\b(.*?)^\s*EndC\b', text):
                for d in re.finditer(r'(?m)^(?!\s*static\b)[A-Za-z_][\w \*]*?\b(\w+)\s*\([^;{]*\)\s*\{', m.group(1)):
                    defined.setdefault(d.group(1), p)
            for m in re.finditer(r'(?ms)^\s*BeginCDeclaration\b(.*?)^\s*EndC\b', text):
                declared |= set(re.findall(r'\b(\w+)\s*\(', m.group(1)))
            for no, line in enumerate(text.split('\n'), 1):
                t = re.match(r'\s*toolbox\s+(?:fn\s+)?(\w+)', line)
                if t: called.setdefault(t.group(1), (p, no))
        for name, (p, no) in sorted(called.items()):
            if name in defined and name not in declared:
                problems.append(f'{p}:{no}: {name} is a C function (BeginCFunction) with no declaration in a BeginCDeclaration block - '
                                f'add its prototype there, or other files of the project cannot call it')
    # names from opt-in headers (NSLog.incl, Tlbx *.incl): the project must include the header
    opt = opt_in_names(headers)
    if opt:
        projects = set()
        for a in argv:
            for proj in glob.glob(os.path.join(a, '**', 'data.fbproj'), recursive=True) if os.path.isdir(a) else []:
                projects.add(os.path.dirname(os.path.dirname(proj)))
        for folder in sorted(projects):
            members = [p for p in files if os.path.dirname(p) == folder]
            problems += opt_in_problems(members, opt)
        for p in files:
            if p.endswith(('.fb', '.bas')): problems += opt_in_problems([p], opt)
    for p in files:
        problems += style_problems(p, open(p, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n'))
    for line in problems: print(line)
    print(f'fblint: {len(files)} files, {len(problems)} problems')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
