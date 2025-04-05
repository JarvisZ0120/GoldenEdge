import backtrader as bt
import pandas as pd


class GridMACDStrategy(bt.Strategy):
    params = (
        ("macd_fast", 12),
        ("macd_slow", 26),
        ("macd_signal", 9),

        ("rsi_period", 14),
        ("rsi_overbought", 65),
        ("rsi_oversold", 35),

        ("adx_period", 30),
        ("adx_range", 40),

        ("atr_period", 14),

        ("grid_step", 1.0),
        ("max_grid_orders", 5),
        ("lot_size", 0.01),  
    )

    def log(self, txt):
        dt = self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d %H:%M')
        print(f"[{dt}] {txt}")

    def __init__(self):
        self.macd = bt.indicators.MACD(
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal,
        )
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        self.adx = bt.indicators.ADX(period=self.params.adx_period)
        self.atr = bt.indicators.ATR(period=self.params.atr_period)

        self.dataclose = self.datas[0].close
        self.order = None
        self.grid_orders = []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            tp = getattr(order.info, 'tp', None)
            sl = getattr(order.info, 'sl', None)
            tp_str = f"{tp:.2f}" if isinstance(tp, (int, float)) else "N/A"
            sl_str = f"{sl:.2f}" if isinstance(sl, (int, float)) else "N/A"
            if order.isbuy():
                self.log(f"✅ 买入执行: {order.executed.price:.2f} | 止盈: {tp_str} | 止损: {sl_str}")
            else:
                self.log(f"✅ 卖出执行: {order.executed.price:.2f} | 止盈: {tp_str} | 止损: {sl_str}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"⚠️ 订单失败 [{order.getstatusname()}] | 价格: {order.created.price:.2f} | 资金: {self.broker.getcash():.2f}")

    def get_max_affordable_orders(self, unit_price):
        self.log(f"UNIT_PRICE: {unit_price}")
        est_cost_per_order = unit_price * self.params.lot_size * 1.01  
        max_affordable = int(self.broker.getcash() // est_cost_per_order)
        max_orders = min(max_affordable, self.params.max_grid_orders)
        self.log(f"可承受订单数: {max_orders}, 每单成本估算: {est_cost_per_order:.2f}")
        return max_orders

    def place_grid_orders(self, direction):
        base_price = self.dataclose[0]
        atr = self.atr[0]
        max_orders = self.get_max_affordable_orders(base_price)

        for i in range(max_orders):
            grid_price = base_price - i * self.params.grid_step if direction == "buy" else base_price + i * self.params.grid_step
            tp = grid_price + 2 * atr if direction == "buy" else grid_price - 2 * atr
            sl = grid_price - 1.5 * atr if direction == "buy" else grid_price + 1.5 * atr

            size = self.params.lot_size
            if direction == "buy":
                main, stop, limit = self.buy_bracket(
                    size=size,
                    price=grid_price,
                    exectype=bt.Order.Limit,
                    stopargs=dict(price=sl),
                    limitargs=dict(price=tp),
                )
            else:
                main, stop, limit = self.sell_bracket(
                    size=size,
                    price=grid_price,
                    exectype=bt.Order.Limit,
                    stopargs=dict(price=sl),
                    limitargs=dict(price=tp),
                )

            # 添加信息到主订单
            main.info.tp = tp
            main.info.sl = sl

            self.grid_orders.append((main, stop, limit))
            self.log(f"📌 挂单[{direction.upper()}] 价格: {grid_price:.2f}, TP: {tp:.2f}, SL: {sl:.2f}, Size: {size}")

    def next(self):
        # 输出调试信息
        self.log(f"MACD: {self.macd.macd[0]:.2f}, Signal: {self.macd.signal[0]:.2f}, RSI: {self.rsi[0]:.2f}, ADX: {self.adx[0]:.2f}")
        
        is_bullish = self.macd.macd[0] > self.macd.signal[0] and self.macd.macd[-1] < self.macd.signal[-1]
        is_bearish = self.macd.macd[0] < self.macd.signal[0] and self.macd.macd[-1] > self.macd.signal[-1]
        is_oversold = self.rsi[0] < self.params.rsi_oversold
        is_overbought = self.rsi[0] > self.params.rsi_overbought
        is_range_market = self.adx[0] < self.params.adx_range

        if not self.position:
            if is_range_market:
                if is_oversold and is_bullish:
                    self.log("📈 满足买入条件，执行网格挂单!")
                    self.place_grid_orders("buy")
                elif is_overbought and is_bearish:
                    self.log("📉 满足卖出条件，执行网格挂单!")
                    self.place_grid_orders("sell")




if __name__ == "__main__":
    datapath = "./XAUUSD_historical_data_30mins.csv"
    df = pd.read_csv(datapath, usecols=range(5))
    df.columns = ["datetime", "open", "high", "low", "close"]

    df["datetime"] = pd.to_datetime(df["datetime"], format="%m/%d/%Y %H:%M")
    df = df.sort_values(by="datetime").reset_index(drop=True)
    df.set_index("datetime", inplace=True)
    df["volume"] = 0  

    cerebro = bt.Cerebro()
    cerebro.addstrategy(GridMACDStrategy)

    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.broker.setcash(1000.0)
    cerebro.broker.setcommission(commission=0.001)

    print(f"💰 初始资金: {cerebro.broker.getvalue():.2f}")
    cerebro.run()
    print(f"💰 最终资金: {cerebro.broker.getvalue():.2f}")

    # cerebro.plot()
