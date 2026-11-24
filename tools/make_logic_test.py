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


// ---- aggregates: the canonical check-credit logic (nw/logic/readme_logic.md)

local fn OrderIsUnshipped( logicRow as LogicRowRef ) as BOOL
end fn = fn LogicIsEmpty( logicRow, @"ShippedDate" )


// OrderDetail.ShippedDate = Order.ShippedDate (a parent reference)
local fn OrderDetailShippedDate( logicRow as LogicRowRef ) as CFTypeRef
end fn = fn LogicParentValue( logicRow, @"Order", @"ShippedDate" )


void local fn DeclareAggregateRules
fn LogicFormula( @"OrderDetail", @"Amount", @fn OrderDetailAmount, @[ @"Quantity", @"UnitPrice" ] )
fn LogicFormula( @"OrderDetail", @"ShippedDate", @fn OrderDetailShippedDate, @[ @"Order.ShippedDate" ] )
fn LogicSum( @"Order", @"AmountTotal", @"OrderDetailList", @"Amount", NULL )
fn LogicCount( @"Order", @"OrderDetailCount", @"OrderDetailList", NULL )
fn LogicSum( @"Customer", @"Balance", @"OrderList", @"AmountTotal", @fn OrderIsUnshipped )
fn LogicCount( @"Customer", @"UnpaidOrderCount", @"OrderList", @fn OrderIsUnshipped )
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

end fn


local fn OrderRow( orderId as long ) as DictionaryRef
end fn = fn DataFetchOne( @"Order", @{ @"Id":fn NumberWithInteger( orderId ) } )


local fn CustomerRow( customerId as StringRef ) as DictionaryRef
end fn = fn DataFetchOne( @"Customer", @{ @"Id":customerId } )


local fn Num( aRecord as DictionaryRef, attrName as StringRef ) as double
end fn = fn LogicNumberOf( fn DictionaryObjectForKey( aRecord, attrName ) )


local fn OrderChange( orderId as long, attrName as StringRef, value as CFTypeRef ) as BOOL
MutableDictionaryRef upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( orderId ), @"Id" )
MutableDictionarySetObjectForKey( upd, value, attrName )
end fn = fn LogicUpdate( @"Order", upd, NULL )


local fn DetailOn( orderId as long, quantity as long ) as MutableDictionaryRef
MutableDictionaryRef item = fn NewItem( quantity )
MutableDictionarySetObjectForKey( item, fn NumberWithInteger( orderId ), @"OrderId" )
MutableDictionarySetObjectForKey( item, fn NumberWithDouble( 10.0 ), @"UnitPrice" )
end fn = item


void local fn RunAggregateScenarios
DictionaryRef        o0, c0, a0, o1, c1, o2, c2, c3, r0, o9
MutableDictionaryRef item, upd, shippedItem, newOrder, firstItem, upItem
NumberRef            itemId
long                 newId
BOOL                 ok, shipped, moved, back

gLogicRules = NULL
fn DeclareAggregateRules
fn Check( @"aggregates: activate", fn LogicActivate, @"" )
fn Check( @"aggregates: filed under the child", fn ArrayCount( fn LogicRulesOf( @"Order", @"aggregates" ) ) == 2, @"" )

o0 = fn OrderRow( 10643 ) : c0 = fn CustomerRow( @"ALFKI" ) : a0 = fn CustomerRow( @"ANATR" )
item = fn DetailOn( 10643, 2 )
ok = fn LogicInsert( @"OrderDetail", item )
itemId = fn DictionaryObjectForKey( item, @"Id" )
o1 = fn OrderRow( 10643 ) : c1 = fn CustomerRow( @"ALFKI" )
fn Check( @"aggregates: insert detail: Order.AmountTotal +20", ok && fn Num( o1, @"AmountTotal" ) == fn Num( o0, @"AmountTotal" ) + 20.0, fn LogicMessage )
fn Check( @"aggregates: insert detail: Order.OrderDetailCount +1", fn Num( o1, @"OrderDetailCount" ) == fn Num( o0, @"OrderDetailCount" ) + 1.0, @"" )
fn Check( @"aggregates: insert detail: chained to Customer.Balance +20", fn Num( c1, @"Balance" ) == fn Num( c0, @"Balance" ) + 20.0, @"" )
fn Check( @"aggregates: insert detail: parent reference (the order is unshipped)", fn DataIsNull( fn DictionaryObjectForKey( item, @"ShippedDate" ) ), @"" )

upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, itemId, @"Id" )
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( 5 ), @"Quantity" )
ok = fn LogicUpdate( @"OrderDetail", upd, NULL )
o2 = fn OrderRow( 10643 ) : c2 = fn CustomerRow( @"ALFKI" )
fn Check( @"aggregates: change quantity: Order +30, Balance +30", ok && fn Num( o2, @"AmountTotal" ) == fn Num( o1, @"AmountTotal" ) + 30.0 && fn Num( c2, @"Balance" ) == fn Num( c1, @"Balance" ) + 30.0, fn LogicMessage )

ok = fn LogicInsert( @"OrderDetail", fn DetailOn( 10643, 1000 ) )
fn Check( @"aggregates: credit limit: the chained constraint fails the detail insert", ok == NO && fn StringContainsString( fn LogicMessage, @"exceeds credit limit" ), fn LogicMessage )
fn Check( @"aggregates: credit limit: nothing changed", fn ObjectIsEqual( fn OrderRow( 10643 ), o2 ) && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ), @"" )

ok = fn OrderChange( 10643, @"ShippedDate", @"2026-11-24" )
c3 = fn CustomerRow( @"ALFKI" )
fn Check( @"aggregates: ship the order: Balance - AmountTotal, UnpaidOrderCount -1 (where no longer met)", ok && fn Num( c3, @"Balance" ) == fn Num( c2, @"Balance" ) - fn Num( o2, @"AmountTotal" ) && fn Num( c3, @"UnpaidOrderCount" ) == fn Num( c2, @"UnpaidOrderCount" ) - 1.0, fn LogicMessage )
ok = fn OrderChange( 10643, @"ShippedDate", fn DataNull )
fn Check( @"aggregates: unship: back again", ok && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ), fn LogicMessage )

ok = fn OrderChange( 10643, @"CustomerId", @"ANATR" )
fn Check( @"aggregates: re-parent over the new customer's credit limit fails (ANATR limit 1000)", ok == NO && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ) && fn ObjectIsEqual( fn CustomerRow( @"ANATR" ), a0 ), fn LogicMessage )

shipped = fn OrderChange( 10643, @"ShippedDate", @"2026-11-24" )
moved   = fn OrderChange( 10643, @"CustomerId", @"ANATR" )
fn Check( @"aggregates: re-parent a shipped order: both balances unchanged (where not met), counts unchanged", shipped && moved && fn Num( fn CustomerRow( @"ANATR" ), @"Balance" ) == fn Num( a0, @"Balance" ) && fn Num( fn CustomerRow( @"ANATR" ), @"UnpaidOrderCount" ) == fn Num( a0, @"UnpaidOrderCount" ), fn LogicMessage )
back = fn OrderChange( 10643, @"CustomerId", @"ALFKI" )
if ( back ) then back = fn OrderChange( 10643, @"ShippedDate", fn DataNull )
fn Check( @"aggregates: re-parent back and unship", back && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ), fn LogicMessage )

// test setup on the copy, outside the rules: room for the order under ANATR's limit
fn DataExecute( @"UPDATE \"Customer\" SET \"CreditLimit\" = 5000 WHERE \"Id\" = 'ANATR'", NULL, NULL )
r0 = fn CustomerRow( @"ANATR" )
ok = fn OrderChange( 10643, @"CustomerId", @"ANATR" )
fn Check( @"aggregates: re-parent to ANATR (room under its limit): ALFKI -, ANATR +, counts move", ok && fn Num( fn CustomerRow( @"ALFKI" ), @"Balance" ) == fn Num( c2, @"Balance" ) - fn Num( o2, @"AmountTotal" ) && fn Num( fn CustomerRow( @"ANATR" ), @"Balance" ) == fn Num( r0, @"Balance" ) + fn Num( o2, @"AmountTotal" ) && fn Num( fn CustomerRow( @"ANATR" ), @"UnpaidOrderCount" ) == fn Num( r0, @"UnpaidOrderCount" ) + 1.0, fn LogicMessage )
ok = fn OrderChange( 10643, @"CustomerId", @"ALFKI" )
fn Check( @"aggregates: re-parent back from ANATR", ok && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ) && fn Num( fn CustomerRow( @"ANATR" ), @"Balance" ) == fn Num( r0, @"Balance" ), fn LogicMessage )

o9 = fn OrderRow( 10692 )
shippedItem = fn DetailOn( 10692, 1 )
ok = fn LogicInsert( @"OrderDetail", shippedItem )
fn Check( @"aggregates: parent reference: a detail on a shipped order takes its ShippedDate", ok && fn ObjectIsEqual( fn DictionaryObjectForKey( shippedItem, @"ShippedDate" ), fn DictionaryObjectForKey( o9, @"ShippedDate" ) ), fn LogicMessage )
fn Check( @"aggregates: detail on a shipped order: AmountTotal +10, Balance unchanged (where not met)", fn Num( fn OrderRow( 10692 ), @"AmountTotal" ) == fn Num( o9, @"AmountTotal" ) + 10.0 && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ), fn LogicMessage )
fn LogicDelete( @"OrderDetail", @{ @"Id":fn DictionaryObjectForKey( shippedItem, @"Id" ) } )

// LB-41: derived totals belong to the rules
upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( 10643 ), @"Id" )
MutableDictionarySetObjectForKey( upd, fn NumberWithDouble( 99999.0 ), @"AmountTotal" )
MutableDictionarySetObjectForKey( upd, @"x", @"ShipName" )
ok = fn LogicUpdate( @"Order", upd, NULL )
fn Check( @"aggregates: LB-41: a client write to Order.AmountTotal keeps the stored value", ok && fn Num( fn OrderRow( 10643 ), @"AmountTotal" ) == fn Num( o2, @"AmountTotal" ) && fn StringIsEqual( fn DictionaryObjectForKey( fn OrderRow( 10643 ), @"ShipName" ), @"x" ) && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ), fn LogicMessage )
fn OrderChange( 10643, @"ShipName", fn DictionaryObjectForKey( o2, @"ShipName" ) )
upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, @"ALFKI", @"Id" )
MutableDictionarySetObjectForKey( upd, fn NumberWithDouble( 0.0 ), @"Balance" )
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( 0 ), @"UnpaidOrderCount" )
ok = fn LogicUpdate( @"Customer", upd, NULL )
fn Check( @"aggregates: LB-41: a client write to Customer.Balance / UnpaidOrderCount keeps the stored values", ok && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ), fn LogicMessage )

newOrder = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( newOrder, @"ALFKI", @"CustomerId" )
MutableDictionarySetObjectForKey( newOrder, fn NumberWithInteger( 1 ), @"EmployeeId" )
MutableDictionarySetObjectForKey( newOrder, fn NumberWithDouble( 500.0 ), @"AmountTotal" )
MutableDictionarySetObjectForKey( newOrder, fn NumberWithInteger( 7 ), @"OrderDetailCount" )
ok = fn LogicInsert( @"Order", newOrder )
if ( ok == NO )
fn Check( @"aggregates: new order: the rest of its scenarios could not run", NO, fn LogicMessage )
else
newId = fn NumberIntegerValue( fn DictionaryObjectForKey( newOrder, @"Id" ) )
fn Check( @"aggregates: LB-41: a new order starts with AmountTotal 0 and OrderDetailCount 0", fn Num( fn OrderRow( newId ), @"AmountTotal" ) == 0.0 && fn Num( fn OrderRow( newId ), @"OrderDetailCount" ) == 0.0, @"" )
fn Check( @"aggregates: new unshipped order: Customer.UnpaidOrderCount +1, Balance unchanged", fn Num( fn CustomerRow( @"ALFKI" ), @"UnpaidOrderCount" ) == fn Num( c2, @"UnpaidOrderCount" ) + 1.0 && fn Num( fn CustomerRow( @"ALFKI" ), @"Balance" ) == fn Num( c2, @"Balance" ), @"" )
firstItem = fn DetailOn( newId, 3 )
ok = fn LogicInsert( @"OrderDetail", firstItem )
fn Check( @"aggregates: first detail of the new order: AmountTotal 30, Balance +30", ok && fn Num( fn OrderRow( newId ), @"AmountTotal" ) == 30.0 && fn Num( fn CustomerRow( @"ALFKI" ), @"Balance" ) == fn Num( c2, @"Balance" ) + 30.0, fn LogicMessage )

// upsert: Studio's fourth operation
upItem = fn DetailOn( newId, 2 )
MutableDictionarySetObjectForKey( upItem, fn NumberWithInteger( 42 ), @"ProductId" )
MutableDictionarySetObjectForKey( upItem, fn NumberWithDouble( 5.0 ), @"UnitPrice" )
ok = fn LogicUpsert( @"OrderDetail", upItem )
fn Check( @"aggregates: upsert without a key inserts (Amount 10, order 40)", ok && fn DictionaryObjectForKey( upItem, @"Id" ) != NULL && fn Num( fn OrderRow( newId ), @"AmountTotal" ) == 40.0, fn LogicMessage )
upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, fn DictionaryObjectForKey( upItem, @"Id" ), @"Id" )
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( 4 ), @"Quantity" )
ok = fn LogicUpsert( @"OrderDetail", upd )
fn Check( @"aggregates: upsert with an existing key updates (Amount 20, order 50)", ok && fn Num( fn OrderRow( newId ), @"AmountTotal" ) == 50.0 && fn ArrayCount( fn DataFetch( @"OrderDetail", @{ @"OrderId":fn NumberWithInteger( newId ) }, NULL ) ) == 2, fn LogicMessage )
upd = fn DetailOn( newId, 1 )
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( 999999 ), @"Id" )
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( 42 ), @"ProductId" )
MutableDictionarySetObjectForKey( upd, fn NumberWithDouble( 1.0 ), @"UnitPrice" )
ok = fn LogicUpsert( @"OrderDetail", upd )
fn Check( @"aggregates: upsert with an unknown key inserts it (order 51)", ok && fn DataFetchOne( @"OrderDetail", @{ @"Id":fn NumberWithInteger( 999999 ) } ) != NULL && fn Num( fn OrderRow( newId ), @"AmountTotal" ) == 51.0, fn LogicMessage )
upd = fn MutableDictionaryNew
MutableDictionarySetObjectForKey( upd, fn DictionaryObjectForKey( upItem, @"Id" ), @"Id" )
MutableDictionarySetObjectForKey( upd, fn NumberWithInteger( 10000 ), @"Quantity" )
ok = fn LogicUpsert( @"OrderDetail", upd )
fn Check( @"aggregates: upsert update over the credit limit is refused, nothing changed", ok == NO && fn StringContainsString( fn LogicMessage, @"exceeds credit limit" ) && fn Num( fn OrderRow( newId ), @"AmountTotal" ) == 51.0, fn LogicMessage )

fn LogicDelete( @"OrderDetail", @{ @"Id":fn NumberWithInteger( 999999 ) } )
fn LogicDelete( @"OrderDetail", @{ @"Id":fn DictionaryObjectForKey( upItem, @"Id" ) } )
fn LogicDelete( @"OrderDetail", @{ @"Id":fn DictionaryObjectForKey( firstItem, @"Id" ) } )
ok = fn LogicDelete( @"Order", @{ @"Id":fn NumberWithInteger( newId ) } )
fn Check( @"aggregates: delete the new order: the customer is back as before", ok && fn ObjectIsEqual( fn CustomerRow( @"ALFKI" ), c2 ), fn LogicMessage )
end if

ok = fn LogicDelete( @"OrderDetail", @{ @"Id":itemId } )
fn Check( @"aggregates: delete detail: Order and Balance back to the start", ok && fn Num( fn OrderRow( 10643 ), @"AmountTotal" ) == fn Num( o0, @"AmountTotal" ) && fn Num( fn CustomerRow( @"ALFKI" ), @"Balance" ) == fn Num( c0, @"Balance" ), fn LogicMessage )
end fn


isLoggingOn = YES
if ( fn DataOpen( NULL ) )
fn RunScenarios
fn RunAggregateScenarios
NSLog( @"logic test: %ld scenarios, %ld failed", gTestsRun, gTestsFailed )
end if
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
    if argv and argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
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
