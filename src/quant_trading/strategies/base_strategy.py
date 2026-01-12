"""
Base strategy classes for quantitative trading system.
Provides standardized interfaces for trading strategies.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum


class Signal(Enum):
    """Signal types for trading strategies."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Position(Enum):
    """Position types for trading strategies."""
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str, params: Dict[str, Any] = None):
        """
        Initialize strategy.

        Args:
            name: Name of the strategy
            params: Strategy parameters
        """
        self.name = name
        self.params = params or {}
        self.position = Position.FLAT
        self.entry_price = 0.0
        self.performance_metrics = {}

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Generate trading signal based on market data.

        Args:
            data: DataFrame with market data

        Returns:
            Trading signal (BUY, SELL, or HOLD)
        """
        pass

    @abstractmethod
    def calculate_position_size(self, signal: Signal, data: pd.DataFrame,
                              account_value: float) -> float:
        """
        Calculate position size based on signal and account value.

        Args:
            signal: Trading signal
            data: DataFrame with market data
            account_value: Current account value

        Returns:
            Position size (number of shares/contracts)
        """
        pass

    def update_position(self, signal: Signal, price: float):
        """
        Update position based on signal.

        Args:
            signal: Trading signal
            price: Current price
        """
        if signal == Signal.BUY and self.position == Position.FLAT:
            self.position = Position.LONG
            self.entry_price = price
        elif signal == Signal.SELL and self.position == Position.FLAT:
            self.position = Position.SHORT
            self.entry_price = price
        elif signal == Signal.SELL and self.position == Position.LONG:
            self.position = Position.FLAT
            self.entry_price = 0.0
        elif signal == Signal.BUY and self.position == Position.SHORT:
            self.position = Position.FLAT
            self.entry_price = 0.0

    def get_current_position(self) -> Position:
        """
        Get current position.

        Returns:
            Current position
        """
        return self.position

    def get_entry_price(self) -> float:
        """
        Get entry price.

        Returns:
            Entry price
        """
        return self.entry_price

    def reset(self):
        """Reset strategy state."""
        self.position = Position.FLAT
        self.entry_price = 0.0
        self.performance_metrics = {}


class StrategyResult:
    """Container for strategy backtest results."""

    def __init__(self):
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: pd.Series = pd.Series()
        self.metrics: Dict[str, float] = {}

    def add_trade(self, trade: Dict[str, Any]):
        """Add a trade to results."""
        self.trades.append(trade)

    def set_equity_curve(self, equity_curve: pd.Series):
        """Set equity curve."""
        self.equity_curve = equity_curve

    def set_metrics(self, metrics: Dict[str, float]):
        """Set performance metrics."""
        self.metrics = metrics