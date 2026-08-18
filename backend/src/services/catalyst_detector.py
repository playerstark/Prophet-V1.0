from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz
from src.models import CatalystType, CatalystSentiment

class CatalystDetector:
    """
    Detects and classifies catalysts for stocks.

    Catalysts include:
    - Corporate events (earnings, acquisitions, announcements)
    - Sector momentum (industry outperformance)
    - News events (company-specific developments)
    - Regulatory developments
    - Market threats and opportunities
    """

    # Keywords for catalyst type detection
    EARNINGS_KEYWORDS = ['earnings', 'eps', 'revenue', 'q1', 'q2', 'q3', 'q4', 'results', 'profit', 'fy']
    ACQUISITION_KEYWORDS = ['acquire', 'acquisition', 'merger', 'merge', 'combine', 'deal', 'takeover']
    PRODUCT_KEYWORDS = ['launch', 'release', 'introduce', 'new product', 'new service', 'announce']
    REGULATORY_KEYWORDS = ['sec', 'fda', 'approval', 'license', 'regulation', 'compliance', 'filing']
    THREAT_KEYWORDS = ['lawsuit', 'investigation', 'recall', 'fine', 'penalty', 'downgrade', 'miss', 'loss', 'decline']

    # Positive sentiment keywords
    POSITIVE_KEYWORDS = ['beat', 'exceed', 'approval', 'success', 'award', 'growth', 'gain', 'strong', 'positive', 'upside', 'upgrade', 'bull']

    # Negative sentiment keywords
    NEGATIVE_KEYWORDS = ['miss', 'loss', 'decline', 'fail', 'lawsuit', 'investigation', 'fine', 'downgrade', 'bear', 'risk', 'threat', 'warning']

    def __init__(self):
        """Initialize CatalystDetector"""
        self.recency_window_days = 14
        self.min_confidence = 0.5

    def detect_catalyst_type(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect the type of catalyst from event data

        Args:
            event: Event dict with title, description, etc.

        Returns:
            Dict with detected type and confidence score
        """
        title = (event.get('title', '') + ' ' + event.get('description', '')).lower()

        # Check for earnings
        if any(keyword in title for keyword in self.EARNINGS_KEYWORDS):
            return {'type': CatalystType.EARNINGS, 'confidence': 0.95}

        # Check for acquisitions/mergers
        if any(keyword in title for keyword in self.ACQUISITION_KEYWORDS):
            return {'type': CatalystType.CORPORATE_EVENT, 'confidence': 0.90}

        # Check for product launches
        if any(keyword in title for keyword in self.PRODUCT_KEYWORDS):
            return {'type': CatalystType.OPPORTUNITY, 'confidence': 0.85}

        # Check for regulatory
        if any(keyword in title for keyword in self.REGULATORY_KEYWORDS):
            return {'type': CatalystType.REGULATORY, 'confidence': 0.85}

        # Check for threats
        if any(keyword in title for keyword in self.THREAT_KEYWORDS):
            return {'type': CatalystType.THREAT, 'confidence': 0.80}

        # Default to news event
        return {'type': CatalystType.NEWS_EVENT, 'confidence': 0.70}

    def classify_sentiment(self, text: str) -> CatalystSentiment:
        """
        Classify sentiment of catalyst text

        Args:
            text: Title or description

        Returns:
            CatalystSentiment value
        """
        text_lower = text.lower()

        positive_count = sum(1 for keyword in self.POSITIVE_KEYWORDS if keyword in text_lower)
        negative_count = sum(1 for keyword in self.NEGATIVE_KEYWORDS if keyword in text_lower)

        if positive_count > negative_count:
            return CatalystSentiment.POSITIVE
        elif negative_count > positive_count:
            return CatalystSentiment.NEGATIVE
        else:
            return CatalystSentiment.NEUTRAL

    def calculate_recency_weight(self, event_date: datetime) -> float:
        """
        Calculate weight based on event age. Recent events are most relevant.

        Args:
            event_date: When event occurred

        Returns:
            Weight 0-1, higher = more recent
        """
        now = datetime.now(pytz.UTC)
        if event_date.tzinfo is None:
            event_date = pytz.UTC.localize(event_date)

        days_old = (now - event_date).days

        if days_old < 0:  # Future event
            return 1.0
        elif days_old <= 14:  # Recent (within 2 weeks)
            return 1.0 - (days_old / 14.0) * 0.5  # 1.0 to 0.5
        elif days_old <= 30:  # Last month
            return 0.5 - ((days_old - 14) / 16.0) * 0.3  # 0.5 to 0.2
        else:  # Older than a month
            return max(0, 0.2 - ((min(days_old - 30, 30) / 30.0) * 0.2))  # 0.2 to 0

    def calculate_confidence_score(self, catalyst: Dict[str, Any]) -> float:
        """
        Calculate confidence that this is a meaningful catalyst

        Factors: type detection confidence, source reliability, confirmation count

        Args:
            catalyst: Catalyst dict

        Returns:
            Confidence score 0-1
        """
        confidence = catalyst.get('type_confidence', 0.7)

        # Boost for verified sources
        source = catalyst.get('source', '').lower()
        if source == 'finnhub':
            confidence = min(1.0, confidence + 0.1)
        elif source in ['sec', 'official']:
            confidence = min(1.0, confidence + 0.15)

        # Boost for multiple confirmations
        confirmation_count = catalyst.get('confirmation_count', 1)
        if confirmation_count > 1:
            confidence = min(1.0, confidence + (0.05 * (confirmation_count - 1)))

        return confidence

    def is_catalyst_still_relevant(self, catalyst: Dict[str, Any]) -> bool:
        """
        Check if catalyst is still relevant for intraday trading

        Args:
            catalyst: Catalyst data

        Returns:
            True if still relevant
        """
        event_date = catalyst.get('event_date')
        if not event_date:
            return True

        now = datetime.now(pytz.UTC)
        if event_date.tzinfo is None:
            event_date = pytz.UTC.localize(event_date)

        days_old = (now - event_date).days

        catalyst_type = catalyst.get('type')

        # Earnings impact lasts longer
        if catalyst_type == CatalystType.EARNINGS:
            return days_old < 7

        # News events are more timely
        if catalyst_type == CatalystType.NEWS_EVENT:
            return days_old < 3

        # Regulatory changes can be longer term
        if catalyst_type == CatalystType.REGULATORY:
            return days_old < 30

        # Threats can persist
        if catalyst_type == CatalystType.THREAT:
            return days_old < 14

        # Default: 2 weeks
        return days_old < 14

    def deduplicate_catalysts(self, catalysts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate catalysts, keeping highest confidence version

        Args:
            catalysts: List of catalyst dicts

        Returns:
            Deduplicated list
        """
        seen = {}

        for catalyst in sorted(catalysts, key=lambda x: x.get('confidence_score', 0), reverse=True):
            key = (
                catalyst.get('symbol'),
                catalyst.get('type'),
                catalyst.get('title', '')[:50]
            )

            if key not in seen:
                seen[key] = catalyst

        return list(seen.values())
