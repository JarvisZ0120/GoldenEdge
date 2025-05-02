import pandas as pd
import talib


class BollingerBands:
    """
    A wrapper class for calculating Bollinger Bands (BB) using TA-Lib.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        timeperiod: int = 20,
        nbdevup: float = 2,
        nbdevdn: float = 2,
        matype: int = 0,
    ) -> None:
        """
        Initialize the Bollinger Bands calculator.

        Args:
            df (pd.DataFrame): A DataFrame with a 'close' price column.
            timeperiod (int, optional): The number of periods for moving average. Default is 20.
            nbdevup (float, optional): Number of standard deviations above the MA. Default is 2.
            nbdevdn (float, optional): Number of standard deviations below the MA. Default is 2.
            matype (int, optional): Type of moving average (0=SMA). Default is 0.

        Raises:
            ValueError: If the required 'close' column is not found in the input DataFrame.
        """
        self.required_col = "close"
        self.df = df.copy()
        self.timeperiod = timeperiod
        self.nbdevup = nbdevup
        self.nbdevdn = nbdevdn
        self.matype = matype

        if self.required_col not in self.df.columns:
            raise ValueError(
                "⚠️ Missing column 'close'. Cannot compute Bollinger Bands."
            )

    def get_bbands(self) -> tuple:
        """
        Calculate and return the most recent Bollinger Bands (upper, middle, lower).

        Returns:
            tuple: (upper_band: float, middle_band: float, lower_band: float)
        
        Raises:
            ValueError: If the DataFrame does not contain enough data to compute BB.
        """
        if len(self.df) < self.timeperiod + 1:
            raise ValueError(
                f"⚠️ Insufficient data to calculate Bollinger Bands: At least {self.timeperiod + 1} rows are needed."
            )

        upper, middle, lower = talib.BBANDS(
            self.df["close"].to_numpy(),
            timeperiod=self.timeperiod,
            nbdevup=self.nbdevup,
            nbdevdn=self.nbdevdn,
            matype=self.matype,
        )

        return (round(upper[-1], 3), round(middle[-1], 3), round(lower[-1], 3))


# example use
if __name__ == "__main__":

    data = {
        "close": [
            1.12, 1.14, 1.18, 1.20, 1.19,
            1.22, 1.24, 1.26, 1.23, 1.28,
            1.26, 1.30, 1.12, 1.14, 1.18,
            1.12, 1.14, 1.18, 1.20, 1.19,
            1.22, 1.24, 1.26, 1.23, 1.28,
            1.26, 1.30, 1.12, 1.14, 1.18,
        ]
    }

    df = pd.DataFrame(data)
    bb_analyzer = BollingerBands(df)

    try:
        upper, middle, lower = bb_analyzer.get_bbands()
        print(f"Bollinger Bands:\nUpper: {upper}\nMiddle: {middle}\nLower: {lower}")
    except ValueError as e:
        print(f"[Main Error] {e}")
