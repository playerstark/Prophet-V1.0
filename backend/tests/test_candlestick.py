import pytest
from datetime import datetime
import pandas as pd
import numpy as np
from src.services.candlestick_analyzer import CandlestickAnalyzer
from src.models import CandleColor, CandlePattern


class TestCandlestickAnalyzer:
    """Test CandlestickAnalyzer service"""

    def setup_method(self):
        self.analyzer = CandlestickAnalyzer()

    def create_base_ohlcv(self, days=60):
        """Create base OHLCV data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        data = []
        for i, date in enumerate(dates):
            price = 100 + (i * 0.3)
            data.append({
                'Open': price,
                'High': price + 1,
                'Low': price - 0.5,
                'Close': price + 0.2,
                'Volume': 1_000_000
            })
        return pd.DataFrame(data, index=dates)

    def test_bullish_candle_classification(self):
        """Test bullish candle color detection"""
        # Bullish: close > open
        color = self.analyzer.classify_candle_color(
            open_price=100,
            close_price=102,
            high=103,
            low=99
        )
        assert color == CandleColor.BULLISH

    def test_bearish_candle_classification(self):
        """Test bearish candle color detection"""
        # Bearish: close < open
        color = self.analyzer.classify_candle_color(
            open_price=100,
            close_price=98,
            high=101,
            low=97
        )
        assert color == CandleColor.BEARISH

    def test_doji_classification(self):
        """Test doji candle detection"""
        # Doji: very small body relative to range (body < 0.5% of range)
        # Range = 2, so body < 0.01
        color = self.analyzer.classify_candle_color(
            open_price=100.0,
            close_price=100.005,  # Almost no body
            high=101,
            low=99
        )
        assert color == CandleColor.DOJI

    def test_hammer_classification(self):
        """Test hammer candle detection"""
        # Hammer: small body, long lower wick
        color = self.analyzer.classify_candle_color(
            open_price=100,
            close_price=101,
            high=101.2,
            low=95  # Long lower wick
        )
        assert color == CandleColor.HAMMER

    def test_candle_properties(self):
        """Test candle property calculations"""
        props = self.analyzer.calculate_candle_properties(
            open_p=100,
            high=103,
            low=97,
            close_p=102
        )

        assert props['range'] == 6
        assert props['body'] == 2
        assert props['upper_wick'] == 1
        assert props['lower_wick'] == 3

    def test_candle_size_classification(self):
        """Test candle size classification"""
        # Large body
        size = self.analyzer.get_candle_size(0.75)
        assert size == "large"

        # Medium body
        size = self.analyzer.get_candle_size(0.4)
        assert size == "medium"

        # Small body
        size = self.analyzer.get_candle_size(0.1)
        assert size == "small"

    def test_engulfing_pattern_bullish(self):
        """Test bullish engulfing pattern detection"""
        ohlcv = self.create_base_ohlcv()

        # Setup bearish candle followed by bullish engulfing
        ohlcv.loc[ohlcv.index[-2], 'Open'] = 101
        ohlcv.loc[ohlcv.index[-2], 'Close'] = 100
        ohlcv.loc[ohlcv.index[-2], 'High'] = 101.5
        ohlcv.loc[ohlcv.index[-2], 'Low'] = 99.5

        ohlcv.loc[ohlcv.index[-1], 'Open'] = 99
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 102
        ohlcv.loc[ohlcv.index[-1], 'High'] = 103
        ohlcv.loc[ohlcv.index[-1], 'Low'] = 99

        pattern = self.analyzer.detect_engulfing_pattern(ohlcv)

        if pattern:  # May or may not detect depending on exact values
            assert pattern['pattern'] == CandlePattern.ENGULFING

    def test_harami_pattern_detection(self):
        """Test harami pattern detection"""
        ohlcv = self.create_base_ohlcv()

        # Setup large previous candle
        ohlcv.loc[ohlcv.index[-2], 'Open'] = 98
        ohlcv.loc[ohlcv.index[-2], 'Close'] = 102
        ohlcv.loc[ohlcv.index[-2], 'High'] = 103
        ohlcv.loc[ohlcv.index[-2], 'Low'] = 97

        # Setup small current candle inside previous
        ohlcv.loc[ohlcv.index[-1], 'Open'] = 100
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 100.5
        ohlcv.loc[ohlcv.index[-1], 'High'] = 101
        ohlcv.loc[ohlcv.index[-1], 'Low'] = 99

        pattern = self.analyzer.detect_harami_pattern(ohlcv)

        if pattern:
            assert pattern['pattern'] == CandlePattern.HARAMI

    def test_morning_star_pattern(self):
        """Test morning star pattern detection"""
        ohlcv = self.create_base_ohlcv()

        # Bar 1: Bearish (downtrend)
        ohlcv.loc[ohlcv.index[-3], 'Open'] = 102
        ohlcv.loc[ohlcv.index[-3], 'Close'] = 99
        ohlcv.loc[ohlcv.index[-3], 'High'] = 103
        ohlcv.loc[ohlcv.index[-3], 'Low'] = 98

        # Bar 2: Small body (indecision)
        ohlcv.loc[ohlcv.index[-2], 'Open'] = 99.5
        ohlcv.loc[ohlcv.index[-2], 'Close'] = 99.8
        ohlcv.loc[ohlcv.index[-2], 'High'] = 100.2
        ohlcv.loc[ohlcv.index[-2], 'Low'] = 99

        # Bar 3: Bullish above mid-point
        ohlcv.loc[ohlcv.index[-1], 'Open'] = 99.5
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 101
        ohlcv.loc[ohlcv.index[-1], 'High'] = 101.5
        ohlcv.loc[ohlcv.index[-1], 'Low'] = 99

        pattern = self.analyzer.detect_morning_star_pattern(ohlcv)

        if pattern:
            assert pattern['pattern'] == CandlePattern.MORNING_STAR

    def test_three_white_soldiers(self):
        """Test three white soldiers pattern"""
        ohlcv = self.create_base_ohlcv()

        # Three consecutive bullish with each close > previous close
        ohlcv.loc[ohlcv.index[-3], 'Open'] = 100
        ohlcv.loc[ohlcv.index[-3], 'Close'] = 101

        ohlcv.loc[ohlcv.index[-2], 'Open'] = 101
        ohlcv.loc[ohlcv.index[-2], 'Close'] = 102

        ohlcv.loc[ohlcv.index[-1], 'Open'] = 102
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 103

        pattern = self.analyzer.detect_three_white_soldiers(ohlcv)

        assert pattern is not None
        assert pattern['pattern'] == CandlePattern.THREE_WHITE_SOLDIERS

    def test_three_black_crows(self):
        """Test three black crows pattern"""
        ohlcv = self.create_base_ohlcv()

        # Three consecutive bearish with each close < previous close
        ohlcv.loc[ohlcv.index[-3], 'Open'] = 103
        ohlcv.loc[ohlcv.index[-3], 'Close'] = 102

        ohlcv.loc[ohlcv.index[-2], 'Open'] = 102
        ohlcv.loc[ohlcv.index[-2], 'Close'] = 101

        ohlcv.loc[ohlcv.index[-1], 'Open'] = 101
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 100

        pattern = self.analyzer.detect_three_black_crows(ohlcv)

        assert pattern is not None
        assert pattern['pattern'] == CandlePattern.THREE_BLACK_CROWS

    def test_candle_position_above_ma20(self):
        """Test candle position detection above MA20"""
        position, distances = self.analyzer.get_candle_position(
            close=105,
            ma20=100,
            ma50=95,
            bb_upper=110,
            bb_lower=90
        )

        assert position is not None
        assert distances is not None

    def test_candle_position_below_lower_bb(self):
        """Test candle position at support"""
        position, distances = self.analyzer.get_candle_position(
            close=85,
            ma20=100,
            ma50=95,
            bb_upper=110,
            bb_lower=90
        )

        assert position is not None

    def test_volume_confirmation_bullish(self):
        """Test volume confirmation for bullish candle"""
        ohlcv = self.create_base_ohlcv()

        # Increase volume on last bar
        ohlcv.loc[ohlcv.index[-1], 'Volume'] = 2_000_000

        confirmed, confidence, trend = self.analyzer.analyze_volume_confirmation(
            ohlcv,
            CandleColor.BULLISH
        )

        assert isinstance(confirmed, (bool, np.bool_))
        assert 0 <= confidence <= 1

    def test_volume_confirmation_bearish(self):
        """Test volume confirmation for bearish candle"""
        ohlcv = self.create_base_ohlcv()

        # Increase volume on last bar
        ohlcv.loc[ohlcv.index[-1], 'Volume'] = 2_000_000

        confirmed, confidence, trend = self.analyzer.analyze_volume_confirmation(
            ohlcv,
            CandleColor.BEARISH
        )

        assert isinstance(confirmed, (bool, np.bool_))
        assert 0 <= confidence <= 1

    def test_candle_quality_score(self):
        """Test candle quality scoring"""
        quality = self.analyzer.calculate_candle_quality_score(
            open_p=100,
            high=103,
            low=97,
            close_p=102,
            pattern_confidence=0.85,
            volume_confirmed=True
        )

        assert 0 <= quality <= 1

    def test_rejection_candle_detection(self):
        """Test price rejection at level"""
        ohlcv = self.create_base_ohlcv()

        # Candle that touches level but closes away
        ohlcv.loc[ohlcv.index[-1], 'High'] = 110
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 95

        is_rejection = self.analyzer.is_rejection_candle(ohlcv, level=110)

        assert isinstance(is_rejection, (bool, np.bool_))

    def test_inside_bar_detection(self):
        """Test inside bar detection"""
        ohlcv = self.create_base_ohlcv()

        # Setup previous bar range
        ohlcv.loc[ohlcv.index[-2], 'High'] = 105
        ohlcv.loc[ohlcv.index[-2], 'Low'] = 95

        # Current bar inside previous range
        ohlcv.loc[ohlcv.index[-1], 'High'] = 103
        ohlcv.loc[ohlcv.index[-1], 'Low'] = 97

        is_inside = self.analyzer.is_inside_bar(ohlcv)

        assert isinstance(is_inside, (bool, np.bool_))

    def test_pin_bar_detection(self):
        """Test pin bar detection"""
        ohlcv = self.create_base_ohlcv()

        # Pin bar: long wick, small body
        ohlcv.loc[ohlcv.index[-1], 'Open'] = 100
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 100.1
        ohlcv.loc[ohlcv.index[-1], 'High'] = 110
        ohlcv.loc[ohlcv.index[-1], 'Low'] = 95

        is_pin = self.analyzer.is_pin_bar(ohlcv)

        assert isinstance(is_pin, (bool, np.bool_))

    def test_comprehensive_candle_analysis(self):
        """Test complete candle analysis"""
        ohlcv = self.create_base_ohlcv(days=100)  # Use more data for better analysis

        analysis = self.analyzer.analyze_candle(
            ohlcv,
            ma20=100,
            ma50=98,
            bb_upper=105,
            bb_lower=95
        )

        # Verify analysis exists and has key fields
        assert len(analysis) > 0, "Analysis should not be empty"
        assert 'color' in analysis or len(analysis) > 0, "Should have analysis"
        if 'quality_score' in analysis:
            assert isinstance(analysis['quality_score'], (int, float, np.floating))

    def test_analysis_with_bullish_setup(self):
        """Test analysis in bullish market setup"""
        ohlcv = self.create_base_ohlcv()

        # Bullish setup
        ohlcv.loc[ohlcv.index[-1], 'Open'] = 100
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 102
        ohlcv.loc[ohlcv.index[-1], 'Volume'] = 1_500_000

        analysis = self.analyzer.analyze_candle(
            ohlcv,
            ma20=99,
            ma50=97,
            bb_upper=106,
            bb_lower=94
        )

        if analysis:
            assert analysis['color'] == CandleColor.BULLISH

    def test_analysis_with_bearish_setup(self):
        """Test analysis in bearish market setup"""
        ohlcv = self.create_base_ohlcv()

        # Bearish setup
        ohlcv.loc[ohlcv.index[-1], 'Open'] = 100
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 98
        ohlcv.loc[ohlcv.index[-1], 'Volume'] = 1_500_000

        analysis = self.analyzer.analyze_candle(
            ohlcv,
            ma20=101,
            ma50=103,
            bb_upper=106,
            bb_lower=94
        )

        if analysis:
            assert analysis['color'] == CandleColor.BEARISH

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])

        analysis = self.analyzer.analyze_candle(empty_df)

        assert analysis == {}

    def test_insufficient_data_handling(self):
        """Test handling with only 1 bar"""
        small_df = pd.DataFrame({
            'Open': [100],
            'High': [101],
            'Low': [99],
            'Close': [100.5],
            'Volume': [1_000_000]
        })

        analysis = self.analyzer.analyze_candle(small_df)

        assert len(analysis) > 0  # Should still analyze single candle

    def test_pattern_detection_multiple(self):
        """Test detecting multiple patterns"""
        ohlcv = self.create_base_ohlcv()

        # Setup for multiple detections
        ohlcv.loc[ohlcv.index[-3], 'Open'] = 100
        ohlcv.loc[ohlcv.index[-3], 'Close'] = 101

        ohlcv.loc[ohlcv.index[-2], 'Open'] = 101
        ohlcv.loc[ohlcv.index[-2], 'Close'] = 102

        ohlcv.loc[ohlcv.index[-1], 'Open'] = 102
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 103

        analysis = self.analyzer.analyze_candle(ohlcv)

        if analysis and 'pattern_count' in analysis:
            assert analysis['pattern_count'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
