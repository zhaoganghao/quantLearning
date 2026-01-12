"""
Main module for quantitative trading system.
Provides a unified interface for all components of the quant trading system.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from .data import DataManager
from .strategies import StrategyManager
from .risk import RiskManager
from .analysis import AnalysisManager


class QuantTradingSystem:
    """Main interface for the quantitative trading system."""

    def __init__(self, initial_capital: float = 10000.0, risk_free_rate: float = 0.02):
        """
        Initialize the quantitative trading system.

        Args:
            initial_capital: Initial account capital (default $10,000)
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.data_manager = DataManager()
        self.strategy_manager = StrategyManager()
        self.risk_manager = RiskManager()
        self.analysis_manager = AnalysisManager(risk_free_rate)
        self.initial_capital = initial_capital
        self.current_capital = initial_capital

    def collect_and_store_data(self, symbol: str, start_date: str, end_date: str) -> bool:
        """
        Collect and store market data.

        Args:
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            True if successful, False otherwise
        """
        return self.data_manager.collect_and_store(symbol, start_date, end_date)

    def get_market_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Retrieve market data for analysis.

        Args:
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            DataFrame with market data
        """
        return self.data_manager.get_data(symbol, start_date, end_date)

    def add_strategy(self, strategy):
        """
        Add a trading strategy to the system.

        Args:
            strategy: Strategy to add
        """
        self.strategy_manager.add_strategy(strategy)

    def run_strategy_backtest(self, strategy_name: str, symbol: str,
                            start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Run backtest for a strategy using market data.

        Args:
            strategy_name: Name of strategy to backtest
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            Dictionary with backtest results
        """
        # Get market data
        data = self.get_market_data(symbol, start_date, end_date)

        # Run backtest
        result = self.strategy_manager.run_backtest(strategy_name, data)

        return {
            'strategy_name': strategy_name,
            'symbol': symbol,
            'result': result
        }

    def calculate_position_size(self, method: str, symbol: str, price: float,
                              risk_params: Dict[str, Any]) -> float:
        """
        Calculate position size using specified method.

        Args:
            method: Position sizing method
            symbol: Asset symbol
            price: Current asset price
            risk_params: Risk parameters specific to the sizing method

        Returns:
            Position size
        """
        return self.risk_manager.calculate_position_size(method, self.current_capital, price, risk_params)[0]

    def validate_trade(self, symbol: str, size: float, price: float) -> tuple:
        """
        Validate if a trade complies with risk limits.

        Args:
            symbol: Asset symbol
            size: Proposed position size
            price: Current price

        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.risk_manager.validate_trade(symbol, size, price, self.current_capital)

    def analyze_strategy_performance(self, equity_curve: pd.Series,
                                   trades: Optional[List[Dict[str, Any]]] = None,
                                   title: str = "Strategy Performance") -> Dict[str, Any]:
        """
        Analyze strategy performance and generate report.

        Args:
            equity_curve: Series with equity values over time
            trades: List of trade dictionaries (optional)
            title: Report title

        Returns:
            Dictionary with performance analysis report
        """
        return self.analysis_manager.generate_performance_report(equity_curve, trades, title)

    def print_performance_summary(self, metrics: Dict[str, float]):
        """
        Print a formatted summary of performance metrics.

        Args:
            metrics: Dictionary with performance metrics
        """
        self.analysis_manager.print_metrics_summary(metrics)

    def update_capital(self, new_capital: float):
        """
        Update current capital.

        Args:
            new_capital: New capital value
        """
        self.current_capital = new_capital

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status and summary.

        Returns:
            Dictionary with system status information
        """
        portfolio_summary = self.risk_manager.get_portfolio_summary()

        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'available_strategies': self.strategy_manager.list_strategies(),
            'portfolio_summary': portfolio_summary
        }