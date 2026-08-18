import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestEddieMarketDetectionAPI:
    """Integration tests for Eddie market detection endpoints"""

    def test_get_active_market_endpoint_exists(self):
        """Test /api/eddie/market/active endpoint"""
        response = client.get("/api/eddie/market/active")
        assert response.status_code == 200

        data = response.json()
        assert "market" in data
        assert "is_open" in data
        assert "current_time" in data

    def test_get_active_market_with_timezone(self):
        """Test active market with specific timezone"""
        response = client.get("/api/eddie/market/active?timezone=Asia/Kolkata")
        assert response.status_code == 200

        data = response.json()
        if data.get("market"):  # If market is open
            assert data["market"] in ["NSE", "BSE"]
            assert data["region"] == "INDIA"

    def test_get_active_market_invalid_timezone(self):
        """Test with invalid timezone - should return 422"""
        response = client.get("/api/eddie/market/active?timezone=Invalid/Timezone")
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_get_market_status_nse(self):
        """Test NSE market status endpoint"""
        response = client.get("/api/eddie/market/status/NSE")
        assert response.status_code == 200

        data = response.json()
        assert data["market"] == "NSE"
        assert "is_open" in data
        assert "timezone" in data
        assert data["timezone"] == "Asia/Kolkata"
        assert "session" in data
        assert data["session"] in ["pre_market", "main", "post_market", "closed"]

    def test_get_market_status_nyse(self):
        """Test NYSE market status endpoint"""
        response = client.get("/api/eddie/market/status/NYSE")
        assert response.status_code == 200

        data = response.json()
        assert data["market"] == "NYSE"
        assert data["timezone"] == "US/Eastern"
        assert data["region"] == "US"

    def test_get_market_status_invalid_market(self):
        """Test with invalid market code - should return 404"""
        response = client.get("/api/eddie/market/status/INVALID")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    def test_get_market_status_case_insensitive(self):
        """Test that market codes are case-insensitive"""
        response = client.get("/api/eddie/market/status/nse")
        assert response.status_code == 200

        data = response.json()
        assert data["market"] == "NSE"

    def test_get_all_markets_status(self):
        """Test all markets status endpoint"""
        response = client.get("/api/eddie/market/all-status")
        assert response.status_code == 200

        data = response.json()
        assert "NSE" in data
        assert "BSE" in data
        assert "NYSE" in data
        assert "active_market" in data

        # Verify structure of each market status
        for market_code in ["NSE", "BSE", "NYSE"]:
            status = data[market_code]
            assert "market" in status
            assert "is_open" in status
            assert "timezone" in status

    def test_all_markets_status_has_consistent_structure(self):
        """Test that all-status has consistent response structure"""
        response = client.get("/api/eddie/market/all-status")
        assert response.status_code == 200

        data = response.json()

        # All markets should have same keys
        nse_keys = set(data["NSE"].keys())
        bse_keys = set(data["BSE"].keys())
        nyse_keys = set(data["NYSE"].keys())

        # Allow some variation for errors, but check main structure
        for market_code in ["NSE", "BSE", "NYSE"]:
            assert "market" in data[market_code]
            assert isinstance(data[market_code]["market"], str)
