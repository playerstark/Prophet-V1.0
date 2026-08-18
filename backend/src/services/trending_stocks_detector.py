"""Detect trending stocks from Yahoo Finance"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict

class TrendingStocksDetector:
    """Get trending stocks for the active market"""
    
    # Indian trending stocks (NSE)
    INDIAN_STOCKS = [
        'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'ICICIBANK.NS',
        'HINDUNILVR.NS', 'WIPRO.NS', 'BAJAJ-AUTO.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
        'ADANIGREEN.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'BHARTIARTL.NS', 'LT.NS'
    ]
    
    # US trending stocks (NYSE)
    US_STOCKS = [
        'NVDA', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX',
        'DDOG', 'MSTR', 'PLTR', 'COIN', 'SOFI', 'SQ', 'HOOD'
    ]
    
    def __init__(self):
        self.period = '5d'  # Last 5 days for trend detection
        
    def get_trending_stocks(self, market: str) -> List[Dict]:
        """
        Get trending stocks for the given market.
        Returns list of stocks sorted by momentum.
        """
        stocks = self.INDIAN_STOCKS if market == 'INDIA' else self.US_STOCKS
        trending = []
        
        for symbol in stocks:
            try:
                data = yf.download(symbol, period=self.period, progress=False)
                
                if data.empty or len(data) < 2:
                    continue
                
                # Calculate momentum
                close_prices = data['Close']
                momentum = ((close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0]) * 100
                
                # Get current price and volume
                current_price = close_prices.iloc[-1]
                volume = data['Volume'].iloc[-1]
                
                trending.append({
                    'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                    'price': float(current_price),
                    'momentum': float(momentum),
                    'volume': int(volume),
                    'market': market
                })
            except Exception as e:
                continue
        
        # Sort by momentum (descending)
        trending.sort(key=lambda x: x['momentum'], reverse=True)
        return trending[:20]  # Return top 20 trending stocks
    
    def classify_by_market_cap(self, stock: Dict) -> str:
        """Classify stock by market cap"""
        price = stock['price']
        
        # Simplified classification based on price
        # In production, use actual market cap data
        if price > 200:
            return 'LARGE_CAP'
        elif price > 50:
            return 'MID_CAP'
        else:
            return 'SMALL_CAP'
