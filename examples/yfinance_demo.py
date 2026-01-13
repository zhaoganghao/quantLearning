"""
yfinance 使用示例脚本
演示如何使用 yfinance 获取和分析股票数据

国内使用说明：
- yfinance 在国内使用可能需要配置代理
- 请根据实际情况配置 PROXY 设置
- 如果无法访问，请参考 docs/yfinance_tutorial.md 中的"国内使用说明"
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 国内使用配置 ====================
# 如果在国内使用，请根据实际情况配置代理
# 方式 1: 直接设置代理（取消注释并修改为你的代理地址）
PROXY = None  # 示例: {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

# 方式 2: 使用环境变量（在终端设置或取消注释以下代码）
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 超时设置（秒）
TIMEOUT = 30

# 重试次数
RETRIES = 3
# ====================================================


def test_connection():
    """测试 yfinance 连接"""
    print("\n" + "="*60)
    print("测试 yfinance 连接")
    print("="*60)
    
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d", proxy=PROXY, timeout=TIMEOUT)
        
        if not hist.empty:
            print("✓ 连接成功！")
            print(f"下载了 {len(hist)} 条数据")
            print(f"数据日期范围: {hist.index[0].date()} 到 {hist.index[-1].date()}")
            return True
        else:
            print("✗ 连接失败：没有数据返回")
            return False
            
    except Exception as e:
        print(f"✗ 连接失败：{e}")
        print("\n可能的解决方案：")
        print("1. 检查网络连接")
        print("2. 配置代理（修改脚本中的 PROXY 设置）")
        print("3. 增加超时时间（修改 TIMEOUT 设置）")
        print("4. 参考 docs/yfinance_tutorial.md 中的'国内使用说明'")
        return False


def safe_download(ticker_symbol, period="1y"):
    """安全下载数据，支持重试"""
    for attempt in range(RETRIES):
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(
                period=period,
                proxy=PROXY,
                timeout=TIMEOUT
            )
            
            if not hist.empty:
                return hist
            else:
                print(f"✗ {ticker_symbol} 没有数据返回")
                return None
                
        except Exception as e:
            print(f"✗ 第 {attempt + 1} 次尝试下载 {ticker_symbol} 失败: {e}")
            if attempt < RETRIES - 1:
                import time
                time.sleep(2)  # 等待 2 秒后重试
    
    return None


def example_1_basic_data_download():
    """示例 1: 基础数据下载"""
    print("\n" + "="*60)
    print("示例 1: 基础数据下载")
    print("="*60)
    
    # 下载苹果公司(AAPL)过去一年的数据
    hist = safe_download("AAPL", period="1y")
    
    if hist is None:
        print("无法下载数据，请检查网络连接或代理配置")
        return None
    
    print(f"\n下载了 {len(hist)} 条数据")
    print("\n数据列:")
    print(hist.columns.tolist())
    
    print("\n前5条数据:")
    print(hist.head())
    
    print("\n数据统计信息:")
    print(hist.describe())
    
    return hist


def example_2_real_time_quotes():
    """示例 2: 获取实时报价"""
    print("\n" + "="*60)
    print("示例 2: 获取实时报价")
    print("="*60)
    
    try:
        ticker = yf.Ticker("AAPL")
        info = ticker.info
    except Exception as e:
        print(f"获取实时报价失败: {e}")
        return
    
    print(f"\n公司名称: {info.get('longName', 'N/A')}")
    print(f"当前价格: ${info.get('currentPrice', 'N/A')}")
    print(f"前收盘价: ${info.get('previousClose', 'N/A')}")
    print(f"开盘价: ${info.get('open', 'N/A')}")
    print(f"最高价: ${info.get('dayHigh', 'N/A')}")
    print(f"最低价: ${info.get('dayLow', 'N/A')}")
    print(f"成交量: {info.get('volume', 'N/A'):,}")
    print(f"市值: ${info.get('marketCap', 0):,.0f}")
    print(f"市盈率: {info.get('trailingPE', 'N/A')}")
    print(f"股息率: {info.get('dividendYield', 0)*100:.2f}%")


def example_3_multiple_stocks():
    """示例 3: 批量下载多只股票"""
    print("\n" + "="*60)
    print("示例 3: 批量下载多只股票")
    print("="*60)
    
    # 定义股票列表
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    # 下载多只股票数据
    try:
        data = yf.download(tickers, period="1y", proxy=PROXY, timeout=TIMEOUT)
    except Exception as e:
        print(f"批量下载失败: {e}")
        return None
    
    print(f"\n下载了 {len(tickers)} 只股票的数据")
    print("\n数据形状:", data.shape)
    
    # 获取收盘价
    close_prices = data['Close']
    print("\n收盘价数据:")
    print(close_prices.head())
    
    return data


def example_4_technical_indicators(hist):
    """示例 4: 技术指标计算"""
    print("\n" + "="*60)
    print("示例 4: 技术指标计算")
    print("="*60)
    
    # 计算收益率
    hist['Returns'] = hist['Close'].pct_change()
    
    # 计算移动平均线
    hist['MA20'] = hist['Close'].rolling(window=20).mean()
    hist['MA50'] = hist['Close'].rolling(window=50).mean()
    
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
    
    print("\n技术指标计算完成")
    print("\n最新数据:")
    print(hist[['Close', 'MA20', 'MA50', 'RSI', 'MACD', 'BB_Upper', 'BB_Lower']].tail())
    
    return hist


def example_5_visualization(hist):
    """示例 5: 数据可视化"""
    print("\n" + "="*60)
    print("示例 5: 数据可视化")
    print("="*60)
    
    # 创建图表目录
    os.makedirs('output', exist_ok=True)
    
    # 图表 1: 价格和移动平均线
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    ax1.plot(hist.index, hist['Close'], label='Close Price', linewidth=2)
    ax1.plot(hist.index, hist['MA20'], label='MA20', linewidth=1.5, alpha=0.8)
    ax1.plot(hist.index, hist['MA50'], label='MA50', linewidth=1.5, alpha=0.8)
    ax1.fill_between(hist.index, hist['BB_Upper'], hist['BB_Lower'], alpha=0.2, label='Bollinger Bands')
    ax1.set_title('AAPL Stock Price with Technical Indicators', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # 图表 2: RSI
    ax2.plot(hist.index, hist['RSI'], label='RSI', color='purple', linewidth=2)
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought (70)')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold (30)')
    ax2.set_title('Relative Strength Index (RSI)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('RSI', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 100])
    
    plt.tight_layout()
    plt.savefig('output/price_and_rsi.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存到: output/price_and_rsi.png")
    plt.close()
    
    # 图表 3: MACD
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(hist.index, hist['MACD'], label='MACD', linewidth=2)
    ax.plot(hist.index, hist['Signal'], label='Signal', linewidth=2)
    ax.bar(hist.index, hist['Histogram'], label='Histogram', alpha=0.3)
    ax.set_title('MACD Indicator', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('MACD', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/macd.png', dpi=300, bbox_inches='tight')
    print("图表已保存到: output/macd.png")
    plt.close()


def example_6_performance_analysis(hist):
    """示例 6: 性能分析"""
    print("\n" + "="*60)
    print("示例 6: 性能分析")
    print("="*60)
    
    # 计算收益率
    returns = hist['Returns'].dropna()
    
    # 计算统计指标
    mean_return = returns.mean()
    std_return = returns.std()
    
    annual_return = mean_return * 252
    annual_volatility = std_return * np.sqrt(252)
    sharpe_ratio = annual_return / annual_volatility
    
    # 计算最大回撤
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    max_drawdown_date = drawdown.idxmin()
    
    print(f"\n性能指标:")
    print(f"  平均日收益率: {mean_return*100:.4f}%")
    print(f"  日收益率标准差: {std_return*100:.4f}%")
    print(f"  年化收益率: {annual_return*100:.2f}%")
    print(f"  年化波动率: {annual_volatility*100:.2f}%")
    print(f"  夏普比率: {sharpe_ratio:.2f}")
    print(f"  最大回撤: {max_drawdown*100:.2f}%")
    print(f"  最大回撤日期: {max_drawdown_date.strftime('%Y-%m-%d')}")
    
    # 绘制回撤图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    ax1.plot(cumulative.index, cumulative.values, linewidth=2)
    ax1.set_title('Cumulative Returns', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cumulative Returns', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    ax2.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
    ax2.plot(drawdown.index, drawdown.values, color='red', linewidth=2)
    ax2.set_title('Drawdown', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Drawdown', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/drawdown.png', dpi=300, bbox_inches='tight')
    print("\n回撤图已保存到: output/drawdown.png")
    plt.close()


def example_7_portfolio_analysis():
    """示例 7: 投资组合分析"""
    print("\n" + "="*60)
    print("示例 7: 投资组合分析")
    print("="*60)
    
    # 定义投资组合
    portfolio = {
        'AAPL': 0.3,
        'GOOGL': 0.2,
        'MSFT': 0.2,
        'AMZN': 0.15,
        'TSLA': 0.15
    }
    
    print("\n投资组合权重:")
    for ticker, weight in portfolio.items():
        print(f"  {ticker}: {weight*100:.1f}%")
    
    # 下载数据
    tickers = list(portfolio.keys())
    try:
        data = yf.download(tickers, period="1y", proxy=PROXY, timeout=TIMEOUT)['Close']
    except Exception as e:
        print(f"下载投资组合数据失败: {e}")
        return
    
    # 计算收益率
    returns = data.pct_change().dropna()
    
    # 计算投资组合收益率
    portfolio_returns = returns.dot(pd.Series(portfolio))
    
    # 计算投资组合统计指标
    annual_return = portfolio_returns.mean() * 252
    annual_volatility = portfolio_returns.std() * np.sqrt(252)
    sharpe_ratio = annual_return / annual_volatility
    
    print(f"\n投资组合性能:")
    print(f"  年化收益率: {annual_return*100:.2f}%")
    print(f"  年化波动率: {annual_volatility*100:.2f}%")
    print(f"  夏普比率: {sharpe_ratio:.2f}")
    
    # 计算投资组合价值
    initial_investment = 10000
    portfolio_value = (1 + portfolio_returns).cumprod() * initial_investment
    
    print(f"\n投资价值:")
    print(f"  初始投资: ${initial_investment:,.2f}")
    print(f"  当前价值: ${portfolio_value.iloc[-1]:,.2f}")
    print(f"  总收益: ${portfolio_value.iloc[-1] - initial_investment:,.2f}")
    print(f"  收益率: {(portfolio_value.iloc[-1] / initial_investment - 1)*100:.2f}%")
    
    # 绘制投资组合表现
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(portfolio_value.index, portfolio_value.values, linewidth=2, label='Portfolio Value')
    ax.axhline(y=initial_investment, color='r', linestyle='--', alpha=0.5, label='Initial Investment')
    ax.set_title('Portfolio Performance', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value ($)', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/portfolio.png', dpi=300, bbox_inches='tight')
    print("\n投资组合图表已保存到: output/portfolio.png")
    plt.close()
    
    # 计算相关性矩阵
    correlation = returns.corr()
    print("\n股票相关性矩阵:")
    print(correlation.round(3))


def example_8_financial_statements():
    """示例 8: 获取财务报表"""
    print("\n" + "="*60)
    print("示例 8: 获取财务报表")
    print("="*60)
    
    try:
        ticker = yf.Ticker("AAPL")
        
        # 获取财务报表
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        cashflow = ticker.cashflow
    except Exception as e:
        print(f"获取财务报表失败: {e}")
        return
    
    print("\n利润表 (最近5年):")
    print(financials.head())
    
    print("\n资产负债表 (最近5年):")
    print(balance_sheet.head())
    
    print("\n现金流量表 (最近5年):")
    print(cashflow.head())


def example_9_dividends_and_splits():
    """示例 9: 分红和股票分割"""
    print("\n" + "="*60)
    print("示例 9: 分红和股票分割")
    print("="*60)
    
    try:
        ticker = yf.Ticker("AAPL")
        
        # 获取分红历史
        dividends = ticker.dividends
        print(f"\n分红历史 (共 {len(dividends)} 次):")
        print(dividends.tail(10))
        
        # 获取股票分割历史
        splits = ticker.splits
        print(f"\n股票分割历史 (共 {len(splits)} 次):")
        print(splits)
        
        # 计算总分红
        total_dividends = dividends.sum()
        print(f"\n总分红: ${total_dividends:.2f}")
    except Exception as e:
        print(f"获取分红和股票分割数据失败: {e}")


def example_10_comparison_analysis():
    """示例 10: 多股票比较分析"""
    print("\n" + "="*60)
    print("示例 10: 多股票比较分析")
    print("="*60)
    
    # 定义股票列表
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    # 下载数据
    try:
        data = yf.download(tickers, period="1y", proxy=PROXY, timeout=TIMEOUT)['Close']
    except Exception as e:
        print(f"下载比较分析数据失败: {e}")
        return
    
    # 计算收益率
    returns = data.pct_change()
    
    # 计算累计收益率
    cumulative_returns = (1 + returns).cumprod()
    
    # 计算每只股票的年化收益率和波动率
    print("\n股票性能比较:")
    print(f"{'股票':<10} {'年化收益率':<15} {'年化波动率':<15} {'夏普比率':<10}")
    print("-" * 55)
    
    for ticker in tickers:
        ticker_returns = returns[ticker].dropna()
        annual_return = ticker_returns.mean() * 252
        annual_volatility = ticker_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility
        
        print(f"{ticker:<10} {annual_return*100:>10.2f}% {annual_volatility*100:>10.2f}% {sharpe_ratio:>10.2f}")
    
    # 绘制累计收益率比较
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for ticker in tickers:
        ax.plot(cumulative_returns.index, cumulative_returns[ticker], 
                label=ticker, linewidth=2)
    
    ax.set_title('Cumulative Returns Comparison', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Returns', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/comparison.png', dpi=300, bbox_inches='tight')
    print("\n比较图表已保存到: output/comparison.png")
    plt.close()


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "="*60)
    print("yfinance 使用示例")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 首先测试连接
    if not test_connection():
        print("\n无法连接到 Yahoo Finance，请检查网络配置")
        print("参考 docs/yfinance_tutorial.md 中的'国内使用说明'")
        return
    
    try:
        # 运行示例
        hist = example_1_basic_data_download()
        if hist is None:
            print("基础数据下载失败，跳过后续示例")
            return
            
        example_2_real_time_quotes()
        data = example_3_multiple_stocks()
        if data is None:
            print("批量下载失败，跳过相关示例")
        else:
            hist = example_4_technical_indicators(hist)
            example_5_visualization(hist)
            example_6_performance_analysis(hist)
            example_7_portfolio_analysis()
            example_8_financial_statements()
            example_9_dividends_and_splits()
            example_10_comparison_analysis()
        
        print("\n" + "="*60)
        print("所有示例运行完成!")
        print("="*60)
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n生成的图表文件:")
        print("  - output/price_and_rsi.png")
        print("  - output/macd.png")
        print("  - output/drawdown.png")
        print("  - output/portfolio.png")
        print("  - output/comparison.png")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()