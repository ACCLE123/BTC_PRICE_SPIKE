from src.models import TradeRecord

class TradeSimulator:
    def __init__(self, tp=0.01, sl=-0.007, max_hold_minutes=180):
        self.tp = tp
        self.sl = sl
        self.max_hold_seconds = max_hold_minutes * 60
        self.active_trade = None
        self.trades = []

    def handle_spike(self, spike_event):
        """Enter a trade if no trade is currently active."""
        if self.active_trade is None:
            self.active_trade = TradeRecord(
                entry_time=spike_event.timestamp,
                entry_price=spike_event.current_price
            )

    def update(self, timestamp, price):
        """Update active trade state based on new price."""
        if not self.active_trade:
            return

        entry_price = self.active_trade.entry_price
        entry_time = self.active_trade.entry_time
        pct_change = (price - entry_price) / entry_price

        # Check exit conditions
        exit_reason = None
        if pct_change >= self.tp:
            exit_reason = "TP"
        elif pct_change <= self.sl:
            exit_reason = "SL"
        elif (timestamp - entry_time) >= self.max_hold_seconds:
            exit_reason = "TIME"

        if exit_reason:
            self.active_trade.exit_time = timestamp
            self.active_trade.exit_price = price
            self.active_trade.exit_reason = exit_reason
            self.active_trade.pnl_pct = pct_change
            self.active_trade.is_active = False
            
            self.trades.append(self.active_trade)
            self.active_trade = None

    def get_stats(self):
        if not self.trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "avg_return": 0,
                "cum_return": 0,
                "max_drawdown": 0
            }

        pnls = [t.pnl_pct for t in self.trades]
        wins = [p for p in pnls if p > 0]
        
        total_trades = len(pnls)
        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        avg_return = sum(pnls) / total_trades
        cum_return = sum(pnls)
        
        # Simple Max Drawdown approximation on the equity curve
        equity = 0
        max_equity = 0
        max_dd = 0
        for p in pnls:
            equity += p
            if equity > max_equity:
                max_equity = equity
            dd = max_equity - equity
            if dd > max_dd:
                max_dd = dd
                
        return {
            "total_trades": total_trades,
            "win_rate": win_rate,
            "avg_return": avg_return,
            "cum_return": cum_return,
            "max_drawdown": max_dd
        }
