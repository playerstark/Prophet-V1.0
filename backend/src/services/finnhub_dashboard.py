import asyncio
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.config import settings

class FinnhubDashboard:
    """Finnhub-powered dashboards for watchlist analytics"""

    def __init__(self):
        self.api_key = settings.finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"

    async def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive company profile"""
        try:
            url = f"{self.base_url}/stock/profile2"
            params = {"symbol": symbol, "token": self.api_key}

            response = await asyncio.to_thread(
                requests.get,
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': data.get('ticker'),
                    'name': data.get('name'),
                    'sector': data.get('finnhubIndustry'),
                    'market_cap': data.get('marketCapitalization'),
                    'pe_ratio': data.get('peRatio'),
                    'dividend_yield': data.get('dividendYield'),
                    'website': data.get('weburl'),
                    'logo': data.get('logo'),
                    'country': data.get('country'),
                    'ipo_date': data.get('ipo')
                }
            return None
        except Exception as e:
            print(f"Error fetching company profile for {symbol}: {e}")
            return None

    async def get_real_time_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote data"""
        try:
            url = f"{self.base_url}/quote"
            params = {"symbol": symbol, "token": self.api_key}

            response = await asyncio.to_thread(
                requests.get,
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                current = data.get('c', 0)
                previous_close = data.get('pc', current)
                change = current - previous_close
                change_pct = (change / previous_close * 100) if previous_close else 0

                return {
                    'current_price': current,
                    'previous_close': previous_close,
                    'change': change,
                    'change_percent': change_pct,
                    'day_high': data.get('h'),
                    'day_low': data.get('l'),
                    'open': data.get('o'),
                    'timestamp': data.get('t'),
                    'volume': data.get('v'),
                    'bid': data.get('bid'),
                    'ask': data.get('ask'),
                    'bid_size': data.get('bidSize'),
                    'ask_size': data.get('askSize')
                }
            return None
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    async def get_company_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """Get latest company news with sentiment indicators"""
        try:
            url = f"{self.base_url}/company-news"
            params = {"symbol": symbol, "limit": limit, "token": self.api_key}

            response = await asyncio.to_thread(
                requests.get,
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                news_list = response.json()
                return [
                    {
                        'title': news.get('headline'),
                        'summary': news.get('summary'),
                        'source': news.get('source'),
                        'url': news.get('url'),
                        'image': news.get('image'),
                        'timestamp': news.get('datetime'),
                        'category': news.get('category'),
                        'sentiment': self._classify_sentiment(news.get('headline', ''))
                    }
                    for news in news_list
                ]
            return []
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    async def get_peers(self, symbol: str) -> List[str]:
        """Get competitor/peer stocks"""
        try:
            url = f"{self.base_url}/stock/peers"
            params = {"symbol": symbol, "token": self.api_key}

            response = await asyncio.to_thread(
                requests.get,
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching peers for {symbol}: {e}")
            return []

    async def get_earnings_surprises(self, symbol: str) -> Optional[Dict]:
        """Get earnings surprise data"""
        try:
            url = f"{self.base_url}/stock/earnings"
            params = {"symbol": symbol, "token": self.api_key}

            response = await asyncio.to_thread(
                requests.get,
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                earnings = response.json()
                if earnings:
                    latest = earnings[0]
                    return {
                        'report_date': latest.get('reportDate'),
                        'estimated_eps': latest.get('epsEstimate'),
                        'actual_eps': latest.get('epsActual'),
                        'eps_surprise': latest.get('epsSurprise'),
                        'eps_surprise_pct': latest.get('epsSurprisePercent')
                    }
            return None
        except Exception as e:
            print(f"Error fetching earnings for {symbol}: {e}")
            return None

    async def get_insider_trades(self, symbol: str, limit: int = 5) -> List[Dict]:
        """Get insider trading data"""
        try:
            url = f"{self.base_url}/stock/insider-trades"
            params = {"symbol": symbol, "limit": limit, "token": self.api_key}

            response = await asyncio.to_thread(
                requests.get,
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                trades = response.json().get('data', [])
                return [
                    {
                        'name': trade.get('name'),
                        'title': trade.get('title'),
                        'share': trade.get('share'),
                        'change': trade.get('change'),
                        'filingDate': trade.get('filingDate'),
                        'transactionDate': trade.get('transactionDate')
                    }
                    for trade in trades
                ]
            return []
        except Exception as e:
            print(f"Error fetching insider trades for {symbol}: {e}")
            return []

    async def get_recommendation_trends(self, symbol: str) -> List[Dict]:
        """Get analyst recommendation trends"""
        try:
            url = f"{self.base_url}/stock/recommendation"
            params = {"symbol": symbol, "token": self.api_key}

            response = await asyncio.to_thread(
                requests.get,
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                trends = response.json()
                return [
                    {
                        'period': trend.get('period'),
                        'strong_buy': trend.get('strongBuy'),
                        'buy': trend.get('buy'),
                        'hold': trend.get('hold'),
                        'sell': trend.get('sell'),
                        'strong_sell': trend.get('strongSell')
                    }
                    for trend in trends[:4]
                ]
            return []
        except Exception as e:
            print(f"Error fetching recommendations for {symbol}: {e}")
            return []

    async def get_price_target(self, symbol: str) -> Optional[Dict]:
        """Get analyst price targets"""
        try:
            url = f"{self.base_url}/stock/price-target"
            params = {"symbol": symbol, "token": self.api_key}

            response = await asyncio.to_thread(
                requests.get,
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'target_high': data.get('targetHigh'),
                    'target_low': data.get('targetLow'),
                    'target_mean': data.get('targetMean'),
                    'target_median': data.get('targetMedian'),
                    'recommendation': data.get('recommendation'),
                    'number_of_analysts': data.get('numberOfAnalysts')
                }
            return None
        except Exception as e:
            print(f"Error fetching price target for {symbol}: {e}")
            return None

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
            target_task = self.get_price_target(symbol)
            earnings_task = self.get_earnings_surprises(symbol)

            quote, profile, news, target, earnings = await asyncio.gather(
                quote_task, profile_task, news_task, target_task, earnings_task
            )

            return {
                'symbol': symbol,
                'quote': quote,
                'profile': profile,
                'news': news,
                'price_target': target,
                'earnings': earnings
            }
        except Exception as e:
            print(f"Error getting dashboard for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def _classify_sentiment(self, text: str) -> str:
        """Simple sentiment classification based on keywords"""
        text_lower = text.lower()

        positive_words = ['surge', 'rally', 'beat', 'outperform', 'gain', 'up', 'rise', 'strong', 'bullish']
        negative_words = ['drop', 'crash', 'miss', 'decline', 'fall', 'down', 'weak', 'bearish', 'loss']

        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)

        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        return 'neutral'
