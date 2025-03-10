# import MetaTrader5 as mt5
# import time
# from MetaTrader.mt5_connection import MT5Connection
# from MetaTrader.mt5_data_fetcher import MT5DataFetcher
# from Indicators.macd_grid_m1 import MACDGridM1
# from Indicators.rsi_grid_m1 import RSIGridM1
# from Indicators.atr_grid_m1 import ATRGridM1
# from Others.log_manager import LogManager

class MT5GridTrader:
    def __init__(self, mt5_connection, symbol, lot_size, max_grid_orders, grid_step, timeframe, dynamic_atr, log_manager):
        self.mt5_connection = mt5_connection
        self.mt5 = self.mt5_connection.get_mt5()
        self.symbol = symbol
        self.lot_size = lot_size
        self.max_grid_orders = max_grid_orders
        self.grid_step = grid_step
        self.timeframe = self.get_timeframe(timeframe)
        self.dynamic_atr = dynamic_atr
        self.logger = log_manager.get_logger()
    
    def get_timeframe(self,timrframe):
        """
        获取 MetaTrader5 相对应的 TIMEFRAME
        """

        mt5 = self.mt5
        switch = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
        }
        return switch.get(timrframe, None) 
    
    def place_grid_orders(self, direction):
        """执行网格挂单"""
        price = self.mt5.symbol_info_tick(self.symbol).ask if direction == "buy" else self.mt5.symbol_info_tick(self.symbol).bid
        
        for i in range(self.max_grid_orders):
            grid_price = (price - i * self.grid_step) if direction == "buy" else (price + i * self.grid_step)
            atr = self.dynamic_atr
            
            request = {
                "action": self.mt5.TRADE_ACTION_PENDING,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": self.mt5.ORDER_TYPE_BUY_LIMIT if direction == "buy" else self.mt5.ORDER_TYPE_SELL_LIMIT,
                "price": grid_price,
                "sl": grid_price - (atr * 1.5) if direction == "buy" else grid_price + (atr * 1.5),
                "tp": grid_price + (atr * 2.5) if direction == "buy" else grid_price - (atr * 2.5),
                "comment": "Grid Order M1",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC
            }
            
            result = self.mt5.order_send(request)
            if result is None:
                print("⚠️ 订单发送失败! ")
                self.logger.info("⚠️ 订单发送失败! ")
                self.mt5_connection.disconnect()
                quit()
            
            if result.retcode == self.mt5.TRADE_RETCODE_DONE:
                print(f"✅ 成功挂单: {grid_price}")
                self.logger.info(f"✅ 成功挂单: {grid_price}")
            else:
                print(f"⚠️ 挂单失败: {result.comment}")
                self.logger.info(f"⚠️ 挂单失败: {result.comment}")

    
    def remove_orders(self, order_type):
        """删除指定类型的挂单 (Buy Limit / Sell Limit)"""
        pending_orders = self.mt5.orders_get()
        if pending_orders is None:
            print("⚠️ 无法获取挂单信息! ")
            self.logger.info("⚠️ 无法获取挂单信息! ")
            return
        
        for order in pending_orders:
            if order.type == order_type:
                request = {"action": self.mt5.TRADE_ACTION_REMOVE, "order": order.ticket}
                result = self.mt5.order_send(request)
                
                if result.retcode == self.mt5.TRADE_RETCODE_DONE:
                    print(f"✅ 成功删除 {order_type} 订单 {order.ticket}!")
                    self.logger.info(f"✅ 成功删除 {order_type} 订单 {order.ticket}!")

                else:
                    print(f"⚠️ 删除 {order_type} 订单 {order.ticket} 失败! 错误代码：{result.retcode}")
                    self.logger.info(f"⚠️ 删除 {order_type} 订单 {order.ticket} 失败! 错误代码：{result.retcode}")
    def has_active_orders(self):
        """检查是否有进行中的订单（持仓）"""
        positions = self.mt5.positions_get()
        if positions is None:
            print("⚠️ 获取持仓失败!")
            self.logger.info("⚠️ 获取持仓失败!")

            return False
        return len(positions) > 0

# if __name__ == "__main__":
#      # 配置登录信息
#     account = 5033993521
#     password = "G!I0FwJn"
#     server = "MetaQuotes-Demo"
#     symbol = "XAUUSD"
#     timeframe = "M1"
#     lot_size = 0.01
#     max_grid_orders = 5
#     grid_step = 1

#     # 创建 MT5 连接实例
#     mt5_connection = MT5Connection(account, password, server)

#     # 连接到 MT5
#     mt5_connection.connect()
#     # print(f"已经连接：{mt5_connection.is_connected()}")
#     mt5 = mt5_connection.get_mt5()
#     # mt5_connection.disconnect()

#     while True:
#         account_info = mt5.account_info()
#         print(f"Account Balance: {account_info.balance}")

#         # 获取OHLCV
#         mt5_data_fetcher = MT5DataFetcher(mt5_connection)
#         ohlcv_data = mt5_data_fetcher.fetch_ohlcv(symbol, timeframe)
#         # 显示数据
#         # if not ohlcv_data.empty:
#         #     print(ohlcv_data.tail(5))
#         # else:
#         #     print("No data fetched.")

#         # 获取MACD
#         macd_analyzer = MACDGridM1(ohlcv_data)
#         macd, signal, hist = macd_analyzer.get_macd()
#         # 判断是否出现金叉（多头信号）和死叉（空头信号）
#         is_bullish = macd_analyzer.is_macd_bullish()
#         is_bearish = macd_analyzer.is_macd_bearish()
#         # 显示数据
#         print(f"MACD: {macd: .2f}, Signal: {signal: .2f}, Histogram: {hist: .2f}")
#         # print(f"是否金叉：{is_bullish}")
#         # print(f"是否死叉：{is_bearish}")

#         # 获取RSI
#         rsi_analyzer = RSIGridM1(ohlcv_data)
#         # 判断超买超卖
#         rsi_value = rsi_analyzer.get_rsi()
#         is_overbought = rsi_analyzer.is_overbought()
#         is_oversold = rsi_analyzer.is_oversold()
#         # 显示数据
#         print(f"RSI: {rsi_value}")
#         # print(f"是否超卖：{is_oversold}")
#         # print(f"是否超买：{is_overbought}")

#         # 获取ATR
#         atr_analyzer = ATRGridM1(ohlcv_data)
#         atr_value = atr_analyzer.get_atr()
#         print(f"ATR: {atr_value}")
#         print("")

#         # 下单
#         mt5_grid_trader = MT5GridTrader(mt5_connection, symbol, lot_size, max_grid_orders, grid_step, timeframe,atr_value)
#         if not mt5_grid_trader.has_active_orders():
#             mt5_grid_trader.remove_orders(mt5.ORDER_TYPE_BUY_LIMIT)
#             mt5_grid_trader.remove_orders(mt5.ORDER_TYPE_SELL_LIMIT)
        
#         # 判断趋势并执行网格交易
#         if is_oversold and is_bullish:
#             print("📈 触发买入网格")
#             mt5_grid_trader.place_grid_orders("buy")
#             mt5_grid_trader.remove_orders(mt5.ORDER_TYPE_SELL_LIMIT)
#         elif is_overbought and is_bearish:
#             print("📉 触发卖出网格")
#             mt5_grid_trader.place_grid_orders("sell")
#             mt5_grid_trader.remove_orders(mt5.ORDER_TYPE_BUY_LIMIT)

#         time.sleep(10)  # 每 10 秒运行一次策略