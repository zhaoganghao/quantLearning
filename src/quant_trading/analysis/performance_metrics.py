"""
Performance metrics calculation for quantitative trading system.
Calculates comprehensive performance metrics for trading strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy import stats


class PerformanceMetrics:
    """Calculates performance metrics for trading strategies."""

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize performance metrics calculator.

        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.risk_free_rate = risk_free_rate

    def calculate_returns(self, equity_curve: pd.Series) -> pd.Series:
        """
        Calculate returns from equity curve.

        Args:
            equity_curve: Series with equity values over time

        Returns:
            Series with returns
        """
        return equity_curve.pct_change().dropna()

    def calculate_total_return(self, equity_curve: pd.Series) -> float:
        """
        Calculate total return.

        Args:
            equity_curve: Series with equity values over time

        Returns:
            Total return as decimal
        """
        if len(equity_curve) < 2:
            return 0.0
        return (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1

    def calculate_annualized_return(self, equity_curve: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate annualized return.

        Args:
            equity_curve: Series with equity values over time
            periods_per_year: Number of periods per year (252 for daily, 12 for monthly, etc.)

        Returns:
            Annualized return as decimal
        """
        total_return = self.calculate_total_return(equity_curve)
        num_periods = len(equity_curve) - 1
        if num_periods <= 0:
            return 0.0
        return (1 + total_return) ** (periods_per_year / num_periods) - 1

    def calculate_volatility(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate annualized volatility.

        Args:
            returns: Series with returns
            periods_per_year: Number of periods per year

        Returns:
            Annualized volatility (standard deviation of returns)
        """
        if len(returns) < 2:
            return 0.0
        return returns.std() * np.sqrt(periods_per_year)

    def calculate_sharpe_ratio(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            returns: Series with returns
            periods_per_year: Number of periods per year

        Returns:
            Sharpe ratio
        """
        if len(returns) < 2:
            return 0.0

        volatility = self.calculate_volatility(returns, periods_per_year)
        if volatility == 0:
            return 0.0

        # Calculate excess returns
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        return excess_returns.mean() / returns.std() * np.sqrt(periods_per_year)

    def calculate_sortino_ratio(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate Sortino ratio.

        Args:
            returns: Series with returns
            periods_per_year: Number of periods per year

        Returns:
            Sortino ratio
        """
        if len(returns) < 2:
            return 0.0

        # Calculate downside deviation
        negative_returns = returns[returns < 0]
        if len(negative_returns) == 0:
            downside_deviation = 0.0
        else:
            downside_deviation = negative_returns.std() * np.sqrt(periods_per_year)

        if downside_deviation == 0:
            return 0.0

        # Calculate excess returns
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        return excess_returns.mean() / downside_deviation * np.sqrt(periods_per_year)

    def calculate_maximum_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown.

        Args:
            equity_curve: Series with equity values over time

        Returns:
            Maximum drawdown as decimal
        """
        if len(equity_curve) < 2:
            return 0.0

        # Calculate running maximum
        running_max = equity_curve.expanding().max()

        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max

        # Return maximum drawdown
        return drawdown.min()

    def calculate_average_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate average drawdown.

        Args:
            equity_curve: Series with equity values over time

        Returns:
            Average drawdown as decimal
        """
        if len(equity_curve) < 2:
            return 0.0

        # Calculate running maximum
        running_max = equity_curve.expanding().max()

        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max

        # Return average drawdown
        return drawdown.mean()

    def calculate_calmar_ratio(self, equity_curve: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate Calmar ratio (return/drawdown).

        Args:
            equity_curve: Series with equity values over time
            periods_per_year: Number of periods per year

        Returns:
            Calmar ratio
        """
        annualized_return = self.calculate_annualized_return(equity_curve, periods_per_year)
        max_drawdown = abs(self.calculate_maximum_drawdown(equity_curve))

        if max_drawdown == 0:
            return 0.0

        return annualized_return / max_drawdown

    def calculate_win_rate(self, trades: List[Dict[str, Any]]) -> float:
        """
        Calculate win rate from trades.

        Args:
            trades: List of trade dictionaries

        Returns:
            Win rate as decimal
        """
        if not trades:
            return 0.0

        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        return len(winning_trades) / len(trades)

    def calculate_profit_factor(self, trades: List[Dict[str, Any]]) -> float:
        """
        Calculate profit factor (gross profits/gross losses).

        Args:
            trades: List of trade dictionaries

        Returns:
            Profit factor
        """
        if not trades:
            return 0.0

        gross_profits = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        gross_losses = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))

        if gross_losses == 0:
            return float('inf') if gross_profits > 0 else 0.0

        return gross_profits / gross_losses

    def calculate_all_metrics(self, equity_curve: pd.Series, trades: List[Dict[str, Any]] = None,
                            periods_per_year: int = 252) -> Dict[str, float]:
        """
        Calculate all performance metrics.

        Args:
            equity_curve: Series with equity values over time
            trades: List of trade dictionaries (optional)
            periods_per_year: Number of periods per year

        Returns:
            Dictionary with all performance metrics
        """
        returns = self.calculate_returns(equity_curve)

        metrics = {
            'total_return': self.calculate_total_return(equity_curve),
            'annualized_return': self.calculate_annualized_return(equity_curve, periods_per_year),
            'volatility': self.calculate_volatility(returns, periods_per_year),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns, periods_per_year),
            'sortino_ratio': self.calculate_sortino_ratio(returns, periods_per_year),
            'max_drawdown': self.calculate_maximum_drawdown(equity_curve),
            'avg_drawdown': self.calculate_average_drawdown(equity_curve),
            'calmar_ratio': self.calculate_calmar_ratio(equity_curve, periods_per_year),
            'num_periods': len(equity_curve) - 1
        }

        if trades:
            metrics['win_rate'] = self.calculate_win_rate(trades)
            metrics['profit_factor'] = self.calculate_profit_factor(trades)
            metrics['num_trades'] = len(trades)

        return metrics