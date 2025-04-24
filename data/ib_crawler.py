import json
from ib_insync import IB, Future, Index, util
from datetime import datetime

class IBClient:
    def __init__(self, config, host='127.0.0.1', port=7497, client_id=1):
        """
        Initializes the IBClient and connects to TWS API. Loads config from config file.
        """
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = client_id
        self.config = config
        self.connect()

    def load_config(self, path):
        """
        Loads the configuration file.
        """
        try:
            with open(path, 'r') as file:
                config = json.load(file)
            print("Configuration loaded successfully.")
            return config
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            return None

    def connect(self):
        """
        Connects to the TWS API.
        """
        try:
            self.ib.connect(host=self.host, port=self.port, clientId=self.client_id)
            print("Connection established to TWS API.")
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.ib = None

    def disconnect(self):
        """
        Disconnects from the TWS API.
        """
        if self.ib:
            self.ib.disconnect()
            print("Disconnected from TWS API.")

    def print_account_summary(self):
        """
        Prints the account summary.
        """
        if not self.ib:
            print("IB connection is not established. Cannot fetch account summary.")
            return

        try:
            account_summary = self.ib.accountSummary()
            print("Account Summary:")
            for item in account_summary:
                print(item)
        except Exception as e:
            print(f"Failed to retrieve account summary: {e}")

    def download_historical_data(self, duration='30 D', bar_size='5 mins'):
        """
        Downloads historical data for S&P 500 futures and the regular S&P 500 index.
        Saves data to CSV files for S&P 500 futures and index data.
        """
        
        if not self.ib or not self.config:
            print("IB connection or configuration is not established. Cannot download historical data.")
            return

        # Define contracts for S&P 500 futures and regular S&P 500 index
        contracts = {
            "SP500_futures": Future(symbol='ES', exchange='GLOBEX', currency='USD'),
            "SP500_index": Index(symbol='SPX', exchange='CBOE', currency='USD')
        }

        contracts_config = self.config.get('contracts', {})
        duration = self.config.get('default_duration', '30 D')
        bar_size = self.config.get('default_bar_size', '5 mins')
        end_date = datetime.now()

        for name, contract_details in contracts_config.items():
            try:
                contract_type = contract_details.get('type')
                symbol = contract_details.get('symbol')
                exchange = contract_details.get('exchange')
                currency = contract_details.get('currency')

                # Dynamically create the contract based on type
                contract = None
                if contract_type == 'Future':
                    contract = Future(symbol=symbol, exchange=exchange, currency=currency)
                elif contract_type == 'Index':
                    contract = Index(symbol=symbol, exchange=exchange, currency=currency)
                else:
                    print(f"Unsupported contract type: {contract_type}")
                    continue

                self.ib.qualifyContracts(contract)
                bars = self.ib.reqHistoricalData(
                    contract,
                    endDateTime=end_date.strftime('%Y%m%d %H:%M:%S'),
                    durationStr=duration,
                    barSizeSetting=bar_size,
                    whatToShow='TRADES',
                    useRTH=True  # Regular Trading Hours only
                )

                # Convert to DataFrame
                df = util.df(bars)

                # Save to CSV
                filename = f"{name}_data.csv"
                df.to_csv(filename, index=False)
                print(f"Saved {name} data to {filename}")
            except Exception as e:
                print(f"Failed to download data for {name}: {e}")