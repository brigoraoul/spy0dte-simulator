import pandas as pd
from abc import ABC, abstractmethod
from strategies.conditions import *


class Strategy(ABC):
    """
    A strategy defines entry and exit points for bull put and bear call spreads, given a dataframe
    df with chart data. The derivation of entry and exit points can be very different between 
    strategies. Typically, a strategy implementation makes use of conditions from 
    'strategies.conditions.Conditions' to derive entry and exit points.
    """
    @abstractmethod
    def generate_entries(self, df):
        pass

    @abstractmethod
    def generate_trades(self, df):
        pass


class StochRSIStrategy(Strategy):
    def __init__(self, stoch_rsi_entry_threshold=0.2, stoch_rsi_exit_threshold=0.8):
        "This is the threshold below which you consider entering a Bull Put Spread position. "
        "The default value is 0.2, which signifies an oversold condition."
        self.stoch_rsi_entry_threshold = stoch_rsi_entry_threshold
        "This is the threshold above which you consider exiting the position. " 
        "The default value is 0.8, which signifies an overbought condition."
        self.stoch_rsi_exit_threshold = stoch_rsi_exit_threshold

    def generate_entries(self, df):
        signals = []

        # iterate over ohlc and generate signals based on stoch RSI criteria
        for _, bar in df.iterrows():
            if bar['stoch_RSI'] < self.stoch_rsi_entry_threshold:
                signals.append({'action': 'enter', 'bar': bar})

        return signals
    
    def generate_trades(self, signals, df):
        signals = self.generate_entries(df)
        trades = []

        # get entry signals
        entry_signals = [e for e in signals if e['action'] == 'enter']
        df = df.reset_index(drop=True)

        for entry in entry_signals:
            entry_bar = entry['bar']
            entry_index = df.index[df['timestamp'] == entry_bar['timestamp']].tolist()

            if not entry_index:
                continue
            entry_idx = entry_index[0]

            # iterrate over ohlc to find exit
            for i in range(entry_idx + 1, len(df)):
                if df.loc[i, 'stoch_RSI'] > self.stoch_rsi_exit_threshold:
                    exit_bar = df.loc[i]
                    trades.append({
                        'entry_bar': entry_bar,
                        'exit_bar': exit_bar
                    })
                    break  

        return trades


