from indicators import atr, macd, rsi, adx
from metatrader import mt5_trader
from others import log_manager
import time
from datetime import datetime


ACCOUNT = 5035257814
PASSWORD = "!7XvJjRs"
SERVER = "MetaQuotes-Demo"

SYMBOL = "XAUUSD"
TIMEFRAME = "M1"

ATR_PERIOD = 14
RSI_PERIOD = 14
RSI_N = 3
RSI_OVERBOUGHT_THRESHOLD = 65
RSI_OVERSOLD_THRESHOLD = 35

VOLUME = 0.05


def main():
    logger = log_manager.LogManager().get_logger()
    trader = mt5_trader.MT5Trader(logger)
    trader.connect(ACCOUNT, PASSWORD, SERVER)

    # position state：'long'、'short'、None
    position_state = None

    # previous RSI state：'overbought', 'oversold', 'normal'
    prev_rsi_state = "normal"

    try:
        while True:
            df = trader.fetch_ohlcv(SYMBOL, TIMEFRAME)

            # compute indicators
            atr_val = atr.ATR(df, ATR_PERIOD).get_atr()
            rsi_vals = rsi.RSI(df, RSI_PERIOD).get_rsi(RSI_N)
            curr_rsi = rsi_vals[-1]

            # update current RSI state
            if curr_rsi > RSI_OVERBOUGHT_THRESHOLD:
                curr_rsi_state = "overbought"
            elif curr_rsi < RSI_OVERSOLD_THRESHOLD:
                curr_rsi_state = "oversold"
            else:
                curr_rsi_state = "normal"

            # update position state
            if trader.get_positions() == 0:
                position_state = None

            print(
                f"[{datetime.now():%Y-%m-%d %H:%M:%S}] RSI={curr_rsi:.2f} RSI_STATE={curr_rsi_state}, POSITION_STATE={position_state}"
            )
            logger.info(
                f"RSI={curr_rsi:.2f} RSI_STATE={curr_rsi_state}, POSITION_STATE={position_state}"
            )

            # 1) overbought → normal, SELL
            if prev_rsi_state == "overbought" and curr_rsi_state == "normal":
                if position_state == "long":
                    # close BUY positions
                    trader.close_position(SYMBOL, "buy")
                    logger.info("Ready to SELL, close all BUY positions.")
                # start to SELL
                logger.info(" ✅ Start to SELL.")
                trader.place_market_order(SYMBOL, "sell", VOLUME, atr_val)
                position_state = "short"

            # 2) oversold → normal, BUY
            elif prev_rsi_state == "oversold" and curr_rsi_state == "normal":
                if position_state == "short":
                    # close SELL positions
                    trader.close_position(SYMBOL, "sell")
                    logger.info("Ready to BUY, Close all SELL positions.")
                # start to BUY
                logger.info(" ✅ Start to BUY.")
                trader.place_market_order(SYMBOL, "buy", VOLUME, atr_val)
                position_state = "long"

            # 3) normal → overbought/oversold, close all positions
            elif prev_rsi_state == "normal" and curr_rsi_state in (
                "overbought",
                "oversold",
            ):
                if position_state == "long":
                    trader.close_position(SYMBOL, "buy")
                    logger.info(" ⚠️ CLose positions (BUY).")
                elif position_state == "short":
                    trader.close_position(SYMBOL, "sell")
                    logger.info(" ⚠️ CLose positions (SELL).")
                position_state = None

            prev_rsi_state = curr_rsi_state
            time.sleep(10)

    except Exception as e:
        print(f"[Main Error] {e}")
        logger.error(f"[Main Error] {e}")


if __name__ == "__main__":
    main()
