import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import talib
import logging

from datetime import datetime

# 获取当前日期和时间，格式为 YYYYMMDD_HHMMSS，例如 "20250206_153045"
date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = "app_M1_" + date_time_str + ".log"

# 配置 logging 模块，将日志信息写入文件 'app.log'
logging.basicConfig(
    level=logging.DEBUG,                          # 设置日志级别，可根据需要调整（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    format='%(asctime)s - %(levelname)s - %(message)s',  # 定义日志格式，包含时间、日志级别和信息
    filename=log_filename,                           # 指定日志文件的文件名
    filemode='a'                                  # 追加模式（如果希望每次运行覆盖日志，可将其改为 'w'）
)


# === 连接 MT4 ===
def connect_mt4():
    if not mt5.initialize():
        print("⚠️ MT4 连接失败")
        logging.error("MT4 Connected failed!")
        quit()

    account = 5033700150 
    authorized = mt5.login(account, password="!8AzJiDa", server="MetaQuotes-Demo")
    if not authorized:
        error_info = mt5.last_error()
        print("登录失败，错误代码：", error_info)
        logging.error("Login failed, error code: %s", error_info)
        mt5.shutdown()
        quit()

    print("✅ MT4 连接成功！Login Successfully!")
    logging.info("MT4 Connected successfully! Login Successfully!")

# === 交易参数 ===
symbol = "XAUUSD"  # 交易品种
grid_step = 1 # 网格间距（单位：美元）
take_profit = 3.0  # 止盈（单位：美元）
stop_loss = 5.0  # 止损（单位：美元）
max_grid_orders = 5  # 最大网格订单数
lot_size = 0.01  # 交易手数
timeframe = mt5.TIMEFRAME_M1

# === 获取市场数据 ===
def fetch_ohlcv():
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1000)  # 获取最近 1000 根 M1 K 线
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

# === 计算 RSI & MACD ===
def get_indicators(df):
    df["RSI"] = talib.RSI(df["close"], timeperiod=14)
    df["MACD"], df["MACD_signal"], df['MACD_hist'] = talib.MACD(df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
    return df

# === 获取当前订单数量 ===
def count_orders(order_type):
    count = 0
    orders = mt5.orders_get(symbol=symbol)
    if orders:
        for order in orders:
            if order.type == order_type:
                count += 1
    return count


def get_atr(symbol, timeframe, period=14):
    """ 计算 ATR (Average True Range) 并处理异常情况 """
    
    # 获取历史数据
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period + 1)
    
    # 处理获取数据失败的情况
    if rates is None or len(rates) < period + 1:
        print(f"⚠️ 无法获取 {symbol} 的历史数据，使用默认 ATR")
        logging.warning(f"Failed to get {symbol} history, using default ATR")
        return 1.0  # 返回默认 ATR，避免交易异常

    # 转换为 Pandas DataFrame
    df = pd.DataFrame(rates)
    
    # 计算 True Range (TR)
    df['high-low'] = df['high'] - df['low']
    df['high-prevclose'] = abs(df['high'] - df['close'].shift(1))
    df['low-prevclose'] = abs(df['low'] - df['close'].shift(1))
    
    # 取三者的最大值作为 TR
    df['tr'] = df[['high-low', 'high-prevclose', 'low-prevclose']].max(axis=1)
    
    # 计算 ATR (14周期)
    df['atr'] = df['tr'].rolling(window=period).mean()

    # 获取最新 ATR 值
    atr_value = df['atr'].iloc[-1]

    # 处理 ATR 计算失败的情况（避免 NaN）
    if np.isnan(atr_value) or atr_value <= 0:
        print(f"⚠️ ATR 计算失败，返回默认值 1.0")
        logging.warning("ATR calculation failed, using default ATR = 1.0")
        return 1.0

    # 打印 ATR 结果
    print(f"✅ ATR 计算成功: {atr_value}")
    logging.info(f"ATR calculated successfully: {atr_value}")
    
    return atr_value  # 返回最新 ATR 值


def get_dynamic_atr(symbol, timeframe, period=14):
    """ 计算 ATR 并动态调整 SL/TP """
    atr = get_atr(symbol, timeframe, period)
    
    if atr is None or atr <= 0:
        atr = 0.5  # M1 默认 0.5 美元
        logging.warning("M1 Dynamic ATR calculated failed")

    # 限制 ATR 适用范围，避免 SL 过大或过小
    atr = max(0.3, min(atr, 2.0))  # 限制 ATR 在 0.3 - 2.0 之间
    # 记录 ATR 计算日志
    print(f"✅ M1 动态 ATR 计算成功: {atr}")
    logging.info(f"M1 Dynamic ATR calculated: {atr}")
    return atr


# === 发送网格订单 ===
def place_grid_orders(direction):
    # 获取当前价格：买入时使用 ask 价，卖出时使用 bid 价
    price = mt5.symbol_info_tick(symbol).ask if direction == "buy" else mt5.symbol_info_tick(symbol).bid

    # "sl": grid_price - 100 * point if direction == "buy" else grid_price + 100 * point, 
    # "tp": grid_price + 250 * point if direction == "buy" else grid_price - 250 * point,

    for i in range(0, max_grid_orders):
        grid_price = (price - i * grid_step) if direction == "buy" else (price + i * grid_step)
        # point = mt5.symbol_info(symbol).point

        atr = get_dynamic_atr(symbol, timeframe)  # 获取 M1 ATR

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY_LIMIT if direction == "buy" else mt5.ORDER_TYPE_SELL_LIMIT,
            "price": grid_price,
            "sl": grid_price - (atr * 1.5) if direction == "buy" else grid_price + (atr * 1.5),
            "tp": grid_price + (atr * 2.5) if direction == "buy" else grid_price - (atr * 2.5),
            "comment": "Grid Order M1",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }
        
        result = mt5.order_send(request)
        if result is None:
            print("订单发送失败，返回结果为 None")
            logging.error("The order failed to be sent, and the return result is None. Request details: %s", request)
            mt5.shutdown()
            quit()
        else:
            print("订单发送成功，结果：", result)
            logging.info("The order was sent successfully, the result: %s", result)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            success_msg = f"✅ 成功挂单: {grid_price}"
            print(success_msg)
            logging.info(f"Successful order: {grid_price}")
        else:
            error_msg = f"⚠️ 挂单失败: {result.comment}"
            print(error_msg)
            logging.error(f"Order failed: {result.comment}")


def remove_orders(order_type):
    """ 删除指定类型的挂单(Buy Limit / Sell Limit)"""
    pending_orders = mt5.orders_get()
    if pending_orders is None:
        print("⚠️ 无法获取挂单信息")
        logging.error("Failed to retrieve pending orders")
        return

    for order in pending_orders:
        if order.type == order_type:
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order.ticket,
            }
            result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ 成功删除 {order_type} 订单 {order.ticket}")
                logging.info(f"Successfully removed {order_type} order {order.ticket}")
            else:
                print(f"⚠️ 删除 {order_type} 订单 {order.ticket} 失败，错误代码：{result.retcode}")
                logging.error(f"Failed to remove {order_type} order {order.ticket}, error code: {result.retcode}")



def place_one_order(direction):
    # 获取当前价格：买入时使用 ask 价，卖出时使用 bid 价
    price = mt5.symbol_info_tick(symbol).ask if direction == "buy" else mt5.symbol_info_tick(symbol).bid

    point = mt5.symbol_info(symbol).point

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": 0.2,
        "type": mt5.ORDER_TYPE_BUY_LIMIT if direction == "buy" else mt5.ORDER_TYPE_SELL_LIMIT,
        "price": price,
        "sl": price - 200 * point if direction == "buy" else price + 200 * point, 
        "tp": price + 50 * point if direction == "buy" else price - 50 * point,
        "comment": "Grid Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
        
    result = mt5.order_send(request)
    if result is None:
        print("订单发送失败，返回结果为 None")
        logging.error("The order failed to be sent, and the return result is None. Request details: %s", request)
        mt5.shutdown()
        quit()
    else:
        print("订单发送成功，结果：", result)
        logging.info("The order was sent successfully, the result: %s", result)



def has_active_orders():
    """ 检查是否有进行中的订单（持仓） """
    positions = mt5.positions_get()
    if positions is None:
        print("获取持仓失败")
        return False
    return len(positions) > 0



# === 交易主逻辑 ===
def main():
    connect_mt4()  # 假设该函数已定义，用于连接 MT4/MT5
    
    while True:
        account_info = mt5.account_info()
        print(f"Account Balance: {account_info.balance}")
        logging.info(f"Account Balance: {account_info.balance}")

        df = fetch_ohlcv()      # 获取最新市场数据（假设该函数已定义）
        df = get_indicators(df)   # 计算 RSI & MACD（假设该函数已定义）

        rsi_value    = df["RSI"].iloc[-1]
        macd_main    = df["MACD"].iloc[-1]
        macd_signal  = df["MACD_signal"].iloc[-1]
        macd_hist    = df['MACD_hist'].iloc[-1]


        indicator_msg = (f"RSI: {rsi_value:.2f}, MACD: {macd_main:.2f}, "
                         f"MACD Signal: {macd_signal:.2f}, MACD Hist: {macd_hist:.2f}")
        print(indicator_msg)
        logging.info(indicator_msg)

        if not has_active_orders():
            remove_orders(mt5.ORDER_TYPE_BUY_LIMIT)
            remove_orders(mt5.ORDER_TYPE_SELL_LIMIT)

        # 判断趋势并执行网格交易
        if rsi_value < 35 and macd_main > macd_signal and macd_hist > 0:
            print("📈 触发买入网格")
            logging.info("Triggering the Buy Grid")
            place_grid_orders("buy")
            remove_orders(mt5.ORDER_TYPE_SELL_LIMIT)
        elif rsi_value > 65 and macd_main < macd_signal and macd_hist < 0:
            print("📉 触发卖出网格")
            logging.info("Triggering the Sell Grid")
            place_grid_orders("sell")
            remove_orders(mt5.ORDER_TYPE_BUY_LIMIT)

        
        time.sleep(10)  # 每 10 秒运行一次策略

# 仅在脚本作为主程序运行时执行
if __name__ == "__main__":
    main()
