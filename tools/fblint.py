#!/usr/bin/env python3
"""
fblint - check FutureBasic sources against the rules in docs/FB Coding Rules.md.

Run it on this repo's FB code and on every generated project before a build:

    python3 tools/fblint.py Generator Runtime
    python3 tools/fblint.py ~/ApiLogicClient/"Northwind Project"
    python3 tools/fblint.py --headers ../FutureBasic_Documentation/Toolboxes/Headers Generator Runtime

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


def lint_file(path, is_project_file, known_toolbox, local_fns):
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
    problems = []
    for p in files:
        # single-file programs (.fb/.bas) may use #build; project files may not
        problems += lint_file(p, not p.endswith(('.fb', '.bas')), known, local_fns)
    for line in problems: print(line)
    print(f'fblint: {len(files)} files, {len(problems)} problems')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
