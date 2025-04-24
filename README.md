# spy0dte-simulator

## Overview
This is a simple setup for backtesting SPY and SPX options trading strategies on historical data. It is specifically designed for 0dte credit spread strategies (bull put and bear call), however it can also be used for regular option trading strategies. Furthermore, this setup was originally developed for SPY and SPX options, but is designed to work for any OHLC data (see section *Data*). For experiment tracking we us MLFlow.

### Eval workflow


## Get started
1. Create virtual environment. Choose Python 3.9, if available.
```
python3.9 -m venv venv
source venv/bin/activate
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Start MLFlow and view tracked experiments at *127.0.0.1:5000*
```
mlflow ui --port 5000
```

4. Run eval.py
```
python eval.py
```



## Data
The folder data is meant to contain all historical data files and all data preprocessing / filtering. This implementation of our backtesting setup does not support loading data from a database. For historical 0dte options data, we recommend using the developer plan from [Polygon](https://polygon.io/options), however other free options are available too. This repo also contains example Python scripts to download index and options data from interactive brokers via the TWS api.

### Format
All data files are expected to be in **CSV format**. Each CSV file should include the following columns with **exact names**, where each row represents a ohlc bar:

- `Datetime`: A timestamp representing the date and time of  (e.g., `2025-03-07 08:38:00-06:00`).
- `High`: The highest price during the period.
- `Open`: The opening price of the period.
- `Low`: The lowest price during the period.
- `Close`: The closing price of the period.

The columns must be comma-separated and contain no missing values.

Example:

```csv
Datetime,High,Open,Low,Close
2025-03-07 08:38:00-06:00,5724.35,5735.39,5724.22,5734.96
2025-03-07 08:39:00-06:00,5735.62,5736.09,5731.38,5732.28
```

## Testing
Optionally, the repo contains a github workflow for automated testing, using PyTest. To deactivate it, just delete the *.github* folder. If activated, all tests in the *tests* folder are run upon pushing a commit to the remote branch.
