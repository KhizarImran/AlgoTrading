import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime


def connect_to_mt5():
    if not mt5.initialize():
        print("Failed to initialize the Metatrader 5 library.")
        return False
    print("Connecteed to MetaTrader 5")
    return True

def get_data(symbol, timeframe, start_date, end_time):
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_time)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def get_sma(data, period):
    sma = data['close'].rolling(period).mean()
    return sma


def market_order(symbol, volume, order_type, deviation=20, magic=261200):
    
    order_type_dict = {
        'buy'  : mt5.ORDER_TYPE_BUY,
        'sell'  : mt5.ORDER_TYPE_SELL
    }

    price_dict = {
        'buy' : mt5.symbol_info_tick(symbol).ask,
        'sell' : mt5.symbol_info_tick(symbol).bid
    }
    
    # Calculate stop loss and take profit levels based on price and pips
    if order_type == 'buy':
        sl_price = price_dict['buy'] - (20 * mt5.symbol_info(symbol).point)
        tp_price = price_dict['buy'] + (50 * mt5.symbol_info(symbol).point)
    elif order_type == 'sell':
        sl_price = price_dict['sell'] + (20 * mt5.symbol_info(symbol).point)
        tp_price = price_dict['sell'] - (50 * mt5.symbol_info(symbol).point)
    else:
        raise ValueError("Invalid order type.")
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,  # FLOAT
        "type": order_type_dict[order_type],
        "price": price_dict[order_type],
        "sl": sl_price,  # FLOAT
        "tp": tp_price,  # FLOAT
        "deviation": deviation,  # INTERGER
        "magic": magic,  # INTERGER
        "comment": "my_first_strat",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    order_result = mt5.order_send(request)
    return(order_result)

def main():

    symbol = 'XAUUSD'
    timeframe = mt5.TIMEFRAME_H1
    volume = 0.1
    
    
    if not connect_to_mt5():
        return
    
    while True:
        account_info = mt5.account_info()
        print(datetime.now(),
              '| Login: ', account_info.login,
              '| Balance: ', account_info.balance,
              '| Equity: ' , account_info.equity)
        
        current_time = int(time.time())
        start_time = datetime(2022, 8, 1)
        end_time = current_time

        data = get_data(symbol, timeframe, start_time, end_time)
        if len(data) < 120:  
            print("Not enough data.")
            time.sleep(60)
            continue
        
        # Initiating strategy
        fast_ma = get_sma(data,  20)
        slow_ma = get_sma(data, 120)

        for index, row in data.iterrows():
            if fast_ma.loc[index] > slow_ma.loc[index]:
                if mt5.positions_total() == 0:
                    market_order(symbol, volume, 'buy')
            elif fast_ma.loc[index] < slow_ma.loc[index]:
                if mt5.positions_total() == 0:
                    market_order(symbol, volume, 'sell')
        
        time.sleep(900)  # Check every 15 minute

if __name__ == "__main__":
    main()
    
    