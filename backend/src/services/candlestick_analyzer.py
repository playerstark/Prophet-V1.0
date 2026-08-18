from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np
from src.models import CandleColor, CandlePattern, CandlePosition


class CandlestickAnalyzer:
    """
    Analyzes candlestick patterns and candle quality for stocks.

    Detects:
    - Candle colors (bullish, bearish, doji, hammer, hanging man)
    - Single candle patterns (doji, hammer, etc.)
    - Multi-candle patterns (engulfing, harami, morning/evening star, etc.)
    - Price position relative to technical levels
    - Volume confirmation
    - Pattern strength and reliability
    """

    def __init__(self):
        """Initialize CandlestickAnalyzer with thresholds"""
        # Doji threshold: body < 0.5% of range
        self.doji_threshold = 0.005

        # Hammer/Hanging Man: small body, long lower wick
        self.hammer_body_ratio = 0.3  # Body < 30% of range
        self.hammer_wick_ratio = 2.0  # Lower wick > 2x body

        # Engulfing: previous body completely inside current body
        self.engulfing_threshold = 0.05  # 5% overlap tolerance

        # Pattern strength thresholds
        self.strong_pattern_threshold = 0.75
        self.weak_pattern_threshold = 0.40

    def classify_candle_color(
        self,
        open_price: float,
        close_price: float,
        high: float,
        low: float,
        doji_threshold: float = None
    ) -> CandleColor:
        """Classify candle color (bullish, bearish, doji, hammer, hanging_man)."""
        if doji_threshold is None:
            doji_threshold = self.doji_threshold

        body = abs(close_price - open_price)
        range_size = high - low

        # Check for doji (very small body)
        if range_size > 0 and (body / range_size) < doji_threshold:
            return CandleColor.DOJI

        # Check for hammer (small body, long lower wick, close near high)
        if range_size > 0:
            lower_wick = min(open_price, close_price) - low
            body_ratio = body / range_size if range_size > 0 else 0
            wick_ratio = lower_wick / body if body > 0 else 0

            if body_ratio < self.hammer_body_ratio and wick_ratio > self.hammer_wick_ratio:
                return CandleColor.HAMMER

            # Check for hanging man (similar to hammer but bearish context)
            if body_ratio < self.hammer_body_ratio and wick_ratio > self.hammer_wick_ratio:
                if close_price < open_price:
                    return CandleColor.HANGING_MAN

        # Regular bullish or bearish
        if close_price > open_price:
            return CandleColor.BULLISH
        else:
            return CandleColor.BEARISH

    def calculate_candle_properties(self, open_p: float, high: float, low: float, close_p: float, volume: float = 1.0) -> Dict[str, float]:
        """Calculate candle body, wicks, and ratios."""
        candle_range = high - low
        body = close_p - open_p
        upper_wick = high - max(open_p, close_p)
        lower_wick = min(open_p, close_p) - low

        if candle_range > 0:
            body_strength = abs(body) / candle_range
            wick_strength = (upper_wick + lower_wick) / candle_range if (upper_wick + lower_wick) > 0 else 0
        else:
            body_strength = 0
            wick_strength = 0

        return {
            'range': candle_range,
            'body': body,
            'upper_wick': upper_wick,
            'lower_wick': lower_wick,
            'body_strength': body_strength,
            'wick_strength': wick_strength
        }

    def get_candle_size(self, body_strength: float) -> str:
        """Classify candle size based on body strength."""
        if body_strength > 0.6:
            return "large"
        elif body_strength > 0.3:
            return "medium"
        else:
            return "small"

    def detect_hammer_pattern(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect hammer pattern (reversal at bottom)."""
        if len(ohlcv) < 2:
            return None

        current = ohlcv.iloc[-1]
        props = self.calculate_candle_properties(
            current['Open'], current['High'], current['Low'], current['Close']
        )

        if props['body_strength'] < self.hammer_body_ratio:
            wick_ratio = props['lower_wick'] / abs(props['body']) if props['body'] != 0 else 0
            if wick_ratio > self.hammer_wick_ratio:
                return {
                    'type': 'hammer',
                    'confidence': 0.85,
                    'reversal': True
                }

        return None

    def detect_engulfing_pattern(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect bullish/bearish engulfing pattern (reversal)."""
        if len(ohlcv) < 2:
            return None

        prev = ohlcv.iloc[-2]
        curr = ohlcv.iloc[-1]

        prev_open = prev['Open']
        prev_close = prev['Close']
        prev_high = prev['High']
        prev_low = prev['Low']

        curr_open = curr['Open']
        curr_close = curr['Close']
        curr_high = curr['High']
        curr_low = curr['Low']

        # Bullish engulfing: prev bearish, curr bullish, curr completely engulfs prev
        if prev_close < prev_open and curr_close > curr_open:
            if curr_open <= prev_close and curr_close >= prev_open:
                if curr_close > prev_close and curr_open < prev_open:
                    return {
                        'pattern': CandlePattern.ENGULFING,
                        'direction': 'bullish',
                        'confidence': 0.90,
                        'reversal': True
                    }

        # Bearish engulfing: prev bullish, curr bearish, curr completely engulfs prev
        if prev_close > prev_open and curr_close < curr_open:
            if curr_open >= prev_close and curr_close <= prev_open:
                if curr_close < prev_close and curr_open > prev_open:
                    return {
                        'pattern': CandlePattern.ENGULFING,
                        'direction': 'bearish',
                        'confidence': 0.90,
                        'reversal': True
                    }

        return None

    def detect_harami_pattern(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect harami pattern (inside bar reversal signal)."""
        if len(ohlcv) < 2:
            return None

        prev = ohlcv.iloc[-2]
        curr = ohlcv.iloc[-1]

        prev_range = prev['High'] - prev['Low']
        curr_high = curr['High']
        curr_low = curr['Low']
        curr_open = curr['Open']
        curr_close = curr['Close']

        # Current candle inside previous candle's range
        if curr_high < prev['High'] and curr_low > prev['Low']:
            # Small body relative to range
            curr_body = abs(curr_close - curr_open)
            if curr_body / prev_range < 0.3:
                return {
                    'pattern': CandlePattern.HARAMI,
                    'confidence': 0.80,
                    'reversal': True
                }

        return None

    def detect_morning_star_pattern(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect morning star pattern (reversal from downtrend)."""
        if len(ohlcv) < 3:
            return None

        bar1 = ohlcv.iloc[-3]
        bar2 = ohlcv.iloc[-2]
        bar3 = ohlcv.iloc[-1]

        # Bar 1: bearish (downtrend)
        # Bar 2: small body (indecision)
        # Bar 3: bullish close above bar1 midpoint
        if (bar1['Close'] < bar1['Open'] and  # Bar 1 bearish
            abs(bar2['Close'] - bar2['Open']) < (bar1['High'] - bar1['Low']) * 0.3 and  # Bar 2 small body
            bar3['Close'] > bar1['Open']):  # Bar 3 bullish

            midpoint = (bar1['Open'] + bar1['Close']) / 2
            if bar3['Close'] > midpoint:
                return {
                    'pattern': CandlePattern.MORNING_STAR,
                    'confidence': 0.85,
                    'reversal': True
                }

        return None

    def detect_evening_star_pattern(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect evening star pattern (reversal from uptrend)."""
        if len(ohlcv) < 3:
            return None

        bar1 = ohlcv.iloc[-3]
        bar2 = ohlcv.iloc[-2]
        bar3 = ohlcv.iloc[-1]

        # Bar 1: bullish (uptrend)
        # Bar 2: small body (indecision)
        # Bar 3: bearish close below bar1 midpoint
        if (bar1['Close'] > bar1['Open'] and  # Bar 1 bullish
            abs(bar2['Close'] - bar2['Open']) < (bar1['High'] - bar1['Low']) * 0.3 and  # Bar 2 small body
            bar3['Close'] < bar1['Open']):  # Bar 3 bearish

            midpoint = (bar1['Open'] + bar1['Close']) / 2
            if bar3['Close'] < midpoint:
                return {
                    'pattern': CandlePattern.EVENING_STAR,
                    'confidence': 0.85,
                    'reversal': True
                }

        return None

    def detect_three_white_soldiers(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect three white soldiers pattern (bullish continuation)."""
        if len(ohlcv) < 3:
            return None

        bar1 = ohlcv.iloc[-3]
        bar2 = ohlcv.iloc[-2]
        bar3 = ohlcv.iloc[-1]

        # Three consecutive bullish candles with each close > previous close
        if (bar1['Close'] > bar1['Open'] and
            bar2['Close'] > bar2['Open'] and
            bar3['Close'] > bar3['Open'] and
            bar2['Close'] > bar1['Close'] and
            bar3['Close'] > bar2['Close']):

            return {
                'pattern': CandlePattern.THREE_WHITE_SOLDIERS,
                'confidence': 0.85,
                'continuation': True
            }

        return None

    def detect_three_black_crows(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect three black crows pattern (bearish continuation)."""
        if len(ohlcv) < 3:
            return None

        bar1 = ohlcv.iloc[-3]
        bar2 = ohlcv.iloc[-2]
        bar3 = ohlcv.iloc[-1]

        # Three consecutive bearish candles with each close < previous close
        if (bar1['Close'] < bar1['Open'] and
            bar2['Close'] < bar2['Open'] and
            bar3['Close'] < bar3['Open'] and
            bar2['Close'] < bar1['Close'] and
            bar3['Close'] < bar2['Close']):

            return {
                'pattern': CandlePattern.THREE_BLACK_CROWS,
                'confidence': 0.85,
                'continuation': True
            }

        return None

    def get_candle_position(
        self,
        close: float,
        ma20: Optional[float],
        ma50: Optional[float],
        bb_upper: Optional[float],
        bb_lower: Optional[float]
    ) -> Tuple[CandlePosition, Dict[str, float]]:
        """Determine candle position relative to technical levels."""
        distances = {
            'from_ma20': None,
            'from_ma50': None,
            'from_upper_bb': None,
            'from_lower_bb': None
        }

        if bb_upper and close > bb_upper:
            return CandlePosition.ABOVE_UPPER_BB, distances

        if ma20 and close > ma20:
            if distances['from_ma20'] is None:
                distances['from_ma20'] = ((close - ma20) / ma20) * 100

            if ma50 and close > ma50:
                distances['from_ma50'] = ((close - ma50) / ma50) * 100
                return CandlePosition.ABOVE_MA50, distances
            else:
                return CandlePosition.ABOVE_MA20, distances

        if ma50 and close > ma50:
            distances['from_ma50'] = ((close - ma50) / ma50) * 100
            return CandlePosition.BETWEEN_MA20_MA50, distances

        if ma50 and close < ma50:
            distances['from_ma50'] = ((close - ma50) / ma50) * 100
            return CandlePosition.BELOW_MA50, distances

        if bb_lower and close < bb_lower:
            distances['from_lower_bb'] = ((close - bb_lower) / bb_lower) * 100
            return CandlePosition.BELOW_LOWER_BB, distances

        return CandlePosition.NEAR_SUPPORT, distances

    def analyze_volume_confirmation(
        self,
        ohlcv: pd.DataFrame,
        candle_color: CandleColor
    ) -> Tuple[bool, float, str]:
        """Analyze volume confirmation for candle signal."""
        if len(ohlcv) < 5 or 'Volume' not in ohlcv.columns:
            return False, 0.5, "neutral"

        current_vol = ohlcv['Volume'].iloc[-1]
        avg_vol = ohlcv['Volume'].tail(5).mean()
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0

        volume_trend = "increasing" if current_vol > avg_vol else "decreasing"

        # Volume confirmation depends on signal
        if candle_color in [CandleColor.BULLISH, CandleColor.HAMMER]:
            # Bullish signals benefit from increasing volume
            confirmed = vol_ratio > 1.2
            confidence = min(0.95, vol_ratio * 0.5)
        elif candle_color in [CandleColor.BEARISH, CandleColor.HANGING_MAN]:
            # Bearish signals benefit from increasing volume
            confirmed = vol_ratio > 1.2
            confidence = min(0.95, vol_ratio * 0.5)
        else:
            confirmed = vol_ratio > 1.1
            confidence = 0.6

        return confirmed, confidence, volume_trend

    def calculate_candle_quality_score(
        self,
        open_p: float,
        high: float,
        low: float,
        close_p: float,
        pattern_confidence: float = 0.5,
        volume_confirmed: bool = False
    ) -> float:
        """Calculate overall candle quality score (0-1)."""
        props = self.calculate_candle_properties(open_p, high, low, close_p)

        # Score based on body strength (0-1)
        body_score = min(1.0, props['body_strength'] * 1.5)

        # Score based on pattern (external input)
        pattern_score = pattern_confidence

        # Volume bonus
        volume_bonus = 0.1 if volume_confirmed else 0

        # Composite score
        quality = (body_score * 0.4 + pattern_score * 0.5 + volume_bonus * 0.1)

        return max(0, min(1, quality))

    def is_rejection_candle(self, ohlcv: pd.DataFrame, level: float) -> bool:
        """Detect if current candle rejects a technical level."""
        if len(ohlcv) < 1:
            return False

        curr = ohlcv.iloc[-1]
        # Price touched level but closed away from it
        return (curr['High'] >= level and curr['Close'] < level - (curr['High'] - curr['Close']))

    def is_inside_bar(self, ohlcv: pd.DataFrame) -> bool:
        """Detect inside bar (current bar inside previous bar's range)."""
        if len(ohlcv) < 2:
            return False

        prev = ohlcv.iloc[-2]
        curr = ohlcv.iloc[-1]

        return (curr['High'] < prev['High'] and curr['Low'] > prev['Low'])

    def is_pin_bar(self, ohlcv: pd.DataFrame) -> bool:
        """Detect pin bar (long wick rejection at level)."""
        if len(ohlcv) < 1:
            return False

        curr = ohlcv.iloc[-1]
        props = self.calculate_candle_properties(
            curr['Open'], curr['High'], curr['Low'], curr['Close']
        )

        # Long wick with small body
        return (props['wick_strength'] > 2.0 and props['body_strength'] < 0.3)

    def analyze_candle(
        self,
        ohlcv: pd.DataFrame,
        ma20: Optional[float] = None,
        ma50: Optional[float] = None,
        bb_upper: Optional[float] = None,
        bb_lower: Optional[float] = None
    ) -> Dict[str, any]:
        """Comprehensive candlestick analysis."""
        if ohlcv.empty:
            return {}

        current = ohlcv.iloc[-1]
        open_p = current['Open']
        high = current['High']
        low = current['Low']
        close = current['Close']
        volume = current.get('Volume', 1.0)

        results = {}

        # Basic candle properties
        results['color'] = self.classify_candle_color(open_p, close, high, low)
        props = self.calculate_candle_properties(open_p, high, low, close)
        results.update({
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
            'range': props['range'],
            'body': props['body'],
            'upper_wick': props['upper_wick'],
            'lower_wick': props['lower_wick'],
            'body_strength': props['body_strength'],
            'candle_size': self.get_candle_size(props['body_strength'])
        })

        # Position relative to technical levels
        position, distances = self.get_candle_position(close, ma20, ma50, bb_upper, bb_lower)
        results['position'] = position
        results.update(distances)

        # Pattern detection
        patterns_found = []
        pattern_confidence = 0.5

        if hammer := self.detect_hammer_pattern(ohlcv):
            patterns_found.append(hammer)
            pattern_confidence = max(pattern_confidence, hammer['confidence'])

        if engulfing := self.detect_engulfing_pattern(ohlcv):
            patterns_found.append(engulfing)
            pattern_confidence = max(pattern_confidence, engulfing['confidence'])

        if harami := self.detect_harami_pattern(ohlcv):
            patterns_found.append(harami)
            pattern_confidence = max(pattern_confidence, harami['confidence'])

        if morning_star := self.detect_morning_star_pattern(ohlcv):
            patterns_found.append(morning_star)
            pattern_confidence = max(pattern_confidence, morning_star['confidence'])

        if evening_star := self.detect_evening_star_pattern(ohlcv):
            patterns_found.append(evening_star)
            pattern_confidence = max(pattern_confidence, evening_star['confidence'])

        if three_white := self.detect_three_white_soldiers(ohlcv):
            patterns_found.append(three_white)
            pattern_confidence = max(pattern_confidence, three_white['confidence'])

        if three_black := self.detect_three_black_crows(ohlcv):
            patterns_found.append(three_black)
            pattern_confidence = max(pattern_confidence, three_black['confidence'])

        results['patterns_found'] = patterns_found
        results['pattern_count'] = len(patterns_found)
        results['primary_pattern'] = patterns_found[0] if patterns_found else None

        # Volume analysis
        vol_confirmed, vol_confidence, vol_trend = self.analyze_volume_confirmation(ohlcv, results['color'])
        results.update({
            'volume_confirmed': vol_confirmed,
            'volume_confidence': vol_confidence,
            'volume_trend': vol_trend,
            'volume': volume
        })

        # Risk/signal detection
        results['is_rejection'] = self.is_rejection_candle(ohlcv, level=(bb_upper or close))
        results['is_inside_bar'] = self.is_inside_bar(ohlcv)
        results['is_pin_bar'] = self.is_pin_bar(ohlcv)

        # Quality scoring
        results['quality_score'] = self.calculate_candle_quality_score(
            open_p, high, low, close,
            pattern_confidence=pattern_confidence,
            volume_confirmed=vol_confirmed
        )

        return results
