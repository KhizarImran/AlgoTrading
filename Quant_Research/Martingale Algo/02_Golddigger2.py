import MetaTrader5 as mt5
from TradingMetaTraderForex import TradingMetaTraderForex
import pandas as pd
import time
from datetime import datetime, timedelta
import math

def connect_to_mt5():
    if not mt5.initialize():
        print("Failed to initialize the Metatrader 5 library.")
        return False
    print("Connected to MetaTrader 5")
    return True

def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    return (tick.bid + tick.ask) / 2

def place_order(symbol, order_type, volume, price, deviation=20, magic=100922):
    if order_type == 'buy':
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - 0.75
        tp = price + 0.85
    elif order_type == 'sell':
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
        sl = price + 0.75
        tp = price - 0.85
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": magic,
        "comment": "grid_trading_bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    order_result = mt5.order_send(request)
    print(f"place_order() executed. output: {order_result}")
    
    return order_result

def close_all_positions(symbol):
    positions = mt5.positions_get(symbol=symbol)
    for position in positions:
        if position.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": position.volume,
            "type": order_type,
            "position": position.ticket,
            "price": price,
            "deviation": 20,
            "magic": 100922,
            "comment": "close_grid_position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        mt5.order_send(request)
    

def volume(symbol, current_volume):
    # Check for closed positions
    if last_pnl(symbol) < 0:
        calculated_volume = calculate_volume(False, current_volume)
        print(f"Last closed trade was a loss. Doubling volume to {current_volume}")
    if last_pnl(symbol) >= 0:
        calculated_volume = calculate_volume(True, current_volume)
        print(f"Last closed trade was a win. Resetting volume to {current_volume}")

        
    return calculated_volume


def calculate_volume(is_loss, current_volume):
    base_volume = 0.1
    if not is_loss:
        return current_volume * 2
    
    return base_volume

def last_pnl(symbol):
    try:
        martingale_xau_data = mt5.history_deals_get(datetime(2024,4,1),(datetime.now() + timedelta(hours=3)), symbol=symbol)
        data = {
            'time': [datetime.fromtimestamp(deal.time) for deal in martingale_xau_data],
            'profit': [deal.profit for deal in martingale_xau_data],
            'volume': [deal.volume for deal in martingale_xau_data],
            'symbol': [deal.symbol for deal in martingale_xau_data]
        }
        data = pd.DataFrame(data)
        # print(f"FAULT CHECK DATA: {data}")
        martingale_xau = data[data['symbol'] == symbol]
        profit_or_loss = martingale_xau[martingale_xau['profit'] != 0]
        # print(f"FAULT CHECK PROFIT AND LOSS profit_or_loss:\n{profit_or_loss}")
        
        if not profit_or_loss.empty:
            last_pnl = profit_or_loss.iloc[-1]['profit']
            print(f"Last PNL: {last_pnl}")
            return last_pnl
        else:
            print("No profit/loss data found")
            return 0
    except Exception as e:
        print(f"ERROR IN last_pnl(): {e}")
        print("error code =", mt5.last_error())
        
            
def main():
    symbol = 'XAUUSD'
    base_volume = 0.1  # Starting with 0.01 lot
    max_positions = 2
    
    if not connect_to_mt5():
        return
    
    current_volume = base_volume
    last_closed_trade_profit = 0
    last_ceiling_price = None
    last_floor_price = None
    last_position_type = None
    
    previous_current_price = get_current_price(symbol)
    
    while True:
        try:
            current_price = get_current_price(symbol) # Get the current price of the symbol ever time(x) seconds
            positions = mt5.positions_get(symbol=symbol) # Get all open positions
            buy_positions = [p for p in positions if p.type == mt5.ORDER_TYPE_BUY]
            sell_positions = [p for p in positions if p.type == mt5.ORDER_TYPE_SELL]
            
            print(f"Current open positions: Buy: {len(buy_positions)} | Sell: {len(sell_positions)} |")
            
            account_info = mt5.account_info()
            print(datetime.now(),
                  '| Balance:', account_info.balance,
                  '| Equity:', account_info.equity,
                  '| Profit:', account_info.profit)
            
            ceiling_price = math.ceil(current_price)
            floor_price = math.floor(current_price)
            
            print(f"Current price: {current_price}")
            print(f"Ceiling price: {ceiling_price}")
            print(f"Floor price: {floor_price}")
            
            # Check if price has crossed the ceiling or floor
            if last_ceiling_price is not None and last_floor_price is not None:
                if current_price > last_ceiling_price and len(positions) == 0:
                    if len(buy_positions) < max_positions:
                        print("Opening buy position")
                        current_volume = volume(symbol, current_volume)
                        place_order(symbol, 'buy', current_volume, current_price)
                if current_price < last_floor_price and len(positions) == 0:
                    if len(sell_positions) < max_positions:
                        print("Opening sell position")
                        current_volume = volume(symbol, current_volume)
                        place_order(symbol, 'sell', current_volume, current_price)
            
            last_ceiling_price = ceiling_price
            last_floor_price = floor_price
            
            print(f'Current price: {current_price}, Current volume: {current_volume}')
            
            time.sleep(0.5)  # Check every second
            
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
    
# place_order() executed. output: OrderSendResult(retcode=10027, deal=0, order=0, volume=0.0, price=0.0, bid=0.0, ask=0.0, comment='AutoTrading disabled by client', request_id=0, retcode_external=0, request=TradeRequest(action=1, magic=100922, order=0, symbol='XAUUSD', volume=0.01, price=2326.08, stoplimit=0.0, sl=0.0, tp=0.0, deviation=20, type=0, type_filling=1, type_time=0, expiration=0, comment='grid_trading_bot', position=0, position_by=0))