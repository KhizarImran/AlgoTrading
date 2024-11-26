import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def fetch_ohlc_data(symbol, timeframe, num_candles=300):
    """
    Fetch OHLC data for a given symbol using MT5.
    
    :param symbol: The trading symbol (e.g., "XAUUSD")
    :param timeframe: The timeframe (e.g., mt5.TIMEFRAME_D1)
    :param num_candles: Number of candles to fetch (default: 300)
    :return: DataFrame with OHLC data
    """
    if not mt5.initialize():
        print("Failed to initialize MT5. Check if MT5 is running and logged in.")
        return None

    current_time = datetime.now()
    start_time = current_time - timedelta(days=num_candles)
    
    rates = mt5.copy_rates_range(symbol, timeframe, start_time, current_time)
    
    if rates is None or len(rates) == 0:
        print(f"Failed to fetch data for {symbol}")
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    return df

def calculate_zscore(xau_data, xag_data):
    """
    Calculate the current z-score based on the price difference between XAUUSD and XAGUSD.
    
    :param xau_data: DataFrame with XAUUSD OHLC data
    :param xag_data: DataFrame with XAGUSD OHLC data
    :return: Current z-score
    """
    # Ensure both dataframes have the same length
    min_length = min(len(xau_data), len(xag_data))
    xau_data = xau_data.iloc[-min_length:]
    xag_data = xag_data.iloc[-min_length:]
    
    # Calculate the ratio of gold to silver prices
    xau_xag_ratio = xau_data['close'] / xag_data['close']
    
    # Calculate the difference between consecutive ratios
    price_diff = xau_xag_ratio.diff().dropna()
    
    # Calculate mean and standard deviation
    mu = price_diff.mean()
    sigma = price_diff.std()
    
    # Calculate Z-score for each data point
    z_scores = (price_diff - mu) / sigma
    
    # Return the most recent z-score
    return z_scores.iloc[-1]

def main():
    # Initialize MT5 connection
    if not mt5.initialize():
        print("Failed to initialize MT5. Check if MT5 is running and logged in.")
        return

    # Fetch OHLC data for XAUUSD and XAGUSD
    xau_data = fetch_ohlc_data("XAUUSD", mt5.TIMEFRAME_D1)
    xag_data = fetch_ohlc_data("XAGUSD", mt5.TIMEFRAME_D1)
    
    if xau_data is None or xag_data is None:
        print("Failed to fetch data. Exiting.")
        return
    
    # Calculate and print the current z-score
    current_zscore = calculate_zscore(xau_data, xag_data)
    print(f"Current Z-Score: {current_zscore:.4f}")
    
    # Shutdown MT5 connection
    mt5.shutdown()

if __name__ == "__main__":
    main()