import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timedelta
import ta

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

def get_lowerbb(data, window):
    lowerbb = ta.volatility.bollinger_lband(data['close'], window = window)
    return lowerbb

def get_rsi(data, window):
    rsi = ta.momentum.RSIIndicator(data['close'], window=window).rsi()
    return rsi

def market_order(symbol, volume, order_type, deviation=20, magic=200101):
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
    symbol = 'SP500USD'
    timeframe = mt5.TIMEFRAME_M5
    volume = 0.01
    
    if not connect_to_mt5():
        return
    
    while True:
        
        # Get current UTC time
        current_time_utc = datetime.utcnow()
        
        # Convert UTC time to UK time
        current_time_uk = current_time_utc + timedelta(hours=1)  # UTC+1 for UK time
        
        # Check if current time is within trading hours (7am - 9pm UK time)
        if current_time_uk.hour < 7 or current_time_uk.hour >= 21:
            print("Outside trading hours. Waiting...")
            time.sleep(300)  # Check every 5 minutes
            continue
        
        
        account_info = mt5.account_info()
        print(datetime.now(),
              '| Login: ', account_info.login,
              '| Balance: ', account_info.balance,
              '| Equity: ' , account_info.equity,
              '| Profit: ', account_info.profit)
        
        current_time = datetime.utcfromtimestamp(mt5.symbol_info(symbol).time)
        start_time = current_time - timedelta(days=7)
        end_time = current_time + timedelta(hours=1)
        
        data = get_data(symbol, timeframe, start_time, end_time)
        if len(data) < 100:  
            print("Not enough data.")
            time.sleep(60)
            continue
        
        lower_bb = get_lowerbb(data, 20).iloc[-1]
        rsi = get_rsi(data, 14).iloc[-1]
        
        # Check if there are open positions
        positions_total = mt5.positions_total()
        
        # Keep track of current position
        in_position = positions_total > 0
        
        if not in_position:
             if rsi <= 40 and data['close'].iloc[-1] >= lower_bb:
                 market_order(symbol, volume, 'buy')
                 in_position = True
            
        output = rsi <= 40 and data['close'].iloc[-1] >= lower_bb
        
        if output == True:
            print('*****Algo entered buy*****')
        
        print(f'Lower_bb : {lower_bb}')
        print(f'rsi : {rsi}')
        
        time.sleep(300)  # Check every 5 minutes
        
if __name__ == "__main__":
    main()
            
        