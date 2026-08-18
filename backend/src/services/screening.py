import pandas as pd
from typing import List, Dict, Optional
from src.services.indicators import IndicatorCalculator

class StockScreener:
    """Screen stocks across three horizons using technical indicators"""

    def __init__(self):
        self.calc = IndicatorCalculator()
        self.rsi_upper_band = 70
        self.rsi_lower_band = 30
        self.adx_threshold = 20
        self.volume_threshold_multiplier = 1.2

    def screen_intraday_breakout(self, ohlcv: pd.DataFrame, symbol: str) -> List[Dict]:
        """Screen for intraday RSI breakouts with ADX confirmation"""
        candidates = []

        if len(ohlcv) < 30:
            return candidates

        rsi = self.calc.calculate_rsi(ohlcv['Close'])
        adx = self.calc.calculate_adx(ohlcv)

        current_rsi = rsi.iloc[-1]
        current_adx = adx.iloc[-1]
        current_price = ohlcv['Close'].iloc[-1]
        current_volume = ohlcv['Volume'].iloc[-1]
        avg_volume = ohlcv['Volume'].iloc[-20:].mean()

        rsi_breakout_up = (rsi.iloc[-2] <= self.rsi_upper_band) and (current_rsi > self.rsi_upper_band)
        rsi_breakout_down = (rsi.iloc[-2] >= self.rsi_lower_band) and (current_rsi < self.rsi_lower_band)
        volume_confirmed = current_volume > (avg_volume * self.volume_threshold_multiplier)
        adx_confirmed = current_adx > self.adx_threshold

        if rsi_breakout_up and adx_confirmed and volume_confirmed:
            candidates.append({
                'symbol': symbol,
                'direction': 'long',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'volume_ratio': float(current_volume / avg_volume),
                'breakout_type': 'RSI_UPPER_BAND'
            })

        if rsi_breakout_down and adx_confirmed and volume_confirmed:
            candidates.append({
                'symbol': symbol,
                'direction': 'short',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'volume_ratio': float(current_volume / avg_volume),
                'breakout_type': 'RSI_LOWER_BAND'
            })

        return candidates

    def screen_swing_trading(self, ohlcv: pd.DataFrame, symbol: str) -> List[Dict]:
        """Screen for swing trading: RSI + ADX + Momentum"""
        candidates = []

        if len(ohlcv) < 30:
            return candidates

        rsi = self.calc.calculate_rsi(ohlcv['Close'])
        adx = self.calc.calculate_adx(ohlcv)
        momentum = self.calc.calculate_momentum(ohlcv['Close'])

        current_rsi = rsi.iloc[-1]
        current_adx = adx.iloc[-1]
        current_momentum = momentum.iloc[-1]
        current_price = ohlcv['Close'].iloc[-1]

        # Bullish swing setup
        if (30 < current_rsi < 70) and (current_adx > self.adx_threshold) and (current_momentum > 0):
            candidates.append({
                'symbol': symbol,
                'direction': 'long',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'momentum': float(current_momentum),
                'pattern': 'BULLISH_SWING'
            })

        # Bearish swing setup
        if (30 < current_rsi < 70) and (current_adx > self.adx_threshold) and (current_momentum < 0):
            candidates.append({
                'symbol': symbol,
                'direction': 'short',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'momentum': float(current_momentum),
                'pattern': 'BEARISH_SWING'
            })

        return candidates

    def screen_long_term(self, ohlcv: pd.DataFrame, symbol: str) -> List[Dict]:
        """Screen for long-term investing: trend + momentum + fundamentals check"""
        candidates = []

        if len(ohlcv) < 200:
            return candidates

        rsi = self.calc.calculate_rsi(ohlcv['Close'], period=14)
        adx = self.calc.calculate_adx(ohlcv, period=14)
        momentum = self.calc.calculate_momentum(ohlcv['Close'], period=50)

        sma_50 = ohlcv['Close'].rolling(window=50).mean()
        sma_200 = ohlcv['Close'].rolling(window=200).mean()

        current_price = ohlcv['Close'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_adx = adx.iloc[-1]
        current_momentum = momentum.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        current_sma_200 = sma_200.iloc[-1]

        # Bullish long-term setup
        if (current_price > current_sma_50 > current_sma_200) and (40 < current_rsi < 80) and (current_adx > 15):
            candidates.append({
                'symbol': symbol,
                'direction': 'long',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'momentum': float(current_momentum),
                'pattern': 'UPTREND_SMA_CROSS'
            })

        return candidates
