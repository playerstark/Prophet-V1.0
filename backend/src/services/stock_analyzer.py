import asyncio
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import feedparser

class StockAnalyzer:
    """Yahoo Finance-only stock analyzer for comprehensive technical and fundamental analysis"""

    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 minutes

    def _get_cache(self, key: str):
        if key in self.cache:
            if datetime.now() - self.cache_time[key] < timedelta(seconds=self.cache_duration):
                return self.cache[key]
        return None

    def _set_cache(self, key: str, value):
        self.cache[key] = value
        self.cache_time[key] = datetime.now()

    async def fetch_ohlcv(self, symbol: str, period: str = '60d', interval: str = '1d') -> Optional[pd.DataFrame]:
        """Fetch OHLCV data from Yahoo Finance only"""
        try:
            cache_key = f"{symbol}_{period}_{interval}"
            cached = self._get_cache(cache_key)
            if cached is not None:
                return cached

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: yf.download(
                    symbol,
                    period=period,
                    interval=interval,
                    progress=False,
                    threads=False
                )
            )

            if data is not None and not data.empty:
                # Handle MultiIndex columns from newer yfinance versions
                if isinstance(data.columns, pd.MultiIndex):
                    # For single ticker, get the first level of MultiIndex
                    data.columns = data.columns.get_level_values(0)

                # Remove rows that are completely NaN (market hasn't opened yet)
                data = data.dropna(how='all', subset=['Close', 'High', 'Low', 'Open'])

                if data.empty:
                    return None

                self._set_cache(cache_key, data)
                return data

            return None
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return None

    async def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive stock information from Yahoo Finance"""
        try:
            cache_key = f"info_{symbol}"
            cached = self._get_cache(cache_key)
            if cached is not None:
                return cached

            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol))
            info = await loop.run_in_executor(None, lambda: ticker.info)

            result = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'eps': info.get('trailingEps'),
                'revenue_per_share': info.get('revenuePerShare'),
                'profit_margin': info.get('profitMargins'),
                'return_on_equity': info.get('returnOnEquity'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_price': info.get('currentPrice'),
                'previous_close': info.get('previousClose'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'fifty_day_average': info.get('fiftyDayAverage'),
                'two_hundred_day_average': info.get('twoHundredDayAverage'),
                'beta': info.get('beta'),
                'website': info.get('website'),
                'country': info.get('country'),
            }

            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            return None

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote data"""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol))

            info = await loop.run_in_executor(None, lambda: ticker.info)
            hist = await loop.run_in_executor(None, lambda: ticker.history(period='1d'))

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
                'bid_size': int(info.get('bidSize', 0)),
                'ask_size': int(info.get('askSize', 0)),
                'market_cap': info.get('marketCap'),
                '52_week_high': float(info.get('fiftyTwoWeekHigh', 0)),
                '52_week_low': float(info.get('fiftyTwoWeekLow', 0)),
            }
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    async def get_company_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get latest company news from Yahoo Finance"""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol))
            news_list = await loop.run_in_executor(None, lambda: ticker.news[:limit])

            news = []
            for item in news_list:
                if item:
                    news.append({
                        'title': item.get('title', ''),
                        'summary': item.get('summary', ''),
                        'source': item.get('source', 'Yahoo Finance'),
                        'url': item.get('link', ''),
                        'timestamp': item.get('providerPublishTime', 0),
                        'sentiment': self._classify_sentiment(item.get('title', ''))
                    })

            return news
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    async def get_financial_metrics(self, symbol: str) -> Optional[Dict]:
        """Get key financial metrics from Yahoo Finance"""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol))
            info = await loop.run_in_executor(None, lambda: ticker.info)

            return {
                'symbol': symbol,
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'eps': info.get('trailingEps'),
                'revenue': info.get('totalRevenue'),
                'gross_profit': info.get('grossProfit'),
                'operating_income': info.get('operatingIncome'),
                'net_income': info.get('netIncomeToCommon'),
                'free_cash_flow': info.get('freeCashflow'),
                'operating_cash_flow': info.get('operatingCashflow'),
                'total_assets': info.get('totalAssets'),
                'total_debt': info.get('totalDebt'),
                'total_equity': info.get('totalEquity'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'return_on_assets': info.get('returnOnAssets'),
                'return_on_equity': info.get('returnOnEquity'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
            }
        except Exception as e:
            print(f"Error fetching financial metrics for {symbol}: {e}")
            return None

    async def get_historical_data(self, symbol: str, period: str = '5y', interval: str = '1d') -> Optional[List[Dict]]:
        """Get historical price data"""
        try:
            ohlcv = await self.fetch_ohlcv(symbol, period=period, interval=interval)
            if ohlcv is None or ohlcv.empty:
                return None

            data = []
            for idx, row in ohlcv.iterrows():
                date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)
                data.append({
                    'date': date_str,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'adj_close': float(row.get('Adj Close', row['Close']))
                })

            return data
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None

    async def calculate_returns(self, symbol: str, period: str = '1y') -> Optional[Dict]:
        """Calculate returns over various periods"""
        try:
            ohlcv = await self.fetch_ohlcv(symbol, period=period, interval='1d')
            if ohlcv is None or ohlcv.empty:
                return None

            current_price = float(ohlcv['Close'].iloc[-1])

            returns = {}
            for days, label in [(1, '1d'), (7, '1w'), (30, '1m'), (90, '3m'), (365, '1y')]:
                if len(ohlcv) > days:
                    past_price = float(ohlcv['Close'].iloc[-days-1])
                    ret = ((current_price - past_price) / past_price) * 100
                    returns[label] = ret

            return returns
        except Exception as e:
            print(f"Error calculating returns for {symbol}: {e}")
            return None

    async def get_volatility(self, symbol: str, period: str = '60d') -> Optional[Dict]:
        """Calculate volatility metrics"""
        try:
            ohlcv = await self.fetch_ohlcv(symbol, period=period, interval='1d')
            if ohlcv is None or ohlcv.empty:
                return None

            returns = ohlcv['Close'].pct_change().dropna()

            return {
                'volatility_daily': float(returns.std()),
                'volatility_annual': float(returns.std() * (252 ** 0.5)),
                'min_return': float(returns.min()),
                'max_return': float(returns.max()),
                'average_return': float(returns.mean()),
            }
        except Exception as e:
            print(f"Error calculating volatility for {symbol}: {e}")
            return None

    def _classify_sentiment(self, text: str) -> str:
        """Classify sentiment from news title"""
        text_lower = text.lower()

        positive_words = ['surge', 'rally', 'beat', 'outperform', 'gain', 'up', 'rise', 'strong',
                         'bullish', 'jump', 'soar', 'boost', 'growth', 'profit', 'deal', 'win']
        negative_words = ['drop', 'crash', 'miss', 'decline', 'fall', 'down', 'weak', 'bearish',
                         'loss', 'plunge', 'cut', 'layoff', 'risk', 'warning', 'concern']

        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)

        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        return 'neutral'

    async def get_comprehensive_analysis(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive analysis combining all data"""
        try:
            # Fetch all data in parallel
            info_task = self.get_stock_info(symbol)
            quote_task = self.get_quote(symbol)
            news_task = self.get_company_news(symbol, limit=5)
            metrics_task = self.get_financial_metrics(symbol)
            returns_task = self.calculate_returns(symbol, period='1y')
            volatility_task = self.get_volatility(symbol, period='60d')
            history_task = self.get_historical_data(symbol, period='1y')

            info, quote, news, metrics, returns, volatility, history = await asyncio.gather(
                info_task, quote_task, news_task, metrics_task, returns_task, volatility_task, history_task
            )

            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'info': info,
                'quote': quote,
                'news': news,
                'financial_metrics': metrics,
                'returns': returns,
                'volatility': volatility,
                'historical_data': history,
            }
        except Exception as e:
            print(f"Error in comprehensive analysis for {symbol}: {e}")
            return None
