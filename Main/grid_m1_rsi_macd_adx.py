import time
from MetaTrader.mt5_connection import MT5Connection
from MetaTrader.mt5_data_fetcher import MT5DataFetcher
from MetaTrader.mt5_grid_trader import MT5GridTrader
from Indicators.macd import MACD
from Indicators.rsi import RSI
from Indicators.adx import ADX
from Indicators.atr import ATR
from Others.log_manager import LogManager

if __name__ == "__main__":
    # 配置 log 文件
    log_manager = LogManager()
    logger = log_manager.get_logger()
    logger.info("logger 初始化成功！")

    # 配置登录信息
    account = 5033993521
    password = "G!I0FwJn"
    server = "MetaQuotes-Demo"
    symbol = "XAUUSD"
    timeframe = "M1"
    lot_size = 0.01
    max_grid_orders = 5
    grid_step = 1

    # 创建 MT5 连接实例
    mt5_connection = MT5Connection(account, password, server)

    # 连接到 MT5
    mt5_connection.connect()
    mt5 = mt5_connection.get_mt5()

    # 循环爬取数据并进行下单操作
    while True:
        account_info = mt5.account_info()
        print("")
        logger.info("")
        print(f"Account Balance: {account_info.balance}")
        logger.info(f"Account Balance: {account_info.balance}")

        # 获取 OHLCV
        mt5_data_fetcher = MT5DataFetcher(mt5_connection)
        ohlcv_data = mt5_data_fetcher.fetch_ohlcv(symbol, timeframe)

        # 获取 MACD
        macd_analyzer = MACD(ohlcv_data, 12, 26, 9)
        macd, signal, hist = macd_analyzer.get_macd()
        # 判断是否出现金叉（多头信号）和死叉（空头信号）
        is_bullish = macd_analyzer.is_macd_bullish()
        is_bearish = macd_analyzer.is_macd_bearish()
        # 显示数据
        print(f"MACD: {macd: .2f}, Signal: {signal: .2f}, Histogram: {hist: .2f}")
        logger.info(f"Hist: {hist: .2f}")

        # 获取 RSI
        rsi_analyzer = RSI(ohlcv_data, 14)
        rsi_value = rsi_analyzer.get_rsi()
        # 判断超买超卖
        is_overbought = rsi_analyzer.is_overbought(65)
        is_oversold = rsi_analyzer.is_oversold(35)
        # 显示数据
        print(f"RSI: {rsi_value}")
        logger.info(f"RSI: {rsi_value: .2f}")

        # 获取 ADX
        adx_analyzer = ADX(ohlcv_data, 30)
        adx_value = adx_analyzer.get_adx()
        is_range_market = adx_analyzer.is_range_market(40)
        print(f"ADX: {adx_value}")
        logger.info(f"ADX: {adx_value: .2f}")

        # 获取 ATR
        atr_analyzer = ATR(ohlcv_data, 14)
        atr_value = atr_analyzer.get_atr()
        dynamic_atr_value = atr_analyzer.get_dynamic_atr()
        print(f"ATR: {atr_value}")
        logger.info(f"ATR: {atr_value: .2f}")
        print(f"Dynamic ATR: {dynamic_atr_value}")
        logger.info(f"Dynamic ATR: {dynamic_atr_value: .2f}")

        # 下单
        mt5_grid_trader = MT5GridTrader(mt5_connection, symbol, lot_size, max_grid_orders, grid_step, timeframe, dynamic_atr_value, log_manager)
        if not mt5_grid_trader.has_active_orders():
            mt5_grid_trader.remove_orders(mt5.ORDER_TYPE_BUY_LIMIT)
            mt5_grid_trader.remove_orders(mt5.ORDER_TYPE_SELL_LIMIT)
        
        # 判断趋势并执行网格交易
        if is_range_market:
            if is_oversold and is_bullish:
                print("📈 触发买入网格")
                logger.info("📈 触发买入网格")
                mt5_grid_trader.place_grid_orders("buy")
                mt5_grid_trader.remove_orders(mt5.ORDER_TYPE_SELL_LIMIT)
            elif is_overbought and is_bearish:
                print("📉 触发卖出网格")
                logger.info("📈 触发卖出网格")
                mt5_grid_trader.place_grid_orders("sell")
                mt5_grid_trader.remove_orders(mt5.ORDER_TYPE_BUY_LIMIT)

        time.sleep(10)  # 每 10 秒运行一次策略