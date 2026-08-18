import pytest
from datetime import datetime
import pytz
from src.models import PriceVolumeAnomaly, AnomalyType, MarketCapClass

class TestPriceVolumeModels:
    """Test price/volume anomaly models"""

    def test_anomaly_types_enum(self):
        """Test all anomaly types are defined"""
        types = [
            AnomalyType.PRICE_BREAKOUT,
            AnomalyType.VOLUME_SPIKE,
            AnomalyType.PRICE_VOLUME_CONFLUENCE,
            AnomalyType.RSI_EXTREME,
            AnomalyType.ADX_SURGE,
            AnomalyType.MA_CROSSOVER
        ]
        assert len(types) == 6

    def test_market_cap_class_enum(self):
        """Test market cap classifications"""
        classes = [
            MarketCapClass.LARGE_CAP,
            MarketCapClass.MID_CAP,
            MarketCapClass.SMALL_CAP
        ]
        assert len(classes) == 3

    def test_price_volume_anomaly_creation(self):
        """Test creating an anomaly record"""
        anomaly = PriceVolumeAnomaly(
            symbol='AAPL',
            market='US',
            type=AnomalyType.PRICE_VOLUME_CONFLUENCE,
            market_cap_class=MarketCapClass.LARGE_CAP,
            price_change_percent=5.2,
            price_current=180.50,
            price_ma_20=178.20,
            price_ma_50=176.80,
            volume_change_percent=150.0,
            volume_current=85000000,
            volume_avg_5day=40000000,
            volume_relative_strength=2.125,
            rsi=65.5,
            adx=35.2,
            momentum=12.5,
            liquidity_quality_score=0.95,
            volume_distribution_healthy=True,
            technical_confirmation_score=0.88,
            is_manipulation_risk=False,
            timestamp=datetime.now(pytz.UTC)
        )

        assert anomaly.symbol == 'AAPL'
        assert anomaly.type == AnomalyType.PRICE_VOLUME_CONFLUENCE
        assert anomaly.market_cap_class == MarketCapClass.LARGE_CAP
        assert anomaly.price_change_percent == 5.2
        assert anomaly.volume_relative_strength == 2.125

    def test_small_cap_anomaly(self):
        """Test creating small-cap anomaly with liquidity scoring"""
        anomaly = PriceVolumeAnomaly(
            symbol='TINY',
            market='US',
            type=AnomalyType.PRICE_BREAKOUT,
            market_cap_class=MarketCapClass.SMALL_CAP,
            price_change_percent=8.5,
            price_current=12.30,
            volume_change_percent=200.0,
            volume_current=500000,
            volume_avg_5day=100000,
            volume_relative_strength=5.0,
            liquidity_quality_score=0.45,  # Lower for small-cap
            volume_distribution_healthy=False,  # Spike vs distributed
            technical_confirmation_score=0.55,
            is_manipulation_risk=True,  # Flag for further review
            timestamp=datetime.now(pytz.UTC)
        )

        assert anomaly.market_cap_class == MarketCapClass.SMALL_CAP
        assert anomaly.is_manipulation_risk == True
        assert anomaly.liquidity_quality_score < 0.50

    def test_technical_confirmation_scoring(self):
        """Test anomalies with varying technical confirmation"""
        high_confidence = PriceVolumeAnomaly(
            symbol='MSFT',
            market='US',
            type=AnomalyType.RSI_EXTREME,
            market_cap_class=MarketCapClass.LARGE_CAP,
            price_change_percent=3.5,
            price_current=350.00,
            volume_change_percent=120.0,
            volume_current=50000000,
            volume_avg_5day=30000000,
            volume_relative_strength=1.67,
            rsi=75.0,  # Overbought
            adx=42.0,  # Strong trend
            momentum=15.0,
            technical_confirmation_score=0.92,  # High confirmation
            timestamp=datetime.now(pytz.UTC)
        )

        assert high_confidence.technical_confirmation_score > 0.90

    def test_defaults_applied(self):
        """Test default values are set"""
        anomaly = PriceVolumeAnomaly(
            symbol='TEST',
            market='US',
            type=AnomalyType.VOLUME_SPIKE,
            market_cap_class=MarketCapClass.MID_CAP,
            price_change_percent=2.0,
            price_current=100.0,
            volume_change_percent=50.0,
            volume_current=5000000,
            volume_avg_5day=3000000,
            volume_relative_strength=1.67,
            technical_confirmation_score=0.75,
            timestamp=datetime.now(pytz.UTC)
        )

        assert anomaly.is_manipulation_risk == False  # Default
        assert anomaly.detected_at is not None  # Should be set
