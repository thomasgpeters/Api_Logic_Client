#!/usr/bin/env python3
"""Build the Customs sample database: samples/Customs/customs.sqlite

    python3 samples/Customs/build_db.py [out.sqlite] [--lookup-only]

schema.sql makes the tables; lookup.sql (the reference data that stays: countries, the tariff, ports of
entry, carriers, registered routes) and sample.sql (the demo scenario: importers, arrivals, declarations,
the trucks at the gate) fill them - every row through the business rules (customs_rules.py, run by
tools/logic_reference.py's engine, the same engine as LogicBank for FutureBasic), so every duty, total,
lane and gate decision is what the rules computed. --lookup-only leaves the demo scenario out: an empty
customs service, ready to use. purge_sample.sql removes the scenario from a database later.

Set in Bermuda. Sample duty rates in Bermuda's style - not the official tariff. The shipping lines,
hauliers, importers and people are made up. "Today" is 2026-11-26.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import sqlite3                                   # noqa: E402
from logic_reference import Data, Logic          # noqa: E402
import sample_loader                              # noqa: E402
import customs_rules                              # noqa: E402

LOOKUP = ['Country', 'Tariff', 'PortOfEntry', 'Carrier', 'Route']
SAMPLE = ['Importer', 'Arrival', 'Container', 'Declaration', 'DeclarationLine', 'Payment', 'Inspection', 'Truck', 'Driver', 'Movement']
# lodged first, then its goods, payments and inspections, then released or held; a truck waits at the
# gate first, then goes through or is stopped - in this order, as in the app
INITIAL = {'Declaration': {'Status': 'L'}, 'Movement': {'Status': 'W'}}


def build(path, with_sample=True):
    if os.path.exists(path):
        os.remove(path)
    schema = os.path.join(HERE, 'schema.sql')
    db = sqlite3.connect(path)
    db.executescript(open(schema).read())
    db.close()
    data = Data(path)
    logic = Logic(data)
    customs_rules.declare(logic)
    if not logic.activate():
        raise SystemExit('build_db: the rules did not activate: ' + '; '.join(logic.log))
    sample_loader.replay(logic, data, sample_loader.read_rows(schema, os.path.join(HERE, 'lookup.sql')), LOOKUP)
    if with_sample:
        later, finals = sample_loader.replay(logic, data, sample_loader.read_rows(schema, os.path.join(HERE, 'sample.sql')), SAMPLE, None, INITIAL)
        sample_loader.apply(logic, later, 'sample')
        for table in INITIAL:
            sample_loader.apply(logic, [(table, r) for r in finals.get(table, [])], 'sample status')
    data.db.close()
    return path


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = args[0] if args else os.path.join(HERE, 'customs.sqlite')
    build(out, '--lookup-only' not in sys.argv)
    print(f'build_db: {out}')
