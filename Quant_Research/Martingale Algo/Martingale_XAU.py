import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timedelta
import ta
"""
This script is an sma moving avergae crossover strategy looking at sma periods 20 and 120 on gold.
There is also a martingale approach  to the trade size as losses are taken the position size is increased by 30%.

With some testing on the live markets, the performance shows drawdown for periods with high volatility,
this is assumed due to using hard stoplosses of 20 pips instead of something dynamic like ATR.
ATR can be used to filter out profitable periods instead of using it as a stoploss; this is so the big
drawdown periods are avoided when wider stoplosses are in play, this can wipe out alot of profits.

"""
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
    sma = data['close'].rolling(period).mean()
    return sma

def get_atr(data, period):
    atr = ta.volatility.average_true_range(data['high'], data['low'], data['close'], window=period)
    return atr

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
    timeframe = mt5.TIMEFRAME_M5
    init_volume = 0.15
    my_volume = init_volume
    prev_last_profit = None  # Initialize previous profit
    #account = 701092
    
    if not connect_to_mt5():
      return  
    # Login to MetaTrader 5
    #if not mt5.login(account, password="jS}I?y2t:Y", server="FEMarketsCorp-Live"):
        #print("Failed to log in to MetaTrader 5.")
        #return
    
    while True:
        account_info = mt5.account_info()
        print(datetime.now(),
              '| Login: ', account_info.login,
              '| Balance: ', account_info.balance,
              '| Equity: ' , account_info.equity,
              '| Profit: ', account_info.profit)
        
        current_time = datetime.utcfromtimestamp(mt5.symbol_info(symbol).time)
        print('Current time :',current_time)
        start_time = current_time - timedelta(days=7)
        print('Start time :', start_time)
        end_time = current_time + timedelta(hours=1)
        print('end_time: ', end_time)

        data = get_data(symbol, timeframe, start_time, end_time)
        if len(data) < 120:  
            print("Not enough data.")
            time.sleep(60)
            continue
        
        fast_ma = get_sma(data,  20).iloc[-1]
        slow_ma = get_sma(data, 120).iloc[-1]
        
        # Looking at previous closed trade
        history_orders = mt5.history_deals_get(datetime(2024,4,8), datetime.now(), symbol=symbol)
        # print(history_orders)
        last_profit = history_orders[-1].profit
        
         # Adjust volume only if last profit has changed
        if last_profit != prev_last_profit:
             if last_profit < 0:
                 my_volume = round(my_volume * 1.3, 2)
                 print(f'lot size for next position {my_volume}')
             elif last_profit >= 0:  # Adjust this condition
                 my_volume = init_volume
             prev_last_profit = last_profit
        
        # Check if there are open positions
        positions_get = mt5.positions_get(symbol=symbol)
        
        # Keep track of current position
        in_position = len(positions_get) > 0
        
        prev_fast_ma = get_sma(data, 20).iloc[-2]
        prev_slow_ma = get_sma(data, 120).iloc[-2]
        
        atr = get_atr(data, 14).iloc[-1]
        atr_condition = atr <= 3.5
        
        # Check conditions and place trades
        if not in_position and atr_condition: 
            if (fast_ma > slow_ma) and (prev_fast_ma <= prev_slow_ma):
                market_order(symbol, my_volume, 'buy')
                print('***Buy signal detected***')
                in_position = True

            elif (fast_ma < slow_ma) and (prev_fast_ma >= prev_slow_ma):
                market_order(symbol, my_volume, 'sell')
                print('***Sell signal detected***')
                in_position = True
        output1 = (fast_ma > slow_ma) and (prev_fast_ma <= prev_slow_ma)
        output2 = (fast_ma < slow_ma) and (prev_fast_ma >= prev_slow_ma)
        
        print(f'Fastma :{fast_ma}', f'Slowma :{slow_ma}')
       
        print(f'Prev Fastma :{prev_fast_ma}', f'Prev Slowma :{prev_slow_ma}')
        
        print(f'ATR :{atr}')
        
        print(f'Buy Signal :{output1}', f'Sell Signal :{output2}')
        
        # print(f'last profit  :{last_profit}', f'prev last profit :{prev_last_profit}')  
        
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
