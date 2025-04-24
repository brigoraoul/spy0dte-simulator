import pandas as pd
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


DIRECTORY_PATH = Path("dev/data/polygon/index_flat_files/1_min_aggregates")

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

    # scale values
    df[["Open", "High", "Low", "Close"]] *= 10

    df.to_csv(file_path, index=False)
    print("saved: ", file_path)
