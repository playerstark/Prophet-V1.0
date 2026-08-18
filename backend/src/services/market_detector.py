"""
Market Detector Service - Active Market Detection

Determines which market is currently active based on user timezone and market hours.
Handles timezone conversion, trading hours, weekends, and holidays for multiple markets.
"""

from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import Optional, Dict, List, Any
import pytz


@dataclass
class MarketSession:
    """Market trading session information"""
    market: str
    open_hour: int
    open_minute: int
    close_hour: int
    close_minute: int
    timezone: str
    region: str


class Market(str, Enum):
    """Market constants as proper Enum"""
    NSE = "NSE"
    BSE = "BSE"
    NYSE = "NYSE"


class MarketDetector:
    """
    Detects active markets based on timezone-aware datetime.
    Handles trading hours, weekends, and market-specific holidays.

    Supported regions:
    - India: NSE, BSE (Asia/Kolkata timezone)
    - US: NYSE (US/Eastern timezone)
    """

    # Explicit timezone to region mapping to avoid fragile string matching
    TIMEZONE_TO_REGION: Dict[str, str] = {
        'Asia/Kolkata': 'INDIA',
        'US/Eastern': 'US',
        'US/Central': 'US',
        'US/Mountain': 'US',
        'US/Pacific': 'US',
    }

    # Region to markets mapping
    REGION_MARKETS: Dict[str, List[str]] = {
        'INDIA': ['NSE', 'BSE'],
        'US': ['NYSE'],
    }

    def __init__(self) -> None:
        """Initialize market detector with session info and holidays"""
        self.sessions = self._initialize_sessions()
        self.holidays = self._initialize_holidays()

    def _initialize_sessions(self) -> Dict[str, 'MarketSession']:
        """Define trading sessions for all supported markets"""
        return {
            'NSE': MarketSession(
                market='NSE',
                open_hour=9,
                open_minute=15,
                close_hour=15,
                close_minute=30,
                timezone='Asia/Kolkata',
                region='INDIA'
            ),
            'BSE': MarketSession(
                market='BSE',
                open_hour=9,
                open_minute=15,
                close_hour=15,
                close_minute=30,
                timezone='Asia/Kolkata',
                region='INDIA'
            ),
            'NYSE': MarketSession(
                market='NYSE',
                open_hour=9,
                open_minute=30,
                close_hour=16,
                close_minute=0,
                timezone='US/Eastern',
                region='US'
            )
        }

    def _initialize_holidays(self) -> Dict[str, List[tuple[int, int]]]:
        """
        Define market-specific holidays as (month, day) tuples.
        These are fixed holidays. Note: For moveable holidays, additional logic may be needed.
        """
        return {
            'NSE': [
                (1, 26),   # Republic Day
                (3, 8),    # Maha Shivaratri (2024)
                (3, 25),   # Holi
                (3, 29),   # Good Friday
                (4, 11),   # Eid ul-Fitr (approximate)
                (4, 17),   # Ram Navami
                (5, 23),   # Buddha Purnima
                (6, 17),   # Eid ul-Adha (approximate)
                (7, 17),   # Muharram
                (8, 15),   # Independence Day
                (8, 26),   # Janmashtami
                (9, 16),   # Milad-un-Nabi
                (10, 2),   # Gandhi Jayanti
                (10, 12),  # Dussehra
                (10, 31),  # Diwali
                (11, 1),   # Diwali (Day 2)
                (11, 15),  # Guru Nanak Jayanti
                (12, 25),  # Christmas
            ],
            'BSE': [
                (1, 26),   # Republic Day
                (3, 8),    # Maha Shivaratri
                (3, 25),   # Holi
                (3, 29),   # Good Friday
                (4, 11),   # Eid ul-Fitr
                (4, 17),   # Ram Navami
                (5, 23),   # Buddha Purnima
                (6, 17),   # Eid ul-Adha
                (7, 17),   # Muharram
                (8, 15),   # Independence Day
                (8, 26),   # Janmashtami
                (9, 16),   # Milad-un-Nabi
                (10, 2),   # Gandhi Jayanti
                (10, 12),  # Dussehra
                (10, 31),  # Diwali
                (11, 1),   # Diwali (Day 2)
                (11, 15),  # Guru Nanak Jayanti
                (12, 25),  # Christmas
            ],
            'NYSE': [
                (1, 1),    # New Year's Day
                (1, 15),   # MLK Jr. Day (3rd Monday, approximate)
                (2, 19),   # Presidents Day (3rd Monday, approximate)
                (3, 29),   # Good Friday
                (5, 27),   # Memorial Day (last Monday, approximate)
                (6, 19),   # Juneteenth
                (7, 4),    # Independence Day
                (9, 2),    # Labor Day (1st Monday, approximate)
                (11, 28),  # Thanksgiving (4th Thursday, approximate)
                (12, 25),  # Christmas
            ]
        }

    def is_market_open(self, market: str, dt: datetime) -> bool:
        """
        Check if a market is open at the given datetime.

        Args:
            market: Market identifier ('NSE', 'BSE', 'NYSE')
            dt: Timezone-aware datetime to check

        Returns:
            True if market is open, False otherwise

        Raises:
            ValueError: If datetime is not timezone-aware or market not found
        """
        if market not in self.sessions:
            return False

        if dt.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")

        # Check if it's a weekend (Saturday=5, Sunday=6)
        if dt.weekday() >= 5:
            return False

        # Check if it's a holiday
        if self._is_holiday(market, dt):
            return False

        # Convert to market timezone
        session = self.sessions[market]
        try:
            market_tz = pytz.timezone(session.timezone)
        except pytz.exceptions.UnknownTimeZoneError as e:
            raise ValueError(f"Invalid timezone for market {market}: {session.timezone}") from e

        try:
            market_time = dt.astimezone(market_tz)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to convert datetime to market timezone: {e}") from e

        # Check trading hours
        open_time = time(session.open_hour, session.open_minute)
        close_time = time(session.close_hour, session.close_minute)
        current_time = market_time.time()

        return open_time <= current_time < close_time

    def _is_holiday(self, market: str, dt: datetime) -> bool:
        """
        Check if the given date is a holiday for the market.

        Args:
            market: Market identifier ('NSE', 'BSE', 'NYSE')
            dt: Timezone-aware datetime

        Returns:
            True if it's a holiday for the market, False otherwise
        """
        if market not in self.holidays:
            return False

        holidays = self.holidays[market]
        return (dt.month, dt.day) in holidays

    def get_active_market(self, dt: datetime) -> Optional[Dict[str, Any]]:
        """
        Determine which market is currently active in the user's timezone.

        The user's timezone is inferred from the tzinfo of the input datetime.
        Only markets in that region are checked.

        Args:
            dt: Timezone-aware datetime to check (the timezone indicates the user's location)

        Returns:
            Dictionary with market info (market, region, is_open, open_time, close_time, timezone)
            if a market is open in the user's timezone, None if no market is open or
            if the timezone is not recognized.

        Raises:
            ValueError: If datetime is not timezone-aware
        """
        if dt.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")

        # Get the timezone name to determine user's region
        tz_name = str(dt.tzinfo)

        # Look up region using explicit mapping instead of fragile string matching
        region = self.TIMEZONE_TO_REGION.get(tz_name)
        if region is None:
            # Timezone not recognized
            return None

        # Get markets for this region
        markets = self.REGION_MARKETS.get(region, [])

        # Check if any market in the region is open
        for market in markets:
            try:
                if self.is_market_open(market, dt):
                    session = self.sessions[market]
                    return {
                        'market': market,
                        'region': session.region,
                        'is_open': True,
                        'open_time': f"{session.open_hour:02d}:{session.open_minute:02d}",
                        'close_time': f"{session.close_hour:02d}:{session.close_minute:02d}",
                        'timezone': session.timezone
                    }
            except ValueError:
                # If there's an error checking this market, continue to next
                continue

        return None

    def get_market_session(self, market: str) -> Optional[Dict[str, Any]]:
        """
        Get trading session information for a market.

        Args:
            market: Market identifier ('NSE', 'BSE', 'NYSE')

        Returns:
            Dictionary with session details (market, open_hour, open_minute, close_hour, close_minute,
            timezone, region) or None if market not found
        """
        if market not in self.sessions:
            return None

        session = self.sessions[market]
        return {
            'market': session.market,
            'open_hour': session.open_hour,
            'open_minute': session.open_minute,
            'close_hour': session.close_hour,
            'close_minute': session.close_minute,
            'timezone': session.timezone,
            'region': session.region
        }

    def get_symbol_market(self, symbol: str) -> Optional[str]:
        """
        Infer which market a stock symbol belongs to based on suffix/format.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TCS.NS', 'RELIANCE.BO')

        Returns:
            Market code ('NYSE', 'NSE', 'BSE') or None if cannot determine
        """
        if not symbol:
            return None

        symbol_upper = symbol.upper()

        # Indian market indicators
        if '.NS' in symbol_upper or '.NSE' in symbol_upper:
            return 'NSE'
        if '.BO' in symbol_upper or '.BSE' in symbol_upper:
            return 'BSE'

        # Common Indian stocks (without suffix)
        indian_symbols = ['RELIANCE', 'TCS', 'INFY', 'WIPRO', 'HDFC', 'LT', 'MARUTI', 'BAJAJ']
        if symbol_upper in indian_symbols:
            return 'NSE'  # Default to NSE for Indian stocks

        # US market (default for common US symbols)
        us_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        if symbol_upper in us_symbols:
            return 'NYSE'

        # If no clear indicator, return None
        return None

    def get_active_markets(self, dt: datetime) -> List[str]:
        """
        Get list of all active markets at the given datetime (regardless of timezone).

        Args:
            dt: Timezone-aware datetime to check

        Returns:
            List of active market codes (e.g., ['NSE', 'BSE'] or ['NYSE'])
        """
        if dt.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")

        active_markets = []
        for market in ['NSE', 'BSE', 'NYSE']:
            if self.is_market_open(market, dt):
                active_markets.append(market)

        return active_markets

    def get_market_status(self, market: str, dt: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get detailed status for a specific market.

        Args:
            market: Market identifier ('NSE', 'BSE', 'NYSE')
            dt: Optional timezone-aware datetime. If not provided, uses current UTC time.

        Returns:
            Dictionary with market status including:
            - market: Market identifier
            - is_open: Whether market is open
            - timezone: Market's timezone
            - current_time: Current time in market's timezone
            - open_time: Market open time (HH:MM format)
            - close_time: Market close time (HH:MM format)
            - session: Trading session ('main', 'pre_market', 'post_market', 'closed')
            - region: Market region (INDIA, US)
            Or error dict if market not found
        """
        if market not in self.sessions:
            return {'error': f"Market '{market}' not found"}

        # Use current UTC time if not provided
        if dt is None:
            dt = datetime.now(pytz.UTC)

        session = self.sessions[market]
        market_tz = pytz.timezone(session.timezone)
        market_time = dt.astimezone(market_tz)

        is_open = self.is_market_open(market, dt)

        # Determine session type
        current_time_obj = market_time.time()
        open_time_obj = time(session.open_hour, session.open_minute)
        close_time_obj = time(session.close_hour, session.close_minute)

        if current_time_obj < open_time_obj:
            session_type = 'pre_market'
        elif current_time_obj >= close_time_obj:
            session_type = 'post_market'
        elif is_open:
            session_type = 'main'
        else:
            session_type = 'closed'

        return {
            'market': market,
            'is_open': is_open,
            'timezone': session.timezone,
            'current_time': market_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'open_time': f"{session.open_hour:02d}:{session.open_minute:02d}",
            'close_time': f"{session.close_hour:02d}:{session.close_minute:02d}",
            'session': session_type,
            'region': session.region
        }
