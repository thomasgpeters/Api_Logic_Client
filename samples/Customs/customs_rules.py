"""The Customs sample's business rules - the reference, run here by tools/logic_reference.py's engine
(the same engine, function for function, as LogicBank for FutureBasic in a generated app).

    duty        a line copies its tariff's rate (the rate when it was declared); Duty = Value x rate;
                the declaration adds its lines up, plus the port's processing fee; payments bring the
                balance down; released goods still owing count against the importer's deferment bond
    lane        a declaration is pre-cleared - the green lane - when it was lodged before the goods
                arrived, by a registered importer, with every licence its goods need; otherwise red:
                it must pass an inspection before it is released, and a failed inspection holds it
    the gate    a movement out of the port goes through only when the declaration is released, the
                transponder was read, the seal read matches the one declared, the truck and the driver
                are cleared on the day, and the route is registered and approved - else it says why

FB: samples/Customs/Rules.incl (the same rules, for the generated app).
"""


def declare(logic):
    from logic_reference import Logic
    n, v = Logic.number, Logic.value

    def parent(lr, role, attr):
        return logic.parent_value(lr, role, attr)

    def text(x):
        return '' if x is None else str(x)

    def truthy(x):                                   # a BOOLEAN column: 1 / 0 / empty
        try:
            return float(x) != 0
        except (TypeError, ValueError):
            return False

    # --- the tariff -------------------------------------------------------------------------------
    logic.constraint('Tariff', lambda lr: 0 <= n(lr, 'DutyRate') <= 100, 'Duty rate {DutyRate} must be between 0 and 100 percent')

    # --- arrivals ---------------------------------------------------------------------------------
    logic.copy('Arrival', 'ProcessingFee', 'PortOfEntry', 'ProcessingFee')
    logic.delete_action('Arrival', 'ContainerList', 'prevent', 'Arrival {VoyageNumber} still has containers')

    # --- declaration lines: duty ----------------------------------------------------------------------
    logic.parent_check('DeclarationLine', 'Tariff', 'There is no tariff heading {TariffCode}')
    logic.copy('DeclarationLine', 'DutyRate', 'Tariff', 'DutyRate')
    logic.copy('DeclarationLine', 'LicenceRequired', 'Tariff', 'LicenceRequired')
    logic.formula('DeclarationLine', 'Duty', lambda lr: round(n(lr, 'Value') * n(lr, 'DutyRate') / 100.0, 2), ['Value', 'DutyRate'])
    logic.constraint('DeclarationLine', lambda lr: n(lr, 'Quantity') > 0, 'Quantity {Quantity} must be more than 0')
    logic.constraint('DeclarationLine', lambda lr: n(lr, 'Value') >= 0, 'Value {Value} cannot be negative')

    # --- the declaration: what is owed --------------------------------------------------------------
    logic.copy('Declaration', 'ProcessingFee', 'Arrival', 'ProcessingFee')
    logic.count('Declaration', 'LineCount', 'DeclarationLineList')
    logic.sum('Declaration', 'TotalValue', 'DeclarationLineList', 'Value')
    logic.sum('Declaration', 'TotalDuty', 'DeclarationLineList', 'Duty')
    logic.formula('Declaration', 'AmountDue', lambda lr: round(n(lr, 'TotalDuty') + n(lr, 'ProcessingFee'), 2), ['TotalDuty', 'ProcessingFee'])
    logic.sum('Declaration', 'Paid', 'PaymentList', 'Amount')
    logic.formula('Declaration', 'Balance', lambda lr: round(n(lr, 'AmountDue') - n(lr, 'Paid'), 2), ['AmountDue', 'Paid'])
    logic.constraint('Payment', lambda lr: n(lr, 'Amount') > 0, 'A payment must be more than 0')

    # --- the declaration: pre-clearance and release ----------------------------------------------------
    logic.count('Declaration', 'MissingLicences', 'DeclarationLineList',
                lambda lr: n(lr, 'LicenceRequired') != 0 and text(v(lr, 'LicenceNumber')).strip() == '')

    def pre_cleared(lr):
        arrival = parent(lr, 'Arrival', 'ArrivalDate')
        early = arrival is not None and text(v(lr, 'LodgedDate')) < str(arrival)
        registered = truthy(parent(lr, 'Importer', 'Registered'))
        return 1 if early and registered and n(lr, 'MissingLicences') == 0 and n(lr, 'LineCount') > 0 else 0
    logic.formula('Declaration', 'PreCleared', pre_cleared,
                  ['LodgedDate', 'ArrivalId', 'Arrival.ArrivalDate', 'ImporterId', 'Importer.Registered', 'MissingLicences', 'LineCount'])
    logic.formula('Declaration', 'Lane', lambda lr: 'G' if n(lr, 'PreCleared') else 'R', ['PreCleared'])
    logic.count('Declaration', 'PassedInspections', 'InspectionList', lambda lr: v(lr, 'Result') == 'P')
    logic.count('Declaration', 'FailedInspections', 'InspectionList', lambda lr: v(lr, 'Result') == 'F')
    logic.constraint('Declaration', lambda lr: v(lr, 'Status') != 'R' or n(lr, 'LineCount') > 0,
                     'Entry {EntryNumber} declares no goods: it cannot be released')
    logic.constraint('Declaration', lambda lr: v(lr, 'Status') != 'R' or v(lr, 'Lane') == 'G' or n(lr, 'PassedInspections') > 0,
                     'Entry {EntryNumber} is in the red lane: it must pass an inspection before it is released')
    logic.constraint('Declaration', lambda lr: v(lr, 'Status') != 'R' or n(lr, 'FailedInspections') == 0,
                     'Entry {EntryNumber} failed an inspection: it cannot be released')
    # order matters: refuse first (payments), then cascade (lines) - a cascade before the refusal would
    # change the entry (no goods left) and another rule would refuse it for the wrong reason
    logic.delete_action('Declaration', 'PaymentList', 'prevent', 'Entry {EntryNumber} has payments: it cannot be deleted')
    logic.delete_action('Declaration', 'DeclarationLineList', 'cascade')

    # --- the importer: the deferment bond --------------------------------------------------------------
    logic.count('Importer', 'DeclarationCount', 'DeclarationList')
    logic.sum('Importer', 'DeferredBalance', 'DeclarationList', 'Balance', lambda lr: v(lr, 'Status') == 'R')
    logic.constraint('Importer', lambda lr: n(lr, 'DeferredBalance') <= n(lr, 'BondAmount'),
                     '{Name}: released goods would owe {DeferredBalance}, more than the deferment bond {BondAmount} - pay first')
    logic.delete_action('Importer', 'DeclarationList', 'prevent', '{Name} has declarations')

    # --- the gate: pre-clearance of the movement ---------------------------------------------------------
    def reason(lr):
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
    logic.formula('Movement', 'Reason', reason,
                  ['DeclarationId', 'Declaration.Status', 'TransponderRead', 'ContainerId', 'Container.SealNumber', 'ObservedSeal',
                   'MoveDate', 'TruckId', 'Truck.ClearedUntil', 'DriverId', 'Driver.ClearedUntil', 'RouteId', 'Route.Approved'])
    logic.formula('Movement', 'Lane', lambda lr: 'G' if v(lr, 'Reason') in (None, '') else 'R', ['Reason'])
    logic.constraint('Movement', lambda lr: v(lr, 'Status') != 'O' or v(lr, 'Lane') == 'G',
                     'The gate stays closed: {Reason}')
    logic.constraint('Movement', lambda lr: v(lr, 'ContainerId') == parent(lr, 'Declaration', 'ContainerId'),
                     'Container {ContainerId} is not the one entry {DeclarationId} declares')
