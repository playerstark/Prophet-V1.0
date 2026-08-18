from typing import Dict, Any
from src.services.deepseek_analyzer import DeepSeekAnalyzer


class CatalystAnalyzer:
    """
    Uses DeepSeek to reason about catalyst quality and confidence.
    Acts as a secondary analytical layer after quantitative detection.
    """

    def __init__(self):
        self.deepseek = DeepSeekAnalyzer()

    async def analyze_catalyst_quality(self, catalyst: Dict[str, Any]) -> Dict[str, Any]:
        """
        Have DeepSeek reason about whether this is a meaningful catalyst.

        Args:
            catalyst: Catalyst data from detector

        Returns:
            Analysis with confidence assessment
        """
        prompt = f"""Analyze this catalyst for quality and relevance to intraday trading:

Symbol: {catalyst.get('symbol')}
Type: {catalyst.get('type')}
Title: {catalyst.get('title')}
Description: {catalyst.get('description')}
Sentiment: {catalyst.get('sentiment')}
Confidence Score: {catalyst.get('confidence')}
Event Date: {catalyst.get('event_date')}

Questions:
1. Is this catalyst likely to move the stock intraday?
2. What's the expected impact timeframe?
3. What's your confidence level (0-1)?
4. Any red flags or missing context?

Respond with: confidence_score, impact_timeframe, is_valid (true/false), brief_reasoning
"""

        try:
            analysis = await self.deepseek.analyze(prompt)

            # Extract confidence from response
            confidence = self._extract_confidence(analysis)

            return {
                'analysis_text': analysis,
                'reasoning_confidence': confidence,
                'is_valid': 'high' in analysis.lower() or 'strong' in analysis.lower(),
                'relevance_score': confidence
            }
        except Exception as e:
            print(f"Error in DeepSeek analysis: {e}")
            return {
                'analysis_text': f'Analysis error: {str(e)}',
                'reasoning_confidence': 0.5,
                'is_valid': True,  # Default to valid if analysis fails
                'relevance_score': 0.5
            }

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from analysis text"""
        text_lower = text.lower()

        if 'high' in text_lower or '0.8' in text_lower or '0.9' in text_lower:
            return 0.85
        elif 'medium' in text_lower or '0.6' in text_lower or '0.7' in text_lower:
            return 0.70
        elif 'low' in text_lower or '0.4' in text_lower or '0.5' in text_lower:
            return 0.50
        else:
            return 0.65  # Default
