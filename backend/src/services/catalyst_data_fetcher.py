from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from src.config import settings
import pytz


class CatalystDataFetcher:
    """
    Fetches catalyst data from multiple sources:
    - Finnhub API (news, company events)
    - Earnings calendar
    - Sector performance data
    """

    def __init__(self):
        self.finnhub_key = settings.finnhub_api_key
        self.finnhub_base_url = "https://finnhub.io/api/v1"

    def parse_news_to_catalyst(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw news article to catalyst format

        Args:
            news: Raw news dict from API

        Returns:
            Catalyst dict
        """
        timestamp = news.get('datetime', 0)
        news_date = datetime.fromtimestamp(timestamp, tz=pytz.UTC)

        return {
            'symbol': news.get('symbol', ''),
            'type': 'news_event',
            'title': news.get('headline', ''),
            'description': news.get('summary', ''),
            'event_date': news_date,
            'source': 'finnhub',
            'source_url': news.get('url') or '',
            'source_id': str(news.get('id', ''))
        }

    def parse_earnings_to_catalyst(self, earnings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert earnings event to catalyst format

        Args:
            earnings: Earnings event dict

        Returns:
            Catalyst dict
        """
        date_str = earnings.get('date', '')
        try:
            event_date = datetime.fromisoformat(date_str).replace(tzinfo=pytz.UTC)
        except:
            event_date = datetime.now(pytz.UTC)

        quarter = earnings.get('quarter', 'Earnings')

        return {
            'symbol': earnings.get('symbol', ''),
            'type': 'earnings',
            'title': f"{earnings.get('symbol')} Reports {quarter} Earnings",
            'description': 'Earnings announcement scheduled',
            'event_date': event_date,
            'source': 'finnhub_earnings',
            'source_id': earnings.get('symbol', '')
        }

    async def fetch_company_news(self, symbol: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch company news from Finnhub

        Args:
            symbol: Stock symbol
            days_back: Number of days to look back

        Returns:
            List of news articles
        """
        import aiohttp

        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')

        params = {
            'symbol': symbol,
            'from': from_date,
            'to': to_date,
            'token': self.finnhub_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.finnhub_base_url}/company-news', params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return []
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    async def fetch_earnings_calendar(self, days_forward: int = 90) -> List[Dict[str, Any]]:
        """
        Fetch earnings calendar

        Args:
            days_forward: Number of days forward to look

        Returns:
            List of earnings events
        """
        import aiohttp

        from_date = datetime.now().strftime('%Y-%m-%d')
        to_date = (datetime.now() + timedelta(days=days_forward)).strftime('%Y-%m-%d')

        params = {
            'from': from_date,
            'to': to_date,
            'token': self.finnhub_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.finnhub_base_url}/calendar/earnings', params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('earningsCalendar', [])
                    else:
                        return []
        except Exception as e:
            print(f"Error fetching earnings calendar: {e}")
            return []

    async def fetch_sector_performance(self) -> Dict[str, Dict[str, float]]:
        """
        Fetch sector performance (which sectors are strongest)

        Returns:
            Dict mapping sector to performance data
        """
        import aiohttp

        params = {'token': self.finnhub_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.finnhub_base_url}/stock/sector-performance', params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data if isinstance(data, dict) else {}
                    else:
                        return {}
        except Exception as e:
            print(f"Error fetching sector performance: {e}")
            return {}
