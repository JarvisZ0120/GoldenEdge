import pandas as pd
import talib


class ATR:
    """
    A wrapper class for calculating the Average True Range (ATR) using TA-Lib.

    """

    def __init__(self, df: pd.DataFrame, timeperiod: int = 14) -> None:
        """
        Initialize the ATR calculator.

        Args:
            df (pd.DataFrame): A DataFrame with 'high', 'low', and 'close' price columns.
            timeperiod (int, optional): Period length for ATR calculation. Default is 14.

        Raises:
            ValueError: If the required columns are not found in the DataFrame.
        """
        self.required_cols = ["high", "low", "close"]
        self.df = df.copy()
        self.timeperiod = timeperiod

        if not all(col in self.df.columns for col in self.required_cols):
            raise ValueError(
                "⚠️ Missing columns 'high', 'low', or 'close'. Cannot compute ATR."
            )

    def get_atr(self) -> float:
        """
        Calculate the most current ATR value.

        Returns:
            float: The current ATR value.

        Raises:
            ValueError: If the DataFrame does not contain enough data to compute ATR.
        """
        if len(self.df) < self.timeperiod + 1:
            raise ValueError(
                f"⚠️ Insufficient data to calculate ATR: At least {self.timeperiod + 1} rows are needed."
            )

        atr_array = talib.ATR(
            self.df["high"].to_numpy(),
            self.df["low"].to_numpy(),
            self.df["close"].to_numpy(),
            timeperiod=self.timeperiod,
        )

        return round(atr_array[-1], 3)


# example use
if __name__ == "__main__":

    data = {
        "high": [
            1.15,
            1.18,
            1.20,
            1.22,
            1.21,
            1.24,
            1.26,
            1.28,
            1.25,
            1.30,
            1.28,
            1.32,
            1.15,
            1.18,
            1.20,
        ],
        "low": [
            1.10,
            1.12,
            1.14,
            1.13,
            1.12,
            1.15,
            1.17,
            1.18,
            1.16,
            1.19,
            1.18,
            1.20,
            1.10,
            1.12,
            1.14,
        ],
        "close": [
            1.12,
            1.14,
            1.18,
            1.20,
            1.19,
            1.22,
            1.24,
            1.26,
            1.23,
            1.28,
            1.26,
            1.30,
            1.12,
            1.14,
            1.18,
        ],
    }

    df = pd.DataFrame(data)
    atr_analyzer = ATR(df)

    try:
        atr_values = atr_analyzer.get_atr()
        print(f"ATR: {atr_values}")
    except ValueError as e:
        print(f"[Main Error] {e}")
