import os
import pandas as pd
from datetime import datetime
from ib_insync import *

def download_historical_data(duration='30 D', bar_size='5 mins'):
    """
    Downloads historical S&P 500 (SPX) data from Interactive Brokers TWS API and saves it as a CSV file.
    
    :param duration: Duration of historical data (e.g., '30 D' for 30 days).
    :param bar_size: Bar size (e.g., '5 mins', '1 min', '1 hour').
    """
    # Connect to IB TWS or Gateway
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7497, clientId=1)  # Port 7496 for live, 7497 for paper trading
        
        # Define S&P 500 index contract
        contract = Index(symbol='SPX', exchange='CBOE')
        ib.qualifyContracts(contract)

        # Request historical data
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )

        # Convert data to DataFrame
        df = pd.DataFrame(bars)
        df['date'] = df['date'].astype(str)  # Ensure date is string

        # Ensure data_files directory exists
        os.makedirs("data_files", exist_ok=True)

        # Generate a fitting filename
        current_date = datetime.today().strftime('%Y-%m-%d')  # Format: YYYY-MM-DD
        filename = f"data_files/SPX_{duration.replace(' ', '')}_{bar_size.replace(' ', '')}_{current_date}.csv"
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        ib.disconnect()


download_historical_data('30 D', '5 mins')
