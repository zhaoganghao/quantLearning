"""
Tests for the analysis module of the quantitative trading system.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
import matplotlib.pyplot as plt

from ..analysis import AnalysisManager
from ..analysis.performance_metrics import PerformanceMetrics
from ..analysis.visualization import PerformanceVisualizer


class TestPerformanceMetrics(unittest.TestCase):
    """Test cases for performance metrics calculation."""

    def setUp(self):
        """Set up test fixtures."""
        self.metrics = PerformanceMetrics()

    def test_calculate_returns(self):
        """Test returns calculation."""
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        equity = pd.Series([100, 105, 102, 108, 110], index=dates)

        returns = self.metrics.calculate_returns(equity)

        self.assertEqual(len(returns), 4)
        self.assertAlmostEqual(returns.iloc[0], 0.05)  # 5% return
        self.assertAlmostEqual(returns.iloc[1], -0.02857, places=5)  # ~-2.86% return

    def test_calculate_total_return(self):
        """Test total return calculation."""
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        equity = pd.Series([100, 105, 102, 108, 110], index=dates)

        total_return = self.metrics.calculate_total_return(equity)

        self.assertAlmostEqual(total_return, 0.10)  # 10% total return

    def test_calculate_annualized_return(self):
        """Test annualized return calculation."""
        dates = pd.date_range(start='2023-01-01', periods=253, freq='D')  # ~1 year of data
        equity = pd.Series([100] * 253, index=dates)
        # Add some growth
        equity = pd.Series([100 * (1 + 0.0004 * i) for i in range(253)], index=dates)

        annualized_return = self.metrics.calculate_annualized_return(equity, 252)

        self.assertGreater(annualized_return, 0)

    def test_calculate_volatility(self):
        """Test volatility calculation."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        # Generate returns with some volatility
        returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=dates)

        volatility = self.metrics.calculate_volatility(returns, 252)

        self.assertGreater(volatility, 0)

    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        # Generate returns with positive drift
        returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=dates)

        sharpe = self.metrics.calculate_sharpe_ratio(returns, 252)

        # Sharpe ratio could be positive or negative depending on random data
        self.assertIsInstance(sharpe, float)

    def test_calculate_maximum_drawdown(self):
        """Test maximum drawdown calculation."""
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        # Create equity curve with a drawdown
        equity = pd.Series([100, 110, 105, 102, 108], index=dates)

        max_dd = self.metrics.calculate_maximum_drawdown(equity)

        self.assertLessEqual(max_dd, 0)  # Drawdown should be negative or zero

    def test_calculate_all_metrics(self):
        """Test calculation of all metrics."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        equity = pd.Series([100 * (1 + 0.001 * i) for i in range(100)], index=dates)
        # Add some noise
        equity += pd.Series(np.random.normal(0, 1, 100), index=dates)

        trades = [
            {'date': dates[10], 'pnl': 50},
            {'date': dates[20], 'pnl': -20},
            {'date': dates[30], 'pnl': 30}
        ]

        metrics = self.metrics.calculate_all_metrics(equity, trades, 252)

        self.assertIsInstance(metrics, dict)
        self.assertIn('total_return', metrics)
        self.assertIn('annualized_return', metrics)
        self.assertIn('volatility', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('win_rate', metrics)
        self.assertIn('profit_factor', metrics)


class TestPerformanceVisualizer(unittest.TestCase):
    """Test cases for performance visualization."""

    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = PerformanceVisualizer()

    def test_plot_equity_curve(self):
        """Test equity curve plotting."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        equity = pd.Series([100 * (1 + 0.001 * i) for i in range(100)], index=dates)

        fig = self.visualizer.plot_equity_curve(equity, "Test Equity Curve")

        self.assertIsNotNone(fig)
        plt.close(fig)  # Clean up

    def test_plot_drawdown_curve(self):
        """Test drawdown curve plotting."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        equity = pd.Series([100 * (1 + 0.001 * i) for i in range(100)], index=dates)

        fig = self.visualizer.plot_drawdown_curve(equity, "Test Drawdown Curve")

        self.assertIsNotNone(fig)
        plt.close(fig)  # Clean up

    def test_plot_returns_histogram(self):
        """Test returns histogram plotting."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=dates)

        fig = self.visualizer.plot_returns_histogram(returns, "Test Returns Histogram")

        self.assertIsNotNone(fig)
        plt.close(fig)  # Clean up

    def test_plot_trade_analysis(self):
        """Test trade analysis plotting."""
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        trades = [
            {'date': dates[0], 'pnl': 50},
            {'date': dates[1], 'pnl': -20},
            {'date': dates[2], 'pnl': 30},
            {'date': dates[3], 'pnl': -10},
            {'date': dates[4], 'pnl': 40}
        ]

        fig = self.visualizer.plot_trade_analysis(trades, "Test Trade Analysis")

        self.assertIsNotNone(fig)
        plt.close(fig)  # Clean up


class TestAnalysisManager(unittest.TestCase):
    """Test cases for analysis manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.analysis_manager = AnalysisManager()

    def test_initialization(self):
        """Test analysis manager initialization."""
        self.assertIsInstance(self.analysis_manager.metrics_calculator, PerformanceMetrics)
        self.assertIsInstance(self.analysis_manager.visualizer, PerformanceVisualizer)

    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation through manager."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        equity = pd.Series([100 * (1 + 0.001 * i) for i in range(100)], index=dates)

        metrics = self.analysis_manager.calculate_performance_metrics(equity)

        self.assertIsInstance(metrics, dict)
        self.assertIn('total_return', metrics)

    def test_generate_performance_report(self):
        """Test performance report generation."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        equity = pd.Series([100 * (1 + 0.001 * i) for i in range(100)], index=dates)
        trades = [
            {'date': dates[10], 'pnl': 50},
            {'date': dates[20], 'pnl': -20},
            {'date': dates[30], 'pnl': 30}
        ]

        report = self.analysis_manager.generate_performance_report(equity, trades, "Test Report")

        self.assertIsInstance(report, dict)
        self.assertIn('metrics', report)
        self.assertIn('figures', report)
        self.assertIn('title', report)

        # Clean up figures
        for figure in report['figures'].values():
            plt.close(figure)

    def test_save_report_figures(self):
        """Test saving report figures."""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
            equity = pd.Series([100 * (1 + 0.001 * i) for i in range(100)], index=dates)

            report = self.analysis_manager.generate_performance_report(equity, title="Test Report")

            # Save figures
            self.analysis_manager.save_report_figures(report, temp_dir)

            # Check that files were created
            files = os.listdir(temp_dir)
            self.assertGreater(len(files), 0)

            # Clean up figures
            for figure in report['figures'].values():
                plt.close(figure)


if __name__ == '__main__':
    unittest.main()