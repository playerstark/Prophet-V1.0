from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np
from src.models import TrendType, BollingerBandPosition, MAAlignment


class VolatilityTrendAnalyzer:
    """
    Analyzes volatility and trend direction for stocks.

    Detects:
    - Bollinger Band position and expansion/contraction
    - Moving average direction and alignment
    - Trend type (strong up/down, sideways, etc.)
    - Volatility expansion/contraction
    - Trend continuation vs emerging trends
    """

    def __init__(self):
        """Initialize VolatilityTrendAnalyzer with thresholds"""
        # Bollinger Bands parameters
        self.bb_period = 20
        self.bb_std_dev = 2

        # Volatility thresholds
        self.high_volatility_atr_percentile = 0.75
        self.low_volatility_atr_percentile = 0.25

        # Trend strength thresholds
        self.strong_trend_threshold = 0.7
        self.weak_trend_threshold = 0.3

        # MA alignment thresholds
        self.bullish_ma_alignment_threshold = 0.15  # 15% difference threshold
        self.bearish_ma_alignment_threshold = -0.15

    def calculate_bollinger_bands(
        self,
        ohlcv: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        if len(ohlcv) < period:
            return {'upper': None, 'middle': None, 'lower': None, 'width': None}

        close = ohlcv['Close']

        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        width = upper - lower

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'width': width
        }

    def get_bb_position(
        self,
        price: float,
        bb_upper: float,
        bb_middle: float,
        bb_lower: float
    ) -> BollingerBandPosition:
        """Determine position of price relative to Bollinger Bands."""
        if price >= bb_upper:
            return BollingerBandPosition.ABOVE_UPPER
        elif price >= bb_middle + (bb_upper - bb_middle) * 0.75:
            return BollingerBandPosition.NEAR_UPPER
        elif price >= bb_middle - (bb_middle - bb_lower) * 0.75:
            return BollingerBandPosition.BETWEEN
        elif price >= bb_lower:
            return BollingerBandPosition.NEAR_LOWER
        else:
            return BollingerBandPosition.BELOW_LOWER

    def calculate_volatility_metrics(self, ohlcv: pd.DataFrame) -> Dict[str, any]:
        """Calculate volatility-related metrics."""
        if ohlcv.empty or len(ohlcv) < 14:
            return {}

        # ATR (Average True Range)
        high = ohlcv['High']
        low = ohlcv['Low']
        close = ohlcv['Close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()

        current_atr = atr.iloc[-1]
        current_volatility = (tr.iloc[-1] / close.iloc[-1]) * 100

        # Volatility trend
        if len(atr) >= 2:
            volatility_trend = "increasing" if atr.iloc[-1] > atr.iloc[-2] else "decreasing"
        else:
            volatility_trend = "neutral"

        return {
            'atr': current_atr,
            'volatility_percent': current_volatility,
            'volatility_trend': volatility_trend,
            'atr_series': atr
        }

    def calculate_ma_metrics(self, ohlcv: pd.DataFrame) -> Dict[str, any]:
        """Calculate moving average metrics and alignment."""
        if ohlcv.empty or len(ohlcv) < 50:
            return {}

        close = ohlcv['Close']

        ma_20 = close.rolling(window=20).mean()
        ma_50 = close.rolling(window=50).mean()
        ma_200 = close.rolling(window=200).mean() if len(close) >= 200 else None

        current_price = close.iloc[-1]
        current_ma20 = ma_20.iloc[-1]
        current_ma50 = ma_50.iloc[-1]
        current_ma200 = ma_200.iloc[-1] if ma_200 is not None else None

        # MA direction
        ma20_direction = "up" if ma_20.iloc[-1] > ma_20.iloc[-2] else "down"
        ma50_direction = "up" if ma_50.iloc[-1] > ma_50.iloc[-2] else "down"

        # MA slope (rate of change)
        if len(ma_20) >= 5:
            ma20_slope = (ma_20.iloc[-1] - ma_20.iloc[-5]) / ma_20.iloc[-5]
            ma50_slope = (ma_50.iloc[-1] - ma_50.iloc[-5]) / ma_50.iloc[-5]
        else:
            ma20_slope = 0
            ma50_slope = 0

        # MA alignment
        if ma_200 is not None:
            ma20_above_50 = current_ma20 > current_ma50
            ma50_above_200 = current_ma50 > current_ma200

            if ma20_above_50 and ma50_above_200:
                alignment = MAAlignment.BULLISH_ALIGNED
            elif not ma20_above_50 and not ma50_above_200:
                alignment = MAAlignment.BEARISH_ALIGNED
            else:
                alignment = MAAlignment.MIXED
        else:
            alignment = MAAlignment.NOT_ENOUGH_DATA

        # Price relative to MAs
        price_above_ma20 = current_price > current_ma20
        price_above_ma50 = current_price > current_ma50
        price_above_ma200 = current_price > current_ma200 if current_ma200 else None

        return {
            'ma_20': current_ma20,
            'ma_50': current_ma50,
            'ma_200': current_ma200,
            'ma_20_direction': ma20_direction,
            'ma_50_direction': ma50_direction,
            'ma_20_slope': ma20_slope,
            'ma_50_slope': ma50_slope,
            'ma_alignment': alignment,
            'price_above_ma20': price_above_ma20,
            'price_above_ma50': price_above_ma50,
            'price_above_ma200': price_above_ma200,
        }

    def classify_trend_type(self, ohlcv: pd.DataFrame) -> Tuple[TrendType, float]:
        """Classify trend type and calculate trend strength."""
        if len(ohlcv) < 50:
            return TrendType.SIDEWAYS, 0.5

        close = ohlcv['Close']
        ma_20 = close.rolling(window=20).mean()
        ma_50 = close.rolling(window=50).mean()

        current_price = close.iloc[-1]
        current_ma20 = ma_20.iloc[-1]
        current_ma50 = ma_50.iloc[-1]

        # Calculate trend strength based on distance from MAs
        ma20_distance = (current_price - current_ma20) / current_ma20
        ma50_distance = (current_price - current_ma50) / current_ma50

        combined_distance = (ma20_distance + ma50_distance) / 2

        # Determine trend type
        if combined_distance > 0.03:  # > 3% above MAs
            if ma_20.iloc[-1] > ma_50.iloc[-1]:
                trend_type = TrendType.STRONG_UPTREND
                strength = min(1.0, abs(combined_distance) * 10)
            else:
                trend_type = TrendType.UPTREND
                strength = min(1.0, abs(combined_distance) * 8)

        elif combined_distance < -0.03:  # < -3% below MAs
            if ma_20.iloc[-1] < ma_50.iloc[-1]:
                trend_type = TrendType.STRONG_DOWNTREND
                strength = min(1.0, abs(combined_distance) * 10)
            else:
                trend_type = TrendType.DOWNTREND
                strength = min(1.0, abs(combined_distance) * 8)

        else:
            trend_type = TrendType.SIDEWAYS
            strength = 1 - abs(combined_distance) * 50

        return trend_type, max(0, min(1, strength))

    def detect_trend_continuation(self, ohlcv: pd.DataFrame) -> bool:
        """Detect if current trend is continuing."""
        if len(ohlcv) < 20:
            return False

        close = ohlcv['Close']
        high = ohlcv['High']
        low = ohlcv['Low']

        # Check if recent highs/lows are making series
        recent_highs = high.tail(10).values
        recent_lows = low.tail(10).values

        # Uptrend: each high > previous high, each low > previous low
        uptrend_score = sum(
            1 for i in range(1, len(recent_highs))
            if recent_highs[i] > recent_highs[i-1] and recent_lows[i] > recent_lows[i-1]
        ) / (len(recent_highs) - 1)

        # Downtrend: each high < previous high, each low < previous low
        downtrend_score = sum(
            1 for i in range(1, len(recent_highs))
            if recent_highs[i] < recent_highs[i-1] and recent_lows[i] < recent_lows[i-1]
        ) / (len(recent_highs) - 1)

        return max(uptrend_score, downtrend_score) > 0.6

    def detect_emerging_trend(self, ohlcv: pd.DataFrame) -> bool:
        """Detect if new trend is forming."""
        if len(ohlcv) < 50:
            return False

        close = ohlcv['Close']
        returns = close.pct_change()

        # Calculate trend in recent bars vs earlier bars
        recent_returns = returns.tail(10).mean()
        earlier_returns = returns.iloc[-20:-10].mean()

        # New trend if direction change or significant acceleration
        direction_change = (recent_returns > 0) != (earlier_returns > 0)
        acceleration = abs(recent_returns) > abs(earlier_returns) * 1.5

        return direction_change or acceleration

    def detect_trend_exhaustion(self, ohlcv: pd.DataFrame) -> bool:
        """Detect potential trend reversal/exhaustion."""
        if len(ohlcv) < 20:
            return False

        close = ohlcv['Close']
        high = ohlcv['High']
        low = ohlcv['Low']

        # Check for divergence in momentum
        recent_price_change = (close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]
        recent_range = (high.tail(10).max() - low.tail(10).min()) / close.iloc[-1]

        # Exhaustion: small range relative to distance traveled
        # Indicates momentum may be fading
        exhaustion_ratio = abs(recent_price_change) / (recent_range + 0.001)

        return exhaustion_ratio > 2.5

    def score_trend_confirmation(self, ohlcv: pd.DataFrame) -> float:
        """Score how many signals confirm the current trend (0-1 scale)."""
        if len(ohlcv) < 50:
            return 0.5

        close = ohlcv['Close']
        ma_20 = close.rolling(window=20).mean()
        ma_50 = close.rolling(window=50).mean()

        confirmations = 0
        total_checks = 0

        # Check 1: Price above/below MA20
        total_checks += 1
        if close.iloc[-1] > ma_20.iloc[-1] and ma_20.iloc[-1] > ma_50.iloc[-1]:
            confirmations += 1
        elif close.iloc[-1] < ma_20.iloc[-1] and ma_20.iloc[-1] < ma_50.iloc[-1]:
            confirmations += 1

        # Check 2: MA direction
        total_checks += 1
        if ma_20.iloc[-1] > ma_20.iloc[-2] and ma_50.iloc[-1] > ma_50.iloc[-2]:
            confirmations += 1
        elif ma_20.iloc[-1] < ma_20.iloc[-2] and ma_50.iloc[-1] < ma_50.iloc[-2]:
            confirmations += 1

        # Check 3: Trend continuation
        total_checks += 1
        if self.detect_trend_continuation(ohlcv):
            confirmations += 1

        return confirmations / total_checks if total_checks > 0 else 0.5

    def score_volatility_confirmation(self, ohlcv: pd.DataFrame) -> float:
        """Score volatility metrics (0-1 scale)."""
        if len(ohlcv) < 50:
            return 0.5

        bb_data = self.calculate_bollinger_bands(ohlcv)
        vol_data = self.calculate_volatility_metrics(ohlcv)

        if bb_data['width'] is None or not vol_data:
            return 0.5

        confirmations = 0
        total_checks = 0

        # Check 1: BB width expanding
        total_checks += 1
        if len(bb_data['width']) >= 2:
            if bb_data['width'].iloc[-1] > bb_data['width'].iloc[-2]:
                confirmations += 1

        # Check 2: Volatility trend
        total_checks += 1
        if vol_data.get('volatility_trend') == 'increasing':
            confirmations += 1

        return confirmations / total_checks if total_checks > 0 else 0.5

    def detect_bb_expansion_contraction(self, ohlcv: pd.DataFrame) -> Tuple[bool, float]:
        """Detect Bollinger Band expansion vs contraction."""
        if len(ohlcv) < self.bb_period + 5:
            return False, 0.0

        bb_data = self.calculate_bollinger_bands(ohlcv)
        width_series = bb_data['width']

        if width_series is None or len(width_series) < 2:
            return False, 0.0

        current_width = width_series.iloc[-1]
        prev_width = width_series.iloc[-2]
        avg_width = width_series.tail(20).mean()

        is_expanding = current_width > prev_width
        expansion_percent = (current_width - avg_width) / avg_width if avg_width > 0 else 0

        return is_expanding, expansion_percent

    def analyze_stock(self, ohlcv: pd.DataFrame) -> Dict[str, any]:
        """Comprehensive volatility and trend analysis."""
        if ohlcv.empty or len(ohlcv) < 20:
            return {}

        results = {}

        # Bollinger Bands
        bb_data = self.calculate_bollinger_bands(ohlcv)
        if bb_data['upper'] is not None:
            results['bb_upper'] = bb_data['upper'].iloc[-1]
            results['bb_middle'] = bb_data['middle'].iloc[-1]
            results['bb_lower'] = bb_data['lower'].iloc[-1]
            results['bb_width'] = bb_data['width'].iloc[-1]
            results['bb_width_percent'] = (bb_data['width'].iloc[-1] / bb_data['middle'].iloc[-1]) * 100

            results['price_position'] = self.get_bb_position(
                ohlcv['Close'].iloc[-1],
                results['bb_upper'],
                results['bb_middle'],
                results['bb_lower']
            )

            # BB expansion
            is_expanding, exp_pct = self.detect_bb_expansion_contraction(ohlcv)
            results['bb_expanding'] = is_expanding
            results['bb_expansion_percent'] = exp_pct

        # Moving Averages
        ma_data = self.calculate_ma_metrics(ohlcv)
        results.update(ma_data)

        # Volatility
        vol_data = self.calculate_volatility_metrics(ohlcv)
        results.update(vol_data)

        # Trend classification
        trend_type, trend_strength = self.classify_trend_type(ohlcv)
        results['trend_type'] = trend_type
        results['trend_strength'] = trend_strength

        # Trend signals
        results['trend_continuation'] = self.detect_trend_continuation(ohlcv)
        results['emerging_trend'] = self.detect_emerging_trend(ohlcv)
        results['trend_exhaustion'] = self.detect_trend_exhaustion(ohlcv)

        # Confirmation scores
        results['trend_confirmation_score'] = self.score_trend_confirmation(ohlcv)
        results['volatility_confirmation_score'] = self.score_volatility_confirmation(ohlcv)

        return results
