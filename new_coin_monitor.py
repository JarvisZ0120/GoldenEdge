from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import *
import time
import logging
from datetime import datetime

# 设置API密钥
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'


# 生成带时间戳的日志文件名
date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"crypto_trading_{date_time_str}.log"

# 创建日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建文件处理器并设置编码
file_handler = logging.FileHandler(log_filename, mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 创建日志格式
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# 添加文件处理器到日志记录器
logger.addHandler(file_handler)

# 还可以添加控制台日志输出
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 记录一条日志测试
logger.info("Logging initialized successfully.")
print(f"日志系统已初始化，日志文件：{log_filename}")

# 交易对列表和 WebSocket 监听流
monitored_symbols = {}
streams = {}
latest_prices = {}  # 用于缓存每个 symbol 的最新成交价


usdt_free_balance = 0.0


def send_telegram_message(text):
    import requests
    BOT_TOKEN = 'YOUR_BOT_TOKEN'
    CHAT_ID = 'YOUR_CHAT_ID'
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': text, 'disable_notification': False }
    requests.post(url, data=payload)



def initialize_monitored_symbols():
    """初始化监听列表，添加所有 USDT 交易对"""
    global monitored_symbols
    monitored_symbols = {}

    try:
        exchange_info = client.get_exchange_info()

        for symbol_data in exchange_info['symbols']:
            symbol = symbol_data['symbol']
            if symbol.endswith('USDT'):  # 只添加 USDT 交易对

                monitored_symbols[symbol] = {'bought': False}
                print(f"已初始化 {symbol} 到监听列表中")
                logging.info(f"Initialized {symbol} into the monitoring list.")
        print(f"已初始化 {len(monitored_symbols)} 个 USDT 交易对")
        logging.info(f"Initialized {len(monitored_symbols)} USDT trading pairs.")
    except Exception as e:
        print(f"初始化交易对失败: {e}")
        logging.error(f"Failed to initialize trading pairs: {e}")


def calculate_buy_quantity(usdt_balance, market_price, symbol, fee_rate):
    """计算可购买的数量"""
    try:

        buy_qty = int(usdt_balance / (market_price * (1 + fee_rate)))  # 计算买入数量，保留6位小数

        print(f"计算手续费后得到的买入数量: {buy_qty} {symbol}")
        logger.info(f"Calculated Buy Quantity after commission: {buy_qty} {symbol}")
        return buy_qty
    except Exception as e:
        print(f"计算买入数量失败: {e}")
        logger.error(f"Failed to calculate buy quantity: {e}")
        return 0




# 获取市场价格 -- if handle_ticker_price_update() works fine, can be deleted 
def get_market_price(symbol):
    """获取市场当前价格"""
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        print(ticker)
        price = float(ticker['price'])
        print(f"{symbol} 当前市场价格: {price} USDT")
        logger.info(f"{symbol} Market Price: {price} USDT")
        return price
    except Exception as e:
        print(f"获取 {symbol} 价格失败: {e}")
        logger.error(f"Failed to get {symbol} price: {e}")
        return 0


def handle_ticker_price_update(msg):
    """接收 Binance WebSocket 推送的 24hrTicker 数据，更新价格缓存"""
    if isinstance(msg, list):  # 处理多条 ticker 推送
        for item in msg:
            if item.get('e') == '24hrTicker':
                symbol = item['s']
                price = float(item['c'])
                latest_prices[symbol] = price
    elif isinstance(msg, dict):  # 单条 ticker 推送
        if msg.get('e') == '24hrTicker':
            symbol = msg['s']
            price = float(msg['c'])
            latest_prices[symbol] = price


def handle_new_listing(msg):
    """处理新币上市信息"""
    global monitored_symbols, streams
    global usdt_free_balance

    # 兼容 msg 是单个 dict 或列表的情况
    if isinstance(msg, dict):
        msg = [msg]  # 如果是单个字典，转换成列表

    for ticker in msg:  # 遍历所有 ticker 数据
        if ticker.get('e') == '24hrTicker':
            symbol = ticker['s']
            
            # 只交易 USDT 交易对，且必须是新币
            if symbol.endswith('USDT') and symbol not in monitored_symbols:
                print(f"检测到新币上市: {symbol}")
                logging.info(f"New listing detected: {symbol}")

                monitored_symbols[symbol] = {'bought': False}
                try:
                    if usdt_free_balance < 10:
                        print("USDT 余额不足，无法交易")
                        logger.warning("Insufficient USDT balance for trading.")
                        return

                    market_price = latest_prices.get(symbol, 0)
                    print(f"{symbol} market Price is: {market_price}" )
                    logger.info(f"{symbol} market Price is: {market_price}" )
                    if market_price == 0:
                        market_price = get_market_price(symbol)  # 使用 REST API 获取一次
                        if market_price == 0:
                            print(f"⚠️ 无法获取 {symbol} 的实时价格，可能尚未推送")
                            logger.warning(f"Price for {symbol} not available in WebSocket cache")
                            return

                    fee_rate = 0  # 默认手续费为 0
                    
                    buy_qty = calculate_buy_quantity(usdt_free_balance*0.9, market_price, symbol, fee_rate)
                    if buy_qty == 0:
                        print(f"无法计算买入数量，取消交易")
                        logger.warning("Failed to calculate buy quantity, trade canceled.")
                        return
                    
                    start_time = time.time()  # 记录买入开始时间
                    buy_order = client.order_market_buy(symbol=symbol, quantity=buy_qty)
                    end_time = time.time()  # 记录买入结束时间
                    time_taken = round((end_time - start_time) * 1000, 2)  # 计算耗时（毫秒）
                    print(f"已买入 {symbol}, 订单信息: {buy_order}, 耗时 {time_taken} 毫秒")
                    logger.info(f"Bought {symbol}, Order details: {buy_order}, Time Taken: {time_taken} ms")

                    send_telegram_message(f"Bought {symbol}, Order details: {buy_order}, Time Taken: {time_taken} ms")

                    # 记录买入价格
                    last_trade = client.get_my_trades(symbol=symbol)[-1]
                    buy_price = float(last_trade['price'])
                    monitored_symbols[symbol] = {'bought': True, 'buy_price': buy_price}

                    print(f"✅ 成功记录 {symbol} 的买入价格: {buy_price} USDT" if last_trade else f"无法获取 {symbol} 的交易记录，可能尚未成交。")

                    # 监听价格更新
                    streams[symbol] = bsm.start_symbol_ticker_socket(
                        symbol=symbol,
                        callback=handle_price_update
                    )
                except Exception as e:
                    print(f"买入 {symbol} 失败: {e}")
                    logging.error(f"Failed to buy {symbol}: {e}")
                    send_telegram_message(f"Failed to buy {symbol}: {e}")





def adjust_to_step_size(symbol, quantity):
    from decimal import Decimal, ROUND_DOWN
    """Adjust quantity to match Binance LOT_SIZE rules."""
    info = client.get_symbol_info(symbol)
    if not info:
        raise ValueError(f"Symbol info not found for {symbol}")
    
    for f in info['filters']:
        if f['filterType'] == 'LOT_SIZE':
            step_size = float(f['stepSize'])
            if step_size == 0:
                raise ValueError(f"Invalid step_size 0 for {symbol}")
            precision = abs(Decimal(str(step_size)).as_tuple().exponent)
            adjusted_qty = int(Decimal(str(quantity)).quantize(Decimal('1e-{0}'.format(precision)), rounding=ROUND_DOWN))
            return adjusted_qty
    raise ValueError(f"LOT_SIZE filter not found for {symbol}")


def handle_price_update(msg):
    global monitored_symbols, streams

    symbol = msg['s']
    base_asset = symbol.replace('USDT', '')    
    current_price = float(msg['c'])

    def try_sell(reason):
        try:
            balance_info = client.get_asset_balance(asset=base_asset)
            raw_quantity = float(balance_info['free'])

            print(f"{symbol} 当前持仓数量为: {raw_quantity}")
            logging.info(f"{symbol} balance available for selling: {raw_quantity}")

            if raw_quantity == 0:
                print(f"{symbol} 当前无持仓，跳过卖出")
                logging.info(f"{symbol} no available balance to sell. Skipping.")
                return

            quantity = adjust_to_step_size(symbol, raw_quantity)
            print(f"可卖出ROUND_DOWN数量: {quantity}")
            logging.info(f"Available ROUND_DOWN quantity to sell is: {quantity}")

            if quantity == 0:
                print(f"{symbol} 可用数量不足最小交易单位，跳过")
                logging.info(f"{symbol} quantity too small after adjustment. Skipping.")
                return

            # 这里可以加一步：如果step_size是1，强制取整
            symbol_info = client.get_symbol_info(symbol)
            for f in symbol_info['filters']:
                if f['filterType'] == 'LOT_SIZE' and float(f['stepSize']) >= 1:
                    quantity = int(quantity)
                    print(f"强制整数处理后数量: {quantity}")
                    logging.info(f"Forced integer quantity: {quantity}")

            sell_order = client.order_market_sell(symbol=symbol, quantity=quantity)
            print(f"{reason} 已卖出 {symbol}, 卖出数量: {quantity}, 订单信息: {sell_order}")
            logging.info(f"{reason} sold {symbol}, quantity: {quantity}, order: {sell_order}")

            send_telegram_message(f"{reason} sold {symbol}, quantity: {quantity}, order: {sell_order}")

            bsm.stop_socket(streams[symbol])
            # del monitored_symbols[symbol]
            del streams[symbol]
            #break

        except Exception as e:
            print(f"{reason} 卖出 {symbol} 失败: {e}")
            logging.error(f"{reason} failed to sell {symbol}: {e}")

            send_telegram_message(f"{reason} failed to sell {symbol}: {e}")


    if symbol in monitored_symbols and monitored_symbols[symbol]['bought']:
        buy_price = monitored_symbols[symbol]['buy_price']
        target_price = buy_price * 1.24
        stop_loss_price = buy_price * 0.95

        print(
            f"{symbol} 当前价格: {current_price:.6f}，买入价: {buy_price:.6f}，"
            f"止盈价: {target_price:.6f}，止损价: {stop_loss_price:.6f}"
        )
        logging.info(
            f"{symbol} price check | current: {current_price:.6f} | "
            f"buy: {buy_price:.6f} | TP: {target_price:.6f} | SL: {stop_loss_price:.6f}"
        )

        if current_price >= target_price:
            try_sell("达到止盈目标")
        elif current_price <= stop_loss_price:
            try_sell("达到止损阈值")


# 获取账户信息
def get_account_info():
    """获取 Binance 账户信息和 USDT 余额"""
    global usdt_free_balance
    try:
        account_info = client.get_account()
        usdt_balance = client.get_asset_balance(asset='USDT')
        total_balance = float(usdt_balance['free']) + float(usdt_balance['locked'])
        
        print(f"账户信息获取成功，现货 USDT 可用余额: {usdt_balance['free']} USDT, 总余额: {total_balance} USDT")
        logger.info(f"Account info retrieved: USDT Free: {usdt_balance['free']}, Total: {total_balance}")

        usdt_free_balance = float(usdt_balance['free'])

        return float(usdt_balance['free'])
    except Exception as e:
        print(f"获取账户信息失败: {e}")
        logger.error(f"Failed to get account info: {e}")
        return 0

def reconnect():
    """ 处理 WebSocket 断开后的重连逻辑 """
    global bsm
    logging.warning("WebSocket 断开，尝试重连...")
    time.sleep(5)  # 避免频繁重连
    bsm.stop()
    
    # 重新初始化 WebSocket
    bsm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    bsm.start()
    bsm.start_ticker_socket(callback=handle_new_listing)
    logging.info("WebSocket 重新连接成功！")




def main():
    global client, bsm

    # 初始化客户端
    client = Client(api_key, api_secret)

    # 初始化WebSocket管理器
    bsm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    bsm.start()  # 先启动WebSocket

    # 初始化 USDT 交易对列表
    initialize_monitored_symbols()

    get_account_info()

    # 开始监听所有交易对的24小时价格
    # 启动两个 WebSocket，一个用于更新价格缓存，一个用于处理新币
    bsm.start_ticker_socket(callback=handle_ticker_price_update)   # 持续维护 latest_prices
    bsm.start_ticker_socket(callback=handle_new_listing)           # 检测新币

    # 事件循环
    while True:
        time.sleep(20)
        if not bsm.is_alive():
            reconnect()


if __name__ == "__main__":
    main()

