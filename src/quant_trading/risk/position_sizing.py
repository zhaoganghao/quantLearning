"""
Position sizing algorithms for quantitative trading system.
Determines appropriate trade sizes based on account equity, risk tolerance, and strategy parameters.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class PositionSizer(ABC):
    """Abstract base class for position sizers."""

    @abstractmethod
    def calculate_position_size(self, account_value: float, price: float,
                              risk_params: Dict[str, Any]) -> Tuple[float, float]:
        """
        Calculate position size and risk amount.

        Args:
            account_value: Current account value
            price: Current asset price
            risk_params: Risk parameters specific to the sizing method

        Returns:
            Tuple of (position_size, risk_amount)
        """
        pass


class FixedFractionalSizer(PositionSizer):
    """Fixed fractional position sizing - risks a fixed fraction of account equity."""

    def calculate_position_size(self, account_value: float, price: float,
                              risk_params: Dict[str, Any]) -> Tuple[float, float]:
        """
        Calculate position size using fixed fractional method.

        Args:
            account_value: Current account value
            price: Current asset price
            risk_params: Risk parameters (fraction: fraction of account to risk)

        Returns:
            Tuple of (position_size, risk_amount)
        """
        fraction = risk_params.get('fraction', 0.01)  # Default to 1% of account
        risk_amount = account_value * fraction
        position_size = risk_amount / price if price > 0 else 0.0

        return position_size, risk_amount


class VolatilityAdjustedSizer(PositionSizer):
    """Volatility-adjusted position sizing - adjusts position size inversely to asset volatility."""

    def calculate_position_size(self, account_value: float, price: float,
                              risk_params: Dict[str, Any]) -> Tuple[float, float]:
        """
        Calculate position size using volatility-adjusted method.

        Args:
            account_value: Current account value
            price: Current asset price
            risk_params: Risk parameters (fraction: fraction of account to risk,
                         volatility_lookback: lookback period for volatility calculation,
                         volatility_data: historical price data for volatility calculation)

        Returns:
            Tuple of (position_size, risk_amount)
        """
        fraction = risk_params.get('fraction', 0.01)  # Default to 1% of account
        lookback = risk_params.get('volatility_lookback', 20)
        volatility_data = risk_params.get('volatility_data')

        risk_amount = account_value * fraction

        if volatility_data is not None and len(volatility_data) >= lookback:
            # Calculate volatility (standard deviation of returns)
            returns = volatility_data['close'].pct_change().dropna().tail(lookback)
            volatility = returns.std()

            if volatility > 0:
                # Adjust position size inversely to volatility
                # Higher volatility -> smaller position size
                adjusted_risk_amount = risk_amount / (volatility * 100)  # Scale factor
                position_size = adjusted_risk_amount / price if price > 0 else 0.0
                return position_size, adjusted_risk_amount

        # Fallback to fixed fractional if volatility calculation fails
        position_size = risk_amount / price if price > 0 else 0.0
        return position_size, risk_amount


class KellyCriterionSizer(PositionSizer):
    """Kelly Criterion position sizing - optimizes position size based on win probability and payoff."""

    def calculate_position_size(self, account_value: float, price: float,
                              risk_params: Dict[str, Any]) -> Tuple[float, float]:
        """
        Calculate position size using Kelly Criterion.

        Args:
            account_value: Current account value
            price: Current asset price
            risk_params: Risk parameters (win_rate: historical win rate,
                         avg_win: average win per trade,
                         avg_loss: average loss per trade)

        Returns:
            Tuple of (position_size, risk_amount)
        """
        win_rate = risk_params.get('win_rate', 0.5)
        avg_win = risk_params.get('avg_win', 1.0)
        avg_loss = risk_params.get('avg_loss', 1.0)

        if avg_loss > 0:
            # Kelly Criterion formula: f* = p - (1-p)/b
            # where p = win probability, b = avg_win/avg_loss
            b = avg_win / avg_loss
            kelly_fraction = win_rate - (1 - win_rate) / b if b > 0 else 0

            # Use fractional Kelly to reduce risk
            fractional_kelly = kelly_fraction * 0.25  # 1/4 Kelly

            if fractional_kelly > 0:
                risk_amount = account_value * min(fractional_kelly, 0.02)  # Cap at 2%
                position_size = risk_amount / price if price > 0 else 0.0
                return position_size, risk_amount

        # Fallback to fixed fractional if Kelly calculation fails
        fraction = 0.01
        risk_amount = account_value * fraction
        position_size = risk_amount / price if price > 0 else 0.0
        return position_size, risk_amount