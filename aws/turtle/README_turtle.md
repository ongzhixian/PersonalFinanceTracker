# Turtle Trading System Implementation

This is a complete implementation of the famous Turtle Trading system developed by Richard Dennis and William Eckhardt in the 1980s.

## Features

- **Complete Turtle Rules**: Implements both System 1 (20-day) and System 2 (55-day)
- **Position Sizing**: Proper risk management with 2% risk per trade
- **Pyramiding**: Adding to winning positions at 0.5 ATR intervals
- **Stop Losses**: 2 ATR stop losses for risk control
- **Backtesting**: Full backtesting capabilities with performance metrics
- **Visualization**: Equity curve and trade plotting

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the example:
```bash
python turtle_example.py
```

## Core Components

### TurtleTrading Class

The main class that implements the Turtle Trading system:

```python
from turtle_trading import TurtleTrading

# Initialize with $100,000 capital, 2% risk per trade
turtle = TurtleTrading(initial_capital=100000, risk_per_trade=0.02)

# Run backtest
turtle.backtest("SPY", "2020-01-01", "2023-12-31", system=1)

# Get performance statistics
stats = turtle.get_performance_stats()
print(stats)
```

### Key Methods

- `backtest()`: Run backtest on historical data
- `get_performance_stats()`: Calculate performance metrics
- `plot_equity_curve()`: Plot portfolio value over time
- `plot_trades()`: Plot entry/exit points on price chart

## Turtle Trading Rules Implemented

### 1. **Market Entry**
- **System 1**: Enter long on 20-day high breakout, short on 20-day low breakout
- **System 2**: Enter long on 55-day high breakout, short on 55-day low breakout

### 2. **Position Sizing**
- Risk 2% of capital per trade
- Position size = (Account Risk) / (2 × ATR)
- Maximum 4 units per position

### 3. **Adding Units (Pyramiding)**
- Add units at 0.5 ATR intervals in favorable direction
- Each additional unit has same risk as original
- Maximum 4 units total per position

### 4. **Stop Losses**
- Initial stop: 2 ATR from entry price
- Mechanical stops, no discretion

### 5. **Exits**
- **System 1**: Exit on 10-day channel break in opposite direction
- **System 2**: Exit on 20-day channel break in opposite direction

## Example Usage

### Basic Backtest
```python
from turtle_trading import TurtleTrading

turtle = TurtleTrading(initial_capital=100000)
turtle.backtest("SPY", "2020-01-01", "2023-12-31")

# Print results
stats = turtle.get_performance_stats()
for key, value in stats.items():
    print(f"{key}: {value}")
```

### Multiple Symbols
```python
symbols = ["SPY", "QQQ", "GLD", "TLT"]

for symbol in symbols:
    turtle = TurtleTrading(initial_capital=100000)
    turtle.backtest(symbol, "2020-01-01", "2023-12-31")
    stats = turtle.get_performance_stats()
    print(f"{symbol}: {stats['Total Return']}")
```

### Compare Systems
```python
# Test both System 1 and System 2
for system in [1, 2]:
    turtle = TurtleTrading(initial_capital=100000)
    turtle.backtest("SPY", "2020-01-01", "2023-12-31", system=system)
    stats = turtle.get_performance_stats()
    print(f"System {system}: {stats['Total Return']}")
```

## Performance Metrics

The system calculates comprehensive performance statistics:

- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of profitable trades
- **Average Win/Loss**: Average profit/loss per trade
- **Profit Factor**: Ratio of total profits to total losses
- **Total Return**: Overall portfolio return
- **Maximum Drawdown**: Largest peak-to-trough decline

## Key Features

### Realistic Implementation
- Uses actual market data via Yahoo Finance
- Implements proper slippage considerations
- Realistic position sizing based on account equity

### Risk Management
- Never risk more than 2% per trade
- Automatic stop-loss execution
- Position size scales with volatility (ATR)

### Trend Following
- Only profitable in trending markets
- Many small losses, few large wins
- Mechanical execution removes emotions

## Important Notes

### Market Considerations
- **Trending Markets**: System works best in strong trends
- **Sideways Markets**: Expect multiple small losses
- **Volatile Markets**: Position sizes automatically adjust

### Limitations
- High drawdowns during choppy periods
- Requires discipline to follow mechanically
- Transaction costs not included in basic implementation

### Best Practices
- Always backtest before live trading
- Diversify across multiple uncorrelated markets
- Never override the system rules
- Ensure sufficient capital for drawdowns

## Historical Context

The original Turtle experiment:
- 23 novice traders taught this system
- Generated average annual returns of 80%
- Proved that trading could be taught systematically
- Emphasized that the system's success came from following rules exactly

## Disclaimer

This implementation is for educational purposes only. Past performance does not guarantee future results. Always do your own research and consider your risk tolerance before trading.
