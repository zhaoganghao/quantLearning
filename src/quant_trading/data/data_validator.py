"""
Data validation and cleaning module for quantitative trading system.
Ensures quality and consistency of financial market data.
"""

import pandas as pd
import numpy as np
from typing import Tuple


class DataValidator:
    """Validates and cleans financial market data."""

    @staticmethod
    def validate_data(data: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate market data for common issues.

        Args:
            data: DataFrame with market data

        Returns:
            Tuple of (is_valid, error_message)
        """
        if data.empty:
            return False, "Data is empty"

        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return False, f"Missing required columns: {missing_columns}"

        # Check for negative prices
        if (data['open'] < 0).any() or (data['high'] < 0).any() or \
           (data['low'] < 0).any() or (data['close'] < 0).any():
            return False, "Negative prices found"

        # Check for negative volume
        if (data['volume'] < 0).any():
            return False, "Negative volume found"

        # Check for high/low consistency
        if (data['high'] < data['low']).any():
            return False, "High price lower than low price found"

        # Check for open/close outside high/low range
        if (data['open'] > data['high']).any() or (data['open'] < data['low']).any():
            return False, "Open price outside high/low range"

        if (data['close'] > data['high']).any() or (data['close'] < data['low']).any():
            return False, "Close price outside high/low range"

        return True, ""

    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean market data by handling missing values and outliers.

        Args:
            data: DataFrame with market data

        Returns:
            Cleaned DataFrame
        """
        # Make a copy to avoid modifying original data
        cleaned_data = data.copy()

        # Handle missing values using forward fill, then backward fill
        cleaned_data = cleaned_data.ffill()
        cleaned_data = cleaned_data.bfill()

        # Remove duplicate dates
        cleaned_data.drop_duplicates(subset=['date'], keep='first', inplace=True)

        # Sort by date
        cleaned_data.sort_values('date', inplace=True)

        # Handle zero volume days (may indicate non-trading days)
        cleaned_data = cleaned_data[cleaned_data['volume'] > 0]

        return cleaned_data

    @staticmethod
    def detect_outliers(data: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect outliers in price data using z-score method.

        Args:
            data: DataFrame with market data
            threshold: Z-score threshold for outlier detection

        Returns:
            DataFrame with outlier information
        """
        # Calculate returns
        returns = data['close'].pct_change().dropna()

        # Calculate z-scores
        z_scores = np.abs((returns - returns.mean()) / returns.std())

        # Identify outliers
        outliers = returns[z_scores > threshold]

        # Create DataFrame with outlier information
        outlier_info = pd.DataFrame({
            'date': outliers.index,
            'return': outliers.values,
            'z_score': z_scores[outliers.index].values
        })

        return outlier_info