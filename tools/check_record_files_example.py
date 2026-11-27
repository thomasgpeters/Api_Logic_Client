#!/usr/bin/env python3
"""check_record_files_example.py - test: the Record Files example's C outside the B-tree.

Compiles the text between the markers in src/RecordFilesExample/Sample Data.incl ("sample data core") and
SQLite Comparison.incl ("sqlite comparison core") with a small driver, runs the SQLite side of the benchmark on
1,000 customers, and checks what comes back: every row there, every lookup found, each customer's orders, the
customers in caseless name order, the deletes and adds; and that the sample data's amounts and dates are sound.
Skipped when there is no C compiler or no sqlite3 header.
"""
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(ROOT, 'src', 'RecordFilesExample')

DRIVER = r'''
int main( int argc, char **argv ) {
    long customers = 1000;
    double t = SQLiteBuildPath( argv[1], customers, 5, 4 );
    printf( "build %f\n", t );
    t = SQLiteReopenPath( argv[1] ); printf( "reopen %f\n", t );
    t = SQLiteFindCustomers( 10000, customers, 2026 ); printf( "find %f %ld\n", t, SQLiteLastRows() );
    t = SQLiteOrdersOfCustomers( 2000, customers, 2027 ); printf( "orders %f %ld\n", t, SQLiteLastRows() );
    t = SQLiteScanByName(); printf( "scan %f %ld\n", t, SQLiteLastRows() );
    t = SQLiteDeleteAndAdd( 1000, customers * 20, 2028 ); printf( "delete %f %ld\n", t, SQLiteLastRows() );
    SQLiteCloseDatabase();
    RBSeed( 7 ); long lo = 99, hi = 0;
    for ( int n = 0; n < 100000; n++ ) { long r = RBRandom( 50 ); if ( r < lo ) lo = r; if ( r > hi ) hi = r; }
    printf( "random %ld %ld\n", lo, hi );
    char name[64]; RBCustomerNameC( 31, name, sizeof name ); printf( "name %s\n", name );
    return argc > 99;
}
'''


def core(path, start, end):
    text = open(path, 'rb').read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
    return text[text.index(start):text.index(end) + len(end)]


def main():
    cc = shutil.which('cc') or shutil.which('gcc') or shutil.which('clang')
    if not cc or not os.path.exists('/usr/include/sqlite3.h'):
        print('skipped: no C compiler or no sqlite3 header')
        return 0
    failed = []

    def check(name, ok, detail=''):
        print(('PASS  ' if ok else 'FAIL  ') + name + ('' if ok else f'   {detail}'))
        if not ok:
            failed.append(name)

    tmp = tempfile.mkdtemp(prefix='recordfiles')
    try:
        src = '#define _XOPEN_SOURCE 700\n#define _DEFAULT_SOURCE\n#include <sqlite3.h>\n' + \
              core(os.path.join(FOLDER, 'Sample Data.incl'), '/* --- sample data core', '/* --- end sample data core --- */') + '\n' + \
              core(os.path.join(FOLDER, 'SQLite Comparison.incl'), '/* --- sqlite comparison core', '/* --- end sqlite comparison core --- */') + DRIVER
        open(os.path.join(tmp, 'x.c'), 'w').write(src)
        exe = os.path.join(tmp, 'x')
        r = subprocess.run([cc, '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-o', exe, os.path.join(tmp, 'x.c'), '-lsqlite3', '-lm'],
                           capture_output=True, text=True)
        check('the sample data and SQLite comparison compile (-Wall -Wextra -Werror)', r.returncode == 0, r.stderr[:600])
        if r.returncode:
            return 1
        db = os.path.join(tmp, 'c.sqlite')
        out = dict((l.split()[0], l.split()[1:]) for l in subprocess.run([exe, db], capture_output=True, text=True).stdout.splitlines())
        check('SQLite build: done', float(out['build'][0]) >= 0)
        check('10,000 customers by number: every one found', out['find'][1] == '10000')
        con = sqlite3.connect(db)
        counts = [con.execute(f'select count(*) from {t}').fetchone()[0] for t in ('Customer', '"Order"', 'Item')]
        check('1,000 customers, 5,000 orders, 20,000 items (after deleting and adding as many)', counts == [1000, 5000, 20000], str(counts))
        check('the orders of 2,000 customers: 5 each', out['orders'][1] == '10000')
        check('every customer in name order', out['scan'][1] == '1000')
        names = [r[0] for r in con.execute('select Name from Customer order by Name collate nocase')]
        check('names sort caseless, as the name index does', names == sorted(names, key=lambda s: s.upper()))
        check('deletes at random: some ids drawn twice, the rest removed', 900 < int(out['delete'][1]) <= 1000, out['delete'][1])
        bad = con.execute('select count(*) from Item where ItemId <= 20000 and abs(Amount - round(Quantity * UnitPrice * (100 - (select Discount from "Order" o where o.OrderId = Item.OrderId)) / 100.0, 2)) > 0.005').fetchone()[0]
        check('every item: quantity x price less the discount, to the cent', bad == 0, f'{bad} wrong')
        bad = con.execute('select count(*) from "Order" o where abs(AmountTotal - (select coalesce(sum(Amount), 0) from Item i where i.OrderId = o.OrderId and i.ItemId <= 20000)) > 0.005 and (select count(*) from Item i where i.OrderId = o.OrderId and i.ItemId <= 20000) = o.ItemCount').fetchone()[0]
        check('every order that kept its items: its items added up', bad == 0, f'{bad} wrong')
        bad = con.execute('select count(*) from Customer c where abs(Balance - (select coalesce(sum(AmountTotal), 0) from "Order" o where o.CustomerId = c.CustomerId and ShippedDate = 0)) > 0.005').fetchone()[0]
        check('every customer: the unshipped orders added up', bad == 0, f'{bad} wrong')
        dates = [r[0] for r in con.execute('select OrderDate from "Order"')]
        check('order dates are real dates (yyyymmdd)', all(1 <= d // 100 % 100 <= 12 and 1 <= d % 100 <= 28 for d in dates))
        check('random numbers: 1 to n', out['random'] == ['1', '50'])
        check('a customer name: "Last, First n"', ' '.join(out['name']) == 'Hughes, Carla 31', ' '.join(out['name']))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'check_record_files_example: {len(failed)} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
