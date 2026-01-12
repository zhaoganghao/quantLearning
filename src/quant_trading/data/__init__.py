"""
Main data module for quantitative trading system.
Provides a unified interface for data collection, storage, and validation.
"""

from .data_collector import DataCollector, MockDataCollector
from .data_storage import DataStorage
from .data_validator import DataValidator
import pandas as pd


class DataManager:
    """Main interface for data management in the quant trading system."""

    def __init__(self, collector: DataCollector = None, storage: DataStorage = None):
        """
        Initialize data manager.

        Args:
            collector: Data collector instance (defaults to MockDataCollector)
            storage: Data storage instance (defaults to DataStorage with default DB)
        """
        self.collector = collector or MockDataCollector()
        self.storage = storage or DataStorage()
        self.validator = DataValidator()

    def collect_and_store(self, symbol: str, start_date: str, end_date: str) -> bool:
        """
        Collect historical data and store it.

        Args:
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            True if successful, False otherwise
        """
        try:
            # Collect data
            data = self.collector.get_historical_data(symbol, start_date, end_date)

            # Validate data
            is_valid, error_msg = self.validator.validate_data(data)
            if not is_valid:
                print(f"Data validation failed: {error_msg}")
                return False

            # Clean data
            cleaned_data = self.validator.clean_data(data)

            # Store data
            self.storage.save_data(symbol, cleaned_data)

            return True
        except Exception as e:
            print(f"Error collecting and storing data: {e}")
            return False

    def get_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Retrieve data for analysis.

        Args:
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            DataFrame with market data
        """
        return self.storage.load_data(symbol, start_date, end_date)

    def stream_realtime_data(self, symbol: str):
        """
        Stream real-time data for a symbol.

        Args:
            symbol: The ticker symbol for the asset

        Yields:
            Real-time data points
        """
        while True:
            data = self.collector.get_realtime_data(symbol)
            yield data