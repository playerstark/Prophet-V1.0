import asyncio
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd
from src.config import settings


class TwelveDataProvider:
    """Twelve Data API provider for premium stock market data"""

    BASE_URL = "https://api.twelvedata.com"
    TIMEOUT = 15

    async def fetch_ohlcv(self, symbol: str, interval: str = "1d", period: str = "60d") -> Optional[pd.DataFrame]:
        """Fetch OHLCV data from Twelve Data"""
        if not settings.twelvedata_api_key:
            return None

        try:
            # Map intervals to Twelve Data format
            interval_map = {
                "1m": "1min",
                "5m": "5min",
                "15m": "15min",
                "30m": "30min",
                "60m": "1h",
                "1h": "1h",
                "1d": "1day",
                "1wk": "1week",
                "1mo": "1month",
            }

            td_interval = interval_map.get(interval, "1day")

            # Calculate number of records needed
            record_map = {
                "1m": 1440,
                "5m": 288,
                "15m": 96,
                "30m": 48,
                "60m": 24,
                "1h": 24,
                "1d": 60,
                "1wk": 12,
                "1mo": 12,
            }
            outputsize = record_map.get(interval, 60)

            params = {
                "symbol": symbol,
                "interval": td_interval,
                "outputsize": outputsize,
                "apikey": settings.twelvedata_api_key,
            }

            url = f"{self.BASE_URL}/time_series"

            response = await asyncio.to_thread(
                requests.get, url, params=params, timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()

                if "values" in data and len(data["values"]) > 0:
                    values = data["values"]

                    df = pd.DataFrame(
                        {
                            "Open": [float(v.get("open", 0)) for v in values],
                            "High": [float(v.get("high", 0)) for v in values],
                            "Low": [float(v.get("low", 0)) for v in values],
                            "Close": [float(v.get("close", 0)) for v in values],
                            "Volume": [int(v.get("volume", 0)) for v in values],
                        }
                    )

                    if not df.empty:
                        df = df.dropna()
                        return df[::-1].reset_index(drop=True)  # Reverse to ascending order

            return None

        except requests.exceptions.Timeout:
            print(f"Twelve Data timeout for {symbol}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Twelve Data request error for {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Twelve Data parsing error for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"Twelve Data error for {symbol}: {e}")
            return None

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol"""
        if not settings.twelvedata_api_key:
            return None

        try:
            params = {
                "symbol": symbol,
                "apikey": settings.twelvedata_api_key,
                "prepost": True,
            }

            url = f"{self.BASE_URL}/quote"

            response = await asyncio.to_thread(
                requests.get, url, params=params, timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                return response.json()

            return None

        except Exception as e:
            print(f"Twelve Data quote error for {symbol}: {e}")
            return None

    async def search_symbol(self, query: str) -> Optional[List[Dict]]:
        """Search for symbols"""
        if not settings.twelvedata_api_key:
            return None

        try:
            params = {
                "symbol": query,
                "apikey": settings.twelvedata_api_key,
            }

            url = f"{self.BASE_URL}/symbol_search"

            response = await asyncio.to_thread(
                requests.get, url, params=params, timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])

            return None

        except Exception as e:
            print(f"Twelve Data symbol search error: {e}")
            return None

    async def get_technical_indicators(
        self, symbol: str, indicator: str = "rsi", interval: str = "1d"
    ) -> Optional[Dict]:
        """Get technical indicator data"""
        if not settings.twelvedata_api_key:
            return None

        try:
            interval_map = {
                "1m": "1min",
                "5m": "5min",
                "15m": "15min",
                "30m": "30min",
                "60m": "1h",
                "1h": "1h",
                "1d": "1day",
                "1wk": "1week",
                "1mo": "1month",
            }

            td_interval = interval_map.get(interval, "1day")

            params = {
                "symbol": symbol,
                "interval": td_interval,
                "apikey": settings.twelvedata_api_key,
            }

            url = f"{self.BASE_URL}/ta/{indicator}"

            response = await asyncio.to_thread(
                requests.get, url, params=params, timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                return response.json()

            return None

        except Exception as e:
            print(f"Twelve Data indicator error for {symbol}: {e}")
            return None
