"""
Backtrader 使用示例脚本
演示如何使用 Backtrader 进行量化交易策略回测

功能包括：
- 基础回测
- 多种交易策略
- 参数优化
- 性能分析
- 可视化
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 配置参数 ====================
# 数据配置
TICKER = 'AAPL'
START_DATE = '2023-01-01'
END_DATE = '2024-01-01'

# 回测配置
INITIAL_CASH = 100000.0
COMMISSION = 0.001  # 0.1% 手续费

# 输出配置
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)
# =================================================


class YFinanceData(bt.feeds.PandasData):
    """自定义 yfinance 数据源"""
    params = (
        ('datetime', None),
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
        ('openinterest', None),
    )


def download_data(ticker, start_date, end_date):
    """下载股票数据"""
    print(f"\n下载 {ticker} 数据...")
    print(f"时间范围: {start_date} 到 {end_date}")
    
    try:
        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(start=start_date, end=end_date)
        
        if hist.empty:
            print(f"✗ 无法下载 {ticker} 的数据")
            return None
        
        print(f"✓ 成功下载 {len(hist)} 条数据")
        print(f"数据日期范围: {hist.index[0].date()} 到 {hist.index[-1].date()}")
        
        return hist
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return None


def example_1_basic_backtest(data):
    """示例 1: 基础回测"""
    print("\n" + "="*60)
    print("示例 1: 基础回测")
    print("="*60)
    
    class BasicStrategy(bt.Strategy):
        def __init__(self):
            self.dataclose = self.datas[0].close
        
        def next(self):
            # 简单的买入持有策略
            if not self.position:
                self.buy()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(BasicStrategy)
    
    # 添加数据
    cerebro.adddata(YFinanceData(dataname=data))
    
    # 设置初始资金
    cerebro.broker.setcash(INITIAL_CASH)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=COMMISSION)
    
    # 运行回测
    print(f'\n初始资金: ${cerebro.broker.getvalue():,.2f}')
    results = cerebro.run()
    print(f'最终资金: ${cerebro.broker.getvalue():,.2f}')
    print(f'收益率: {(cerebro.broker.getvalue() / INITIAL_CASH - 1) * 100:.2f}%')
    
    # 绘制结果
    cerebro.plot(style='candlestick', barup='red', bardown='green')
    plt.savefig(f'{OUTPUT_DIR}/example1_basic_backtest.png', dpi=300, bbox_inches='tight')
    print(f'\n图表已保存到: {OUTPUT_DIR}/example1_basic_backtest.png')
    plt.close()
    
    return cerebro


def example_2_double_sma(data):
    """示例 2: 双均线策略"""
    print("\n" + "="*60)
    print("示例 2: 双均线策略")
    print("="*60)
    
    class DoubleSMAStrategy(bt.Strategy):
        params = (
            ('fast_period', 10),
            ('slow_period', 30),
            ('printlog', False),
        )
        
        def __init__(self):
            self.fast_sma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
            self.slow_sma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
            self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
            self.order = None
        
        def notify_order(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                return
            
            if order.status in [order.Completed]:
                if order.isbuy():
                    if self.params.printlog:
                        print(f'买入执行, 价格: ${order.executed.price:.2f}')
                else:
                    if self.params.printlog:
                        print(f'卖出执行, 价格: ${order.executed.price:.2f}')
            
            self.order = None
        
        def next(self):
            if self.order:
                return
            
            if not self.position:
                if self.crossover > 0:  # 金叉
                    if self.params.printlog:
                        print(f'金叉买入信号, 价格: ${self.data.close[0]:.2f}')
                    self.order = self.buy()
            else:
                if self.crossover < 0:  # 死叉
                    if self.params.printlog:
                        print(f'死叉卖出信号, 价格: ${self.data.close[0]:.2f}')
                    self.order = self.sell()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(DoubleSMAStrategy, fast_period=10, slow_period=30, printlog=True)
    
    # 添加数据
    cerebro.adddata(YFinanceData(dataname=data))
    
    # 设置初始资金
    cerebro.broker.setcash(INITIAL_CASH)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=COMMISSION)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 运行回测
    print(f'\n初始资金: ${cerebro.broker.getvalue():,.2f}')
    results = cerebro.run()
    strat = results[0]
    print(f'最终资金: ${cerebro.broker.getvalue():,.2f}')
    print(f'收益率: {(cerebro.broker.getvalue() / INITIAL_CASH - 1) * 100:.2f}%')
    
    # 打印分析结果
    print('\n回测分析结果:')
    returns_analysis = strat.analyzers.returns.get_analysis()
    print(f'年化收益率: {returns_analysis.get("rnorm100", 0):.2f}%')
    
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    print(f'夏普比率: {sharpe_analysis.get("sharperatio", 0):.2f}')
    
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown_analysis.get("max", {}).get("drawdown", 0):.2f}%')
    
    trade_analysis = strat.analyzers.trades.get_analysis()
    total_trades = trade_analysis.get('total', {}).get('total', 0)
    won_trades = trade_analysis.get('won', {}).get('total', 0)
    print(f'总交易次数: {total_trades}')
    print(f'盈利交易次数: {won_trades}')
    print(f'胜率: {(won_trades / total_trades * 100) if total_trades > 0 else 0:.2f}%')
    
    # 绘制结果
    cerebro.plot(style='candlestick', barup='red', bardown='green')
    plt.savefig(f'{OUTPUT_DIR}/example2_double_sma.png', dpi=300, bbox_inches='tight')
    print(f'\n图表已保存到: {OUTPUT_DIR}/example2_double_sma.png')
    plt.close()
    
    return cerebro


def example_3_rsi_strategy(data):
    """示例 3: RSI 策略"""
    print("\n" + "="*60)
    print("示例 3: RSI 策略")
    print("="*60)
    
    class RSIStrategy(bt.Strategy):
        params = (
            ('rsi_period', 14),
            ('rsi_upper', 70),
            ('rsi_lower', 30),
        )
        
        def __init__(self):
            self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
            self.order = None
        
        def next(self):
            if self.order:
                return
            
            if not self.position:
                if self.rsi < self.params.rsi_lower:
                    print(f'RSI 超卖买入信号, RSI: {self.rsi[0]:.2f}')
                    self.order = self.buy()
            else:
                if self.rsi > self.params.rsi_upper:
                    print(f'RSI 超买卖出信号, RSI: {self.rsi[0]:.2f}')
                    self.order = self.sell()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(RSIStrategy)
    
    # 添加数据
    cerebro.adddata(YFinanceData(dataname=data))
    
    # 设置初始资金
    cerebro.broker.setcash(INITIAL_CASH)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=COMMISSION)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    # 运行回测
    print(f'\n初始资金: ${cerebro.broker.getvalue():,.2f}')
    results = cerebro.run()
    strat = results[0]
    print(f'最终资金: ${cerebro.broker.getvalue():,.2f}')
    print(f'收益率: {(cerebro.broker.getvalue() / INITIAL_CASH - 1) * 100:.2f}%')
    
    # 打印分析结果
    print('\n回测分析结果:')
    returns_analysis = strat.analyzers.returns.get_analysis()
    print(f'年化收益率: {returns_analysis.get("rnorm100", 0):.2f}%')
    
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    print(f'夏普比率: {sharpe_analysis.get("sharperatio", 0):.2f}')
    
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown_analysis.get("max", {}).get("drawdown", 0):.2f}%')
    
    # 绘制结果
    cerebro.plot(style='candlestick', barup='red', bardown='green')
    plt.savefig(f'{OUTPUT_DIR}/example3_rsi_strategy.png', dpi=300, bbox_inches='tight')
    print(f'\n图表已保存到: {OUTPUT_DIR}/example3_rsi_strategy.png')
    plt.close()
    
    return cerebro


def example_4_bollinger_bands(data):
    """示例 4: 布林带策略"""
    print("\n" + "="*60)
    print("示例 4: 布林带策略")
    print("="*60)
    
    class BollingerBandsStrategy(bt.Strategy):
        params = (
            ('period', 20),
            ('devfactor', 2),
        )
        
        def __init__(self):
            self.bollinger = bt.indicators.BollingerBands(
                self.data.close,
                period=self.params.period,
                devfactor=self.params.devfactor
            )
            self.order = None
        
        def next(self):
            if self.order:
                return
            
            if not self.position:
                if self.data.close < self.bollinger.lines.bot:
                    print(f'跌破下轨买入信号, 价格: ${self.data.close[0]:.2f}')
                    self.order = self.buy()
            else:
                if self.data.close > self.bollinger.lines.top:
                    print(f'突破上轨卖出信号, 价格: ${self.data.close[0]:.2f}')
                    self.order = self.sell()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(BollingerBandsStrategy)
    
    # 添加数据
    cerebro.adddata(YFinanceData(dataname=data))
    
    # 设置初始资金
    cerebro.broker.setcash(INITIAL_CASH)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=COMMISSION)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    # 运行回测
    print(f'\n初始资金: ${cerebro.broker.getvalue():,.2f}')
    results = cerebro.run()
    strat = results[0]
    print(f'最终资金: ${cerebro.broker.getvalue():,.2f}')
    print(f'收益率: {(cerebro.broker.getvalue() / INITIAL_CASH - 1) * 100:.2f}%')
    
    # 打印分析结果
    print('\n回测分析结果:')
    returns_analysis = strat.analyzers.returns.get_analysis()
    print(f'年化收益率: {returns_analysis.get("rnorm100", 0):.2f}%')
    
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    print(f'夏普比率: {sharpe_analysis.get("sharperatio", 0):.2f}')
    
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown_analysis.get("max", {}).get("drawdown", 0):.2f}%')
    
    # 绘制结果
    cerebro.plot(style='candlestick', barup='red', bardown='green')
    plt.savefig(f'{OUTPUT_DIR}/example4_bollinger_bands.png', dpi=300, bbox_inches='tight')
    print(f'\n图表已保存到: {OUTPUT_DIR}/example4_bollinger_bands.png')
    plt.close()
    
    return cerebro


def example_5_combined_strategy(data):
    """示例 5: 组合策略 (RSI + MACD)"""
    print("\n" + "="*60)
    print("示例 5: 组合策略 (RSI + MACD)")
    print("="*60)
    
    class CombinedStrategy(bt.Strategy):
        params = (
            ('rsi_period', 14),
            ('rsi_upper', 70),
            ('rsi_lower', 30),
            ('macd_fast', 12),
            ('macd_slow', 26),
            ('macd_signal', 9),
        )
        
        def __init__(self):
            self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
            self.macd = bt.indicators.MACD(
                self.data.close,
                period_me1=self.params.macd_fast,
                period_me2=self.params.macd_slow,
                period_signal=self.params.macd_signal
            )
            self.order = None
        
        def next(self):
            if self.order:
                return
            
            if not self.position:
                # 买入条件：RSI 超卖且 MACD 金叉
                if self.rsi < self.params.rsi_lower and self.macd.macd > self.macd.signal:
                    print(f'组合买入信号, RSI: {self.rsi[0]:.2f}, MACD: {self.macd.macd[0]:.2f}')
                    self.order = self.buy()
            else:
                # 卖出条件：RSI 超买或 MACD 死叉
                if self.rsi > self.params.rsi_upper or self.macd.macd < self.macd.signal:
                    print(f'组合卖出信号, RSI: {self.rsi[0]:.2f}, MACD: {self.macd.macd[0]:.2f}')
                    self.order = self.sell()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(CombinedStrategy)
    
    # 添加数据
    cerebro.adddata(YFinanceData(dataname=data))
    
    # 设置初始资金
    cerebro.broker.setcash(INITIAL_CASH)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=COMMISSION)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 运行回测
    print(f'\n初始资金: ${cerebro.broker.getvalue():,.2f}')
    results = cerebro.run()
    strat = results[0]
    print(f'最终资金: ${cerebro.broker.getvalue():,.2f}')
    print(f'收益率: {(cerebro.broker.getvalue() / INITIAL_CASH - 1) * 100:.2f}%')
    
    # 打印分析结果
    print('\n回测分析结果:')
    returns_analysis = strat.analyzers.returns.get_analysis()
    print(f'年化收益率: {returns_analysis.get("rnorm100", 0):.2f}%')
    
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    print(f'夏普比率: {sharpe_analysis.get("sharperatio", 0):.2f}')
    
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown_analysis.get("max", {}).get("drawdown", 0):.2f}%')
    
    trade_analysis = strat.analyzers.trades.get_analysis()
    total_trades = trade_analysis.get('total', {}).get('total', 0)
    won_trades = trade_analysis.get('won', {}).get('total', 0)
    print(f'总交易次数: {total_trades}')
    print(f'盈利交易次数: {won_trades}')
    print(f'胜率: {(won_trades / total_trades * 100) if total_trades > 0 else 0:.2f}%')
    
    # 绘制结果
    cerebro.plot(style='candlestick', barup='red', bardown='green')
    plt.savefig(f'{OUTPUT_DIR}/example5_combined_strategy.png', dpi=300, bbox_inches='tight')
    print(f'\n图表已保存到: {OUTPUT_DIR}/example5_combined_strategy.png')
    plt.close()
    
    return cerebro


def example_6_parameter_optimization(data):
    """示例 6: 参数优化"""
    print("\n" + "="*60)
    print("示例 6: 参数优化")
    print("="*60)
    
    class OptimizableStrategy(bt.Strategy):
        params = (
            ('fast_period', 10),
            ('slow_period', 30),
        )
        
        def __init__(self):
            self.fast_sma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
            self.slow_sma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
            self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
        
        def next(self):
            if not self.position:
                if self.crossover > 0:
                    self.buy()
            else:
                if self.crossover < 0:
                    self.sell()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    
    # 添加策略并设置参数范围
    cerebro.optstrategy(
        OptimizableStrategy,
        fast_period=range(5, 20, 5),
        slow_period=range(20, 50, 10)
    )
    
    # 添加数据
    cerebro.adddata(YFinanceData(dataname=data))
    
    # 设置初始资金
    cerebro.broker.setcash(INITIAL_CASH)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=COMMISSION)
    
    # 运行优化
    print('\n开始参数优化...')
    results = cerebro.run(maxcpu=4)
    
    # 分析结果
    print(f'\n共测试了 {len(results)} 种参数组合')
    print('\n最佳参数组合:')
    
    best_result = None
    best_value = 0
    
    for i, result in enumerate(results):
        final_value = result[0].broker.getvalue()
        if final_value > best_value:
            best_value = final_value
            best_result = result
    
    if best_result:
        strat = best_result[0]
        print(f'  快速均线周期: {strat.params.fast_period}')
        print(f'  慢速均线周期: {strat.params.slow_period}')
        print(f'  最终资金: ${best_value:,.2f}')
        print(f'  收益率: {(best_value / INITIAL_CASH - 1) * 100:.2f}%')
    
    return cerebro


def example_7_risk_management(data):
    """示例 7: 风险管理策略"""
    print("\n" + "="*60)
    print("示例 7: 风险管理策略")
    print("="*60)
    
    class RiskManagementStrategy(bt.Strategy):
        params = (
            ('risk_per_trade', 0.02),  # 每笔交易风险 2%
            ('atr_period', 14),
            ('atr_multiplier', 2),
        )
        
        def __init__(self):
            self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
            self.sma = bt.indicators.SMA(self.data.close, period=20)
            self.order = None
            self.entry_price = None
        
        def calculate_position_size(self):
            """基于 ATR 计算仓位大小"""
            cash = self.broker.getcash()
            price = self.data.close[0]
            atr_value = self.atr[0]
            
            # 计算止损距离
            stop_distance = atr_value * self.params.atr_multiplier
            
            # 计算风险金额
            risk_amount = cash * self.params.risk_per_trade
            
            # 计算仓位大小
            position_size = int(risk_amount / stop_distance)
            
            return position_size
        
        def next(self):
            if self.order:
                return
            
            if not self.position:
                if self.data.close > self.sma:
                    size = self.calculate_position_size()
                    if size > 0:
                        print(f'买入信号, 仓位大小: {size}, 价格: ${self.data.close[0]:.2f}')
                        self.order = self.buy(size=size)
                        self.entry_price = self.data.close[0]
            else:
                # 止损
                stop_loss_price = self.entry_price * (1 - self.params.atr_multiplier * self.atr[0] / self.entry_price)
                if self.data.close < stop_loss_price:
                    print(f'止损卖出, 价格: ${self.data.close[0]:.2f}')
                    self.order = self.sell()
                # 趋势反转
                elif self.data.close < self.sma:
                    print(f'趋势反转卖出, 价格: ${self.data.close[0]:.2f}')
                    self.order = self.sell()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(RiskManagementStrategy)
    
    # 添加数据
    cerebro.adddata(YFinanceData(dataname=data))
    
    # 设置初始资金
    cerebro.broker.setcash(INITIAL_CASH)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=COMMISSION)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    # 运行回测
    print(f'\n初始资金: ${cerebro.broker.getvalue():,.2f}')
    results = cerebro.run()
    strat = results[0]
    print(f'最终资金: ${cerebro.broker.getvalue():,.2f}')
    print(f'收益率: {(cerebro.broker.getvalue() / INITIAL_CASH - 1) * 100:.2f}%')
    
    # 打印分析结果
    print('\n回测分析结果:')
    returns_analysis = strat.analyzers.returns.get_analysis()
    print(f'年化收益率: {returns_analysis.get("rnorm100", 0):.2f}%')
    
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    print(f'夏普比率: {sharpe_analysis.get("sharperatio", 0):.2f}')
    
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    print(f'最大回撤: {drawdown_analysis.get("max", {}).get("drawdown", 0):.2f}%')
    
    # 绘制结果
    cerebro.plot(style='candlestick', barup='red', bardown='green')
    plt.savefig(f'{OUTPUT_DIR}/example7_risk_management.png', dpi=300, bbox_inches='tight')
    print(f'\n图表已保存到: {OUTPUT_DIR}/example7_risk_management.png')
    plt.close()
    
    return cerebro


def example_8_performance_comparison(data):
    """示例 8: 多策略性能比较"""
    print("\n" + "="*60)
    print("示例 8: 多策略性能比较")
    print("="*60)
    
    # 定义策略列表
    strategies = [
        ('双均线策略', DoubleSMAStrategy, {'fast_period': 10, 'slow_period': 30}),
        ('RSI 策略', RSIStrategy, {'rsi_period': 14, 'rsi_upper': 70, 'rsi_lower': 30}),
        ('布林带策略', BollingerBandsStrategy, {'period': 20, 'devfactor': 2}),
    ]
    
    results = []
    
    for name, strategy_class, params in strategies:
        print(f'\n测试策略: {name}')
        
        # 创建 Cerebro 引擎
        cerebro = bt.Cerebro()
        
        # 添加策略
        cerebro.addstrategy(strategy_class, **params)
        
        # 添加数据
        cerebro.adddata(YFinanceData(dataname=data))
        
        # 设置初始资金
        cerebro.broker.setcash(INITIAL_CASH)
        
        # 设置手续费
        cerebro.broker.setcommission(commission=COMMISSION)
        
        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        
        # 运行回测
        result = cerebro.run()
        strat = result[0]
        
        # 收集结果
        returns_analysis = strat.analyzers.returns.get_analysis()
        sharpe_analysis = strat.analyzers.sharpe.get_analysis()
        drawdown_analysis = strat.analyzers.drawdown.get_analysis()
        
        results.append({
            'name': name,
            'final_value': cerebro.broker.getvalue(),
            'return_pct': (cerebro.broker.getvalue() / INITIAL_CASH - 1) * 100,
            'annual_return': returns_analysis.get('rnorm100', 0),
            'sharpe_ratio': sharpe_analysis.get('sharperatio', 0),
            'max_drawdown': drawdown_analysis.get('max', {}).get('drawdown', 0),
        })
    
    # 打印比较结果
    print('\n' + '='*60)
    print('策略性能比较')
    print('='*60)
    print(f"{'策略名称':<15} {'最终资金':<15} {'收益率':<12} {'年化收益率':<12} {'夏普比率':<10} {'最大回撤':<10}")
    print('-' * 80)
    
    for result in results:
        print(f"{result['name']:<15} ${result['final_value']:>10,.2f} {result['return_pct']:>10.2f}% {result['annual_return']:>10.2f}% {result['sharpe_ratio']:>8.2f} {result['max_drawdown']:>8.2f}%")
    
    # 绘制比较图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    names = [r['name'] for r in results]
    returns = [r['return_pct'] for r in results]
    sharpe_ratios = [r['sharpe_ratio'] for r in results]
    
    x = np.arange(len(names))
    width = 0.35
    
    ax.bar(x - width/2, returns, width, label='收益率 (%)', alpha=0.8)
    ax.bar(x + width/2, sharpe_ratios, width, label='夏普比率', alpha=0.8)
    
    ax.set_xlabel('策略', fontsize=12)
    ax.set_ylabel('数值', fontsize=12)
    ax.set_title('策略性能比较', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/example8_performance_comparison.png', dpi=300, bbox_inches='tight')
    print(f'\n比较图表已保存到: {OUTPUT_DIR}/example8_performance_comparison.png')
    plt.close()
    
    return results


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "="*60)
    print("Backtrader 使用示例")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 下载数据
    data = download_data(TICKER, START_DATE, END_DATE)
    
    if data is None:
        print("\n无法下载数据，程序退出")
        return
    
    try:
        # 运行示例
        example_1_basic_backtest(data)
        example_2_double_sma(data)
        example_3_rsi_strategy(data)
        example_4_bollinger_bands(data)
        example_5_combined_strategy(data)
        example_6_parameter_optimization(data)
        example_7_risk_management(data)
        example_8_performance_comparison(data)
        
        print("\n" + "="*60)
        print("所有示例运行完成!")
        print("="*60)
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n生成的图表文件:")
        print(f"  - {OUTPUT_DIR}/example1_basic_backtest.png")
        print(f"  - {OUTPUT_DIR}/example2_double_sma.png")
        print(f"  - {OUTPUT_DIR}/example3_rsi_strategy.png")
        print(f"  - {OUTPUT_DIR}/example4_bollinger_bands.png")
        print(f"  - {OUTPUT_DIR}/example5_combined_strategy.png")
        print(f"  - {OUTPUT_DIR}/example7_risk_management.png")
        print(f"  - {OUTPUT_DIR}/example8_performance_comparison.png")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()