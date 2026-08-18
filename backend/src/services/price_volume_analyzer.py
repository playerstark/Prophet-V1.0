from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from src.models import AnomalyType, MarketCapClass
from src.services.indicators import IndicatorCalculator


class PriceVolumeAnalyzer:
    """
    Analyzes price and volume data to detect meaningful anomalies.

    Detects:
    - Price breakouts above resistance/support
    - Volume spikes vs historical average
    - Technical indicator extremes (RSI, ADX)
    - Moving average crossovers
    - Confluence signals (multiple confirmations)
    - Manipulation risks and liquidity issues
    """

    def __init__(self):
        """Initialize PriceVolumeAnalyzer with thresholds"""
        # Price anomaly thresholds
        self.price_breakout_threshold = 0.02  # 2% move
        self.volume_spike_threshold = 1.5  # 1.5x average volume

        # Technical indicator thresholds
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.adx_strong_trend = 25
        self.adx_very_strong_trend = 40

        # Manipulation detection
        self.concentration_threshold = 0.3  # 30% in single bar
        self.small_cap_liquidity_threshold = 0.5  # Score below 0.5 is risky

        # Market cap thresholds (in USD)
        self.large_cap_threshold = 10_000_000_000  # $10B
        self.mid_cap_threshold = 2_000_000_000    # $2B

    def classify_market_cap(self, market_cap: float) -> MarketCapClass:
        """Classify stock by market capitalization."""
        if market_cap >= self.large_cap_threshold:
            return MarketCapClass.LARGE_CAP
        elif market_cap >= self.mid_cap_threshold:
            return MarketCapClass.MID_CAP
        else:
            return MarketCapClass.SMALL_CAP

    def calculate_price_metrics(self, ohlcv: pd.DataFrame) -> Dict[str, float]:
        """Calculate price-based metrics."""
        if ohlcv.empty or len(ohlcv) < 2:
            return {}

        current_close = ohlcv['Close'].iloc[-1]
        prev_close = ohlcv['Close'].iloc[-2]

        price_change_pct = ((current_close - prev_close) / prev_close) * 100

        ma_20 = ohlcv['Close'].tail(20).mean() if len(ohlcv) >= 20 else None
        ma_50 = ohlcv['Close'].tail(50).mean() if len(ohlcv) >= 50 else None

        distance_from_ma20 = None
        distance_from_ma50 = None

        if ma_20:
            distance_from_ma20 = ((current_close - ma_20) / ma_20) * 100
        if ma_50:
            distance_from_ma50 = ((current_close - ma_50) / ma_50) * 100

        period_high = ohlcv['High'].max()
        period_low = ohlcv['Low'].min()

        support = ohlcv['Low'].tail(10).min()
        resistance = ohlcv['High'].tail(10).max()

        return {
            'current_price': current_close,
            'price_change_percent': price_change_pct,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'distance_from_ma20': distance_from_ma20,
            'distance_from_ma50': distance_from_ma50,
            'period_high': period_high,
            'period_low': period_low,
            'support': support,
            'resistance': resistance,
        }

    def calculate_volume_metrics(self, ohlcv: pd.DataFrame) -> Dict[str, float]:
        """Calculate volume-based metrics."""
        if ohlcv.empty or 'Volume' not in ohlcv.columns:
            return {}

        current_volume = ohlcv['Volume'].iloc[-1]

        avg_volume_5day = ohlcv['Volume'].tail(5).mean() if len(ohlcv) >= 5 else None
        avg_volume_20day = ohlcv['Volume'].tail(20).mean() if len(ohlcv) >= 20 else None

        volume_change_pct = None
        prev_volume = ohlcv['Volume'].iloc[-2] if len(ohlcv) >= 2 else None

        if prev_volume and prev_volume > 0:
            volume_change_pct = ((current_volume - prev_volume) / prev_volume) * 100

        volume_relative_strength = None
        if avg_volume_5day and avg_volume_5day > 0:
            volume_relative_strength = current_volume / avg_volume_5day

        obv = self._calculate_obv(ohlcv)
        obv_trend = None
        if obv is not None and len(obv) >= 2:
            obv_trend = "bullish" if obv.iloc[-1] > obv.iloc[-2] else "bearish"

        return {
            'current_volume': current_volume,
            'avg_volume_5day': avg_volume_5day,
            'avg_volume_20day': avg_volume_20day,
            'volume_change_percent': volume_change_pct,
            'volume_relative_strength': volume_relative_strength,
            'obv_trend': obv_trend,
        }

    def calculate_technical_indicators(self, ohlcv: pd.DataFrame) -> Dict[str, float]:
        """Calculate all technical indicators."""
        if ohlcv.empty or len(ohlcv) < 14:
            return {}

        indicators = {}

        rsi = IndicatorCalculator.calculate_rsi(ohlcv['Close'], period=14)
        indicators['rsi'] = rsi.iloc[-1]
        indicators['rsi_level'] = self._classify_rsi(indicators['rsi'])

        adx = IndicatorCalculator.calculate_adx(ohlcv, period=14)
        indicators['adx'] = adx.iloc[-1]
        indicators['trend_strength'] = self._classify_trend_strength(indicators['adx'])

        momentum = IndicatorCalculator.calculate_momentum(ohlcv['Close'], period=10)
        indicators['momentum'] = momentum.iloc[-1]
        indicators['momentum_direction'] = "bullish" if momentum.iloc[-1] > 0 else "bearish"

        if len(ohlcv) >= 26:
            ema_12 = ohlcv['Close'].ewm(span=12).mean()
            ema_26 = ohlcv['Close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            indicators['macd'] = macd.iloc[-1]
            indicators['macd_signal'] = "bullish" if macd.iloc[-1] > 0 else "bearish"

        return indicators

    def detect_price_breakout(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect price breakouts above recent resistance or below support."""
        if len(ohlcv) < 20:
            return None

        current_price = ohlcv['Close'].iloc[-1]
        resistance = ohlcv['High'].tail(20).max()
        support = ohlcv['Low'].tail(20).min()

        if current_price > resistance * (1 + self.price_breakout_threshold/100):
            price_change = ((current_price - resistance) / resistance) * 100
            return {
                'type': AnomalyType.PRICE_BREAKOUT,
                'direction': 'upside',
                'breakout_level': resistance,
                'current_price': current_price,
                'breakout_percent': price_change,
                'confidence': 0.85 if price_change > 3 else 0.70,
            }

        elif current_price < support * (1 - self.price_breakout_threshold/100):
            price_change = ((support - current_price) / support) * 100
            return {
                'type': AnomalyType.PRICE_BREAKOUT,
                'direction': 'downside',
                'breakout_level': support,
                'current_price': current_price,
                'breakout_percent': price_change,
                'confidence': 0.85 if price_change > 3 else 0.70,
            }

        return None

    def detect_volume_spike(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect abnormal volume spikes."""
        if len(ohlcv) < 5 or 'Volume' not in ohlcv.columns:
            return None

        current_volume = ohlcv['Volume'].iloc[-1]
        avg_volume = ohlcv['Volume'].tail(5).mean()

        if current_volume < avg_volume:
            return None

        spike_ratio = current_volume / avg_volume

        if spike_ratio >= self.volume_spike_threshold:
            return {
                'type': AnomalyType.VOLUME_SPIKE,
                'spike_ratio': spike_ratio,
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'confidence': min(0.95, 0.60 + (spike_ratio - self.volume_spike_threshold) * 0.1),
            }

        return None

    def detect_ma_crossover(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect moving average crossovers."""
        if len(ohlcv) < 50:
            return None

        close = ohlcv['Close']
        ma_20 = close.tail(20).mean()
        ma_50 = close.tail(50).mean()

        current_price = close.iloc[-1]
        prev_price = close.iloc[-2] if len(close) >= 2 else close.iloc[-1]

        if prev_price <= ma_50 and current_price > ma_50:
            return {
                'type': AnomalyType.MA_CROSSOVER,
                'signal': 'bullish',
                'ma_20': ma_20,
                'ma_50': ma_50,
                'current_price': current_price,
                'confidence': 0.80,
            }

        elif prev_price >= ma_50 and current_price < ma_50:
            return {
                'type': AnomalyType.MA_CROSSOVER,
                'signal': 'bearish',
                'ma_20': ma_20,
                'ma_50': ma_50,
                'current_price': current_price,
                'confidence': 0.80,
            }

        return None

    def detect_rsi_extreme(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect RSI extremes."""
        if len(ohlcv) < 14:
            return None

        rsi = IndicatorCalculator.calculate_rsi(ohlcv['Close'], period=14)
        current_rsi = rsi.iloc[-1]

        if current_rsi >= self.rsi_overbought:
            return {
                'type': AnomalyType.RSI_EXTREME,
                'condition': 'overbought',
                'rsi_value': current_rsi,
                'threshold': self.rsi_overbought,
                'confidence': min(0.95, 0.70 + (current_rsi - self.rsi_overbought) * 0.01),
            }

        elif current_rsi <= self.rsi_oversold:
            return {
                'type': AnomalyType.RSI_EXTREME,
                'condition': 'oversold',
                'rsi_value': current_rsi,
                'threshold': self.rsi_oversold,
                'confidence': min(0.95, 0.70 + (self.rsi_oversold - current_rsi) * 0.01),
            }

        return None

    def detect_adx_surge(self, ohlcv: pd.DataFrame) -> Optional[Dict[str, any]]:
        """Detect ADX surge."""
        if len(ohlcv) < 14:
            return None

        adx = IndicatorCalculator.calculate_adx(ohlcv, period=14)
        current_adx = adx.iloc[-1]

        if current_adx >= self.adx_strong_trend:
            strength = "very_strong" if current_adx >= self.adx_very_strong_trend else "strong"
            return {
                'type': AnomalyType.ADX_SURGE,
                'trend_strength': strength,
                'adx_value': current_adx,
                'threshold': self.adx_strong_trend,
                'confidence': min(0.95, 0.60 + (current_adx - self.adx_strong_trend) * 0.02),
            }

        return None

    def score_technical_confirmation(self, ohlcv: pd.DataFrame) -> Dict[str, any]:
        """Score technical confirmation."""
        confirmations = []
        confidence_scores = []

        price_breakout = self.detect_price_breakout(ohlcv)
        if price_breakout:
            confirmations.append('price_breakout')
            confidence_scores.append(price_breakout['confidence'])

        volume_spike = self.detect_volume_spike(ohlcv)
        if volume_spike:
            confirmations.append('volume_spike')
            confidence_scores.append(volume_spike['confidence'])

        ma_crossover = self.detect_ma_crossover(ohlcv)
        if ma_crossover:
            confirmations.append('ma_crossover')
            confidence_scores.append(ma_crossover['confidence'])

        rsi_extreme = self.detect_rsi_extreme(ohlcv)
        if rsi_extreme:
            confirmations.append('rsi_extreme')
            confidence_scores.append(rsi_extreme['confidence'])

        adx_surge = self.detect_adx_surge(ohlcv)
        if adx_surge:
            confirmations.append('adx_surge')
            confidence_scores.append(adx_surge['confidence'])

        num_confirmations = len(confirmations)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        confirmation_multiplier = min(1.0, num_confirmations * 0.25)
        technical_confirmation_score = (avg_confidence * 0.6 + confirmation_multiplier * 0.4)

        return {
            'confirmations': confirmations,
            'num_confirmations': num_confirmations,
            'avg_confidence': avg_confidence,
            'technical_confirmation_score': technical_confirmation_score,
        }

    def detect_manipulation_risk(self, ohlcv: pd.DataFrame, market_cap: float) -> Dict[str, any]:
        """Detect manipulation risks."""
        is_risky = False
        risk_factors = []

        if len(ohlcv) > 0 and 'Volume' in ohlcv.columns:
            current_volume = ohlcv['Volume'].iloc[-1]
            total_recent_volume = ohlcv['Volume'].tail(5).sum()

            concentration = current_volume / total_recent_volume if total_recent_volume > 0 else 0
            if concentration > self.concentration_threshold:
                is_risky = True
                risk_factors.append(f'high_volume_concentration_{concentration:.1%}')

        market_cap_class = self.classify_market_cap(market_cap)
        if market_cap_class == MarketCapClass.SMALL_CAP:
            is_risky = True
            risk_factors.append('small_cap_liquidity_risk')

        return {
            'is_manipulation_risk': is_risky,
            'risk_factors': risk_factors,
            'market_cap_class': market_cap_class.value,
        }

    def calculate_liquidity_quality_score(self, ohlcv: pd.DataFrame, market_cap: float) -> float:
        """Calculate liquidity quality score."""
        if ohlcv.empty or 'Volume' not in ohlcv.columns:
            return 0.0

        score = 1.0

        if market_cap >= self.large_cap_threshold:
            return 1.0

        volumes = ohlcv['Volume'].tail(20)
        if len(volumes) > 0:
            volume_std = volumes.std()
            volume_mean = volumes.mean()

            if volume_mean > 0:
                cv = volume_std / volume_mean
                volume_score = max(0, 1 - cv)
                score *= (0.3 + volume_score * 0.7)

        if len(ohlcv) >= 2:
            closes = ohlcv['Close'].tail(20)
            returns = closes.pct_change()
            volatility = returns.std()

            volatility_score = max(0, 1 - (volatility * 20))
            score *= (0.3 + volatility_score * 0.7)

        if len(ohlcv) > 0:
            high_low_ratio = (ohlcv['High'] - ohlcv['Low']).mean() / ohlcv['Close'].mean()
            spread_score = max(0, 1 - (high_low_ratio * 50))
            score *= (0.3 + spread_score * 0.7)

        return max(0, min(1, score))

    def _calculate_obv(self, ohlcv: pd.DataFrame) -> Optional[pd.Series]:
        """Calculate On-Balance Volume."""
        if ohlcv.empty or 'Volume' not in ohlcv.columns or 'Close' not in ohlcv.columns:
            return None

        close = ohlcv['Close']
        volume = ohlcv['Volume']

        obv = pd.Series(0.0, index=close.index)
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        return obv

    def _classify_rsi(self, rsi_value: float) -> str:
        """Classify RSI level"""
        if rsi_value >= self.rsi_overbought:
            return "overbought"
        elif rsi_value <= self.rsi_oversold:
            return "oversold"
        else:
            return "neutral"

    def _classify_trend_strength(self, adx_value: float) -> str:
        """Classify trend strength"""
        if adx_value >= self.adx_very_strong_trend:
            return "very_strong"
        elif adx_value >= self.adx_strong_trend:
            return "strong"
        else:
            return "weak"
