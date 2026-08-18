from fastapi import APIRouter, HTTPException
from src.services.stock_analyzer import StockAnalyzer
from src.services.indicators import IndicatorCalculator
from src.services.ai_engine import AIEngine
from typing import Dict, List
from datetime import datetime
import pandas as pd

router = APIRouter(prefix="/api/stocks", tags=["stocks"])
analyzer = StockAnalyzer()
calc = IndicatorCalculator()
ai_engine = AIEngine()


def safe_float(val):
    """Safely convert value to float, handling NaN and Series"""
    if val is None:
        return 0.0
    try:
        if isinstance(val, pd.Series):
            val = val.iloc[-1]
        f = float(val)
        if pd.isna(f):
            return 0.0
        return f
    except:
        return 0.0


def safe_int(val):
    """Safely convert value to int"""
    if val is None:
        return 0
    try:
        if isinstance(val, pd.Series):
            val = val.iloc[-1]
        i = int(val)
        if pd.isna(i):
            return 0
        return i
    except:
        return 0


@router.get("/{symbol}")
async def get_stock_data(symbol: str):
    """Get comprehensive stock data with chart and indicators - Yahoo Finance only"""
    try:
        symbol = symbol.upper()

        ohlcv = await analyzer.fetch_ohlcv(symbol, period='60d', interval='1d')
        if ohlcv is None or ohlcv.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

        rsi = calc.calculate_rsi(ohlcv['Close'])
        adx = calc.calculate_adx(ohlcv)
        momentum = calc.calculate_momentum(ohlcv['Close'])

        chart_data = []
        for idx, row in ohlcv.iterrows():
            chart_data.append({
                'date': idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx),
                'open': safe_float(row['Open']),
                'high': safe_float(row['High']),
                'low': safe_float(row['Low']),
                'close': safe_float(row['Close']),
                'volume': safe_int(row['Volume'])
            })

        market = 'IN' if symbol.endswith(('.NS', '.BO')) else 'US'

        news_list = await analyzer.get_company_news(symbol, limit=10)
        news = [
            {
                'title': n.get('title', 'N/A'),
                'sentiment': n.get('sentiment', 'neutral'),
                'source': n.get('source', 'Yahoo Finance'),
                'url': n.get('url', '')
            }
            for n in news_list
        ]

        quote = await analyzer.get_quote(symbol)

        return {
            'symbol': symbol,
            'market': market,
            'current_price': safe_float(ohlcv['Close'].iloc[-1]),
            'rsi': safe_float(rsi.iloc[-1]),
            'adx': safe_float(adx.iloc[-1]),
            'momentum': safe_float(momentum.iloc[-1]),
            'chart_data': chart_data,
            'news': news,
            'quote': quote
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")


@router.get("/{symbol}/indicators")
async def get_stock_indicators(symbol: str):
    """Fetch OHLCV and calculate technical indicators"""
    try:
        symbol = symbol.upper()
        ohlcv = await analyzer.fetch_ohlcv(symbol, period='60d', interval='1d')
        if ohlcv is None or ohlcv.empty:
            raise HTTPException(status_code=404, detail="No data found")

        rsi = calc.calculate_rsi(ohlcv['Close'])
        adx = calc.calculate_adx(ohlcv)
        momentum = calc.calculate_momentum(ohlcv['Close'])

        return {
            'symbol': symbol,
            'current_price': safe_float(ohlcv['Close'].iloc[-1]),
            'rsi': safe_float(rsi.iloc[-1]),
            'adx': safe_float(adx.iloc[-1]),
            'momentum': safe_float(momentum.iloc[-1]),
            'volume': safe_int(ohlcv['Volume'].iloc[-1]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/news")
async def get_stock_news(symbol: str):
    """Fetch news for a stock"""
    try:
        symbol = symbol.upper()
        news = await analyzer.get_company_news(symbol, limit=15)
        return {
            'symbol': symbol,
            'news': news,
            'source': 'Yahoo Finance',
            'count': len(news)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/info")
async def get_stock_info(symbol: str):
    """Get stock information"""
    try:
        symbol = symbol.upper()
        info = await analyzer.get_stock_info(symbol)
        if not info:
            raise HTTPException(status_code=404, detail=f"No info for {symbol}")
        return info
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/quote")
async def get_stock_quote(symbol: str):
    """Get real-time quote"""
    try:
        symbol = symbol.upper()
        quote = await analyzer.get_quote(symbol)
        if not quote:
            raise HTTPException(status_code=404, detail=f"No quote for {symbol}")
        return quote
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/financials")
async def get_financial_metrics(symbol: str):
    """Get financial metrics"""
    try:
        symbol = symbol.upper()
        metrics = await analyzer.get_financial_metrics(symbol)
        if not metrics:
            raise HTTPException(status_code=404, detail=f"No financials for {symbol}")
        return metrics
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/history")
async def get_historical_data(symbol: str, period: str = '1y', interval: str = '1d'):
    """Get historical data"""
    try:
        symbol = symbol.upper()
        history = await analyzer.get_historical_data(symbol, period=period, interval=interval)
        if not history:
            raise HTTPException(status_code=404, detail=f"No history for {symbol}")
        return {
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': history,
            'count': len(history)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/returns")
async def get_returns(symbol: str, period: str = '1y'):
    """Get returns"""
    try:
        symbol = symbol.upper()
        returns = await analyzer.calculate_returns(symbol, period=period)
        if not returns:
            raise HTTPException(status_code=404, detail=f"No returns for {symbol}")
        return {
            'symbol': symbol,
            'period': period,
            'returns': returns
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/volatility")
async def get_volatility(symbol: str, period: str = '60d'):
    """Get volatility"""
    try:
        symbol = symbol.upper()
        volatility = await analyzer.get_volatility(symbol, period=period)
        if not volatility:
            raise HTTPException(status_code=404, detail=f"No volatility for {symbol}")
        return {
            'symbol': symbol,
            'period': period,
            'metrics': volatility
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/ai-suggestion")
async def get_ai_suggestion(symbol: str):
    """Get AI suggestion"""
    try:
        symbol = symbol.upper()
        ohlcv = await analyzer.fetch_ohlcv(symbol, period='60d', interval='1d')
        if ohlcv is None or ohlcv.empty:
            raise HTTPException(status_code=404, detail="No data found")

        current_price = safe_float(ohlcv['Close'].iloc[-1])
        rsi = calc.calculate_rsi(ohlcv['Close'])
        adx = calc.calculate_adx(ohlcv)

        high_low = ohlcv['High'] - ohlcv['Low']
        tr1 = ohlcv['High'] - ohlcv['Close'].shift()
        tr2 = ohlcv['Low'] - ohlcv['Close'].shift()
        tr = high_low.abs().combine(tr1.abs(), max).combine(tr2.abs(), max)
        atr = tr.rolling(14).mean().iloc[-1]

        rsi_value = safe_float(rsi.iloc[-1])
        adx_value = safe_float(adx.iloc[-1])

        if rsi_value < 30:
            entry = current_price
            stop_loss = entry - (atr * 1.5)
            target = entry + (atr * 3)
            reasoning = "Oversold (RSI < 30). Mean reversion opportunity."
        elif rsi_value > 70:
            entry = current_price
            stop_loss = entry + (atr * 1.5)
            target = entry - (atr * 3)
            reasoning = "Overbought (RSI > 70). Pullback expected."
        elif adx_value > 25:
            entry = current_price + (atr * 0.5)
            target = entry + (atr * 2.5)
            stop_loss = entry - (atr * 1)
            reasoning = "Strong trend (ADX > 25). Breakout continuation."
        else:
            return {
                'entry_price': current_price,
                'stop_loss': current_price * 0.95,
                'target_price': current_price * 1.05,
                'reasoning': 'Weak trend. Wait for clearer setup.'
            }

        return {
            'entry_price': float(entry),
            'stop_loss': float(stop_loss),
            'target_price': float(target),
            'reasoning': reasoning
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{symbol}/trade-suggestion")
async def generate_trade_suggestion(symbol: str):
    """Generate trade suggestion"""
    try:
        symbol = symbol.upper()
        ohlcv = await analyzer.fetch_ohlcv(symbol, period='60d', interval='1d')
        if ohlcv is None or ohlcv.empty:
            raise HTTPException(status_code=404, detail="No data found")

        rsi = calc.calculate_rsi(ohlcv['Close'])
        adx = calc.calculate_adx(ohlcv)
        volatility = ohlcv['Close'].pct_change().std()

        market_data = {
            'symbol': symbol,
            'current_price': safe_float(ohlcv['Close'].iloc[-1]),
            'rsi': safe_float(rsi.iloc[-1]),
            'adx': safe_float(adx.iloc[-1]),
            'volatility': float(volatility) if not pd.isna(volatility) else 0.0,
        }

        news = await analyzer.get_company_news(symbol, limit=5)
        bullish = sum(1 for n in news if n.get('sentiment') == 'positive')
        bearish = sum(1 for n in news if n.get('sentiment') == 'negative')

        news_sentiment = {
            'bullish_count': bullish,
            'bearish_count': bearish,
            'sentiment_score': (bullish - bearish) / (bullish + bearish + 1)
        }

        suggestion = await ai_engine.generate_trade_suggestion(market_data, news_sentiment)
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/analysis")
async def get_comprehensive_analysis(symbol: str):
    """Get comprehensive analysis"""
    try:
        symbol = symbol.upper()
        analysis = await analyzer.get_comprehensive_analysis(symbol)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No analysis for {symbol}")
        return analysis
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/ai-analysis")
async def get_ai_analysis(symbol: str):
    """Get DeepSeek AI-generated analysis report"""
    try:
        from src.services.deepseek_analyzer import deepseek_analyzer
        
        symbol = symbol.upper()
        
        # Fetch stock data first
        ohlcv = await analyzer.fetch_ohlcv(symbol, period='60d', interval='1d')
        if ohlcv is None or ohlcv.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        rsi = calc.calculate_rsi(ohlcv['Close'])
        adx = calc.calculate_adx(ohlcv)
        momentum = calc.calculate_momentum(ohlcv['Close'])
        quote = await analyzer.get_quote(symbol)
        news = await analyzer.get_company_news(symbol, limit=5)
        
        # Prepare data for DeepSeek
        stock_data = {
            'symbol': symbol,
            'current_price': safe_float(ohlcv['Close'].iloc[-1]),
            'rsi': safe_float(rsi.iloc[-1]),
            'adx': safe_float(adx.iloc[-1]),
            'momentum': safe_float(momentum.iloc[-1]),
            'quote': quote,
            'news': news
        }
        
        # Generate AI analysis using DeepSeek
        ai_report = await deepseek_analyzer.generate_stock_analysis(stock_data)
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'ai_analysis': ai_report,
            'data_summary': stock_data
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")


@router.get("/{symbol}/swing-prediction")
async def get_swing_prediction(symbol: str):
    """Get DeepSeek swing trade prediction with hold time and potential gain"""
    try:
        from src.services.deepseek_analyzer import deepseek_analyzer

        symbol = symbol.upper()

        # Fetch stock data
        ohlcv = await analyzer.fetch_ohlcv(symbol, period='120d', interval='1d')
        if ohlcv is None or ohlcv.empty:
            raise HTTPException(status_code=404, detail="No data found")

        rsi = calc.calculate_rsi(ohlcv['Close'])
        adx = calc.calculate_adx(ohlcv)
        momentum = calc.calculate_momentum(ohlcv['Close'])

        # Calculate ATR for support/resistance
        high_low = ohlcv['High'] - ohlcv['Low']
        tr1 = ohlcv['High'] - ohlcv['Close'].shift()
        tr2 = ohlcv['Low'] - ohlcv['Close'].shift()
        tr = high_low.abs().combine(tr1.abs(), max).combine(tr2.abs(), max)
        atr = tr.rolling(14).mean().iloc[-1]

        current_price = safe_float(ohlcv['Close'].iloc[-1])
        rsi_value = safe_float(rsi.iloc[-1])
        adx_value = safe_float(adx.iloc[-1])

        # Calculate support and resistance levels
        recent_high = ohlcv['High'].tail(20).max()
        recent_low = ohlcv['Low'].tail(20).min()
        support = current_price - (atr * 1.5)
        resistance = current_price + (atr * 1.5)

        # Prepare data for DeepSeek swing prediction
        swing_data = {
            'symbol': symbol,
            'current_price': current_price,
            'rsi': rsi_value,
            'adx': adx_value,
            'momentum': safe_float(momentum.iloc[-1]),
            'atr': safe_float(atr),
            'support': support,
            'resistance': resistance,
            'recent_high': recent_high,
            'recent_low': recent_low,
            'price_history': ohlcv['Close'].tail(30).tolist()
        }

        # Generate swing prediction using DeepSeek
        prediction = await deepseek_analyzer.generate_swing_prediction(swing_data)

        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'hold_time_days': prediction.get('hold_time_days', 5),
            'hold_time_range': prediction.get('hold_time_range', '3-7 days'),
            'potential_gain_pct': prediction.get('potential_gain_pct', 5.0),
            'potential_gain_range': prediction.get('potential_gain_range', '3-7%'),
            'confidence_score': prediction.get('confidence_score', 0.65),
            'key_levels': {
                'support': float(support),
                'resistance': float(resistance)
            },
            'best_entry_zone': prediction.get('best_entry_zone', f'${current_price:.2f} ± ${safe_float(atr):.2f}'),
            'exit_strategy': prediction.get('exit_strategy', 'Take profit at resistance or stop loss at support'),
            'risk_reward_ratio': prediction.get('risk_reward_ratio', 1.5)
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating swing prediction: {str(e)}")
