# GoldenEdge
# 黄金 & 加密货币自动交易系统 (EA)

## 📌 项目简介
本项目是一个基于 **MetaTrader (MT4/MT5)** 和 **加密货币交易所 API** 的自动交易系统 (Expert Advisor, EA)，支持多种交易策略，包括趋势跟随、震荡突破和网格交易，适用于 **黄金（XAU/USD）** 和主要 **加密货币（BTC, ETH等）** 的自动化交易。

## 🚀 功能特性
- **📈 多策略支持**  
  - **海龟交易法则**（趋势跟随）  
  - **均线突破**（EMA/SMA 突破信号）  
  - **震荡区间突破**（布林带 + RSI）  
  - **网格交易策略**（Grid Trading）  
  - **马丁格尔加仓策略**（Martingale）  
  - **智能止损 & 移动止盈**  
- **🛠 兼容多个交易平台**  
  - **MT4 / MT5**（MetaTrader 自动交易）  
  - **加密货币交易所 API（Binance, OKX, Bybit等）**  
- **⚡ 高效订单执行**  
  - 支持 **挂单交易**、**市价交易** 和 **自定义交易规则**  
  - 低延迟订单执行，确保最佳交易价格  
- **📊 交易数据可视化**  
  - 实时交易统计与盈亏分析  
  - 支持交易日志记录，方便回测和优化  

## 🏗 技术栈
- **Python / MQL4 / MQL5**（EA 开发 & 交易策略实现）
- **NumPy / Pandas / Scikit-learn**（数据分析 & 策略优化）
- **Binance API / Bybit API**（加密货币交易所 API）
- **MetaTrader 4 / 5**（黄金 & 外汇交易）

## 🔧 系统要求
- **Windows 10/11 或 Linux（支持 MT4/MT5 终端）**
- **Python 3.8+**
- **MetaTrader 4 / 5 交易账户**
- **加密货币交易所 API Key（如 Binance, Bybit, OKX）**

## 🔄 安装与使用
### 1️⃣ **安装依赖**
```bash
pip install numpy pandas requests ta binance
```

### 2️⃣ **配置交易账户**
- **MT4/MT5 账户**  
  - 将 EA 代码复制到 `MetaTrader/MQL4/Experts/` 或 `MQL5/Experts/`
  - 启动 MetaTrader 并在 **EA 设置** 中启用自动交易

- **加密货币 API 配置**  
  - 在 `config.json` 中输入 API Key：
    ```json
    {
      "exchange": "binance",
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET"
    }
    ```

### 3️⃣ **运行 EA**
- 在 MetaTrader 终端加载 EA，选择策略并启用自动交易  
- 在 Python 运行加密货币交易脚本：
  ```bash
  python trade_bot.py
  ```

## 📈 策略优化与回测
- **MT4/MT5** 提供内置日志文件，可调整参数优化交易策略 

## 文件名格式
- ** {指标}_{策略}_{timeframe}.py **  


## ⚠️ 风险提示
- **交易存在风险**，请勿投入超出承受范围的资金  
- **建议使用模拟账户进行测试**，确认策略稳定性后再实盘交易  

## 📮 联系我们
💬 **社区讨论:** [Discord Group]

