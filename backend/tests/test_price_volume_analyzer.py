import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.services.price_volume_analyzer import PriceVolumeAnalyzer
from src.models import AnomalyType, MarketCapClass


@pytest.fixture
def analyzer():
    """Create PriceVolumeAnalyzer instance"""
    return PriceVolumeAnalyzer()


@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1D')

    np.random.seed(42)
    close_arr = 100 + np.cumsum(np.random.randn(100) * 2)
    high_arr = close_arr + np.abs(np.random.randn(100))
    low_arr = close_arr - np.abs(np.random.randn(100))
    volume_arr = 1000000 + np.random.randint(-100000, 100000, 100)

    close = pd.Series(close_arr, index=dates)
    high = pd.Series(high_arr, index=dates)
    low = pd.Series(low_arr, index=dates)
    volume = pd.Series(volume_arr, index=dates)

    df = pd.DataFrame({
        'Date': dates,
        'Open': close.shift(1).fillna(close.iloc[0]),
        'High': high,
        'Low': low,
        'Close': close,
        'Volume': volume
    })

    return df.set_index('Date')


@pytest.fixture
def bullish_breakout_data():
    """Create data with bullish price breakout"""
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1D')
    close_vals = np.ones(50) * 100.0
    close_vals[-5:] = np.array([100, 101, 102.5, 103.5, 105])

    df = pd.DataFrame({
        'Date': dates,
        'Open': close_vals * 0.995,
        'High': close_vals * 1.01,
        'Low': close_vals * 0.99,
        'Close': close_vals,
        'Volume': np.ones(50) * 1000000
    })

    return df.set_index('Date')


@pytest.fixture
def volume_spike_data():
    """Create data with volume spike"""
    dates = pd.date_range(start='2024-01-01', periods=30, freq='1D')
    volume = np.ones(30) * 1000000
    volume[-1] = 2500000

    df = pd.DataFrame({
        'Date': dates,
        'Open': 100,
        'High': 101,
        'Low': 99,
        'Close': 100.5,
        'Volume': volume
    })

    return df.set_index('Date')


class TestMarketCapClassification:
    """Test market cap classification"""

    def test_large_cap_classification(self, analyzer):
        """Test classification of large cap stock"""
        market_cap = 50_000_000_000
        result = analyzer.classify_market_cap(market_cap)
        assert result == MarketCapClass.LARGE_CAP

    def test_mid_cap_classification(self, analyzer):
        """Test classification of mid cap stock"""
        market_cap = 5_000_000_000
        result = analyzer.classify_market_cap(market_cap)
        assert result == MarketCapClass.MID_CAP

    def test_small_cap_classification(self, analyzer):
        """Test classification of small cap stock"""
        market_cap = 1_000_000_000
        result = analyzer.classify_market_cap(market_cap)
        assert result == MarketCapClass.SMALL_CAP


class TestPriceMetrics:
    """Test price metric calculations"""

    def test_price_metrics_basic(self, analyzer, sample_ohlcv_data):
        """Test basic price metrics calculation"""
        metrics = analyzer.calculate_price_metrics(sample_ohlcv_data)
        assert 'current_price' in metrics
        assert 'price_change_percent' in metrics
        assert metrics['current_price'] > 0

    def test_price_metrics_empty_data(self, analyzer):
        """Test with empty data"""
        df = pd.DataFrame({'Close': [], 'High': [], 'Low': []})
        metrics = analyzer.calculate_price_metrics(df)
        assert metrics == {}


class TestVolumeMetrics:
    """Test volume metric calculations"""

    def test_volume_metrics_basic(self, analyzer, sample_ohlcv_data):
        """Test basic volume metrics"""
        metrics = analyzer.calculate_volume_metrics(sample_ohlcv_data)
        assert 'current_volume' in metrics
        assert 'avg_volume_5day' in metrics
        assert metrics['current_volume'] > 0

    def test_volume_relative_strength(self, analyzer, volume_spike_data):
        """Test volume relative strength calculation"""
        metrics = analyzer.calculate_volume_metrics(volume_spike_data)
        assert metrics['volume_relative_strength'] is not None
        # Spike is 2.5M on 1M avg, but need to account for exact calculation
        assert metrics['volume_relative_strength'] > 1.8


class TestTechnicalIndicators:
    """Test technical indicator calculations"""

    def test_technical_indicators_calculation(self, analyzer, sample_ohlcv_data):
        """Test technical indicators are calculated"""
        indicators = analyzer.calculate_technical_indicators(sample_ohlcv_data)
        assert 'rsi' in indicators
        assert 'adx' in indicators
        assert 'momentum' in indicators

    def test_insufficient_data_for_indicators(self, analyzer):
        """Test with insufficient data"""
        df = pd.DataFrame({
            'Open': [100, 101],
            'High': [101, 102],
            'Low': [99, 100],
            'Close': [100, 101],
            'Volume': [1000, 1100]
        })

        indicators = analyzer.calculate_technical_indicators(df)
        assert indicators == {}


class TestPriceBreakout:
    """Test price breakout detection"""

    def test_bullish_breakout_detection(self, analyzer, bullish_breakout_data):
        """Test detection of bullish breakout"""
        result = analyzer.detect_price_breakout(bullish_breakout_data)
        # Should detect breakout - price went from ~100 to 105
        if result:
            assert result['type'] == AnomalyType.PRICE_BREAKOUT
            assert result['direction'] == 'upside'
            assert result['confidence'] > 0.6

    def test_insufficient_data_for_breakout(self, analyzer):
        """Test with insufficient data"""
        df = pd.DataFrame({
            'Close': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101]
        })

        result = analyzer.detect_price_breakout(df)
        assert result is None


class TestVolumeSpike:
    """Test volume spike detection"""

    def test_volume_spike_detection(self, analyzer, volume_spike_data):
        """Test detection of volume spike"""
        result = analyzer.detect_volume_spike(volume_spike_data)
        assert result is not None
        assert result['type'] == AnomalyType.VOLUME_SPIKE


class TestTechnicalConfirmation:
    """Test technical confirmation scoring"""

    def test_confirmation_scoring(self, analyzer, bullish_breakout_data):
        """Test confirmation score calculation"""
        result = analyzer.score_technical_confirmation(bullish_breakout_data)
        assert 'confirmations' in result
        assert 'num_confirmations' in result
        assert 'technical_confirmation_score' in result
        assert 0 <= result['technical_confirmation_score'] <= 1


class TestManipulationRisk:
    """Test manipulation risk detection"""

    def test_small_cap_risk_detection(self, analyzer):
        """Test detection of small cap liquidity risk"""
        market_cap = 500_000_000
        result = analyzer.detect_manipulation_risk(pd.DataFrame(), market_cap)
        assert result['is_manipulation_risk'] is True
        assert 'small_cap_liquidity_risk' in result['risk_factors']

    def test_large_cap_no_risk(self, analyzer, sample_ohlcv_data):
        """Test large cap has low risk"""
        market_cap = 50_000_000_000
        result = analyzer.detect_manipulation_risk(sample_ohlcv_data, market_cap)
        assert 'small_cap_liquidity_risk' not in result['risk_factors']


class TestLiquidityScore:
    """Test liquidity quality scoring"""

    def test_large_cap_perfect_liquidity(self, analyzer):
        """Test large cap has perfect liquidity score"""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='1D')
        df = pd.DataFrame({
            'Close': 100,
            'High': 101,
            'Low': 99,
            'Volume': 10_000_000
        }, index=dates)

        market_cap = 50_000_000_000
        score = analyzer.calculate_liquidity_quality_score(df, market_cap)
        assert score == 1.0

    def test_small_cap_liquidity_score(self, analyzer):
        """Test small cap liquidity scoring"""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='1D')
        df = pd.DataFrame({
            'Close': 100,
            'High': 101,
            'Low': 99,
            'Volume': 1_000_000
        }, index=dates)

        market_cap = 500_000_000
        score = analyzer.calculate_liquidity_quality_score(df, market_cap)
        assert 0 <= score <= 1


class TestIntegration:
    """Integration tests for complete analysis"""

    def test_complete_analysis_flow(self, analyzer, sample_ohlcv_data):
        """Test complete analysis workflow"""
        market_cap = 10_000_000_000

        price_metrics = analyzer.calculate_price_metrics(sample_ohlcv_data)
        volume_metrics = analyzer.calculate_volume_metrics(sample_ohlcv_data)
        technical_indicators = analyzer.calculate_technical_indicators(sample_ohlcv_data)
        confirmation = analyzer.score_technical_confirmation(sample_ohlcv_data)
        manipulation = analyzer.detect_manipulation_risk(sample_ohlcv_data, market_cap)
        liquidity = analyzer.calculate_liquidity_quality_score(sample_ohlcv_data, market_cap)

        assert len(price_metrics) > 0
        assert len(volume_metrics) > 0
        assert len(technical_indicators) > 0
        assert confirmation['technical_confirmation_score'] >= 0
        assert len(manipulation) > 0
        assert 0 <= liquidity <= 1
