import time
import MetaTrader5 as mt5
import pandas as pd
import talib
import logging
from datetime import datetime

# Generate a timestamp for the log filename
log_filename = "atr_ma_dynamic_sl_tp_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename,
    filemode='a'
)

# === Connect to MT4 ===
def connect_mt4():
    if not mt5.initialize():
        print("⚠️ MT4 connection failed!")
        logging.error("MT4 connection failed!")
        quit()
        return False
    
    # account = 5033700150  # Your account number
    # authorized = mt5.login(account, password="!8AzJiDa", server="MetaQuotes-Demo")

    account = 5034140779 
    authorized = mt5.login(account, password="OlEvQ-B4", server="MetaQuotes-Demo")
    if not authorized:
        error_info = mt5.last_error()
        print(f"Login failed, error code: {error_info}")
        logging.error(f"Login failed, error code: {error_info}")
        mt5.shutdown()
        quit()
        return False

    print("✅ MT4 connected successfully!")
    logging.info("MT4 connected successfully!")
    return True

import MetaTrader5 as mt5
import pandas as pd
import talib
import numpy as np

# === Get Smoothed ATR Value ===
def get_atr(symbol="XAUUSD", period=14, timeframe=mt5.TIMEFRAME_M1, clip_ratio=1.5, smoothing=True):
    # Retrieve a larger window of data to ensure sufficient data for ATR calculation
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period + 14)  
    if rates is None:
        print("Failed to retrieve market data.")
        logging.warning("Failed to retrieve market data.")
        return None
    
    # Convert the data to a DataFrame
    df = pd.DataFrame(rates)
    
    # Calculate the standard ATR using TALIB
    raw_atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
    
    # Limit excessive ATR spikes if smoothing is enabled
    if smoothing:
        # Forward fill missing values to prevent NaN affecting calculations
        raw_atr_filled = raw_atr.ffill()  # Or use fillna(0) depending on your preference
        # Calculate the median of the filled ATR values
        median_atr = raw_atr_filled.rolling(window=period).median()  
        # Limit extreme ATR values using a clip ratio
        clipped_atr = np.minimum(raw_atr_filled, median_atr * clip_ratio)  
    else:
        clipped_atr = raw_atr

    # Return the last value of the clipped ATR
    return clipped_atr.iloc[-1]



# === Determine Market Trend ===
def get_trend(symbol="XAUUSD", ma_period=50, timeframe=mt5.TIMEFRAME_M1):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, ma_period + 1)
    if rates is None:
        print("Failed to retrieve trend data.")
        logging.warning("Failed to retrieve trend data.")
        return None
    df = pd.DataFrame(rates)
    df["SMA"] = talib.SMA(df["close"], timeperiod=ma_period)
    latest_price = df["close"].iloc[-1]
    latest_ma = df["SMA"].iloc[-1]

    if latest_price > latest_ma:
        return "up"  # Uptrend
    elif latest_price < latest_ma:
        return "down"  # Downtrend
    else:
        return "sideways"  # Sideways market

# === Adjust SL/TP with Trailing Stop and Extreme Condition Filtering ===
def update_orders(symbol="XAUUSD", atr_multiplier_trend=3, atr_multiplier_sideways=1.5, trailing_stop_multiplier=1.5):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None or len(positions) == 0:
        print(f"No open positions for {symbol}.")
        logging.info(f"No open positions for {symbol}.")
        return
    
    atr = get_atr(symbol)
    print(f"ATR for {symbol}: {atr}")
    logging.info(f"ATR for {symbol}: {atr}")
    
    trend = get_trend(symbol)
    print(f"Market trend for {symbol}: {trend}")
    logging.info(f"Market trend for {symbol}: {trend}")

    if atr is None or trend is None:
        return
    
    atr_multiplier = atr_multiplier_trend if trend in ["up", "down"] else atr_multiplier_sideways

    for pos in positions:
        order_id = pos.ticket
        price = pos.price_open
        current_price = mt5.symbol_info_tick(symbol).bid if pos.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
        is_buy = pos.type == mt5.ORDER_TYPE_BUY
        stop_loss = price - atr * atr_multiplier if is_buy else price + atr * atr_multiplier
        take_profit = price + atr * atr_multiplier if is_buy else price - atr * atr_multiplier
        
        # Apply Trailing Stop
        if is_buy and current_price - stop_loss > atr * trailing_stop_multiplier:
            stop_loss = current_price - atr * trailing_stop_multiplier
        elif not is_buy and stop_loss - current_price > atr * trailing_stop_multiplier:
            stop_loss = current_price + atr * trailing_stop_multiplier
        
        # Avoid extreme SL/TP changes
        if abs(take_profit - price) > 5 * atr:
            take_profit = price + (5 * atr) if is_buy else price - (5 * atr)
        if abs(stop_loss - price) > 5 * atr:
            stop_loss = price - (5 * atr) if is_buy else price + (5 * atr)

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": order_id,
            "sl": round(stop_loss, 2),
            "tp": round(take_profit, 2),
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order {order_id} update failed: {result.comment}")
            logging.error(f"Order {order_id} update failed: {result.comment}")
        else:
            print(f"Order {order_id} stop loss and take profit updated successfully.")
            logging.info(f"Order {order_id} stop loss and take profit updated successfully.")

# === Main Execution Loop ===
def main(interval=30):
    if not connect_mt4():
        return
    
    try:
        while True:
            update_orders()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Process terminated by user.")
        logging.info("Process terminated by user.")
    finally:
        mt5.shutdown()
        print("MT4 connection closed.")
        logging.info("MT4 connection closed.")

if __name__ == "__main__":
    main(30)
