import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def connect_to_mt5():
    if not mt5.initialize():
        print("Failed to initialize the Metatrader 5 library.")
        return False
    print("Connected to MetaTrader 5")
    return True

def get_data(symbol, timeframe, num_candles):
    current_time = datetime.now()
    start_time = current_time - timedelta(days=num_candles)
    rates = mt5.copy_rates_range(symbol, timeframe, start_time, current_time)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def is_bullish_engulfing(df, i):
    return (df['close'].iloc[i] > df['open'].iloc[i-1] and
            df['open'].iloc[i] <= df['close'].iloc[i-1] and
            df['close'].iloc[i] > df['open'].iloc[i] and
            df['open'].iloc[i] <= df['open'].iloc[i-1])

def is_bearish_engulfing(df, i):
    return (df['close'].iloc[i] < df['open'].iloc[i-1] and
            df['open'].iloc[i] >= df['close'].iloc[i-1] and
            df['close'].iloc[i] < df['open'].iloc[i] and
            df['open'].iloc[i] >= df['open'].iloc[i-1])

def calculate_lot_size(account_size, account_currency, risk_percentage, stop_loss_pips, symbol):
    # Get the current tick value
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Failed to get symbol info for {symbol}")
        return None
    
    print(symbol)
    tick_value = symbol_info.trade_tick_value
    print(f"tick value {tick_value}")
    tick_size = symbol_info.trade_tick_size
    print(f"tick size {tick_size}")
    contract_size = symbol_info.trade_contract_size
    print(f"contract size {contract_size}")

    # Calculate the value of 1 pip
    pip_value = tick_value * (0.0001 / tick_size)
    print(f"pip value {pip_value}")

    # If the account currency is different from the base currency of the pair,
    # we need to adjust the pip value
    if account_currency != symbol[:3]:
        conversion_pair = f"{symbol[:3]}{account_currency}"
        conversion_tick = mt5.symbol_info_tick(conversion_pair)
        if conversion_tick is None:
            try:
                conversion_pair = f"{account_currency}{symbol[:3]}"
                conversion_tick = mt5.symbol_info_tick(conversion_pair) 
            except:
                print(f"Failed to get tick info for {conversion_pair}")
                # Use a fallback method or return None
                return None
        conversion_rate = conversion_tick.ask
        pip_value *= conversion_rate

    # Calculate the risk amount
    risk_amount = account_size * (risk_percentage / 100)
    print(f"risk amount {risk_amount}")

    # Calculate the lot size
    lot_size = risk_amount / (stop_loss_pips * pip_value * contract_size)
    print(f"lot size {lot_size}")

    # Round down to the nearest 0.01
    lot_size = max(0.01, round(lot_size - 0.005, 2))

    return lot_size

def scan_patterns(buy_symbols, sell_symbols, account_size, account_currency, risk_percentage):
    results = []
    for symbol in buy_symbols:
        df = get_data(symbol, mt5.TIMEFRAME_D1, 10)
        if df.empty:
            print(f"No data available for {symbol}")
            continue
        
        current_candle = df.iloc[-1]
        previous_candle = df.iloc[-2]
        
        if is_bullish_engulfing(df, -1):
            stop_loss = previous_candle['low'] - 0.0002  # 2 pips below previous candle low
            stop_loss_pips = (current_candle['close'] - stop_loss)
            print(f"stoploss pips {stop_loss_pips}")
            lot_size = calculate_lot_size(account_size, account_currency, risk_percentage, stop_loss_pips, symbol)
            
            if lot_size is not None:
                results.append({
                    "Symbol": symbol,
                    "Pattern": "Bullish Engulfing",
                    "Action": "Buy",
                    "Date": current_candle.name.date(),
                    "Open": current_candle['open'],
                    "High": current_candle['high'],
                    "Low": current_candle['low'],
                    "Close": current_candle['close'],
                    "Stop Loss": stop_loss,
                    "Lot Size": lot_size
                })
            else:
                print(f"Could not calculate lot size for {symbol}")
    
    for symbol in sell_symbols:
        df = get_data(symbol, mt5.TIMEFRAME_D1, 10)
        if df.empty:
            print(f"No data available for {symbol}")
            continue
        
        current_candle = df.iloc[-1]
        previous_candle = df.iloc[-2]
        
        if is_bearish_engulfing(df, -1):
            stop_loss = previous_candle['high'] + 0.0002  # 2 pips above previous candle high
            stop_loss_pips = (stop_loss - current_candle['close'])
            print(f"stoploss pips {stop_loss_pips}")
            lot_size = calculate_lot_size(account_size, account_currency, risk_percentage, stop_loss_pips, symbol)
            
            if lot_size is not None:
                results.append({
                    "Symbol": symbol,
                    "Pattern": "Bearish Engulfing",
                    "Action": "Sell",
                    "Date": current_candle.name.date(),
                    "Open": current_candle['open'],
                    "High": current_candle['high'],
                    "Low": current_candle['low'],
                    "Close": current_candle['close'],
                    "Stop Loss": stop_loss,
                    "Lot Size": lot_size
                })
            else:
                print(f"Could not calculate lot size for {symbol}")
    
    return pd.DataFrame(results)

def main():
    if not connect_to_mt5():
        return
    
    # Account settings
    account_size = 10000  # Your account size
    account_currency = "USD"  # Your account currency
    risk_percentage = 1  # Risk percentage per trade

    buy_symbols = [
        "EURUSD", "USDJPY", "GBPUSD", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
        "EURJPY", "EURGBP", "EURCHF", "EURCAD", "EURAUD", "EURNZD",
        "GBPJPY", "GBPCHF", "GBPCAD", "GBPAUD", "GBPNZD",
        "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
        "NZDJPY", "NZDCHF", "NZDCAD",
        "CADJPY", "CADCHF",
        "CHFJPY"
    ]
    
    sell_symbols = [
        "EURUSD", "USDJPY", "GBPUSD", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
        "EURJPY", "EURGBP", "EURCHF", "EURCAD", "EURAUD", "EURNZD",
        "GBPJPY", "GBPCHF", "GBPCAD", "GBPAUD", "GBPNZD",
        "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
        "NZDJPY", "NZDCHF", "NZDCAD",
        "CADJPY", "CADCHF",
        "CHFJPY"
    ]
        
    print(f"Scanning for patterns at {datetime.now()}...")
    results = scan_patterns(buy_symbols, sell_symbols, account_size, account_currency, risk_percentage)
    
    if not results.empty:
        print("\nDetected patterns:")
        print(results.to_string(index=False))
    else:
        print("No patterns detected.")
    
    mt5.shutdown()

if __name__ == "__main__":
    main()