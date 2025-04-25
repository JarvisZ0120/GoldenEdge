from indicators import atr, macd, rsi, adx
from metatrader import mt5_trader
from others import log_manager
import time
from datetime import datetime


def main():
    # configuration
    ACCOUNT = 5035257814
    PASSWORD = "!7XvJjRs"
    SERVER = "MetaQuotes-Demo"

    SYMBOL = "XAUUSD"
    TIMEFRAME = "M1"

    ADX_PERIOD = 14
    ADX_THRESHOLD = 40
    ATR_PERIOD = 14
    RSI_PERIOD = 14
    RSI_N = 3
    RSI_OVERBOUGHT_THRESHOLD = 65
    RSI_OVERSOLD_THRESHOLD = 35
    MACD_FASTPERIOD = 6
    MACD_SLOWPERIOD = 13
    MACD_SIGNALPERIOD = 5
    MACD_N = 3

    try:
        logger = log_manager.LogManager().get_logger()
        trader = mt5_trader.MT5Trader(logger)
        trader.connect(ACCOUNT, PASSWORD, SERVER)

        while True:
            df = trader.fetch_ohlcv(SYMBOL, TIMEFRAME)
            # print(df.tail())

            adx_analyzer = adx.ADX(df, ADX_PERIOD)
            adx_val = adx_analyzer.get_adx()

            atr_analyzer = atr.ATR(df, ATR_PERIOD)
            atr_val = atr_analyzer.get_atr()

            rsi_analyzer = rsi.RSI(df, RSI_PERIOD)
            rsi_list = rsi_analyzer.get_rsi(RSI_N)

            macd_analyzer = macd.MACD(
                df, MACD_FASTPERIOD, MACD_SLOWPERIOD, MACD_SIGNALPERIOD
            )
            macd_list = macd_analyzer.get_macd(MACD_N)

            print(f"DATETIME: {datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}")
            print(
                f"ADX: {adx_val} | MACD_HIST: {macd_list[-1][-1]} | RSI: {rsi_list[-1]} | ATR: {atr_val}"
            )
            logger.info(
                f"ADX: {adx_val} | MACD_HIST: {macd_list[-1][-1]} | RSI: {rsi_list[-1]} | ATR: {atr_val}"
            )

            if adx_val <= ADX_THRESHOLD:
                print("IT IS RANGE MARKET!")
                logger.info("It is in range market!")
                if (
                    rsi_analyzer.is_overbought(RSI_OVERBOUGHT_THRESHOLD)
                    and macd_analyzer.is_macd_bearish()
                ):
                    print(" ✅ SELL SIGNAL")
                    logger.info(" ✅ SELL SIGNAL")
                    trader.place_market_order("XAUUSD", "sell", 0.05, atr_val)
                    trader.place_market_order("XAUUSD", "sell", 0.05, atr_val)

                elif (
                    rsi_analyzer.is_oversold(RSI_OVERSOLD_THRESHOLD)
                    and macd_analyzer.is_macd_bullish()
                ):
                    print(" ✅ BUY SIGNAL")
                    logger.info(" ✅ BUY SIGNAL")
                    trader.place_market_order("XAUUSD", "buy", 0.05, atr_val)
                    trader.place_market_order("XAUUSD", "buy", 0.05, atr_val)

            time.sleep(30)

    except Exception as e:
        print(f"[Main Error] {e}")


if __name__ == "__main__":
    main()
