"""Seed Eddie's watchlist with demo data"""
import sys
sys.path.insert(0, '/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0 (2)/backend')

from src.database import SessionLocal
from src.models import WatchlistEntry, TradeHorizon
from datetime import datetime

# Demo stocks that pass the screening criteria
DEMO_STOCKS = [
    {'symbol': 'AAPL', 'market': 'US', 'direction': 'BULLISH', 'rsi': 65, 'adx': 28, 'momentum': 2.5, 'price': 185.50},
    {'symbol': 'MSFT', 'market': 'US', 'direction': 'BULLISH', 'rsi': 58, 'adx': 35, 'momentum': 1.8, 'price': 420.75},
    {'symbol': 'TSLA', 'market': 'US', 'direction': 'BEARISH', 'rsi': 42, 'adx': 26, 'momentum': -1.2, 'price': 245.30},
    {'symbol': 'GOOGL', 'market': 'US', 'direction': 'BULLISH', 'rsi': 62, 'adx': 22, 'momentum': 3.1, 'price': 155.80},
    {'symbol': 'NVDA', 'market': 'US', 'direction': 'BULLISH', 'rsi': 68, 'adx': 32, 'momentum': 4.2, 'price': 875.40},
    {'symbol': 'TCS', 'market': 'INDIA', 'direction': 'BULLISH', 'rsi': 55, 'adx': 24, 'momentum': 0.8, 'price': 4125.50},
    {'symbol': 'INFY', 'market': 'INDIA', 'direction': 'BULLISH', 'rsi': 60, 'adx': 28, 'momentum': 1.5, 'price': 1845.25},
    {'symbol': 'RELIANCE', 'market': 'INDIA', 'direction': 'BEARISH', 'rsi': 38, 'adx': 25, 'momentum': -2.1, 'price': 3025.80},
    {'symbol': 'HDFC', 'market': 'INDIA', 'direction': 'BULLISH', 'rsi': 64, 'adx': 30, 'momentum': 2.3, 'price': 2750.40},
    {'symbol': 'ICICI', 'market': 'INDIA', 'direction': 'BULLISH', 'rsi': 52, 'adx': 21, 'momentum': 0.6, 'price': 1125.15},
]

def seed():
    db = SessionLocal()

    # Clear existing long-term entries
    db.query(WatchlistEntry).filter(
        WatchlistEntry.horizon == TradeHorizon.LONG_TERM,
        WatchlistEntry.removed_at == None
    ).delete()

    # Add demo stocks
    for stock in DEMO_STOCKS:
        entry = WatchlistEntry(
            symbol=stock['symbol'],
            horizon=TradeHorizon.LONG_TERM,
            direction=stock['direction'],
            rsi=stock['rsi'],
            adx=stock['adx'],
            momentum=stock['momentum'],
            current_price=stock['price'],
            volume_ratio=1.3,
            breakout_timestamp=datetime.utcnow()
        )
        db.add(entry)
        print(f"✓ Added {stock['symbol']} ({stock['market']}) - {stock['direction']}")

    db.commit()
    db.close()
    print(f"\n✓ Seeded {len(DEMO_STOCKS)} stocks to Eddie's Watchlist")

if __name__ == '__main__':
    seed()
