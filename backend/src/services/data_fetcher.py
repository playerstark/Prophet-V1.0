import asyncio
import yfinance
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from src.config import settings
from src.services.twelvedata_provider import TwelveDataProvider

class DataFetcher:
    """Fetch OHLCV data and news from multiple sources"""

    def __init__(self):
        self.twelvedata = TwelveDataProvider()

    async def fetch_ohlcv(self, symbol: str, period: str = '60d', interval: str = '1d') -> Optional[pd.DataFrame]:
        """Fetch OHLCV data - Twelve Data > Finnhub > yfinance"""

        # Try Twelve Data first (premium, most reliable)
        twelvedata_data = await self.twelvedata.fetch_ohlcv(symbol, interval, period)
        if twelvedata_data is not None:
            print(f"✓ Fetched {symbol} from Twelve Data (premium)")
            return twelvedata_data

        # Fall back to Finnhub
        print(f"Twelve Data failed for {symbol}, falling back to Finnhub...")
        finnhub_data = await self._fetch_from_finnhub(symbol, interval)
        if finnhub_data is not None:
            print(f"✓ Fetched {symbol} from Finnhub")
            return finnhub_data

        # Final fallback to yfinance
        print(f"Finnhub failed for {symbol}, falling back to yfinance...")
        yfinance_data = await self._fetch_from_yfinance(symbol, period, interval)
        if yfinance_data is not None:
            print(f"✓ Fetched {symbol} from yfinance (free tier)")
            return yfinance_data

        print(f"✗ Failed to fetch {symbol} from all sources")
        return None

    async def _fetch_from_finnhub(self, symbol: str, interval: str = '1d') -> Optional[pd.DataFrame]:
        """Fetch from Finnhub - Real-time & Historical data"""
        try:
            if not settings.finnhub_api_key:
                return None

            url = "https://finnhub.io/api/v1/quote"

            # Get current quote for latest price
            quote_params = {
                "symbol": symbol,
                "token": settings.finnhub_api_key
            }

            quote_response = await asyncio.to_thread(
                requests.get,
                url,
                params=quote_params,
                timeout=10
            )

            if quote_response.status_code != 200:
                return None

            quote_data = quote_response.json()

            # Get candle data
            candle_url = "https://finnhub.io/api/v1/stock/candle"

            # Determine resolution based on interval
            resolution_map = {'1m': '1', '5m': '5', '15m': '15', '30m': '30', '60m': '60', '1d': 'D', '1wk': 'W', '1mo': 'M'}
            resolution = resolution_map.get(interval, 'D')

            from datetime import datetime, timedelta
            now = int(datetime.now().timestamp())

            # Calculate from date (60 days ago for daily)
            if resolution == 'D':
                from_date = now - (60 * 24 * 3600)
            else:
                from_date = now - (30 * 24 * 3600)

            candle_params = {
                "symbol": symbol,
                "resolution": resolution,
                "from": from_date,
                "to": now,
                "token": settings.finnhub_api_key
            }

            candle_response = await asyncio.to_thread(
                requests.get,
                candle_url,
                params=candle_params,
                timeout=10
            )

            if candle_response.status_code == 200:
                candle_data = candle_response.json()

                if 'o' in candle_data and len(candle_data['o']) > 0:
                    df = pd.DataFrame({
                        'Open': candle_data.get('o', []),
                        'High': candle_data.get('h', []),
                        'Low': candle_data.get('l', []),
                        'Close': candle_data.get('c', []),
                        'Volume': candle_data.get('v', [])
                    })

                    if not df.empty:
                        return df

            return None
        except Exception as e:
            print(f"Finnhub error for {symbol}: {e}")
            return None

    async def _fetch_from_yfinance(self, symbol: str, period: str = '60d', interval: str = '1d') -> Optional[pd.DataFrame]:
        """Fetch from yfinance (fallback)"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: yfinance.download(
                    symbol,
                    period=period,
                    interval=interval,
                    progress=False
                )
            )

            if data is not None and not data.empty:
                # Handle MultiIndex columns from newer yfinance versions
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                return data

            return None
        except Exception as e:
            print(f"yfinance error for {symbol}: {e}")
            return None

    async def fetch_news_finnhub(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Fetch US company news from Finnhub"""
        if not settings.finnhub_api_key:
            return []

        try:
            url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&limit={limit}&token={settings.finnhub_api_key}"
            response = await asyncio.to_thread(requests.get, url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching Finnhub news: {e}")
            return []

    async def fetch_news_google_rss(self, ticker: str, limit: int = 10) -> List[Dict]:
        """Fetch news from Google News RSS (Indian + geopolitical coverage)"""
        try:
            url = f"https://news.google.com/rss/search?q={ticker}&hl=en-IN&gl=IN&ceid=IN:en"
            feed = await asyncio.to_thread(feedparser.parse, url)

            news = []
            for entry in feed.entries[:limit]:
                news.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'summary': entry.get('summary', '')
                })
            return news
        except Exception as e:
            print(f"Error fetching Google News RSS: {e}")
            return []

    async def fetch_earnings_calendar(self, market: str = 'US') -> List[Dict]:
        """Fetch upcoming earnings using Finnhub"""
        if not settings.finnhub_api_key:
            return []

        try:
            today = datetime.now().date()
            from_date = today
            to_date = today + timedelta(days=30)

            url = f"https://finnhub.io/api/v1/calendar/earnings?from={from_date}&to={to_date}&token={settings.finnhub_api_key}"
            response = await asyncio.to_thread(requests.get, url, timeout=5)
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching earnings calendar: {e}")
            return []
