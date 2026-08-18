import pytest
from datetime import datetime
import pytz
from src.models import Catalyst, CatalystType, CatalystSentiment, CatalystAnalysis

class TestCatalystModels:
    """Test catalyst model creation"""

    def test_catalyst_model_creation(self):
        """Test creating a catalyst record"""
        catalyst = Catalyst(
            symbol="AAPL",
            market="US",
            type=CatalystType.CORPORATE_EVENT,
            title="Q4 Earnings Announcement",
            description="Apple reports Q4 earnings",
            sentiment=CatalystSentiment.POSITIVE,
            event_date=datetime(2024, 1, 30, tzinfo=pytz.UTC),
            confidence_score=0.95,
            impact_score=0.8,
            source="finnhub"
        )

        assert catalyst.symbol == "AAPL"
        assert catalyst.type == CatalystType.CORPORATE_EVENT
        assert catalyst.sentiment == CatalystSentiment.POSITIVE
        assert catalyst.confidence_score == 0.95

    def test_catalyst_types_enum(self):
        """Test all catalyst types are defined"""
        types = [
            CatalystType.CORPORATE_EVENT,
            CatalystType.SECTOR_MOMENTUM,
            CatalystType.NEWS_EVENT,
            CatalystType.REGULATORY,
            CatalystType.EARNINGS,
            CatalystType.THREAT,
            CatalystType.OPPORTUNITY
        ]
        assert len(types) == 7
        assert all(isinstance(t, CatalystType) for t in types)

    def test_catalyst_sentiment_enum(self):
        """Test sentiment values"""
        sentiments = [
            CatalystSentiment.POSITIVE,
            CatalystSentiment.NEGATIVE,
            CatalystSentiment.NEUTRAL,
            CatalystSentiment.UNKNOWN
        ]
        assert len(sentiments) == 4
        assert all(isinstance(s, CatalystSentiment) for s in sentiments)

    def test_catalyst_analysis_model(self):
        """Test catalyst analysis record"""
        analysis = CatalystAnalysis(
            catalyst_id=1,
            analysis_text="This is a high-quality catalyst",
            reasoning_confidence=0.92,
            suggested_sentiment=CatalystSentiment.POSITIVE,
            is_valid=True,
            relevance_score=0.85
        )

        assert analysis.catalyst_id == 1
        assert analysis.is_valid == True
        assert analysis.relevance_score == 0.85

    def test_catalyst_defaults(self):
        """Test catalyst default values"""
        catalyst = Catalyst(
            symbol="MSFT",
            market="US",
            type=CatalystType.NEWS_EVENT,
            title="New Partnership Announced",
            sentiment=CatalystSentiment.POSITIVE,
            confidence_score=0.75,
            impact_score=0.6,
            source="news"
        )

        # Should have defaults set
        assert catalyst.is_active == True
        assert catalyst.detected_at is not None
        assert catalyst.price_impact_observed == False
        assert catalyst.volume_impact_observed == False
