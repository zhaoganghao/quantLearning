"""
Portfolio risk management for quantitative trading system.
Provides tools to monitor and manage portfolio-level risk exposure.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from scipy.stats import norm


class PortfolioRiskManager:
    """Manages portfolio-level risk exposure."""

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize portfolio risk manager.

        Args:
            confidence_level: Confidence level for risk calculations (default 95%)
        """
        self.confidence_level = confidence_level
        self.positions = {}
        self.risk_limits = {}

    def add_position(self, symbol: str, size: float, price: float, volatility: float):
        """
        Add a position to the portfolio.

        Args:
            symbol: Asset symbol
            size: Position size (positive for long, negative for short)
            price: Current price
            volatility: Asset volatility (standard deviation of returns)
        """
        self.positions[symbol] = {
            'size': size,
            'price': price,
            'volatility': volatility,
            'value': abs(size) * price
        }

    def remove_position(self, symbol: str):
        """
        Remove a position from the portfolio.

        Args:
            symbol: Asset symbol to remove
        """
        if symbol in self.positions:
            del self.positions[symbol]

    def set_risk_limit(self, limit_type: str, limit_value: float):
        """
        Set a risk limit for the portfolio.

        Args:
            limit_type: Type of risk limit ('max_position_size', 'max_portfolio_var', etc.)
            limit_value: Limit value
        """
        self.risk_limits[limit_type] = limit_value

    def calculate_value_at_risk(self, time_horizon: int = 1) -> float:
        """
        Calculate portfolio Value-at-Risk (VaR).

        Args:
            time_horizon: Time horizon in days (default 1)

        Returns:
            Value-at-Risk for the portfolio
        """
        if not self.positions:
            return 0.0

        # Calculate portfolio variance
        portfolio_variance = 0.0
        symbols = list(self.positions.keys())

        for i, symbol1 in enumerate(symbols):
            pos1 = self.positions[symbol1]
            # Variance of individual position
            position_var = (pos1['value'] * pos1['volatility']) ** 2

            portfolio_variance += position_var

            # Covariance with other positions (simplified - assuming 50% correlation)
            for symbol2 in symbols[i+1:]:
                pos2 = self.positions[symbol2]
                correlation = 0.5  # Simplified assumption
                covariance = (pos1['value'] * pos1['volatility'] *
                            pos2['value'] * pos2['volatility'] * correlation)
                portfolio_variance += 2 * covariance

        # Calculate VaR
        portfolio_volatility = np.sqrt(portfolio_variance)
        z_score = norm.ppf(self.confidence_level)
        var = portfolio_volatility * z_score * np.sqrt(time_horizon)

        return var

    def calculate_maximum_drawdown(self, historical_returns: pd.Series) -> float:
        """
        Calculate maximum drawdown from historical returns.

        Args:
            historical_returns: Series of historical portfolio returns

        Returns:
            Maximum drawdown as a decimal
        """
        if historical_returns.empty:
            return 0.0

        # Calculate cumulative returns
        cumulative = (1 + historical_returns).cumprod()

        # Calculate running maximum
        running_max = cumulative.expanding().max()

        # Calculate drawdown
        drawdown = (cumulative - running_max) / running_max

        # Return maximum drawdown
        return drawdown.min()

    def calculate_correlation_risk(self, correlation_matrix: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate correlation risk measures.

        Args:
            correlation_matrix: DataFrame with asset correlation matrix

        Returns:
            Dictionary with correlation risk measures
        """
        if correlation_matrix.empty:
            return {}

        # Average correlation
        avg_correlation = correlation_matrix.values[np.triu_indices_from(
            correlation_matrix.values, k=1)].mean()

        # Correlation volatility (standard deviation of correlations)
        corr_volatility = correlation_matrix.values[np.triu_indices_from(
            correlation_matrix.values, k=1)].std()

        return {
            'average_correlation': avg_correlation,
            'correlation_volatility': corr_volatility
        }

    def check_risk_limits(self, portfolio_value: float) -> Dict[str, bool]:
        """
        Check if portfolio exceeds any risk limits.

        Args:
            portfolio_value: Current portfolio value

        Returns:
            Dictionary indicating which limits are exceeded
        """
        violations = {}

        # Check maximum position size limit
        if 'max_position_size' in self.risk_limits:
            max_position_value = self.risk_limits['max_position_size']
            for symbol, position in self.positions.items():
                if position['value'] > max_position_value:
                    violations[f'max_position_size_{symbol}'] = True

        # Check maximum portfolio VaR limit
        if 'max_portfolio_var' in self.risk_limits:
            max_var = self.risk_limits['max_portfolio_var']
            current_var = self.calculate_value_at_risk()
            violations['max_portfolio_var'] = current_var > max_var

        # Check maximum portfolio drawdown limit
        if 'max_drawdown' in self.risk_limits:
            max_drawdown = self.risk_limits['max_drawdown']
            # This would require historical returns data
            # For now, we'll skip this check in this simplified implementation

        return violations

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get portfolio risk summary.

        Returns:
            Dictionary with portfolio risk metrics
        """
        if not self.positions:
            return {
                'total_value': 0.0,
                'num_positions': 0,
                'value_at_risk': 0.0
            }

        total_value = sum(pos['value'] for pos in self.positions.values())
        var = self.calculate_value_at_risk()

        return {
            'total_value': total_value,
            'num_positions': len(self.positions),
            'value_at_risk': var,
            'positions': {symbol: pos['value'] for symbol, pos in self.positions.items()}
        }