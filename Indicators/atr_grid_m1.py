import pandas as pd
import talib


class ATRGridM1:
    def __init__(self, df, timeperiod=14):
        """
        初始化 ATR 指标计算类
        
        参数：
            df: pandas DataFrame, 必须包含 'high', 'low', 'close' 列
            timeperiod: int, 计算 ATR 的周期（默认 14）
        """
        self.df = df
        self.timeperiod = timeperiod

    def get_atr(self):
        """
        计算 ATR (Average True Range)
        
        返回：
            float: 最新的 ATR 值
        """
        atr_series = talib.ATR(self.df['high'], self.df['low'], self.df['close'], timeperiod=self.timeperiod)
        return round(atr_series.iloc[-1], 3)

    # def is_high_volatility(self, threshold=1.5):
    #     """
    #     判断市场是否处于高波动状态
        
    #     参数：
    #         threshold: float, ATR 高波动阈值 (默认 1.5)
        
    #     返回：
    #         bool: 若 ATR > threshold, 则返回 True (高波动)，否则返回 False
    #     """
    #     atr_value = self.get_atr()
    #     return atr_value > threshold

    # def is_low_volatility(self, threshold=0.5):
        """
        判断市场是否处于低波动状态
        
        参数：
            threshold: float, ATR 低波动阈值 (默认 0.5)
        
        返回：
            bool: 若 ATR < threshold, 则返回 True (低波动)，否则返回 False
        """
        atr_value = self.get_atr()
        return atr_value < threshold


# 示例用法：
if __name__ == "__main__":
    # 模拟数据示例
    data = {
        "high": [1.15, 1.18, 1.20, 1.22, 1.21, 1.24, 1.26, 1.28, 1.25, 1.30, 1.28, 1.32,
                 1.15, 1.18, 1.20],
        "low": [1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20,
                1.10, 1.12, 1.14],
        "close": [1.12, 1.14, 1.18, 1.20, 1.19, 1.22, 1.24, 1.26, 1.23, 1.28, 1.26, 1.30,
                  1.12, 1.14, 1.18]
    }
    df = pd.DataFrame(data)
    
    atr_analyzer = ATRGridM1(df)
    
    # 获取 ATR
    atr_value = atr_analyzer.get_atr()
    print(f"最新的 ATR 值: {atr_value}")
    
    # # 判断是否高波动
    # if atr_analyzer.is_high_volatility():
    #     print("市场处于高波动状态！")
    # else:
    #     print("市场未达到高波动标准。")
    
    # # 判断是否低波动
    # if atr_analyzer.is_low_volatility():
    #     print("市场处于低波动状态！")
    # else:
    #     print("市场未达到低波动标准。")
