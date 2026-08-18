"""Stock screening service for multi-market analysis"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, time
import asyncio
import logging

logger = logging.getLogger(__name__)


class StockScreener:
    """Screen stocks from major indices based on technical criteria"""

    # Index tickers and their constituent lists
    INDICES = {
        'SP500': '^GSPC',  # S&P 500
        'RUSSELL2000': '^RUT',  # Small cap
        'NIFTY500': '^NSEI',  # India Nifty 500
        'NIFTYMIDCAP': '^NSEMDX',  # India MidCap
        'NIFTYSMALLCAP': '^NSMIDX',  # India SmallCap
    }

    # Popular stocks from each index for initial screening
    SP500_SAMPLES = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
                     'NFLX', 'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'KO']

    NIFTY500_SAMPLES = ['TCS', 'INFY', 'RELIANCE', 'HDFC', 'ICICI', 'SBIN',
                        'BAJAJ-AUTO', 'MARUTI', 'LT', 'WIPRO', 'SUNPHARMA',
                        'ASIAPAINT', 'BPCL', 'COALINDIA', 'INDIGO']

    def __init__(self):
        self.rsi_lower = 30
        self.rsi_upper = 70
        self.adx_threshold = 20
        self.volume_multiplier = 1.2
        self.momentum_threshold = 0

    def is_us_market_open(self) -> bool:
        """Check if US market is currently open (9:30 AM - 4:00 PM EST)"""
        from datetime import datetime
        import pytz

        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)

        # Check if weekday (Mon-Fri)
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False

        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now <= market_close

    def is_india_market_open(self) -> bool:
        """Check if India market is currently open (9:15 AM - 3:30 PM IST)"""
        from datetime import datetime
        import pytz

        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)

        # Check if weekday (Mon-Fri)
        if now.weekday() >= 5:
            return False

        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

        return market_open <= now <= market_close

    def get_active_markets(self) -> List[str]:
        """Get list of currently active markets"""
        active = []
        if self.is_us_market_open():
            active.append('US')
        if self.is_india_market_open():
            active.append('INDIA')
        return active if active else ['US', 'INDIA']  # Default to both if outside hours

    async def fetch_stock_data(self, symbol: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for a stock"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: yf.download(symbol, period=period, progress=False)
            )

            if data is None or data.empty:
                return None

            # Handle MultiIndex columns from newer yfinance versions
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            return data
        except Exception as e:
            logger.warning(f"Failed to fetch {symbol}: {e}")
            return None

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_adx(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ADX indicator"""
        high = data['High']
        low = data['Low']
        close = data['Close']

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        # Directional Movement
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)

        di_diff = abs(plus_di - minus_di)
        di_sum = plus_di + minus_di
        dx = 100 * di_diff / di_sum
        adx = dx.rolling(period).mean()

        return adx

    def calculate_momentum(self, prices: pd.Series, period: int = 10) -> pd.Series:
        """Calculate momentum indicator"""
        return prices - prices.shift(period)

    def screen_stock(self, symbol: str, data: pd.DataFrame, market: str) -> Optional[Dict]:
        """Screen a single stock against criteria"""
        try:
            if data is None or len(data) < 30:
                return None

            close = data['Close']
            volume = data['Volume']

            # Calculate indicators
            rsi = self.calculate_rsi(close)
            adx = self.calculate_adx(data)
            momentum = self.calculate_momentum(close)

            # Get current values
            current_rsi = rsi.iloc[-1]
            current_adx = adx.iloc[-1]
            current_momentum = momentum.iloc[-1]
            current_price = close.iloc[-1]
            current_volume = volume.iloc[-1]
            avg_volume = volume.rolling(20).mean().iloc[-1]

            # Skip if NaN
            if pd.isna(current_rsi) or pd.isna(current_adx):
                return None

            # Check criteria
            rsi_in_range = self.rsi_lower <= current_rsi <= self.rsi_upper
            adx_confirmed = current_adx > self.adx_threshold
            volume_confirmed = current_volume > (avg_volume * self.volume_multiplier)

            if not (rsi_in_range and adx_confirmed and volume_confirmed):
                return None

            # Determine direction based on momentum
            direction = 'BULLISH' if current_momentum > self.momentum_threshold else 'BEARISH'

            return {
                'symbol': symbol,
                'market': market,
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'momentum': float(current_momentum),
                'volume_ratio': float(current_volume / avg_volume) if avg_volume > 0 else 0,
                'direction': direction,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.warning(f"Error screening {symbol}: {e}")
            return None

    async def screen_market_stocks(self, market: str = 'US') -> List[Dict]:
        """Screen all stocks in a market"""
        symbols = self.SP500_SAMPLES if market == 'US' else self.NIFTY500_SAMPLES
        results = []

        for symbol in symbols:
            # Add market suffix for India stocks
            ticker = f"{symbol}.NS" if market == 'INDIA' else symbol

            data = await self.fetch_stock_data(ticker)
            if data is not None:
                screen_result = self.screen_stock(symbol, data, market)
                if screen_result:
                    results.append(screen_result)
                    logger.info(f"✓ {symbol} ({market}) passed screening: RSI={screen_result['rsi']:.1f}, ADX={screen_result['adx']:.1f}")

            await asyncio.sleep(0.1)  # Rate limiting

        return results

    async def screen_all_markets(self) -> List[Dict]:
        """Screen stocks across all active markets"""
        active_markets = self.get_active_markets()
        all_results = []

        for market in active_markets:
            logger.info(f"Screening {market} market...")
            results = await self.screen_market_stocks(market)
            all_results.extend(results)

        return all_results


async def run_screening():
    """Run the screening and return results"""
    screener = StockScreener()
    return await screener.screen_all_markets()
