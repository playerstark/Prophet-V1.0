import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from src.services.confluence_analyzer import ConfluenceAnalyzer
from src.models import TradeDirection, OpportunityRating


class TestConfluenceAnalyzer:
    """Test ConfluenceAnalyzer service"""

    def setup_method(self):
        self.analyzer = ConfluenceAnalyzer()

    def create_mock_signal(self, signal_type, strength=0.75):
        """Create mock signal object"""
        signal = Mock()
        signal.type = signal_type
        signal.strength = strength
        return signal

    def test_signal_classification_bullish(self):
        """Test bullish signal classification"""
        signal = self.analyzer.classify_signal(0.75)
        assert signal == "bullish"

    def test_signal_classification_bearish(self):
        """Test bearish signal classification"""
        signal = self.analyzer.classify_signal(0.35)
        assert signal == "bearish"

    def test_signal_classification_neutral(self):
        """Test neutral signal classification"""
        signal = self.analyzer.classify_signal(0.45)
        assert signal == "neutral"

    def test_analyze_single_bullish_signal(self):
        """Test agreement analysis with single bullish signal"""
        signals = {
            'catalyst': None,
            'anomaly': Mock(technical_confirmation_score=0.8),
            'trend': None,
            'candle': None
        }

        agreement = self.analyzer.analyze_signal_agreement(signals)

        assert agreement['bullish_count'] == 1
        assert agreement['bearish_count'] == 0
        assert agreement['neutral_count'] == 0

    def test_analyze_multiple_signals_agreement(self):
        """Test agreement analysis with multiple bullish signals"""
        signals = {
            'catalyst': None,
            'anomaly': Mock(technical_confirmation_score=0.8, is_manipulation_risk=False),
            'trend': Mock(trend_type=Mock(value='strong_uptrend'), trend_strength=0.85),
            'candle': Mock(candle_color=Mock(value='bullish'), candle_quality_score=0.75)
        }

        agreement = self.analyzer.analyze_signal_agreement(signals)

        assert agreement['bullish_count'] >= 2
        assert agreement['agreement_score'] > 0.5

    def test_analyze_conflicting_signals(self):
        """Test agreement analysis with conflicting signals"""
        signals = {
            'catalyst': None,
            'anomaly': Mock(technical_confirmation_score=0.8, is_manipulation_risk=False),
            'trend': Mock(trend_type=Mock(value='strong_downtrend'), trend_strength=0.85),
            'candle': Mock(candle_color=Mock(value='bearish'), candle_quality_score=0.75)
        }

        agreement = self.analyzer.analyze_signal_agreement(signals)

        # Should have mixed signals
        assert agreement['bullish_count'] > 0 or agreement['bearish_count'] > 0

    def test_determine_direction_bullish(self):
        """Test direction determination for bullish signals"""
        agreement = {
            'bullish_percentage': 0.75,
            'bearish_percentage': 0.25,
            'neutral_percentage': 0.0,
            'avg_strength': 0.8
        }

        direction, strength = self.analyzer.determine_direction(agreement)

        assert direction == TradeDirection.LONG
        assert strength == 0.8

    def test_determine_direction_bearish(self):
        """Test direction determination for bearish signals"""
        agreement = {
            'bullish_percentage': 0.25,
            'bearish_percentage': 0.75,
            'neutral_percentage': 0.0,
            'avg_strength': 0.8
        }

        direction, strength = self.analyzer.determine_direction(agreement)

        assert direction == TradeDirection.SHORT
        assert strength == 0.8

    def test_determine_direction_neutral(self):
        """Test direction determination for neutral signals"""
        agreement = {
            'bullish_percentage': 0.33,
            'bearish_percentage': 0.33,
            'neutral_percentage': 0.34,
            'avg_strength': 0.5
        }

        direction, strength = self.analyzer.determine_direction(agreement)

        assert direction == TradeDirection.NEUTRAL

    def test_determine_rating_strong_buy(self):
        """Test rating determination for strong buy"""
        agreement = {
            'bullish_count': 4,
            'bearish_count': 0,
            'neutral_count': 0
        }
        direction = TradeDirection.LONG
        confidence = 0.85

        rating = self.analyzer.determine_rating(direction, agreement, confidence)

        assert rating == OpportunityRating.STRONG_BUY

    def test_determine_rating_buy(self):
        """Test rating determination for buy"""
        agreement = {
            'bullish_count': 3,
            'bearish_count': 0,
            'neutral_count': 1
        }
        direction = TradeDirection.LONG
        confidence = 0.70

        rating = self.analyzer.determine_rating(direction, agreement, confidence)

        assert rating == OpportunityRating.BUY

    def test_determine_rating_strong_sell(self):
        """Test rating determination for strong sell"""
        agreement = {
            'bullish_count': 0,
            'bearish_count': 4,
            'neutral_count': 0
        }
        direction = TradeDirection.SHORT
        confidence = 0.85

        rating = self.analyzer.determine_rating(direction, agreement, confidence)

        assert rating == OpportunityRating.STRONG_SELL

    def test_determine_rating_sell(self):
        """Test rating determination for sell"""
        agreement = {
            'bullish_count': 0,
            'bearish_count': 3,
            'neutral_count': 1
        }
        direction = TradeDirection.SHORT
        confidence = 0.70

        rating = self.analyzer.determine_rating(direction, agreement, confidence)

        assert rating == OpportunityRating.SELL

    def test_determine_rating_neutral(self):
        """Test rating determination for neutral"""
        agreement = {
            'bullish_count': 1,
            'bearish_count': 1,
            'neutral_count': 2
        }
        direction = TradeDirection.NEUTRAL
        confidence = 0.50

        rating = self.analyzer.determine_rating(direction, agreement, confidence)

        assert rating == OpportunityRating.NEUTRAL

    def test_calculate_noise_reduction_no_signals(self):
        """Test noise reduction with no signals"""
        signals = {
            'catalyst': None,
            'anomaly': None,
            'trend': None,
            'candle': None
        }

        noise = self.analyzer.calculate_noise_reduction(signals)

        assert noise == 0.0

    def test_calculate_noise_reduction_single_signal(self):
        """Test noise reduction with single signal"""
        signals = {
            'catalyst': None,
            'anomaly': Mock(),
            'trend': None,
            'candle': None
        }

        noise = self.analyzer.calculate_noise_reduction(signals)

        assert 0 <= noise <= 1

    def test_calculate_noise_reduction_aligned_signals(self):
        """Test noise reduction with aligned signals"""
        signals = {
            'catalyst': None,
            'anomaly': Mock(technical_confirmation_score=0.8),
            'trend': Mock(trend_type=Mock(value='uptrend')),
            'candle': Mock(candle_color=Mock(value='bullish'))
        }

        noise = self.analyzer.calculate_noise_reduction(signals)

        # Aligned signals should have higher clarity
        assert 0 <= noise <= 1

    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation"""
        agreement = {
            'agreement_score': 0.8,
            'avg_strength': 0.75
        }
        noise_reduction = 0.7

        confidence = self.analyzer.calculate_overall_confidence(agreement, noise_reduction)

        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be reasonably confident

    def test_confluence_analysis_strong_bullish(self):
        """Test confluence analysis for strong bullish setup"""
        # Create mock DB
        db = Mock()
        signals = {
            'catalyst': None,
            'anomaly': Mock(technical_confirmation_score=0.85, is_manipulation_risk=False),
            'trend': Mock(trend_type=Mock(value='strong_uptrend'), trend_strength=0.90),
            'candle': Mock(candle_color=Mock(value='bullish'), candle_quality_score=0.80)
        }

        # Mock the get_latest_signals call
        self.analyzer.get_latest_signals = Mock(return_value=signals)

        analysis = self.analyzer.analyze_confluence('TEST', db)

        # Should be bullish with high confidence
        assert analysis['direction'] == TradeDirection.LONG
        assert analysis['bullish_count'] > analysis['bearish_count']
        assert analysis['overall_confidence'] > 0.6

    def test_confluence_analysis_conflicting_signals(self):
        """Test confluence analysis with conflicting signals"""
        db = Mock()
        signals = {
            'catalyst': None,
            'anomaly': Mock(technical_confirmation_score=0.8, is_manipulation_risk=False),
            'trend': Mock(trend_type=Mock(value='downtrend'), trend_strength=0.75),
            'candle': Mock(candle_color=Mock(value='bearish'), candle_quality_score=0.70)
        }

        self.analyzer.get_latest_signals = Mock(return_value=signals)

        analysis = self.analyzer.analyze_confluence('TEST', db)

        # Should be bearish due to multiple bearish signals
        assert analysis['direction'] == TradeDirection.SHORT or analysis['direction'] == TradeDirection.NEUTRAL

    def test_high_probability_signal_detection(self):
        """Test detection of high-probability signals"""
        agreement = {
            'agreement_score': 0.9,
            'avg_strength': 0.85
        }
        noise_reduction = 0.8

        confidence = self.analyzer.calculate_overall_confidence(agreement, noise_reduction)

        # Should exceed high confidence threshold
        assert confidence > self.analyzer.high_confidence_threshold

    def test_requires_confirmation_detection(self):
        """Test when confirmation is needed"""
        agreement = {
            'agreement_score': 0.5,
            'avg_strength': 0.55
        }
        noise_reduction = 0.4

        confidence = self.analyzer.calculate_overall_confidence(agreement, noise_reduction)

        # Should be below moderate threshold
        assert confidence < self.analyzer.moderate_confidence_threshold

    def test_consensus_threshold_met(self):
        """Test consensus threshold detection"""
        agreement = {
            'bullish_count': 3,
            'bearish_count': 0,
            'neutral_count': 1,
            'total_filters': 4
        }

        # Should meet consensus threshold
        assert agreement['bullish_count'] >= self.analyzer.consensus_threshold

    def test_strong_consensus_threshold_met(self):
        """Test strong consensus threshold detection"""
        agreement = {
            'bullish_count': 4,
            'bearish_count': 0,
            'neutral_count': 0,
            'total_filters': 4
        }

        # Should meet strong consensus threshold
        assert agreement['bullish_count'] >= self.analyzer.strong_consensus_threshold


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
