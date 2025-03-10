import pandas as pd
import talib


class MACDGridM1:
    def __init__(self, df, fastperiod=12, slowperiod=26, signalperiod=9):
        """
        初始化 MACD 指标计算类
        
        参数：
            df: pandas DataFrame, 必须包含 'close' 列
            fastperiod: int, 快速 EMA 周期 (默认 12)
            slowperiod: int, 慢速 EMA 周期 (默认 26)
            signalperiod: int, 信号线 EMA 周期 (默认 9)
        """
        if 'close' not in df.columns:
            print("⚠️ DataFrame 缺失 'close' 列, 无法计算 MACD! ")
        
        self.df = df
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.signalperiod = signalperiod

    def get_macd(self):
        """
        计算 MACD 指标
        
        返回：
            tuple: (最新的 MACD 值, MACD 信号线, MACD 柱状图)
        """
        if len(self.df) < self.slowperiod + 1:
            print("⚠️ 数据量太少，无法计算 MACD! ")
            return False
        
        macd, signal, hist = talib.MACD(self.df['close'], 
                                        fastperiod=self.fastperiod, 
                                        slowperiod=self.slowperiod, 
                                        signalperiod=self.signalperiod)
        return round(macd.iloc[-1], 3), round(signal.iloc[-1], 3), round(hist.iloc[-1], 3)

    def is_macd_bullish(self):
        """
        判断是否出现 MACD 金叉（多头信号）
        
        返回：
            bool: 若 MACD 线上穿信号线，则返回 True (多头信号),否则返回 False
        """
        macd, signal, _ = self.get_macd()
        return macd > signal  # MACD 线上穿信号线，表示金叉（看涨信号）

    def is_macd_bearish(self):
        """
        判断是否出现 MACD 死叉（空头信号）
        
        返回：
            bool: 若 MACD 线下穿信号线，则返回 True(空头信号), 否则返回 False
        """
        macd, signal, _ = self.get_macd()
        return macd < signal  # MACD 线下穿信号线，表示死叉（看跌信号）

# 示例用法
if __name__ == "__main__":
    data = {
        'time': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'close': [100 + (i * 0.5) + (i % 5) * 2 for i in range(100)]  # 示例收盘价数据
    }
    df = pd.DataFrame(data)

    # 创建 macd_grid_m1 实例
    macd_analyzer = MACDGridM1(df)

    # 获取最新的 MACD 值和信号线
    macd, signal, hist = macd_analyzer.get_macd()

    # 判断是否出现金叉（多头信号）和死叉（空头信号）
    is_bullish = macd_analyzer.is_macd_bullish()
    is_bearish = macd_analyzer.is_macd_bearish()

    # 输出结果
    print(f"Latest MACD: {macd}, Signal: {signal}, Histogram: {hist}")
    print(f"是否金叉：{is_bullish}")
    print(f"是否死叉：{is_bearish}")



