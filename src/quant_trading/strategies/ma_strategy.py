"""
Moving Average strategy implementation for quantitative trading system.
Simple strategy that uses moving averages to generate buy/sell signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_strategy import BaseStrategy, Signal, Position


class MAStrategy(BaseStrategy):
    """Moving Average trading strategy."""

    def __init__(self, name: str = "MA_Strategy", params: Dict[str, Any] = None):
        """
        Initialize MA strategy.

        Args:
            name: Name of the strategy
            params: Strategy parameters (fast_period, slow_period)
        """
        super().__init__(name, params)
        self.fast_period = params.get('fast_period', 10) if params else 10
        self.slow_period = params.get('slow_period', 30) if params else 30

    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate trading signal based on moving average crossover.

        Args:
            data: DataFrame with market data

        Returns:
            Trading signal (BUY, SELL, or HOLD)
        """
        if len(data) < self.slow_period:
            return Signal.HOLD

        # Calculate moving averages
        fast_ma = data['close'].rolling(window=self.fast_period).mean()
        slow_ma = data['close'].rolling(window=self.slow_period).mean()

        # Get latest values
        current_fast = fast_ma.iloc[-1]
        current_slow = slow_ma.iloc[-1]
        previous_fast = fast_ma.iloc[-2]
        previous_slow = slow_ma.iloc[-2]

        # Generate signals
        if previous_fast <= previous_slow and current_fast > current_slow:
            # Fast MA crosses above slow MA - buy signal
            return Signal.BUY
        elif previous_fast >= previous_slow and current_fast < current_slow:
            # Fast MA crosses below slow MA - sell signal
            if self.position == Position.LONG:
                return Signal.SELL
            else:
                return Signal.HOLD
        else:
            return Signal.HOLD

    def calculate_position_size(self, signal: Signal, data: pd.DataFrame,
                              account_value: float) -> float:
        """
        Calculate position size as a fixed fraction of account value.

        Args:
            signal: Trading signal
            data: DataFrame with market data
            account_value: Current account value

        Returns:
            Position size (number of shares/contracts)
        """
        if signal == Signal.HOLD:
            return 0.0

        current_price = data['close'].iloc[-1]
        # Risk 1% of account per trade
        risk_amount = account_value * 0.01
        position_size = risk_amount / current_price

        return position_size