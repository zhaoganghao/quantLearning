"""
Data collection module for quantitative trading system.
Provides interfaces for collecting financial market data from various sources.
"""

import pandas as pd
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class DataCollector(ABC):
    """Abstract base class for data collectors."""

    @abstractmethod
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve historical data for a given symbol.

        Args:
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with historical price data
        """
        pass

    @abstractmethod
    def get_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time data for a given symbol.

        Args:
            symbol: The ticker symbol for the asset

        Returns:
            Dictionary with current price and other relevant data
        """
        pass


class MockDataCollector(DataCollector):
    """Mock data collector for testing purposes."""

    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate mock historical data.

        Args:
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with mock historical price data
        """
        # Generate mock data for demonstration
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        prices = pd.Series(range(len(dates)), index=dates) * 0.1 + 100

        df = pd.DataFrame({
            'date': dates,
            'open': prices * 0.99,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'close': prices,
            'volume': prices * 1000
        })

        return df

    def get_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """
        Generate mock real-time data.

        Args:
            symbol: The ticker symbol for the asset

        Returns:
            Dictionary with mock current price data
        """
        import random
        return {
            'symbol': symbol,
            'price': 100 + random.random() * 10,
            'timestamp': pd.Timestamp.now(),
            'volume': random.randint(1000, 10000)
        }