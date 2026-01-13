"""
PyBroker 量化交易回测示例

本示例展示了如何使用 PyBroker 进行量化交易策略回测，包括：
1. 移动平均线交叉策略
2. RSI 策略
3. 布林带策略
4. 止损止盈策略
5. 多策略组合
6. 性能分析和可视化
"""

import pybroker
from pybroker import Strategy, YFinance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 1. 移动平均线交叉策略
# ============================================================================

def ma_crossover_strategy(data, state, short_period=20, long_period=50):
    """
    移动平均线交叉策略
    
    参数:
        data: 历史数据
        state: 策略状态
        short_period: 短期移动平均线周期
        long_period: 长期移动平均线周期
    """
    # 计算移动平均线
    ma_short = data['close'].mean(short_period)
    ma_long = data['close'].mean(long_period)
    
    # 金叉买入
    if ma_short[-1] > ma_long[-1] and ma_short[-2] <= ma_long[-2]:
        if not state.long_pos():
            state.buy_limit_price = data['close'][-1]
            state.buy_shares = 100
            print(f"买入信号: {data.index[-1].date()}, 价格: {data['close'][-1]:.2f}")
    
    # 死叉卖出
    elif ma_short[-1] < ma_long[-1] and ma_short[-2] >= ma_long[-2]:
        if state.long_pos():
            state.sell_limit_price = data['close'][-1]
            state.sell_shares = state.long_pos().shares
            print(f"卖出信号: {data.index[-1].date()}, 价格: {data['close'][-1]:.2f}")


# ============================================================================
# 2. RSI 策略
# ============================================================================

def calculate_rsi(prices, period=14):
    """计算 RSI 指标"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def rsi_strategy(data, state, rsi_period=14, oversold=30, overbought=70):
    """
    RSI 超买超卖策略
    
    参数:
        data: 历史数据
        state: 策略状态
        rsi_period: RSI 周期
        oversold: 超卖阈值
        overbought: 超买阈值
    """
    rsi = calculate_rsi(data['close'], rsi_period)
    
    # RSI < 30 超卖，买入
    if rsi[-1] < oversold and not state.long_pos():
        state.buy_limit_price = data['close'][-1]
        state.buy_shares = 100
        print(f"RSI买入信号: {data.index[-1].date()}, RSI: {rsi[-1]:.2f}, 价格: {data['close'][-1]:.2f}")
    
    # RSI > 70 超买，卖出
    elif rsi[-1] > overbought and state.long_pos():
        state.sell_limit_price = data['close'][-1]
        state.sell_shares = state.long_pos().shares
        print(f"RSI卖出信号: {data.index[-1].date()}, RSI: {rsi[-1]:.2f}, 价格: {data['close'][-1]:.2f}")


# ============================================================================
# 3. 布林带策略
# ============================================================================

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """计算布林带"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band


def bollinger_bands_strategy(data, state, period=20, std_dev=2):
    """
    布林带策略
    
    参数:
        data: 历史数据
        state: 策略状态
        period: 布林带周期
        std_dev: 标准差倍数
    """
    upper_band, middle_band, lower_band = calculate_bollinger_bands(
        data['close'], period, std_dev
    )
    
    # 价格触及下轨，买入
    if data['close'][-1] <= lower_band[-1] and not state.long_pos():
        state.buy_limit_price = data['close'][-1]
        state.buy_shares = 100
        print(f"布林带买入信号: {data.index[-1].date()}, 价格: {data['close'][-1]:.2f}")
    
    # 价格触及上轨，卖出
    elif data['close'][-1] >= upper_band[-1] and state.long_pos():
        state.sell_limit_price = data['close'][-1]
        state.sell_shares = state.long_pos().shares
        print(f"布林带卖出信号: {data.index[-1].date()}, 价格: {data['close'][-1]:.2f}")


# ============================================================================
# 4. 止损止盈策略
# ============================================================================

def stop_loss_strategy(data, state, short_period=20, long_period=50, 
                       stop_loss_pct=0.05, take_profit_pct=0.10):
    """
    带止损止盈的移动平均线策略
    
    参数:
        data: 历史数据
        state: 策略状态
        short_period: 短期移动平均线周期
        long_period: 长期移动平均线周期
        stop_loss_pct: 止损百分比
        take_profit_pct: 止盈百分比
    """
    ma_short = data['close'].mean(short_period)
    ma_long = data['close'].mean(long_period)
    
    # 金叉买入
    if ma_short[-1] > ma_long[-1] and ma_short[-2] <= ma_long[-2]:
        if not state.long_pos():
            state.buy_limit_price = data['close'][-1]
            state.buy_shares = 100
            state.stop_loss_pct = stop_loss_pct
            state.take_profit_pct = take_profit_pct
            print(f"买入信号: {data.index[-1].date()}, 价格: {data['close'][-1]:.2f}, "
                  f"止损: {stop_loss_pct*100}%, 止盈: {take_profit_pct*100}%")
    
    # 死叉卖出
    elif ma_short[-1] < ma_long[-1] and ma_short[-2] >= ma_long[-2]:
        if state.long_pos():
            state.sell_limit_price = data['close'][-1]
            state.sell_shares = state.long_pos().shares
            print(f"卖出信号: {data.index[-1].date()}, 价格: {data['close'][-1]:.2f}")


# ============================================================================
# 5. 仓位管理策略
# ============================================================================

def position_sizing_strategy(data, state, short_period=20, long_period=50, 
                            position_pct=0.1):
    """
    仓位管理策略
    
    参数:
        data: 历史数据
        state: 策略状态
        short_period: 短期移动平均线周期
        long_period: 长期移动平均线周期
        position_pct: 每次使用的资金比例
    """
    ma_short = data['close'].mean(short_period)
    ma_long = data['close'].mean(long_period)
    
    # 根据账户价值计算仓位大小
    account_value = state.account_value
    position_size = account_value * position_pct
    
    # 金叉买入
    if ma_short[-1] > ma_long[-1] and ma_short[-2] <= ma_long[-2]:
        if not state.long_pos():
            state.buy_limit_price = data['close'][-1]
            # 计算可买入的股数
            shares = int(position_size / data['close'][-1])
            state.buy_shares = shares
            print(f"买入信号: {data.index[-1].date()}, 价格: {data['close'][-1]:.2f}, "
                  f"股数: {shares}, 仓位: {position_pct*100}%")
    
    # 死叉卖出
    elif ma_short[-1] < ma_long[-1] and ma_short[-2] >= ma_long[-2]:
        if state.long_pos():
            state.sell_limit_price = data['close'][-1]
            state.sell_shares = state.long_pos().shares
            print(f"卖出信号: {data.index[-1].date()}, 价格: {data['close'][-1]:.2f}")


# ============================================================================
# 6. 性能分析和可视化
# ============================================================================

def analyze_performance(result, strategy_name):
    """分析回测性能"""
    print("\n" + "="*80)
    print(f"{strategy_name} - 回测结果")
    print("="*80)
    
    # 基本指标
    print(f"\n初始资金: ${result.initial_cash:,.2f}")
    print(f"最终资金: ${result.equity_curve.iloc[-1]:,.2f}")
    print(f"总收益: {result.total_return*100:.2f}%")
    print(f"年化收益: {result.annual_return*100:.2f}%")
    print(f"夏普比率: {result.sharpe_ratio:.2f}")
    print(f"最大回撤: {result.max_drawdown*100:.2f}%")
    print(f"胜率: {result.win_rate*100:.2f}%")
    
    # 交易统计
    print(f"\n交易次数: {len(result.trades)}")
    print(f"盈利交易: {result.win_trades}")
    print(f"亏损交易: {result.loss_trades}")
    
    if len(result.trades) > 0:
        avg_profit = result.trades[result.trades['pnl'] > 0]['pnl'].mean()
        avg_loss = result.trades[result.trades['pnl'] < 0]['pnl'].mean()
        print(f"平均盈利: ${avg_profit:,.2f}")
        print(f"平均亏损: ${avg_loss:,.2f}")
        print(f"盈亏比: {abs(avg_profit/avg_loss):.2f}")


def plot_equity_curve(result, strategy_name):
    """绘制权益曲线"""
    plt.figure(figsize=(12, 6))
    plt.plot(result.equity_curve.index, result.equity_curve.values, 
             linewidth=2, label='权益曲线')
    plt.title(f'{strategy_name} - 权益曲线', fontsize=14, fontweight='bold')
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('权益 ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(f'pybroker_{strategy_name}_equity.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_returns_distribution(result, strategy_name):
    """绘制收益分布"""
    plt.figure(figsize=(12, 6))
    plt.hist(result.returns, bins=50, edgecolor='black', alpha=0.7)
    plt.title(f'{strategy_name} - 收益分布', fontsize=14, fontweight='bold')
    plt.xlabel('收益率', fontsize=12)
    plt.ylabel('频数', fontsize=12)
    plt.axvline(result.returns.mean(), color='red', linestyle='--', 
                label=f'平均收益: {result.returns.mean()*100:.2f}%')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(f'pybroker_{strategy_name}_returns.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_drawdown(result, strategy_name):
    """绘制回撤曲线"""
    equity = result.equity_curve
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max
    
    plt.figure(figsize=(12, 6))
    plt.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
    plt.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
    plt.title(f'{strategy_name} - 回撤曲线', fontsize=14, fontweight='bold')
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('回撤 (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'pybroker_{strategy_name}_drawdown.png', dpi=300, bbox_inches='tight')
    plt.show()


# ============================================================================
# 7. 主函数 - 运行所有策略
# ============================================================================

def run_ma_crossover_backtest():
    """运行移动平均线交叉策略回测"""
    print("\n" + "="*80)
    print("运行移动平均线交叉策略回测")
    print("="*80)
    
    strategy = Strategy(
        initial_cash=100000,
        buy_delay=1,
        sell_delay=1
    )
    
    strategy.add_execution(
        ma_crossover_strategy,
        symbols=['AAPL'],
        model_id='ma_crossover',
        short_period=20,
        long_period=50
    )
    
    result = strategy.backtest(
        YFinance(),
        start_date='2020-01-01',
        end_date='2023-12-31'
    )
    
    analyze_performance(result, "移动平均线交叉策略")
    plot_equity_curve(result, "移动平均线交叉策略")
    plot_returns_distribution(result, "移动平均线交叉策略")
    plot_drawdown(result, "移动平均线交叉策略")
    
    return result


def run_rsi_backtest():
    """运行 RSI 策略回测"""
    print("\n" + "="*80)
    print("运行 RSI 策略回测")
    print("="*80)
    
    strategy = Strategy(
        initial_cash=100000,
        buy_delay=1,
        sell_delay=1
    )
    
    strategy.add_execution(
        rsi_strategy,
        symbols=['AAPL'],
        model_id='rsi_strategy',
        rsi_period=14,
        oversold=30,
        overbought=70
    )
    
    result = strategy.backtest(
        YFinance(),
        start_date='2020-01-01',
        end_date='2023-12-31'
    )
    
    analyze_performance(result, "RSI策略")
    plot_equity_curve(result, "RSI策略")
    plot_returns_distribution(result, "RSI策略")
    plot_drawdown(result, "RSI策略")
    
    return result


def run_bollinger_bands_backtest():
    """运行布林带策略回测"""
    print("\n" + "="*80)
    print("运行布林带策略回测")
    print("="*80)
    
    strategy = Strategy(
        initial_cash=100000,
        buy_delay=1,
        sell_delay=1
    )
    
    strategy.add_execution(
        bollinger_bands_strategy,
        symbols=['AAPL'],
        model_id='bollinger_bands',
        period=20,
        std_dev=2
    )
    
    result = strategy.backtest(
        YFinance(),
        start_date='2020-01-01',
        end_date='2023-12-31'
    )
    
    analyze_performance(result, "布林带策略")
    plot_equity_curve(result, "布林带策略")
    plot_returns_distribution(result, "布林带策略")
    plot_drawdown(result, "布林带策略")
    
    return result


def run_stop_loss_backtest():
    """运行止损止盈策略回测"""
    print("\n" + "="*80)
    print("运行止损止盈策略回测")
    print("="*80)
    
    strategy = Strategy(
        initial_cash=100000,
        buy_delay=1,
        sell_delay=1
    )
    
    strategy.add_execution(
        stop_loss_strategy,
        symbols=['AAPL'],
        model_id='stop_loss',
        short_period=20,
        long_period=50,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )
    
    result = strategy.backtest(
        YFinance(),
        start_date='2020-01-01',
        end_date='2023-12-31'
    )
    
    analyze_performance(result, "止损止盈策略")
    plot_equity_curve(result, "止损止盈策略")
    plot_returns_distribution(result, "止损止盈策略")
    plot_drawdown(result, "止损止盈策略")
    
    return result


def run_position_sizing_backtest():
    """运行仓位管理策略回测"""
    print("\n" + "="*80)
    print("运行仓位管理策略回测")
    print("="*80)
    
    strategy = Strategy(
        initial_cash=100000,
        buy_delay=1,
        sell_delay=1
    )
    
    strategy.add_execution(
        position_sizing_strategy,
        symbols=['AAPL'],
        model_id='position_sizing',
        short_period=20,
        long_period=50,
        position_pct=0.1
    )
    
    result = strategy.backtest(
        YFinance(),
        start_date='2020-01-01',
        end_date='2023-12-31'
    )
    
    analyze_performance(result, "仓位管理策略")
    plot_equity_curve(result, "仓位管理策略")
    plot_returns_distribution(result, "仓位管理策略")
    plot_drawdown(result, "仓位管理策略")
    
    return result


def run_multi_strategy_backtest():
    """运行多策略组合回测"""
    print("\n" + "="*80)
    print("运行多策略组合回测")
    print("="*80)
    
    strategy = Strategy(
        initial_cash=100000,
        buy_delay=1,
        sell_delay=1
    )
    
    # 添加多个策略
    strategy.add_execution(
        ma_crossover_strategy,
        symbols=['AAPL'],
        model_id='ma_crossover',
        short_period=20,
        long_period=50
    )
    
    strategy.add_execution(
        rsi_strategy,
        symbols=['MSFT'],
        model_id='rsi_strategy',
        rsi_period=14,
        oversold=30,
        overbought=70
    )
    
    strategy.add_execution(
        bollinger_bands_strategy,
        symbols=['GOOGL'],
        model_id='bollinger_bands',
        period=20,
        std_dev=2
    )
    
    result = strategy.backtest(
        YFinance(),
        start_date='2020-01-01',
        end_date='2023-12-31'
    )
    
    analyze_performance(result, "多策略组合")
    plot_equity_curve(result, "多策略组合")
    plot_returns_distribution(result, "多策略组合")
    plot_drawdown(result, "多策略组合")
    
    return result


def compare_strategies():
    """比较不同策略的性能"""
    print("\n" + "="*80)
    print("策略性能比较")
    print("="*80)
    
    # 运行所有策略
    ma_result = run_ma_crossover_backtest()
    rsi_result = run_rsi_backtest()
    bb_result = run_bollinger_bands_backtest()
    sl_result = run_stop_loss_backtest()
    ps_result = run_position_sizing_backtest()
    
    # 创建比较表格
    comparison_data = {
        '策略': ['移动平均线', 'RSI', '布林带', '止损止盈', '仓位管理'],
        '总收益(%)': [
            ma_result.total_return * 100,
            rsi_result.total_return * 100,
            bb_result.total_return * 100,
            sl_result.total_return * 100,
            ps_result.total_return * 100
        ],
        '夏普比率': [
            ma_result.sharpe_ratio,
            rsi_result.sharpe_ratio,
            bb_result.sharpe_ratio,
            sl_result.sharpe_ratio,
            ps_result.sharpe_ratio
        ],
        '最大回撤(%)': [
            ma_result.max_drawdown * 100,
            rsi_result.max_drawdown * 100,
            bb_result.max_drawdown * 100,
            sl_result.max_drawdown * 100,
            ps_result.max_drawdown * 100
        ],
        '胜率(%)': [
            ma_result.win_rate * 100,
            rsi_result.win_rate * 100,
            bb_result.win_rate * 100,
            sl_result.win_rate * 100,
            ps_result.win_rate * 100
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    print("\n" + df_comparison.to_string(index=False))
    
    # 绘制比较图表
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 总收益比较
    axes[0, 0].bar(df_comparison['策略'], df_comparison['总收益(%)'], 
                   color='steelblue', alpha=0.7)
    axes[0, 0].set_title('总收益比较', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('收益率 (%)', fontsize=10)
    axes[0, 0].grid(True, alpha=0.3)
    
    # 夏普比率比较
    axes[0, 1].bar(df_comparison['策略'], df_comparison['夏普比率'], 
                   color='forestgreen', alpha=0.7)
    axes[0, 1].set_title('夏普比率比较', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('夏普比率', fontsize=10)
    axes[0, 1].grid(True, alpha=0.3)
    
    # 最大回撤比较
    axes[1, 0].bar(df_comparison['策略'], df_comparison['最大回撤(%)'], 
                   color='crimson', alpha=0.7)
    axes[1, 0].set_title('最大回撤比较', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('回撤 (%)', fontsize=10)
    axes[1, 0].grid(True, alpha=0.3)
    
    # 胜率比较
    axes[1, 1].bar(df_comparison['策略'], df_comparison['胜率(%)'], 
                   color='orange', alpha=0.7)
    axes[1, 1].set_title('胜率比较', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('胜率 (%)', fontsize=10)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('pybroker_strategy_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()


# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("PyBroker 量化交易回测示例")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 选择要运行的策略
    print("\n请选择要运行的策略:")
    print("1. 移动平均线交叉策略")
    print("2. RSI 策略")
    print("3. 布林带策略")
    print("4. 止损止盈策略")
    print("5. 仓位管理策略")
    print("6. 多策略组合")
    print("7. 比较所有策略")
    print("8. 运行所有策略")
    
    choice = input("\n请输入选项 (1-8): ").strip()
    
    if choice == '1':
        run_ma_crossover_backtest()
    elif choice == '2':
        run_rsi_backtest()
    elif choice == '3':
        run_bollinger_bands_backtest()
    elif choice == '4':
        run_stop_loss_backtest()
    elif choice == '5':
        run_position_sizing_backtest()
    elif choice == '6':
        run_multi_strategy_backtest()
    elif choice == '7':
        compare_strategies()
    elif choice == '8':
        run_ma_crossover_backtest()
        run_rsi_backtest()
        run_bollinger_bands_backtest()
        run_stop_loss_backtest()
        run_position_sizing_backtest()
        run_multi_strategy_backtest()
    else:
        print("无效选项，运行移动平均线交叉策略")
        run_ma_crossover_backtest()
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("回测完成！")
    print("="*80)