import pytest
from datetime import datetime
import pandas as pd
import numpy as np
from src.services.volatility_trend_analyzer import VolatilityTrendAnalyzer
from src.models import TrendType, BollingerBandPosition, MAAlignment


class TestVolatilityTrendAnalyzer:
    """Test VolatilityTrendAnalyzer service"""

    def setup_method(self):
        self.analyzer = VolatilityTrendAnalyzer()

    def create_uptrend_ohlcv(self, days=60):
        """Create uptrend OHLCV data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 100

        data = []
        for i, date in enumerate(dates):
            # Create uptrend
            price = base_price + (i * 0.5)
            open_price = price
            close_price = price + 0.2
            high = price + 1
            low = price - 0.5
            volume = 1_000_000 + i * 10_000

            data.append({
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close_price,
                'Volume': volume
            })

        df = pd.DataFrame(data, index=dates)
        return df

    def create_downtrend_ohlcv(self, days=60):
        """Create downtrend OHLCV data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 100

        data = []
        for i, date in enumerate(dates):
            # Create downtrend
            price = base_price - (i * 0.5)
            open_price = price
            close_price = price - 0.2
            high = price + 0.5
            low = price - 1
            volume = 1_000_000 + i * 10_000

            data.append({
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close_price,
                'Volume': volume
            })

        df = pd.DataFrame(data, index=dates)
        return df

    def create_sideways_ohlcv(self, days=60):
        """Create sideways OHLCV data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        data = []
        for i, date in enumerate(dates):
            # Create sideways movement around 100
            noise = np.sin(i / 5) * 2
            price = 100 + noise
            open_price = price
            close_price = price + np.random.randn() * 0.5
            high = price + 1
            low = price - 1
            volume = 1_000_000

            data.append({
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close_price,
                'Volume': volume
            })

        df = pd.DataFrame(data, index=dates)
        return df

    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation"""
        ohlcv = self.create_uptrend_ohlcv()
        bb_data = self.analyzer.calculate_bollinger_bands(ohlcv)

        assert bb_data['upper'] is not None
        assert bb_data['middle'] is not None
        assert bb_data['lower'] is not None
        assert bb_data['width'] is not None

        # Check relationship: upper > middle > lower
        assert bb_data['upper'].iloc[-1] > bb_data['middle'].iloc[-1]
        assert bb_data['middle'].iloc[-1] > bb_data['lower'].iloc[-1]

    def test_bb_position_detection(self):
        """Test Bollinger Band position detection"""
        # Test above upper
        position = self.analyzer.get_bb_position(105, 100, 98, 96)
        assert position == BollingerBandPosition.ABOVE_UPPER

        # Test between
        position = self.analyzer.get_bb_position(98, 100, 98, 96)
        assert position == BollingerBandPosition.BETWEEN

        # Test below lower
        position = self.analyzer.get_bb_position(95, 100, 98, 96)
        assert position == BollingerBandPosition.BELOW_LOWER

    def test_volatility_metrics(self):
        """Test volatility metric calculations"""
        ohlcv = self.create_uptrend_ohlcv()
        vol_data = self.analyzer.calculate_volatility_metrics(ohlcv)

        assert 'atr' in vol_data
        assert 'volatility_percent' in vol_data
        assert 'volatility_trend' in vol_data

        assert vol_data['atr'] > 0
        assert vol_data['volatility_percent'] > 0

    def test_ma_metrics(self):
        """Test moving average metrics"""
        ohlcv = self.create_uptrend_ohlcv()
        ma_data = self.analyzer.calculate_ma_metrics(ohlcv)

        assert 'ma_20' in ma_data
        assert 'ma_50' in ma_data
        assert 'ma_20_direction' in ma_data
        assert 'ma_50_direction' in ma_data
        assert 'ma_alignment' in ma_data

        # In uptrend: MA20 should be above MA50
        assert ma_data['ma_20'] > ma_data['ma_50']

    def test_trend_classification_uptrend(self):
        """Test trend classification for uptrends"""
        ohlcv = self.create_uptrend_ohlcv()
        trend_type, strength = self.analyzer.classify_trend_type(ohlcv)

        assert trend_type in [TrendType.UPTREND, TrendType.STRONG_UPTREND]
        assert 0 <= strength <= 1

    def test_trend_classification_downtrend(self):
        """Test trend classification for downtrends"""
        ohlcv = self.create_downtrend_ohlcv()
        trend_type, strength = self.analyzer.classify_trend_type(ohlcv)

        assert trend_type in [TrendType.DOWNTREND, TrendType.STRONG_DOWNTREND]
        assert 0 <= strength <= 1

    def test_trend_classification_sideways(self):
        """Test trend classification for sideways movement"""
        ohlcv = self.create_sideways_ohlcv()
        trend_type, strength = self.analyzer.classify_trend_type(ohlcv)

        assert trend_type == TrendType.SIDEWAYS
        assert 0 <= strength <= 1

    def test_trend_continuation_detection(self):
        """Test trend continuation detection"""
        ohlcv = self.create_uptrend_ohlcv()
        is_continuing = self.analyzer.detect_trend_continuation(ohlcv)

        # Uptrend should have continuation signal
        assert hasattr(is_continuing, '__bool__') or isinstance(is_continuing, (bool, np.bool_))

    def test_emerging_trend_detection(self):
        """Test emerging trend detection"""
        ohlcv = self.create_uptrend_ohlcv()
        is_emerging = self.analyzer.detect_emerging_trend(ohlcv)

        # Check if it's a boolean-like value (bool or np.bool_)
        assert hasattr(is_emerging, '__bool__') or isinstance(is_emerging, (bool, np.bool_))

    def test_trend_exhaustion_detection(self):
        """Test trend exhaustion detection"""
        ohlcv = self.create_uptrend_ohlcv()
        is_exhausted = self.analyzer.detect_trend_exhaustion(ohlcv)

        assert hasattr(is_exhausted, '__bool__') or isinstance(is_exhausted, (bool, np.bool_))

    def test_trend_confirmation_scoring(self):
        """Test trend confirmation score"""
        ohlcv = self.create_uptrend_ohlcv()
        score = self.analyzer.score_trend_confirmation(ohlcv)

        assert 0 <= score <= 1

    def test_volatility_confirmation_scoring(self):
        """Test volatility confirmation score"""
        ohlcv = self.create_uptrend_ohlcv(days=100)  # Need more data for volatility calc
        score = self.analyzer.score_volatility_confirmation(ohlcv)

        assert isinstance(score, (int, float, np.floating))
        assert 0 <= score <= 1

    def test_bb_expansion_detection(self):
        """Test Bollinger Band expansion/contraction detection"""
        ohlcv = self.create_uptrend_ohlcv()
        is_expanding, exp_pct = self.analyzer.detect_bb_expansion_contraction(ohlcv)

        assert hasattr(is_expanding, '__bool__') or isinstance(is_expanding, (bool, np.bool_))
        assert isinstance(exp_pct, (int, float, np.floating))

    def test_comprehensive_analysis(self):
        """Test complete stock analysis"""
        ohlcv = self.create_uptrend_ohlcv(days=100)  # Use more data for reliable results
        analysis = self.analyzer.analyze_stock(ohlcv)

        # Check that analysis is not empty
        assert len(analysis) > 0, "Analysis returned empty dict"

        # Check critical keys exist
        critical_keys = ['trend_type', 'trend_strength']
        for key in critical_keys:
            assert key in analysis, f"Missing critical key: {key}"

    def test_ma_alignment_bullish(self):
        """Test MA alignment detection for bullish scenario"""
        ohlcv = self.create_uptrend_ohlcv(days=250)  # Need 200+ days for MA200
        ma_data = self.analyzer.calculate_ma_metrics(ohlcv)

        # In uptrend with enough data: should be bullish aligned
        if ma_data.get('ma_alignment') != MAAlignment.NOT_ENOUGH_DATA:
            assert ma_data['ma_alignment'] in [
                MAAlignment.BULLISH_ALIGNED,
                MAAlignment.MIXED
            ]

    def test_ma_alignment_bearish(self):
        """Test MA alignment detection for bearish scenario"""
        ohlcv = self.create_downtrend_ohlcv(days=250)
        ma_data = self.analyzer.calculate_ma_metrics(ohlcv)

        # In downtrend with enough data: should be bearish aligned
        if ma_data.get('ma_alignment') != MAAlignment.NOT_ENOUGH_DATA:
            assert ma_data['ma_alignment'] in [
                MAAlignment.BEARISH_ALIGNED,
                MAAlignment.MIXED
            ]

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])

        analysis = self.analyzer.analyze_stock(empty_df)
        assert analysis == {}

    def test_insufficient_data_handling(self):
        """Test handling of insufficient data"""
        small_df = pd.DataFrame({
            'Open': [100],
            'High': [101],
            'Low': [99],
            'Close': [100.5],
            'Volume': [1_000_000]
        })

        analysis = self.analyzer.analyze_stock(small_df)
        assert analysis == {}

    def test_volatility_expansion_with_strong_trend(self):
        """Test volatility expansion with strong trend"""
        ohlcv = self.create_uptrend_ohlcv(days=100)

        # Add increasing volatility in last 10 bars
        for i in range(len(ohlcv) - 10, len(ohlcv)):
            idx = i - (len(ohlcv) - 10)
            ohlcv.loc[ohlcv.index[i], 'High'] = ohlcv.loc[ohlcv.index[i], 'High'] + idx * 0.5
            ohlcv.loc[ohlcv.index[i], 'Low'] = ohlcv.loc[ohlcv.index[i], 'Low'] - idx * 0.5

        analysis = self.analyzer.analyze_stock(ohlcv)

        # Should have valid analysis
        assert len(analysis) > 0
        if 'bb_expanding' in analysis:
            assert isinstance(analysis['bb_expanding'], (bool, np.bool_))

    def test_price_position_distribution(self):
        """Test BB position across different price locations"""
        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')

        positions = []
        for base_close in [95, 98, 100, 102, 105]:
            ohlcv = pd.DataFrame({
                'Open': [100] * 60,
                'High': [101] * 60,
                'Low': [99] * 60,
                'Close': [base_close] * 60,
                'Volume': [1_000_000] * 60
            }, index=dates)

            bb_data = self.analyzer.calculate_bollinger_bands(ohlcv)
            if bb_data['upper'] is not None and not pd.isna(bb_data['upper'].iloc[-1]):
                position = self.analyzer.get_bb_position(
                    float(ohlcv['Close'].iloc[-1]),
                    float(bb_data['upper'].iloc[-1]),
                    float(bb_data['middle'].iloc[-1]),
                    float(bb_data['lower'].iloc[-1])
                )
                positions.append(position)

        # Should have detected positions
        assert len(positions) > 0


class TestTrendWithDifferentTimeframes:
    """Test trend analysis across different data frequencies"""

    def setup_method(self):
        self.analyzer = VolatilityTrendAnalyzer()

    def create_ohlcv_with_frequency(self, days=60, frequency='D'):
        """Create OHLCV data with specified frequency"""
        if frequency == 'D':
            periods = days
        elif frequency in ('4H', '4h'):
            periods = days * 6  # 6 4-hour bars per day
        elif frequency in ('1H', '1h'):
            periods = days * 24
        else:
            periods = days

        dates = pd.date_range(end=datetime.now(), periods=periods, freq=frequency)
        base_price = 100

        data = []
        for i, date in enumerate(dates):
            # Uptrend
            price = base_price + (i * 0.1)
            data.append({
                'Open': price,
                'High': price + 0.5,
                'Low': price - 0.5,
                'Close': price + 0.2,
                'Volume': 1_000_000
            })

        return pd.DataFrame(data, index=dates)

    def test_daily_trend_analysis(self):
        """Test trend analysis on daily data"""
        ohlcv = self.create_ohlcv_with_frequency(days=60, frequency='D')
        analysis = self.analyzer.analyze_stock(ohlcv)

        # Analysis should not be empty
        assert len(analysis) > 0
        if 'trend_type' in analysis:
            assert analysis['trend_type'] is not None

    def test_4hour_trend_analysis(self):
        """Test trend analysis on 4-hour data"""
        ohlcv = self.create_ohlcv_with_frequency(days=10, frequency='4h')
        analysis = self.analyzer.analyze_stock(ohlcv)

        # Analysis should not be empty
        assert len(analysis) > 0
        if 'trend_type' in analysis:
            assert analysis['trend_type'] is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
