from dataclasses import dataclass
from typing import Optional

@dataclass
class SpikeEvent:
    timestamp: float
    baseline_timestamp: float
    baseline_price: float
    current_price: float
    pct_change: float

@dataclass
class TradeRecord:
    entry_time: float
    entry_price: float
    exit_time: Optional[float] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None  # TP, SL, TIME
    pnl_pct: Optional[float] = None
    is_active: bool = True

