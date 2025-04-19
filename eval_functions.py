import os
import glob
import pandas as pd
import numpy as np
import mlflow
import datetime
from collections import OrderedDict
from data.data_processing import Preprocessor
from strategies.conditions import Conditions
from strategies.strategies import *
from utils.report_utils import *
from utils.chart_visualization import *
from utils.options_helper import *
import eval_config

def run_eval_month(df_1_min, df_5_min, file_name,
               start_time=eval_config.START_TIME, 
               end_time=eval_config.END_TIME,
               strategy = eval_config.STRATEGY,
               use_trend_line=eval_config.USE_TREND_LINE,
               use_stoch_rsi=eval_config.USE_STOCH_RSI,
               enforce_ITM=eval_config.ENFORCE_ITM,
               middle_ITM=eval_config.MIDDLE_ITM,
               enforce_OTM=eval_config.ENFORCE_OTM,
               stop_loss=eval_config.STOP_LOSS,
               take_profit=eval_config.TAKE_PROFIT, 
               exit_w_open=eval_config.EXIT_W_OPEN,
               exit_w_mm=eval_config.EXIT_W_MM,
               exit_w_midpoint=eval_config.EXIT_W_MIDPOINT,
               mm_type=eval_config.MM_TYPE,
               exit_based_on_close=eval_config.EXIT_BASED_ON_CLOSE):
    # 1. load test data files for target date
    data = [df_1_min, df_5_min]

    # 2. Pre-process data: calculate indicators and split data per day
    # 2.1 group dataframe by day (maintain order of the days) and filter for dates
    # that are present in all files
    data = [Preprocessor.split_by_day(df) for df in data]
   
    year, month = map(int, file_name.removesuffix(".csv").split("-"))
    common_dates = {
        date for date in (set(data[0].keys()) & set(data[1].keys()))
        if date.year == year and date.month == month
    }
    data = [OrderedDict((key, value) for key, value in d.items() if key in common_dates) for d in data]

    # 2.2 calculate indicators
    data = [
        OrderedDict((key, Conditions.get_all(df)) for key, df in file.items())
        for file in data
    ]

    # 2.3 get relevant time window
    data = [
        OrderedDict((key, Preprocessor.get_time_window_data(df, start_time=start_time, end_time=end_time)) for key, df in file.items())
        for file in data
    ]

    # 3. Apply strategy, to get entry and exit signals
    strategy = strategy
    signals_dict = OrderedDict()

    # apply 'generate_signals' once for each date and store results in ordered dict
    for date in common_dates:
        df_1min_index = data[0][date]
        df_5min_index = data[1][date]

        signals = {}
        if strategy.__class__.__name__ == "DeHighInLowSimple":
            signals = strategy.generate_entries(df_1min_index, df_5min_index, use_trend_line=use_trend_line, use_stoch_rsi=use_stoch_rsi)
        if strategy.__class__.__name__ == "LHLFormation":
            signals = strategy.generate_entries(df_1min_index=df_1min_index, date=date, start_time=start_time, end_time=end_time, enforce_ITM=enforce_ITM, middle_ITM=middle_ITM)

        if signals is not None:                                        
            signals_dict[date] = signals


    # 4. Get spread charts and generate trades
    trades_dict = OrderedDict()
    for date, signals in signals_dict.items():
        spreads = get_spreads(signals=signals, date=date, start_time=start_time, end_time=end_time, enforce_ITM=enforce_ITM, middle_ITM=middle_ITM, enforce_OTM=enforce_OTM)
        trades, report_metrics = strategy.generate_trades(df=signals, spreads=spreads, stop_loss=stop_loss, take_profit=take_profit, exit_w_open=exit_w_open, exit_w_mm=exit_w_mm, money_management=(mm_type, exit_based_on_close))

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
    print("ENTRY SIGNAL RESULTS ", file_name)
    print("----------------------------------------------")
    signal_stats, signal_stats_per_day = summarize_signals(signals_dict)
    print(signal_stats)
    print(signal_stats_per_day)

    print("----------------------------------------------")
    print("TRADE AND PROFIT RESULTS ", file_name)
    print("----------------------------------------------")
    trade_stats, trade_stats_per_day = summarize_trades(trades_dict)
    print(trade_stats)
    print(trade_stats_per_day)

    print("----------------------------------------------")
    print("----------------------------------------------")

    return signal_stats, trade_stats

def run_total_eval(experiment_name, run_name = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
                quicktest = False,
                start_time=eval_config.START_TIME, 
                end_time=eval_config.END_TIME,
                strategy = eval_config.STRATEGY,
                confirm_with_5min = eval_config.CONFIRM_WITH_5MIN,
                use_trend_line=eval_config.USE_TREND_LINE,
                use_stoch_rsi=eval_config.USE_STOCH_RSI,
                enforce_ITM=eval_config.ENFORCE_ITM,
                middle_ITM=eval_config.MIDDLE_ITM,
                enforce_OTM=eval_config.ENFORCE_OTM,
                stop_loss=eval_config.STOP_LOSS,
                take_profit=eval_config.TAKE_PROFIT, 
                exit_w_open=eval_config.EXIT_W_OPEN,
                exit_w_midpoint=eval_config.EXIT_W_MIDPOINT,
                exit_w_mm=eval_config.EXIT_W_MM,
                mm_type=eval_config.MM_TYPE,
                exit_based_on_close=eval_config.EXIT_BASED_ON_CLOSE):
    
    mlflow.set_experiment(experiment_name=experiment_name)
    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("strategy/CONFIRM_WITH_5MIN", confirm_with_5min)
        mlflow.log_param("strategy/USE_TREND_LINE", use_trend_line)
        mlflow.log_param("strategy/USE_STOCH_RSI", use_stoch_rsi)
        mlflow.log_param("__START_TIME", start_time)
        mlflow.log_param("__END_TIME", end_time)
        mlflow.log_param("mm/STOP_LOSS", stop_loss)
        mlflow.log_param("mm/TAKE_PROFIT", take_profit)
        mlflow.log_param("mm/MM_TYPE", mm_type)
        mlflow.log_param("mm/EXIT_BASED_ON_CLOSE", exit_based_on_close)
        mlflow.log_param("exit/EXIT_W_OPEN", exit_w_open)
        mlflow.log_param("exit/EXIT_W_MIDPOINT", exit_w_midpoint)
        mlflow.log_param("exit/EXIT_W_MM", exit_w_mm)
        mlflow.log_param("spread_calc/ENFORCE_ITM", enforce_ITM)
        mlflow.log_param("spread_calc/MIDDLE_ITM", middle_ITM)
        mlflow.log_param("strategy/STRATEGY", strategy.__class__.__name__)


        # Define flat file directories and get all files from first directory (extra directories for quicktest)
        _1min_file_dir = "dev/data/polygon/index_flat_files/1_min_aggregates"
        _5min_file_dir = "dev/data/polygon/index_flat_files/5_min_aggregates"
        if quicktest:
            _1min_file_dir = "dev/data/polygon/quick_test_files/1_min"
            _5min_file_dir = "dev/data/polygon/quick_test_files/5_min"
        _1min_files = glob.glob(os.path.join(_1min_file_dir, "*.csv"))

        
        # init empty report dicts
        signal_stats_summary = {
            'avg_entries_per_day': 0,
            'avg_bp_entries_per_day': 0,
            'avg_bc_entries_per_day': 0
        }
        trade_stats_summary = {
            'avg_trades_per_day': 0,
            'avg_bp_trades_per_day': 0,
            'avg_bc_trades_per_day': 0,
            'avg_spread_availability': 0,
            'avg_profit_per_day': 0,
            'total_profit': 0,
            'total_wins': 0,
            'total_losses': 0,
            'win_rate': 0
        }

        valid_iterations = 0
        results_per_month = []
        for _1min_file in _1min_files:
            # get corresponding 5 min file by name
            file_name = os.path.basename(_1min_file)
            _5min_file = os.path.join(_5min_file_dir, file_name)
            
            if os.path.exists(_5min_file):
                df_1_min = pd.read_csv(_1min_file)
                df_5_min = pd.read_csv(_5min_file)

                signal_stats, trade_stats = run_eval_month(df_1_min, df_5_min, file_name, 
                                                           start_time, 
                                                           end_time,
                                                           strategy=strategy,
                                                           use_trend_line=use_trend_line,
                                                           use_stoch_rsi=use_stoch_rsi,
                                                           stop_loss=stop_loss,
                                                           take_profit=take_profit,
                                                           enforce_ITM=enforce_ITM,
                                                           middle_ITM=middle_ITM,
                                                           enforce_OTM=enforce_OTM,
                                                           exit_w_open=exit_w_open,
                                                           exit_w_midpoint=exit_w_midpoint,
                                                           exit_w_mm=exit_w_mm,
                                                           mm_type=mm_type,
                                                           exit_based_on_close=exit_based_on_close)
                
                # Update the summary dictionaries
                signal_stats_summary['avg_entries_per_day'] += signal_stats['avg_entries_per_day']
                signal_stats_summary['avg_bp_entries_per_day'] += signal_stats['avg_bp_entries_per_day']
                signal_stats_summary['avg_bc_entries_per_day'] += signal_stats['avg_bc_entries_per_day']
                trade_stats_summary['avg_trades_per_day'] += trade_stats['avg_trades_per_day']
                trade_stats_summary['avg_bp_trades_per_day'] += trade_stats['avg_bp_trades_per_day']
                trade_stats_summary['avg_bc_trades_per_day'] += trade_stats['avg_bc_trades_per_day']
                trade_stats_summary['avg_spread_availability'] += trade_stats['avg_spread_availability']
                trade_stats_summary['avg_profit_per_day'] += trade_stats['avg_profit_per_day']
                trade_stats_summary['total_profit'] += trade_stats['total_profit']
                trade_stats_summary['total_wins'] += trade_stats['total_wins']
                trade_stats_summary['total_losses'] += trade_stats['total_losses']
                trade_stats_summary['win_rate'] += trade_stats['win_rate']

                # record results per month
                total_trades = trade_stats['total_losses'] + trade_stats['total_wins']
                results_per_month.append({
                    'file_name': file_name,
                    'total_profit': trade_stats['total_profit'],
                    'win_rate': trade_stats['win_rate'],
                    'total_wins': trade_stats['total_wins'],
                    'total_losses': trade_stats['total_losses'],
                    'total_trades': total_trades
                })
                valid_iterations += 1

            else:
                print(f"No matching file found for: {_1min_file} and {_5min_file}")
                continue

        # print the per month results
        df_results_per_month = pd.DataFrame(results_per_month)
        df_results_per_month = df_results_per_month.sort_values(by='file_name')
        print("Per month results (Total Profit and Win Rate per File):")
        print(df_results_per_month)

        if valid_iterations > 0:
            signal_stats_summary['avg_entries_per_day'] /= valid_iterations
            signal_stats_summary['avg_bp_entries_per_day'] /= valid_iterations
            signal_stats_summary['avg_bc_entries_per_day'] /= valid_iterations
            
            trade_stats_summary['avg_trades_per_day'] /= valid_iterations
            trade_stats_summary['avg_bp_trades_per_day'] /= valid_iterations
            trade_stats_summary['avg_bc_trades_per_day'] /= valid_iterations
            trade_stats_summary['avg_spread_availability'] /= valid_iterations
            trade_stats_summary['avg_profit_per_day'] /= valid_iterations
            trade_stats_summary['win_rate'] /= valid_iterations
        
        # calculate additional metrics
        profit_per_trade = 0
        total_wins = trade_stats_summary["total_wins"]
        total_losses = trade_stats_summary["total_losses"]
        if total_wins > 0 or total_losses > 0:
            profit_per_trade = trade_stats_summary["total_profit"] / (total_wins + total_losses)

        profit_std = df_results_per_month['total_profit'].std()
        profit_z_score = ((df_results_per_month['total_profit'] - df_results_per_month['total_profit'].mean()) / profit_std).mean()

        winrate_std = df_results_per_month['win_rate'].std()
        winrate_z_score = ((df_results_per_month['win_rate'] - df_results_per_month['win_rate'].mean()) / winrate_std).mean()

        sharpe_ratio = df_results_per_month['total_profit'].mean() / profit_std
        
        # Log key metrics to mlflow
        mlflow.log_metric("avg/avg_trades_per_day", trade_stats_summary["avg_trades_per_day"])
        mlflow.log_metric("avg/avg_bp_trades_per_day", trade_stats_summary["avg_bp_trades_per_day"])
        mlflow.log_metric("avg/avg_bc_trades_per_day", trade_stats_summary["avg_bc_trades_per_day"])
        mlflow.log_metric("avg/avg_spread_availability", trade_stats_summary["avg_spread_availability"])
        mlflow.log_metric("avg/avg_profit_per_day", trade_stats_summary["avg_profit_per_day"])
        mlflow.log_metric("t/total_profit", trade_stats_summary["total_profit"])
        mlflow.log_metric("t/total_wins", total_wins)
        mlflow.log_metric("t/total_losses", total_losses)
        mlflow.log_metric("win_rate", trade_stats_summary["win_rate"])
        mlflow.log_metric("profit_per_trade", profit_per_trade)
        mlflow.log_metric("avg/avg_entries_per_day", signal_stats_summary["avg_entries_per_day"])
        mlflow.log_metric("avg/avg_bp_entries_per_day", signal_stats_summary["avg_bp_entries_per_day"])
        mlflow.log_metric("avg/avg_bc_entries_per_day", signal_stats_summary["avg_bc_entries_per_day"])
        mlflow.log_metric("stat/profit_std", profit_std)
        mlflow.log_metric("stat/profit_z_score", profit_z_score)
        mlflow.log_metric("stat/winrate_std", winrate_std)
        mlflow.log_metric("stat/winrate_z_score", winrate_z_score)
        mlflow.log_metric("stat/sharpe_ratio", sharpe_ratio)

        mlflow.log_table(data=df_results_per_month, artifact_file="monthly_stats.json")

        mlflow.end_run()
