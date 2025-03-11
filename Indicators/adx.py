import pandas as pd
import talib


class ADX:
    def __init__(self, df, timeperiod=30):
        """
        初始化 ADXIndicator 类，用于计算 ADX 指标。

        参数：
            df: pandas DataFrame, 必须包含 'high', 'low', 'close' 列
            timeperiod: int, 计算 ADX 的周期(默认 30)
        """
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            print(f"⚠️ DataFrame 缺失 'high', 'low', 'close' 列, 无法计算ADX! ")
        
        self.df = df
        self.timeperiod = timeperiod

    def get_adx(self):
        """
        计算并返回最新的 ADX 值。

        返回：
            float: 最新的 ADX 值
        """
        if len(self.df) < self.timeperiod + 1:
            print("⚠️ 数据量太少，无法计算 ADX! ")
            return False
        
        adx_series = talib.ADX(self.df['high'], self.df['low'], self.df['close'], timeperiod=self.timeperiod)
        return round(adx_series.iloc[-1], 3)

    def is_range_market(self, threshold):
        """
        判断市场是否为震荡市场 (范围盘),
        当 ADX 值低于设定阈值 (例如 35) 时，认为市场处于震荡状态。

        参数：
            threshold: float, 判断震荡市场的 ADX 阈值 (默认 35)
        
        返回：
            bool: 若 ADX < threshold, 则返回 True (震荡市场)，否则返回 False (趋势市场)
        """
        return self.get_adx() < threshold
    
    def is_trending_market(self, threshold):
        """
        判断市场是否为趋势行情。
        当 ADX 值大于设定阈值时，认为市场处于趋势行情。

        参数：
            threshold: float, 判断趋势市场的 ADX 阈值 (默认 35)
        
        返回：
            bool: 若 ADX > threshold, 则返回 True (趋势行情)，否则返回 False (震荡市场)
        """
        return self.get_adx() >= threshold

# 示例用法
if __name__ == "__main__":
    # 模拟数据示例，实际使用时需要从你的数据源获取数据

    # TODO: data 中数据不足30 周期， 需修改 ---- Damon
    data = {
        "high": [1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20, 1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20, 
                 1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20, 1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20],
        "low": [1.08, 1.10, 1.12, 1.11, 1.10, 1.13, 1.15, 1.16, 1.14, 1.17, 1.16, 1.18, 1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20,
                1.08, 1.10, 1.12, 1.11, 1.10, 1.13, 1.15, 1.16, 1.14, 1.17, 1.16, 1.18, 1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20],
        "close": [1.09, 1.11, 1.13, 1.12, 1.11, 1.14, 1.16, 1.17, 1.15, 1.18, 1.17, 1.19, 1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20,
                  1.09, 1.11, 1.13, 1.12, 1.11, 1.14, 1.16, 1.17, 1.15, 1.18, 1.17, 1.19, 1.10, 1.12, 1.14, 1.13, 1.12, 1.15, 1.17, 1.18, 1.16, 1.19, 1.18, 1.20]
    }
    df = pd.DataFrame(data)
    
    adx_analyzer = ADX(df)
    
    # 获取 ADX
    adx_value = adx_analyzer.get_adx()
    print(f"最新的 ADX 值: {adx_value}")
    
    # 判断是否为震荡市场
    if adx_analyzer.is_range_market(35):
        print("市场处于震荡状态。")
    elif adx_analyzer.is_trending_market(35):
        print("市场处于趋势状态。")
    else:
        print("没判断出来！")
