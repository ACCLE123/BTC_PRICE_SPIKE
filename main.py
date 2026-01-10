import pandas as pd
from src.detector import PriceSpikeDetector
from src.simulator import TradeSimulator
from datetime import datetime

def run_backtest(csv_path):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Ensure data is sorted by timestamp
    df = df.sort_values('timestamp')
    
    detector = PriceSpikeDetector()
    simulator = TradeSimulator()
    
    spike_count = 0
    
    print("Running backtest...")
    for _, row in df.iterrows():
        ts = row['timestamp']
        price = row['close']
        
        # 1. Update simulator (check active trade exits)
        simulator.update(ts, price)
        
        # 2. Check for new spikes
        spike = detector.process_price(ts, price)
        if spike:
            spike_count += 1
            # 3. If spike detected, signal simulator to enter trade
            simulator.handle_spike(spike)
            
    # Final stats
    stats = simulator.get_stats()
    
    print("\n" + "="*40)
    print("BACKTEST SUMMARY")
    print("="*40)
    print(f"Total Spikes Detected: {spike_count}")
    print(f"Total Trades:         {stats['total_trades']}")
    print(f"Win Rate:             {stats['win_rate']:.2%}")
    print(f"Average Return:       {stats['avg_return']:.4%}")
    print(f"Cumulative Return:    {stats['cum_return']:.4%}")
    print(f"Max Drawdown (approx): {stats['max_drawdown']:.4%}")
    print("="*40)
    
    # Optional: Display first few trades
    if simulator.trades:
        print("\nFirst 5 Trades:")
        trade_df = pd.DataFrame([
            {
                "Entry Time": datetime.fromtimestamp(t.entry_time).strftime('%Y-%m-%d %H:%M'),
                "Entry Price": t.entry_price,
                "Exit Reason": t.exit_reason,
                "PnL %": f"{t.pnl_pct:.2%}"
            } for t in simulator.trades[:5]
        ])
        print(trade_df.to_string(index=False))

if __name__ == "__main__":
    import os
    data_file = 'data/btc_price_data.csv'
    if os.path.exists(data_file):
        run_backtest(data_file)
    else:
        print(f"Error: {data_file} not found. Please run data/download_data.py first.")

