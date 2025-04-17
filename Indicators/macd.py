import pandas as pd
import talib


class MACD:
    """
    A wrapper for calculating the MACD (Moving Average Convergence Divergence) using TA-Lib.

    """

    def __init__(
        self,
        df: pd.DataFrame,
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9,
    ):
        """
        Initialize the MACD calculator.

        Args:
            df (pd.DataFrame): A DataFrame with a 'close' price column.
            fastperiod (int): Fast EMA period. Default is 12.
            slowperiod (int): Slow EMA period. Default is 26.
            signalperiod (int): Signal line EMA period. Default is 9.

        Raises:
            ValueError: If the 'close' column is not found in the DataFrame.
        """
        self.df = df.copy()
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.signalperiod = signalperiod

        if "close" not in self.df.columns:
            raise ValueError("⚠️ Missing columns 'close'. Cannot compute MACD.")

    def get_macd(self, recent_n: int = 3) -> list[tuple[float, float, float]]:
        """
        Compute the MACD line, signal line, and histogram.

        Args:
            recent_n (int): Number of most recent values to return. Default is 3.

        Returns:
            list[tuple[float, float, float]]: A list of tuples (macd, signal, histogram).

        Raises:
            ValueError: If insufficient data is available to compute MACD.
        """
        if len(self.df) < self.slowperiod + recent_n:
            raise ValueError(
                f"⚠️ Insufficient data to calulate MACD. At least {self.slowperiod + recent_n} rows are needed."
            )

        macd, signal, hist = talib.MACD(
            self.df["close"].to_numpy(),
            fastperiod=self.fastperiod,
            slowperiod=self.slowperiod,
            signalperiod=self.signalperiod,
        )

        return [
            (round(float(m), 3), round(float(s), 3), round(float(h), 3))
            for m, s, h in zip(
                macd[-1 * recent_n :], signal[-1 * recent_n :], hist[-1 * recent_n :]
            )
        ]

    def is_macd_bullish(self) -> bool:
        """
        Check if a bullish MACD crossover occurred (histogram turns positive from negative).

        Returns:
            bool: True if a bullish crossover is detected, False otherwise.
        """
        try:
            macd_data = self.get_macd(recent_n=2)
            return macd_data[-2][-1] < 0 and macd_data[-1][-1] > 0
        except Exception as e:
            print(f"[MACD Error] Failed to detect bullish crossover: {e}")
            return False

    def is_macd_bearish(self) -> bool:
        """
        Check if a bearish MACD crossover occurred (histogram turns negative from positive).

        Returns:
            bool: True if a bearish crossover is detected, False otherwise.
        """
        try:
            macd_data = self.get_macd(recent_n=2)
            return macd_data[-2][-1] > 0 and macd_data[-1][-1] < 0
        except Exception as e:
            print(f"[MACD Error] Failed to detect bearish crossover: {e}")
            return False


if __name__ == "__main__":

    data = {
        "time": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "close": [100 + (i * 0.5) + (i % 5) * 2 for i in range(100)],
    }

    df = pd.DataFrame(data)
    macd_analyzer = MACD(df)

    try:
        macd_data = macd_analyzer.get_macd()
        is_bullish = macd_analyzer.is_macd_bullish()
        is_bearish = macd_analyzer.is_macd_bearish()
        print(f"MACD: {macd_data}")
        print("Recent MACD values (MACD, Signal, Histogram):")
        for m, s, h in macd_data:
            print(f"MACD: {m}, Signal: {s}, Histogram: {h}")

        print(f"Bullish Crossover: {is_bullish}")
        print(f"Bearish Crossover: {is_bearish}")
    except Exception as e:
        print(f"[Main Error] {e}")
