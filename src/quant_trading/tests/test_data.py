"""
Tests for the data module of the quantitative trading system.
"""

import unittest
import pandas as pd
import tempfile
import os
from datetime import datetime, timedelta

from ..data import DataManager
from ..data.data_collector import MockDataCollector
from ..data.data_storage import DataStorage
from ..data.data_validator import DataValidator


class TestDataCollector(unittest.TestCase):
    """Test cases for data collector functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.collector = MockDataCollector()

    def test_get_historical_data(self):
        """Test getting historical data."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        data = self.collector.get_historical_data('TEST', start_date, end_date)

        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn('open', data.columns)
        self.assertIn('high', data.columns)
        self.assertIn('low', data.columns)
        self.assertIn('close', data.columns)
        self.assertIn('volume', data.columns)

    def test_get_realtime_data(self):
        """Test getting real-time data."""
        data = self.collector.get_realtime_data('TEST')

        self.assertIsInstance(data, dict)
        self.assertIn('symbol', data)
        self.assertIn('price', data)
        self.assertIn('timestamp', data)
        self.assertIn('volume', data)


class TestDataStorage(unittest.TestCase):
    """Test cases for data storage functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.storage = DataStorage(self.temp_db.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_db.name)

    def test_save_and_load_data(self):
        """Test saving and loading data."""
        # Create test data
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': [100.0] * len(dates),
            'high': [101.0] * len(dates),
            'low': [99.0] * len(dates),
            'close': [100.5] * len(dates),
            'volume': [1000] * len(dates)
        })

        # Save data
        self.storage.save_data('TEST', data)

        # Load data
        loaded_data = self.storage.load_data('TEST')

        self.assertIsInstance(loaded_data, pd.DataFrame)
        self.assertFalse(loaded_data.empty)
        self.assertEqual(len(loaded_data), len(data))

    def test_load_data_with_date_range(self):
        """Test loading data with date range."""
        # Create test data
        dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': [100.0] * len(dates),
            'high': [101.0] * len(dates),
            'low': [99.0] * len(dates),
            'close': [100.5] * len(dates),
            'volume': [1000] * len(dates)
        })

        # Save data
        self.storage.save_data('TEST', data)

        # Load data with date range
        loaded_data = self.storage.load_data(
            'TEST',
            start_date='2023-01-10',
            end_date='2023-01-20'
        )

        self.assertIsInstance(loaded_data, pd.DataFrame)
        self.assertFalse(loaded_data.empty)
        self.assertEqual(len(loaded_data), 11)  # 11 days from Jan 10-20


class TestDataValidator(unittest.TestCase):
    """Test cases for data validator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = DataValidator()

    def test_validate_valid_data(self):
        """Test validating valid data."""
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': [100.0] * len(dates),
            'high': [101.0] * len(dates),
            'low': [99.0] * len(dates),
            'close': [100.5] * len(dates),
            'volume': [1000] * len(dates)
        })

        is_valid, error_msg = self.validator.validate_data(data)

        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_validate_invalid_data_negative_prices(self):
        """Test validating data with negative prices."""
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': [-100.0] * len(dates),  # Negative prices
            'high': [101.0] * len(dates),
            'low': [99.0] * len(dates),
            'close': [100.5] * len(dates),
            'volume': [1000] * len(dates)
        })

        is_valid, error_msg = self.validator.validate_data(data)

        self.assertFalse(is_valid)
        self.assertIn("Negative prices", error_msg)

    def test_clean_data(self):
        """Test cleaning data."""
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
        # Create data with some missing values
        data = pd.DataFrame({
            'date': dates,
            'open': [100.0, None, 102.0, 103.0, 104.0, None, 106.0, 107.0, 108.0, 109.0],
            'high': [101.0] * len(dates),
            'low': [99.0] * len(dates),
            'close': [100.5] * len(dates),
            'volume': [1000] * len(dates)
        })

        cleaned_data = self.validator.clean_data(data)

        self.assertIsInstance(cleaned_data, pd.DataFrame)
        self.assertFalse(cleaned_data.isnull().any().any())  # No missing values
        self.assertEqual(len(cleaned_data), len(data))


class TestDataManager(unittest.TestCase):
    """Test cases for data manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()

        collector = MockDataCollector()
        storage = DataStorage(self.temp_db.name)
        self.manager = DataManager(collector, storage)

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_db.name)

    def test_collect_and_store(self):
        """Test collecting and storing data."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        result = self.manager.collect_and_store('TEST', start_date, end_date)

        self.assertTrue(result)

    def test_get_data(self):
        """Test getting data."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        # First collect and store some data
        self.manager.collect_and_store('TEST', start_date, end_date)

        # Then retrieve it
        data = self.manager.get_data('TEST')

        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)


if __name__ == '__main__':
    unittest.main()