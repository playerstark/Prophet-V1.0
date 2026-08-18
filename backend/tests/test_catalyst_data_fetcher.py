import pytest
from datetime import datetime
import pytz
from src.services.catalyst_data_fetcher import CatalystDataFetcher

class TestCatalystDataFetcher:
    """Test catalyst data fetching"""

    def test_fetcher_initialization(self):
        """CatalystDataFetcher should initialize"""
        fetcher = CatalystDataFetcher()
        assert fetcher is not None
        assert fetcher.finnhub_key is not None
        assert fetcher.finnhub_base_url == "https://finnhub.io/api/v1"

    def test_parse_news_to_catalyst(self):
        """Should convert news article to catalyst format"""
        fetcher = CatalystDataFetcher()

        news = {
            'symbol': 'AAPL',
            'headline': 'Apple launches new AI features',
            'summary': 'Apple announced new AI capabilities',
            'datetime': 1704067200,  # 2024-01-01
            'url': 'https://example.com/news',
            'id': 'news_123'
        }

        catalyst = fetcher.parse_news_to_catalyst(news)
        assert catalyst['symbol'] == 'AAPL'
        assert catalyst['type'] == 'news_event'
        assert 'title' in catalyst
        assert catalyst['source'] == 'finnhub'
        assert catalyst['source_url'] == 'https://example.com/news'
        assert catalyst['source_id'] == 'news_123'

    def test_parse_earnings_to_catalyst(self):
        """Should convert earnings event to catalyst format"""
        fetcher = CatalystDataFetcher()

        earnings = {
            'symbol': 'MSFT',
            'date': '2024-01-30',
            'quarter': 'Q4'
        }

        catalyst = fetcher.parse_earnings_to_catalyst(earnings)
        assert catalyst['symbol'] == 'MSFT'
        assert catalyst['type'] == 'earnings'
        assert 'title' in catalyst
        assert 'Q4' in catalyst['title']

    def test_news_parsing_handles_missing_fields(self):
        """Should handle missing fields gracefully"""
        fetcher = CatalystDataFetcher()

        minimal_news = {
            'symbol': 'GOOG',
            'headline': 'Google announces partnership',
            'datetime': 1704067200
        }

        catalyst = fetcher.parse_news_to_catalyst(minimal_news)
        assert catalyst['symbol'] == 'GOOG'
        assert catalyst['source_url'] is None or catalyst['source_url'] == ''

    def test_earnings_parsing_handles_missing_fields(self):
        """Should handle missing earnings fields"""
        fetcher = CatalystDataFetcher()

        minimal_earnings = {
            'symbol': 'TSLA',
            'date': '2024-02-15'
        }

        catalyst = fetcher.parse_earnings_to_catalyst(minimal_earnings)
        assert catalyst['symbol'] == 'TSLA'
        assert 'Earnings announcement' in catalyst['description']
