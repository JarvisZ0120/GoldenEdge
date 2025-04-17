import pandas as pd
import talib


class RSI:
    """
    A wrapper class to calculate the Relative Strength Index (RSI) and detect overbought/oversold conditions.

    """

    def __init__(self, df: pd.DataFrame, timeperiod: int = 14) -> None:
        """
        Initialize the RSI calculator.

        Args:
            df (pd.DataFrame): A DataFrame with 'close' price column.
            timeperiod (int, optional): Period length for RSI calculation. Default is 14.

        Raises:
            ValueError: If the required column is not found in the DataFrame.
        """
        self.df = df
        self.timeperiod = timeperiod

        if "close" not in df.columns:
            raise ValueError(
                "⚠️ Missing 'close' column in the DataFrame. Cannot compute RSI."
            )

    def get_rsi(self, recent_n: int = 3) -> list[float]:
        """
        Calculates the RSI value.

        Args:
            recent_n (int): Number of most recent values to return. Default is 3.

        Returns:
            list[float]: Last 3 RSI values as a list of floats, or False if data is insufficient.
         Raises:
            ValueError: If insufficient data is available to compute RSI.
        """
        if len(self.df) < self.timeperiod + recent_n:
            raise ValueError(
                f"⚠️ Insufficient data to calculate RSI: At least {self.timeperiod + recent_n} rows are needed."
            )

        rsi_array = talib.RSI(self.df["close"].to_numpy(), timeperiod=self.timeperiod)
        return list(round(float(val), 3) for val in rsi_array[-1 * recent_n :])

    def is_overbought(self, threshold: float = 70):
        """
        Checks if the latest RSI value is above the overbought threshold.

        Args:
            threshold (float): Overbought threshold, default is 70.

        Returns:
            bool: True if RSI is above the threshold.
        """
        rsi = self.get_rsi()
        return rsi and rsi[-1] > threshold

    def is_oversold(self, threshold: float = 30):
        """
        Checks if the latest RSI value is below the oversold threshold.

        Args:
            threshold (float): Oversold threshold, default is 30.

        Returns:
            bool: True if RSI is below the threshold.
        """
        rsi = self.get_rsi()
        return rsi and rsi[-1] < threshold


if __name__ == "__main__":

    close_prices = [
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
        1.13,
        1.12,
        1.15,
        1.17,
        1.18,
        1.16,
        1.19,
        1.18,
        1.20,
    ]

    df = pd.DataFrame({"close": close_prices})

    rsi_analyzer = RSI(df)
    rsi_values = rsi_analyzer.get_rsi()

    if rsi_values:
        print(f"Last 3 RSI values: {rsi_values}")

        if rsi_analyzer.is_overbought(65):
            print("Market is overbought!")

        if rsi_analyzer.is_oversold(35):
            print("Market is oversold!")
    else:
        print("Could not compute RSI due to insufficient data.")
