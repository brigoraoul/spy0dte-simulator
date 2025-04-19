import ta
import pandas as pd

class Conditions:

    @staticmethod
    def get_all(df):
        df = Conditions.stoch_rsi(df, window=8, upper_threshhold=0.8, lower_threshhold=0.2)
        
        return df


    @staticmethod
    def stoch_rsi(df, window=8, upper_threshhold=0.8, lower_threshhold=0.2):
        """
        Calculates the Stochastic RSI using the 'ta' library and identifies rows of the df
        that lie above the upper threshhold or below the lower threshhold.
        
        Parameters:
            df (pd.DataFrame): DataFrame containing the 'close' prices.
            length (int): Lookback period for Stochastic RSI calculation (default is 8).
        
        Returns:
            pd.DataFrame: Original DataFrame with an added 'stoch_rsi', 'stoch_rsi_upper'
            and 'stoch_rsi_lower' column.
        """
        df = df.copy()
        df['stoch_rsi'] = ta.momentum.StochRSIIndicator(df['Close'], window=window).stochrsi()
        df['stoch_rsi_upper'] = df['stoch_rsi'] > upper_threshhold
        df['stoch_rsi_lower'] = df['stoch_rsi'] < lower_threshhold
        
        return df
    
