from necessary_import import *

'''
OBJECTIVE
---------
Have a code that is fully compatible between Zipline and Quantopian, and that can be debug under Linux/Spyder.

-> To investigate Zip & Quant results : significative discrepencies on returns and the number of switches between pairs.


STRATEGY
--------
Lit.rev
    http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1917044
    Paired-switching for tactical portfolio allocation

Starting from the end of the first full week of the year, we look at the performance of the two equities
over the prior thirteen weeks (the ranking period), and buy the equity that has the higher return during
the ranking period. The position is held for thirteen weeks (the investment period). At the end of the
investment period the cycle is repeated.

Obviously, the number of weeks in the ranking period and the investment period can be varied
(independently) to optimize the strategy for a given pair of equities. Although the inevitable concerns
on over-fitting associated with such an optimization can be addressed by means of an
appropriate cross-validation methodology


IMPLEMENTATION
--------------
-> FROM http://www.portfolio123.com/mvnforum/viewthread_thread,6472

SPY / TLT
rebalance period: 1st day of month
ranking period: 4months
investment period: 1 month
'''

def initialize(context):
    context.stocks = [symbol('SPY'), symbol('TLT')]
    context.nbSwitch = 0

    context.lookback = 4*21 # 4 months period, 21 trading days per month

    context.Periodicity = 1 # every x period ; 1 means every period
    context.periodCount = 0

    context.cagr_period = 0
    context.portf_allocation = 0.9

    context.max_priceslippage = (float(0.5)/100)


    context.env = get_environment('platform')
    if context.env == 'quantopian':

        set_commission(commission.PerTrade(cost=4.0))
        set_slippage(slippage.FixedSlippage(spread=0.00))
        schedule_function(ordering_logic,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))

        schedule_function(get_cagr,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=5, minutes=0))
    elif context.env == 'zipline':

        context.set_commission(commission.PerTrade(cost=4.0))
        context.set_slippage(slippage.FixedSlippage(spread=0.00))
        context.schedule_function(ordering_logic,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))

        context.schedule_function(get_cagr,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=5, minutes=0))

        context.startDate = datetime(2003, 1, 1, 0, 0, 0, 0, pytz.utc)
        context.endDate = datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc)

    '''
    get_environment(field='platform')
    Returns information about the environment in which the backtest or live algorithm is running.
    If no parameter is passed, the platform value is returned. Pass * to get all the values returned in a dictionary.
    To use this method when running Zipline standalone, import get_environment from the zipline.api library.

    Parameters
    arena: Returns IB, live (paper trading), or backtest.
    data_frequency: Returns minute or daily.
    start: Returns the UTC datetime for start of backtest. In IB and live arenas, this is when the live algorithm was deployed.
    end: Returns the UTC datetime for end of backtest. In IB and live arenas, this is the trading day's close datetime.
    capital_base: Returns the float of the original capital in USD.
    platform: Returns the platform running the algorithm: quantopian or zipline.
    '''
    context.limit_order = None
    if get_environment('arena') == 'backtest':
        if get_environment('data_frequency') == 'daily':
            context.limit_order = False
        elif get_environment('data_frequency') == 'minute':
            context.limit_order = True
    elif get_environment('arena') == 'live' or get_environment('arena') == 'IB':
        context.limit_order = True

    return

def ordering_logic(context, data):

    context.periodCount += 1

    # execute modulo context.Periodicity
    if context.periodCount % context.Periodicity == 0:
        ror = stockMetrics (context,data, context.lookback)
        if (ror[0] > ror[1]):
            allin(0, context, data)
        else:
            allin(1,context, data)

    return

def allin (stockid, context, data):
    status = context.portfolio.positions[context.stocks[stockid]].amount
    if status > 0:
        # do nothing, we are already invested
        pass

    else:
        context.nbSwitch +=1
        print("Date "+ str(data[context.stocks[0]].datetime) +"   Switch Nb: " +str(context.nbSwitch))

        up = context.stocks[stockid]
        if (stockid == 0):
            dwn = context.stocks[1]
        else:
            dwn = context.stocks[0]

        if context.limit_order:
            lp1 = round(data[up].price*(1 +context.max_priceslippage),2)
            lp2 = round(data[dwn].price*(1 -context.max_priceslippage),2)

            order_target_percent(up, 1 *context.portf_allocation, style=LimitOrder(limit_price =lp1))
            order_target_percent(dwn, 0, style=LimitOrder(limit_price =lp2))
        else:
            order_target_percent(up, 1 *context.portf_allocation)
            order_target_percent(dwn, 0)

    return

def handle_data(context, data):
    # visually check for tapping in the margin
    check_cash_status(context)
    record(leverage=context.account.leverage)
    return
