import pytest
import pandas as pd
import numpy as np
from src.services.screening import StockScreener

@pytest.fixture
def sample_ohlcv():
    np.random.seed(42)
    close_prices = 100 + np.cumsum(np.random.randn(250) * 0.5)
    return pd.DataFrame({
        'Open': close_prices - 1,
        'High': close_prices + 1,
        'Low': close_prices - 2,
        'Close': close_prices,
        'Volume': [1000 + i*50 for i in range(250)],
    }, index=pd.date_range('2023-01-01', periods=250))

def test_screener_instantiation():
    screener = StockScreener()
    assert screener is not None

def test_screen_intraday_breakout(sample_ohlcv):
    screener = StockScreener()
    candidates = screener.screen_intraday_breakout(sample_ohlcv, 'AAPL')
    assert isinstance(candidates, list)

def test_screen_swing_trading(sample_ohlcv):
    screener = StockScreener()
    candidates = screener.screen_swing_trading(sample_ohlcv, 'AAPL')
    assert isinstance(candidates, list)

def test_screen_long_term(sample_ohlcv):
    screener = StockScreener()
    candidates = screener.screen_long_term(sample_ohlcv, 'AAPL')
    assert isinstance(candidates, list)

def test_intraday_returns_dict_structure(sample_ohlcv):
    screener = StockScreener()
    candidates = screener.screen_intraday_breakout(sample_ohlcv, 'AAPL')
    if candidates:
        candidate = candidates[0]
        assert 'symbol' in candidate
        assert 'direction' in candidate
        assert 'current_price' in candidate
        assert candidate['direction'] in ['long', 'short']
