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


def plot_candle_chart_with_markers(df, title="Candlestick Chart with Signals", signal_column_1=None, signal_column_2=None, signal_column_3=None):
    """
    Plots a candlestick chart and optionally marks points where a certain condition is met.
    Params:
        df: Should include at least 'Datetime', 'Open', 'High', 'Low', 'Close'.
        signal_column: Optional string, the name of a column containing boolean values 
            (True to mark).
    """
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['Datetime'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Candlestick"
    ))

    marker_offset = 0.5  # Amount to shift each marker vertically to prevent overlap

    if signal_column_1 and signal_column_1 in df.columns:
        signal_points = df[df[signal_column_1] == True]
        fig.add_trace(go.Scatter(
            x=signal_points['Datetime'],
            y=signal_points['High'] + marker_offset,
            mode='markers',
            marker=dict(color='blue', size=9, symbol='circle'),
            name=f"Signal: {signal_column_1}"
        ))

    if signal_column_2 and signal_column_2 in df.columns:
        signal_points = df[df[signal_column_2] == True]
        fig.add_trace(go.Scatter(
            x=signal_points['Datetime'],
            y=signal_points['High'] + marker_offset * 2,
            mode='markers',
            marker=dict(color='black', size=9, symbol='circle'),
            name=f"Signal: {signal_column_2}"
        ))

    if signal_column_3 and signal_column_3 in df.columns:
        signal_points = df[df[signal_column_3] == True]
        fig.add_trace(go.Scatter(
            x=signal_points['Datetime'],
            y=signal_points['High'] + marker_offset * 3,
            mode='markers',
            marker=dict(color='yellow', size=9, symbol='circle'),
            name=f"Signal: {signal_column_3}"
        ))


    fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Price")
    fig.show()
    

def plot_candle_chart_with_indicator(df, title="Candlestick Chart with Signals", indicator_column="stoch_rsi"):
    """
    Plots a candlestick chart and a Stochastic RSI subplot below it.
    Params:
        df: DataFrame including 'Datetime', 'Open', 'High', 'Low', 'Close'.
    """
    # Create a figure with two rows (one for price chart, one for Stoch RSI)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, 
                        row_heights=[0.7, 0.3])  # Adjust heights

    # Add candlestick chart
    fig.add_trace(go.Candlestick(x=df['Datetime'],
                                 open=df['Open'],
                                 high=df['High'],
                                 low=df['Low'],
                                 close=df['Close'],
                                 name="Candlestick Chart"),
                  row=1, col=1)

    # Add Stochastic RSI line
    fig.add_trace(go.Scatter(x=df['Datetime'], y=df[indicator_column], 
                             mode='lines', name="Stochastic RSI",
                             line=dict(color='blue')),
                  row=2, col=1)

    # Add overbought (0.8) and oversold (0.2) reference lines
    fig.add_hline(y=0.8, line=dict(color="red", dash="dash"), row=2, col=1)
    fig.add_hline(y=0.2, line=dict(color="green", dash="dash"), row=2, col=1)

    # Update layout
    fig.update_layout(title=title,
                      xaxis2_title="Datetime",
                      yaxis_title="Price",
                      yaxis2_title="Stochastic RSI",
                      showlegend=True
                      )

    fig.show()