"""
Backtesting engine for quantitative trading system.
Simulates trading strategies using historical data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from .base_strategy import BaseStrategy, Signal, StrategyResult


class Backtester:
    """Backtesting engine for trading strategies."""

    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.0):
        """
        Initialize backtester.

        Args:
            initial_capital: Initial account capital
            commission: Commission per trade (as fraction of trade value)
        """
        self.initial_capital = initial_capital
        self.commission = commission

    def run_backtest(self, strategy: BaseStrategy, data: pd.DataFrame) -> StrategyResult:
        """
        Run backtest for a strategy.

        Args:
            strategy: Trading strategy to backtest
            data: DataFrame with market data

        Returns:
            StrategyResult with backtest results
        """
        # Reset strategy state
        strategy.reset()

        # Initialize tracking variables
        capital = self.initial_capital
        position_size = 0.0
        equity_curve = []
        trades = []
        holdings = []

        # Run backtest
        for i, (date, row) in enumerate(data.iterrows()):
            current_price = row['close']

            # Generate signal
            signal = strategy.generate_signal(data.iloc[:i+1] if i > 0 else data.iloc[:1])

            # Execute trade if signal is not HOLD
            if signal != Signal.HOLD:
                # Calculate position size
                position_size = strategy.calculate_position_size(signal, data.iloc[:i+1], capital)

                # Calculate transaction cost
                transaction_cost = abs(position_size * current_price) * self.commission

                # Execute trade
                if signal == Signal.BUY:
                    # Buy signal
                    cost = position_size * current_price + transaction_cost
                    if cost <= capital:
                        capital -= cost
                        holdings.append({
                            'date': date,
                            'price': current_price,
                            'size': position_size,
                            'type': 'BUY'
                        })
                        trades.append({
                            'date': date,
                            'price': current_price,
                            'size': position_size,
                            'type': 'BUY',
                            'cost': cost
                        })
                        strategy.update_position(signal, current_price)
                elif signal == Signal.SELL:
                    # Sell signal
                    if holdings:
                        # Sell existing holdings
                        proceeds = position_size * current_price - transaction_cost
                        capital += proceeds
                        holdings.append({
                            'date': date,
                            'price': current_price,
                            'size': position_size,
                            'type': 'SELL'
                        })
                        trades.append({
                            'date': date,
                            'price': current_price,
                            'size': position_size,
                            'type': 'SELL',
                            'proceeds': proceeds
                        })
                        strategy.update_position(signal, current_price)

            # Calculate current portfolio value
            holding_value = sum(h['size'] * current_price for h in holdings)
            total_value = capital + holding_value
            equity_curve.append(total_value)

        # Create result object
        result = StrategyResult()
        result.trades = trades

        # Create equity curve series
        equity_series = pd.Series(equity_curve, index=data.index)
        result.set_equity_curve(equity_series)

        # Calculate performance metrics
        metrics = self._calculate_metrics(equity_series, trades)
        result.set_metrics(metrics)

        return result

    def _calculate_metrics(self, equity_curve: pd.Series, trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate performance metrics.

        Args:
            equity_curve: Series with equity values
            trades: List of trades

        Returns:
            Dictionary with performance metrics
        """
        if len(equity_curve) < 2:
            return {}

        # Calculate returns
        returns = equity_curve.pct_change().dropna()

        # Basic metrics
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1  # Assuming daily data

        # Risk metrics
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0

        # Drawdown metrics
        rolling_max = equity_curve.expanding().max()
        drawdown = (equity_curve - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # Trade metrics
        num_trades = len(trades)
        win_rate = 0.0
        if num_trades > 0:
            # Simplified win rate calculation
            winning_trades = [t for t in trades if t.get('proceeds', 0) > t.get('cost', 0)]
            win_rate = len(winning_trades) / num_trades if num_trades > 0 else 0

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'num_trades': num_trades,
            'win_rate': win_rate
        }

    def run_portfolio_backtest(self, strategies: List[BaseStrategy],
                             data_dict: Dict[str, pd.DataFrame]) -> Dict[str, StrategyResult]:
        """
        Run backtest for a portfolio of strategies.

        Args:
            strategies: List of trading strategies
            data_dict: Dictionary mapping strategy names to market data

        Returns:
            Dictionary mapping strategy names to StrategyResult objects
        """
        results = {}
        for strategy in strategies:
            if strategy.name in data_dict:
                result = self.run_backtest(strategy, data_dict[strategy.name])
                results[strategy.name] = result

        return results