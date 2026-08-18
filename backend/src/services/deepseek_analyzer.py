import asyncio
import json
import httpx
from typing import Optional, Dict
from src.config import settings
from typing import Optional, Dict


class DeepSeekAnalyzer:
    """AI-powered stock analysis using DeepSeek API"""
    
    def __init__(self):
        self.base_url = getattr(settings, "deepseek_api_url", "https://api.deepseek.com/v1")
        self.api_key = settings.deepseek_api_key
        self.model = "deepseek-chat"
    
    async def categorize_stock(self, symbol: str, current_price: Optional[float] = None) -> Optional[Dict]:
        """
        Dynamically categorize a stock's market cap and get general information using DeepSeek.

        Args:
            symbol: Stock ticker symbol
            current_price: Optional current price for context

        Returns:
            Dictionary with categorization info or None if API unavailable
        """
        if not self.api_key:
            return self._fallback_categorization(symbol)

        try:
            price_context = f" (Current price: ${current_price})" if current_price else ""
            prompt = f"""
Provide stock market capitalization category and key information for {symbol}{price_context}.

Respond in JSON format with exactly these fields:
{{
    "symbol": "{symbol}",
    "market_cap_class": "LARGE_CAP|MID_CAP|SMALL_CAP",
    "market_cap_usd": "approximate market cap in billions",
    "sector": "company sector",
    "description": "1-line company description"
}}

Use these thresholds:
- LARGE_CAP: Market cap > $300 billion
- MID_CAP: Market cap $10-300 billion
- SMALL_CAP: Market cap < $10 billion

Only return valid JSON, no other text.
"""
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 200
                    },
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                # Try to extract JSON from response
                try:
                    categorization = json.loads(content)
                    return categorization
                except json.JSONDecodeError:
                    # If JSON parsing fails, return fallback
                    return self._fallback_categorization(symbol)
            else:
                return self._fallback_categorization(symbol)

        except Exception as e:
            print(f"Error categorizing stock {symbol}: {e}")
            return self._fallback_categorization(symbol)

    def _fallback_categorization(self, symbol: str) -> Dict:
        """Fallback categorization using known market cap data (no API needed)"""
        # Known market cap classifications
        large_cap_stocks = {
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'HDFC.NS', 'LT.NS'
        }
        mid_cap_stocks = {
            'WIPRO.NS', 'BAJAJ-AUTO.NS', 'MARUTI.NS'
        }

        clean_symbol = symbol.upper()

        if clean_symbol in large_cap_stocks:
            market_cap_class = "LARGE_CAP"
        elif clean_symbol in mid_cap_stocks:
            market_cap_class = "MID_CAP"
        else:
            market_cap_class = "MID_CAP"  # Default to MID_CAP for unknown stocks

        return {
            "symbol": symbol,
            "market_cap_class": market_cap_class,
            "market_cap_usd": "See DeepSeek API for real-time data",
            "sector": "See DeepSeek API for sector data",
            "description": f"{symbol} - Market cap classification: {market_cap_class}"
        }

    async def analyze(self, prompt: str) -> Optional[str]:
        """
        Generic analyze method for any prompt-based analysis.
        Used by CatalystAnalyzer and other components for AI reasoning.

        Args:
            prompt: The prompt to send to DeepSeek

        Returns:
            Analysis text from DeepSeek or fallback reasoning
        """
        if not self.api_key:
            return self._fallback_generic_analysis(prompt)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"DeepSeek API error: {response.status_code}")
                return self._fallback_generic_analysis(prompt)

        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            return self._fallback_generic_analysis(prompt)

    async def generate_stock_analysis(self, stock_data: Dict) -> Optional[str]:
        """Generate AI analysis using DeepSeek"""
        
        if not self.api_key:
            return self._fallback_analysis(stock_data)
        
        try:
            prompt = self._build_analysis_prompt(stock_data)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 1500
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"DeepSeek API error: {response.status_code}")
                return self._fallback_analysis(stock_data)
                
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            return self._fallback_analysis(stock_data)
    
    def _build_analysis_prompt(self, stock_data: Dict) -> str:
        """Build prompt with stock data for DeepSeek"""
        
        symbol = stock_data.get('symbol', 'UNKNOWN')
        price = stock_data.get('current_price', 0)
        rsi = stock_data.get('rsi', 0)
        adx = stock_data.get('adx', 0)
        momentum = stock_data.get('momentum', 0)
        news_count = len(stock_data.get('news', []))
        
        quote = stock_data.get('quote', {})
        daily_change = quote.get('change_percent', 0)
        volume = quote.get('volume', 0)
        
        prompt = f"""
Analyze this stock and generate a professional investment report:

STOCK DATA:
Symbol: {symbol}
Current Price: ${price:.2f}
Daily Change: {daily_change:+.2f}%
Volume: {volume:,}

TECHNICAL INDICATORS (60-day):
- RSI (14): {rsi:.2f} {'(OVERSOLD)' if rsi < 30 else '(OVERBOUGHT)' if rsi > 70 else '(NEUTRAL)'}
- ADX (14): {adx:.2f} {'(Weak Trend)' if adx < 25 else '(Strong Trend)'}
- Momentum: {momentum:+.2f} {'(Bullish)' if momentum > 0 else '(Bearish)'}

NEWS ARTICLES: {news_count} latest articles retrieved

Please generate a comprehensive stock analysis report that includes:
1. Executive Summary (2-3 sentences)
2. Technical Analysis Interpretation
3. Market Sentiment Assessment
4. Trading Signal/Recommendation (BUY/SELL/HOLD)
5. Risk Assessment
6. Price Target & Time Horizon
7. Key Levels to Watch

Format as a professional investment report with clear sections and actionable insights.
"""
        return prompt
    
    def _fallback_generic_analysis(self, prompt: str) -> str:
        """Fallback for generic prompt analysis when API is unavailable"""
        return f"Analysis based on: {prompt[:100]}... [Fallback: DeepSeek API unavailable]"

    def _fallback_analysis(self, stock_data: Dict) -> str:
        """Generate basic analysis when DeepSeek API is unavailable"""

        symbol = stock_data.get('symbol', 'UNKNOWN')
        price = stock_data.get('current_price', 0)
        rsi = stock_data.get('rsi', 0)
        adx = stock_data.get('adx', 0)
        momentum = stock_data.get('momentum', 0)

        if rsi < 30:
            signal = "BUY (Oversold)"
            reason = "RSI indicates oversold conditions with mean reversion potential"
        elif rsi > 70:
            signal = "SELL (Overbought)"
            reason = "RSI indicates overbought conditions with pullback expected"
        elif adx > 25:
            signal = "BUY (Strong Trend)"
            reason = "Strong trend detected with ADX > 25"
        else:
            signal = "HOLD (Neutral)"
            reason = "Weak trend with no clear directional bias"

        report = f"""
STOCK ANALYSIS REPORT - {symbol}
{'='*50}

EXECUTIVE SUMMARY
Current Price: ${price:.2f}
Signal: {signal}
Reason: {reason}

TECHNICAL ANALYSIS
RSI (14): {rsi:.2f} - {'Oversold' if rsi < 30 else 'Overbought' if rsi > 70 else 'Neutral'} conditions
ADX (14): {adx:.2f} - {'Weak' if adx < 25 else 'Strong'} trend strength
Momentum: {momentum:+.2f} - {'Bullish' if momentum > 0 else 'Bearish'} momentum

RECOMMENDATION
Signal: {signal}
Confidence: Medium
Time Horizon: 2-5 days

RISK ASSESSMENT
- Market Risk: Medium (large-cap stock)
- Technical Risk: Medium (trend weakness)
- Overall: Monitor key support/resistance levels

KEY LEVELS
Entry: ${price:.2f}
Stop Loss: ${price * 0.98:.2f}
Take Profit: ${price * 1.02:.2f}

Note: This is a basic technical analysis. For AI-powered insights, ensure DeepSeek API is configured.
"""
        return report

    async def generate_swing_prediction(self, swing_data: Dict) -> Optional[Dict]:
        """Generate swing trade prediction with hold time and potential gain using DeepSeek"""

        if not self.api_key:
            return self._fallback_swing_prediction(swing_data)

        try:
            prompt = self._build_swing_prediction_prompt(swing_data)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                prediction = self._parse_swing_prediction(content)
                return prediction
            else:
                print(f"DeepSeek API error: {response.status_code}")
                return self._fallback_swing_prediction(swing_data)

        except Exception as e:
            print(f"Error calling DeepSeek API for swing prediction: {e}")
            return self._fallback_swing_prediction(swing_data)

    def _build_swing_prediction_prompt(self, swing_data: Dict) -> str:
        """Build prompt for swing trade prediction"""

        symbol = swing_data.get('symbol', 'UNKNOWN')
        price = swing_data.get('current_price', 0)
        rsi = swing_data.get('rsi', 0)
        adx = swing_data.get('adx', 0)
        momentum = swing_data.get('momentum', 0)
        atr = swing_data.get('atr', 0)
        support = swing_data.get('support', 0)
        resistance = swing_data.get('resistance', 0)

        prompt = f"""
Analyze this stock for swing trading (multi-day hold, NOT intraday) and provide specific predictions:

STOCK DATA:
Symbol: {symbol}
Current Price: ${price:.2f}
Support Level: ${support:.2f}
Resistance Level: ${resistance:.2f}
ATR (volatility): ${atr:.2f}

TECHNICAL INDICATORS:
- RSI (14): {rsi:.2f} {'(Oversold)' if rsi < 30 else '(Overbought)' if rsi > 70 else '(Neutral)'}
- ADX (14): {adx:.2f} {'(Weak Trend)' if adx < 25 else '(Strong Trend)'}
- Momentum: {momentum:+.2f} {'(Bullish)' if momentum > 0 else '(Bearish)'}

Based on this analysis, provide swing trade predictions in this EXACT JSON format:
{{
    "hold_time_days": <integer between 2-14>,
    "hold_time_range": "<e.g., 5-7 days>",
    "potential_gain_pct": <float, e.g., 5.25>,
    "potential_gain_range": "<e.g., 3-7%>",
    "confidence_score": <float between 0.4-0.95>,
    "best_entry_zone": "<e.g., $150.00 - $151.50>",
    "exit_strategy": "<specific exit instructions>",
    "risk_reward_ratio": <float, e.g., 2.0>
}}

Only respond with valid JSON, no other text. Predictions should be for swing trading (hold days, not minutes).
"""
        return prompt

    def _parse_swing_prediction(self, response_text: str) -> Dict:
        """Parse swing prediction from DeepSeek response"""
        try:
            # Try to extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                prediction = json.loads(json_str)
                return prediction
        except json.JSONDecodeError:
            pass

        # Fallback if JSON parsing fails
        return {}

    def _fallback_swing_prediction(self, swing_data: Dict) -> Dict:
        """Generate basic swing prediction when DeepSeek API is unavailable"""

        symbol = swing_data.get('symbol', 'UNKNOWN')
        rsi = swing_data.get('rsi', 50)
        adx = swing_data.get('adx', 20)
        momentum = swing_data.get('momentum', 0)
        price = swing_data.get('current_price', 100)
        atr = swing_data.get('atr', price * 0.02)

        # Determine hold time based on RSI
        if rsi < 30:
            hold_days = 5
            gain_pct = 6.0
            entry_zone = f"${price:.2f} (oversold bounce)"
            exit = "At resistance or +6% profit target"
            rr = 2.0
        elif rsi > 70:
            hold_days = 4
            gain_pct = 4.0
            entry_zone = f"${price:.2f} (pullback entry)"
            exit = "At support or 4% profit target"
            rr = 1.5
        elif adx > 25:
            hold_days = 7
            gain_pct = 8.0
            entry_zone = f"${price + atr:.2f} (breakout)"
            exit = "At resistance or 8% profit target"
            rr = 2.5
        else:
            hold_days = 5
            gain_pct = 3.0
            entry_zone = f"${price:.2f} (current price)"
            exit = "At resistance or 3% profit target"
            rr = 1.0

        return {
            "hold_time_days": hold_days,
            "hold_time_range": f"{hold_days-1}-{hold_days+2} days",
            "potential_gain_pct": gain_pct,
            "potential_gain_range": f"{max(2, gain_pct-2):.1f}-{gain_pct+2:.1f}%",
            "confidence_score": 0.65,
            "best_entry_zone": entry_zone,
            "exit_strategy": exit,
            "risk_reward_ratio": rr
        }

deepseek_analyzer = DeepSeekAnalyzer()
