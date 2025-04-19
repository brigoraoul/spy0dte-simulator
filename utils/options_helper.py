import pandas as pd
from pathlib import Path
from polygon import RESTClient
from datetime import datetime, timedelta

def load_options_from_file(date):
    """
    Loads the csv file for a given date that contains all options data from that date.
    Filters for SPY and returns the filtered dataframe.
    If the file does not exist, returns None.
    """
    month_string = date.strftime("%Y-%m")
    date_string = date.strftime("%Y-%m-%d")
    filename = f"dev/data/polygon/options_flat_files/{month_string}/{date_string}.csv"
    filepath = Path(filename)

    if not filepath.exists():
        print("Path does not exist: ", filename)
        return None 

    df = pd.read_csv(filename)
    df = df[df["ticker"].str.contains("SPY", na=False)]
    df['Datetime'] = pd.to_datetime(df['Datetime'] / 1e9, unit='s')

    return df


def get_option(df, ticker, start_time="00:00", end_time="23:59"):
    """
    Given a Dataframe that represents option data of one day, 'get_option' filters the 
    df for a specific option. The 'start_time' and 'end_time' parameters allow for the
    specification of a time window.

    Params:
        df: options data Dataframe
        ticker: string, specifying the option, e.g. 'O:SPY250307C00578000'
        start_time: time, from which one option data should be returned
        end_time: time, until which option data should be returned
    
    Returns:
        df: options data for ticker
    """
    filtered_df = df[df["ticker"] == ticker].copy()
    
    filtered_df["Datetime"] = pd.to_datetime(filtered_df["Datetime"])  
    filtered_df["Time"] = filtered_df["Datetime"].dt.time  # get time component of datetime column

    start = pd.to_datetime(start_time).time()
    end = pd.to_datetime(end_time).time()

    filtered_df = filtered_df[(filtered_df["Time"] >= start) & (filtered_df["Time"] <= end)]
    return filtered_df.drop(columns=["Time"])  # Drop time column if not needed


def get_option_api(ticker, date):
    """
    Get option data via polygon api (not loading from local file).

    Params:
        ticker: string, specifying the option, e.g. 'O:SPY250307C00578000'

    Returns:
        df: options data for ticker
    """

    # make date strings
    prev_day = date - timedelta(days=1)
    next_day = date + timedelta(days=1)

    prev_day = prev_day.strftime("%Y-%m-%d")
    date = date.strftime("%Y-%m-%d")
    next_day = next_day.strftime("%Y-%m-%d")
    
    client = RESTClient("1qCvKyfRajf_ewGpw2ryraerx5Ct_MAB")
    aggs = []
    for a in client.list_aggs(
        ticker,
        1,
        "minute",
        prev_day,
        date,
        adjusted="true",
        sort="asc",
        limit=5000, # 5000 is limit set by api
    ):
        aggs.append(a)

    
    df = pd.DataFrame([{
        "Datetime": agg.timestamp,
        "Open": agg.open,
        "High": agg.high,
        "Low": agg.low,
        "Close": agg.close,
        "volume": agg.volume,
        "vwap": agg.vwap,
        "transactions": agg.transactions,
        "otc": agg.otc,
    } for agg in aggs])
    df['Datetime'] = pd.to_datetime(df['Datetime'], unit='ms')

    return df


def calculate_spread_strike_prices(index_price, spread_type, spread_width=20, enforce_ITM=True, middle_ITM=False, enforce_OTM=False):
    """
    Calculate the in the money spread, including the strike price of both options, given the index price and a spread width.
    Params:
        index_price: Current SPX price
        spread_type: Either 'Bull Put' for Bull Put spread or 'Bear Call' for Bear Call spread
        spread_width: Difference between the two options that form the spread
        enforce_ITM: If True, guarantees that the index price will lie inbetween the upper and the lower strike price
            of the resulting spread. If False, the spread can sometimes be slightly out of the money.
        middle_ITM: If True, the middle point of the spread will be the closest rounded 5 points from the index price.
        
    Returns:
        A tuple containing the strike prices of the two options in the spread (strike_sell, strike_buy).
    """
    def round_to_nearest_5(x):
        return round(x / 5) * 5
    
    if middle_ITM:
        middle = round_to_nearest_5(index_price)
        upper_strike = middle + (spread_width / 2)
        lower_strike = middle - (spread_width / 2)

        if spread_type == 'Bull Put':
            return upper_strike, lower_strike
        if spread_type == 'Bear Call':
            return lower_strike, upper_strike
    
    elif not middle_ITM and spread_type == 'Bull Put':
        # In a Bull Put Spread, you sell a put at the index price and buy a put 20 points lower
        strike_sell = round_to_nearest_5(index_price)
        if enforce_ITM and strike_sell < index_price:
            strike_sell = round_to_nearest_5(index_price + 5) # to ensure index price lies between strike prices
        elif enforce_OTM and strike_sell >= index_price:
            strike_sell = round_to_nearest_5(index_price - 5) # to ensure index price lies outside of strike prices

        strike_buy = strike_sell - spread_width
        return (strike_sell, strike_buy)
    
    elif not middle_ITM and spread_type == 'Bear Call':
        # In a Bear Call Spread, you sell a call at the index price and buy a call 20 points higher
        strike_sell = round_to_nearest_5(index_price) 
        if enforce_ITM and strike_sell > index_price:
            strike_sell = round_to_nearest_5(index_price - 5) # to ensure index price lies between strike prices
        elif enforce_OTM and strike_sell <= index_price:
            strike_sell = round_to_nearest_5(index_price + 5) # to ensure index price lies outside of strike prices

        strike_buy = strike_sell + spread_width
        return (strike_sell, strike_buy)
    
    else:
        raise ValueError("Invalid spread type. Use 'Bull Put' or 'Bear Call'.")
    

def get_option_ticker(date, option_type, strike_price):
    """
    Returns ticker as string

    Params:
        date: Datetime object, indicating expiration date of option
        option_type: either C for Bear Call or P for Bull Put
        strike_price: strike price of the option
    """
    if option_type == "Bull Put":
        option_type = "P"
    elif option_type == "Bear Call":
        option_type = "C"

    formatted_date = date.strftime("%y%m%d")
    formatted_strike = f"{int(strike_price * 100):08d}"
    ticker = f"O:SPY{formatted_date}{option_type}{formatted_strike}"
    
    return ticker


def calculate_spread_ohlc(short_option_df, long_option_df):
    """
    Calculate the OHLC chart for a bull put or bear call spread.

    Parameters:
    - short_option_df: DataFrame with OHLC for the short option
    - long_option_df: DataFrame with OHLC for the long option

    Returns:
    - DataFrame with OHLC for the spread
    """
    spread_ohlc = pd.DataFrame()

    if "Datetime" in short_option_df.columns:
        spread_ohlc["Datetime"] = short_option_df["Datetime"]

    spread_ohlc["Open"] = short_option_df["Open"] - long_option_df["Open"]
    spread_ohlc["High"] = short_option_df["High"] - long_option_df["Low"]  # Max possible value
    spread_ohlc["Low"] = short_option_df["Low"] - long_option_df["High"]   # Min possible value
    spread_ohlc["Close"] = short_option_df["Close"] - long_option_df["Close"]

    return spread_ohlc


def align_and_fill_missing_data(sold_df, bought_df):
    """
    Aligns and fills missing OHLC data for two options to ensure matching timestamps. Missing timestamps are filled with the
    last known value, through the 'ffill' (= "forward fill") method.

    Params:
        sold_df: DataFrame of OHLC for the sold option
        bought_df: DataFrame of OHLC for the bought option

    Returns:
        Both DataFrames with aligned timestamps and missing data filled.
    """
    # Merge on timestamp and fill missing values
    merged_df = sold_df.merge(bought_df, on="Datetime", how="outer", suffixes=('_sold', '_bought'))

    # Forward fill, then backward fill if necessary
    merged_df.fillna(method="ffill", inplace=True)
    merged_df.fillna(method="bfill", inplace=True)

    # Split data back into separate dataframes
    sold_filled = merged_df[["Datetime", "Open_sold", "High_sold", "Low_sold", "Close_sold"]].rename(
        columns={"Open_sold": "Open", "High_sold": "High", "Low_sold": "Low", "Close_sold": "Close"}
    )
    bought_filled = merged_df[["Datetime", "Open_bought", "High_bought", "Low_bought", "Close_bought"]].rename(
        columns={"Open_bought": "Open", "High_bought": "High", "Low_bought": "Low", "Close_bought": "Close"}
    )

    return sold_filled, bought_filled


def fill_missing_minutes(df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a minute-resolution OHLC DataFrame with a 'Datetime' column and fills any missing rows.
        Assumes 'Datetime' is already timezone-aware and in datetime format.
        """
        df = df.set_index("Datetime").sort_index()

        # create a complete datetime index at 1-minute frequency and reindex
        full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq="1min", tz=df.index.tz)
        df = df.reindex(full_index)

        # Convert OHLC columns to float if they aren’t already
        ohlc_cols = ["Open", "High", "Low", "Close"]
        for col in ohlc_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")  # This turns bad values into np.nan

        # Fill missing values
        df = df.ffill().bfill()

        # Restore Datetime as a column
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Datetime"}, inplace=True)

        return df


def get_spreads(signals, date, start_time, end_time, enforce_ITM=True, middle_ITM=False, enforce_OTM=False):
    """
    Get all necessary options data for the required spreads, based on the signals calculated by the strategy.

    Params:
        df: All SPY options data for the desired day.
        signals: Bull put and Bear call entry signals calculated by strategy.
        date: Datetime object for desired date.

    Returns:
        Spreads dictionary if option data is available for the given date.
        None if not option data is available for the given date.
    """
    spreads = {}
    signals = signals[
        (signals['entry_bull_put']) |
        (signals['entry_bear_call']) |
        (signals['exit_bull_put']) | 
        (signals['exit_bear_call'])
    ]
    df = load_options_from_file(date)
    if df is None:
        return None
    
    for index, row in signals.iterrows():    
        timestamp = row["Datetime"]

        if row["entry_bull_put"]:
            spread_type="Bull Put"
            spread = calculate_spread_strike_prices(row["Close"], spread_type, enforce_ITM=enforce_ITM, middle_ITM=middle_ITM, enforce_OTM=enforce_OTM)
            sold_option_ticker = get_option_ticker(date, "P", spread[0])  # higher strike price
            bought_option_ticker = get_option_ticker(date, "P", spread[1])  # lower strike price
            
        elif row["entry_bear_call"]:
            spread_type="Bear Call"
            spread = calculate_spread_strike_prices(row["Close"], spread_type, enforce_ITM=enforce_ITM, middle_ITM=middle_ITM, enforce_OTM=enforce_OTM)
            sold_option_ticker = get_option_ticker(date, "C", spread[0])  # lower strike price
            bought_option_ticker = get_option_ticker(date, "C", spread[1])  # higher strike price
        
        else:
            continue

        sold_option_ohlc = get_option(df, sold_option_ticker, start_time, end_time)
        bought_option_ohlc = get_option(df, bought_option_ticker, start_time, end_time)

        # skip if either of the option's data is not available
        if sold_option_ohlc.empty or bought_option_ohlc.empty:
            continue

        # fill missing OHLC data to align timestamps
        sold_option_ohlc = fill_missing_minutes(sold_option_ohlc)
        bought_option_ohlc = fill_missing_minutes(bought_option_ohlc)

        # calculate spread OHLC
        spread_ohlc = calculate_spread_ohlc(bought_option_ohlc, sold_option_ohlc)
        
        # Store results in dictionary
        spreads[timestamp] = {
            "spread_type": spread_type,
            "sold_option_price": spread[0],
            "bought_option_price": spread[1],
            "sold_option_ohlc": sold_option_ohlc,
            "bought_option_ohlc": bought_option_ohlc,
            "spread_ohlc": spread_ohlc
        }

    return spreads