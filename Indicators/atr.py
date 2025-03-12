import pandas as pd
import talib


class ATR:
    def __init__(self, df, timeperiod=14):
        """
        初始化 ATR 指标计算类
        
        参数：
            df: pandas DataFrame, 必须包含 'high', 'low', 'close' 列
            timeperiod: int, 计算 ATR 的周期(默认 14)
        """
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            print(f"⚠️ 数据缺失 'high', 'low', 'close' 列, 无法计算ATR! ")
        self.df = df
        self.timeperiod = timeperiod


    # TODO: atr methiod 需要修改 --- Jarvis
    def get_atr(self):
        """
        计算 ATR (Average True Range)
        
        返回：
            float: 最新的 ATR 值
        """
        if len(self.df) < self.timeperiod + 1:
            print("⚠️ 数据量太少，无法计算 ATR! ")
        atr_series = talib.ATR(self.df['high'], self.df['low'], self.df['close'], timeperiod=self.timeperiod)
        return round(atr_series.iloc[-1], 3)



    def get_dynamic_atr(self):
        """ 计算 ATR 并动态调整 SL/TP """
        dynamic_atr = self.get_atr()
        
        if dynamic_atr is None or dynamic_atr <= 0:
            dynamic_atr = 0.5  # M1 默认 0.5 美元
            print("⚠️ Dynamic ATR 计算失败！")

        # 限制 ATR 适用范围，避免 SL 过大或过小
        dynamic_atr = max(0.3, min(dynamic_atr, 2.0))  # 限制 ATR 在 0.3 - 2.0 之间
        # 记录 ATR 计算日志
        return dynamic_atr
    
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
    
    atr_analyzer = ATR(df)
    
    # 获取 ATR
    atr_value = atr_analyzer.get_atr()
    dynamic_atr_value = atr_analyzer.get_dynamic_atr()
    print(f"ATR: {atr_value}")
    print(f"Dynamic ATR: {dynamic_atr_value}")
