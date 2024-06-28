# Disclaimer: Nothing herein is financial advice, and NOT a recommendation to trade real money. Many platforms exist
# for trading with real money. Please use common sense and always consult a professional before trading or investing.

# Setup Meta Trader real trading
# You might have to pip install MetaTrader5
# https://www.mql5.com/en/docs/python_metatrader5 For the documentation

"""
FUNCTIONS USED FROM METATRADER5
-------------------------------
✅ initialize | Establish a connection with the MetaTrader 5 terminal
✅ login | Connect to a trading account using specified parameters
✅ shutdown | Close the previously established connection to the MetaTrader 5 terminal
✅ version | Return the MetaTrader 5 terminal version
✅ last_error | Return data on the last error
✅ account_info | Get info on the current trading account
✅ terminal_Info | Get status and parameters of the connected MetaTrader 5 terminal
✅ symbols_total | Get the number of all financial instruments in the MetaTrader 5 terminal
✅ symbols_get | Get all financial instruments from the MetaTrader 5 terminal
✅ symbol_info | Get data on the specified financial instrument
✅ symbol_info_tick | Get the last tick for the specified financial instrument
✅ symbol_select | Select a symbol in the MarketWatch window or remove a symbol from the window
market_book_add | Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol
market_book_get | Returns a tuple from BookInfo featuring Market Depth entries for the specified symbol
market_book_release | Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol
copy_rates_from | Get bars from the MetaTrader 5 terminal starting from the specified date
copy_rates_from_pos | Get bars from the MetaTrader 5 terminal starting from the specified index
copyrates_range | Get bars in the specified date range from the MetaTrader 5 terminal
copy_ticks_from | Get ticks from the MetaTrader 5 terminal starting from the specified date
copy_ticks_range | Get ticks for the specified date range from the MetaTrader 5 terminal
✅ orders_total | Get the number of active orders.
✅ orders_get | Get active orders with the ability to filter by symbol or ticket
✅ order_calc_margin | Return margin in the account currency to perform a specified trading operation
order_calc_profit | Return profit in the account currency for a specified trading operation
✅ order_check | Check funds sufficiency for performing a required trading operation
✅ order_send | Send a request to perform a trading operation.
✅ positions_total | Get the number of open positions
✅ positions_get | Get open positions with the ability to filter by symbol or ticket
history_orders_total | Get the number of orders in trading history within the specified interval
history_orders_get | Get orders from trading history with the ability to filter by ticket or position
history_deals_total | Get the number of deals in trading history within the specified interval
history_deals_get | Get deals from trading history with the ability to filter by ticket or position
"""

# *** WINDOWS ONLY AS OF 3rd JUNE 2024 ***

import MetaTrader5 as mt
import pandas as pd
from datetime import time


class TradingMetaTraderForex:
    def __init__(
        self,
        login,
        password,
        server,
        symbol,
        initialise=True,
    ):
        self.login = login
        self.password = password
        self.server = server
        self.initialise = initialise
        if self.initialise:
            self.terminal_initialise()

        self.authorised = None
        self.positions = {}

        # --------------------ACCOUNT INFORMATION--------------------
        self.account_info = self.get_account_info()
        # Storing all the necessary account information into the object for easy utilisation
        self.account_info_balance = self.account_info.balance if self.account_info is not None else None
        self.account_info_credit = self.account_info.credit if self.account_info is not None else None
        self.account_info_currency = self.account_info.currency if self.account_info is not None else None
        self.account_info_equity = self.account_info.equity if self.account_info is not None else None
        self.account_info_leverage = self.account_info.leverage if self.account_info is not None else None
        self.account_info_margin = self.account_info.margin if self.account_info is not None else None
        self.account_info_margin_free = self.account_info.margin_free if self.account_info is not None else None
        self.account_info_margin_level = self.account_info.margin_level if self.account_info is not None else None
        self.account_info_profit = self.account_info.profit if self.account_info is not None else None

        self.account_total_number_of_orders = mt.orders_total()
        self.account_total_number_of_orders_info = mt.orders_get()
        self.account_total_number_of_positions = mt.positions_total()
        self.account_total_number_of_positions_info = mt.positions_get()

        self.account_info_trade_allowed = self.account_info.trade_allowed if self.account_info is not None else None
        self.account_info_trade_mode = self.account_info.trade_mode if self.account_info is not None else None

        # --------------------SYMBOL INFORMATION--------------------
        self.symbols_name = symbol
        self.symbols_info_dict = {}

    def terminal_initialise(self):
        # Establish a connection with the MetaTrader 5 terminal. There are three call options.
        """

        Parameters
        path
        [in]  Path to the metatrader.exe or metatrader64.exe file. Optional unnamed parameter. It is indicated first without a parameter name. If the path is not specified, the module attempts to find the executable file on its own.
        login=LOGIN
        [in]  Trading account number. Optional named parameter. If not specified, the last trading account is used.
        password="PASSWORD"
        [in]  Trading account password. Optional named parameter. If the password is not set, the password for a specified trading account saved in the terminal database is applied automatically.
        server="SERVER"
        [in]  Trade server name. Optional named parameter. If the server is not set, the server for a specified trading account saved in the terminal database is applied automatically.
        timeout=TIMEOUT
        [in]  Connection timeout in milliseconds. Optional named parameter. If not specified, the value of 60 000 (60 seconds) is applied.
        portable=False
        [in]  Flag of the terminal launch in portable mode. Optional named parameter. If not specified, the value of False is used.
        Return Value
        Returns True in case of successful connection to the MetaTrader 5 terminal, otherwise - False.

        Note
        If required, the MetaTrader 5 terminal is launched to establish connection when executing the initialize() call.

        """
        try:
            response = mt.initialize(login=self.login, password=self.password, server=self.server)
            if response:
                dataframe = False
                print(f"Successfully connected to MetaTrader terminal."
                      f"\nTerminal Information:\n{self.get_terminal_info(dataframe)}"
                      f"\nMetaTrader5 Version:\n{mt.version()}")
            else:
                print(f"FAILED to connect to MetaTrader terminal. Please check account info!: Error code = {mt.last_error()}"
                      f"\nShutting down the connection to the terminal")
                self.terminal_shutdown()
        except:
            raise ValueError(
                f"FATAL ERROR with Initialisation of the MetaTrader Terminal: {mt.last_error()}"
            )

    def login(self):
        # Connect to a trading account using specified parameters.
        """

        Parameters
        login
        [in]  Trading account number. Required unnamed parameter.
        password
        [in]  Trading account password. Optional named parameter. If the password is not set, the password saved in the terminal database is applied automatically.
        server
        [in]  Trade server name. Optional named parameter. If no server is set, the last used server is applied automatically.
        timeout=TIMEOUT
        [in]  Connection timeout in milliseconds. Optional named parameter. If not specified, the value of 60 000 (60 seconds) is applied. If the connection is not established within the specified time, the call is forcibly terminated and the exception is generated.

        Return Value
        True in case of a successful connection to the trade account, otherwise – False.

        """
        try:
            self.authorised = mt.login(login=self.login, passwod=self.password, server=self.server)
            if self.authorised:
                dataframe = False
                self.account_info = self.get_account_info(dataframe)
                print(f"Successfully connected to account {self.login}.")
                if not dataframe:
                    for key in self.account_info:
                        print(f"{key}={self.account_info[key]}")
                else:
                    print(self.account_info)
            else:
                print(f"FAILED to connect to account. Please check account info!: Error code = {mt.last_error()}")
        except:
            raise ValueError(
                f"FATAL ERROR with connecting to the MetaTrader account: {mt.last_error()}"
            )

    def make_request(self, symbol, volume, side, sl, tp, price=None, deviation=15):
        try:
            # Check if the account is valid for the trade
            boolean_or_none = self.is_valid(symbol, volume, price)
            if boolean_or_none is None:
                print("CHECK is_valid() function. Returned 'None'")

            if not boolean_or_none:
                print(f"Account is not valid for {side} trade of {volume} lot(s) on {symbol} at {price} {self.account_info_currency}.")
                return

            symbol_info = mt.symbol_info(symbol)

            if symbol_info is None:
                raise ValueError(f"Symbol cannot be found. symbol_info: {symbol_info}")

            # if the symbol is unavailable in MarketWatch, add it
            if not symbol_info.visible:
                print(symbol, " is not visible, trying to switch on")
                if not mt.symbol_select(symbol, True):
                    raise ValueError(f"symbol_select({symbol}, True) failed")

            if side == "buy":
                type = mt.ORDER_TYPE_BUY
                if price is not None:
                    # Use provided price for the buy order
                    order_price = price
                else:
                    # Use latest price
                    order_price = mt.symbol_info_tick(symbol).ask
                comment = "python script buy"
            elif side == "sell":
                type = mt.ORDER_TYPE_SELL
                if price is not None:
                    # Use provided price for the sell order
                    order_price = price
                else:
                    # Use latest price
                    order_price = mt.symbol_info_tick(symbol).bid
                comment = "python script sell"
            else:
                raise ValueError(f"Invalid side. Please choose either 'buy' or 'sell'")

            open_request = {
                "action": mt.TRADE_ACTION_DEAL if price is None else mt.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": volume,
                "type": type,
                "price": order_price,
                "sl": sl,
                "tp": tp,
                "deviation": deviation,
                # Make magic dynamic
                "magic": 234000,
                "comment": comment,
                "type_time": mt.ORDER_TIME_GTC,  # Good Till Cancelled
                "type_filling": mt.ORDER_FILLING_RETURN,
            }

            try:
                result = mt.order_send(open_request)
            except Exception as e:
                raise ValueError(f"❌❌❌| Error in order_send: {str(e)}")

            if result.retcode != mt.TRADE_RETCODE_DONE:
                raise ValueError(f"Failed to send order. Error: {result.comment}")

            print(f"🔄| order_send(): {result}: by {symbol} {volume} lots at {price} {self.account_info_currency} with deviation={deviation} points")
            print(f"✅| opened position with POSITION_TICKET={result.order}")

            # Store the position details in the positions dictionary
            self.positions[result.order] = {
                "symbol": symbol,
                "price": result.price,
                "retcode": result.retcode,
                "deal": result.deal,
                "volume": result.volume,
                "bid": result.bid,
                "ask": result.ask,
                "sl": sl,
                "tp": tp,
                "deviation": deviation,
                "comment": result.comment,
                "request_id": result.request_id,
                "retcode_external": result.retcode_external
            }

        except Exception as e:
            print(f"❌| Error in make_request: {str(e)}")
            # Can add more specific error handling or logging here

    def cancel_request(self, order_id):
        try:
            # Check if the order exists in the positions dictionary
            if order_id not in self.positions:
                print(f"Order {order_id} not found in positions.")
                return


            # Get the order details from the positions dictionary
            order = self.positions[order_id]

            symbol = order["symbol"]
            volume = order["volume"]

            # Prepare the request to cancel the order
            request = {
                "action": mt.TRADE_ACTION_REMOVE,
                "order": order_id,
                "magic": 234000,
                "comment": "python script cancel"
            }

            # Send the request to cancel the order
            result = mt.order_send(request)

            # Check the result of the cancellation
            if result.retcode != mt.TRADE_RETCODE_DONE:
                print(f"Failed to cancel order {order_id}, retcode={result.retcode}")
                # Request the result as a dictionary and display it element by element
                result_dict = result._asdict()
                for field in result_dict.keys():
                    print(f"   {field}={result_dict[field]}")
            else:
                print(f"Order {order_id} cancelled successfully, {result}")
                # Remove the order from the positions dictionary
                del self.positions[order_id]

                # Request the result as a dictionary and display it element by element
                result_dict = result._asdict()
                for field in result_dict.keys():
                    print(f"   {field}={result_dict[field]}")
                    # If this is a trading request structure, display it element by element as well
                    if field == "request":
                        traderequest_dict = result_dict[field]._asdict()
                        for tradereq_field in traderequest_dict:
                            print(f"       traderequest: {tradereq_field}={traderequest_dict[tradereq_field]}")

        except Exception as e:
            print(f"Error in cancel_request: {str(e)}")
            # Can add more specific error handling or logging here

    def close_position(self, position_id, deviation=15):
        try:
            # Get the position details from the positions dictionary
            position = self.positions.get(position_id)
            if position is None:
                print(f"Position {position_id} not found in positions.")
                return

            # Prepare the request to close the position
            symbol = position["symbol"]
            volume = position["volume"]
            type = mt.ORDER_TYPE_SELL if position["type"] == mt.ORDER_TYPE_BUY else mt.ORDER_TYPE_BUY
            price = mt.symbol_info_tick(symbol).bid if type == mt.ORDER_TYPE_SELL else mt.symbol_info_tick(symbol).ask

            close_request = {
                "action": mt.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": type,
                "position": position_id,
                "price": price,
                "deviation": deviation,
                "magic": 234000,
                "comment": "python script close",
                "type_time": mt.ORDER_TIME_GTC,
                "type_filling": mt.ORDER_FILLING_RETURN,
            }

            # Perform the check for the close request
            try:
                check_result = mt.order_check(close_request)
                if check_result.retcode != mt.TRADE_RETCODE_DONE:
                    print(f"Failed to check the close request. Error: {check_result.comment}")
                    return
            except Exception as e:
                raise ValueError(f"Error when sending a closing position request {e}")

            # Send the request to close the position
            result = mt.order_send(close_request)
            if result.retcode != mt.TRADE_RETCODE_DONE:
                print(f"Failed to close position {position_id}. Error: {result.comment}")
            else:
                print(f"Position {position_id} closed successfully.")
                # Remove the position from the positions dictionary
                del self.positions[position_id]

        except Exception as e:
            print(f"Error in close_position: {str(e)}")

    # TODO: Calculate the volume to add the volume parameter the order_send() function
    def calculate_volume(self):
        # Calculate the necessary volume to use depending on the account balance and equity
        self.update_account_info()
        leverage = self.account_info_leverage
        balance = self.account_info_balance

        volume = balance / leverage

        return volume

    def get_terminal_info(self, dataframe=False):
        # Get the connected MetaTrader 5 client terminal status and settings.
        """

        Return Value
        Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using last_error().

        """
        if not dataframe:
            return mt.terminal_info()._asdict()
        else:
            temp = mt.terminal_info()._asdict()
            return pd.DataFrame(list(temp.items()), columns=['property', 'value'])

    def get_account_info(self, dataframe=False):
        # Get info on the current trading account.
        """
        Return Value:
        Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using last_error().
        """
        print("Fetching account details")
        try:
            account_info = mt.account_info()
            print(f"FAULT CHECK 1 get_account_info() | account_info = mt.account_info() = {account_info}")
            if account_info is None:
                print("Failed to retrieve account info. Error code:", mt.last_error())
                return None
            else:
                print("Account info retrieved successfully.")
                print(f"--------------------Welcome {account_info.name}--------------------")
                print("Login:", account_info.login)
                print("Balance:", account_info.balance)
                print("Equity:", account_info.equity)
                print("Margin:", account_info.margin)
                print("Free Margin:", account_info.margin_free)
                print("Server:", account_info.server)

                if not dataframe:
                    return account_info
                else:
                    temp = account_info._asdict()
                    df = pd.DataFrame(list(temp.items()), columns=['property', 'value'])
                    print(f"FAULT CHECK 2 get_account_info() | df = pd.DataFrame(list(temp.items()), columns=['property', 'value']) = {df}")
                    print("Account info as DataFrame:")
                    print(df)
                    return df

        except Exception as e:
            print("An error occurred while retrieving account info:", str(e))
            return None

    def get_symbol_info(self):
        # Get all financial instruments from the MetaTrader 5 terminal.
        """

        Return Value
        Return symbols in the form of a tuple. Return None in case of an error. The info on the error can be obtained using last_error().

        Note
        The group parameter allows sorting out symbols by name. '*' can be used at the beginning and the end of a string.
        The group parameter can be used as a named or an unnamed one. Both options work the same way. The named option (group="GROUP") makes the code easier to read.
        The group parameter may contain several comma separated conditions. A condition can be set as a mask using '*'. The logical negation symbol '!' can be used for an exclusion.
        All conditions are applied sequentially, which means conditions of including to a group should be specified first followed by an exclusion condition.
        For example, group="*, !EUR" means that all symbols should be selected first and the ones containing "EUR" in their names should be excluded afterwards.

        Unlike symbol_info(), the symbols_get() function returns data on all requested symbols within a single call.

        Example use:
        # Create an instance of the TradingMetaTrader class
        trade = TradingMetaTrader(login, password, server)

        # Set the symbols_name attribute with a group of symbols
        trade.symbols_name = ["EURUSD", "GBPUSD", "USDJPY"]

        # Call the get_symbol_info function
        trade.get_symbol_info()

        """
        print("Fetching given symbol information")
        try:
            if len(self.symbols_name) == 1:
                group = self.symbols_name[0]
                print(f"Single Group Symbol: {group}")
            elif len(self.symbols_name) > 1:
                group = ",".join(self.symbols_name)
                print(f"Group Symbol: {group}")
            else:
                group = "*"  # If symbols_name is empty, get all symbols
                print(f"Group All Symbols: {group}")
        except Exception as e:
            raise ValueError(f"Set symbol_name like this: ['EURUSD', 'GBPUSD', 'USDJPY']. {e}")

        try:
            # symbols_info = mt.symbols_get(group=group)._asdict()
            symbols_info = mt.symbols_get(group=group)
            print(f"FAULT CHECK 1 get_symbol_info() | symbols_info = mt.symbols_get(group=group) = {symbols_info}")
        except Exception as e:
            raise ValueError(f"Error when retrieving symbol info: {e}")

        if symbols_info is None:
            print("Failed to retrieve symbol info. Error code:", mt.last_error())
            return

        for symbol in symbols_info:
            symbol_dict = symbol._asdict()
            print(f"FAULT CHECK 2 get_symbol_info() | symbol_dict = symbol._asdict() = {symbol_dict}")
            self.symbols_info_dict[symbol.name] = symbol_dict
            print(f"Symbol: {symbol.name}")
            for prop, value in symbol_dict.items():
                print(f" - {prop}: {value}")
            print()

        print(f"Retrieved {len(self.symbols_info_dict)} symbols.")
        print(f"FAULT CHECK 3 get_symbol_info() | self.symbols_info_dict = {self.symbols_info_dict}")

    def get_latest_symbol_prices(self, symbols=None, dataframe=False):
        # Collect the latest symbol data from MetaTrader
        """

        Return Value
        Return the latest state (price) of the symbol passed as a parameter

        """
        try:
            if symbols is None:
                symbols = self.symbols_name

            latest_prices = {}

            for symbol in symbols:
                try:
                    print(f"FAULT CHECK 1 get_latest_symbol_prices() | symbol = {symbol}")
                    tick = mt.symbol_info_tick(symbol)
                    print(f"FAULT CHECK 2 get_latest_symbol_prices() | tick = mt.symbol_info_tick(symbol) = {tick}")

                    if tick is None:
                        print(f"No tick data available for {symbol}.")
                        continue

                    latest_prices[symbol] = {
                        'symbol': symbol,
                        'time': tick.time,
                        'bid': tick.bid,
                        'ask': tick.ask,
                        'last': tick.last,
                        'volume': tick.volume
                    }
                    print(f"FAULT CHECK 3 get_latest_symbol_prices() | latest_prices[symbol] = {latest_prices[symbol]}")
                    print(f"Successfully fetched data for {symbol}")

                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")
                    continue

            print(f"FAULT CHECK 4 get_latest_symbol_prices() | latest_prices = {latest_prices}")

            if dataframe:
                try:
                    latest_prices_df = pd.DataFrame.from_dict(latest_prices, orient='index')
                    print(f"FAULT CHECK 5 get_latest_symbol_prices() | latest_prices_df = {latest_prices_df}")
                    return latest_prices_df
                except Exception as e:
                    print(f"Error converting latest_prices to DataFrame: {str(e)}")
                    return None
            else:
                return latest_prices

        except Exception as e:
            print(f"Error in get_latest_symbol_prices: {str(e)}")
            return None

    # TODO: THIS FUNCTION WILL NOT WORK BECAUSE OF THE ORDER.TYPE
    def get_order_action(self, order_id):
        try:
            # Retrieve the order history
            orders = mt.history_orders_get(position=order_id)
            if orders is None or len(orders) == 0:
                print(f"No orders found for position {order_id}.")
                return None

            # Get the first order (assuming there is only one order for the position)
            order = orders[0]

            # Determine the order action based on the type
            if order.type == mt.ORDER_TYPE_BUY:
                action = "BUY"
            elif order.type == mt.ORDER_TYPE_SELL:
                action = "SELL"
            elif order.type == mt.ORDER_TYPE_BUY_LIMIT:
                action = "BUY LIMIT"
            elif order.type == mt.ORDER_TYPE_SELL_LIMIT:
                action = "SELL LIMIT"
            elif order.type == mt.ORDER_TYPE_BUY_STOP:
                action = "BUY STOP"
            elif order.type == mt.ORDER_TYPE_SELL_STOP:
                action = "SELL STOP"
            elif order.type == mt.ORDER_TYPE_CLOSE_BY:
                action = "CLOSE BY"
            elif order.type == mt.ORDER_TYPE_PENDING:
                action = "PENDING"
            else:
                action = "UNKNOWN"

            return action

        except Exception as e:
            print(f"Error in get_order_action: {str(e)}")
            return None

    def is_valid(self, symbol, volume, price):
        try:
            # Update the account information
            self.update_account_info()

            # Get the symbol information
            symbol_info = mt.symbol_info(symbol)
            if symbol_info is None:
                print(f"Symbol {symbol} not found.")
                return False

            # Calculate the required margin for the trade
            required_margin = mt.order_calc_margin(mt.ORDER_TYPE_BUY, symbol, volume, price)
            if required_margin is None:
                print("order_calc_margin(mt.ORDER_TYPE_BUY, symbol, volume, price) FAILED: error code = ", mt.last_error())
                return None

            # Check if the account balance is sufficient
            if self.account_info_balance < required_margin:
                print(f"Insufficient balance. Required: {required_margin}, Available: {self.account_info_balance}")
                return False

            # Check if the account equity is sufficient
            if self.account_info_equity < required_margin:
                print(f"Insufficient equity. Required: {required_margin}, Available: {self.account_info_equity}")
                return False

            # Check if the account free margin is sufficient
            if self.account_info_margin_free < required_margin:
                print(f"Insufficient free margin. Required: {required_margin}, Available: {self.account_info_margin_free}")
                return False

            # All checks passed, the account is valid for the trade
            return True

        except Exception as e:
            print(f"Error in is_valid: {str(e)}")
            return False

    def update_account_info(self):
        # Update the account information when called
        # Make sure to call this function before accessing the account-related attributes
        self.account_info = self.get_account_info()
        self.account_balance = self.account_info.balance if self.account_info is not None else None
        self.account_equity = self.account_info.equity if self.account_info is not None else None
        self.account_margin = self.account_info.margin if self.account_info is not None else None
        self.account_margin_free = self.account_info.margin_free if self.account_info is not None else None
        self.account_margin_level = self.account_info.margin_level if self.account_info is not None else None

    def terminal_shutdown(self):
        # Close the previous established connection to the MetaTrader5 terminal
        mt.shutdown()
