# yfinance 使用教程

## 目录
1. [简介](#简介)
2. [安装](#安装)
3. [国内使用说明](#国内使用说明)
4. [基础用法](#基础用法)
5. [高级功能](#高级功能)
6. [实战示例](#实战示例)
7. [最佳实践](#最佳实践)
8. [常见问题](#常见问题)

## 简介

[yfinance](https://github.com/ranaroussi/yfinance) 是一个流行的 Python 库，用于从 Yahoo Finance 获取股票市场数据。它提供了简单易用的 API 来获取历史数据、实时报价、财务信息等。

### 主要特性
- 📊 获取历史股价数据（OHLCV）
- 💰 实时股票报价
- 📈 技术指标计算
- 🏢 公司财务信息
- 📰 新闻和公告
- 🔄 股票分割和分红信息

## 安装

### 使用 pip 安装
```bash
pip install yfinance
```

### 使用 conda 安装
```bash
conda install -c conda-forge yfinance
```

### 验证安装
```python
import yfinance as yf
print(yf.__version__)
```

## 基础用法

### 1. 获取历史数据

#### 下载单只股票数据
## 国内使用说明

### ⚠️ 重要提示

**yfinance 在国内使用时可能会遇到网络访问问题**，因为：
- Yahoo Finance 的服务器位于海外
- 国内网络环境可能限制访问
- 数据请求可能超时或失败

### 解决方案

#### 方案 1: 使用代理（推荐）

```python
import yfinance as yf

# 设置代理
proxies = {
    'http': 'http://your-proxy-server:port',
    'https': 'https://your-proxy-server:port'
}

# 使用代理下载数据
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y", proxy=proxies)
```

#### 方案 2: 使用环境变量

```bash
# 在终端设置代理
export HTTP_PROXY=http://your-proxy-server:port
export HTTPS_PROXY=https://your-proxy-server:port

# 然后运行 Python 脚本
python your_script.py
```

或在 Python 中设置：

```python
import os
import yfinance as yf

# 设置环境变量
os.environ['HTTP_PROXY'] = 'http://your-proxy-server:port'
os.environ['HTTPS_PROXY'] = 'https://your-proxy-server:port'

# 正常使用 yfinance
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")
```

#### 方案 3: 增加超时时间

```python
import yfinance as yf

# 增加超时时间（单位：秒）
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y", timeout=30)
```

#### 方案 4: 使用国内替代数据源

如果 yfinance 无法使用，可以考虑以下国内替代方案：

1. **Tushare** - 中国股票数据
   ```python
   import tushare as ts
   # 需要注册获取 token
   ts.set_token('your_token')
   pro = ts.pro_api()
   ```

2. **AkShare** - 开源财经数据接口
   ```python
   import akshare as ak
   # 支持国内外多种数据源
   stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily")
   ```

3. **Baostock** - 证券宝
   ```python
   import baostock as bs
   lg = bs.login()
   ```

### 测试连接

在使用 yfinance 之前，建议先测试连接：

```python
import yfinance as yf

def test_connection():
    """测试 yfinance 连接"""
    try:
        # 尝试下载少量数据
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d", timeout=10)
        
        if not hist.empty:
            print("✓ 连接成功！")
            print(f"下载了 {len(hist)} 条数据")
            return True
        else:
            print("✗ 连接失败：没有数据返回")
            return False
            
    except Exception as e:
        print(f"✗ 连接失败：{e}")
        return False

# 运行测试
if test_connection():
    print("可以正常使用 yfinance")
else:
    print("请检查网络连接或配置代理")
```

### 常见网络问题

#### 问题 1: 连接超时
```
ReadTimeoutError: HTTPSConnectionPool
```
**解决方案**：
- 增加超时时间
- 使用代理
- 检查网络连接

#### 问题 2: SSL 证书错误
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```
**解决方案**：
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

#### 问题 3: 403 Forbidden
```
HTTPError: 403 Client Error: Forbidden
```
**解决方案**：
- 更换代理服务器
- 等待一段时间后重试
- 使用不同的请求头

### 推荐的国内使用配置

```python
import yfinance as yf
import os
from datetime import datetime, timedelta

# 配置代理（根据实际情况修改）
PROXY = {
    'http': 'http://127.0.0.1:7890',  # 示例代理地址
    'https': 'http://127.0.0.1:7890'
}

# 或者设置环境变量
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

def download_data_safe(ticker_symbol, period="1y", retries=3):
    """安全下载数据，支持重试"""
    for attempt in range(retries):
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(
                period=period,
                proxy=PROXY,
                timeout=30
            )
            
            if not hist.empty:
                print(f"✓ 成功下载 {ticker_symbol} 数据")
                return hist
            else:
                print(f"✗ {ticker_symbol} 没有数据返回")
                return None
                
        except Exception as e:
            print(f"✗ 第 {attempt + 1} 次尝试失败: {e}")
            if attempt < retries - 1:
                import time
                time.sleep(2)  # 等待 2 秒后重试
    
    return None

# 使用示例
data = download_data_safe("AAPL", period="1y")
if data is not None:
    print(data.head())
```

### 注意事项

1. **代理稳定性**：确保代理服务器稳定可靠
2. **请求频率**：避免频繁请求，可能被限制
3. **数据时效性**：国内访问可能有延迟
4. **法律合规**：使用代理时请遵守相关法律法规
5. **数据备份**：建议缓存数据，避免重复下载

### 性能优化建议

```python
import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# 1. 使用缓存
CACHE_DIR = "yfinance_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cached_data(ticker, period="1y"):
    """带缓存的数据获取"""
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_{period}.csv")
    
    # 检查缓存是否存在且是今天的
    if os.path.exists(cache_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if file_time.date() == datetime.now().date():
            print(f"从缓存加载 {ticker}")
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
    
    # 下载新数据
    print(f"下载 {ticker} 数据")
    ticker_obj = yf.Ticker(ticker)
    hist = ticker_obj.history(period=period, proxy=PROXY, timeout=30)
    
    # 保存到缓存
    hist.to_csv(cache_file)
    
    return hist

# 2. 批量下载时添加延迟
import time

def batch_download_with_delay(tickers, delay=1):
    """批量下载，添加延迟避免被限制"""
    results = {}
    
    for i, ticker in enumerate(tickers):
        print(f"下载 {ticker} ({i+1}/{len(tickers)})")
        data = get_cached_data(ticker)
        
        if data is not None:
            results[ticker] = data
        
        # 添加延迟
        if i < len(tickers) - 1:
            time.sleep(delay)
    
    return results
```

```python
import yfinance as yf

# 下载苹果公司(AAPL)过去一年的数据
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

print(hist.head())
```

#### 支持的时间周期
- `period="1d"`: 1天
- `period="5d"`: 5天
- `period="1mo"`: 1个月
- `period="3mo"`: 3个月
- `period="6mo"`: 6个月
- `period="1y"`: 1年
- `period="2y"`: 2年
- `period="5y"`: 5年
- `period="10y"`: 10年
- `period="ytd"`: 年初至今
- `period="max"`: 最大可用数据

#### 指定日期范围
```python
import yfinance as yf
from datetime import datetime

# 指定开始和结束日期
start_date = "2023-01-01"
end_date = "2024-01-01"

ticker = yf.Ticker("AAPL")
hist = ticker.history(start=start_date, end=end_date)

print(hist)
```

#### 使用 datetime 对象
```python
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

hist = ticker.history(start=start_date, end=end_date)
```

### 2. 数据结构说明

历史数据包含以下列：
- `Open`: 开盘价
- `High`: 最高价
- `Low`: 最低价
- `Close`: 收盘价
- `Volume`: 成交量
- `Dividends`: 分红
- `Stock Splits`: 股票分割

```python
# 查看数据列
print(hist.columns)

# 查看数据类型
print(hist.dtypes)

# 查看统计信息
print(hist.describe())
```

### 3. 获取实时报价

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取最新价格
info = ticker.info
print(f"当前价格: ${info['currentPrice']}")
print(f"前收盘价: ${info['previousClose']}")
print(f"开盘价: ${info['open']}")
print(f"最高价: ${info['dayHigh']}")
print(f"最低价: ${info['dayLow']}")
print(f"成交量: {info['volume']}")
```

### 4. 批量下载多只股票

```python
import yfinance as yf

# 定义股票列表
tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

# 下载多只股票数据
data = yf.download(tickers, period="1y")

print(data.head())
```

#### 按股票访问数据
```python
# 获取所有股票的收盘价
close_prices = data['Close']
print(close_prices.head())

# 获取特定股票的数据
aapl_data = data['Close']['AAPL']
print(aapl_data.head())
```

## 高级功能

### 1. 获取公司信息

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取公司基本信息
info = ticker.info

print(f"公司名称: {info.get('longName', 'N/A')}")
print(f"行业: {info.get('industry', 'N/A')}")
print(f"板块: {info.get('sector', 'N/A')}")
print(f"市值: ${info.get('marketCap', 0):,.0f}")
print(f"市盈率: {info.get('trailingPE', 'N/A')}")
print(f"股息率: {info.get('dividendYield', 0)*100:.2f}%")
print(f"52周最高: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
print(f"52周最低: ${info.get('fiftyTwoWeekLow', 'N/A')}")
```

### 2. 获取财务报表

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取财务报表
financials = ticker.financials  # 利润表
balance_sheet = ticker.balance_sheet  # 资产负债表
cashflow = ticker.cashflow  # 现金流量表

print("利润表:")
print(financials.head())

print("\n资产负债表:")
print(balance_sheet.head())

print("\n现金流量表:")
print(cashflow.head())
```

### 3. 获取季度财务报表

```python
# 季度财务报表
quarterly_financials = ticker.quarterly_financials
quarterly_balance_sheet = ticker.quarterly_balance_sheet
quarterly_cashflow = ticker.quarterly_cashflow

print("季度利润表:")
print(quarterly_financials.head())
```

### 4. 获取分红和股票分割信息

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取分红历史
dividends = ticker.dividends
print("分红历史:")
print(dividends.tail())

# 获取股票分割历史
splits = ticker.splits
print("\n股票分割历史:")
print(splits.tail())

# 获取分红信息
actions = ticker.actions
print("\n所有行动:")
print(actions.tail())
```

### 5. 获取分析师推荐

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取分析师推荐
recommendations = ticker.recommendations
print("分析师推荐:")
print(recommendations.head())

# 获取目标价格
info = ticker.info
print(f"\n目标价格: ${info.get('targetMeanPrice', 'N/A')}")
print(f"最高目标价: ${info.get('targetHighPrice', 'N/A')}")
print(f"最低目标价: ${info.get('targetLowPrice', 'N/A')}")
```

### 6. 获取期权数据

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取期权到期日
expirations = ticker.options
print("可用的期权到期日:")
print(expirations)

# 获取特定到期日的期权链
if expirations:
    opt = ticker.option_chain(expirations[0])
    
    # 看涨期权
    calls = opt.calls
    print("\n看涨期权:")
    print(calls.head())
    
    # 看跌期权
    puts = opt.puts
    print("\n看跌期权:")
    print(puts.head())
```

### 7. 获取新闻

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取新闻
news = ticker.news
print("最新新闻:")
for item in news[:5]:  # 显示前5条新闻
    print(f"\n标题: {item['title']}")
    print(f"链接: {item['link']}")
    print(f"发布时间: {item['providerPublishTime']}")
```

### 8. 获取机构持股

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取主要机构持股
major_holders = ticker.major_holders
print("主要持股人:")
print(major_holders)

# 获取机构持股
institutional_holders = ticker.institutional_holders
print("\n机构持股:")
print(institutional_holders.head())
```

### 9. 获取可持续性信息

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取 ESG 评分
sustainability = ticker.sustainability
print("ESG 评分:")
print(sustainability)
```

## 实战示例

### 示例 1: 基本数据分析

```python
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 下载数据
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

# 计算收益率
hist['Returns'] = hist['Close'].pct_change()

# 计算移动平均线
hist['MA20'] = hist['Close'].rolling(window=20).mean()
hist['MA50'] = hist['Close'].rolling(window=50).mean()

# 绘制价格和移动平均线
plt.figure(figsize=(12, 6))
plt.plot(hist.index, hist['Close'], label='Close Price')
plt.plot(hist.index, hist['MA20'], label='MA20')
plt.plot(hist.index, hist['MA50'], label='MA50')
plt.title('AAPL Stock Price with Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.legend()
plt.grid(True)
plt.show()

# 计算统计指标
print(f"平均日收益率: {hist['Returns'].mean()*100:.2f}%")
print(f"年化收益率: {hist['Returns'].mean()*252*100:.2f}%")
print(f"年化波动率: {hist['Returns'].std()*252**0.5*100:.2f}%")
print(f"夏普比率: {hist['Returns'].mean()/hist['Returns'].std()*252**0.5:.2f}")
```

### 示例 2: 多股票比较分析

```python
import yfinance as yf
import matplotlib.pyplot as plt

# 定义股票列表
tickers = ["AAPL", "GOOGL", "MSFT", "AMZN"]

# 下载数据
data = yf.download(tickers, period="1y")['Close']

# 计算收益率
returns = data.pct_change()

# 计算累计收益率
cumulative_returns = (1 + returns).cumprod()

# 绘制累计收益率
plt.figure(figsize=(12, 6))
for ticker in tickers:
    plt.plot(cumulative_returns.index, cumulative_returns[ticker], label=ticker)

plt.title('Cumulative Returns Comparison')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.legend()
plt.grid(True)
plt.show()

# 计算相关性矩阵
correlation = returns.corr()
print("相关性矩阵:")
print(correlation)
```

### 示例 3: 技术指标计算

```python
import yfinance as yf
import pandas as pd
import numpy as np

# 下载数据
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

# RSI (相对强弱指标)
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

hist['RSI'] = calculate_rsi(hist['Close'])

# MACD (指数平滑异同移动平均线)
def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

hist['MACD'], hist['Signal'], hist['Histogram'] = calculate_macd(hist['Close'])

# 布林带
def calculate_bollinger_bands(prices, period=20, std_dev=2):
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band

hist['BB_Upper'], hist['BB_Middle'], hist['BB_Lower'] = calculate_bollinger_bands(hist['Close'])

print("技术指标计算完成:")
print(hist[['Close', 'RSI', 'MACD', 'Signal', 'BB_Upper', 'BB_Lower']].tail())
```

### 示例 4: 回撤分析

```python
import yfinance as yf
import matplotlib.pyplot as plt

# 下载数据
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="5y")

# 计算累计收益
cumulative = (1 + hist['Close'].pct_change()).cumprod()

# 计算回撤
running_max = cumulative.expanding().max()
drawdown = (cumulative - running_max) / running_max

# 找到最大回撤
max_drawdown = drawdown.min()
max_drawdown_date = drawdown.idxmin()

print(f"最大回撤: {max_drawdown*100:.2f}%")
print(f"最大回撤日期: {max_drawdown_date}")

# 绘制回撤图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# 累计收益
ax1.plot(cumulative.index, cumulative.values)
ax1.set_title('Cumulative Returns')
ax1.set_ylabel('Cumulative Returns')
ax1.grid(True)

# 回撤
ax2.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
ax2.plot(drawdown.index, drawdown.values, color='red')
ax2.set_title('Drawdown')
ax2.set_ylabel('Drawdown')
ax2.grid(True)

plt.tight_layout()
plt.show()
```

### 示例 5: 投资组合分析

```python
import yfinance as yf
import pandas as pd
import numpy as np

# 定义投资组合
portfolio = {
    'AAPL': 0.3,
    'GOOGL': 0.2,
    'MSFT': 0.2,
    'AMZN': 0.15,
    'TSLA': 0.15
}

# 下载数据
tickers = list(portfolio.keys())
data = yf.download(tickers, period="1y")['Close']

# 计算收益率
returns = data.pct_change().dropna()

# 计算投资组合收益率
portfolio_returns = returns.dot(pd.Series(portfolio))

# 计算投资组合统计指标
annual_return = portfolio_returns.mean() * 252
annual_volatility = portfolio_returns.std() * np.sqrt(252)
sharpe_ratio = annual_return / annual_volatility

print(f"年化收益率: {annual_return*100:.2f}%")
print(f"年化波动率: {annual_volatility*100:.2f}%")
print(f"夏普比率: {sharpe_ratio:.2f}")

# 计算投资组合价值
initial_investment = 10000
portfolio_value = (1 + portfolio_returns).cumprod() * initial_investment

print(f"\n初始投资: ${initial_investment:,.2f}")
print(f"当前价值: ${portfolio_value.iloc[-1]:,.2f}")
print(f"总收益: ${portfolio_value.iloc[-1] - initial_investment:,.2f}")
print(f"收益率: {(portfolio_value.iloc[-1] / initial_investment - 1)*100:.2f}%")
```

## 最佳实践

### 1. 错误处理

```python
import yfinance as yf
from datetime import datetime, timedelta

def safe_download(ticker_symbol, period="1y"):
    """安全下载股票数据"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            print(f"警告: {ticker_symbol} 没有数据")
            return None
            
        return hist
        
    except Exception as e:
        print(f"下载 {ticker_symbol} 数据时出错: {e}")
        return None

# 使用示例
data = safe_download("AAPL")
if data is not None:
    print(data.head())
```

### 2. 数据缓存

```python
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def get_cached_data(ticker_symbol, period="1y", cache_dir="cache"):
    """获取缓存的数据"""
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f"{ticker_symbol}_{period}.csv")
    
    # 检查缓存是否存在且是今天的
    if os.path.exists(cache_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if file_time.date() == datetime.now().date():
            print(f"从缓存加载 {ticker_symbol} 数据")
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
    
    # 下载新数据
    print(f"下载 {ticker_symbol} 数据")
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period)
    
    # 保存到缓存
    hist.to_csv(cache_file)
    
    return hist

# 使用示例
data = get_cached_data("AAPL")
print(data.head())
```

### 3. 批量处理

```python
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def download_ticker(ticker_symbol, period="1y"):
    """下载单只股票数据"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        return ticker_symbol, hist
    except Exception as e:
        print(f"下载 {ticker_symbol} 失败: {e}")
        return ticker_symbol, None

def batch_download(tickers, period="1y", max_workers=5):
    """批量下载股票数据"""
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_ticker, ticker, period) for ticker in tickers]
        
        for future in futures:
            ticker_symbol, data = future.result()
            if data is not None and not data.empty:
                results[ticker_symbol] = data
    
    return results

# 使用示例
tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"]
data_dict = batch_download(tickers)

print(f"成功下载 {len(data_dict)} 只股票的数据")
for ticker, data in data_dict.items():
    print(f"{ticker}: {len(data)} 条记录")
```

### 4. 数据验证

```python
import yfinance as yf
import pandas as pd

def validate_data(data):
    """验证数据质量"""
    issues = []
    
    # 检查空值
    if data.isnull().any().any():
        null_counts = data.isnull().sum()
        issues.append(f"发现空值: {null_counts[null_counts > 0].to_dict()}")
    
    # 检查负价格
    if (data[['Open', 'High', 'Low', 'Close']] < 0).any().any():
        issues.append("发现负价格")
    
    # 检查价格逻辑
    invalid_prices = (data['High'] < data['Low']) | \
                     (data['Close'] > data['High']) | \
                     (data['Close'] < data['Low'])
    if invalid_prices.any():
        issues.append(f"发现 {invalid_prices.sum()} 条无效价格记录")
    
    # 检查成交量
    if (data['Volume'] < 0).any():
        issues.append("发现负成交量")
    
    return issues

# 使用示例
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

issues = validate_data(hist)
if issues:
    print("数据验证发现问题:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("数据验证通过")
```

## 常见问题

### Q1: yfinance 数据准确吗？
A: yfinance 从 Yahoo Finance 获取数据，数据质量总体可靠，但建议：
- 对于重要决策，交叉验证多个数据源
- 注意数据可能存在延迟
- 检查异常值和缺失值

### Q2: 如何处理数据缺失？
A: 可以使用以下方法：
```python
# 前向填充
data = data.fillna(method='ffill')

# 后向填充
data = data.fillna(method='bfill')

# 删除缺失值
data = data.dropna()

# 插值
data = data.interpolate()
```

### Q3: 如何获取实时数据？
A: yfinance 提供接近实时的数据，但有延迟：
```python
ticker = yf.Ticker("AAPL")
info = ticker.info
print(f"当前价格: ${info.get('currentPrice', 'N/A')}")
```

### Q4: 支持哪些市场？
A: yfinance 支持全球主要市场：
- 美股: AAPL, GOOGL, MSFT
- 港股: 0700.HK (腾讯), 9988.HK (阿里巴巴)
- A股: 600519.SS (贵州茅台), 000858.SZ (五粮液)
- 加密货币: BTC-USD, ETH-USD

### Q5: 如何避免 API 限制？
A: 建议：
- 使用缓存机制
- 批量下载时添加延迟
- 合理设置请求频率
- 使用多线程但控制并发数

### Q6: 数据更新频率如何？
A: 
- 历史数据: 通常每日更新
- 实时报价: 有15-20分钟延迟
- 财务数据: 季度更新

## 总结

yfinance 是一个强大而易用的金融数据获取工具，适合：
- 📊 数据分析和研究
- 💼 投资组合管理
- 📈 技术分析
- 🎓 学习和教学

通过本教程，你应该能够：
1. 安装和配置 yfinance
2. 获取各种类型的金融数据
3. 进行基本的数据分析
4. 实现常见的技术指标
5. 构建投资组合分析

## 参考资源

- [yfinance GitHub 仓库](https://github.com/ranaroussi/yfinance)
- [yfinance 官方文档](https://pypi.org/project/yfinance/)
- [Yahoo Finance](https://finance.yahoo.com/)
- [Pandas 文档](https://pandas.pydata.org/docs/)
- [Matplotlib 文档](https://matplotlib.org/stable/contents.html)