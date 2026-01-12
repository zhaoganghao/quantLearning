"""
Main risk management module for quantitative trading system.
Provides a unified interface for position sizing and portfolio risk management.
"""

import pandas as pd
from .position_sizing import PositionSizer, FixedFractionalSizer, VolatilityAdjustedSizer, KellyCriterionSizer
from .portfolio_risk import PortfolioRiskManager
from typing import Dict, Any, Tuple


class RiskManager:
    """Main interface for risk management in the quant trading system."""

    def __init__(self):
        """Initialize risk manager."""
        self.position_sizers = {
            'fixed_fractional': FixedFractionalSizer(),
            'volatility_adjusted': VolatilityAdjustedSizer(),
            'kelly_criterion': KellyCriterionSizer()
        }
        self.portfolio_manager = PortfolioRiskManager()

    def calculate_position_size(self, method: str, account_value: float, price: float,
                              risk_params: Dict[str, Any]) -> Tuple[float, float]:
        """
        Calculate position size using specified method.

        Args:
            method: Position sizing method ('fixed_fractional', 'volatility_adjusted', 'kelly_criterion')
            account_value: Current account value
            price: Current asset price
            risk_params: Risk parameters specific to the sizing method

        Returns:
            Tuple of (position_size, risk_amount)

        Raises:
            ValueError: If method is not supported
        """
        if method not in self.position_sizers:
            raise ValueError(f"Position sizing method '{method}' not supported")

        sizer = self.position_sizers[method]
        return sizer.calculate_position_size(account_value, price, risk_params)

    def add_portfolio_position(self, symbol: str, size: float, price: float, volatility: float):
        """
        Add a position to the portfolio risk manager.

        Args:
            symbol: Asset symbol
            size: Position size (positive for long, negative for short)
            price: Current price
            volatility: Asset volatility (standard deviation of returns)
        """
        self.portfolio_manager.add_position(symbol, size, price, volatility)

    def remove_portfolio_position(self, symbol: str):
        """
        Remove a position from the portfolio risk manager.

        Args:
            symbol: Asset symbol to remove
        """
        self.portfolio_manager.remove_position(symbol)

    def set_risk_limit(self, limit_type: str, limit_value: float):
        """
        Set a risk limit for the portfolio.

        Args:
            limit_type: Type of risk limit ('max_position_size', 'max_portfolio_var', etc.)
            limit_value: Limit value
        """
        self.portfolio_manager.set_risk_limit(limit_type, limit_value)

    def calculate_value_at_risk(self, time_horizon: int = 1) -> float:
        """
        Calculate portfolio Value-at-Risk (VaR).

        Args:
            time_horizon: Time horizon in days (default 1)

        Returns:
            Value-at-Risk for the portfolio
        """
        return self.portfolio_manager.calculate_value_at_risk(time_horizon)

    def calculate_maximum_drawdown(self, historical_returns: pd.Series) -> float:
        """
        Calculate maximum drawdown from historical returns.

        Args:
            historical_returns: Series of historical portfolio returns

        Returns:
            Maximum drawdown as a decimal
        """
        return self.portfolio_manager.calculate_maximum_drawdown(historical_returns)

    def check_risk_limits(self, portfolio_value: float) -> Dict[str, bool]:
        """
        Check if portfolio exceeds any risk limits.

        Args:
            portfolio_value: Current portfolio value

        Returns:
            Dictionary indicating which limits are exceeded
        """
        return self.portfolio_manager.check_risk_limits(portfolio_value)

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get portfolio risk summary.

        Returns:
            Dictionary with portfolio risk metrics
        """
        return self.portfolio_manager.get_portfolio_summary()

    def validate_trade(self, symbol: str, size: float, price: float,
                      account_value: float) -> Tuple[bool, str]:
        """
        Validate if a trade complies with risk limits.

        Args:
            symbol: Asset symbol
            size: Proposed position size
            price: Current price
            account_value: Current account value

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if this trade would exceed position size limits
        if 'max_position_size' in self.portfolio_manager.risk_limits:
            max_position_value = self.portfolio_manager.risk_limits['max_position_size']
            proposed_value = abs(size) * price
            if proposed_value > max_position_value:
                return False, f"Trade would exceed maximum position size limit of {max_position_value}"

        # Check if this trade would exceed portfolio VaR limits
        if 'max_portfolio_var' in self.portfolio_manager.risk_limits:
            # Add the proposed position temporarily
            current_positions = self.portfolio_manager.positions.copy()
            self.add_portfolio_position(symbol, size, price, 0.01)  # Assume 1% volatility for check

            max_var = self.portfolio_manager.risk_limits['max_portfolio_var']
            current_var = self.calculate_value_at_risk()

            # Restore original positions
            self.portfolio_manager.positions = current_positions

            if current_var > max_var:
                return False, f"Trade would exceed maximum portfolio VaR limit of {max_var}"

        return True, ""