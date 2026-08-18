import pytest
import pandas as pd
from src.services.indicators import IndicatorCalculator

@pytest.fixture
def sample_ohlcv():
    import numpy as np
    np.random.seed(42)
    close_prices = 100 + np.cumsum(np.random.randn(50) * 0.5)
    return pd.DataFrame({
        'Open': close_prices - 1,
        'High': close_prices + 1,
        'Low': close_prices - 2,
        'Close': close_prices,
        'Volume': [1000 + i*100 for i in range(50)],
    }, index=pd.date_range('2024-01-01', periods=50))

def test_rsi_calculation(sample_ohlcv):
    calc = IndicatorCalculator()
    rsi = calc.calculate_rsi(sample_ohlcv['Close'], period=14)
    assert len(rsi) == len(sample_ohlcv)
    assert rsi.iloc[-1] > 0 and rsi.iloc[-1] < 100

def test_adx_calculation(sample_ohlcv):
    calc = IndicatorCalculator()
    adx = calc.calculate_adx(sample_ohlcv, period=14)
    assert len(adx) == len(sample_ohlcv)
    assert adx.iloc[-1] >= 0 and adx.iloc[-1] <= 100

def test_momentum_calculation(sample_ohlcv):
    calc = IndicatorCalculator()
    momentum = calc.calculate_momentum(sample_ohlcv['Close'], period=10)
    assert len(momentum) == len(sample_ohlcv)
