"""The Customs sample's business rules - the reference, run here by tools/logic_reference.py's engine
(the same engine, function for function, as LogicBank for FutureBasic in a generated app).
Research and sources: docs/research/Customs Clearance Research.md.

    value      a line's price paid (FOB) x the week's exchange rate, rounded first (Public Notice 17);
               CIF = value + freight + insurance, kept for statistics
    duty       ad valorem, specific (a unit) or both (compound), stepped above a value (cars); a relief
               claim (CPC 4071) only for an approved importer; wharfage (1.25 %) except personal baggage;
               a personal declaration's allowance (resident 300, visitor 50) takes its share of the duty
    manifest   a master bill's house bills' packages must add up; a late security filing is a risk
    risk       the score: the country, the importer's compliance points (when lodged), unregistered, first-time, a trusted
               trader's discount, undervalued lines, a broken seal, a late filing; the lane: green under
               30, yellow under 60, red; blue for a trusted trader chosen for audit; a random draw sends
               some to red whatever the score
    release    the first reason it cannot be released: no goods, prohibited goods, not arrived, a manifest
               mismatch, open holds, missing permits, a failed inspection, the lane's check not passed,
               unpaid and not on a statement - Releasable when none; Status R only then. Automatic
               release: the app (or ALS) releases every Releasable declaration - when the ship arrives,
               a permit is approved, a payment is made
    bond       an importer's open statements may owe no more than its bond; RequiredBond = 10 % of the
               year's duty, at least 10,000
    the gate   a truck goes out only with released goods, the transponder read, the declared seal, a cleared
               truck and driver, an approved route

FB: samples/Customs/Rules.incl (the same rules, for the generated app).
"""
import math
from datetime import date

ALLOWANCE = {'R': 300.0, 'V': 50.0}       # personal declarations: residents, visitors (BMD)
GREEN_BELOW, YELLOW_BELOW = 30, 60       # risk score lanes
RANDOM_RED = 0.03                         # the share sent to red whatever the score
MIN_BOND = 10000.0


def rounded(x, places=2):
    scale = 10 ** places
    return math.floor(x * scale + 0.5) / scale


def days_between(first, last):
    try:
        return (date.fromisoformat(str(last)[:10]) - date.fromisoformat(str(first)[:10])).days
    except (TypeError, ValueError):
        return None


def declare(logic):
    from logic_reference import Logic
    n, v = Logic.number, Logic.value

    def parent(lr, role, attr):
        return logic.parent_value(lr, role, attr)

    def pn(lr, role, attr):
        x = parent(lr, role, attr)
        try:
            return 0.0 if x is None else float(x)
        except (TypeError, ValueError):
            return 0.0

    def text(x):
        return '' if x is None else str(x)

    def truthy(x):
        try:
            return float(x) != 0
        except (TypeError, ValueError):
            return False

    def money(x):
        return f'{x:.2f}'

    # --- reference data ------------------------------------------------------------------------------------
    logic.constraint('Tariff', lambda lr: 0 <= n(lr, 'DutyRate') <= 300 and n(lr, 'SpecificRate') >= 0 and n(lr, 'RateAbove') >= 0,
                     'Tariff {Code}: rates cannot be negative, nor ad valorem over 300 percent')
    logic.constraint('ExchangeRate', lambda lr: n(lr, 'Rate') > 0, 'An exchange rate must be more than 0')
    logic.delete_action('Tariff', 'DeclarationLineList', 'prevent', 'Tariff {Code} is used by declarations')

    # --- importers and statements ----------------------------------------------------------------------------
    logic.count('Importer', 'DeclarationCount', 'DeclarationList')
    logic.sum('Importer', 'PenaltyPoints', 'DeclarationList', 'Penalties')
    logic.formula('Importer', 'CompliancePoints', lambda lr: int(max(0, n(lr, 'ComplianceBase') - n(lr, 'PenaltyPoints'))), ['ComplianceBase', 'PenaltyPoints'])
    logic.sum('Importer', 'StatementBalance', 'StatementList', 'Balance', lambda lr: v(lr, 'Status') == 'O')
    logic.constraint('Importer', lambda lr: n(lr, 'StatementBalance') <= n(lr, 'BondAmount'),
                     '{Name}: its statements would owe {StatementBalance}, more than its bond {BondAmount} - pay first')
    logic.sum('Importer', 'YearDuty', 'DeclarationList', 'TotalDuty', lambda lr: v(lr, 'Status') == 'R')
    logic.formula('Importer', 'RequiredBond', lambda lr: max(MIN_BOND, rounded(n(lr, 'YearDuty') * 0.10, 0)), ['YearDuty'])
    logic.formula('Importer', 'BondSufficient', lambda lr: 1 if n(lr, 'BondAmount') >= n(lr, 'RequiredBond') else 0, ['BondAmount', 'RequiredBond'])
    logic.delete_action('Importer', 'DeclarationList', 'prevent', '{Name} has declarations')
    logic.delete_action('Importer', 'StatementList', 'prevent', '{Name} has statements')

    logic.sum('Statement', 'Total', 'DeclarationList', 'AmountDue', lambda lr: v(lr, 'Status') == 'R')
    logic.sum('Statement', 'Paid', 'PaymentList', 'Amount')
    logic.formula('Statement', 'Balance', lambda lr: rounded(n(lr, 'Total') - n(lr, 'Paid')), ['Total', 'Paid'])
    logic.constraint('Statement', lambda lr: v(lr, 'Status') != 'C' or n(lr, 'Balance') <= 0, 'Statement {Period} still owes {Balance}: it cannot be closed')
    logic.constraint('Statement', lambda lr: truthy(parent(lr, 'Importer', 'OnStatement')), 'The importer does not pay on statements')

    # --- the manifest ---------------------------------------------------------------------------------------------
    logic.copy('Arrival', 'WharfageRate', 'PortOfEntry', 'WharfageRate')
    logic.delete_action('Arrival', 'ContainerList', 'prevent', 'Arrival {VoyageNumber} still has containers')
    logic.delete_action('Arrival', 'MasterBillList', 'prevent', 'Arrival {VoyageNumber} still has bills of lading')
    logic.count('MasterBill', 'HouseCount', 'HouseBillList')
    logic.sum('MasterBill', 'HousePackages', 'HouseBillList', 'Packages')
    logic.formula('MasterBill', 'ManifestMatch', lambda lr: 1 if n(lr, 'HouseCount') == 0 or n(lr, 'HousePackages') == n(lr, 'Packages') else 0,
                  ['HouseCount', 'HousePackages', 'Packages'])
    logic.copy('HouseBill', 'ArrivalId', 'MasterBill', 'ArrivalId')

    def late(lr):
        ahead = days_between(v(lr, 'SecurityFiled'), v(lr, 'LadingDate'))
        return 1 if ahead is None or ahead < 1 else 0
    logic.formula('HouseBill', 'LateFiling', late, ['SecurityFiled', 'LadingDate'])
    logic.delete_action('HouseBill', 'DeclarationList', 'prevent', 'House bill {Number} is declared')
    logic.delete_action('MasterBill', 'HouseBillList', 'cascade')

    # --- declaration lines -----------------------------------------------------------------------------------------
    logic.parent_check('DeclarationLine', 'Tariff', 'There is no tariff heading {TariffCode}')
    for attr in ('DutyRate', 'SpecificRate', 'StepAbove', 'RateAbove', 'AgencyCode', 'Prohibited', 'ReferencePrice'):
        logic.copy('DeclarationLine', attr, 'Tariff', attr)
    logic.formula('DeclarationLine', 'Value', lambda lr: rounded(n(lr, 'InvoiceValue') * pn(lr, 'Declaration', 'Rate')),
                  ['InvoiceValue', 'DeclarationId', 'Declaration.Rate'])

    def duty(lr):
        if truthy(v(lr, 'ReliefClaimed')):
            return 0.0
        value, step = n(lr, 'Value'), n(lr, 'StepAbove')
        if step > 0 and value > step:
            ad_valorem = step * n(lr, 'DutyRate') / 100 + (value - step) * n(lr, 'RateAbove') / 100
        else:
            ad_valorem = value * n(lr, 'DutyRate') / 100
        return rounded(ad_valorem + n(lr, 'Quantity') * n(lr, 'SpecificRate'))
    logic.formula('DeclarationLine', 'Duty', duty, ['ReliefClaimed', 'Value', 'StepAbove', 'DutyRate', 'RateAbove', 'Quantity', 'SpecificRate'])
    logic.formula('DeclarationLine', 'Wharfage',
                  lambda lr: 0.0 if parent(lr, 'Declaration', 'Kind') == 'P' else rounded(n(lr, 'Value') * pn(lr, 'Declaration', 'WharfageRate') / 100),
                  ['Value', 'DeclarationId', 'Declaration.Kind', 'Declaration.WharfageRate'])
    logic.formula('DeclarationLine', 'Undervalued',
                  lambda lr: 1 if n(lr, 'ReferencePrice') > 0 and n(lr, 'Quantity') > 0 and n(lr, 'Value') / n(lr, 'Quantity') < n(lr, 'ReferencePrice') / 2 else 0,
                  ['ReferencePrice', 'Quantity', 'Value'])
    logic.count('DeclarationLine', 'ApprovedPermits', 'PermitList', lambda lr: v(lr, 'Status') == 'A')
    logic.formula('DeclarationLine', 'PermitMissing', lambda lr: 1 if v(lr, 'AgencyCode') not in (None, '') and n(lr, 'ApprovedPermits') == 0 else 0,
                  ['AgencyCode', 'ApprovedPermits'])
    logic.constraint('DeclarationLine', lambda lr: n(lr, 'Quantity') > 0, 'Quantity {Quantity} must be more than 0')
    logic.constraint('DeclarationLine', lambda lr: n(lr, 'InvoiceValue') >= 0, 'Value {InvoiceValue} cannot be negative')
    logic.constraint('DeclarationLine', lambda lr: not truthy(v(lr, 'ReliefClaimed')) or truthy(parent(lr, 'Declaration', 'ReliefApproved')),
                     'Relief is claimed, but the importer is not approved for duty relief')
    logic.constraint('Permit', lambda lr: v(lr, 'AgencyCode') == parent(lr, 'DeclarationLine', 'AgencyCode'),
                     'Permit {Number} is from {AgencyCode}: the goods need another agency\'s')
    logic.delete_action('DeclarationLine', 'PermitList', 'cascade')

    # --- the declaration: value, duty, what is owed --------------------------------------------------------------
    logic.copy('Declaration', 'WharfageRate', 'Arrival', 'WharfageRate')
    # the master bill, for the manifest check: a house bill's own formula would read the master's totals before
    # they count that house bill, so the declaration reads the master bill itself
    logic.copy('Declaration', 'MasterBillId', 'HouseBill', 'MasterBillId')
    logic.formula('Declaration', 'Rate', lambda lr: pn(lr, 'ExchangeRate', 'Rate'), ['ExchangeRateId', 'ExchangeRate.Rate'])

    def rate_week(lr):
        since = days_between(parent(lr, 'ExchangeRate', 'WeekOf'), v(lr, 'LodgedDate'))
        return since is not None and 0 <= since < 7
    logic.constraint('Declaration', rate_week, 'Exchange rate {ExchangeRateId} is not the week the entry was lodged')
    # scored with the importer's compliance points as they were when it was lodged: a failed inspection on
    # this entry lowers the points for the importer's later entries (and a live read would be a cycle)
    logic.copy('Declaration', 'CompliancePoints', 'Importer', 'CompliancePoints')
    logic.formula('Declaration', 'ReliefApproved', lambda lr: 1 if truthy(parent(lr, 'Importer', 'ReliefApproved')) else 0, ['ImporterId', 'Importer.ReliefApproved'])
    logic.count('Declaration', 'LineCount', 'DeclarationLineList')
    logic.sum('Declaration', 'TotalValue', 'DeclarationLineList', 'Value')
    logic.sum('Declaration', 'TotalDuty', 'DeclarationLineList', 'Duty')
    logic.sum('Declaration', 'TotalWharfage', 'DeclarationLineList', 'Wharfage')
    logic.formula('Declaration', 'CifValue', lambda lr: rounded(n(lr, 'TotalValue') + rounded((n(lr, 'Freight') + n(lr, 'Insurance')) * n(lr, 'Rate'))),
                  ['TotalValue', 'Freight', 'Insurance', 'Rate'])
    logic.formula('Declaration', 'Allowance', lambda lr: ALLOWANCE.get(text(v(lr, 'Declarant')), 0.0) if v(lr, 'Kind') == 'P' else 0.0, ['Kind', 'Declarant'])
    logic.formula('Declaration', 'AllowanceDuty',
                  lambda lr: rounded(min(n(lr, 'Allowance'), n(lr, 'TotalValue')) * n(lr, 'TotalDuty') / n(lr, 'TotalValue')) if n(lr, 'TotalValue') > 0 else 0.0,
                  ['Allowance', 'TotalValue', 'TotalDuty'])
    logic.formula('Declaration', 'AmountDue', lambda lr: rounded(n(lr, 'TotalDuty') - n(lr, 'AllowanceDuty') + n(lr, 'TotalWharfage')),
                  ['TotalDuty', 'AllowanceDuty', 'TotalWharfage'])
    logic.sum('Declaration', 'Paid', 'PaymentList', 'Amount')
    logic.formula('Declaration', 'Balance', lambda lr: rounded(n(lr, 'AmountDue') - n(lr, 'Paid')), ['AmountDue', 'Paid'])
    logic.constraint('Declaration', lambda lr: n(lr, 'Paid') <= n(lr, 'AmountDue'), 'Entry {EntryNumber}: paid {Paid}, more than the {AmountDue} due')
    logic.constraint('Declaration', lambda lr: v(lr, 'StatementId') is None or parent(lr, 'Statement', 'ImporterId') == v(lr, 'ImporterId'),
                     'Statement {StatementId} is another importer\'s')
    logic.constraint('Declaration', lambda lr: v(lr, 'HouseBillId') is None or parent(lr, 'HouseBill', 'ArrivalId') == v(lr, 'ArrivalId'),
                     'House bill {HouseBillId} came on another arrival')
    logic.constraint('Declaration', lambda lr: v(lr, 'Kind') != 'P' or v(lr, 'Declarant') in ('R', 'V'),
                     'A personal declaration says resident (R) or visitor (V)')
    logic.constraint('Payment', lambda lr: n(lr, 'Amount') > 0, 'A payment must be more than 0')
    logic.constraint('Payment', lambda lr: (v(lr, 'DeclarationId') is None) != (v(lr, 'StatementId') is None),
                     'A payment is for a declaration or for a statement')

    # --- what can hold it ------------------------------------------------------------------------------------------
    logic.count('Declaration', 'ProhibitedLines', 'DeclarationLineList', lambda lr: truthy(v(lr, 'Prohibited')))
    logic.count('Declaration', 'PermitsMissing', 'DeclarationLineList', lambda lr: truthy(v(lr, 'PermitMissing')))
    logic.count('Declaration', 'UndervaluedLines', 'DeclarationLineList', lambda lr: truthy(v(lr, 'Undervalued')))
    logic.count('Declaration', 'OpenHolds', 'HoldList', lambda lr: truthy(v(lr, 'Open')))
    logic.count('Declaration', 'PassedChecks', 'InspectionList', lambda lr: v(lr, 'Result') == 'P')
    logic.count('Declaration', 'PassedExams', 'InspectionList', lambda lr: v(lr, 'Result') == 'P' and v(lr, 'Kind') in ('P', 'X'))
    logic.count('Declaration', 'FailedInspections', 'InspectionList', lambda lr: v(lr, 'Result') == 'F')
    logic.formula('Inspection', 'Penalty', lambda lr: 25 if v(lr, 'Result') == 'F' else 0, ['Result'])
    logic.sum('Declaration', 'Penalties', 'InspectionList', 'Penalty')
    logic.constraint('Hold', lambda lr: v(lr, 'Source') != 'A' or v(lr, 'AgencyCode') not in (None, ''), 'An agency hold names its agency')

    # --- risk and the lane ----------------------------------------------------------------------------------------
    def first_time(lr):
        since = days_between(parent(lr, 'Importer', 'RegisteredSince'), v(lr, 'LodgedDate'))
        return since is None or since < 365

    def risk(lr):
        score = pn(lr, 'Country', 'RiskWeight')
        score += (100 - n(lr, 'CompliancePoints')) / 2
        if not truthy(parent(lr, 'Importer', 'Registered')):
            score += 20
        if first_time(lr):
            score += 15
        if parent(lr, 'Importer', 'TrustedTrader') == 'AEO':
            score -= 30
        score += 20 * n(lr, 'UndervaluedLines')
        if v(lr, 'ContainerId') is not None and not truthy(parent(lr, 'Container', 'SealIntact')):
            score += 40
        if v(lr, 'HouseBillId') is not None and truthy(parent(lr, 'HouseBill', 'LateFiling')):
            score += 20
        return int(max(0, rounded(score, 0)))
    logic.formula('Declaration', 'RiskScore', risk,
                  ['CountryCode', 'Country.RiskWeight', 'ImporterId', 'CompliancePoints', 'Importer.Registered', 'Importer.RegisteredSince',
                   'LodgedDate', 'Importer.TrustedTrader', 'UndervaluedLines', 'ContainerId', 'Container.SealIntact', 'HouseBillId', 'HouseBill.LateFiling'])

    def lane(lr):
        if n(lr, 'RandomDraw') < RANDOM_RED:
            return 'R'
        score = n(lr, 'RiskScore')
        if score >= YELLOW_BELOW:
            return 'R'
        if score >= GREEN_BELOW:
            return 'Y'
        if parent(lr, 'Importer', 'TrustedTrader') == 'AEO' and truthy(v(lr, 'AuditFlag')):
            return 'B'
        return 'G'
    logic.formula('Declaration', 'Lane', lane, ['RandomDraw', 'RiskScore', 'Importer.TrustedTrader', 'AuditFlag'])

    # --- release ----------------------------------------------------------------------------------------------------
    def release_reason(lr):
        if n(lr, 'LineCount') == 0:
            return 'It declares no goods'
        if n(lr, 'ProhibitedLines') > 0:
            return 'Prohibited goods: they are seized, never released'
        if parent(lr, 'Arrival', 'ArrivedDate') in (None, ''):
            return 'The goods have not arrived'
        if v(lr, 'MasterBillId') is not None and not truthy(parent(lr, 'MasterBill', 'ManifestMatch')):
            return 'The manifest does not add up: the master bill\'s packages and its house bills differ'
        if n(lr, 'OpenHolds') > 0:
            return f'{int(n(lr, "OpenHolds"))} hold(s) open'
        if n(lr, 'PermitsMissing') > 0:
            return f'{int(n(lr, "PermitsMissing"))} line(s) need an agency permit'
        if n(lr, 'FailedInspections') > 0:
            return 'It failed an inspection'
        if v(lr, 'Lane') == 'R' and n(lr, 'PassedExams') == 0:
            return 'Red lane: it must pass a physical examination'
        if v(lr, 'Lane') == 'Y' and n(lr, 'PassedChecks') == 0:
            return 'Yellow lane: it must pass a document check'
        if n(lr, 'Balance') > 0 and v(lr, 'StatementId') is None:
            return f'{money(n(lr, "Balance"))} unpaid'
        return None
    logic.formula('Declaration', 'ReleaseReason', release_reason,
                  ['LineCount', 'ProhibitedLines', 'ArrivalId', 'Arrival.ArrivedDate', 'MasterBillId', 'MasterBill.ManifestMatch', 'OpenHolds',
                   'PermitsMissing', 'FailedInspections', 'Lane', 'PassedExams', 'PassedChecks', 'Balance', 'StatementId'])
    logic.formula('Declaration', 'Releasable', lambda lr: 1 if v(lr, 'ReleaseReason') in (None, '') else 0, ['ReleaseReason'])
    logic.constraint('Declaration', lambda lr: v(lr, 'Status') != 'R' or n(lr, 'Releasable') == 1, 'Entry {EntryNumber} is not released: {ReleaseReason}')
    # refuse first (payments, movements, inspections), then cascade (lines, holds)
    logic.delete_action('Declaration', 'PaymentList', 'prevent', 'Entry {EntryNumber} has payments: it cannot be deleted')
    logic.delete_action('Declaration', 'MovementList', 'prevent', 'Entry {EntryNumber} has moved through the gate')
    logic.delete_action('Declaration', 'InspectionList', 'prevent', 'Entry {EntryNumber} was inspected: the record stays')
    logic.delete_action('Declaration', 'DeclarationLineList', 'cascade')
    logic.delete_action('Declaration', 'HoldList', 'cascade')

    # --- the gate --------------------------------------------------------------------------------------------------
    def gate(lr):
        day = text(v(lr, 'MoveDate'))
        if parent(lr, 'Declaration', 'Status') != 'R':
            return 'The goods are not released yet'
        if n(lr, 'TransponderRead') == 0:
            return 'The truck\'s transponder was not read'
        declared, read = text(parent(lr, 'Container', 'SealNumber')), text(v(lr, 'ObservedSeal'))
        if read != declared:
            return f'Seal {read or "(none)"} does not match the declared seal {declared}'
        if text(parent(lr, 'Truck', 'ClearedUntil')) < day:
            return 'The truck is not cleared on ' + day
        if text(parent(lr, 'Driver', 'ClearedUntil')) < day:
            return 'The driver is not cleared on ' + day
        if not truthy(parent(lr, 'Route', 'Approved')):
            return 'The route is not registered and approved'
        return None
    logic.formula('Movement', 'Reason', gate,
                  ['DeclarationId', 'Declaration.Status', 'TransponderRead', 'ContainerId', 'Container.SealNumber', 'ObservedSeal',
                   'MoveDate', 'TruckId', 'Truck.ClearedUntil', 'DriverId', 'Driver.ClearedUntil', 'RouteId', 'Route.Approved'])
    logic.formula('Movement', 'Lane', lambda lr: 'G' if v(lr, 'Reason') in (None, '') else 'R', ['Reason'])
    logic.constraint('Movement', lambda lr: v(lr, 'Status') != 'O' or v(lr, 'Lane') == 'G', 'The gate stays closed: {Reason}')
    logic.constraint('Movement', lambda lr: v(lr, 'ContainerId') == parent(lr, 'Declaration', 'ContainerId'),
                     'Container {ContainerId} is not the one entry {DeclarationId} declares')
