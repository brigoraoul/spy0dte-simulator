import os
import pandas as pd
from pathlib import Path

DIRECTORY_PATH = Path("dev/data/polygon/options_flat_files/2024-02")

for file_path in DIRECTORY_PATH.glob("*.csv"):
    df = pd.read_csv(file_path)

    # Rename columns
    df.rename(columns={
        "open": "Open",
        "close": "Close",
        "high": "High",
        "low": "Low",
        "window_start": "Datetime"
    }, inplace=True)

    # Filter tickers 
    df = df[df["ticker"].str.contains("SPY|SPXW", na=False, regex=True)]

    # scale values
    df[["Open", "High", "Low", "Close"]] *= 10

    df.to_csv(file_path, index=False)
    print("saved: ", file_path)
