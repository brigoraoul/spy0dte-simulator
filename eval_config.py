from strategies.strategies import *

"""Specifiy date (only applicable for eval by month or by day)"""
YEAR = 2025
MONTH = 1
DAY = 8


#--------------------------------------------------------------------------------------------------
# STRATEGY AND PARAMETERS
#--------------------------------------------------------------------------------------------------

"""strategy class"""
STRATEGY = DeHighInLowSimple()

"""
Parameter for DeHighInLowSimple strategy: When True, the decreasing highs / increasing lows 
should be detected in the 5-min index chart first, before checking other conditions in the
1-min index chart.
"""
CONFIRM_WITH_5MIN=True

"""
Parameter for DeHighInLowSimple strategy: When True, a trend line has to be broken for an entry
signal to be generated (see implementation in conditions.py).
"""
USE_TREND_LINE=True

"""
Parameter for DeHighInLowSimple strategy: When True, the stochastic RSI condition has to be met for
an entry signal to be generated. Usually this means stoch RSI with length 8 > 0.8 or < 0.2
(see implementation in conditions.py).
"""
USE_STOCH_RSI=False

"""
Daily time window (one hour back from trading view charts, e.g. 20:00 = 21:00 on trading view). Only
chart data within this time window will be considered.

Default setting:
    START_TIME = "14:30"
    END_TIME = "21:00"
"""
START_TIME = "14:30"
END_TIME = "21:00"


#--------------------------------------------------------------------------------------------------
# MONEY MANAGEMENT PARAMETERS
#--------------------------------------------------------------------------------------------------

"""stop loss limit and take profit limit"""
STOP_LOSS = 1
TAKE_PROFIT = 2

"""
Type of money management. Options: 'static' or 'trailing'. If 'static' the stop loss price is calculated
when an entry is generated as stop_loss_price = entry_price - stop_loss and not updated if the spread
price changes. If 'trailing', the initial stop loss price is calculated in the same way but updated 
whenever the spread price increases, but not when the spread price decreases.
"""
MM_TYPE = "static"


#--------------------------------------------------------------------------------------------------
# SPREAD CALCULATION OPTIONS
#--------------------------------------------------------------------------------------------------

# spread calculation (only one option should be true at the same time)
ENFORCE_ITM = False
MIDDLE_ITM = False
ENFORCE_OTM = True


#--------------------------------------------------------------------------------------------------
# CALCULATION OF EXITS OPTIONS
#--------------------------------------------------------------------------------------------------

"""
If 'EXIT_BASED_ON_CLOSE' is True, the close price of each bar is considered to determine the exit of
a trade. Meaning, the close price will be compared to the (current) stop loss price and take profit 
price. If 'EXIT_BASED_ON_CLOSE' is False, instead the high price of the current bar will be compared to
the take profit price and the low price of the current bar will be compared to the stop loss price.

Default setting: True
"""
EXIT_BASED_ON_CLOSE = True

"""
If 'EXIT_W_OPEN' is True, the exit price is determined by taking the open price of the bar that follows
the bar for which an exit signal was generated.
"""
EXIT_W_OPEN = True

"""
If 'EXIT_W_MIDPOINT' is True, the exit price is determined by taking the midpoint of the bar that follows
the bar for which an exit signal was generated. The midpoint is calculated as the middle between the 
high and the low price of that bar.
"""
EXIT_W_MIDPOINT = False  # only for logging purposes

"""
If 'EXIT_W_MM' is True, the exit price is determined by the money management parameters. If the stop loss
limit triggered the exit of a trade, the profit of that trade equals -STOP_LOSS. If the take profit
limit triggered the exit of a trade, the profit of that trade equals TAKE_PROFIT. 
"""
EXIT_W_MM = False

