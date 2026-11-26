"""The Telecom sample's business rules - the reference, run here by tools/logic_reference.py's engine
(the same engine, function for function, as LogicBank for FutureBasic in a generated app).

The pricing engine is rules over data, no code of its own:
    Country.CostPerDay   a typical day abroad (0.5 GB, 30 minutes, 20 texts) at the rates of the country's
                         preferred roaming agreement - recomputed when that agreement's rates change
    Country.DayPrice     CostPerDay x the zone's markup, rounded up to the next 5
    TravelPlanCountry    copies the day price when the leg is added (a quote keeps its price), is
                         free when the country is in the plan's home zone, Amount = Days x DayPrice
    TravelPlan.Price     the sum of its legs; purchased plans add up to the phone, the plan, the account -
                         and the account's credit limit can refuse the purchase

FB: samples/Telecom/Rules.incl (the same rules, for the generated app).
"""
import math
from datetime import date

TYPICAL_DAY = {'gb': 0.5, 'minutes': 30, 'texts': 20}   # what a day abroad is priced on
PRICE_STEP = 5.0                                          # day prices round up to the next 5


def days_between(first, last):
    """inclusive days from first to last (ISO dates); None when either is missing or unreadable"""
    try:
        return (date.fromisoformat(str(last)[:10]) - date.fromisoformat(str(first)[:10])).days + 1
    except (TypeError, ValueError):
        return None


def declare(logic):
    from logic_reference import Logic
    n, v = Logic.number, Logic.value

    def parent(lr, role, attr):
        return logic.parent_value(lr, role, attr)

    # --- the pricing world ---------------------------------------------------------------------
    def cost_per_day(lr):
        if v(lr, 'RoamingAgreementId') is None or parent(lr, 'RoamingAgreement', 'RatePerGB') is None:
            return None                                       # no partner network: no service
        cost = (TYPICAL_DAY['gb'] * float(parent(lr, 'RoamingAgreement', 'RatePerGB'))
                + TYPICAL_DAY['minutes'] * float(parent(lr, 'RoamingAgreement', 'RatePerMinute'))
                + TYPICAL_DAY['texts'] * float(parent(lr, 'RoamingAgreement', 'RatePerText')))
        return round(cost, 2)
    logic.formula('Country', 'CostPerDay', cost_per_day,
                  ['RoamingAgreementId', 'RoamingAgreement.RatePerGB', 'RoamingAgreement.RatePerMinute', 'RoamingAgreement.RatePerText'])

    def day_price(lr):
        if v(lr, 'CostPerDay') is None:
            return None
        markup = parent(lr, 'Zone', 'Markup')
        markup = 1.0 if markup is None else float(markup)
        return math.ceil(n(lr, 'CostPerDay') * markup / PRICE_STEP - 1e-9) * PRICE_STEP
    logic.formula('Country', 'DayPrice', day_price, ['CostPerDay', 'Zone.Markup'])

    logic.constraint('RoamingAgreement', lambda lr: str(v(lr, 'ValidTo')) >= str(v(lr, 'ValidFrom')),
                     'The agreement ends ({ValidTo}) before it starts ({ValidFrom})')
    logic.constraint('RoamingAgreement', lambda lr: min(n(lr, 'RatePerGB'), n(lr, 'RatePerMinute'), n(lr, 'RatePerText')) >= 0,
                     'Rates cannot be negative')

    # --- plans and phones ------------------------------------------------------------------------
    logic.copy('Plan', 'MonthlyPrice', 'PlanOffer', 'MonthlyPrice')
    logic.copy('Plan', 'MaxLines', 'PlanOffer', 'MaxLines')
    logic.copy('Plan', 'DataGB', 'PlanOffer', 'DataGB')
    logic.copy('Plan', 'ZoneId', 'PlanOffer', 'ZoneId')
    logic.count('Plan', 'PhoneCount', 'PhoneList')
    logic.constraint('Plan', lambda lr: n(lr, 'PhoneCount') <= n(lr, 'MaxLines'),
                     'The plan allows {MaxLines} phone(s); it would have {PhoneCount}')
    logic.copy('Phone', 'ZoneId', 'Plan', 'ZoneId')

    logic.sum('Phone', 'DataUsedGB', 'UsageList', 'DataGB')
    logic.sum('Plan', 'DataUsedGB', 'PhoneList', 'DataUsedGB')

    def data_over(lr):
        if v(lr, 'DataGB') is None:                           # unlimited
            return 0.0
        return round(max(0.0, n(lr, 'DataUsedGB') - n(lr, 'DataGB')), 3)
    logic.formula('Plan', 'DataOverGB', data_over, ['DataUsedGB', 'DataGB'])

    # --- travel plans ----------------------------------------------------------------------------
    logic.copy('TravelPlan', 'ZoneId', 'Phone', 'ZoneId')
    logic.formula('TravelPlan', 'Days', lambda lr: days_between(v(lr, 'StartDate'), v(lr, 'EndDate')), ['StartDate', 'EndDate'])
    logic.constraint('TravelPlan', lambda lr: str(v(lr, 'EndDate')) >= str(v(lr, 'StartDate')),
                     'The trip ends ({EndDate}) before it starts ({StartDate})')
    logic.constraint('TravelPlan', lambda lr: parent(lr, 'Phone', 'Status') == 'A' or v(lr, 'Status') != 'P',
                     'Phone {PhoneId} is not active: the travel plan cannot be bought')
    logic.count('TravelPlan', 'CountryCount', 'TravelPlanCountryList')
    logic.sum('TravelPlan', 'Price', 'TravelPlanCountryList', 'Amount')

    logic.formula('TravelPlanCountry', 'Days', lambda lr: days_between(v(lr, 'ArriveDate'), v(lr, 'LeaveDate')),
                  ['ArriveDate', 'LeaveDate'])
    logic.copy('TravelPlanCountry', 'DayPrice', 'Country', 'DayPrice')

    def included(lr):
        return 1 if parent(lr, 'Country', 'ZoneId') is not None and parent(lr, 'Country', 'ZoneId') == parent(lr, 'TravelPlan', 'ZoneId') else 0
    logic.formula('TravelPlanCountry', 'Included', included, ['CountryCode', 'Country.ZoneId', 'TravelPlan.ZoneId'])
    logic.formula('TravelPlanCountry', 'Amount',
                  lambda lr: 0.0 if n(lr, 'Included') else round(n(lr, 'Days') * n(lr, 'DayPrice'), 2),
                  ['Included', 'Days', 'DayPrice'])
    logic.constraint('TravelPlanCountry', lambda lr: str(v(lr, 'LeaveDate')) >= str(v(lr, 'ArriveDate')),
                     'Leaving {CountryCode} ({LeaveDate}) before arriving ({ArriveDate})')
    logic.constraint('TravelPlanCountry',
                     lambda lr: str(v(lr, 'ArriveDate')) >= str(parent(lr, 'TravelPlan', 'StartDate'))
                     and str(v(lr, 'LeaveDate')) <= str(parent(lr, 'TravelPlan', 'EndDate')),
                     '{CountryCode} ({ArriveDate} to {LeaveDate}) is outside the trip\'s dates')
    logic.constraint('TravelPlanCountry',
                     lambda lr: n(lr, 'Included') == 1 or parent(lr, 'Country', 'RoamingAgreementId') is not None,
                     'No partner network in {CountryCode}: there is no service there')
    logic.parent_check('TravelPlanCountry', 'Country', 'There is no country {CountryCode}')
    logic.delete_action('TravelPlan', 'TravelPlanCountryList', 'cascade')

    # --- what the account owes -------------------------------------------------------------------
    logic.sum('Phone', 'TravelTotal', 'TravelPlanList', 'Price', lambda lr: v(lr, 'Status') == 'P')
    logic.sum('Plan', 'TravelTotal', 'PhoneList', 'TravelTotal')
    logic.sum('Account', 'MonthlyCharges', 'PlanList', 'MonthlyPrice')
    logic.sum('Account', 'TravelCharges', 'PlanList', 'TravelTotal')
    logic.formula('Account', 'Balance', lambda lr: round(n(lr, 'MonthlyCharges') + n(lr, 'TravelCharges'), 2),
                  ['MonthlyCharges', 'TravelCharges'])
    logic.constraint('Account', lambda lr: n(lr, 'Balance') <= n(lr, 'CreditLimit'),
                     'Account {AccountNumber}: the balance {Balance} would exceed the credit limit {CreditLimit}')
    logic.delete_action('Account', 'PlanList', 'prevent', 'Account {AccountNumber} still has plans')
    logic.delete_action('Plan', 'PhoneList', 'prevent', 'The plan still has phones')
    logic.delete_action('Phone', 'TravelPlanList', 'cascade')
    logic.delete_action('Phone', 'UsageList', 'cascade')
