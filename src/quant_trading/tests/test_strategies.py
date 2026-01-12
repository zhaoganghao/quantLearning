"""
Tests for the strategies module of the quantitative trading system.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from ..strategies import StrategyManager
from ..strategies.base_strategy import BaseStrategy, Signal, Position
from ..strategies.ma_strategy import MAStrategy
from ..strategies.mean_reversion_strategy import MeanReversionStrategy
from ..strategies.backtester import Backtester


class TestBaseStrategy(unittest.TestCase):
    """Test cases for base strategy functionality."""

    def test_signal_enum(self):
        """Test Signal enum values."""
        self.assertEqual(Signal.BUY.value, "BUY")
        self.assertEqual(Signal.SELL.value, "SELL")
        self.assertEqual(Signal.HOLD.value, "HOLD")

    def test_position_enum(self):
        """Test Position enum values."""
        self.assertEqual(Position.LONG.value, "LONG")
        self.assertEqual(Position.SHORT.value, "SHORT")
        self.assertEqual(Position.FLAT.value, "FLAT")


class TestMAStrategy(unittest.TestCase):
    """Test cases for Moving Average strategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = MAStrategy()

    def test_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.name, "MA_Strategy")
        self.assertEqual(self.strategy.fast_period, 10)
        self.assertEqual(self.strategy.slow_period, 30)

    def test_initialization_with_params(self):
        """Test strategy initialization with custom parameters."""
        params = {'fast_period': 5, 'slow_period': 20}
        strategy = MAStrategy("Custom_MA", params)
        self.assertEqual(strategy.fast_period, 5)
        self.assertEqual(strategy.slow_period, 20)

    def test_generate_signal_not_enough_data(self):
        """Test signal generation with insufficient data."""
        # Create data with fewer periods than slow_period
        dates = pd.date_range(start='2023-01-01', periods=20, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': [100.0] * 20,
            'high': [101.0] * 20,
            'low': [99.0] * 20,
            'close': [100.5] * 20,
            'volume': [1000] * 20
        })

        signal = self.strategy.generate_signal(data)
        self.assertEqual(signal, Signal.HOLD)

    def test_calculate_position_size(self):
        """Test position size calculation."""
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': [100.0] * 50,
            'high': [101.0] * 50,
            'low': [99.0] * 50,
            'close': [100.5] * 50,
            'volume': [1000] * 50
        })

        position_size = self.strategy.calculate_position_size(Signal.BUY, data, 10000.0)
        self.assertGreater(position_size, 0)


class TestMeanReversionStrategy(unittest.TestCase):
    """Test cases for Mean Reversion strategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = MeanReversionStrategy()

    def test_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.name, "Mean_Reversion_Strategy")
        self.assertEqual(self.strategy.lookback_period, 20)
        self.assertEqual(self.strategy.z_score_threshold, 2.0)

    def test_initialization_with_params(self):
        """Test strategy initialization with custom parameters."""
        params = {'lookback_period': 15, 'z_score_threshold': 1.5}
        strategy = MeanReversionStrategy("Custom_MR", params)
        self.assertEqual(strategy.lookback_period, 15)
        self.assertEqual(strategy.z_score_threshold, 1.5)


class TestBacktester(unittest.TestCase):
    """Test cases for backtesting engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.backtester = Backtester(initial_capital=10000.0)

    def test_initialization(self):
        """Test backtester initialization."""
        self.assertEqual(self.backtester.initial_capital, 10000.0)
        self.assertEqual(self.backtester.commission, 0.0)

    def test_calculate_metrics_empty_data(self):
        """Test metrics calculation with empty data."""
        equity_curve = pd.Series()
        trades = []
        metrics = self.backtester._calculate_metrics(equity_curve, trades)
        self.assertEqual(metrics, {})


class TestStrategyManager(unittest.TestCase):
    """Test cases for strategy manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = StrategyManager()

    def test_initialization(self):
        """Test manager initialization."""
        self.assertEqual(len(self.manager.strategies), 0)
        self.assertIsInstance(self.manager.backtester, Backtester)

    def test_add_strategy(self):
        """Test adding strategy."""
        strategy = MAStrategy()
        self.manager.add_strategy(strategy)
        self.assertEqual(len(self.manager.strategies), 1)
        self.assertEqual(self.manager.strategies[0], strategy)

    def test_remove_strategy(self):
        """Test removing strategy."""
        strategy1 = MAStrategy("Strategy1")
        strategy2 = MAStrategy("Strategy2")
        self.manager.add_strategy(strategy1)
        self.manager.add_strategy(strategy2)

        self.manager.remove_strategy("Strategy1")
        self.assertEqual(len(self.manager.strategies), 1)
        self.assertEqual(self.manager.strategies[0].name, "Strategy2")

    def test_get_strategy(self):
        """Test getting strategy by name."""
        strategy = MAStrategy("Test_Strategy")
        self.manager.add_strategy(strategy)

        retrieved = self.manager.get_strategy("Test_Strategy")
        self.assertEqual(retrieved, strategy)

        not_found = self.manager.get_strategy("Non_Existent")
        self.assertIsNone(not_found)

    def test_list_strategies(self):
        """Test listing strategies."""
        strategy1 = MAStrategy("Strategy1")
        strategy2 = MAStrategy("Strategy2")
        self.manager.add_strategy(strategy1)
        self.manager.add_strategy(strategy2)

        strategy_names = self.manager.list_strategies()
        self.assertIn("Strategy1", strategy_names)
        self.assertIn("Strategy2", strategy_names)
        self.assertEqual(len(strategy_names), 2)


if __name__ == '__main__':
    unittest.main()