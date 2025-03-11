
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
    
    def get_timeframe(self,timeframe):
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
        return switch.get(timeframe, None) 

    
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
