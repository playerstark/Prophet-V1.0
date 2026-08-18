import httpx
import json
from typing import Dict, Optional
from src.config import settings

class AIEngine:
    """AI-powered trade suggestions using DeepSeek V4"""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = "https://aicredits.in/v1"

    async def generate_trade_suggestion(
        self,
        market_data: Dict,
        news_sentiment: Dict,
        horizon: str = "intraday"
    ) -> Dict:
        """Generate AI-powered trade entry/exit/stop-loss using DeepSeek V4"""

        prompt = self._build_prompt(market_data, news_sentiment, horizon)

        try:
            response = await self._call_deepseek_api(prompt)
            return self._parse_response(response)
        except Exception as e:
            print(f"Error generating trade suggestion: {e}")
            return self._fallback_suggestion(market_data)

    def _build_prompt(self, market_data: Dict, news_sentiment: Dict, horizon: str) -> str:
        """Build the prompt for DeepSeek V4"""
        return f"""
        Analyze this stock and generate a trade recommendation:

        Symbol: {market_data.get('symbol')}
        Current Price: ${market_data.get('current_price')}
        RSI: {market_data.get('rsi')}
        ADX: {market_data.get('adx')}
        Momentum: {market_data.get('momentum')}
        Volatility: {market_data.get('volatility')}

        News Sentiment:
        Bullish Headlines: {news_sentiment.get('bullish_count')}
        Bearish Headlines: {news_sentiment.get('bearish_count')}
        Sentiment Score: {news_sentiment.get('sentiment_score')}

        Trading Horizon: {horizon}

        Provide a JSON response with:
        {{
            "entry_price": <float>,
            "stop_loss": <float>,
            "target_exit": <float>,
            "confidence": <0-1>,
            "rationale": "<brief explanation>"
        }}
        """

    async def _call_deepseek_api(self, prompt: str) -> str:
        """Call DeepSeek V4 API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "deepseek-v4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                }
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']

    def _parse_response(self, response: str) -> Dict:
        """Parse DeepSeek JSON response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Error parsing DeepSeek response: {e}")

        return self._fallback_suggestion({})

    def _fallback_suggestion(self, market_data: Dict) -> Dict:
        """Fallback suggestion when API fails"""
        price = market_data.get('current_price', 100)
        return {
            'entry_price': price * 0.99,
            'stop_loss': price * 0.95,
            'target_exit': price * 1.05,
            'confidence': 0.5,
            'rationale': 'Fallback suggestion - API unavailable'
        }
