import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.services.data_fetcher import DataFetcher
from src.services.screening import StockScreener
from src.services.indicators import IndicatorCalculator
from src.services.stock_screener import StockScreener as MultiMarketScreener
MultiMarketScreener = MultiMarketScreener  # Keep alias
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import WatchlistEntry, TradeHorizon
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class PollingEngine:
    """Background job that continuously polls and screens stocks"""

    def __init__(self):
        self.fetcher = DataFetcher()
        self.screener = StockScreener()
        self.multi_market_screener = MultiMarketScreener()
        self.calc = IndicatorCalculator()
        self.ticker_universe = [
            'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN',
            'TCS.BO', 'INFY.BO', 'RELIANCE.NS', 'HDFC.BO'
        ]
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start background polling"""
        self.scheduler.add_job(
            self.scan_intraday,
            'interval',
            seconds=45,
            id='intraday_scan',
            name='Intraday Breakout Scan'
        )

        self.scheduler.add_job(
            self.scan_swing,
            'interval',
            minutes=15,
            id='swing_scan',
            name='Swing Trading Scan'
        )

        self.scheduler.add_job(
            self.scan_long_term,
            'interval',
            hours=1,
            id='longterm_scan',
            name='Long-term Investing Scan'
        )

        self.scheduler.add_job(
            self.scan_eddie_watchlist,
            'interval',
            minutes=30,
            id='eddie_watchlist_scan',
            name="Eddie's Multi-Market Watchlist Scan"
        )

        self.scheduler.start()

    async def scan_intraday(self):
        """Scan for intraday breakouts"""
        print("[POLL] Starting intraday scan...")

        for symbol in self.ticker_universe:
            try:
                ohlcv = await self.fetcher.fetch_ohlcv(symbol, period='5d', interval='1m')
                if ohlcv is None or ohlcv.empty:
                    continue

                candidates = self.screener.screen_intraday_breakout(ohlcv, symbol)

                if candidates:
                    db = SessionLocal()
                    for candidate in candidates:
                        existing = db.query(WatchlistEntry).filter(
                            WatchlistEntry.symbol == symbol,
                            WatchlistEntry.horizon == TradeHorizon.INTRADAY,
                            WatchlistEntry.removed_at == None
                        ).first()

                        if not existing:
                            entry = WatchlistEntry(
                                symbol=symbol,
                                horizon=TradeHorizon.INTRADAY,
                                direction=candidate['direction'],
                                rsi=candidate.get('rsi'),
                                adx=candidate.get('adx'),
                                current_price=candidate['current_price'],
                                volume_ratio=candidate.get('volume_ratio'),
                                breakout_timestamp=datetime.utcnow()
                            )
                            db.add(entry)

                    db.commit()
                    db.close()
                    print(f"  Found {len(candidates)} intraday candidate(s) for {symbol}")

            except Exception as e:
                print(f"  Error scanning {symbol}: {e}")

    async def scan_swing(self):
        """Scan for swing trading opportunities"""
        print("[POLL] Starting swing trading scan...")

        for symbol in self.ticker_universe:
            try:
                ohlcv = await self.fetcher.fetch_ohlcv(symbol, period='30d', interval='1d')
                if ohlcv is None or ohlcv.empty:
                    continue

                candidates = self.screener.screen_swing_trading(ohlcv, symbol)

                if candidates:
                    db = SessionLocal()
                    for candidate in candidates:
                        existing = db.query(WatchlistEntry).filter(
                            WatchlistEntry.symbol == symbol,
                            WatchlistEntry.horizon == TradeHorizon.SWING,
                            WatchlistEntry.removed_at == None
                        ).first()

                        if not existing:
                            entry = WatchlistEntry(
                                symbol=symbol,
                                horizon=TradeHorizon.SWING,
                                direction=candidate['direction'],
                                rsi=candidate.get('rsi'),
                                adx=candidate.get('adx'),
                                current_price=candidate['current_price'],
                                volume_ratio=1.0,
                                breakout_timestamp=datetime.utcnow()
                            )
                            db.add(entry)

                    db.commit()
                    db.close()
                    print(f"  Found {len(candidates)} swing candidate(s) for {symbol}")

            except Exception as e:
                print(f"  Error scanning {symbol}: {e}")

    async def scan_long_term(self):
        """Scan for long-term investing opportunities"""
        print("[POLL] Starting long-term investing scan...")

        for symbol in self.ticker_universe:
            try:
                ohlcv = await self.fetcher.fetch_ohlcv(symbol, period='1y', interval='1d')
                if ohlcv is None or ohlcv.empty:
                    continue

                candidates = self.screener.screen_long_term(ohlcv, symbol)

                if candidates:
                    db = SessionLocal()
                    for candidate in candidates:
                        existing = db.query(WatchlistEntry).filter(
                            WatchlistEntry.symbol == symbol,
                            WatchlistEntry.horizon == TradeHorizon.LONG_TERM,
                            WatchlistEntry.removed_at == None
                        ).first()

                        if not existing:
                            entry = WatchlistEntry(
                                symbol=symbol,
                                horizon=TradeHorizon.LONG_TERM,
                                direction=candidate['direction'],
                                rsi=candidate.get('rsi'),
                                adx=candidate.get('adx'),
                                current_price=candidate['current_price'],
                                volume_ratio=1.0,
                                breakout_timestamp=datetime.utcnow()
                            )
                            db.add(entry)

                    db.commit()
                    db.close()
                    print(f"  Found {len(candidates)} long-term candidate(s) for {symbol}")

            except Exception as e:
                print(f"  Error scanning {symbol}: {e}")

    async def scan_eddie_watchlist(self):
        """Scan S&P 500, Nifty 500, and other indices for Eddie's Watchlist"""
        print("[POLL] Starting Eddie's Multi-Market Watchlist Scan...")

        try:
            results = await self.multi_market_screener.screen_all_markets()

            if results:
                db = SessionLocal()
                added_count = 0

                for result in results:
                    # Check if already in watchlist
                    existing = db.query(WatchlistEntry).filter(
                        WatchlistEntry.symbol == result['symbol'],
                        WatchlistEntry.horizon == TradeHorizon.LONG_TERM,
                        WatchlistEntry.removed_at == None
                    ).first()

                    if not existing:
                        entry = WatchlistEntry(
                            symbol=result['symbol'],
                            horizon=TradeHorizon.LONG_TERM,
                            direction=result['direction'],
                            rsi=result.get('rsi'),
                            adx=result.get('adx'),
                            current_price=result['current_price'],
                            volume_ratio=result.get('volume_ratio', 1.0),
                            breakout_timestamp=datetime.utcnow()
                        )
                        db.add(entry)
                        added_count += 1
                        logger.info(f"✓ Added {result['symbol']} to Eddie's Watchlist")

                db.commit()
                db.close()
                print(f"  ✓ Eddie's Watchlist: Added {added_count} new stock(s)")
            else:
                print("  No stocks matched screening criteria")

        except Exception as e:
            logger.error(f"Error in Eddie's Watchlist scan: {e}")
            print(f"  Error in Eddie's Watchlist scan: {e}")
