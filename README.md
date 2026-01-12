# Quantitative Trading Learning System

A comprehensive Python framework for learning and implementing quantitative trading strategies with data collection, strategy development, risk management, and performance analysis capabilities.

## Features

- **Data Collection**: Interfaces for collecting financial market data from various sources
- **Strategy Development**: Framework for implementing and backtesting trading strategies
- **Risk Management**: Position sizing algorithms and portfolio risk management tools
- **Performance Analysis**: Comprehensive metrics calculation and visualization tools
- **Integration**: Unified interface for all components

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd quant-learning
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Basic Example

```python
from quant_trading import QuantTradingSystem
from quant_trading.strategies import MAStrategy

# Initialize the system
qts = QuantTradingSystem(initial_capital=10000.0)

# Add a strategy
strategy = MAStrategy("My_MA_Strategy", {"fast_period": 10, "slow_period": 30})
qts.add_strategy(strategy)

# Collect market data
qts.collect_and_store_data("AAPL", "2023-01-01", "2023-12-31")

# Run backtest
results = qts.run_strategy_backtest("My_MA_Strategy", "AAPL")

# Analyze performance
report = qts.analyze_strategy_performance(
    results['result'].equity_curve,
    results['result'].trades,
    "AAPL MA Strategy Backtest"
)

# Print performance summary
qts.print_performance_summary(report['metrics'])
```

## Modules

### Data Module
Handles data collection, storage, and validation:
- `DataManager`: Main interface for data operations
- `DataCollector`: Abstract base class for data collectors
- `MockDataCollector`: Sample implementation for testing
- `DataStorage`: SQLite-based data storage
- `DataValidator`: Data validation and cleaning

### Strategies Module
Framework for strategy development and backtesting:
- `StrategyManager`: Main interface for strategy management
- `BaseStrategy`: Abstract base class for trading strategies
- `Backtester`: Backtesting engine
- `MAStrategy`: Moving average crossover strategy
- `MeanReversionStrategy`: Mean reversion strategy

### Risk Module
Risk management and position sizing:
- `RiskManager`: Main interface for risk management
- `PositionSizer`: Abstract base class for position sizers
- `FixedFractionalSizer`: Fixed fractional position sizing
- `VolatilityAdjustedSizer`: Volatility-adjusted position sizing
- `PortfolioRiskManager`: Portfolio-level risk management

### Analysis Module
Performance analysis and visualization:
- `AnalysisManager`: Main interface for performance analysis
- `PerformanceMetrics`: Comprehensive metrics calculation
- `PerformanceVisualizer`: Data visualization tools

## Testing

Run tests with pytest:
```bash
pytest src/quant_trading/tests/
```

Run tests with coverage:
```bash
pytest --cov=src/quant_trading src/quant_trading/tests/
```

## Development

Code formatting:
```bash
black src/
isort src/
```

Linting:
```bash
flake8 src/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.