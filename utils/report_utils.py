# Helper functions for evaluation reports
import pandas as pd

def get_spread(index_price, spread_type, spread_width=20):
    """
    Calculate the spread, including the strike price of both options, given the index price and a spread width.
    Params:
        index_price: Current SPX price
        spread_type: Either 'Bull Put' for Bull Put spread or 'Bear Call' for Bear Call spread
        spread_width: Difference between the two options that form the spread
    Returns:
        A tuple containing the strike prices of the two options in the spread (strike_sell, strike_buy).
    """
    def round_to_nearest_5(x):
        return round(x / 5) * 5
    
    if spread_type == 'Bull Put':
        # In a Bull Put Spread, you sell a put at the index price and buy a put 20 points lower
        strike_sell = round_to_nearest_5(index_price)
        strike_buy = round_to_nearest_5(index_price - spread_width)
        return (strike_sell, strike_buy)
    
    elif spread_type == 'Bear Call':
        # In a Bear Call Spread, you sell a call at the index price and buy a call 20 points higher
        strike_sell = round_to_nearest_5(index_price) 
        strike_buy = round_to_nearest_5(index_price + spread_width)
        return (strike_sell, strike_buy)
    
    else:
        raise ValueError("Invalid spread type. Use 'Bull Put' or 'Bear Call'.")

def print_signals(df):
    """
    Print out the signals in a list, including
    - time stamp (datetime)
    - open, high, low, close
    - type of spread
    - spread strike prices
    """

    signals = df[(df['entry_bull_put']) | (df['entry_bear_call']) | (df['exit_bull_put']) | (df['exit_bear_call'])]
    
    # print header
    width = 17
    print(f"{'Datetime':<{30}}{'Open':<{width}}{'High':<{width}}{'Low':<{width}}{'Close':<{10}}{'Spread type':<{width}} Strike prices")
    
    for index, row in signals.iterrows():    
        spread_type = "Bull Put"
        if row["entry_bear_call"]:
            spread_type = "Bear Call"
        spread = get_spread(row["Close"], spread_type)
        
        print(str(row["Datetime"]), "  ||  ", str(row["Open"]), "  ||  ", str(row["High"]), "  ||  ", str(row["Low"]), "  ||  ",
               str(row["Close"]), "  ||  ", spread_type ,"  ||  ", str(spread))
        

def summarize_trades(trades_dict):
    """
    Summarizes the trades given by a strategy. Calculates 
    - the total number of trades for each day
    - bull put trades for each day
    - bear call trades for each day
    - availability of spread data per day
    - profit per day
    - average total trades per day 
    - average bull put trades per day 
    - average bear call trades per day 
    - average availability of spread data 
    - average profit
    - total profit
    - win rate
    - profite per trade

    Params:
        trades_dict: Ordered Dict, with dates as keys and dictionaries containing 
        trades, spreads, and spread availability as values.

    Returns:
        Dictionary, containing the above mentioned average metrics
        Dictionary, containing metrics per day
    """
    avg_total_trades = 0
    avg_bp_trades = 0  # TODO
    avg_bc_trades = 0  # TODO
    avg_spread_availability = 0
    avg_profit = 0
    total_profit = 0
    total_wins = 0
    total_losses = 0
    win_rate = 0
    profit_per_trade = 0

    total_trades_per_day = []
    bp_trades_per_day = []
    bc_trades_per_day = []
    spread_availability_per_day = []
    profit_per_day = []
    
    for date, trades in trades_dict.items():
        total_trades = len(trades["trades"])
        total_trades_per_day.append((date, total_trades))

        bp_trades = 0
        bc_trades = 0
        total_profit = 0

        for trade in trades["trades"]:
            if trade["spread"]["spread_type"] == "Bull Put":
                bp_trades += 1
            if trade["spread"]["spread_type"] == "Bear Call":
                bc_trades += 1

            individual_profit = trade['profit']
            total_profit += individual_profit

        bp_trades_per_day.append((date, bp_trades))
        bc_trades_per_day.append((date, bc_trades))
        spread_availability_per_day.append((date, trades["spread_availability"]))
        profit_per_day.append((date, total_profit))

        total_wins += trades["wins"]
        total_losses += trades["losses"]

    results_per_day = pd.DataFrame({
        "date": [entry[0] for entry in total_trades_per_day],  
        "total trades": [entry[1] for entry in total_trades_per_day],
        "bull put trades": [entry[1] for entry in bp_trades_per_day],
        "bear call trades": [entry[1] for entry in bc_trades_per_day],
        "spread availability": [entry[1] for entry in spread_availability_per_day],
        "profit per day": [entry[1] for entry in profit_per_day]
    })
    results_per_day.set_index("date", inplace=True)  # set date column as index
    results_per_day = results_per_day.sort_values(by="date")

    avg_total_trades = results_per_day["total trades"].mean()
    avg_bp_trades = results_per_day["bull put trades"].mean()
    avg_bc_trades = results_per_day["bear call trades"].mean()
    avg_spread_availability = results_per_day["spread availability"].mean()
    avg_profit = results_per_day["profit per day"].mean()
    total_profit = results_per_day["profit per day"].sum()

    if total_wins > 0 or total_losses > 0:
        win_rate = total_wins / (total_wins + total_losses)
        profit_per_trade = total_profit / (total_wins + total_losses)

    results = {
        "avg_trades_per_day": avg_total_trades,
        "avg_bp_trades_per_day": avg_bp_trades,
        "avg_bc_trades_per_day": avg_bc_trades,
        "avg_spread_availability": avg_spread_availability,
        "avg_profit_per_day": avg_profit,
        "total_profit": total_profit,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "win_rate": win_rate,
        "profit_per_trade": profit_per_trade
    }

    return results, results_per_day


def summarize_signals(signals_dict):
    """
    Summarizes how many signals were given by a strategy. Calculates 
    - the total entries for each day
    - bull put entries for each day
    - bear call entries for each day
    - average total entries per day 
    - average bull put entries per day 
    - average bear call entries per day 

    Params:
        signals_dict: Ordered Dict, with dates as keys and data frames containing the signals as values.

    Returns:
        Dictionary, containing the above mentioned average metrics
        Dictionary, containing metrics per day
    """
    avg_total_entries = 0
    avg_bp_entries = 0
    avg_bc_entries = 0
    total_entries_per_day = []
    bp_entries_per_day = []
    bc_entries_per_day = []

    for date, signals in signals_dict.items():
        bp_entries = signals['entry_bull_put'].sum()
        bp_entries_per_day.append((date, bp_entries))

        bc_entries = signals['entry_bear_call'].sum()
        bc_entries_per_day.append((date, bc_entries))

        total_entries = bp_entries + bc_entries
        total_entries_per_day.append((date, total_entries))


    results_per_day = pd.DataFrame({
        "date": [entry[0] for entry in total_entries_per_day],  
        "total entries": [entry[1] for entry in total_entries_per_day],
        "bull put entries": [entry[1] for entry in bp_entries_per_day],
        "bear call entries": [entry[1] for entry in bc_entries_per_day]
    })
    results_per_day.set_index("date", inplace=True)  # set date column as index
    results_per_day = results_per_day.sort_values(by="date")

    avg_total_entries = results_per_day["total entries"].mean()
    avg_bp_entries = results_per_day["bull put entries"].mean()
    avg_bc_entries = results_per_day["bear call entries"].mean()

    results = {
        "avg_entries_per_day": avg_total_entries,
        "avg_bp_entries_per_day": avg_bp_entries,
        "avg_bc_entries_per_day": avg_bc_entries
    }

    return results, results_per_day
       