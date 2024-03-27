import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime

def connect_to_mt5():
    if not mt5.initialize():
        print("Failed to initialize the Metatrader 5 library.")
        return False
    print("Connected to MetaTrader 5")
    return True

def get_data(symbol, timeframe, start_date, end_time):
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_time)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def get_sma(data, period):
    calc_sma = data['close'].tail(period)
    sma = calc_sma.mean()
    return sma

def get_prev_sma(data, period):
    prev_sma = data['close'].rolling(period).mean()
    return prev_sma

def market_order(symbol, volume, order_type, deviation=20, magic=261200):
    order_type_dict = {
        'buy'  : mt5.ORDER_TYPE_BUY,
        'sell'  : mt5.ORDER_TYPE_SELL
    }
    price_dict = {
        'buy' : mt5.symbol_info_tick(symbol).ask,
        'sell' : mt5.symbol_info_tick(symbol).bid
    }
    
    if order_type == 'buy':
        sl_price = price_dict['buy'] - (200 * mt5.symbol_info(symbol).point)
        tp_price = price_dict['buy'] + (500 * mt5.symbol_info(symbol).point)
    elif order_type == 'sell':
        sl_price = price_dict['sell'] + (200 * mt5.symbol_info(symbol).point)
        tp_price = price_dict['sell'] - (500 * mt5.symbol_info(symbol).point)
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
        "deviation": deviation,  # INTEGER
        "magic": magic,  # INTEGER
        "comment": "my_first_strat",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    order_result = mt5.order_send(request)
    return order_result

def main():
    symbol = 'XAUUSD'
    timeframe = mt5.TIMEFRAME_M15
    volume = 0.1
    
    if not connect_to_mt5():
        return
    
    while True:
        account_info = mt5.account_info()
        print(datetime.now(),
              '| Login: ', account_info.login,
              '| Balance: ', account_info.balance,
              '| Equity: ' , account_info.equity,
              '| Profit: ', account_info.profit)
        
        current_time = datetime.now()
        start_time = datetime(2024, 1, 1)
        end_time = current_time

        data = get_data(symbol, timeframe, start_time, end_time)
        if len(data) < 120:  
            print("Not enough data.")
            time.sleep(60)
            continue
        
        fast_ma = get_sma(data,  20)
        slow_ma = get_sma(data, 120)
        


        # Check if there are open positions
        positions_total = mt5.positions_total()
        
        # Keep track of current position
        in_position = positions_total > 0
        
        prev_fast_ma = get_prev_sma(data, 20).iloc[-1]
        prev_slow_ma = get_prev_sma(data, 120).iloc[-1]


        # Check conditions and place trades
        if not in_position: 
            if (fast_ma > slow_ma) and (prev_fast_ma <= prev_slow_ma):
                market_order(symbol, volume, 'buy')
                print('Buy signal detected')
                in_position = True

            elif (fast_ma < slow_ma) and (prev_fast_ma >= prev_slow_ma):
                market_order(symbol, volume, 'sell')
                print('Sell signal detected')
                in_position = True
            
        
        time.sleep(900)  # Check every 15 minutes

if __name__ == "__main__":
    main()
