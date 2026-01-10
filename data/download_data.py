import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta
from tqdm import tqdm

def download_btc_data():
    exchange = ccxt.binance({
        'enableRateLimit': True,  # Let CCXT handle rate limiting efficiently
    })
    symbol = 'BTC/USDT'
    timeframe = '1m'
    
    # Calculate start time (1 year ago from now)
    now = datetime.utcnow()
    start_time = now - timedelta(days=365)
    since = int(start_time.timestamp() * 1000)
    end_timestamp = int(now.timestamp() * 1000)
    
    # Calculate total expected minutes for progress bar
    total_minutes = int((end_timestamp - since) / (60 * 1000))
    
    all_ohlcv = []
    
    print(f"Starting download for {symbol} {timeframe} from {start_time}...")
    
    with tqdm(total=total_minutes, desc="Downloading BTC data") as pbar:
        while since < end_timestamp:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
                if not ohlcv:
                    break
                
                all_ohlcv.extend(ohlcv)
                
                # Update 'since' to the last timestamp + 1 minute (in ms)
                last_ts = ohlcv[-1][0]
                since = last_ts + 60 * 1000
                
                # Update progress bar by the number of candles fetched
                pbar.update(len(ohlcv))
                
                # Small safety break if we are very close to now
                if len(ohlcv) < 1000 and since >= int(datetime.utcnow().timestamp() * 1000):
                    break
                    
            except Exception as e:
                # print(f"Error fetching data: {e}") # Silent error in tqdm is better, or use tqdm.write
                time.sleep(1)
                continue
            
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = df['timestamp'] / 1000  # Convert to seconds as requested
    
    # Save to CSV
    filename = 'btc_price_data.csv'
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}. Total rows: {len(df)}")

if __name__ == "__main__":
    download_btc_data()

