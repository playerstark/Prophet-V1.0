from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import asyncio
import requests
from src.config import settings
from src.services.data_fetcher import DataFetcher


class PriceVolumeDataFetcher:
    """
    Fetches price and volume data for intraday and historical analysis.

    Data sources:
    - Yahoo Finance: Primary for historical and intraday OHLCV data
    - Finnhub: Alternative for real-time and historical candles
    - Twelve Data: Premium data source when available

    Supports:
    - Intraday bars (1m, 5m, 15m, 60m)
    - Daily historical data (up to 60 days)
    - Market cap classification
    - Volume analysis and trending
    """

    def __init__(self):
        """Initialize PriceVolumeDataFetcher"""
        self.data_fetcher = DataFetcher()
        self.cache_ttl_minutes = 60  # Cache freshness window

    async def fetch_intraday_ohlcv(
        self,
        symbol: str,
        interval: str = '60m',
        lookback_days: int = 1
    ) -> Optional[pd.DataFrame]:
        """
        Fetch intraday OHLCV bars.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'ITC.NS')
            interval: Bar interval ('1m', '5m', '15m', '60m')
            lookback_days: How many days back to fetch (default 1)

        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        try:
            # Determine period based on interval and lookback days
            period = f'{lookback_days}d'

            # Fetch data using existing data_fetcher
            ohlcv = await self.data_fetcher.fetch_ohlcv(
                symbol,
                period=period,
                interval=interval
            )

            if ohlcv is None or ohlcv.empty:
                return None

            # Ensure required columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in ohlcv.columns for col in required_columns):
                return None

            # Ensure index is DatetimeIndex
            if not isinstance(ohlcv.index, pd.DatetimeIndex):
                ohlcv.index = pd.to_datetime(ohlcv.index)

            # Sort by timestamp
            ohlcv = ohlcv.sort_index()

            return ohlcv

        except Exception as e:
            print(f"Error fetching intraday OHLCV for {symbol}: {e}")
            return None

    async def fetch_historical_ohlcv(
        self,
        symbol: str,
        days: int = 60
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical daily OHLCV data.

        Args:
            symbol: Stock symbol
            days: Number of days to look back (max 60)

        Returns:
            DataFrame with daily OHLCV data or None
        """
        try:
            # Limit to 60 days
            days = min(days, 60)
            period = f'{days}d'

            ohlcv = await self.data_fetcher.fetch_ohlcv(
                symbol,
                period=period,
                interval='1d'
            )

            if ohlcv is None or ohlcv.empty:
                return None

            # Ensure proper columns and sorting
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in ohlcv.columns for col in required_columns):
                return None

            if not isinstance(ohlcv.index, pd.DatetimeIndex):
                ohlcv.index = pd.to_datetime(ohlcv.index)

            ohlcv = ohlcv.sort_index()

            return ohlcv

        except Exception as e:
            print(f"Error fetching historical OHLCV for {symbol}: {e}")
            return None

    async def fetch_volume_analysis_data(
        self,
        symbol: str,
        lookback_days: int = 30
    ) -> Optional[Dict[str, any]]:
        """
        Fetch historical volume data for analysis.

        Useful for:
        - Calculating average volume
        - Detecting volume trends
        - Computing volume-based signals

        Args:
            symbol: Stock symbol
            lookback_days: How many days to analyze (max 60)

        Returns:
            Dict with volume analysis data
        """
        try:
            # Fetch historical data
            ohlcv = await self.fetch_historical_ohlcv(symbol, days=lookback_days)

            if ohlcv is None or ohlcv.empty or len(ohlcv) < 5:
                return None

            volumes = ohlcv['Volume']

            # Calculate volume statistics
            volume_data = {
                'symbol': symbol,
                'current_volume': volumes.iloc[-1],
                'avg_volume_5d': volumes.tail(5).mean(),
                'avg_volume_20d': volumes.tail(20).mean() if len(volumes) >= 20 else None,
                'avg_volume_all': volumes.mean(),
                'median_volume': volumes.median(),
                'volume_std': volumes.std(),
                'volume_min': volumes.min(),
                'volume_max': volumes.max(),
                'volume_trend': 'increasing' if volumes.iloc[-1] > volumes.mean() else 'decreasing',
                'lookback_days': len(volumes),
                'data_points': len(volumes)
            }

            return volume_data

        except Exception as e:
            print(f"Error fetching volume analysis for {symbol}: {e}")
            return None

    async def fetch_market_cap(self, symbol: str) -> Optional[float]:
        """
        Fetch market cap for a stock.

        Uses Finnhub API for market cap data.

        Args:
            symbol: Stock symbol (US: 'AAPL', India: 'ITC.NS')

        Returns:
            Market cap in USD or None if unavailable
        """
        try:
            if not settings.finnhub_api_key:
                return None

            # Finnhub company profile endpoint
            url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={settings.finnhub_api_key}"

            response = await asyncio.to_thread(
                requests.get,
                url,
                timeout=10
            )

            if response.status_code != 200:
                return None

            data = response.json()

            # Market cap is in millions in Finnhub API
            if 'marketCap' in data and data['marketCap']:
                return data['marketCap'] * 1_000_000  # Convert to USD

            return None

        except Exception as e:
            print(f"Error fetching market cap for {symbol}: {e}")
            return None

    async def fetch_intraday_60m(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Convenience method: Fetch 1 day of 60-minute bars.

        Args:
            symbol: Stock symbol

        Returns:
            DataFrame with 60m OHLCV data
        """
        return await self.fetch_intraday_ohlcv(
            symbol,
            interval='60m',
            lookback_days=1
        )

    async def fetch_intraday_15m(self, symbol: str, days: int = 1) -> Optional[pd.DataFrame]:
        """
        Convenience method: Fetch 15-minute bars.

        Args:
            symbol: Stock symbol
            days: Lookback days (usually 1-5 for intraday)

        Returns:
            DataFrame with 15m OHLCV data
        """
        return await self.fetch_intraday_ohlcv(
            symbol,
            interval='15m',
            lookback_days=days
        )

    async def fetch_stock_data_bundle(
        self,
        symbol: str
    ) -> Optional[Dict[str, any]]:
        """
        Fetch complete data bundle for a stock.

        Includes:
        - Intraday 60m bars (last 1 day)
        - Historical daily (last 60 days)
        - Market cap
        - Volume analysis

        Useful for comprehensive anomaly detection.

        Args:
            symbol: Stock symbol

        Returns:
            Dict with all data or None if critical fetch fails
        """
        try:
            # Fetch all data concurrently
            intraday_60m = await self.fetch_intraday_60m(symbol)
            historical_60d = await self.fetch_historical_ohlcv(symbol, days=60)
            market_cap = await self.fetch_market_cap(symbol)
            volume_analysis = await self.fetch_volume_analysis_data(symbol, lookback_days=30)

            # At least one must succeed
            if intraday_60m is None and historical_60d is None:
                return None

            return {
                'symbol': symbol,
                'intraday_60m': intraday_60m,
                'historical_60d': historical_60d,
                'market_cap': market_cap,
                'volume_analysis': volume_analysis,
                'fetched_at': datetime.utcnow()
            }

        except Exception as e:
            print(f"Error fetching data bundle for {symbol}: {e}")
            return None

    async def validate_ohlcv_data(
        self,
        ohlcv: pd.DataFrame
    ) -> Tuple[bool, List[str]]:
        """
        Validate OHLCV data quality.

        Checks for:
        - Required columns
        - No NaN values
        - Logical OHLC relationships (H >= O,C,L)
        - Positive volume
        - Chronological order

        Args:
            ohlcv: DataFrame with OHLCV data

        Returns:
            Tuple (is_valid, list of error messages)
        """
        errors = []

        # Check columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in ohlcv.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
            return len(errors) == 0, errors

        # Check NaN values
        nan_cols = ohlcv[required_cols].columns[ohlcv[required_cols].isna().any()].tolist()
        if nan_cols:
            errors.append(f"NaN values in columns: {nan_cols}")

        # Check OHLC logic
        invalid_rows = (
            (ohlcv['High'] < ohlcv['Open']) |
            (ohlcv['High'] < ohlcv['Close']) |
            (ohlcv['High'] < ohlcv['Low']) |
            (ohlcv['Low'] > ohlcv['Open']) |
            (ohlcv['Low'] > ohlcv['Close'])
        ).sum()

        if invalid_rows > 0:
            errors.append(f"{invalid_rows} rows with invalid OHLC relationships")

        # Check positive volume
        zero_volume_rows = (ohlcv['Volume'] <= 0).sum()
        if zero_volume_rows > 0:
            errors.append(f"{zero_volume_rows} rows with zero/negative volume")

        # Check chronological order
        if len(ohlcv) > 1:
            if not ohlcv.index.is_monotonic_increasing:
                errors.append("Data is not in chronological order")

        return len(errors) == 0, errors

    async def combine_intraday_and_historical(
        self,
        symbol: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch and combine intraday and historical data.

        For continuous analysis across timeframes.

        Args:
            symbol: Stock symbol

        Returns:
            Combined DataFrame or None
        """
        try:
            intraday = await self.fetch_intraday_60m(symbol)
            historical = await self.fetch_historical_ohlcv(symbol, days=60)

            if historical is None:
                return intraday

            if intraday is None:
                return historical

            # Combine, removing duplicates (keep intraday if duplicate timestamps)
            combined = pd.concat([historical, intraday]).drop_duplicates(
                subset=None,
                keep='last'
            ).sort_index()

            return combined

        except Exception as e:
            print(f"Error combining data for {symbol}: {e}")
            return None
