import MetaTrader5 as mt5

class MT5Connection:
    def __init__(self, account, password, server):
        self.account = account
        self.password = password
        self.server = server
        self.connected = False

    def connect(self):
        """
        连接到 MetaTrader 5

        返回：
            boolean: True 如果登录上， 否则False 
        """
        if not mt5.initialize():
            print("⚠️ MT5 初始化失败！")
            quit()
            return False

        authorized = mt5.login(self.account, password=self.password, server=self.server)
        if not authorized:
            print("⚠️ MT5 登录失败！错误代码：", mt5.last_error())
            mt5.shutdown()
            quit()
            return False

        self.connected = True
        print("✅ MT5 连接成功！")
        return True

    def disconnect(self):
        """
        断开与 MetaTrader 5 的连接
        """
        mt5.shutdown()
        self.connected = False
        print("⚠️ MT5 断开连接！")

    def is_connected(self):
        """
        确认mt5已经连接

        返回：
            True 如果连接成功， 否则 False
        """ 
        return self.connected
    
    def get_mt5(self):
        return mt5

if __name__ == "__main__":
     # 配置登录信息
    account = 5033993521
    password = "G!I0FwJn"
    server = "MetaQuotes-Demo"

    # 创建 MT5 连接实例
    mt5_connection = MT5Connection(account, password, server)

    # 连接到 MT5
    mt5_connection.connect()
    print(f"已经连接：{mt5_connection.is_connected()}")
    # mt5_connection.disconnect()