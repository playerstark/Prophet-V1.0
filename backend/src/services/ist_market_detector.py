"""IST-based market detection for Eddie Intraday"""
from datetime import datetime
import pytz

class ISTMarketDetector:
    """Detects which market to monitor based on IST time"""
    
    IST = pytz.timezone('Asia/Kolkata')
    
    # IST Market hours
    INDIAN_MARKET_OPEN = 9   # 9:15 AM
    INDIAN_MARKET_CLOSE = 15  # 3:30 PM
    US_MARKET_OPEN = 21      # 9:30 PM IST = 9:30 AM EDT (approx)
    US_MARKET_CLOSE = 3      # 4:00 PM EDT = 1:30 AM next day IST
    
    def get_active_market(self):
        """
        Returns active market based on IST time.
        - Daytime IST (9-15:30): India
        - Nighttime IST (21-3): US
        """
        now_ist = datetime.now(self.IST)
        hour = now_ist.hour
        
        # Indian market hours: 9:15 AM - 3:30 PM IST (Mon-Fri)
        if self.INDIAN_MARKET_OPEN <= hour < self.INDIAN_MARKET_CLOSE:
            if now_ist.weekday() < 5:  # Mon-Fri
                return {
                    'market': 'INDIA',
                    'timezone': 'Asia/Kolkata',
                    'session': 'NSE',
                    'current_time': now_ist
                }
        
        # US market hours: 9:30 PM - 3:00 AM IST (Mon-Fri)
        if hour >= self.US_MARKET_OPEN or hour < self.US_MARKET_CLOSE:
            # US market is open during these IST hours (roughly)
            return {
                'market': 'US',
                'timezone': 'US/Eastern',
                'session': 'NYSE',
                'current_time': now_ist
            }
        
        # During Indian market hours (15:30-21:00 IST) or outside trading, return last active market
        if 15 <= hour < 21:
            # Between Indian close and US open
            return {
                'market': 'INDIA',
                'timezone': 'Asia/Kolkata',
                'session': 'NSE',
                'current_time': now_ist,
                'status': 'market_closed'
            }
        
        return {
            'market': None,
            'timezone': None,
            'session': None,
            'current_time': now_ist,
            'status': 'no_market'
        }
