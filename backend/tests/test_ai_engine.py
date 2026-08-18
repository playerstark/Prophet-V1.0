import pytest
from src.services.ai_engine import AIEngine

def test_ai_engine_instantiation():
    engine = AIEngine()
    assert engine is not None
    assert hasattr(engine, 'generate_trade_suggestion')

def test_fallback_suggestion():
    engine = AIEngine()
    market_data = {'current_price': 150.0}
    result = engine._fallback_suggestion(market_data)

    assert 'entry_price' in result
    assert 'stop_loss' in result
    assert 'target_exit' in result
    assert 'confidence' in result
    assert result['entry_price'] == 150.0 * 0.99
    assert result['stop_loss'] == 150.0 * 0.95
    assert result['target_exit'] == 150.0 * 1.05
    assert result['confidence'] == 0.5

def test_prompt_building():
    engine = AIEngine()
    market_data = {
        'symbol': 'AAPL',
        'current_price': 150.0,
        'rsi': 65,
        'adx': 25,
        'momentum': 5.2,
        'volatility': 0.18,
    }
    news_sentiment = {
        'bullish_count': 3,
        'bearish_count': 1,
        'sentiment_score': 0.65,
    }

    prompt = engine._build_prompt(market_data, news_sentiment, 'intraday')
    assert 'AAPL' in prompt
    assert '150.0' in prompt
    assert 'intraday' in prompt
