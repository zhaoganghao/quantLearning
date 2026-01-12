"""
Tests for the risk management module of the quantitative trading system.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from ..risk import RiskManager
from ..risk.position_sizing import FixedFractionalSizer, VolatilityAdjustedSizer, KellyCriterionSizer
from ..risk.portfolio_risk import PortfolioRiskManager


class TestPositionSizers(unittest.TestCase):
    """Test cases for position sizing algorithms."""

    def test_fixed_fractional_sizer(self):
        """Test fixed fractional position sizer."""
        sizer = FixedFractionalSizer()
        account_value = 10000.0
        price = 100.0
        risk_params = {'fraction': 0.02}  # 2% of account

        position_size, risk_amount = sizer.calculate_position_size(account_value, price, risk_params)

        self.assertEqual(risk_amount, 200.0)  # 2% of 10000
        self.assertEqual(position_size, 2.0)  # 200 / 100

    def test_volatility_adjusted_sizer(self):
        """Test volatility-adjusted position sizer."""
        sizer = VolatilityAdjustedSizer()
        account_value = 10000.0
        price = 100.0

        # Create mock volatility data
        dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': [100.0] * 30,
            'high': [101.0] * 30,
            'low': [99.0] * 30,
            'close': [100.0 + i * 0.1 for i in range(30)],  # Increasing prices
            'volume': [1000] * 30
        })

        risk_params = {
            'fraction': 0.01,
            'volatility_lookback': 20,
            'volatility_data': data
        }

        position_size, risk_amount = sizer.calculate_position_size(account_value, price, risk_params)

        self.assertGreater(risk_amount, 0)
        self.assertGreater(position_size, 0)

    def test_kelly_criterion_sizer(self):
        """Test Kelly Criterion position sizer."""
        sizer = KellyCriterionSizer()
        account_value = 10000.0
        price = 100.0
        risk_params = {
            'win_rate': 0.6,
            'avg_win': 1.5,
            'avg_loss': 1.0
        }

        position_size, risk_amount = sizer.calculate_position_size(account_value, price, risk_params)

        self.assertGreater(risk_amount, 0)
        self.assertGreater(position_size, 0)


class TestPortfolioRiskManager(unittest.TestCase):
    """Test cases for portfolio risk manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.portfolio_manager = PortfolioRiskManager()

    def test_add_position(self):
        """Test adding a position."""
        self.portfolio_manager.add_position('AAPL', 100, 150.0, 0.02)

        self.assertIn('AAPL', self.portfolio_manager.positions)
        position = self.portfolio_manager.positions['AAPL']
        self.assertEqual(position['size'], 100)
        self.assertEqual(position['price'], 150.0)
        self.assertEqual(position['volatility'], 0.02)
        self.assertEqual(position['value'], 15000.0)

    def test_remove_position(self):
        """Test removing a position."""
        self.portfolio_manager.add_position('AAPL', 100, 150.0, 0.02)
        self.portfolio_manager.remove_position('AAPL')

        self.assertNotIn('AAPL', self.portfolio_manager.positions)

    def test_set_risk_limit(self):
        """Test setting risk limits."""
        self.portfolio_manager.set_risk_limit('max_position_size', 10000.0)

        self.assertIn('max_position_size', self.portfolio_manager.risk_limits)
        self.assertEqual(self.portfolio_manager.risk_limits['max_position_size'], 10000.0)

    def test_calculate_value_at_risk(self):
        """Test VaR calculation."""
        # Add some positions
        self.portfolio_manager.add_position('AAPL', 100, 150.0, 0.02)
        self.portfolio_manager.add_position('GOOGL', 50, 2500.0, 0.015)

        var = self.portfolio_manager.calculate_value_at_risk()

        self.assertGreaterEqual(var, 0)

    def test_get_portfolio_summary(self):
        """Test portfolio summary."""
        # Add some positions
        self.portfolio_manager.add_position('AAPL', 100, 150.0, 0.02)
        self.portfolio_manager.add_position('GOOGL', 50, 2500.0, 0.015)

        summary = self.portfolio_manager.get_portfolio_summary()

        self.assertIn('total_value', summary)
        self.assertIn('num_positions', summary)
        self.assertIn('value_at_risk', summary)
        self.assertEqual(summary['num_positions'], 2)


class TestRiskManager(unittest.TestCase):
    """Test cases for risk manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager()

    def test_calculate_position_size(self):
        """Test position size calculation."""
        account_value = 10000.0
        price = 100.0
        risk_params = {'fraction': 0.01}

        position_size, risk_amount = self.risk_manager.calculate_position_size(
            'fixed_fractional', account_value, price, risk_params)

        self.assertEqual(risk_amount, 100.0)
        self.assertEqual(position_size, 1.0)

    def test_calculate_position_size_invalid_method(self):
        """Test position size calculation with invalid method."""
        with self.assertRaises(ValueError):
            self.risk_manager.calculate_position_size('invalid_method', 10000.0, 100.0, {})

    def test_add_portfolio_position(self):
        """Test adding portfolio position."""
        self.risk_manager.add_portfolio_position('AAPL', 100, 150.0, 0.02)

        self.assertIn('AAPL', self.risk_manager.portfolio_manager.positions)

    def test_validate_trade(self):
        """Test trade validation."""
        # Set a position size limit
        self.risk_manager.set_risk_limit('max_position_size', 10000.0)

        # Test a valid trade
        is_valid, error_msg = self.risk_manager.validate_trade('AAPL', 50, 100.0, 10000.0)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

        # Test an invalid trade (exceeds position size limit)
        is_valid, error_msg = self.risk_manager.validate_trade('GOOGL', 200, 100.0, 10000.0)
        self.assertFalse(is_valid)
        self.assertIn("maximum position size limit", error_msg)


if __name__ == '__main__':
    unittest.main()