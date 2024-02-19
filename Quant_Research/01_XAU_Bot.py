import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from datetime import datetime

def get_sma(symbol, timeframe, period):
    sma = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timeframe, 1, period))['close'].mean()

    return sma

def get_rates(symbol, number_of_data = 10000, timeframe=mt5.TIMEFRAME_M5):
    # Compute now date
    from_date = datetime.now()

    # Extract n Ticks before now
    rates = mt5.copy_rates_from(symbol, timeframe, from_date, number_of_data)


    # Transform Tuple into a DataFrame
    df_rates = pd.DataFrame(rates)

    # Convert number format of the date into date format
    df_rates["time"] = pd.to_datetime(df_rates["time"], unit="s")

    df_rates = df_rates.set_index("time")

    return df_rates

def find_filling_mode(symbol):

    for i in range(2):
        request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": mt5.symbol_info(symbol).volume_min,
        "type": mt5.ORDER_TYPE_BUY,
        "price": mt5.symbol_info_tick(symbol).ask,
        "type_filling": i,
        "type_time": mt5.ORDER_TIME_GTC}

        result = mt5.order_check(request)
        
        if result.comment == "Done":
            break

    return i








