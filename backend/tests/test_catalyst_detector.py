import pytest
from datetime import datetime, timedelta
import pytz
from src.services.catalyst_detector import CatalystDetector
from src.models import CatalystType, CatalystSentiment

class TestCatalystDetector:
    """Test catalyst detection logic"""

    def test_detector_initialization(self):
        """CatalystDetector should initialize without errors"""
        detector = CatalystDetector()
        assert detector is not None
        assert detector.recency_window_days == 14
        assert detector.min_confidence == 0.5

    def test_classify_earnings_catalyst(self):
        """Should identify earnings events as earnings catalysts"""
        detector = CatalystDetector()

        event = {
            'title': 'Apple Reports Q4 2024 Earnings Results',
            'description': 'Quarterly earnings announcement'
        }

        result = detector.detect_catalyst_type(event)
        assert result['type'] == CatalystType.EARNINGS
        assert result['confidence'] >= 0.9

    def test_classify_acquisition_catalyst(self):
        """Should identify mergers/acquisitions"""
        detector = CatalystDetector()

        event = {
            'title': 'Microsoft Announces Acquisition of TechCorp',
            'description': 'Strategic acquisition completed'
        }

        result = detector.detect_catalyst_type(event)
        assert result['type'] == CatalystType.CORPORATE_EVENT

    def test_classify_threat_catalyst(self):
        """Should identify negative/threat catalysts"""
        detector = CatalystDetector()

        event = {
            'title': 'Apple Faces Lawsuit Over Patent Infringement',
            'description': 'Legal action filed'
        }

        result = detector.detect_catalyst_type(event)
        assert result['type'] == CatalystType.THREAT

    def test_sentiment_classification_positive(self):
        """Should classify positive catalysts"""
        detector = CatalystDetector()

        texts = [
            'Company beats earnings expectations by 25%',
            'FDA approval granted for new drug',
            'Strategic partnership announced with major player'
        ]

        for text in texts:
            sentiment = detector.classify_sentiment(text)
            assert sentiment in [CatalystSentiment.POSITIVE, CatalystSentiment.NEUTRAL]

    def test_sentiment_classification_negative(self):
        """Should classify negative catalysts"""
        detector = CatalystDetector()

        texts = [
            'Company misses earnings expectations',
            'CEO resignation announced',
            'Regulatory investigation launched against company'
        ]

        for text in texts:
            sentiment = detector.classify_sentiment(text)
            assert sentiment in [CatalystSentiment.NEGATIVE, CatalystSentiment.NEUTRAL]

    def test_recency_weight_recent_event(self):
        """Recent events should have high weight"""
        detector = CatalystDetector()

        now = datetime.now(pytz.UTC)
        recent = now - timedelta(days=3)

        weight = detector.calculate_recency_weight(recent)
        assert weight > 0.8  # Recent events should be heavily weighted

    def test_recency_weight_old_event(self):
        """Old events should have lower weight"""
        detector = CatalystDetector()

        now = datetime.now(pytz.UTC)
        old = now - timedelta(days=60)

        weight = detector.calculate_recency_weight(old)
        assert weight < 0.3  # Old events should be downweighted

    def test_recency_weight_future_event(self):
        """Future events should have max weight"""
        detector = CatalystDetector()

        now = datetime.now(pytz.UTC)
        future = now + timedelta(days=5)

        weight = detector.calculate_recency_weight(future)
        assert weight == 1.0  # Future events at max

    def test_confidence_scoring(self):
        """Confidence score should be between 0-1"""
        detector = CatalystDetector()

        catalyst = {
            'type_confidence': 0.9,
            'source': 'finnhub',
            'confirmation_count': 2
        }

        score = detector.calculate_confidence_score(catalyst)
        assert 0 <= score <= 1

    def test_catalyst_relevance_check(self):
        """Should check if catalyst is still relevant"""
        detector = CatalystDetector()

        # Recent news event should be relevant
        recent_news = {
            'type': CatalystType.NEWS_EVENT,
            'event_date': datetime.now(pytz.UTC) - timedelta(days=1)
        }

        assert detector.is_catalyst_still_relevant(recent_news) == True

        # Old news should not be relevant
        old_news = {
            'type': CatalystType.NEWS_EVENT,
            'event_date': datetime.now(pytz.UTC) - timedelta(days=10)
        }

        assert detector.is_catalyst_still_relevant(old_news) == False

    def test_earnings_catalyst_longer_relevance(self):
        """Earnings catalysts should stay relevant longer than news"""
        detector = CatalystDetector()

        old_earnings = {
            'type': CatalystType.EARNINGS,
            'event_date': datetime.now(pytz.UTC) - timedelta(days=5)
        }

        # Earnings 5 days old should still be relevant
        assert detector.is_catalyst_still_relevant(old_earnings) == True

    def test_deduplicate_catalysts(self):
        """Should remove duplicate catalysts, keeping best confidence"""
        detector = CatalystDetector()

        catalysts = [
            {
                'symbol': 'AAPL',
                'type': CatalystType.NEWS_EVENT,
                'title': 'Apple announces new features',
                'confidence_score': 0.8
            },
            {
                'symbol': 'AAPL',
                'type': CatalystType.NEWS_EVENT,
                'title': 'Apple announces new features',  # Same event
                'confidence_score': 0.95  # Higher confidence
            },
            {
                'symbol': 'MSFT',
                'type': CatalystType.NEWS_EVENT,
                'title': 'Microsoft partnership',
                'confidence_score': 0.85
            }
        ]

        deduped = detector.deduplicate_catalysts(catalysts)
        assert len(deduped) == 2  # Should have 2 unique catalysts

        # Should keep the higher confidence version
        aapl_catalyst = [c for c in deduped if c['symbol'] == 'AAPL'][0]
        assert aapl_catalyst['confidence_score'] == 0.95
