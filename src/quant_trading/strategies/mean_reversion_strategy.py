"""
Mean Reversion strategy implementation for quantitative trading system.
Strategy that assumes prices will revert to their mean over time.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_strategy import BaseStrategy, Signal, Position


class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion trading strategy."""

    def __init__(self, name: str = "Mean_Reversion_Strategy", params: Dict[str, Any] = None):
        """
        Initialize Mean Reversion strategy.

        Args:
            name: Name of the strategy
            params: Strategy parameters (lookback_period, z_score_threshold)
        """
        super().__init__(name, params)
        self.lookback_period = params.get('lookback_period', 20) if params else 20
        self.z_score_threshold = params.get('z_score_threshold', 2.0) if params else 2.0

    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate trading signal based on mean reversion.

        Args:
            data: DataFrame with market data

        Returns:
            Trading signal (BUY, SELL, or HOLD)
        """
        if len(data) < self.lookback_period:
            return Signal.HOLD

        # Calculate mean and standard deviation
        prices = data['close'].tail(self.lookback_period)
        mean_price = prices.mean()
        std_price = prices.std()

        current_price = data['close'].iloc[-1]

        # Calculate z-score
        if std_price > 0:
            z_score = (current_price - mean_price) / std_price

            # Generate signals
            if z_score > self.z_score_threshold:
                # Price is significantly above mean - sell signal
                if self.position == Position.LONG:
                    return Signal.SELL
                else:
                    return Signal.HOLD
            elif z_score < -self.z_score_threshold:
                # Price is significantly below mean - buy signal
                return Signal.BUY
            else:
                return Signal.HOLD
        else:
            return Signal.HOLD

    def calculate_position_size(self, signal: Signal, data: pd.DataFrame,
                              account_value: float) -> float:
        """
        Calculate position size based on z-score.

        Args:
            signal: Trading signal
            data: DataFrame with market data
            account_value: Current account value

        Returns:
            Position size (number of shares/contracts)
        """
        if signal == Signal.HOLD:
            return 0.0

        # Calculate mean and standard deviation
        prices = data['close'].tail(self.lookback_period)
        mean_price = prices.mean()
        std_price = prices.std()

        current_price = data['close'].iloc[-1]

        # Calculate z-score
        if std_price > 0:
            z_score = abs((current_price - mean_price) / std_price)
            # Position size proportional to how far price is from mean
            position_fraction = min(z_score / self.z_score_threshold, 1.0)
            risk_amount = account_value * 0.01 * position_fraction
            position_size = risk_amount / current_price
        else:
            position_size = 0.0

        return position_size