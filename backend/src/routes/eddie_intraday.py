"""Simplified Eddie Intraday routes - No SQLAlchemy dependencies"""
from fastapi import APIRouter
from src.services.ist_market_detector import ISTMarketDetector
from src.services.trending_stocks_detector import TrendingStocksDetector
import random

router = APIRouter(prefix="/api/eddie-intraday", tags=["eddie-intraday"])

ist_detector = ISTMarketDetector()
trending_detector = TrendingStocksDetector()

@router.get("/market-status")
async def get_market_status():
    """Get current market status based on IST time"""
    market_info = ist_detector.get_active_market()
    return {
        "market": market_info['market'],
        "session": market_info['session'],
        "timezone": market_info['timezone'],
        "current_time_ist": market_info['current_time'].isoformat(),
        "status": market_info.get('status', 'active')
    }

@router.get("/signals")
async def get_eddie_signals():
    """
    Get Eddie Intraday signals grouped by market cap.
    """
    
    # Get active market based on IST
    market_info = ist_detector.get_active_market()
    market = market_info['market']
    
    if not market:
        return {
            "market": None,
            "session": None,
            "current_time_ist": market_info['current_time'].isoformat(),
            "status": "market_closed",
            "large_cap": [],
            "mid_cap": [],
            "small_cap": []
        }
    
    # Get trending stocks for this market
    trending = trending_detector.get_trending_stocks(market)
    
    # Organize signals by market cap
    signals = {
        'large_cap': [],
        'mid_cap': [],
        'small_cap': []
    }
    
    # Ratings for demo
    ratings = ['strong_buy', 'buy', 'buy', 'neutral', 'sell', 'strong_sell']
    
    for stock in trending:
        # Classify by market cap
        market_cap_class = trending_detector.classify_by_market_cap(stock)
        cap_key = market_cap_class.lower().replace('_', '_')
        
        signal = {
            'symbol': stock['symbol'],
            'price': stock['price'],
            'momentum': stock['momentum'],
            'rating': random.choice(ratings),  # Random for demo
            'confidence': round(random.uniform(0.5, 0.95), 2),  # Random confidence
            'market_cap': market_cap_class,
            'key_signals': ['Momentum', 'Trend']
        }
        
        # Categorize by market cap
        if market_cap_class == 'LARGE_CAP':
            signals['large_cap'].append(signal)
        elif market_cap_class == 'MID_CAP':
            signals['mid_cap'].append(signal)
        else:
            signals['small_cap'].append(signal)
    
    # Sort each category by confidence
    for cap in ['large_cap', 'mid_cap', 'small_cap']:
        signals[cap].sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        "market": market,
        "session": market_info['session'],
        "current_time_ist": market_info['current_time'].isoformat(),
        "status": "active" if market else "market_closed",
        "large_cap": signals['large_cap'][:5],
        "mid_cap": signals['mid_cap'][:5],
        "small_cap": signals['small_cap'][:5]
    }

@router.get("/stock-details/{symbol}")
async def get_stock_details(symbol: str):
    """Get stock details for analyzer integration"""
    return {
        "symbol": symbol,
        "analysis": {
            "rating": "buy",
            "confidence": 0.75
        },
        "ready_for_short_term": True
    }
