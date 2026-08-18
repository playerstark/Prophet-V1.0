import pytest
from datetime import datetime, timedelta
import pytz
from src.services.market_detector import MarketDetector, Market, MarketSession

class TestMarketDetector:
    """Test Active Market Detection logic"""

    def test_is_nse_trading_hours_during_session(self):
        """NSE trading hours: 09:15 - 15:30 IST"""
        detector = MarketDetector()

        # 10:00 IST on a trading day (Monday)
        tz = pytz.timezone('Asia/Kolkata')
        trading_time = tz.localize(datetime(2024, 1, 8, 10, 0, 0))
        assert detector.is_market_open('NSE', trading_time) == True

    def test_is_nse_closed_before_session(self):
        """NSE should be closed before 09:15"""
        detector = MarketDetector()

        tz = pytz.timezone('Asia/Kolkata')
        pre_open = tz.localize(datetime(2024, 1, 8, 9, 0, 0))
        assert detector.is_market_open('NSE', pre_open) == False

    def test_is_nse_closed_after_session(self):
        """NSE should be closed after 15:30"""
        detector = MarketDetector()

        tz = pytz.timezone('Asia/Kolkata')
        post_close = tz.localize(datetime(2024, 1, 8, 16, 0, 0))
        assert detector.is_market_open('NSE', post_close) == False

    def test_is_nse_closed_on_weekend(self):
        """NSE should be closed on Saturday"""
        detector = MarketDetector()

        tz = pytz.timezone('Asia/Kolkata')
        saturday = tz.localize(datetime(2024, 1, 6, 10, 0, 0))
        assert detector.is_market_open('NSE', saturday) == False

    def test_is_nse_closed_on_holiday(self):
        """NSE should be closed on Republic Day (Jan 26)"""
        detector = MarketDetector()

        tz = pytz.timezone('Asia/Kolkata')
        republic_day = tz.localize(datetime(2024, 1, 26, 10, 0, 0))
        assert detector.is_market_open('NSE', republic_day) == False

    def test_is_nyse_trading_hours_during_session(self):
        """NYSE trading hours: 09:30 - 16:00 EST"""
        detector = MarketDetector()

        # 10:00 EST on a trading day (Monday)
        tz = pytz.timezone('US/Eastern')
        trading_time = tz.localize(datetime(2024, 1, 8, 10, 0, 0))
        assert detector.is_market_open('NYSE', trading_time) == True

    def test_is_nyse_closed_before_session(self):
        """NYSE should be closed before 09:30"""
        detector = MarketDetector()

        tz = pytz.timezone('US/Eastern')
        pre_open = tz.localize(datetime(2024, 1, 8, 9, 0, 0))
        assert detector.is_market_open('NYSE', pre_open) == False

    def test_is_nyse_closed_after_session(self):
        """NYSE should be closed after 16:00"""
        detector = MarketDetector()

        tz = pytz.timezone('US/Eastern')
        post_close = tz.localize(datetime(2024, 1, 8, 17, 0, 0))
        assert detector.is_market_open('NYSE', post_close) == False

    def test_is_bse_closed_on_its_holidays(self):
        """BSE should be closed on its specific holidays"""
        detector = MarketDetector()

        # Use a known BSE holiday
        tz = pytz.timezone('Asia/Kolkata')
        bse_holiday = tz.localize(datetime(2024, 3, 8, 10, 0, 0))  # Maha Shivaratri
        assert detector.is_market_open('BSE', bse_holiday) == False

    def test_get_active_market_for_india_timezone(self):
        """During IST trading hours, active market should be India"""
        detector = MarketDetector()

        # 10:00 IST on trading day
        tz = pytz.timezone('Asia/Kolkata')
        india_time = tz.localize(datetime(2024, 1, 8, 10, 0, 0))
        active_market = detector.get_active_market(india_time)

        assert active_market is not None
        assert active_market['market'] in ['NSE', 'BSE']
        assert active_market['region'] == 'INDIA'

    def test_get_active_market_for_us_timezone(self):
        """During EST trading hours, active market should be NYSE"""
        detector = MarketDetector()

        # 10:00 EST on trading day
        tz = pytz.timezone('US/Eastern')
        us_time = tz.localize(datetime(2024, 1, 8, 10, 0, 0))
        active_market = detector.get_active_market(us_time)

        assert active_market is not None
        assert active_market['market'] == 'NYSE'
        assert active_market['region'] == 'US'

    def test_get_active_market_returns_none_when_all_closed(self):
        """When all markets are closed, should return None"""
        detector = MarketDetector()

        # 22:00 IST (no markets open)
        tz = pytz.timezone('Asia/Kolkata')
        offline_time = tz.localize(datetime(2024, 1, 8, 22, 0, 0))
        active_market = detector.get_active_market(offline_time)

        assert active_market is None

    def test_market_session_info(self):
        """Should return correct session info for a market"""
        detector = MarketDetector()

        session = detector.get_market_session('NSE')
        assert session is not None
        assert session['open_hour'] == 9
        assert session['open_minute'] == 15
        assert session['close_hour'] == 15
        assert session['close_minute'] == 30
        assert session['timezone'] == 'Asia/Kolkata'
