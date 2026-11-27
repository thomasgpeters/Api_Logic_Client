#!/usr/bin/env python3
"""check_record_index.py - test: Record Files for FutureBasic's B-tree (the C in Record Index.incl).

Compiles exactly the text between the markers "record index core" in src/RecordFilesExample/Record Index.incl,
drives it with random inserts, deletes and seeks (equal keys included), and compares every answer with a sorted
list. After each run the index file is read by tools/record_files_reference.py, which checks the tree with its own
walk and compares the entries. Also: keys (numbers, text, caseless), closing and reopening, an index left open (the
program stopped), and a timing on 300,000 entries. Skipped when there is no C compiler.

    python3 tools/check_record_index.py [--quick]
"""
import bisect
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import record_files_reference as ref  # noqa: E402

MODULE = os.path.join(ROOT, 'src', 'RecordFilesExample', 'Record Index.incl')
START = '/* --- record index core'
END = '/* --- end record index core --- */'

# commands on stdin, one answer per line on stdout
HARNESS = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static int hexval( char c ) { return c <= '9' ? c - '0' : ( c | 32 ) - 'a' + 10; }
int main( void ) {
    char line[2048], word[32], arg[1024];
    long h = 0, a, b;
    while ( fgets( line, sizeof line, stdin ) ) {
        arg[0] = 0; a = b = 0;
        if ( sscanf( line, "%31s", word ) != 1 ) continue;
        if ( !strcmp( word, "create" ) || !strcmp( word, "open" ) ) {
            sscanf( line, "%*s %ld %1023s", &a, arg );
            h = RIOpenPath( arg, a, word[0] == 'c' );
            printf( "%ld %ld\n", h, h ? RIWasClosedCleanly( h ) : -1 );
        } else if ( !strcmp( word, "close" ) ) { RIClose( h ); printf( "ok\n" ); }
        else if ( !strcmp( word, "abandon" ) ) { h = 0; printf( "ok\n" ); }        /* as if the program stopped */
        else if ( !strcmp( word, "key" ) ) {                                          /* key <hex> */
            unsigned char bytes[512]; int n = 0;
            sscanf( line, "%*s %1023s", arg );
            for ( char *p = arg; p[0] && p[1]; p += 2 ) bytes[n++] = (unsigned char)( hexval( p[0] ) * 16 + hexval( p[1] ) );
            RIKeyClear( h ); RIKeyAddBytes( h, bytes, n, n, 0 ); printf( "ok\n" );
        }
        else if ( !strcmp( word, "klong" ) ) { sscanf( line, "%*s %ld", &a ); RIKeyClear( h ); RIKeyAddLong( h, a ); printf( "ok\n" ); }
        else if ( !strcmp( word, "kpascal" ) ) {                                      /* kpascal width caseless text */
            unsigned char p[256]; char *t;
            sscanf( line, "%*s %ld %ld", &a, &b );
            t = strchr( strchr( strchr( line, ' ' ) + 1, ' ' ) + 1, ' ' ) + 1;
            t[strcspn( t, "\n" )] = 0;
            p[0] = (unsigned char)strlen( t ); memcpy( p + 1, t, p[0] );
            RIKeyClear( h ); RIKeyAddPascal( h, p, a, b ); printf( "ok\n" );
        }
        else if ( !strcmp( word, "ins" ) ) { sscanf( line, "%*s %ld", &a ); printf( "%ld\n", RIInsert( h, a ) ); }
        else if ( !strcmp( word, "del" ) ) { sscanf( line, "%*s %ld", &a ); printf( "%ld\n", RIDelete( h, a ) ); }
        else if ( !strcmp( word, "seek" ) ) { sscanf( line, "%*s %ld", &a ); printf( "%ld\n", RISeek( h, a ) ); }
        else if ( !strcmp( word, "next" ) ) printf( "%ld\n", RINext( h ) );
        else if ( !strcmp( word, "prev" ) ) printf( "%ld\n", RIPrevious( h ) );
        else if ( !strcmp( word, "equals" ) ) printf( "%ld\n", RICursorKeyEquals( h ) );
        else if ( !strcmp( word, "count" ) ) printf( "%ld\n", RIEntryCount( h ) );
        else if ( !strcmp( word, "flush" ) ) printf( "%ld\n", RIFlush( h ) );
        else if ( !strcmp( word, "check" ) ) { char m[300]; long ok = RICheck( h, m, sizeof m ); printf( "%s\n", ok ? "sound" : m ); }
        else if ( !strcmp( word, "bulk" ) ) {                                         /* bulk n: n random 8-byte keys, timed */
            struct timespec t0, t1; long i; unsigned int s = 12345;
            sscanf( line, "%*s %ld", &a );
            clock_gettime( CLOCK_MONOTONIC, &t0 );
            for ( i = 1; i <= a; i++ ) { s = s * 1103515245u + 12345u; RIKeyClear( h ); RIKeyAddLong( h, (long)( s % 1000000 ) ); RIInsert( h, i ); }
            clock_gettime( CLOCK_MONOTONIC, &t1 );
            double ins = ( t1.tv_sec - t0.tv_sec ) + ( t1.tv_nsec - t0.tv_nsec ) / 1e9;
            s = 999; clock_gettime( CLOCK_MONOTONIC, &t0 );
            long hits = 0;
            for ( i = 1; i <= a; i++ ) { s = s * 1103515245u + 12345u; RIKeyClear( h ); RIKeyAddLong( h, (long)( s % 1000000 ) ); if ( RISeek( h, 3 ) ) hits++; }
            clock_gettime( CLOCK_MONOTONIC, &t1 );
            double look = ( t1.tv_sec - t0.tv_sec ) + ( t1.tv_nsec - t0.tv_nsec ) / 1e9;
            clock_gettime( CLOCK_MONOTONIC, &t0 );
            long scanned = 0; for ( long r = RISeek( h, 1 ); r; r = RINext( h ) ) scanned++;
            clock_gettime( CLOCK_MONOTONIC, &t1 );
            double scan = ( t1.tv_sec - t0.tv_sec ) + ( t1.tv_nsec - t0.tv_nsec ) / 1e9;
            printf( "%.3f %.3f %.3f %ld %ld %ld\n", ins, look, scan, hits, scanned, RIHeight( h ) );
        }
        else printf( "?\n" );
        fflush( stdout );
    }
    return 0;
}
'''


class Harness:
    def __init__(self, exe):
        self.p = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

    def __call__(self, command):
        self.p.stdin.write(command + '\n')
        self.p.stdin.flush()
        return self.p.stdout.readline().strip()

    def close(self):
        self.p.stdin.close()
        self.p.wait()


FAILED = []


def check(name, ok, detail=''):
    print(('PASS  ' if ok else 'FAIL  ') + name + ('' if ok else f'   {detail}'))
    if not ok:
        FAILED.append(name)


def build(tmp):
    cc = shutil.which('cc') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        return None
    text = open(MODULE, 'rb').read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
    core = text[text.index(START):text.index(END) + len(END)]
    src = os.path.join(tmp, 'ri.c')
    open(src, 'w').write('#define _XOPEN_SOURCE 700\n' + core + HARNESS)
    exe = os.path.join(tmp, 'ri')
    r = subprocess.run([cc, '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-o', exe, src], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr)
        check('the core compiles (-Wall -Wextra -Werror)', False, 'see above')
        return None
    check('the core compiles (-Wall -Wextra -Werror)', True)
    return exe


def random_run(exe, tmp, seed, key_length, operations, distinct_keys):
    """inserts, deletes and every kind of seek against a sorted list of (key, record) composites"""
    rnd = random.Random(seed)
    path = os.path.join(tmp, f'random{seed}.index')
    h = Harness(exe)
    h(f'create {key_length} {path}')
    model = []                     # sorted composites
    live = {}                      # record -> key
    next_record = 1
    problems = []

    def key_hex(k):
        return k.hex()

    def make_key():
        v = rnd.randrange(distinct_keys)
        return v.to_bytes(4, 'big') + bytes(key_length - 4) if key_length >= 4 else bytes([v % 256]) * key_length

    for step in range(operations):
        r = rnd.random()
        if r < 0.55 or not live:                       # insert
            k = make_key()
            h('key ' + key_hex(k))
            got = h(f'ins {next_record}')
            if got != '1':
                problems.append(f'step {step}: insert returned {got}')
                break
            bisect.insort(model, ref.composite(k, next_record))
            live[next_record] = k
            next_record += 1
        elif r < 0.75:                                 # delete one that is there, and one that is not
            rec = rnd.choice(list(live))
            h('key ' + key_hex(live[rec]))
            if h(f'del {rec}') != '1':
                problems.append(f'step {step}: delete of {rec} failed')
                break
            model.remove(ref.composite(live.pop(rec), rec))
            if h(f'del {rec}') != '0':
                problems.append(f'step {step}: a second delete of {rec} succeeded')
                break
        elif r < 0.78:                                 # a duplicate insert is refused
            rec = rnd.choice(list(live))
            h('key ' + key_hex(live[rec]))
            if h(f'ins {rec}') != '0':
                problems.append(f'step {step}: a duplicate entry was accepted')
                break
        else:                                          # a seek, then a few steps either way
            k = make_key()
            mode = rnd.randint(1, 7)
            h('key ' + key_hex(k))
            got = int(h(f'seek {mode}'))
            lo = bisect.bisect_left(model, ref.composite(k, 0))
            hi = bisect.bisect_right(model, ref.composite(k, 0xFFFFFFFF))
            pos = {1: 0 if model else None, 2: len(model) - 1 if model else None,
                   3: lo if lo < hi else None, 4: lo if lo < len(model) else None,
                   5: hi if hi < len(model) else None, 6: hi - 1 if hi > 0 else None,
                   7: lo - 1 if lo > 0 else None}[mode]
            want = int.from_bytes(model[pos][-4:], 'big') if pos is not None else 0
            if got != want:
                problems.append(f'step {step}: seek mode {mode} gave {got}, expected {want}')
                break
            if pos is not None:
                direction = rnd.choice(['next', 'prev'])
                for _ in range(rnd.randint(1, 6)):
                    pos = pos + 1 if direction == 'next' else pos - 1
                    want = int.from_bytes(model[pos][-4:], 'big') if 0 <= pos < len(model) else 0
                    got = int(h(direction))
                    if got != want:
                        problems.append(f'step {step}: {direction} gave {got}, expected {want}')
                        break
                    if want == 0:
                        break
            if problems:
                break
    if not problems:
        if int(h('count')) != len(model):
            problems.append(f'count {h("count")} != {len(model)}')
        c = h('check')
        if c != 'sound':
            problems.append('RICheck: ' + c)
    h('close')
    h.close()
    if not problems:
        header, entries, ref_problems = ref.read_index(path)
        problems += ['reference: ' + p for p in ref_problems]
        if not ref_problems and [ref.composite(k, r) for k, r in entries] != model:
            problems.append('the entries in the file differ from the model')
        if header['closedCleanly'] != 1:
            problems.append('not marked closed cleanly after close')
    return problems, len(model), next_record - 1


def main(argv):
    quick = '--quick' in argv
    tmp = tempfile.mkdtemp(prefix='recordindex')
    try:
        exe = build(tmp)
        if exe is None:
            if not FAILED:
                print('skipped: no C compiler')
            return 1 if FAILED else 0
        runs = [(1, 8, 4000, 50), (2, 8, 4000, 3), (3, 40, 3000, 400), (4, 200, 1500, 30), (5, 8, 20000, 5000), (6, 220, 12000, 3000)]
        if quick:
            runs = runs[:3]
        for seed, k, ops, distinct in runs:
            problems, kept, made = random_run(exe, tmp, seed, k, ops, distinct)
            check(f'random run {seed}: {ops} operations, {k}-byte keys, {distinct} distinct keys '
                  f'({made} inserted, {kept} kept) - answers, RICheck and the reference reader agree', not problems,
                  '; '.join(problems[:3]))

        # keys: numbers sort as numbers (negatives too), text caseless
        h = Harness(exe)
        p = os.path.join(tmp, 'keys.index')
        h(f'create 8 {p}')
        values = [-5000000000, -3, -1, 0, 1, 2, 255, 256, 70000, 5000000000]
        for i, v in enumerate(random.Random(9).sample(values, len(values)), 1):
            h(f'klong {v}')
            h(f'ins {i}')
        order = []
        r = int(h('seek 1'))
        while r:
            order.append(r)
            r = int(h('next'))
        shuffled = random.Random(9).sample(values, len(values))
        check('number keys sort as numbers, negatives first', [shuffled[i - 1] for i in order] == sorted(values))
        h('close')
        _, entries, _ = ref.read_index(p)
        check('the reference encodes numbers the same way', [k for k, _ in entries] == [ref.key_long(v) for v in sorted(values)])
        p = os.path.join(tmp, 'names.index')
        h(f'create 12 {p}')
        names = ['banana', 'Apple', 'cherry', 'apple', 'Banana split', 'a']
        for i, n in enumerate(names, 1):
            h(f'kpascal 12 1 {n}')
            h(f'ins {i}')
        order = []
        r = int(h('seek 1'))
        while r:
            order.append(names[r - 1])
            r = int(h('next'))
        check('text keys, caseless: Apple and apple together, in record order', order == ['a', 'Apple', 'apple', 'banana', 'Banana split', 'cherry'], str(order))
        h('kpascal 12 1 APPLE')
        first = int(h('seek 3'))
        second = int(h('next'))
        h('kpascal 12 1 apple')
        check('seek Equal finds the first of equal keys; the next has the same key', (first, second, h('equals')) == (2, 4, '1'))
        h('kpascal 12 1 apples')
        check('seek Equal with no such key: 0', h('seek 3') == '0')
        h('close')
        _, entries, _ = ref.read_index(p)
        check('the reference encodes caseless text the same way', [k for k, _ in entries][:2] == [ref.key_bytes(b'a', 12, True), ref.key_bytes(b'Apple', 12, True)])

        # reopen; an index left open
        p = os.path.join(tmp, 'reopen.index')
        h(f'create 8 {p}')
        for i in range(1, 2001):
            h(f'klong {i * 7 % 2001}')
            h(f'ins {i}')
        h('close')
        opened = h(f'open 8 {p}').split()
        check('reopened: closed cleanly, every entry there', opened[1] == '1' and h('count') == '2000' and h('check') == 'sound')
        h('klong 14')
        check('reopened: a lookup', h('seek 3') == '2')
        h('flush')
        h('abandon')
        opened = h(f'open 8 {p}').split()
        check('an index left open (the program stopped) is reported: not closed cleanly', opened[1] == '0')
        h('close')
        check('the wrong key length is refused', h(f'open 16 {p}').split()[0] == '0')
        h.close()

        # timing
        n = 50000 if quick else 300000
        h = Harness(exe)
        h(f'create 8 {os.path.join(tmp, "bulk.index")}')
        t0 = time.time()
        ins, look, scan, hits, scanned, height = h(f'bulk {n}').split()
        h('close')
        h.close()
        _, entries, problems = ref.read_index(os.path.join(tmp, 'bulk.index'))
        check(f'{n:,} random keys: insert {float(ins):.2f} s, {n:,} lookups {float(look):.2f} s, scan {float(scan):.3f} s, '
              f'height {height}', int(scanned) == n and not problems and len(entries) == n, '; '.join(problems[:2]))
        print(f'      (this machine, {time.time() - t0:.1f} s in all; the Mac test times the same on the Mac)')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'check_record_index: {len(FAILED)} failed')
    return 1 if FAILED else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
