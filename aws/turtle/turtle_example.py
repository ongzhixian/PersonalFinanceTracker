"""
Simple Turtle Trading Example
This script demonstrates how to use the Turtle Trading system
"""

from turtle_trading import TurtleTrading
import pandas as pd

def run_turtle_example():
    """Run a simple example of the Turtle Trading system"""
    
    # Initialize the Turtle Trading system
    turtle = TurtleTrading(
        initial_capital=100000,  # $100,000 starting capital
        risk_per_trade=0.02,     # Risk 2% per trade
        max_units=4              # Maximum 4 units per position
    )
    
    # Test on different symbols
    symbols = ["SPY", "QQQ", "GLD", "TLT"]  # ETFs for different asset classes
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    print("Turtle Trading System Backtest Results")
    print("=" * 50)
    
    for symbol in symbols:
        print(f"\nTesting {symbol}...")
        
        # Reset for each symbol
        turtle_test = TurtleTrading(initial_capital=100000, risk_per_trade=0.02)
        
        try:
            # Run backtest
            turtle_test.backtest(symbol, start_date, end_date, system=1)
            
            # Get performance stats
            stats = turtle_test.get_performance_stats()
            
            if stats:
                print(f"Results for {symbol}:")
                print(f"  Total Trades: {stats['Total Trades']}")
                print(f"  Win Rate: {stats['Win Rate']}")
                print(f"  Total Return: {stats['Total Return']}")
                print(f"  Final Capital: {stats['Final Capital']}")
            else:
                print(f"  No trades generated for {symbol}")
                
        except Exception as e:
            print(f"  Error testing {symbol}: {e}")
    
    print("\n" + "=" * 50)
    print("Backtest completed!")

def run_detailed_analysis():
    """Run detailed analysis on a single symbol"""
    
    turtle = TurtleTrading(initial_capital=100000, risk_per_trade=0.02)
    
    symbol = "SPY"
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    print(f"\nDetailed Analysis for {symbol}")
    print("=" * 40)
    
    # Run backtest
    turtle.backtest(symbol, start_date, end_date, system=1)
    
    # Print detailed stats
    stats = turtle.get_performance_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Show individual trades
    print(f"\nFirst 10 Trades:")
    print("-" * 40)
    for i, trade in enumerate(turtle.trades[:10]):
        pnl_sign = "+" if trade['pnl'] > 0 else ""
        print(f"{i+1:2d}. {trade['entry_date'].strftime('%Y-%m-%d')} | "
              f"{trade['side'].upper():5s} | "
              f"Entry: ${trade['entry_price']:7.2f} | "
              f"Exit: ${trade['exit_price']:7.2f} | "
              f"P&L: {pnl_sign}${trade['pnl']:8.2f}")
    
    # Plot results (uncomment these lines if you want to see plots)
    # turtle.plot_equity_curve()
    # turtle.plot_trades(symbol)

def compare_systems():
    """Compare System 1 (20-day) vs System 2 (55-day)"""
    
    symbol = "SPY"
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    print("Comparing Turtle Trading Systems")
    print("=" * 40)
    
    for system in [1, 2]:
        turtle = TurtleTrading(initial_capital=100000, risk_per_trade=0.02)
        turtle.backtest(symbol, start_date, end_date, system=system)
        
        stats = turtle.get_performance_stats()
        system_name = "System 1 (20-day)" if system == 1 else "System 2 (55-day)"
        
        print(f"\n{system_name}:")
        print(f"  Total Trades: {stats.get('Total Trades', 0)}")
        print(f"  Win Rate: {stats.get('Win Rate', 'N/A')}")
        print(f"  Total Return: {stats.get('Total Return', 'N/A')}")
        print(f"  Profit Factor: {stats.get('Profit Factor', 'N/A')}")

if __name__ == "__main__":
    # Run different examples
    print("Choose an example to run:")
    print("1. Simple multi-symbol test")
    print("2. Detailed single symbol analysis")
    print("3. Compare System 1 vs System 2")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            run_turtle_example()
        elif choice == "2":
            run_detailed_analysis()
        elif choice == "3":
            compare_systems()
        else:
            print("Invalid choice. Running simple example...")
            run_turtle_example()
            
    except KeyboardInterrupt:
        print("\nExample interrupted by user")
    except Exception as e:
        print(f"Error running example: {e}")
        print("Running simple example as fallback...")
        run_turtle_example()
