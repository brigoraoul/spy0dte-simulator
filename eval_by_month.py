# Evaluating a strategy
# 1. Specify and load test data files
# 2. Pre-process data: calculate indicators and split data per day
# 3. Apply strategy, to get entry and exit signals
# 4. Calculate evaluation metrics, create eval report

import mlflow
import pandas as pd
from collections import OrderedDict
from datetime import date, datetime
from data.data_processing import Preprocessor
from strategies.conditions import Conditions
from strategies.strategies import *
from utils.report_utils import *
from utils.chart_visualization import *
from utils.options_helper import *
import eval_config

mlflow.set_experiment("ZeroTheta Eval By Month")
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("_YEAR", eval_config.YEAR)
    mlflow.log_param("_MONTH", eval_config.MONTH)
    mlflow.log_param("strategy/CONFIRM_WITH_5MIN", eval_config.CONFIRM_WITH_5MIN)
    mlflow.log_param("strategy/USE_TREND_LINE", eval_config.USE_TREND_LINE)
    mlflow.log_param("strategy/USE_STOCH_RSI", eval_config.USE_STOCH_RSI)
    mlflow.log_param("__START_TIME", eval_config.START_TIME)
    mlflow.log_param("__END_TIME", eval_config.END_TIME)
    mlflow.log_param("mm/STOP_LOSS", eval_config.STOP_LOSS)
    mlflow.log_param("mm/TAKE_PROFIT", eval_config.TAKE_PROFIT)
    mlflow.log_param("mm/MM_TYPE", eval_config.MM_TYPE)
    mlflow.log_param("mm/EXIT_BASED_ON_CLOSE", eval_config.EXIT_BASED_ON_CLOSE)
    mlflow.log_param("EXIT_W_OPEN", eval_config.EXIT_W_OPEN)
    mlflow.log_param("EXIT_W_MIDPOINT", eval_config.EXIT_W_MIDPOINT)
    mlflow.log_param("spread_calc/ENFORCE_ITM", eval_config.ENFORCE_ITM)
    mlflow.log_param("spread_calc/MIDDLE_ITM", eval_config.MIDDLE_ITM)
    mlflow.log_param("strategy/STRATEGY", eval_config.STRATEGY.__class__.__name__)


    # 1. load test data files for target date
    month_str = f"{eval_config.YEAR}-{eval_config.MONTH:02d}"
    index_file_paths = [  # has to include all files necessary for the test a strategy
        f"dev/data/polygon/index_flat_files/1_min_aggregates/{month_str}.csv",
        f"dev/data/polygon/index_flat_files/5_min_aggregates/{month_str}.csv"
    ]
    data = []
    for file_path in index_file_paths:
        file = pd.read_csv(file_path)
        data.append(file)


    # 2. Pre-process data: calculate indicators and split data per day
    # 2.1 group dataframe by day (maintain order of the days) and filter for dates
    # that are present in all files
    data = [Preprocessor.split_by_day(df) for df in data]
    common_dates = {
        date for date in (set(data[0].keys()) & set(data[1].keys()))
        if date.year == eval_config.YEAR and date.month == eval_config.MONTH
    }
    data = [OrderedDict((key, value) for key, value in d.items() if key in common_dates) for d in data]

    # 2.2 calculate indicators
    data = [
        OrderedDict((key, Conditions.get_all(df)) for key, df in file.items())
        for file in data
    ]

    # 2.3 get relevant time window
    data = [
        OrderedDict((key, Preprocessor.get_time_window_data(df, start_time=eval_config.START_TIME, end_time=eval_config.END_TIME)) for key, df in file.items())
        for file in data
    ]

    # 3. Apply strategy, to get entry and exit signals
    strategy = eval_config.STRATEGY
    signals_dict = OrderedDict()

    # apply 'generate_signals' once for each date and store results in ordered dict
    for date in common_dates:
        df_1min_index = data[0][date]
        df_5min_index = data[1][date]
        signals = strategy.generate_entries(df_1min_index, df_5min_index, use_trend_line=eval_config.USE_TREND_LINE, use_stoch_rsi=eval_config.USE_STOCH_RSI)
        signals_dict[date] = signals


    # 4. Get spread charts and generate trades
    trades_dict = OrderedDict()
    for date, signals in signals_dict.items():
        spreads = get_spreads(signals, date, eval_config.START_TIME, eval_config.END_TIME, enforce_ITM=eval_config.ENFORCE_ITM, middle_ITM=eval_config.MIDDLE_ITM)
        trades, report_metrics = strategy.generate_trades(signals, spreads, eval_config.STOP_LOSS, eval_config.TAKE_PROFIT, eval_config.EXIT_W_OPEN, 
                                                          money_management=(eval_config.MM_TYPE, eval_config.EXIT_BASED_ON_CLOSE))

        res = {
            "trades": trades,
            "spreads": spreads,
            "spread_availability": report_metrics["spread_availability"],
            "wins": report_metrics["wins"],
            "losses": report_metrics["losses"]
        }
        trades_dict[date] = res


    # 5. Calculate evaluation metrics, print and log results to ml flow
    print("----------------------------------------------")
    print("ENTRY SIGNAL RESULTS")
    print("----------------------------------------------")
    signal_stats, signal_stats_per_day = summarize_signals(signals_dict)
    print(signal_stats)
    print(signal_stats_per_day)

    print("----------------------------------------------")
    print("TRADE AND PROFIT RESULTS")
    print("----------------------------------------------")
    trade_stats, trade_stats_per_day = summarize_trades(trades_dict)
    print(trade_stats)
    print(trade_stats_per_day)

    print("----------------------------------------------")
    print("----------------------------------------------")


    #for date, signals in signals_dict.items():
        #chart_title = f"{date} || Confirm with 5 min: {confirm_with_5min} || Use trend line: {use_trend_line} || Use stoch RSI: {use_stoch_rsi}"
        #plot_candle_chart_with_markers(signals, title=chart_title, signal_column_1="entry_bull_put", signal_column_2="entry_bear_call")

    # Log key metrics
    mlflow.log_metric("avg_trades_per_day", trade_stats["avg_trades_per_day"])
    mlflow.log_metric("avg_bp_trades_per_day", trade_stats["avg_bp_trades_per_day"])
    mlflow.log_metric("avg_bc_trades_per_day", trade_stats["avg_bc_trades_per_day"])
    mlflow.log_metric("avg_spread_availability", trade_stats["avg_spread_availability"])
    mlflow.log_metric("avg_profit_per_day", trade_stats["avg_profit_per_day"])
    mlflow.log_metric("total_profit", trade_stats["total_profit"])
    mlflow.log_metric("total_wins", trade_stats["total_wins"])
    mlflow.log_metric("total_losses", trade_stats["total_losses"])
    mlflow.log_metric("win_rate", trade_stats["win_rate"])
    mlflow.log_metric("avg_entries_per_day", signal_stats["avg_entries_per_day"])
    mlflow.log_metric("avg_bp_entries_per_day", signal_stats["avg_bp_entries_per_day"])
    mlflow.log_metric("avg_bc_entries_per_day", signal_stats["avg_bc_entries_per_day"])

    mlflow.log_table(data=signal_stats_per_day, artifact_file="signal_stats.json")
    mlflow.log_table(data=trade_stats_per_day, artifact_file="trades_stats.json")

    # log per day metrics
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #path_s = f"mlruns/artifacts/signals_per_day_{timestamp}.csv"
    #signal_stats_per_day.to_csv(path_s, index=False)
    # mlflow.log_artifact(path_s)
    #path_t = f"mlruns/artifacts/trades_per_day_{timestamp}.csv"
    #trade_stats_per_day.to_csv(path_t, index=False)
    # mlflow.log_artifact(path_t)

    mlflow.end_run()