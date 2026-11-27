#!/usr/bin/env python3
"""check_web_layout.py - test: the Web Toolkit's XIB layout code (Objective-C) against its Python reference.

Web Layout.incl carries the XIB reader between the markers "XIB layout core"; this compiles exactly that text here,
with GNUstep (an open-source Foundation, NSXMLDocument included), and checks that it builds the same widget tree as
tools/web_layout_reference.py for the reference's test layout, every XIB in the repository, and the example's layouts.
Skipped when clang or GNUstep is missing (apt install libgnustep-base-dev).
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

MODULE = os.path.join(ROOT, 'src', 'WebToolkit', 'Web Layout.incl')
START = '/* --- XIB layout core'
END = '/* --- end XIB layout core --- */'

HARNESS = r'''
int main( int argc, char **argv ) {
    NSAutoreleasePool *pool = [NSAutoreleasePool new];
    NSMutableArray *all = [NSMutableArray array];
    for ( int i = 1; i < argc; i++ ) {
        NSString *xml = [NSString stringWithContentsOfFile:[NSString stringWithUTF8String:argv[i]] encoding:NSUTF8StringEncoding error:NULL];
        NSArray *tree = WLTreeFromXIB( xml, @"page", @"" );
        [all addObject:( tree ? (id)tree : (id)[NSNull null] )];
    }
    NSData *json = [NSJSONSerialization dataWithJSONObject:all options:0 error:NULL];
    fwrite( [json bytes], 1, [json length], stdout );
    [pool release];
    return 0;
}
'''


def normal(v):
    """booleans and numbers compared by value (Foundation writes NO as false or 0)"""
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, float) and v == int(v):
        return int(v)
    if isinstance(v, list):
        return [normal(x) for x in v]
    if isinstance(v, dict):
        return {k: normal(x) for k, x in v.items()}
    return v


def first_difference(a, b, path='tree'):
    if type(a) != type(b):
        return f'{path}: {a!r} != {b!r}'
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return f'{path}.{k}: only in ' + ('Objective-C' if k in a else 'the reference')
            d = first_difference(a[k], b[k], f'{path}.{k}')
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f'{path}: {len(a)} items != {len(b)}'
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_difference(x, y, f'{path}[{i}]')
            if d:
                return d
        return None
    return None if a == b else f'{path}: {a!r} != {b!r}'


def main():
    clang, config = shutil.which('clang'), shutil.which('gnustep-config')
    if not clang or not config:
        print('SKIP  the XIB layout core (no clang + GNUstep here)')
        return 0
    text = open(MODULE, encoding='utf-8', newline='').read().replace('\r\n', '\n').replace('\r', '\n')
    if START not in text or END not in text:
        print('FAIL  Web Layout.incl has no "XIB layout core" markers')
        return 1
    core = text[text.index(START):text.index(END) + len(END)]
    objc_include = ''
    found = glob.glob('/usr/lib/gcc/*/*/include/objc/objc.h')
    if found:
        objc_include = '-I' + os.path.dirname(os.path.dirname(found[0]))
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'layout.m')
        exe = os.path.join(tmp, 'layout')
        open(src, 'w').write('#import <Foundation/Foundation.h>\n#include <math.h>\n' + core + '\n' + HARNESS)
        flags = subprocess.run([config, '--objc-flags'], capture_output=True, text=True).stdout.split()
        libs = subprocess.run([config, '--base-libs'], capture_output=True, text=True).stdout.split()
        build = subprocess.run([clang] + flags + ([objc_include] if objc_include else []) + ['-Wno-everything', src] + libs + ['-o', exe],
                               capture_output=True, text=True)
        if build.returncode != 0:
            print('FAIL  the XIB layout core compiles\n' + build.stderr[-3000:])
            return 1
        print('PASS  the XIB layout core compiles (Objective-C, as in Web Layout.incl)')
        test_xib = os.path.join(tmp, 'Test.xib')
        open(test_xib, 'w').write(ref.TEST_XIB)
        files = [test_xib] + sorted(glob.glob(os.path.join(ROOT, 'src', 'AppBuilder', '*.xib'))) \
            + sorted(glob.glob(os.path.join(ROOT, 'src', 'WebToolkitExample', '*.webxib')))
        run = subprocess.run([exe] + files, capture_output=True, text=True, timeout=120)
        if run.returncode != 0:
            print('FAIL  the XIB layout core runs\n' + run.stderr[-2000:])
            return 1
        trees = json.loads(run.stdout)
        for path, tree in zip(files, trees):
            want = normal(ref.tree_from_xib(open(path, encoding='utf-8').read()))
            got = normal(tree)
            d = first_difference(got, want)
            name = 'the reference test layout' if path == test_xib else os.path.relpath(path, ROOT)
            print(('PASS  ' if d is None else 'FAIL  ') + f'same widgets as the reference: {name}' + ('' if d is None else f'\n      {d}'))
            failures += d is not None
    print('web layout core: ' + ('all passed' if not failures else f'{failures} failed'))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
