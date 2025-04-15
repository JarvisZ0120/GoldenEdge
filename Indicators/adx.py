import pandas as pd
import talib


class ADX:
    def __init__(self, df: pd.DataFrame, timeperiod: int = 14) -> None:
        """
        Initialize the ADX class for calculating the Average Directional Index.

        Args:
            df (pd.DataFrame): A DataFrame that must contain 'high', 'low', and 'close' columns.
            timeperiod (int, optional): Period for calculating ADX. Default is 14.

        Raises:
            ValueError: If the required columns are missing in the input DataFrame.
        """
        required_cols = ["high", "low", "close"]
        if not all(col in df.columns for col in required_cols):
            raise ValueError(
                "⚠️ Missing columns 'high', 'low', or 'close'. Cannot compute ADX."
            )

        self.df = df
        self.timeperiod = timeperiod

    def get_adx(self) -> float | bool:
        """
        Calculate and return the most recent ADX value.

        Returns:
            float: The latest ADX value (rounded to 3 decimal places).
            bool: False if there is insufficient data to calculate ADX.
        """
        if len(self.df) < self.timeperiod + 1:
            print("⚠️ Not enough data to compute ADX.")
            return False

        adx_array = talib.ADX(
            self.df["high"].to_numpy(),
            self.df["low"].to_numpy(),
            self.df["close"].to_numpy(),
            timeperiod=self.timeperiod,
        )
        return round(adx_array[-1], 3)

    def is_range_market(self, threshold: float) -> bool:
        """
        Determine if the market is in a ranging (sideways) condition.

        Args:
            threshold (float): The ADX threshold below which the market is considered ranging.

        Returns:
            bool: True if ADX < threshold (ranging market), otherwise False.
        """
        adx = self.get_adx()
        return adx is not False and adx < threshold

    def is_trending_market(self, threshold: float) -> bool:
        """
        Determine if the market is in a trending condition.

        Args:
            threshold (float): The ADX threshold above which the market is considered trending.

        Returns:
            bool: True if ADX >= threshold (trending market), otherwise False.
        """
        adx = self.get_adx()
        return adx is not False and adx >= threshold


# example use
if __name__ == "__main__":

    data = {
        "high": [
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
        ],
        "low": [
            1.08,
            1.10,
            1.12,
            1.11,
            1.10,
            1.13,
            1.15,
            1.16,
            1.14,
            1.17,
            1.16,
            1.18,
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
            1.08,
            1.10,
            1.12,
            1.11,
            1.10,
            1.13,
            1.15,
            1.16,
            1.14,
            1.17,
            1.16,
            1.18,
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
            1.09,
            1.11,
            1.13,
            1.12,
            1.11,
            1.14,
            1.16,
            1.17,
            1.15,
            1.18,
            1.17,
            1.19,
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
        ],
        "close": [
            1.09,
            1.11,
            1.13,
            1.12,
            1.11,
            1.14,
            1.16,
            1.17,
            1.15,
            1.18,
            1.17,
            1.19,
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
            1.09,
            1.11,
            1.13,
            1.12,
            1.11,
            1.14,
            1.16,
            1.17,
            1.15,
            1.18,
            1.17,
            1.19,
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
            1.08,
            1.10,
            1.12,
            1.11,
            1.10,
            1.13,
            1.15,
            1.16,
            1.14,
            1.17,
            1.16,
            1.18,
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
        ],
    }
    df = pd.DataFrame(data)

    adx_instance = ADX(df)

    adx_value = adx_instance.get_adx()
    print(f"ADX: {adx_value}")

    if adx_instance.is_range_market(35):
        print("Market is in range.")
    else:
        print("Market is in trending.")
