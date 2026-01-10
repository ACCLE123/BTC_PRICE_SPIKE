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
    
    spikes = []
    
    print("Running backtest...")
    for _, row in df.iterrows():
        ts = row['timestamp']
        price = row['close']
        
        # 1. Update simulator (check active trade exits)
        simulator.update(ts, price)
        
        # 2. Check for new spikes
        spike = detector.process_price(ts, price)
        if spike:
            spikes.append(spike)
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
    print(f"Total Spikes: {len(spikes)}, Total Trades: {stats['total_trades']}, Win Rate: {stats['win_rate']:.2%}")
    print("="*50)
    
    # --- RECORDING DATA ---
    
    # 1. Record Spike Events
    if spikes:
        spike_df = pd.DataFrame([vars(s) for s in spikes])
        spike_df['timestamp'] = pd.to_datetime(spike_df['timestamp'], unit='s')
        spike_df['baseline_timestamp'] = pd.to_datetime(spike_df['baseline_timestamp'], unit='s')
        spike_df.to_csv('spike_events.csv', index=False)
        print(f"\n[Recorded] All spike events saved to 'spike_events.csv'")

    # 2. Record Trade Records
    if simulator.trades:
        trade_data = []
        for t in simulator.trades:
            trade_data.append({
                "Entry Time": datetime.fromtimestamp(t.entry_time),
                "Entry Price": t.entry_price,
                "Exit Time": datetime.fromtimestamp(t.exit_time) if t.exit_time else None,
                "Exit Price": t.exit_price,
                "Exit Reason": t.exit_reason,
                "PnL %": t.pnl_pct
            })
        trade_df = pd.DataFrame(trade_data)
        trade_df.to_csv('trade_records.csv', index=False)
        print(f"[Recorded] All trade records saved to 'trade_records.csv'")
        
        print("\nSample of last 5 trades:")
        print(trade_df.tail(5).to_string(index=False))

if __name__ == "__main__":
    import os
    data_file = 'data/btc_price_data.csv'
    if os.path.exists(data_file):
        run_backtest(data_file)
    else:
        print(f"Error: {data_file} not found. Please run data/download_data.py first.")

