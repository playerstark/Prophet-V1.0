from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from sqlalchemy.orm import Session
from src.models import (
    PriceVolumeAnomaly, VolatilityTrendSignal, CandlestickSignal,
    TradeDirection, OpportunityRating
)


class ConfluenceAnalyzer:
    """
    Final confluence analyzer that combines all 5 filter signals.

    Produces:
    - Multi-signal agreement scoring
    - Final opportunity ranking
    - Noise reduction assessment
    - Trade direction and confidence
    """

    def __init__(self):
        """Initialize ConfluenceAnalyzer with scoring parameters"""
        # Confidence thresholds
        self.high_confidence_threshold = 0.75
        self.moderate_confidence_threshold = 0.60
        self.low_noise_threshold = 0.70

        # Agreement thresholds for ratings
        self.strong_consensus_threshold = 4  # 4+ filters
        self.consensus_threshold = 3  # 3+ filters
        self.weak_consensus_threshold = 2  # 2+ filters

    def classify_signal(self, signal_strength: float) -> str:
        """Convert signal strength to direction label."""
        if signal_strength > 0.5:
            return "bullish"
        elif signal_strength < 0.4:
            return "bearish"
        else:
            return "neutral"

    def get_latest_signals(
        self,
        symbol: str,
        db: Session,
        lookback_hours: int = 4
    ) -> Dict[str, any]:
        """Get latest signals from all filters for a symbol."""
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)

        signals = {
            'catalyst': None,
            'anomaly': None,
            'trend': None,
            'candle': None
        }

        # Get latest from each filter
        signals['anomaly'] = db.query(PriceVolumeAnomaly).filter(
            PriceVolumeAnomaly.symbol == symbol,
            PriceVolumeAnomaly.detected_at > cutoff_time
        ).order_by(PriceVolumeAnomaly.detected_at.desc()).first()

        signals['trend'] = db.query(VolatilityTrendSignal).filter(
            VolatilityTrendSignal.symbol == symbol,
            VolatilityTrendSignal.detected_at > cutoff_time
        ).order_by(VolatilityTrendSignal.detected_at.desc()).first()

        signals['candle'] = db.query(CandlestickSignal).filter(
            CandlestickSignal.symbol == symbol,
            CandlestickSignal.detected_at > cutoff_time
        ).order_by(CandlestickSignal.detected_at.desc()).first()

        return signals

    def analyze_signal_agreement(
        self,
        signals: Dict[str, any]
    ) -> Dict[str, any]:
        """Analyze agreement across all filters."""
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        signal_strengths = []

        # Analyze anomaly signal
        if signals.get('anomaly'):
            anomaly = signals['anomaly']
            # Price breakouts and volume spikes are bullish
            if anomaly.technical_confirmation_score > 0.6:
                bullish_count += 1
                signal_strengths.append(anomaly.technical_confirmation_score)
            elif anomaly.is_manipulation_risk:
                bearish_count += 1
                signal_strengths.append(0.5)
            else:
                neutral_count += 1

        # Analyze trend signal
        if signals.get('trend'):
            trend = signals['trend']
            if trend.trend_type.value.startswith('uptrend'):
                bullish_count += 1
                signal_strengths.append(trend.trend_strength)
            elif trend.trend_type.value.startswith('downtrend'):
                bearish_count += 1
                signal_strengths.append(trend.trend_strength)
            else:
                neutral_count += 1

        # Analyze candle signal
        if signals.get('candle'):
            candle = signals['candle']
            if candle.candle_color.value == 'bullish':
                bullish_count += 1
                signal_strengths.append(candle.candle_quality_score)
            elif candle.candle_color.value == 'bearish':
                bearish_count += 1
                signal_strengths.append(candle.candle_quality_score)
            else:
                neutral_count += 1

        total_filters = bullish_count + bearish_count + neutral_count
        if total_filters == 0:
            total_filters = 1

        # Calculate metrics
        bullish_percentage = bullish_count / total_filters
        bearish_percentage = bearish_count / total_filters
        agreement_score = max(bullish_count, bearish_count) / total_filters

        avg_strength = sum(signal_strengths) / len(signal_strengths) if signal_strengths else 0.5

        return {
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'total_filters': total_filters,
            'bullish_percentage': bullish_percentage,
            'bearish_percentage': bearish_percentage,
            'agreement_score': agreement_score,
            'avg_strength': avg_strength
        }

    def determine_direction(self, agreement: Dict[str, any]) -> Tuple[TradeDirection, float]:
        """Determine trade direction from agreement analysis."""
        bullish_pct = agreement['bullish_percentage']
        bearish_pct = agreement['bearish_percentage']
        strength = agreement['avg_strength']

        if bullish_pct > bearish_pct:
            return TradeDirection.LONG, strength
        elif bearish_pct > bullish_pct:
            return TradeDirection.SHORT, strength
        else:
            return TradeDirection.NEUTRAL, 0.5

    def determine_rating(
        self,
        direction: TradeDirection,
        agreement: Dict[str, any],
        confidence: float
    ) -> OpportunityRating:
        """Determine opportunity rating based on signals and confidence."""
        bullish_count = agreement['bullish_count']
        bearish_count = agreement['bearish_count']

        # Strong buy: 4+ bullish filters, high confidence
        if bullish_count >= self.strong_consensus_threshold and confidence > 0.80:
            return OpportunityRating.STRONG_BUY

        # Buy: 3+ bullish filters, moderate confidence
        if bullish_count >= self.consensus_threshold and confidence > 0.65:
            return OpportunityRating.BUY

        # Strong sell: 4+ bearish filters, high confidence
        if bearish_count >= self.strong_consensus_threshold and confidence > 0.80:
            return OpportunityRating.STRONG_SELL

        # Sell: 3+ bearish filters, moderate confidence
        if bearish_count >= self.consensus_threshold and confidence > 0.65:
            return OpportunityRating.SELL

        # Neutral: mixed or weak signals
        return OpportunityRating.NEUTRAL

    def calculate_noise_reduction(self, signals: Dict[str, any]) -> float:
        """
        Calculate how clean the signal is (0-1).
        Higher = cleaner, less noisy.
        """
        signal_count = sum(1 for v in signals.values() if v is not None)

        if signal_count == 0:
            return 0.0

        clarity = 0.3  # Base clarity

        # More signals = better clarity
        if signal_count >= 3:
            clarity += 0.4
        elif signal_count == 2:
            clarity += 0.2

        # Check signal alignment
        anomaly = signals.get('anomaly')
        trend = signals.get('trend')
        candle = signals.get('candle')

        aligned_signals = 0

        # Check if trend and candle align
        if trend and candle:
            trend_bullish = trend.trend_type.value.startswith('uptrend')
            candle_bullish = candle.candle_color.value == 'bullish'
            if trend_bullish == candle_bullish:
                aligned_signals += 1

        # Check if anomaly supports trend
        if anomaly and trend:
            anomaly_bullish = anomaly.technical_confirmation_score > 0.6
            trend_bullish = trend.trend_type.value.startswith('uptrend')
            if anomaly_bullish == trend_bullish:
                aligned_signals += 1

        clarity += (aligned_signals * 0.15)

        return min(1.0, clarity)

    def calculate_overall_confidence(
        self,
        agreement: Dict[str, any],
        noise_reduction: float
    ) -> float:
        """Calculate final confidence score."""
        # Base confidence from agreement
        consensus_confidence = agreement['agreement_score'] * 0.6
        strength_confidence = agreement['avg_strength'] * 0.4

        # Combine with noise reduction (cleaner signals = more confident)
        final_confidence = (
            (consensus_confidence + strength_confidence) * 0.7 +
            noise_reduction * 0.3
        )

        return min(1.0, max(0.0, final_confidence))

    def analyze_confluence(
        self,
        symbol: str,
        db: Session
    ) -> Dict[str, any]:
        """Complete confluence analysis for a symbol."""
        # Get all signals
        signals = self.get_latest_signals(symbol, db)

        # Analyze agreement
        agreement = self.analyze_signal_agreement(signals)

        # Determine direction
        direction, direction_strength = self.determine_direction(agreement)

        # Calculate noise
        noise_reduction = self.calculate_noise_reduction(signals)

        # Calculate confidence
        confidence = self.calculate_overall_confidence(agreement, noise_reduction)

        # Determine rating
        rating = self.determine_rating(direction, agreement, confidence)

        # Build key signals list
        key_signals = []
        if agreement['bullish_count'] > 0:
            key_signals.append(f"{agreement['bullish_count']} bullish filters")
        if agreement['bearish_count'] > 0:
            key_signals.append(f"{agreement['bearish_count']} bearish filters")

        # Determine if high probability
        is_high_prob = confidence > self.high_confidence_threshold
        is_low_noise = noise_reduction > self.low_noise_threshold
        requires_confirmation = confidence < self.moderate_confidence_threshold

        results = {
            'symbol': symbol,
            'direction': direction,
            'rating': rating,
            'direction_strength': direction_strength,
            'bullish_count': agreement['bullish_count'],
            'bearish_count': agreement['bearish_count'],
            'neutral_count': agreement['neutral_count'],
            'total_filters': agreement['total_filters'],
            'agreement_score': agreement['agreement_score'],
            'filter_consensus_score': agreement['agreement_score'],
            'signal_strength_score': agreement['avg_strength'],
            'noise_reduction_factor': noise_reduction,
            'overall_confidence': confidence,
            'is_high_probability': is_high_prob,
            'is_low_noise': is_low_noise,
            'requires_confirmation': requires_confirmation,
            'key_signals': ', '.join(key_signals) if key_signals else 'Mixed signals',
            'risk_score': 1.0 - noise_reduction,  # More noise = more risk
            'signals': signals
        }

        return results
