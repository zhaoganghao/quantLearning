# PyBroker 使用教程

## 目录
- [简介](#简介)
- [安装](#安装)
- [核心概念](#核心概念)
- [快速开始](#快速开始)
- [数据获取](#数据获取)
- [策略开发](#策略开发)
- [回测](#回测)
- [性能分析](#性能分析)
- [高级功能](#高级功能)
- [最佳实践](#最佳实践)

## 简介

PyBroker 是一个用于算法交易和回测的 Python 库，它提供了以下特性：

- **简单易用**：直观的 API 设计，快速上手
- **灵活的策略定义**：支持自定义交易策略
- **强大的回测引擎**：支持多种回测模式
- **丰富的技术指标**：内置常用技术分析指标
- **性能分析**：详细的回测结果和性能指标
- **数据支持**：支持多种数据源（yfinance、pandas DataFrame 等）

## 安装

```bash
pip install pybroker
```

或者使用 requirements.txt：

```bash
pip install -r requirements.txt
```

## 核心概念

### 1. 数据（Data）
PyBroker 使用 pandas DataFrame 作为数据格式，必须包含以下列：
- `date`：日期时间索引
- `open`：开盘价
- `high`：最高价
- `low`：最低价
- `close`：收盘价
- `volume`：成交量

### 2. 策略（Strategy）
策略是定义交易逻辑的核心组件，包含：
- 入场条件
- 出场条件
- 仓位管理
- 风险控制

### 3. 回测（Backtest）
回测引擎模拟策略在历史数据上的表现，生成：
- 交易记录
- 收益曲线
- 性能指标

### 4. 指标（Indicators）
技术分析指标用于辅助决策，如：
- 移动平均线（MA）
- 相对强弱指数（RSI）
- 布林带（Bollinger Bands）

## 快速开始

### 基础示例

```python
import pybroker
from pybroker import Strategy, YFinance

# 定义策略
def on_bar(data, state):
    # 简单的移动平均线策略
    if data['close'].mean(20) > data['close'].mean(50):
        state.buy_limit_price = data['close'][-1]
    elif data['close'].mean(20) < data['close'].mean(50):
        state.sell_limit_price = data['close'][-1]

# 创建策略
strategy = Strategy(
    initial_cash=100000,
    buy_delay=1,
    sell_delay=1
)

# 添加策略
strategy.add_execution(
    on_bar,
    symbols=['AAPL'],
    model_id='ma_crossover'
)

# 运行回测
result = strategy.backtest(
    YFinance(),
    start_date='2020-01-01',
    end_date='2023-12-31'
)

# 打印结果
print(result)
```

## 数据获取

### 使用 yfinance 获取数据

```python
from pybroker import YFinance

# 创建数据源
data_source = YFinance()

# 获取单只股票数据
df = data_source.fetch(
    symbols=['AAPL'],
    start_date='2020-01-01',
    end_date='2023-12-31'
)

print(df.head())
```

### 使用自定义数据

```python
import pandas as pd
from pybroker import DataSource

class CustomDataSource(DataSource):
    def fetch(self, symbols, start_date, end_date):
        # 从数据库或 API 获取数据
        data = {}
        for symbol in symbols:
            # 这里替换为你的数据获取逻辑
            df = pd.DataFrame({
                'date': pd.date_range(start_date, end_date),
                'open': [100] * len(pd.date_range(start_date, end_date)),
                'high': [105] * len(pd.date_range(start_date, end_date)),
                'low': [95] * len(pd.date_range(start_date, end_date)),
                'close': [100] * len(pd.date_range(start_date, end_date)),
                'volume': [1000000] * len(pd.date_range(start_date, end_date))
            })
            df.set_index('date', inplace=True)
            data[symbol] = df
        return data

# 使用自定义数据源
data_source = CustomDataSource()
```

## 策略开发

### 移动平均线交叉策略

```python
from pybroker import Strategy, YFinance

def ma_crossover_strategy(data, state):
    """移动平均线交叉策略"""
    # 计算 20 日和 50 日移动平均线
    ma20 = data['close'].mean(20)
    ma50 = data['close'].mean(50)
    
    # 金叉买入
    if ma20[-1] > ma50[-1] and ma20[-2] <= ma50[-2]:
        if not state.long_pos():
            state.buy_limit_price = data['close'][-1]
            state.buy_shares = 100
    
    # 死叉卖出
    elif ma20[-1] < ma50[-1] and ma20[-2] >= ma50[-2]:
        if state.long_pos():
            state.sell_limit_price = data['close'][-1]
            state.sell_shares = state.long_pos().shares

strategy = Strategy(initial_cash=100000)
strategy.add_execution(
    ma_crossover_strategy,
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    model_id='ma_crossover'
)
```

### RSI 策略

```python
import numpy as np

def calculate_rsi(prices, period=14):
    """计算 RSI 指标"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def rsi_strategy(data, state):
    """RSI 超买超卖策略"""
    rsi = calculate_rsi(data['close'])
    
    # RSI < 30 超卖，买入
    if rsi[-1] < 30 and not state.long_pos():
        state.buy_limit_price = data['close'][-1]
        state.buy_shares = 100
    
    # RSI > 70 超买，卖出
    elif rsi[-1] > 70 and state.long_pos():
        state.sell_limit_price = data['close'][-1]
        state.sell_shares = state.long_pos().shares

strategy = Strategy(initial_cash=100000)
strategy.add_execution(
    rsi_strategy,
    symbols=['AAPL'],
    model_id='rsi_strategy'
)
```

### 布林带策略

```python
def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """计算布林带"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band

def bollinger_bands_strategy(data, state):
    """布林带策略"""
    upper_band, middle_band, lower_band = calculate_bollinger_bands(data['close'])
    
    # 价格触及下轨，买入
    if data['close'][-1] <= lower_band[-1] and not state.long_pos():
        state.buy_limit_price = data['close'][-1]
        state.buy_shares = 100
    
    # 价格触及上轨，卖出
    elif data['close'][-1] >= upper_band[-1] and state.long_pos():
        state.sell_limit_price = data['close'][-1]
        state.sell_shares = state.long_pos().shares

strategy = Strategy(initial_cash=100000)
strategy.add_execution(
    bollinger_bands_strategy,
    symbols=['AAPL'],
    model_id='bollinger_bands'
)
```

## 回测

### 基本回测

```python
from pybroker import Strategy, YFinance

# 创建策略
strategy = Strategy(
    initial_cash=100000,  # 初始资金
    buy_delay=1,          # 买入延迟
    sell_delay=1          # 卖出延迟
)

# 添加策略执行
strategy.add_execution(
    ma_crossover_strategy,
    symbols=['AAPL'],
    model_id='ma_crossover'
)

# 运行回测
result = strategy.backtest(
    YFinance(),
    start_date='2020-01-01',
    end_date='2023-12-31'
)

# 查看结果
print(result)
```

### 多股票回测

```python
strategy = Strategy(initial_cash=100000)

# 添加多只股票
strategy.add_execution(
    ma_crossover_strategy,
    symbols=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
    model_id='ma_crossover'
)

result = strategy.backtest(
    YFinance(),
    start_date='2020-01-01',
    end_date='2023-12-31'
)
```

### 参数优化

```python
from pybroker import Strategy, YFinance

def ma_strategy(data, state, short_period, long_period):
    """带参数的移动平均线策略"""
    ma_short = data['close'].mean(short_period)
    ma_long = data['close'].mean(long_period)
    
    if ma_short[-1] > ma_long[-1] and ma_short[-2] <= ma_long[-2]:
        if not state.long_pos():
            state.buy_limit_price = data['close'][-1]
            state.buy_shares = 100
    elif ma_short[-1] < ma_long[-1] and ma_short[-2] >= ma_long[-2]:
        if state.long_pos():
            state.sell_limit_price = data['close'][-1]
            state.sell_shares = state.long_pos().shares

strategy = Strategy(initial_cash=100000)

# 添加不同参数的策略
strategy.add_execution(
    ma_strategy,
    symbols=['AAPL'],
    model_id='ma_5_20',
    short_period=5,
    long_period=20
)

strategy.add_execution(
    ma_strategy,
    symbols=['AAPL'],
    model_id='ma_10_30',
    short_period=10,
    long_period=30
)

result = strategy.backtest(
    YFinance(),
    start_date='2020-01-01',
    end_date='2023-12-31'
)
```

## 性能分析

### 查看回测结果

```python
# 打印详细结果
print(result)

# 获取交易记录
trades = result.trades
print(trades)

# 获取权益曲线
equity_curve = result.equity_curve
print(equity_curve)
```

### 性能指标

```python
# 计算收益率
returns = result.returns

# 计算夏普比率
sharpe_ratio = result.sharpe_ratio
print(f"夏普比率: {sharpe_ratio}")

# 计算最大回撤
max_drawdown = result.max_drawdown
print(f"最大回撤: {max_drawdown}")

# 计算胜率
win_rate = result.win_rate
print(f"胜率: {win_rate}")

# 计算总收益
total_return = result.total_return
print(f"总收益: {total_return}")
```

### 可视化

```python
import matplotlib.pyplot as plt

# 绘制权益曲线
plt.figure(figsize=(12, 6))
plt.plot(result.equity_curve.index, result.equity_curve.values)
plt.title('权益曲线')
plt.xlabel('日期')
plt.ylabel('权益')
plt.grid(True)
plt.show()

# 绘制收益分布
plt.figure(figsize=(12, 6))
plt.hist(result.returns, bins=50)
plt.title('收益分布')
plt.xlabel('收益率')
plt.ylabel('频数')
plt.grid(True)
plt.show()
```

## 高级功能

### 止损止盈

```python
def strategy_with_stop_loss(data, state):
    """带止损止盈的策略"""
    # 入场逻辑
    if data['close'].mean(20) > data['close'].mean(50):
        if not state.long_pos():
            state.buy_limit_price = data['close'][-1]
            state.buy_shares = 100
            # 设置止损和止盈
            state.stop_loss_pct = 0.05  # 5% 止损
            state.take_profit_pct = 0.10  # 10% 止盈
    
    # 出场逻辑
    elif data['close'].mean(20) < data['close'].mean(50):
        if state.long_pos():
            state.sell_limit_price = data['close'][-1]
            state.sell_shares = state.long_pos().shares

strategy = Strategy(initial_cash=100000)
strategy.add_execution(
    strategy_with_stop_loss,
    symbols=['AAPL'],
    model_id='stop_loss_strategy'
)
```

### 仓位管理

```python
def position_sizing_strategy(data, state):
    """仓位管理策略"""
    # 根据账户价值计算仓位大小
    account_value = state.account_value
    position_size = account_value * 0.1  # 每次使用 10% 的资金
    
    if data['close'].mean(20) > data['close'].mean(50):
        if not state.long_pos():
            state.buy_limit_price = data['close'][-1]
            # 计算可买入的股数
            shares = int(position_size / data['close'][-1])
            state.buy_shares = shares
    
    elif data['close'].mean(20) < data['close'].mean(50):
        if state.long_pos():
            state.sell_limit_price = data['close'][-1]
            state.sell_shares = state.long_pos().shares

strategy = Strategy(initial_cash=100000)
strategy.add_execution(
    position_sizing_strategy,
    symbols=['AAPL'],
    model_id='position_sizing'
)
```

### 多策略组合

```python
# 创建策略
strategy = Strategy(initial_cash=100000)

# 添加多个策略
strategy.add_execution(
    ma_crossover_strategy,
    symbols=['AAPL'],
    model_id='ma_crossover'
)

strategy.add_execution(
    rsi_strategy,
    symbols=['MSFT'],
    model_id='rsi_strategy'
)

strategy.add_execution(
    bollinger_bands_strategy,
    symbols=['GOOGL'],
    model_id='bollinger_bands'
)

# 运行回测
result = strategy.backtest(
    YFinance(),
    start_date='2020-01-01',
    end_date='2023-12-31'
)
```

## 最佳实践

### 1. 数据质量检查

```python
def check_data_quality(df):
    """检查数据质量"""
    # 检查缺失值
    if df.isnull().any().any():
        print("警告：数据中存在缺失值")
    
    # 检查数据范围
    if (df['high'] < df['low']).any():
        print("警告：最高价低于最低价")
    
    # 检查数据连续性
    date_diff = df.index.to_series().diff()
    if (date_diff > pd.Timedelta(days=7)).any():
        print("警告：数据存在较大间隔")
    
    return True
```

### 2. 策略测试

```python
def test_strategy(strategy_func, data):
    """测试策略逻辑"""
    # 模拟运行
    state = pybroker.State()
    
    for i in range(50, len(data)):
        window_data = data.iloc[i-50:i]
        strategy_func(window_data, state)
    
    print("策略测试完成")
```

### 3. 风险管理

```python
def risk_management_strategy(data, state):
    """风险管理策略"""
    # 最大持仓限制
    max_positions = 5
    if len(state.positions) >= max_positions:
        return
    
    # 单只股票最大仓位
    max_position_pct = 0.2
    if state.long_pos():
        position_value = state.long_pos().shares * data['close'][-1]
        if position_value > state.account_value * max_position_pct:
            return
    
    # 入场逻辑
    if data['close'].mean(20) > data['close'].mean(50):
        if not state.long_pos():
            state.buy_limit_price = data['close'][-1]
            state.buy_shares = 100
```

### 4. 日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pybroker')

def logged_strategy(data, state):
    """带日志记录的策略"""
    if data['close'].mean(20) > data['close'].mean(50):
        if not state.long_pos():
            logger.info(f"买入信号: {data.index[-1]}, 价格: {data['close'][-1]}")
            state.buy_limit_price = data['close'][-1]
            state.buy_shares = 100
```

### 5. 参数敏感性分析

```python
def analyze_parameter_sensitivity(strategy_func, symbols, start_date, end_date):
    """参数敏感性分析"""
    short_periods = [5, 10, 15, 20]
    long_periods = [20, 30, 40, 50]
    
    results = []
    for short in short_periods:
        for long in long_periods:
            strategy = Strategy(initial_cash=100000)
            strategy.add_execution(
                strategy_func,
                symbols=symbols,
                model_id=f'ma_{short}_{long}',
                short_period=short,
                long_period=long
            )
            
            result = strategy.backtest(
                YFinance(),
                start_date=start_date,
                end_date=end_date
            )
            
            results.append({
                'short_period': short,
                'long_period': long,
                'total_return': result.total_return,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown
            })
    
    return pd.DataFrame(results)
```

## 总结

PyBroker 是一个功能强大的量化交易回测框架，具有以下优势：

1. **简单易用**：直观的 API 设计
2. **灵活性强**：支持自定义策略和数据源
3. **性能优秀**：高效的回测引擎
4. **功能丰富**：内置多种技术指标和分析工具

通过本教程，您应该能够：
- 安装和配置 PyBroker
- 获取和处理交易数据
- 开发自定义交易策略
- 运行回测并分析结果
- 实现高级功能如止损止盈、仓位管理等

继续探索 PyBroker 的更多功能，构建您自己的量化交易系统！