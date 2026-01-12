"""
Main strategies module for quantitative trading system.
Provides a unified interface for strategy development and backtesting.
"""

import pandas as pd
from .base_strategy import BaseStrategy, Signal, Position, StrategyResult
from .backtester import Backtester
from .ma_strategy import MAStrategy
from .mean_reversion_strategy import MeanReversionStrategy


class StrategyManager:
    """Main interface for strategy management in the quant trading system."""

    def __init__(self):
        """Initialize strategy manager."""
        self.strategies = []
        self.backtester = Backtester()

    def add_strategy(self, strategy: BaseStrategy):
        """
        Add a strategy to the manager.

        Args:
            strategy: Strategy to add
        """
        self.strategies.append(strategy)

    def remove_strategy(self, strategy_name: str):
        """
        Remove a strategy from the manager.

        Args:
            strategy_name: Name of strategy to remove
        """
        self.strategies = [s for s in self.strategies if s.name != strategy_name]

    def get_strategy(self, strategy_name: str) -> BaseStrategy:
        """
        Get a strategy by name.

        Args:
            strategy_name: Name of strategy to retrieve

        Returns:
            Strategy with given name, or None if not found
        """
        for strategy in self.strategies:
            if strategy.name == strategy_name:
                return strategy
        return None

    def list_strategies(self) -> list:
        """
        List all strategies.

        Returns:
            List of strategy names
        """
        return [strategy.name for strategy in self.strategies]

    def run_backtest(self, strategy_name: str, data: pd.DataFrame) -> StrategyResult:
        """
        Run backtest for a specific strategy.

        Args:
            strategy_name: Name of strategy to backtest
            data: DataFrame with market data

        Returns:
            StrategyResult with backtest results
        """
        strategy = self.get_strategy(strategy_name)
        if strategy is None:
            raise ValueError(f"Strategy '{strategy_name}' not found")

        return self.backtester.run_backtest(strategy, data)

    def run_portfolio_backtest(self, data_dict: dict) -> dict:
        """
        Run backtest for all strategies with provided data.

        Args:
            data_dict: Dictionary mapping strategy names to market data

        Returns:
            Dictionary mapping strategy names to StrategyResult objects
        """
        # Filter strategies to only those with data provided
        strategies_to_test = [s for s in self.strategies if s.name in data_dict]

        return self.backtester.run_portfolio_backtest(strategies_to_test, data_dict)

    def optimize_strategy(self, strategy_name: str, data: pd.DataFrame,
                         param_ranges: dict) -> dict:
        """
        Optimize strategy parameters.

        Args:
            strategy_name: Name of strategy to optimize
            data: DataFrame with market data
            param_ranges: Dictionary mapping parameter names to ranges

        Returns:
            Dictionary with best parameters and metrics
        """
        # This is a simplified implementation
        # In practice, this would use more sophisticated optimization techniques
        strategy_class = None
        if strategy_name == "MA_Strategy":
            strategy_class = MAStrategy
        elif strategy_name == "Mean_Reversion_Strategy":
            strategy_class = MeanReversionStrategy
        else:
            raise ValueError(f"Strategy '{strategy_name}' not supported for optimization")

        best_params = {}
        best_sharpe = -float('inf')

        # Simple grid search (in practice, use more efficient methods)
        # This is just a demonstration
        for param_name, param_range in param_ranges.items():
            if param_name == 'fast_period':
                for fast_val in param_range:
                    for slow_val in param_ranges.get('slow_period', [30]):
                        if fast_val < slow_val:  # Ensure valid relationship
                            params = {'fast_period': fast_val, 'slow_period': slow_val}
                            strategy = strategy_class(f"{strategy_name}_opt", params)
                            result = self.backtester.run_backtest(strategy, data)
                            if result.metrics.get('sharpe_ratio', -float('inf')) > best_sharpe:
                                best_sharpe = result.metrics.get('sharpe_ratio', -float('inf'))
                                best_params = params

        return {
            'best_params': best_params,
            'best_sharpe_ratio': best_sharpe
        }