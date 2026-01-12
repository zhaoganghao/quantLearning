"""
Visualization tools for quantitative trading system.
Generates charts and graphs to display strategy performance.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')


class PerformanceVisualizer:
    """Creates visualizations for strategy performance analysis."""

    def __init__(self):
        """Initialize performance visualizer."""
        # Set default style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

    def plot_equity_curve(self, equity_curve: pd.Series, title: str = "Equity Curve") -> plt.Figure:
        """
        Plot equity curve.

        Args:
            equity_curve: Series with equity values over time
            title: Chart title

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(equity_curve.index, equity_curve.values, linewidth=2)
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Equity ($)", fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    def plot_drawdown_curve(self, equity_curve: pd.Series, title: str = "Drawdown Curve") -> plt.Figure:
        """
        Plot drawdown curve.

        Args:
            equity_curve: Series with equity values over time
            title: Chart title

        Returns:
            Matplotlib figure
        """
        # Calculate running maximum
        running_max = equity_curve.expanding().max()

        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max * 100

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
        ax.plot(drawdown.index, drawdown.values, linewidth=2, color='red')
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Drawdown (%)", fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    def plot_returns_histogram(self, returns: pd.Series, title: str = "Returns Distribution") -> plt.Figure:
        """
        Plot histogram of returns.

        Args:
            returns: Series with returns
            title: Chart title

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(returns.values * 100, bins=50, alpha=0.7, edgecolor='black')
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel("Returns (%)", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.grid(True, alpha=0.3)

        # Add statistics
        mean_return = returns.mean() * 100
        std_return = returns.std() * 100
        ax.axvline(mean_return, color='red', linestyle='--', linewidth=2,
                  label=f'Mean: {mean_return:.2f}%')
        ax.axvline(mean_return + std_return, color='orange', linestyle=':',
                  label=f'+1 Std Dev: {mean_return + std_return:.2f}%')
        ax.axvline(mean_return - std_return, color='orange', linestyle=':',
                  label=f'-1 Std Dev: {mean_return - std_return:.2f}%')
        ax.legend()

        plt.tight_layout()
        return fig

    def plot_trade_analysis(self, trades: List[Dict[str, Any]], title: str = "Trade Analysis") -> plt.Figure:
        """
        Plot trade analysis charts.

        Args:
            trades: List of trade dictionaries
            title: Chart title

        Returns:
            Matplotlib figure
        """
        if not trades:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "No trades to display", ha='center', va='center',
                   transform=ax.transAxes, fontsize=16)
            ax.set_title(title, fontsize=16, pad=20)
            return fig

        # Extract PnL values
        pnls = [t.get('pnl', 0) for t in trades]
        trade_numbers = list(range(len(pnls)))

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot 1: PnL over time
        colors = ['red' if pnl < 0 else 'green' for pnl in pnls]
        ax1.bar(trade_numbers, pnls, color=colors)
        ax1.set_title("PnL by Trade", fontsize=14)
        ax1.set_xlabel("Trade Number", fontsize=12)
        ax1.set_ylabel("PnL ($)", fontsize=12)
        ax1.grid(True, alpha=0.3)

        # Plot 2: PnL distribution
        ax2.hist(pnls, bins=30, alpha=0.7, edgecolor='black', color='blue')
        ax2.set_title("PnL Distribution", fontsize=14)
        ax2.set_xlabel("PnL ($)", fontsize=12)
        ax2.set_ylabel("Frequency", fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.axvline(np.mean(pnls), color='red', linestyle='--', linewidth=2,
                   label=f'Mean PnL: ${np.mean(pnls):.2f}')
        ax2.legend()

        fig.suptitle(title, fontsize=16)
        plt.tight_layout()
        return fig

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
        returns = equity_curve.pct_change().dropna()

        if len(returns) < window:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, "Insufficient data for rolling metrics", ha='center', va='center',
                   transform=ax.transAxes, fontsize=16)
            ax.set_title("Rolling Metrics", fontsize=16, pad=20)
            return fig

        # Calculate rolling metrics
        rolling_returns = returns.rolling(window=window)
        rolling_volatility = rolling_returns.std() * np.sqrt(periods_per_year)
        rolling_sharpe = (rolling_returns.mean() * periods_per_year) / rolling_volatility

        # Align indices
        dates = returns.index[window-1:]
        rr_values = rolling_returns.mean().values[window-1:] * periods_per_year * 100
        rv_values = rolling_volatility.values[window-1:] * 100
        rs_values = rolling_sharpe.values[window-1:]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot 1: Rolling returns and volatility
        ax1.plot(dates, rr_values, label='Rolling Return (%)', linewidth=2)
        ax1.set_title(f"Rolling {window}-Period Returns", fontsize=14)
        ax1.set_xlabel("Date", fontsize=12)
        ax1.set_ylabel("Annualized Return (%)", fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax1_twin = ax1.twinx()
        ax1_twin.plot(dates, rv_values, color='red', label='Rolling Volatility (%)', linewidth=2)
        ax1_twin.set_ylabel("Volatility (%)", fontsize=12, color='red')
        ax1_twin.tick_params(axis='y', labelcolor='red')
        ax1_twin.legend(loc='upper right')

        # Plot 2: Rolling Sharpe ratio
        ax2.plot(dates, rs_values, color='purple', linewidth=2)
        ax2.set_title(f"Rolling {window}-Period Sharpe Ratio", fontsize=14)
        ax2.set_xlabel("Date", fontsize=12)
        ax2.set_ylabel("Sharpe Ratio", fontsize=12)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def create_performance_summary(self, metrics: Dict[str, float]) -> plt.Figure:
        """
        Create performance summary chart.

        Args:
            metrics: Dictionary with performance metrics

        Returns:
            Matplotlib figure
        """
        # Select key metrics for summary
        key_metrics = {
            'Total Return': f"{metrics.get('total_return', 0) * 100:.2f}%",
            'Annual Return': f"{metrics.get('annualized_return', 0) * 100:.2f}%",
            'Volatility': f"{metrics.get('volatility', 0) * 100:.2f}%",
            'Sharpe Ratio': f"{metrics.get('sharpe_ratio', 0):.2f}",
            'Max Drawdown': f"{metrics.get('max_drawdown', 0) * 100:.2f}%",
            'Win Rate': f"{metrics.get('win_rate', 0) * 100:.1f}%" if 'win_rate' in metrics else "N/A"
        }

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('tight')
        ax.axis('off')

        # Create table
        table_data = [[metric, value] for metric, value in key_metrics.items()]
        table = ax.table(cellText=table_data,
                        colLabels=['Metric', 'Value'],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.4, 0.3])

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)

        # Style the table
        for i in range(len(table_data) + 1):
            for j in range(2):
                cell = table[(i, j)]
                if i == 0:  # Header
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')

        ax.set_title("Performance Summary", fontsize=16, pad=20)
        plt.tight_layout()
        return fig