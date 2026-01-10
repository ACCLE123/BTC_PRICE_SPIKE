from src.detector import PriceSpikeDetector
from src.simulator import TradeSimulator

def run_mini_test():
    print("--- Starting Mini Test ---")
    detector = PriceSpikeDetector(spike_threshold=0.02, window_minutes=60, cooldown_minutes=300)
    simulator = TradeSimulator(tp=0.01, sl=-0.007, max_hold_minutes=180)
    
    # 1. Simulate Price Spike (90000 -> 92000 in 10 mins)
    prices = [
        (1000, 90000), # Base
        (1600, 92000), # Spike triggered here (+2.22%)
        (1700, 93000), # Should be ignored (cooldown)
        (2000, 91000),
        (4000, 93500),
    ]
    
    print("\n[Step 1] Simulating Spike and Cooldown...")
    for ts, price in prices:
        simulator.update(ts, price)
        spike = detector.process_price(ts, price)
        if spike:
            print(f"  > Spike Detected at {ts}s: Price {price}, Change {spike.pct_change:.2%}")
            simulator.handle_spike(spike)
        
    # 2. Check results
    if simulator.trades:
        t = simulator.trades[0]
        print(f"\n[Step 2] Completed Trade Demo:")
        print(f"  Entry: {t.entry_price} at {t.entry_time}s")
        print(f"  Exit:  {t.exit_price} at {t.exit_time}s")
        print(f"  Reason: {t.exit_reason}")
        print(f"  PnL:    {t.pnl_pct:.2%}")

if __name__ == "__main__":
    run_mini_test()

