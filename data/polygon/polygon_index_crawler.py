import os
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_candle_chart(df, title="Candlestick Chart with Signals"):
    """
    Plots any chart data, independent of the time frame, in a regular candle chart plot.
    Params: 
        df: Should include at least 'Datetime', 'Open', 'High', 'Low', 'Close'.
    """
    fig = go.Figure(data=go.Ohlc(x=df['Datetime'],
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close']))
    
    fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Price")
    fig.show()

API_KEY = "YOUR-POLYGON-API-KEY"  # api key from polygon dashboard
TICKER = "SPY"
TIMEFRAME = "15"  # minutes
YEAR = "2025"
MONTH = "03"
START_DATE = f"{YEAR}-{MONTH}-01"  # year-month-day
END_DATE = f"{YEAR}-{MONTH}-31"

url = f"https://api.polygon.io/v2/aggs/ticker/{TICKER}/range/{TIMEFRAME}/minute/{START_DATE}/{END_DATE}"
params = {
    "adjusted": "true",
    "sort": "asc",
    "limit": 100000,
    "apiKey": API_KEY
}

# Request data from Polygon.io
response = requests.get(url, params=params)
data = response.json()

# check if data is returned
if "results" in data:
    df = pd.DataFrame(data["results"])
    
    df["Datetime"] = pd.to_datetime(df["t"], unit="ms")
    df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "volume"}, inplace=True)
    df = df[["Datetime", "Open", "High", "Low", "Close", "volume"]]

    # save to CSV
    csv_filename = f"{YEAR}-{MONTH}.csv"
    csv_filepath = os.path.join("dev/data/polygon/index_flat_files/15_min_aggregates", csv_filename)

    # Preprocessing
    # Rename columns
    df.rename(columns={
        "open": "Open",
        "close": "Close",
        "high": "High",
        "low": "Low",
        "window_start": "Datetime"
    }, inplace=True)

    # scale values
    df[["Open", "High", "Low", "Close"]] *= 10
    df.to_csv(csv_filepath, index=False)


    print(f"Data saved to {csv_filepath}")

else:
    print("No data found. Check your API key, ticker, and date range.")
