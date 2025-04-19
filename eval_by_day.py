# Evaluating a strategy on one day

import pandas as pd
from datetime import date
from strategies.conditions import Conditions
from strategies.strategies import DeHighInLowSimple, LHLFormation
#from strategies.strat_lhl_formation import LHLFormation
from data.data_processing import Preprocessor
from utils.chart_visualization import *
from utils.options_helper import *
from utils.report_utils import *
import eval_config


target_date = date(eval_config.YEAR, eval_config.MONTH, eval_config.DAY)

# 1. load test data files for target date
month_str = target_date.strftime("%Y-%m")
index_file_paths = [  # has to include all files necessary for the test a strategy
    f"dev/data/polygon/index_flat_files/1_min_aggregates/{month_str}.csv",
    f"dev/data/polygon/index_flat_files/5_min_aggregates/{month_str}.csv"
]
data = []
for file_path in index_file_paths:
    file = pd.read_csv(file_path)
    data.append(file)
    

# 2. Pre-process data: split data per day, extract target date, calculate indicators, and filter data for time window

# group dataframe by day (maintain order of the days)
data = [Preprocessor.split_by_day(df) for df in data]

# extract target date from each file
data_ = []
if target_date is not None:
    for file in data:
        day = file[target_date] # Throws exception if target date is not available
        data_.append(day)

# calculate indicators
data_ = [Conditions.get_all(df) for df in data_]

# get relevant time window
data_ = [Preprocessor.get_time_window_data(df, start_time=eval_config.START_TIME, end_time=eval_config.END_TIME) for df in data_]


# 3. Apply strategy, to get entry signals
strategy = DeHighInLowSimple()

# DeHighInLow
if not strategy.__class__.__name__ == "LHLFormation":
    entry_signals = strategy.generate_entries(data_[0], data_[1], 
                                        use_trend_line=eval_config.USE_TREND_LINE, 
                                        use_stoch_rsi=eval_config.USE_STOCH_RSI)

# LHLFormation
if strategy.__class__.__name__ == "LHLFormation":
    entry_signals = strategy.generate_entries(df_1min_index=data_[0], date=target_date,
                                        start_time=eval_config.START_TIME,
                                        end_time=eval_config.END_TIME,
                                        enforce_ITM=eval_config.ENFORCE_ITM,
                                        middle_ITM=eval_config.MIDDLE_ITM)


# 4. Get spread charts and apply strategy again, to get exit signals
spreads = get_spreads(entry_signals, target_date, eval_config.START_TIME, eval_config.END_TIME, enforce_ITM=eval_config.ENFORCE_ITM, middle_ITM=eval_config.MIDDLE_ITM, enforce_OTM=eval_config.ENFORCE_OTM)
trades, report_metrics = strategy.generate_trades(entry_signals, spreads, eval_config.STOP_LOSS, eval_config.TAKE_PROFIT, eval_config.EXIT_W_OPEN, eval_config.EXIT_W_MM, money_management=(eval_config.MM_TYPE, eval_config.EXIT_BASED_ON_CLOSE))

# 5. Evaluation
print(report_metrics)
total_profit = 0
for trade in trades:
    individual_profit = trade['profit']
    total_profit += individual_profit
    print(f"Trade profit: {individual_profit}")

print(f"Total combined profit: {total_profit}")

#print_signals(entry_signals)

# visualization of strategy signals
chart_title = f"{target_date} || Confirm with 5 min: {eval_config.CONFIRM_WITH_5MIN} || Use trend line: {eval_config.USE_TREND_LINE} || Use stoch RSI: {eval_config.USE_STOCH_RSI}"

#plot_candle_chart_with_markers(entry_signals, title=chart_title, signal_column_1="entry_bull_put", signal_column_2="entry_bear_call")
#plot_candle_chart_with_markers(entry_signals, title=chart_title, signal_column_1="lhl_formation", signal_column_2="lhl_first_low", signal_column_3="lhl_high")
#plot_candle_chart_with_markers(signals, title=chart_title, signal_column_1="bp_trend_line_signal", signal_column_2="bc_trend_line_signal")
