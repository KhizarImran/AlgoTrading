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
    lowerbb = ta.volatility.bollinger_lband(data['close'], window=window)
    return lowerbb

def get_upperbb(data, window):
    upperbb = ta.volatility.bollinger_hband(data['close'], window=window)
    return upperbb

def market_order(symbol, volume, order_type, deviation=20, magic=100922):
    order_type_dict = {
        'buy': mt5.ORDER_TYPE_BUY,
        'sell': mt5.ORDER_TYPE_SELL
    }
    price_dict = {
        'buy': mt5.symbol_info_tick(symbol).ask,
        'sell': mt5.symbol_info_tick(symbol).bid
    }
    
    if order_type == 'buy':
        sl_price = price_dict['buy'] - (15 * mt5.symbol_info(symbol).point)
        tp_price = price_dict['buy'] + (45 * mt5.symbol_info(symbol).point)
    elif order_type == 'sell':
        sl_price = price_dict['sell'] + (15 * mt5.symbol_info(symbol).point)
        tp_price = price_dict['sell'] - (45 * mt5.symbol_info(symbol).point)
    else:
        raise ValueError("Invalid order type.")
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type_dict[order_type],
        "price": price_dict[order_type],
        "sl": sl_price,
        "tp": tp_price,
        "deviation": deviation,
        "magic": magic,
        "comment": "my_first_strat",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    order_result = mt5.order_send(request)
    return order_result

def close_position(position):
    if position.type == mt5.ORDER_TYPE_BUY:
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(position.symbol).bid
    elif position.type == mt5.ORDER_TYPE_SELL:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(position.symbol).ask
    else:
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": order_type,
        "position": position.ticket,
        "price": price,
        "deviation": 20,
        "magic": position.magic,
        "comment": "close_position",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    return result

def main():
    symbol = 'EURGBP'
    timeframe = mt5.TIMEFRAME_M1
    volume = 1.60
    
    if not connect_to_mt5():
        return
    
    while True:
        current_time_utc = datetime.utcnow()
        current_time_uk = current_time_utc + timedelta(hours=1)
        
        if current_time_uk.hour < 7 or current_time_uk.hour >= 8:
            print("Outside trading hours. Waiting...")
            time.sleep(300)
            continue
        
        account_info = mt5.account_info()
        print(datetime.now(),
              '| Login: ', account_info.login,
              '| Balance: ', account_info.balance,
              '| Equity: ', account_info.equity,
              '| Profit: ', account_info.profit)
        
        current_time = datetime.utcfromtimestamp(mt5.symbol_info(symbol).time)
        start_time = current_time - timedelta(days=2)
        end_time = current_time + timedelta(hours=1)
        
        data = get_data(symbol, timeframe, start_time, end_time)
        if len(data) < 100:  
            print("Not enough data.")
            time.sleep(60)
            continue
        
        lower_bb = get_lowerbb(data, 20).iloc[-1]
        upper_bb = get_upperbb(data, 20).iloc[-1]
        
        positions_get = mt5.positions_get(symbol=symbol)
        in_position = len(positions_get) > 0
        position_type = None
        
        if in_position:
            position = positions_get[0]
            position_type = 'buy' if position.type == mt5.ORDER_TYPE_BUY else 'sell'
        
        if not in_position:
            if data['close'].iloc[-2] < lower_bb and data['close'].iloc[-1] >= lower_bb:
                market_order(symbol, volume, 'buy')
                print('*****Algo entered buy*****')
            elif data['close'].iloc[-2] > upper_bb and data['close'].iloc[-1] <= upper_bb:
                market_order(symbol, volume, 'sell')
                print('*****Algo entered sell*****')
        else:
            if position_type == 'buy' and data['close'].iloc[-2] > upper_bb and data['close'].iloc[-1] <= upper_bb:
                close_position(position)
                market_order(symbol, volume, 'sell')
                print('*****Algo closed buy and entered sell*****')
            elif position_type == 'sell' and data['close'].iloc[-2] < lower_bb and data['close'].iloc[-1] >= lower_bb:
                close_position(position)
                market_order(symbol, volume, 'buy')
                print('*****Algo closed sell and entered buy*****')
        
        print('Symbol :', symbol)
        print(f'Lower_bb : {lower_bb}')
        print(f'Upper_bb : {upper_bb}')
        
        time.sleep(60)

if __name__ == "__main__":
    main()
