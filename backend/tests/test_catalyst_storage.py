import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import SessionLocal
from src.models import Catalyst, CatalystType, CatalystSentiment
from datetime import datetime
import pytz

client = TestClient(app)


@pytest.fixture
def db():
    """Provide a fresh database session for each test"""
    db_session = SessionLocal()
    yield db_session
    db_session.close()


class TestCatalystStorage:
    """Test catalyst storage and retrieval"""

    def test_get_active_catalysts_endpoint(self):
        """Test /api/eddie/catalysts/active endpoint"""
        response = client.get("/api/eddie/catalysts/active?limit=5")
        assert response.status_code == 200

        data = response.json()
        assert 'catalysts' in data
        assert 'count' in data
        assert isinstance(data['catalysts'], list)

    def test_catalyst_can_be_stored(self, db):
        """Test storing a catalyst in database"""
        catalyst = Catalyst(
            symbol='TEST_STORAGE',
            market='US',
            type=CatalystType.NEWS_EVENT,
            title='Test Catalyst',
            description='A test catalyst',
            sentiment=CatalystSentiment.POSITIVE,
            event_date=datetime.now(pytz.UTC),
            confidence_score=0.85,
            impact_score=0.7,
            source='test'
        )

        db.add(catalyst)
        db.commit()

        # Verify it was stored
        stored = db.query(Catalyst).filter(Catalyst.symbol == 'TEST_STORAGE').first()
        assert stored is not None
        assert stored.title == 'Test Catalyst'

        # Cleanup
        if stored:
            db.delete(stored)
            db.commit()

    def test_catalyst_active_filter(self, db):
        """Test that only active catalysts are returned"""
        # Create active catalyst
        active_catalyst = Catalyst(
            symbol='ACTIVE_TEST_NEW',
            market='US',
            type=CatalystType.NEWS_EVENT,
            title='Active Catalyst',
            description='An active catalyst',
            sentiment=CatalystSentiment.POSITIVE,
            event_date=datetime.now(pytz.UTC),
            confidence_score=0.85,
            impact_score=0.7,
            source='test',
            is_active=True
        )

        # Create inactive catalyst
        inactive_catalyst = Catalyst(
            symbol='INACTIVE_TEST_NEW',
            market='US',
            type=CatalystType.NEWS_EVENT,
            title='Inactive Catalyst',
            description='An inactive catalyst',
            sentiment=CatalystSentiment.NEGATIVE,
            event_date=datetime.now(pytz.UTC),
            confidence_score=0.75,
            impact_score=0.6,
            source='test',
            is_active=False
        )

        db.add(active_catalyst)
        db.add(inactive_catalyst)
        db.commit()

        # Query only active
        active_from_db = db.query(Catalyst).filter(
            Catalyst.is_active == True,
            Catalyst.symbol.in_(['ACTIVE_TEST_NEW', 'INACTIVE_TEST_NEW'])
        ).all()
        assert len(active_from_db) >= 1

        # Cleanup
        db.query(Catalyst).filter(Catalyst.symbol.in_(['ACTIVE_TEST_NEW', 'INACTIVE_TEST_NEW'])).delete()
        db.commit()

    def test_catalyst_types_stored_correctly(self, db):
        """Test that catalyst types are stored and retrieved correctly"""
        types_to_test = [
            CatalystType.NEWS_EVENT,
            CatalystType.EARNINGS,
            CatalystType.CORPORATE_EVENT,
        ]

        catalysts = []
        for i, catalyst_type in enumerate(types_to_test):
            catalyst = Catalyst(
                symbol=f'TYP{i}',
                market='US',
                type=catalyst_type,
                title=f'Test {catalyst_type.value}',
                description='Test',
                sentiment=CatalystSentiment.NEUTRAL,
                confidence_score=0.75,
                impact_score=0.6,
                source='test'
            )
            db.add(catalyst)
            catalysts.append(f'TYP{i}')

        db.commit()

        # Verify all were stored
        stored = db.query(Catalyst).filter(
            Catalyst.symbol.in_(catalysts)
        ).all()
        assert len(stored) == len(types_to_test)

        # Cleanup
        db.query(Catalyst).filter(Catalyst.symbol.in_(catalysts)).delete()
        db.commit()

    def test_catalyst_sentiment_values(self, db):
        """Test that sentiment values are stored correctly"""
        sentiments = [
            CatalystSentiment.POSITIVE,
            CatalystSentiment.NEGATIVE,
            CatalystSentiment.NEUTRAL,
        ]

        symbols = []
        for i, sentiment in enumerate(sentiments):
            symbol = f'SEN{i}'
            catalyst = Catalyst(
                symbol=symbol,
                market='US',
                type=CatalystType.NEWS_EVENT,
                title=f'Test {sentiment.value}',
                description='Test',
                sentiment=sentiment,
                confidence_score=0.75,
                impact_score=0.6,
                source='test'
            )
            db.add(catalyst)
            symbols.append(symbol)

        db.commit()

        # Verify all were stored
        stored = db.query(Catalyst).filter(
            Catalyst.symbol.in_(symbols)
        ).all()
        assert len(stored) == len(sentiments)

        # Cleanup
        db.query(Catalyst).filter(Catalyst.symbol.in_(symbols)).delete()
        db.commit()

    def test_catalyst_default_values(self, db):
        """Test that catalyst defaults are applied"""
        catalyst = Catalyst(
            symbol='DEFAULT_TEST_NEW',
            market='US',
            type=CatalystType.NEWS_EVENT,
            title='Test Defaults',
            description='Test',
            sentiment=CatalystSentiment.NEUTRAL,
            confidence_score=0.75,
            impact_score=0.6,
            source='test'
        )

        db.add(catalyst)
        db.commit()

        stored = db.query(Catalyst).filter(
            Catalyst.symbol == 'DEFAULT_TEST_NEW'
        ).first()

        assert stored is not None
        assert stored.is_active == True
        assert stored.detected_at is not None
        assert stored.price_impact_observed == False
        assert stored.volume_impact_observed == False

        # Cleanup
        db.query(Catalyst).filter(Catalyst.symbol == 'DEFAULT_TEST_NEW').delete()
        db.commit()
