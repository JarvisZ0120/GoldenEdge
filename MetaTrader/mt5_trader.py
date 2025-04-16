# pyright: reportAttributeAccessIssue=false
import MetaTrader5 as mt5
import pandas as pd


class MT5Trader:
    """
    A wrapper class for doing MetaTrader5 trading.

    """

    def __init__(self, logger) -> None:
        """
        Initialize the MT5Trader class.

        Args:
            logger: A logger instance for logging messages.
        """
        self.logger = logger
        self.is_connected = False

    def get_mt5(self) -> mt5.mt5:
        """
        Get the MetaTrader5 module instance.

        Returns:
            MetaTrader5: The MetaTrader5 module for executing trading operations.
        """
        return mt5

    def connect(self, account: int, password: str, server: str) -> bool:
        """
        Connect to MetaTrader5 with the given account credentials.

        Args:
            account (int): MetaTrader5 account number.
            password (str): Password for the account.
            server (str): Server address (e.g., 'MetaQuotes-Demo').

        Returns:
            bool: True if connected successfully.

        Raises:
            ValueError: If initialization or login fails.
        """
        if not mt5.initialize():
            self.logger.error(" ⚠️ Failed to initialize MetaTrader5.")
            raise ValueError(" ⚠️ Failed to initialize MetaTrader5.")

        authorized = mt5.login(account, password, server)
        if not authorized:
            self.logger.error(" ⚠️ Failed to log in MetaTrader5 account.")
            mt5.shutdown()
            raise ValueError(" ⚠️ Failed to log in MetaTrader5 account.")

        self.is_connected = True
        self.logger.info(" ✅ Successfully connected to MetaTrader5.")
        return True

    def disconnect(self) -> None:
        """
        Disconnect from MetaTrader5 and clean up resources.
        """
        mt5.shutdown()
        self.is_connected = False
        self.logger.info(" ✅ Successfully disconnected from MetaTrader5.")

    def get_timeframe(self, timeframe: str) -> int | None:
        """
        Convert string timeframe to MetaTrader5 constant.

        Args:
            timeframe (str): One of ['M1', 'M5', 'M15', 'M30', 'H1', 'H4'].

        Returns:
            int | None: MT5 timeframe constant, or None if invalid.
        """
        switch = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
        }
        return switch.get(timeframe, None)

    def fetch_ohlcv(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Fetch OHLCV data for a given symbol and timeframe.

        Args:
            symbol (str): Trading symbol (e.g., 'XAUUSD').
            timeframe (str): Timeframe string (e.g., 'M1', 'H1').

        Returns:
            pd.DataFrame: DataFrame containing OHLCV data with time column.

        Raises:
            ValueError: If not connected or invalid parameters.
        """
        if not self.is_connected:
            self.logger.error(" ⚠️ MetaTrader5 is not connected to fetch data.")
            raise ValueError(" ⚠️ MetaTrader5 is not connected to fetch data.")

        mt5_timeframe = self.get_timeframe(timeframe)
        if mt5_timeframe is None:
            self.logger.error(" ⚠️ Invalid timeframe provided.")
            raise ValueError(" ⚠️ Invalid timeframe provided.")

        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, 1000)
        if rates is None or len(rates) == 0:
            self.logger.error(" ⚠️ Failed to get MetaTrader5 rates.")
            raise ValueError(" ⚠️ Failed to get MetaTrader5 rates.")

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    def get_positions(self) -> int:
        """
        Retrieve and count all currently open positions.

        Returns:
            int: Number of open positions.

        Raises:
            ValueError: If positions cannot be retrieved.
        """
        positions = mt5.positions_get()
        if positions is None:
            self.logger.error("⚠️ Failed to retrieve positions.")
            raise ValueError("⚠️ Failed to retrieve positions.")
        return len(positions)

    def remove_pending_orders(self, order_type: str | None = None) -> None:
        """
        Remove pending orders from MetaTrader5.

        Args:
            order_type (str | None): Type of order to remove, one of:
                "buy_limit", "sell_limit", "buy_stop", "sell_stop", or None to remove all.

        Raises:
            ValueError: If failed to retrieve or remove pending orders.
        """
        type_map = {
            "buy_limit": mt5.ORDER_TYPE_BUY_LIMIT,
            "sell_limit": mt5.ORDER_TYPE_SELL_LIMIT,
            "buy_stop": mt5.ORDER_TYPE_BUY_STOP,
            "sell_stop": mt5.ORDER_TYPE_SELL_STOP,
        }

        type_id = None
        if order_type is not None:
            order_type_lower = order_type.lower()
            if order_type_lower not in type_map:
                self.logger.error(" ⚠️ Unknown order_type: {order_type}")
                raise ValueError(f" ⚠️ Unknown order_type: {order_type}")
            type_id = type_map[order_type_lower]

        pending_orders = mt5.orders_get()

        if pending_orders is None:
            self.logger.error(" ⚠️ Failed to retrieve pending orders.")
            raise ValueError(" ⚠️ Failed to retrieve pending orders.")

        removed_count = 0
        for order in pending_orders:
            if type_id is not None and order.type != type_id:
                continue

            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order.ticket,
            }

            result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                msg = f" ✅ Successfully removed order {order.ticket} (type {order.type})."
                print(msg)
                self.logger.info(msg)
                removed_count += 1
            else:
                err = f" ⚠️ Failed to remove order {order.ticket} (type {order.type}). Retcode: {result.retcode}"
                print(err)
                self.logger.error(err)

        if removed_count == 0:
            print(" ⚠️ No matching pending orders were removed.")

    def place_market_order(
        self,
        symbol: str,
        direction: str,
        lot: float,
        atr: float,
        tp_k: float = 2.0,
        sl_k: float = 1.0,
    ) -> None:
        """
        Places a market order with stop loss and take profit based on ATR.

        Args:
            symbol (str): Trading symbol (e.g., "XAUUSD").
            direction (str): "buy" or "sell".
            lot (float): Lot size to trade.
            atr (float): Average True Range, used to calculate SL/TP distances.
            tp_k (float, optional): Take-profit multiplier of ATR. Defaults to 2.0.
            sl_k (float, optional): Stop-loss multiplier of ATR. Defaults to 1.0.

        Raises:
            ValueError: If order fails to send.
        """
        if direction.lower() not in ("buy", "sell"):
            self.error(f" ⚠️ Invalid direction: {direction}")
            raise ValueError(f" ⚠️ Invalid direction: {direction}")

        info_tick = mt5.symbol_info_tick(symbol)
        if info_tick is None:
            self.error(f" ⚠️ Failed to get tick data for symbol {symbol}")
            raise ValueError(f" ⚠️ Failed to get tick data for symbol {symbol}")

        price = info_tick.ask if direction.lower() == "buy" else info_tick.bid
        order_type = (
            mt5.ORDER_TYPE_BUY if direction.lower() == "buy" else mt5.ORDER_TYPE_SELL
        )

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            self.error(f" ⚠️ Failed to get symbol info for {symbol}")
            raise ValueError(f" ⚠️ Failed to get symbol info for {symbol}")
        digits = symbol_info.digits

        sl_dist = round(sl_k * atr, digits)
        tp_dist = round(tp_k * atr, digits)

        sl = price - sl_dist if direction.lower() == "buy" else price + sl_dist
        tp = price + tp_dist if direction.lower() == "buy" else price - tp_dist

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": round(price, digits),
            "sl": round(sl, digits),
            "tp": round(tp, digits),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result is None:
            self.logger.error(" ⚠️ Failed to send order request. Request: %s", request)
            raise ValueError(" ⚠️ Failed to send order request.")

        self.logger.info(" ✅ Order request sent. Result: %s", result)

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f" ✅ Order placed successfully at price: {round(price, digits)}")
            self.logger.info(
                " ✅ Order placed successfully at price: %s", round(price, digits)
            )
        else:
            print(f" ⚠️ Order failed: {result.comment}")
            self.logger.error(" ⚠️ Order failed: %s", result.comment)
            raise ValueError(f" ⚠️ Order failed: {result.comment}")

    def place_grid_orders(
        self,
        direction: str,
        symbol: str,
        lot: float,
        max_grid_orders: int,
        atr: float,
        grid_step: float,
        tp_k: float = 2.5,
        sl_k: float = 1.5,
    ) -> None:
        """
        Places a series of grid pending orders (buy limit or sell limit) based on ATR and step size.

        Args:
            direction (str): "buy" or "sell".
            symbol (str): Trading symbol, e.g. "XAUUSD".
            lot (float): Lot size for each order.
            max_grid_orders (int): Total number of grid orders to place.
            atr (float): Average True Range value for calculating SL/TP.
            grid_step (float): Distance between each grid order.
            tp_k (float, optional): TP multiplier of ATR. Default is 2.5.
            sl_k (float, optional): SL multiplier of ATR. Default is 1.5.

        Raises:
            ValueError: If any order placement fails.
        """
        if direction.lower() not in ("buy", "sell"):
            raise ValueError(f" ⚠️ Invalid direction: {direction}")

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise ValueError(f" ⚠️ Failed to get tick info for symbol {symbol}")

        price = tick.ask if direction.lower() == "buy" else tick.bid

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            raise ValueError(f" ⚠️ Failed to get symbol info for {symbol}")
        digits = symbol_info.digits

        for i in range(max_grid_orders):
            grid_price = (
                price - i * grid_step
                if direction.lower() == "buy"
                else price + i * grid_step
            )
            grid_price = round(grid_price, digits)

            sl = (
                grid_price - sl_k * atr
                if direction.lower() == "buy"
                else grid_price + sl_k * atr
            )
            tp = (
                grid_price + tp_k * atr
                if direction.lower() == "buy"
                else grid_price - tp_k * atr
            )

            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": lot,
                "type": (
                    mt5.ORDER_TYPE_BUY_LIMIT
                    if direction.lower() == "buy"
                    else mt5.ORDER_TYPE_SELL_LIMIT
                ),
                "price": round(grid_price, digits),
                "sl": round(sl, digits),
                "tp": round(tp, digits),
                "comment": f"Grid Order {direction.upper()} #{i+1}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result is None:
                self.logger.error(
                    f" ⚠️ Grid order {i+1} failed to send. Request: {request}"
                )
                raise ValueError(" ⚠️ Failed to send grid order.")
            elif result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f" ⚠️ Grid order {i+1} failed: {result.comment}")
                raise ValueError(f" ⚠️ Grid order failed: {result.comment}")
            else:
                print(f" ✅ Grid order {i+1} placed at {grid_price}")
                self.logger.info(f" ✅ Grid order {i+1} placed at {grid_price}")


from others.log_manager import LogManager


def main():
    # 1. initialize logger
    logger = LogManager().get_logger()

    # 2. initialize MT5Trader instance
    trader = MT5Trader(logger)

    # 3. connect MT5 account
    ACCOUNT = 5035257814
    PASSWORD = "!7XvJjRs"
    SERVER = "MetaQuotes-Demo"

    try:
        trader.connect(ACCOUNT, PASSWORD, SERVER)

        # 4. get data
        df = trader.fetch_ohlcv("XAUUSD", "M1")
        print(df.tail())

        # 5. get positions
        position_count = trader.get_positions()
        print(f"📌 Current positions: {position_count}")

        # 6. market order test（using mock atr）
        trader.place_market_order(
            symbol="XAUUSD",
            direction="buy",
            lot=0.01,
            atr=1.0,
        )

        # 7. remove orders（all order_type）
        trader.remove_pending_orders()

        # 8. place grid oders (eg. BUY)
        trader.place_grid_orders(
            direction="buy",
            symbol="XAUUSD",
            lot=0.05,
            max_grid_orders=3,
            atr=1.0,
            grid_step=0.5,
        )

        # 9. remove orders（all order_type）
        trader.remove_pending_orders()

    except Exception as e:
        logger.error(f"exception: {e}")

    finally:
        # 9. disconnect
        trader.disconnect()


if __name__ == "__main__":
    main()
