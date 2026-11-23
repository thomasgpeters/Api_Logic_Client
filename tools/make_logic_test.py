#!/usr/bin/env python3
"""
Assemble an FB project that runs the logic engine's acceptance scenarios on a Mac.

    python3 tools/make_logic_test.py <Northwind db.sqlite> <output folder>

The output folder gets:
    Logic Test.fbeproj/   data.fbproj (runtime, test rules, main) + Settings2.plist
    *.incl / *.glbl       the runtime, copied from src/Runtime
    Logic Test Rules.incl the scenarios' rules, in FB
    Logic Test.main       the scenarios: PASS / FAIL lines in the NSLog window
    Model.json            the model, read from the database (tools/sqlite_model.py)
    test.sqlite           a working copy of the database - the original is never touched

Open Logic Test.fbeproj in FutureBasic, build and run. The same scenarios run here in
Python: python3 tools/logic_reference.py --test <db.sqlite>
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sqlite_model  # noqa: E402

RUNTIME = ['Data SQLite.incl', 'DataObject.glbl', 'DataObject_Super.incl', 'DataObject.incl',
           'Data Model.incl', 'Data Records.incl', 'Logic Rules.incl', 'Logic Row.incl', 'Logic Engine.incl']

RULES = r'''/*
 *   Logic Test Rules.incl - the rules of the acceptance scenarios (tools/logic_reference.py)
 */

// OrderDetail.Amount = Quantity * UnitPrice
local fn OrderDetailAmount( logicRow as LogicRowRef ) as CFTypeRef
end fn = fn NumberWithDouble( fn LogicDouble( logicRow, @"Quantity" ) * fn LogicDouble( logicRow, @"UnitPrice" ) )


// OrderDetail.Discount = 5% above 1000 - reads Amount, so it must run after it
local fn OrderDetailDiscount( logicRow as LogicRowRef ) as CFTypeRef
double discount = 0.0
if ( fn LogicDouble( logicRow, @"Amount" ) > 1000.0 ) then discount = 0.05
end fn = fn NumberWithDouble( discount )


local fn OrderDetailQuantityPositive( logicRow as LogicRowRef ) as BOOL
end fn = ( fn LogicDouble( logicRow, @"Quantity" ) > 0.0 )


local fn CustomerCreditCheck( logicRow as LogicRowRef ) as BOOL
end fn = ( fn LogicDouble( logicRow, @"Balance" ) <= fn LogicDouble( logicRow, @"CreditLimit" ) )


void local fn DeclareRules
// declared in the "wrong" order on purpose
fn LogicFormula( @"OrderDetail", @"Discount", @fn OrderDetailDiscount, @[ @"Amount" ] )
fn LogicFormula( @"OrderDetail", @"Amount", @fn OrderDetailAmount, @[ @"Quantity", @"UnitPrice" ] )
fn LogicConstraint( @"OrderDetail", @fn OrderDetailQuantityPositive, @"Quantity {Quantity} must be more than 0" )
fn LogicConstraint( @"Customer", @fn CustomerCreditCheck, @"Customer balance ({row.Balance}) exceeds credit limit ({row.CreditLimit})" )
end fn
'''

MAIN = r'''/*
 *   Logic Test.main - LogicBank for FutureBasic, acceptance scenarios
 *   (the same as tools/logic_reference.py; results in the NSLog window)
 */

begin globals
long gTestsRun
long gTestsFailed
end globals


void local fn Check( testName as StringRef, passed as BOOL, detail as StringRef )
gTestsRun++
if ( passed )
NSLog( @"PASS  %@", testName )
else
gTestsFailed++
NSLog( @"FAIL  %@   [%@]", testName, detail )
end if
end fn


local fn OrderDetailCount as long
end fn = fn ArrayCount( fn DataFetch( @"OrderDetail", @{ @"OrderId":fn NumberWithInteger( 10248 ) }, NULL ) )


local fn NewItem( quantity as long ) as MutableDictionaryRef
MutableDictionaryRef item = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( item, fn NumberWithInteger( 10248 ), @"OrderId" )
MutableDictionarySetObjectForKey( item, fn NumberWithInteger( 11 ), @"ProductId" )
MutableDictionarySetObjectForKey( item, fn NumberWithDouble( 14.0 ), @"UnitPrice" )
MutableDictionarySetObjectForKey( item, fn NumberWithInteger( quantity ), @"Quantity" )
MutableDictionarySetObjectForKey( item, fn NumberWithDouble( 0.0 ), @"Discount" )
end fn = item


void local fn RunScenarios
MutableDictionaryRef item, upd, stored, customer, extra
ArrayRef             formulas
NumberRef            itemId
long                 before
BOOL                 inner, outer

fn DeclareRules
fn Check( @"activate", fn LogicActivate, @"" )
formulas = fn LogicRulesOf( @"OrderDetail", @"formulas" )
fn Check( @"formula order: Amount before Discount", fn StringIsEqual( fn DictionaryObjectForKey( fn ArrayObjectAtIndex( formulas, 0 ), @"attr" ), @"Amount" ), @"" )

before = fn OrderDetailCount
item = fn NewItem( 3 )
fn Check( @"insert computes Amount", fn LogicInsert( @"OrderDetail", item ) && fn NumberDoubleValue( fn DictionaryObjectForKey( item, @"Amount" ) ) == 42.0, fn LogicMessage )
itemId = fn DictionaryObjectForKey( item, @"Id" )
stored = fn DataFetchOne( @"OrderDetail", @{ @"Id":itemId } )
fn Check( @"insert stores Amount and the generated key", stored != NULL && fn NumberDoubleValue( fn DictionaryObjectForKey( stored, @"Amount" ) ) == 42.0, @"" )

upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, itemId, @"Id" )
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( 100 ), @"Quantity" )
fn Check( @"update recomputes Amount, then Discount (dependency order)", fn LogicUpdate( @"OrderDetail", upd, NULL ) && fn NumberDoubleValue( fn DictionaryObjectForKey( upd, @"Amount" ) ) == 1400.0 && fn NumberDoubleValue( fn DictionaryObjectForKey( upd, @"Discount" ) ) == 0.05, fn LogicMessage )

// Quantity and UnitPrice unchanged: Amount's formula is pruned, so a value set by hand stays
upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, itemId, @"Id" )
MutableDictionarySetObjectForKey( upd, @"2026-11-23", @"ShippedDate" )
MutableDictionarySetObjectForKey( upd, fn NumberWithDouble( 1.0 ), @"Amount" )
fn Check( @"update of an unrelated column prunes the formulas", fn LogicUpdate( @"OrderDetail", upd, NULL ) && fn NumberDoubleValue( fn DictionaryObjectForKey( fn DataFetchOne( @"OrderDetail", @{ @"Id":itemId } ), @"Amount" ) ) == 1.0, fn LogicMessage )

fn Check( @"constraint fails the insert", fn LogicInsert( @"OrderDetail", fn NewItem( 0 ) ) == NO, @"" )
fn Check( @"constraint message names the value", fn StringIsEqual( fn LogicMessage, @"Quantity 0 must be more than 0" ), fn LogicMessage )
fn Check( @"failed insert is rolled back", fn OrderDetailCount == before + 1, @"" )

customer = fn DataFetchOne( @"Customer", @{ @"Id":@"ALFKI" } )
upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, @"ALFKI", @"Id" )
MutableDictionarySetObjectForKey( upd, fn NumberWithDouble( fn NumberDoubleValue( fn DictionaryObjectForKey( customer, @"CreditLimit" ) ) + 1.0 ), @"Balance" )
fn Check( @"credit-limit constraint fails the update", fn LogicUpdate( @"Customer", upd, NULL ) == NO, @"" )
fn Check( @"credit-limit message", fn StringHasPrefix( fn LogicMessage, @"Customer balance (" ) && fn StringContainsString( fn LogicMessage, @"exceeds credit limit" ), fn LogicMessage )
fn Check( @"failed update leaves the stored row", fn ObjectIsEqual( fn DictionaryObjectForKey( fn DataFetchOne( @"Customer", @{ @"Id":@"ALFKI" } ), @"Balance" ), fn DictionaryObjectForKey( customer, @"Balance" ) ), @"" )

// nested transaction: an inner failure rolls back the outer work
fn DataBegin
extra = fn NewItem( 1 )
fn DataInsert( @"OrderDetail", extra )
inner = fn LogicInsert( @"OrderDetail", fn NewItem( 0 ) )
outer = fn DataEnd( YES )
fn Check( @"inner failure rolls back the outer transaction", inner == NO && outer == NO && fn OrderDetailCount == before + 1, @"" )

fn Check( @"delete", fn LogicDelete( @"OrderDetail", @{ @"Id":itemId } ) && fn DataFetchOne( @"OrderDetail", @{ @"Id":itemId } ) == NULL, fn LogicMessage )

// activation checks, on a separate rule set
gLogicRules = NULL
fn LogicFormula( @"OrderDetail", @"Amount", @fn OrderDetailAmount, @[ @"Discount" ] )
fn LogicFormula( @"OrderDetail", @"Discount", @fn OrderDetailDiscount, @[ @"Amount" ] )
fn Check( @"cycle is refused at activation", fn LogicOrderFormulas( @"OrderDetail" ) == NO, @"" )
fn Check( @"unknown attribute is refused at activation", fn LogicCheckNames( @{ @"entity":@"OrderDetail", @"attr":@"NoSuchColumn", @"dependsOn":@[ @"Quantity" ] } ) == NO, @"" )
gLogicActive = NO
fn Check( @"saves refuse until rules are active", fn LogicInsert( @"OrderDetail", fn NewItem( 3 ) ) == NO && fn StringContainsString( fn LogicMessage, @"not active" ), fn LogicMessage )

NSLog( @"logic test: %ld scenarios, %ld failed", gTestsRun, gTestsFailed )
end fn


isLoggingOn = YES
if ( fn DataOpen( NULL ) ) then fn RunScenarios
HandleEvents
'''


def model_json(db_path, database_path):
    resources = []
    for name, r in sorted(sqlite_model.read_model(db_path).items()):
        resources.append({
            'name': name, 'kind': r.get('kind', 'table'),
            'fields': [{'name': a['name'], 'type': a.get('type', ''), 'pk': a.get('pk', 0)} for a in r['attributes']],
            'keys': r.get('keys', []), 'keyKind': r.get('keyKind', 'none'),
            'relationships': r.get('relationships', []),
        })
    return {'project': 'Logic Test', 'database': database_path, 'resources': resources}


def cr(text):
    return text.replace('\r\n', '\n').replace('\n', '\r')


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    db, out = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    os.makedirs(os.path.join(out, 'Logic Test.fbeproj'), exist_ok=True)
    work_db = os.path.join(out, 'test.sqlite')
    shutil.copy(db, work_db)
    for name in RUNTIME:
        shutil.copy(os.path.join(ROOT, 'src', 'Runtime', name), os.path.join(out, name))
    with open(os.path.join(out, 'Logic Test Rules.incl'), 'w', newline='') as f:
        f.write(cr(RULES))
    with open(os.path.join(out, 'Logic Test.main'), 'w', newline='') as f:
        f.write(cr(MAIN))
    with open(os.path.join(out, 'Model.json'), 'w') as f:
        json.dump(model_json(db, work_db), f, indent=2)
    shutil.copy(os.path.join(ROOT, 'src', 'Templates', 'Project', 'Settings2.plist'),
                os.path.join(out, 'Logic Test.fbeproj', 'Settings2.plist'))
    project = ['include "NSLog.incl"', '// "Runtime" 1'] + [f'include "{n}"' for n in RUNTIME] + \
              ['// "Tests" 1', 'include "Logic Test Rules.incl"', '// "Resources" 1', 'resources "Model.json"',
               '// "Main" 1', 'include "Logic Test.main"']
    with open(os.path.join(out, 'Logic Test.fbeproj', 'data.fbproj'), 'w', newline='') as f:
        f.write(cr('\n'.join(project) + '\n'))
    print(f'Logic Test project in {out} - open "Logic Test.fbeproj" in FutureBasic, build and run.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
