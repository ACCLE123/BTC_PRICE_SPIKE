import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def plot_backtest_results():
    print("Loading data for visualization...")
    
    # 1. Load BTC Price Data
    df_price = pd.read_csv('data/btc_price_data.csv')
    df_price['datetime'] = pd.to_datetime(df_price['timestamp'], unit='s')
    
    # 2. Load Spike Events
    df_spikes = pd.read_csv('spike_events.csv')
    df_spikes['datetime'] = pd.to_datetime(df_spikes['timestamp'])
    
    # 3. Load Trade Records
    df_trades = pd.read_csv('trade_records.csv')
    df_trades['Entry Time'] = pd.to_datetime(df_trades['Entry Time'])
    
    # --- PREPARE DATA FOR EQUITY CURVE ---
    
    # Calculate Strategy Equity
    df_trades = df_trades.sort_values('Entry Time')
    df_trades['Strategy_Cum_Return'] = df_trades['PnL %'].cumsum()
    
    # Calculate Buy & Hold Equity
    initial_price = df_price.iloc[0]['close']
    df_price['BH_Return'] = (df_price['close'] - initial_price) / initial_price
    
    # --- PLOTTING ---
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot 1: BTC Price and Spikes
    ax1.plot(df_price['datetime'], df_price['close'], color='lightgray', alpha=0.5, label='BTC Price')
    ax1.scatter(df_spikes['datetime'], df_spikes['current_price'], color='red', s=20, label='Spike Detected', zorder=5)
    
    # Mark Trade Entries (optional, could be cluttered)
    ax1.scatter(df_trades['Entry Time'], df_trades['Entry Price'], marker='^', color='green', s=40, label='Trade Entry', zorder=6)
    
    ax1.set_title('BTC/USDT Price & Spike Detection', fontsize=16)
    ax1.set_ylabel('Price (USDT)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Equity Curve Comparison
    # We need to align the strategy return with the time axis
    ax2.plot(df_price['datetime'], df_price['BH_Return'] * 100, color='orange', label='Buy & Hold Return (%)')
    
    # For strategy, we plot a step function at trade exit times
    strategy_times = [df_price['datetime'].iloc[0]] + list(df_trades['Entry Time'])
    strategy_returns = [0] + list(df_trades['Strategy_Cum_Return'] * 100)
    ax2.step(strategy_times, strategy_returns, where='post', color='blue', label='Strategy Cumulative Return (%)', linewidth=2)
    
    ax2.set_title('Cumulative Return: Strategy vs Buy & Hold', fontsize=16)
    ax2.set_ylabel('Return (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Formatting X-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    output_file = 'backtest_visualization.png'
    plt.savefig(output_file)
    print(f"Visualization saved as '{output_file}'")

if __name__ == "__main__":
    plot_backtest_results()

