import pandas as pd
import talib


class RSIGridM1:
    def __init__(self, df, timeperiod=14):
        """
        初始化 RSI 指标计算类
        
        参数：
            df: pandas DataFrame, 必须包含 'close' 列
            timeperiod: int, 计算 RSI 的周期（默认 14）
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame 缺失 'close' 列！")
        
        self.df = df
        self.timeperiod = timeperiod

    def get_rsi(self):
        """
        计算 RSI (相对强弱指数)
        
        返回：
            float: 最新的 RSI 值
        """
        rsi_series = talib.RSI(self.df['close'], timeperiod=self.timeperiod)
        return round(rsi_series.iloc[-1], 3)

    def is_overbought(self, threshold=65):
        """
        判断市场是否处于超买状态
        当 RSI 高于设定阈值时，可认为市场超买。
        
        参数：
            threshold: float, 判断超买的 RSI 阈值 (默认 65)
        
        返回：
            bool: 若 RSI > threshold, 则返回 True (超买), 否则返回 False
        """
        rsi_value = self.get_rsi()
        return rsi_value > threshold

    def is_oversold(self, threshold=35):
        """
        判断市场是否处于超卖状态
        当 RSI 低于设定阈值时，可认为市场超卖。
        
        参数：
            threshold: float, 判断超卖的 RSI 阈值 (默认 35)
        
        返回：
            bool: 若 RSI < threshold, 则返回 True (超卖), 否则返回 False
        """
        rsi_value = self.get_rsi()
        return rsi_value < threshold

# 示例用法
if __name__ == "__main__":
    # 模拟数据示例，实际使用时需要从你的数据源获取数据
    data = {
        "close": [1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20,
                  1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.2, 
                  1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20]
    }
    df = pd.DataFrame(data)
    
    rsi_analyzer = RSIGridM1(df)
    
    # 获取 RSI
    rsi_value = rsi_analyzer.get_rsi()
    print(f"最新的 RSI 值: {rsi_value}")
    
    # 判断是否超买
    if rsi_analyzer.is_overbought():
        print("市场超买！")
    else:
        print("市场没有超买。")
    
    # 判断是否超卖
    if rsi_analyzer.is_oversold():
        print("市场超卖！")
    else:
        print("市场没有超卖。")