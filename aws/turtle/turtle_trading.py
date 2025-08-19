"""
Turtle Trading System Implementation
Based on the original Richard Dennis and William Eckhardt system
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class TurtleTrading:
    def __init__(self, initial_capital=100000, risk_per_trade=0.02, max_units=4):
        """
        Initialize Turtle Trading System
        
        Args:
            initial_capital: Starting capital
            risk_per_trade: Risk percentage per trade (default 2%)
            max_units: Maximum units per position
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_units = max_units
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
    def calculate_true_range(self, data):
        """Calculate True Range for volatility measurement"""
        data['prev_close'] = data['Close'].shift(1)
        data['tr1'] = data['High'] - data['Low']
        data['tr2'] = abs(data['High'] - data['prev_close'])
        data['tr3'] = abs(data['Low'] - data['prev_close'])
        data['true_range'] = data[['tr1', 'tr2', 'tr3']].max(axis=1)
        data['atr'] = data['true_range'].rolling(window=20).mean()
        return data
    
    def calculate_donchian_channels(self, data, short_period=20, long_period=55):
        """Calculate Donchian Channel breakouts"""
        # System 1 (20-day)
        data['donchian_high_20'] = data['High'].rolling(window=short_period).max()
        data['donchian_low_20'] = data['Low'].rolling(window=short_period).min()
        
        # System 2 (55-day)
        data['donchian_high_55'] = data['High'].rolling(window=long_period).max()
        data['donchian_low_55'] = data['Low'].rolling(window=long_period).min()
        
        # Exit channels (10-day and 20-day)
        data['exit_high_10'] = data['High'].rolling(window=10).max()
        data['exit_low_10'] = data['Low'].rolling(window=10).min()
        data['exit_high_20'] = data['High'].rolling(window=20).max()
        data['exit_low_20'] = data['Low'].rolling(window=20).min()
        
        return data
    
    def calculate_position_size(self, atr, price):
        """
        Calculate position size based on Turtle rules
        Risk 2% of capital per unit, with ATR-based stops
        """
        if atr == 0 or pd.isna(atr):
            return 0
            
        # Dollar risk per unit (2 * ATR * position_size)
        dollar_risk_per_unit = 2 * atr
        
        # Risk amount (2% of current capital)
        risk_amount = self.current_capital * self.risk_per_trade
        
        # Position size (number of shares/contracts)
        position_size = int(risk_amount / dollar_risk_per_unit)
        
        return max(position_size, 0)
    
    def generate_signals(self, data, system=1):
        """
        Generate entry and exit signals
        system: 1 for 20-day system, 2 for 55-day system
        """
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['atr'] = data['atr']
        
        if system == 1:
            # System 1: 20-day breakouts
            signals['long_entry'] = data['Close'] > data['donchian_high_20'].shift(1)
            signals['short_entry'] = data['Close'] < data['donchian_low_20'].shift(1)
            signals['long_exit'] = data['Close'] < data['exit_low_10'].shift(1)
            signals['short_exit'] = data['Close'] > data['exit_high_10'].shift(1)
        else:
            # System 2: 55-day breakouts
            signals['long_entry'] = data['Close'] > data['donchian_high_55'].shift(1)
            signals['short_entry'] = data['Close'] < data['donchian_low_55'].shift(1)
            signals['long_exit'] = data['Close'] < data['exit_low_20'].shift(1)
            signals['short_exit'] = data['Close'] > data['exit_high_20'].shift(1)
        
        return signals
    
    def add_units(self, symbol, current_price, atr, position):
        """Add units to existing position (pyramiding)"""
        if position['units'] >= self.max_units:
            return False
            
        # Check if price has moved 0.5 ATR in favorable direction
        if position['side'] == 'long':
            if current_price >= position['last_add_price'] + (0.5 * atr):
                return True
        else:  # short
            if current_price <= position['last_add_price'] - (0.5 * atr):
                return True
        
        return False
    
    def backtest(self, symbol, start_date, end_date, system=1):
        """
        Run backtest on given symbol
        """
        # Download data
        data = yf.download(symbol, start=start_date, end=end_date)
        
        if data.empty:
            print(f"No data available for {symbol}")
            return
        
        # Calculate indicators
        data = self.calculate_true_range(data)
        data = self.calculate_donchian_channels(data)
        
        # Generate signals
        signals = self.generate_signals(data, system)
        
        # Initialize position tracking
        position = None
        
        for i, (date, row) in enumerate(signals.iterrows()):
            if i < 55:  # Skip first 55 days for indicator calculation
                continue
                
            current_price = row['price']
            atr = row['atr']
            
            if pd.isna(atr) or atr == 0:
                continue
            
            # Check for exits first
            if position is not None:
                exit_triggered = False
                
                if position['side'] == 'long' and row['long_exit']:
                    exit_triggered = True
                elif position['side'] == 'short' and row['short_exit']:
                    exit_triggered = True
                
                # Check stop loss
                if position['side'] == 'long' and current_price <= position['stop_loss']:
                    exit_triggered = True
                elif position['side'] == 'short' and current_price >= position['stop_loss']:
                    exit_triggered = True
                
                if exit_triggered:
                    # Close position
                    if position['side'] == 'long':
                        pnl = (current_price - position['avg_price']) * position['total_size']
                    else:
                        pnl = (position['avg_price'] - current_price) * position['total_size']
                    
                    self.current_capital += pnl
                    
                    trade = {
                        'symbol': symbol,
                        'entry_date': position['entry_date'],
                        'exit_date': date,
                        'side': position['side'],
                        'entry_price': position['avg_price'],
                        'exit_price': current_price,
                        'size': position['total_size'],
                        'pnl': pnl,
                        'return_pct': pnl / (position['avg_price'] * position['total_size'])
                    }
                    self.trades.append(trade)
                    position = None
                    continue
                
                # Check for adding units (pyramiding)
                if self.add_units(symbol, current_price, atr, position):
                    add_size = self.calculate_position_size(atr, current_price)
                    if add_size > 0:
                        # Update average price
                        total_cost = (position['avg_price'] * position['total_size']) + (current_price * add_size)
                        position['total_size'] += add_size
                        position['avg_price'] = total_cost / position['total_size']
                        position['units'] += 1
                        position['last_add_price'] = current_price
            
            # Check for entries
            if position is None:
                entry_signal = None
                
                if row['long_entry']:
                    entry_signal = 'long'
                elif row['short_entry']:
                    entry_signal = 'short'
                
                if entry_signal:
                    size = self.calculate_position_size(atr, current_price)
                    
                    if size > 0:
                        # Calculate stop loss (2 ATR from entry)
                        if entry_signal == 'long':
                            stop_loss = current_price - (2 * atr)
                        else:
                            stop_loss = current_price + (2 * atr)
                        
                        position = {
                            'symbol': symbol,
                            'side': entry_signal,
                            'entry_date': date,
                            'avg_price': current_price,
                            'total_size': size,
                            'stop_loss': stop_loss,
                            'units': 1,
                            'last_add_price': current_price
                        }
            
            # Track equity curve
            portfolio_value = self.current_capital
            if position is not None:
                if position['side'] == 'long':
                    unrealized_pnl = (current_price - position['avg_price']) * position['total_size']
                else:
                    unrealized_pnl = (position['avg_price'] - current_price) * position['total_size']
                portfolio_value += unrealized_pnl
            
            self.equity_curve.append({
                'date': date,
                'portfolio_value': portfolio_value
            })
    
    def get_performance_stats(self):
        """Calculate performance statistics"""
        if not self.trades:
            return {}
        
        df_trades = pd.DataFrame(self.trades)
        
        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['pnl'] > 0])
        losing_trades = len(df_trades[df_trades['pnl'] <= 0])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = df_trades['pnl'].sum()
        avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df_trades[df_trades['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0
        
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if avg_loss != 0 else float('inf')
        
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital
        
        return {
            'Total Trades': total_trades,
            'Winning Trades': winning_trades,
            'Losing Trades': losing_trades,
            'Win Rate': f"{win_rate:.2%}",
            'Total P&L': f"${total_pnl:,.2f}",
            'Average Win': f"${avg_win:,.2f}",
            'Average Loss': f"${avg_loss:,.2f}",
            'Profit Factor': f"{profit_factor:.2f}",
            'Total Return': f"{total_return:.2%}",
            'Final Capital': f"${self.current_capital:,.2f}"
        }
    
    def plot_equity_curve(self):
        """Plot the equity curve"""
        if not self.equity_curve:
            print("No equity curve data available")
            return
        
        df_equity = pd.DataFrame(self.equity_curve)
        df_equity['date'] = pd.to_datetime(df_equity['date'])
        
        plt.figure(figsize=(12, 6))
        plt.plot(df_equity['date'], df_equity['portfolio_value'])
        plt.title('Turtle Trading System - Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def plot_trades(self, symbol):
        """Plot trades on price chart"""
        if not self.trades:
            print("No trades to plot")
            return
        
        # Get data for plotting
        start_date = min([trade['entry_date'] for trade in self.trades])
        end_date = max([trade['exit_date'] for trade in self.trades])
        
        data = yf.download(symbol, start=start_date, end=end_date)
        
        plt.figure(figsize=(15, 8))
        plt.plot(data.index, data['Close'], label='Price', alpha=0.7)
        
        # Plot trades
        for trade in self.trades:
            color = 'green' if trade['pnl'] > 0 else 'red'
            plt.scatter(trade['entry_date'], trade['entry_price'], 
                       color='blue', marker='^' if trade['side'] == 'long' else 'v', s=100)
            plt.scatter(trade['exit_date'], trade['exit_price'], 
                       color=color, marker='x', s=100)
        
        plt.title(f'Turtle Trading System - {symbol} Trades')
        plt.xlabel('Date')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


# Example usage
if __name__ == "__main__":
    # Initialize Turtle Trading System
    turtle = TurtleTrading(initial_capital=100000, risk_per_trade=0.02)
    
    # Define test parameters
    symbol = "SPY"  # S&P 500 ETF
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    print(f"Running Turtle Trading backtest on {symbol}")
    print(f"Period: {start_date} to {end_date}")
    print("-" * 50)
    
    # Run backtest
    turtle.backtest(symbol, start_date, end_date, system=1)
    
    # Print performance statistics
    stats = turtle.get_performance_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Plot results
    turtle.plot_equity_curve()
    turtle.plot_trades(symbol)
    
    print("\nTrade Details:")
    for i, trade in enumerate(turtle.trades[:10]):  # Show first 10 trades
        print(f"Trade {i+1}: {trade['side'].upper()} {trade['symbol']} "
              f"Entry: ${trade['entry_price']:.2f} Exit: ${trade['exit_price']:.2f} "
              f"P&L: ${trade['pnl']:.2f}")
