import asyncio
import yfinance as yf
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

class YahooFinanceDashboard:
    """Yahoo Finance-powered dashboards for watchlist analytics - No API key needed!"""

    def __init__(self):
        self.base_url = "https://news.google.com/rss"

    async def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive company profile from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = await asyncio.to_thread(lambda: ticker.info)

            return {
                'symbol': symbol,
                'name': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'website': info.get('website'),
                'country': info.get('country'),
                'employees': info.get('fullTimeEmployees'),
            }
        except Exception as e:
            print(f"Error fetching company profile for {symbol}: {e}")
            return None

    async def get_real_time_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = await asyncio.to_thread(lambda: ticker.info)
            hist = await asyncio.to_thread(lambda: ticker.history(period='1d'))

            if hist.empty:
                return None

            current = info.get('currentPrice', hist['Close'].iloc[-1])
            previous_close = info.get('previousClose', hist['Close'].iloc[0])
            change = current - previous_close
            change_pct = (change / previous_close * 100) if previous_close else 0

            return {
                'current_price': float(current),
                'previous_close': float(previous_close),
                'change': float(change),
                'change_percent': float(change_pct),
                'day_high': float(info.get('dayHigh', hist['High'].max())),
                'day_low': float(info.get('dayLow', hist['Low'].min())),
                'open': float(info.get('open', hist['Open'].iloc[0])),
                'volume': int(info.get('volume', hist['Volume'].iloc[-1])),
                'bid': float(info.get('bid', current)),
                'ask': float(info.get('ask', current)),
                'market_cap': info.get('marketCap'),
            }
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    async def get_company_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """Get latest company news"""
        try:
            ticker = yf.Ticker(symbol)
            news_list = await asyncio.to_thread(lambda: ticker.news[:limit])

            return [
                {
                    'title': news.get('title'),
                    'summary': news.get('summary', ''),
                    'source': news.get('source'),
                    'url': news.get('link'),
                    'timestamp': news.get('providerPublishTime', 0),
                    'sentiment': self._classify_sentiment(news.get('title', ''))
                }
                for news in news_list if news
            ]
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    async def get_key_statistics(self, symbol: str) -> Optional[Dict]:
        """Get key financial statistics"""
        try:
            ticker = yf.Ticker(symbol)
            info = await asyncio.to_thread(lambda: ticker.info)

            return {
                'symbol': symbol,
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'profit_margin': info.get('profitMargins'),
                'eps': info.get('trailingEps')
            }
        except Exception as e:
            print(f"Error fetching statistics for {symbol}: {e}")
            return None

    async def get_indian_news(self, limit: int = 10) -> List[Dict]:
        """Fetch Indian market news from Google News RSS"""
        try:
            url = f"{self.base_url}/search?q=india+stock+market+NSE&hl=en-IN&gl=IN&ceid=IN:en"
            feed = await asyncio.to_thread(feedparser.parse, url)

            news = []
            for entry in feed.entries[:limit]:
                news.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'source': 'Google News',
                    'region': 'India',
                    'sentiment': self._classify_sentiment(entry.title)
                })
            return news
        except Exception as e:
            print(f"Error fetching Indian news: {e}")
            return []

    async def get_global_news(self, limit: int = 10) -> List[Dict]:
        """Fetch global market news from Google News RSS"""
        try:
            url = f"{self.base_url}/search?q=stock+market+nasdaq+sp500&hl=en&gl=US&ceid=US:en"
            feed = await asyncio.to_thread(feedparser.parse, url)

            news = []
            for entry in feed.entries[:limit]:
                news.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'source': 'Google News',
                    'region': 'Global',
                    'sentiment': self._classify_sentiment(entry.title)
                })
            return news
        except Exception as e:
            print(f"Error fetching global news: {e}")
            return []

    async def get_watchlist_dashboard(self, symbols: List[str]) -> Dict:
        """Get comprehensive dashboard data for multiple watchlist symbols"""
        tasks = []
        for symbol in symbols:
            tasks.append(self._get_symbol_dashboard_data(symbol))

        results = await asyncio.gather(*tasks)
        return {
            'stocks': results,
            'generated_at': datetime.now().isoformat()
        }

    async def _get_symbol_dashboard_data(self, symbol: str) -> Dict:
        """Get all dashboard data for a single symbol"""
        try:
            quote_task = self.get_real_time_quote(symbol)
            profile_task = self.get_company_profile(symbol)
            news_task = self.get_company_news(symbol, limit=3)
            stats_task = self.get_key_statistics(symbol)

            quote, profile, news, stats = await asyncio.gather(
                quote_task, profile_task, news_task, stats_task
            )

            return {
                'symbol': symbol,
                'quote': quote,
                'profile': profile,
                'news': news,
                'statistics': stats
            }
        except Exception as e:
            print(f"Error getting dashboard for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def _classify_sentiment(self, text: str) -> str:
        """Simple sentiment classification based on keywords"""
        text_lower = text.lower()

        positive_words = ['surge', 'rally', 'beat', 'outperform', 'gain', 'up', 'rise', 'strong', 'bullish', 'jump', 'soar']
        negative_words = ['drop', 'crash', 'miss', 'decline', 'fall', 'down', 'weak', 'bearish', 'loss', 'plunge']

        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)

        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        return 'neutral'

# Add simple caching
from functools import lru_cache
from datetime import datetime, timedelta

class CachedData:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 minutes
    
    def get(self, key):
        if key in self.cache:
            if datetime.now() - self.cache_time[key] < timedelta(seconds=self.cache_duration):
                return self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = value
        self.cache_time[key] = datetime.now()

# Global cache instance
_cache = CachedData()
