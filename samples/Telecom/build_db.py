#!/usr/bin/env python3
"""Build the Telecom sample database: samples/Telecom/telecom.sqlite

    python3 samples/Telecom/build_db.py [out.sqlite] [--lookup-only]

schema.sql makes the tables; lookup.sql (the reference data that stays) and sample.sql (the demo scenario)
fill them - every row through the business rules (telecom_rules.py, run by tools/logic_reference.py's engine,
the same engine as LogicBank for FutureBasic), so every price, total and count is what the rules computed.
--lookup-only leaves the demo scenario out: an empty carrier, ready to use. purge_sample.sql removes the
scenario from a database later.

Northstar Mobile and its partner networks are made up; the countries are real. "Today" is 2026-11-26.
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
import telecom_rules                              # noqa: E402

LOOKUP = ['Zone', 'Country', 'PartnerNetwork', 'RoamingAgreement', 'PlanOffer']
SAMPLE = ['Customer', 'Account', 'Plan', 'Phone', 'Usage', 'TravelPlan', 'TravelPlanCountry']
DEFER = {'Country': ['RoamingAgreementId']}       # the preferred agreement: set once the agreements are in
INITIAL = {'TravelPlan': {'Status': 'Q'}}         # a quote first, its countries, then bought or cancelled


def build(path, with_sample=True):
    if os.path.exists(path):
        os.remove(path)
    schema = os.path.join(HERE, 'schema.sql')
    db = sqlite3.connect(path)
    db.executescript(open(schema).read())
    db.close()
    data = Data(path)
    logic = Logic(data)
    telecom_rules.declare(logic)
    if not logic.activate():
        raise SystemExit('build_db: the rules did not activate: ' + '; '.join(logic.log))
    later, _ = sample_loader.replay(logic, data, sample_loader.read_rows(schema, os.path.join(HERE, 'lookup.sql')), LOOKUP, DEFER)
    sample_loader.apply(logic, later, 'lookup')
    if with_sample:
        later, finals = sample_loader.replay(logic, data, sample_loader.read_rows(schema, os.path.join(HERE, 'sample.sql')), SAMPLE, DEFER, INITIAL)
        sample_loader.apply(logic, later, 'sample')
        for table in INITIAL:
            sample_loader.apply(logic, [(table, r) for r in finals.get(table, [])], 'sample status')
    data.db.close()
    return path


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = args[0] if args else os.path.join(HERE, 'telecom.sqlite')
    build(out, '--lookup-only' not in sys.argv)
    print(f'build_db: {out}')
