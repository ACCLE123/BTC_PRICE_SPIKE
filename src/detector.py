from collections import deque
from src.models import SpikeEvent

class PriceSpikeDetector:
    def __init__(self, spike_threshold=0.02, window_minutes=60, cooldown_minutes=300):
        self.spike_threshold = spike_threshold
        self.window_seconds = window_minutes * 60
        self.cooldown_seconds = cooldown_minutes * 60
        
        self.window = deque()  # Stores (timestamp, price)
        self.last_spike_time = -float('inf')
        
    def process_price(self, timestamp, price):
        """
        Process a new price update and return a SpikeEvent if triggered.
        """
        # 1. Add new data point
        self.window.append((timestamp, price))
        
        # 2. Remove old data points outside the window
        while self.window and (timestamp - self.window[0][0]) > self.window_seconds:
            self.window.popleft()
            
        # 3. Check cooldown
        if timestamp < self.last_spike_time + self.cooldown_seconds:
            return None
            
        # 4. Find baseline (minimum price in current window)
        # Note: For very large datasets, a monotonic queue could optimize this to O(1),
        # but with a 60-item window (if 1min data), min() is perfectly efficient.
        baseline_ts, baseline_price = min(self.window, key=lambda x: x[1])
        
        # 5. Check spike condition
        if baseline_price > 0:
            pct_change = (price - baseline_price) / baseline_price
            if pct_change >= self.spike_threshold:
                self.last_spike_time = timestamp
                return SpikeEvent(
                    timestamp=timestamp,
                    baseline_timestamp=baseline_ts,
                    baseline_price=baseline_price,
                    current_price=price,
                    pct_change=pct_change
                )
                
        return None

