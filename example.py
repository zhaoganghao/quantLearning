"""
Example script demonstrating the quantitative trading system.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.quant_trading import QuantTradingSystem
from src.quant_trading.strategies import MAStrategy, MeanReversionStrategy


def main():
    """Run example quantitative trading system demonstration."""
    print("Quantitative Trading System Example")
    print("=" * 40)

    # Initialize the system
    qts = QuantTradingSystem(initial_capital=10000.0)
    print(f"System initialized with ${qts.initial_capital:,.2f} capital")

    # Add strategies
    ma_strategy = MAStrategy("MA_Strategy", {"fast_period": 10, "slow_period": 30})
    mr_strategy = MeanReversionStrategy("Mean_Reversion_Strategy", {
        "lookback_period": 20,
        "z_score_threshold": 2.0
    })

    qts.add_strategy(ma_strategy)
    qts.add_strategy(mr_strategy)
    print(f"Added strategies: {qts.strategy_manager.list_strategies()}")

    # Collect mock data (this will use the mock data collector)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    print(f"\nCollecting mock data for AAPL from {start_date} to {end_date}...")
    success = qts.collect_and_store_data("AAPL", start_date, end_date)
    if success:
        print("Data collection successful")
    else:
        print("Data collection failed")

    # Get the data
    data = qts.get_market_data("AAPL")
    print(f"Retrieved {len(data)} data points")

    # Run backtests
    print("\nRunning backtests...")

    # Moving Average Strategy
    ma_results = qts.run_strategy_backtest("MA_Strategy", "AAPL")
    print(f"MA Strategy backtest completed with {len(ma_results['result'].trades)} trades")

    # Mean Reversion Strategy
    mr_results = qts.run_strategy_backtest("Mean_Reversion_Strategy", "AAPL")
    print(f"Mean Reversion Strategy backtest completed with {len(mr_results['result'].trades)} trades")

    # Analyze performance
    print("\nAnalyzing performance...")

    # MA Strategy performance
    ma_report = qts.analyze_strategy_performance(
        ma_results['result'].equity_curve,
        ma_results['result'].trades,
        "MA Strategy Performance"
    )

    print("\nMA Strategy Performance Summary:")
    qts.print_performance_summary(ma_report['metrics'])

    # Mean Reversion Strategy performance
    mr_report = qts.analyze_strategy_performance(
        mr_results['result'].equity_curve,
        mr_results['result'].trades,
        "Mean Reversion Strategy Performance"
    )

    print("\nMean Reversion Strategy Performance Summary:")
    qts.print_performance_summary(mr_report['metrics'])

    # Show system status
    print("\nSystem Status:")
    status = qts.get_system_status()
    print(f"Initial Capital: ${status['initial_capital']:,.2f}")
    print(f"Current Capital: ${status['current_capital']:,.2f}")
    print(f"Available Strategies: {status['available_strategies']}")
    print(f"Portfolio Positions: {status['portfolio_summary']}")

    # Demonstrate position sizing
    print("\nPosition Sizing Examples:")
    price = 150.0  # Current price of AAPL

    # Fixed fractional sizing
    fixed_size = qts.calculate_position_size(
        'fixed_fractional',
        'AAPL',
        price,
        {'fraction': 0.02}
    )
    print(f"Fixed Fractional (2% of capital): {fixed_size:.2f} shares")

    # Volatility adjusted sizing
    vol_size = qts.calculate_position_size(
        'volatility_adjusted',
        'AAPL',
        price,
        {
            'fraction': 0.01,
            'volatility_lookback': 20,
            'volatility_data': data
        }
    )
    print(f"Volatility Adjusted (1% of capital): {vol_size:.2f} shares")

    # Demonstrate risk validation
    print("\nRisk Validation Examples:")
    is_valid, error_msg = qts.validate_trade('AAPL', 100, 150.0)
    print(f"Trade validation for 100 shares at $150: {is_valid} - {error_msg}")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()