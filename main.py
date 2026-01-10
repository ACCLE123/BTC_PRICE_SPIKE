import pandas as pd
from src.detector import PriceSpikeDetector
from src.simulator import TradeSimulator
from datetime import datetime

def calculate_buy_and_hold_stats(df):
    first_price = df.iloc[0]['close']
    last_price = df.iloc[-1]['close']
    
    # 1. Total Return
    total_return = (last_price - first_price) / first_price
    
    # 2. Max Drawdown for Buy and Hold
    prices = df['close'].values
    max_equity = prices[0]
    max_dd = 0
    
    for price in prices:
        if price > max_equity:
            max_equity = price
        dd = (max_equity - price) / max_equity
        if dd > max_dd:
            max_dd = dd
            
    calmar = total_return / max_dd if max_dd > 0 else float('inf')
    
    return {
        "return": total_return,
        "max_dd": max_dd,
        "calmar": calmar
    }

def run_backtest(csv_path):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Ensure data is sorted by timestamp
    df = df.sort_values('timestamp')
    
    # Calculate Buy & Hold stats
    bh_stats = calculate_buy_and_hold_stats(df)
    
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
            
    # Final stats for strategy
    stats = simulator.get_stats()
    strategy_calmar = stats['cum_return'] / stats['max_drawdown'] if stats['max_drawdown'] > 0 else 0
    
    print("\n" + "="*50)
    print(f"{'Metric':<20} | {'Strategy':<12} | {'Buy & Hold':<12}")
    print("-" * 50)
    print(f"{'Cumulative Return':<20} | {stats['cum_return']:>11.2%} | {bh_stats['return']:>11.2%}")
    print(f"{'Max Drawdown':<20} | {stats['max_drawdown']:>11.2%} | {bh_stats['max_dd']:>11.2%}")
    print(f"{'Calmar Ratio':<20} | {strategy_calmar:>11.2f} | {bh_stats['calmar']:>11.2f}")
    print("-" * 50)
    print(f"Total Spikes: {spike_count}, Total Trades: {stats['total_trades']}, Win Rate: {stats['win_rate']:.2%}")
    print("="*50)
    
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

