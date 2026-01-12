"""
Data storage module for quantitative trading system.
Handles storage and retrieval of financial market data.
"""

import pandas as pd
import sqlite3
from typing import Optional
import os


class DataStorage:
    """Handles storage and retrieval of financial market data."""

    def __init__(self, db_path: str = "market_data.db"):
        """
        Initialize data storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    UNIQUE(symbol, date)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol_date ON market_data(symbol, date)")

    def save_data(self, symbol: str, data: pd.DataFrame):
        """
        Save market data to database.

        Args:
            symbol: The ticker symbol for the asset
            data: DataFrame with market data (columns: date, open, high, low, close, volume)
        """
        with sqlite3.connect(self.db_path) as conn:
            for _, row in data.iterrows():
                conn.execute("""
                    INSERT OR REPLACE INTO market_data
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    row['date'].strftime('%Y-%m-%d'),
                    row['open'],
                    row['high'],
                    row['low'],
                    row['close'],
                    row['volume']
                ))

    def load_data(self, symbol: str, start_date: Optional[str] = None,
                  end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Load market data from database.

        Args:
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            DataFrame with market data
        """
        query = "SELECT * FROM market_data WHERE symbol = ?"
        params = [symbol]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date"

        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=params)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        return df

    def delete_data(self, symbol: str, start_date: Optional[str] = None,
                    end_date: Optional[str] = None):
        """
        Delete market data from database.

        Args:
            symbol: The ticker symbol for the asset
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
        """
        query = "DELETE FROM market_data WHERE symbol = ?"
        params = [symbol]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)