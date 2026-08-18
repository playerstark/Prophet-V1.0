import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestCatalystAPI:
    """Integration tests for catalyst endpoints"""

    def test_get_stock_catalysts_endpoint(self):
        """Test /api/eddie/catalysts/stock/{symbol}"""
        response = client.get("/api/eddie/catalysts/stock/AAPL?days_back=14")
        assert response.status_code == 200

        data = response.json()
        assert 'symbol' in data
        assert 'catalysts' in data
        assert 'count' in data
        assert data['symbol'] == 'AAPL'
        assert isinstance(data['catalysts'], list)
        assert isinstance(data['count'], int)

    def test_get_stock_catalysts_with_sentiment_filter(self):
        """Test catalyst filtering by sentiment"""
        response = client.get("/api/eddie/catalysts/stock/AAPL?sentiment=positive")
        assert response.status_code == 200

        data = response.json()
        assert 'catalysts' in data
        assert 'count' in data

    def test_earnings_calendar_endpoint(self):
        """Test /api/eddie/catalysts/earnings-calendar"""
        response = client.get("/api/eddie/catalysts/earnings-calendar?days_forward=30")
        assert response.status_code == 200

        data = response.json()
        assert 'earnings' in data
        assert 'count' in data
        assert isinstance(data['earnings'], list)
        assert isinstance(data['count'], int)

    def test_sector_leaders_endpoint(self):
        """Test /api/eddie/catalysts/sector-leaders"""
        response = client.get("/api/eddie/catalysts/sector-leaders")
        assert response.status_code == 200

        data = response.json()
        assert 'sectors' in data
        assert isinstance(data['sectors'], dict)

    def test_get_stock_catalysts_with_custom_days_back(self):
        """Test stock catalysts with custom days_back parameter"""
        response = client.get("/api/eddie/catalysts/stock/AAPL?days_back=30")
        assert response.status_code == 200

        data = response.json()
        assert data['symbol'] == 'AAPL'
        assert 'catalysts' in data

    def test_earnings_calendar_with_custom_days_forward(self):
        """Test earnings calendar with custom days_forward parameter"""
        response = client.get("/api/eddie/catalysts/earnings-calendar?days_forward=60")
        assert response.status_code == 200

        data = response.json()
        assert 'earnings' in data
        assert 'count' in data
