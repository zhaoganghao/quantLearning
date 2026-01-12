"""
Main analysis module for quantitative trading system.
Provides a unified interface for performance analysis and visualization.
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional
from .performance_metrics import PerformanceMetrics
from .visualization import PerformanceVisualizer


class AnalysisManager:
    """Main interface for performance analysis in the quant trading system."""

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize analysis manager.

        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.metrics_calculator = PerformanceMetrics(risk_free_rate)
        self.visualizer = PerformanceVisualizer()

    def calculate_performance_metrics(self, equity_curve: pd.Series,
                                    trades: Optional[List[Dict[str, Any]]] = None,
                                    periods_per_year: int = 252) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics.

        Args:
            equity_curve: Series with equity values over time
            trades: List of trade dictionaries (optional)
            periods_per_year: Number of periods per year

        Returns:
            Dictionary with all performance metrics
        """
        return self.metrics_calculator.calculate_all_metrics(
            equity_curve, trades, periods_per_year)

    def plot_equity_curve(self, equity_curve: pd.Series, title: str = "Equity Curve") -> plt.Figure:
        """
        Plot equity curve.

        Args:
            equity_curve: Series with equity values over time
            title: Chart title

        Returns:
            Matplotlib figure
        """
        return self.visualizer.plot_equity_curve(equity_curve, title)

    def plot_drawdown_curve(self, equity_curve: pd.Series, title: str = "Drawdown Curve") -> plt.Figure:
        """
        Plot drawdown curve.

        Args:
            equity_curve: Series with equity values over time
            title: Chart title

        Returns:
            Matplotlib figure
        """
        return self.visualizer.plot_drawdown_curve(equity_curve, title)

    def plot_returns_histogram(self, returns: pd.Series, title: str = "Returns Distribution") -> plt.Figure:
        """
        Plot histogram of returns.

        Args:
            returns: Series with returns
            title: Chart title

        Returns:
            Matplotlib figure
        """
        return self.visualizer.plot_returns_histogram(returns, title)

    def plot_trade_analysis(self, trades: List[Dict[str, Any]], title: str = "Trade Analysis") -> plt.Figure:
        """
        Plot trade analysis charts.

        Args:
            trades: List of trade dictionaries
            title: Chart title

        Returns:
            Matplotlib figure
        """
        return self.visualizer.plot_trade_analysis(trades, title)

    def plot_rolling_metrics(self, equity_curve: pd.Series, window: int = 30,
                           periods_per_year: int = 252) -> plt.Figure:
        """
        Plot rolling performance metrics.

        Args:
            equity_curve: Series with equity values over time
            window: Rolling window size
            periods_per_year: Number of periods per year

        Returns:
            Matplotlib figure
        """
        return self.visualizer.plot_rolling_metrics(equity_curve, window, periods_per_year)

    def create_performance_summary(self, metrics: Dict[str, float]) -> plt.Figure:
        """
        Create performance summary chart.

        Args:
            metrics: Dictionary with performance metrics

        Returns:
            Matplotlib figure
        """
        return self.visualizer.create_performance_summary(metrics)

    def generate_performance_report(self, equity_curve: pd.Series,
                                  trades: Optional[List[Dict[str, Any]]] = None,
                                  title: str = "Performance Report") -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Args:
            equity_curve: Series with equity values over time
            trades: List of trade dictionaries (optional)
            title: Report title

        Returns:
            Dictionary with performance report components
        """
        # Calculate metrics
        metrics = self.calculate_performance_metrics(equity_curve, trades)

        # Generate visualizations
        figures = {
            'equity_curve': self.plot_equity_curve(equity_curve, f"{title} - Equity Curve"),
            'drawdown_curve': self.plot_drawdown_curve(equity_curve, f"{title} - Drawdown Curve"),
            'returns_histogram': self.plot_returns_histogram(
                equity_curve.pct_change().dropna(), f"{title} - Returns Distribution"),
            'performance_summary': self.create_performance_summary(metrics)
        }

        # Add trade analysis if trades are provided
        if trades:
            figures['trade_analysis'] = self.plot_trade_analysis(trades, f"{title} - Trade Analysis")

        # Add rolling metrics
        figures['rolling_metrics'] = self.plot_rolling_metrics(equity_curve, 30)

        return {
            'metrics': metrics,
            'figures': figures,
            'title': title
        }

    def save_report_figures(self, report: Dict[str, Any], output_dir: str):
        """
        Save report figures to files.

        Args:
            report: Performance report dictionary
            output_dir: Directory to save figures
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        figures = report.get('figures', {})
        title = report.get('title', 'performance').lower().replace(' ', '_')

        for fig_name, figure in figures.items():
            filename = f"{title}_{fig_name}.png"
            filepath = os.path.join(output_dir, filename)
            figure.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close(figure)  # Close figure to free memory

    def print_metrics_summary(self, metrics: Dict[str, float]):
        """
        Print a formatted summary of performance metrics.

        Args:
            metrics: Dictionary with performance metrics
        """
        print("\n" + "="*50)
        print("PERFORMANCE METRICS SUMMARY")
        print("="*50)

        # Return metrics
        print(f"Total Return:     {metrics.get('total_return', 0) * 100:8.2f}%")
        print(f"Annual Return:    {metrics.get('annualized_return', 0) * 100:8.2f}%")
        print(f"Volatility:       {metrics.get('volatility', 0) * 100:8.2f}%")

        # Risk-adjusted metrics
        print("-" * 30)
        print(f"Sharpe Ratio:     {metrics.get('sharpe_ratio', 0):8.2f}")
        print(f"Sortino Ratio:    {metrics.get('sortino_ratio', 0):8.2f}")
        print(f"Calmar Ratio:     {metrics.get('calmar_ratio', 0):8.2f}")

        # Drawdown metrics
        print("-" * 30)
        print(f"Max Drawdown:     {metrics.get('max_drawdown', 0) * 100:8.2f}%")
        print(f"Avg Drawdown:     {metrics.get('avg_drawdown', 0) * 100:8.2f}%")

        # Trade metrics (if available)
        if 'win_rate' in metrics:
            print("-" * 30)
            print(f"Win Rate:         {metrics.get('win_rate', 0) * 100:8.1f}%")
            print(f"Profit Factor:    {metrics.get('profit_factor', 0):8.2f}")
            print(f"Number of Trades: {metrics.get('num_trades', 0):8.0f}")

        print("="*50)