import pandas as pd
from MetaTrader.mt5_connection import MT5Connection

class MT5DataFetcher:
    def __init__(self, mt5_connection):
        self.mt5_connection = mt5_connection

    def get_timeframe(self,timrframe):
        """
        获取 MetaTrader5 相对应的 TIMEFRAME
        """

        mt5 = self.mt5_connection.get_mt5()
        switch = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
        }
        return switch.get(timrframe, None) 

    def fetch_ohlcv(self, symbol, timeframe):
        """
        获取指定 symbol 和 timeframe 的 OHLCV 数据。

        返回：
            OHLCV的DataFrame格式
        """
        # 确保连接已建立
        if not self.mt5_connection.is_connected():
            print("⚠️ 请先连接到 MetaTrader 5! ")
            return pd.DataFrame()

        mt5 = self.mt5_connection.get_mt5()
        timeframe = self.get_timeframe(timeframe) 
        # 获取最近 1000 根 K 线
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1000)
        
        if rates is None or len(rates) == 0:
            print("⚠️ 无法获取数据! ")
            return pd.DataFrame()
        
        # 转换为 DataFrame 格式
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

# 示例用法：
if __name__ == "__main__":
    # 配置登录信息和数据
    account = 5033993521
    password = "G!I0FwJn"
    server = "MetaQuotes-Demo"

    mt5_connection = MT5Connection(account, password, server)
    mt5_connection.connect()

    # 创建 MT5DataFetcher 实例
    mt5_data_fetcher = MT5DataFetcher(mt5_connection)
    
    # 获取 OHLCV 数据
    ohlcv_data = mt5_data_fetcher.fetch_ohlcv("XAUUSD", "M1")
    
    # 显示数据
    if not ohlcv_data.empty:
        print(ohlcv_data.tail(5))
    else:
        print("No data fetched.")
    
    # 断开连接
    mt5_connection.disconnect()
