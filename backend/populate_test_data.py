import sys
from datetime import datetime, timedelta
sys.path.insert(0, '/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Stock, WatchlistEntry, TradeHorizon, Trade
from src.config import settings

engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)
session = Session()

# Test data
stocks = [
    {'symbol': 'AAPL', 'name': 'Apple Inc', 'market': 'US'},
    {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries', 'market': 'IN'},
    {'symbol': 'GOOGL', 'name': 'Alphabet Inc', 'market': 'US'},
    {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services', 'market': 'IN'},
    {'symbol': 'MSFT', 'name': 'Microsoft', 'market': 'US'},
    {'symbol': 'INFY.NS', 'name': 'Infosys', 'market': 'IN'},
]

trades = [
    {'symbol': 'AAPL', 'horizon': TradeHorizon.SWING, 'direction': 'long', 'entry_price': 150.0, 'exit_price': 155.0, 'stop_loss': 145.0, 'target_price': 160.0, 'quantity': 10, 'status': 'closed', 'pnl': 50.0, 'pnl_percent': 3.33},
    {'symbol': 'RELIANCE.NS', 'horizon': TradeHorizon.INTRADAY, 'direction': 'long', 'entry_price': 2800.0, 'exit_price': 2850.0, 'stop_loss': 2750.0, 'target_price': 2900.0, 'quantity': 5, 'status': 'closed', 'pnl': 250.0, 'pnl_percent': 1.79},
    {'symbol': 'GOOGL', 'horizon': TradeHorizon.SWING, 'direction': 'short', 'entry_price': 140.0, 'exit_price': 135.0, 'stop_loss': 145.0, 'target_price': 130.0, 'quantity': 8, 'status': 'closed', 'pnl': 40.0, 'pnl_percent': 3.57},
    {'symbol': 'MSFT', 'horizon': TradeHorizon.INTRADAY, 'direction': 'long', 'entry_price': 400.0, 'exit_price': 390.0, 'stop_loss': 395.0, 'target_price': 410.0, 'quantity': 5, 'status': 'closed', 'pnl': -50.0, 'pnl_percent': -2.5},
    {'symbol': 'TCS.NS', 'horizon': TradeHorizon.SWING, 'direction': 'long', 'entry_price': 3600.0, 'exit_price': 3750.0, 'stop_loss': 3550.0, 'target_price': 3800.0, 'quantity': 3, 'status': 'closed', 'pnl': 450.0, 'pnl_percent': 4.17},
    {'symbol': 'INFY.NS', 'horizon': TradeHorizon.INTRADAY, 'direction': 'short', 'entry_price': 1500.0, 'exit_price': 1550.0, 'stop_loss': 1520.0, 'target_price': 1450.0, 'quantity': 2, 'status': 'closed', 'pnl': -100.0, 'pnl_percent': -3.33},
]

watchlist_data = [
    {'symbol': 'AAPL', 'horizon': TradeHorizon.INTRADAY, 'direction': 'long', 'price': 185.50, 'rsi': 65.2, 'adx': 28.5, 'momentum': 2.3, 'volume_ratio': 1.8},
    {'symbol': 'RELIANCE.NS', 'horizon': TradeHorizon.INTRADAY, 'direction': 'long', 'price': 2850.25, 'rsi': 72.1, 'adx': 32.1, 'momentum': 3.1, 'volume_ratio': 2.1},
    {'symbol': 'GOOGL', 'horizon': TradeHorizon.SWING, 'direction': 'long', 'price': 140.75, 'rsi': 58.3, 'adx': 24.2, 'momentum': 1.5, 'volume_ratio': 1.3},
    {'symbol': 'TCS.NS', 'horizon': TradeHorizon.INTRADAY, 'direction': 'short', 'price': 3650.10, 'rsi': 28.5, 'adx': 26.7, 'momentum': -2.1, 'volume_ratio': 1.9},
    {'symbol': 'MSFT', 'horizon': TradeHorizon.SWING, 'direction': 'short', 'price': 420.30, 'rsi': 35.2, 'adx': 22.3, 'momentum': -1.8, 'volume_ratio': 1.2},
    {'symbol': 'INFY.NS', 'horizon': TradeHorizon.INTRADAY, 'direction': 'long', 'price': 1540.50, 'rsi': 68.9, 'adx': 29.5, 'momentum': 2.7, 'volume_ratio': 1.7},
]

try:
    # Clear existing data
    session.query(Trade).delete()
    session.query(WatchlistEntry).delete()
    session.query(Stock).delete()

    # Add stocks
    for s in stocks:
        stock = Stock(symbol=s['symbol'], name=s['name'], market=s['market'])
        session.add(stock)

    session.commit()

    # Add watchlist entries
    now = datetime.utcnow()
    for i, w in enumerate(watchlist_data):
        entry = WatchlistEntry(
            symbol=w['symbol'],
            horizon=w['horizon'],
            direction=w['direction'],
            current_price=w['price'],
            rsi=w['rsi'],
            adx=w['adx'],
            momentum=w['momentum'],
            volume_ratio=w['volume_ratio'],
            breakout_timestamp=now - timedelta(minutes=i*5),
            added_at=now - timedelta(minutes=i*5)
        )
        session.add(entry)

    # Add trades
    for i, t in enumerate(trades):
        trade = Trade(
            symbol=t['symbol'],
            horizon=t['horizon'],
            direction=t['direction'],
            entry_price=t['entry_price'],
            exit_price=t['exit_price'],
            stop_loss=t['stop_loss'],
            target_price=t['target_price'],
            quantity=t['quantity'],
            status=t['status'],
            entry_time=now - timedelta(days=i+1),
            exit_time=now - timedelta(days=i, hours=6) if t['status'] == 'closed' else None,
            pnl=t['pnl'],
            pnl_percent=t['pnl_percent']
        )
        session.add(trade)

    session.commit()
    print("✓ Test data populated successfully")
    print(f"  - {len(stocks)} stocks added")
    print(f"  - {len(watchlist_data)} watchlist entries added")
    print(f"  - {len(trades)} trades added")

except Exception as e:
    session.rollback()
    print(f"✗ Error: {e}")
finally:
    session.close()
