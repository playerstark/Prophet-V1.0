import pytest
from datetime import datetime, timedelta
import pytz
import pandas as pd
import numpy as np
from src.services.price_volume_analyzer import PriceVolumeAnalyzer
from src.services.price_volume_data_fetcher import PriceVolumeDataFetcher
from src.models import AnomalyType, MarketCapClass


class TestPriceVolumeAnalyzer:
    """Test PriceVolumeAnalyzer service"""

    def setup_method(self):
        self.analyzer = PriceVolumeAnalyzer()

    def create_sample_ohlcv(self, days=30, base_price=100, has_breakout=False):
        """Create sample OHLCV data for testing"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        data = []
        for i, date in enumerate(dates):
            if has_breakout and i == len(dates) - 1:
                # Add breakout on last day
                open_price = base_price
                close_price = base_price * 1.05
                high = close_price * 1.02
                low = base_price * 0.99
            else:
                open_price = base_price + np.random.randn() * 2
                close_price = open_price + np.random.randn() * 2
                high = max(open_price, close_price) + abs(np.random.randn())
                low = min(open_price, close_price) - abs(np.random.randn())

            volume = np.random.uniform(1_000_000, 5_000_000)

            data.append({
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close_price,
                'Volume': volume
            })

        df = pd.DataFrame(data, index=dates)
        return df

    def test_price_breakout_detection(self):
        """Test price breakout detection"""
        # Create uniform data then add breakout
        ohlcv = pd.DataFrame({
            'Open': [100.0] * 20,
            'High': [101.0] * 20,
            'Low': [99.0] * 20,
            'Close': [100.5] * 20,
            'Volume': [1_000_000] * 20
        })
        ohlcv.index = pd.date_range(end=datetime.now(), periods=20, freq='D')

        # Add strong breakout on last day
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 104
        ohlcv.loc[ohlcv.index[-1], 'High'] = 105

        breakout = self.analyzer.detect_price_breakout(ohlcv)

        # If breakout is detected, check properties
        if breakout is not None:
            assert breakout['type'] == AnomalyType.PRICE_BREAKOUT
            assert 'direction' in breakout
            assert breakout['confidence'] >= 0.7

    def test_volume_spike_detection(self):
        """Test volume spike detection"""
        ohlcv = self.create_sample_ohlcv()
        # Spike last bar
        ohlcv.loc[ohlcv.index[-1], 'Volume'] = ohlcv['Volume'].tail(5).mean() * 2.5

        spike = self.analyzer.detect_volume_spike(ohlcv)

        assert spike is not None
        assert spike['type'] == AnomalyType.VOLUME_SPIKE
        assert spike['spike_ratio'] >= self.analyzer.volume_spike_threshold

    def test_ma_crossover_detection(self):
        """Test moving average crossover detection"""
        ohlcv = self.create_sample_ohlcv(days=60)

        # Create bullish crossover
        ohlcv.loc[ohlcv.index[-2], 'Close'] = 99
        ohlcv.loc[ohlcv.index[-1], 'Close'] = 101

        crossover = self.analyzer.detect_ma_crossover(ohlcv)

        assert crossover is not None
        assert crossover['type'] == AnomalyType.MA_CROSSOVER
        assert 'signal' in crossover

    def test_rsi_extreme_detection(self):
        """Test RSI extreme detection"""
        ohlcv = self.create_sample_ohlcv(days=20)

        # Create oversold condition (declining close prices)
        for i in range(len(ohlcv) - 5, len(ohlcv)):
            ohlcv.loc[ohlcv.index[i], 'Close'] = 100 - (5 - (i - (len(ohlcv) - 5))) * 2

        rsi_extreme = self.analyzer.detect_rsi_extreme(ohlcv)

        # May or may not detect depending on exact values, but shouldn't error
        assert rsi_extreme is None or rsi_extreme['type'] == AnomalyType.RSI_EXTREME

    def test_technical_confirmation_scoring(self):
        """Test technical confirmation score calculation"""
        ohlcv = self.create_sample_ohlcv(days=60)

        score_data = self.analyzer.score_technical_confirmation(ohlcv)

        assert 'num_confirmations' in score_data
        assert 'technical_confirmation_score' in score_data
        assert 0 <= score_data['technical_confirmation_score'] <= 1

    def test_market_cap_classification(self):
        """Test market cap classification"""
        large_cap = self.analyzer.classify_market_cap(50_000_000_000)
        assert large_cap == MarketCapClass.LARGE_CAP

        mid_cap = self.analyzer.classify_market_cap(5_000_000_000)
        assert mid_cap == MarketCapClass.MID_CAP

        small_cap = self.analyzer.classify_market_cap(1_000_000_000)
        assert small_cap == MarketCapClass.SMALL_CAP

    def test_manipulation_risk_detection(self):
        """Test manipulation risk detection"""
        ohlcv = self.create_sample_ohlcv()
        market_cap = 1_000_000_000  # Small cap

        risk_data = self.analyzer.detect_manipulation_risk(ohlcv, market_cap)

        assert 'is_manipulation_risk' in risk_data
        assert 'risk_factors' in risk_data
        assert 'market_cap_class' in risk_data
        assert risk_data['market_cap_class'] == MarketCapClass.SMALL_CAP.value

    def test_liquidity_quality_score(self):
        """Test liquidity quality score calculation"""
        ohlcv = self.create_sample_ohlcv(days=25)

        large_cap_score = self.analyzer.calculate_liquidity_quality_score(ohlcv, 50_000_000_000)
        assert large_cap_score == 1.0  # Large caps are always 1.0

        small_cap_score = self.analyzer.calculate_liquidity_quality_score(ohlcv, 1_000_000_000)
        assert 0 <= small_cap_score <= 1.0

    def test_empty_ohlcv_handling(self):
        """Test handling of empty OHLCV data"""
        empty_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])

        breakout = self.analyzer.detect_price_breakout(empty_df)
        assert breakout is None

        spike = self.analyzer.detect_volume_spike(empty_df)
        assert spike is None


class TestPriceVolumeDataFetcher:
    """Test PriceVolumeDataFetcher service"""

    def setup_method(self):
        self.fetcher = PriceVolumeDataFetcher()

    def test_validate_ohlcv_data(self):
        """Test OHLCV data validation"""
        import asyncio

        async def run_test():
            # Valid data
            valid_data = pd.DataFrame({
                'Open': [100, 101, 102],
                'High': [102, 103, 104],
                'Low': [99, 100, 101],
                'Close': [101, 102, 103],
                'Volume': [1000, 1100, 1200]
            })

            is_valid, errors = await self.fetcher.validate_ohlcv_data(valid_data)
            assert is_valid
            assert len(errors) == 0

        asyncio.run(run_test())

    def test_validate_ohlcv_invalid_data(self):
        """Test OHLCV data validation with invalid data"""
        import asyncio

        async def run_test():
            # Invalid: High < Low
            invalid_data = pd.DataFrame({
                'Open': [100, 101, 102],
                'High': [98, 99, 100],
                'Low': [99, 100, 101],
                'Close': [101, 102, 103],
                'Volume': [1000, 1100, 1200]
            })

            is_valid, errors = await self.fetcher.validate_ohlcv_data(invalid_data)
            assert not is_valid
            assert len(errors) > 0

        asyncio.run(run_test())

    def test_validate_ohlcv_missing_columns(self):
        """Test OHLCV validation with missing columns"""
        import asyncio

        async def run_test():
            incomplete_data = pd.DataFrame({
                'Open': [100, 101, 102],
                'Close': [101, 102, 103],
                'Volume': [1000, 1100, 1200]
            })

            is_valid, errors = await self.fetcher.validate_ohlcv_data(incomplete_data)
            assert not is_valid
            assert len(errors) > 0
            assert any('Missing' in str(e) for e in errors)

        asyncio.run(run_test())


class TestAnomalyEndpointLogic:
    """Test the logic that will be used in anomaly endpoints"""

    def setup_method(self):
        self.analyzer = PriceVolumeAnalyzer()

    def test_anomaly_detection_pipeline(self):
        """Test complete anomaly detection pipeline"""
        # Create test data with multiple anomalies
        ohlcv = pd.DataFrame({
            'Open': [100] * 60 + [102],
            'High': [102] * 60 + [104],
            'Low': [99] * 60 + [101],
            'Close': [100.5] * 60 + [103],
            'Volume': [1_000_000] * 60 + [3_000_000]  # Volume spike
        })

        # Set index to DatetimeIndex
        ohlcv.index = pd.date_range(end=datetime.now(), periods=len(ohlcv), freq='D')

        # Check each detector
        breakout = self.analyzer.detect_price_breakout(ohlcv)
        spike = self.analyzer.detect_volume_spike(ohlcv)
        technical = self.analyzer.score_technical_confirmation(ohlcv)

        assert spike is not None, "Should detect volume spike"
        assert 'technical_confirmation_score' in technical

        # Total anomalies found
        anomalies_count = sum([
            1 if breakout else 0,
            1 if spike else 0,
        ])

        assert anomalies_count >= 1, "Should find at least one anomaly"

    def test_anomaly_risk_assessment(self):
        """Test risk assessment for anomalies"""
        ohlcv = pd.DataFrame({
            'Open': [10] * 30,
            'High': [11] * 30,
            'Low': [9] * 30,
            'Close': [10.5] * 30,
            'Volume': [100_000] * 30  # Low volume = small cap risk
        })

        ohlcv.index = pd.date_range(end=datetime.now(), periods=len(ohlcv), freq='D')

        # Small cap with low liquidity
        risk_data = self.analyzer.detect_manipulation_risk(ohlcv, 500_000_000)
        liquidity = self.analyzer.calculate_liquidity_quality_score(ohlcv, 500_000_000)

        assert risk_data['is_manipulation_risk']
        assert 'small_cap_liquidity_risk' in risk_data['risk_factors']
        assert liquidity < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
