"""
Long-Term Stock Picker Engine
Comprehensive framework for selecting undervalued stocks with strong fundamental growth potential.

Core Philosophy:
- Focus on companies with sustainable competitive advantages
- Strong fundamentals and reasonable valuations over speculative hype
- Risk-adjusted long-term return potential as primary criterion
- Transparent, configurable scoring system
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class TechnicalIndicators:
    """Technical analysis metrics"""
    rsi: Optional[float]
    adx: Optional[float]
    momentum: Optional[float]
    price_above_200ma: Optional[bool]
    trend_direction: str  # "uptrend", "downtrend", "neutral"


@dataclass
class ValuationMetrics:
    """Comprehensive valuation analysis"""
    current_price: float
    pe_ratio: Optional[float]
    forward_pe: Optional[float]
    pb_ratio: Optional[float]
    ps_ratio: Optional[float]
    peg_ratio: Optional[float]
    industry_pe: Optional[float]
    pe_percentile: Optional[float]  # Where stock P/E ranks vs historical
    pe_historical_range: Optional[Tuple[float, float]]  # Min/max historical


@dataclass
class DCFResult:
    """DCF valuation result"""
    per_share_value: Optional[float]
    enterprise_value: Optional[float]
    pv_fcf: float
    pv_terminal: float
    terminal_value: float
    assumptions: Dict


@dataclass
class RiskProfile:
    """Detailed risk assessment"""
    risk_factors: List[str]
    risk_score: float  # 0-100 (lower is better)
    temporary_risks: List[str]  # Short-term headwinds that could reverse
    structural_risks: List[str]  # Long-term, fundamental challenges
    risk_rating: str  # "Low", "Medium", "High", "Critical"
    invalidation_factors: List[str]  # What would break the investment thesis


@dataclass
class StockAnalysis:
    """Complete analysis for a single stock"""
    symbol: str
    company_name: str
    industry: str
    sector: Optional[str] = None

    # Valuation
    valuation: Optional[ValuationMetrics] = None

    # DCF Analysis
    dcf: Optional[DCFResult] = None
    undervaluation_pct: Optional[float] = None
    intrinsic_value: Optional[float] = None

    # Fundamentals
    revenue_growth_3y: Optional[float] = None
    revenue_growth_ttm: Optional[float] = None
    fcf_margin: Optional[float] = None
    net_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    current_ratio: Optional[float] = None

    # Technical confirmation
    technical: Optional[TechnicalIndicators] = None

    # Risk assessment
    risk_profile: Optional[RiskProfile] = None

    # Analyst data
    analyst_target_price: Optional[float] = None
    analyst_upside_pct: Optional[float] = None
    analyst_ratings_consensus: Optional[str] = None  # "Buy", "Hold", "Sell"

    # Return estimation
    estimated_annual_return: float = 0  # As percentage
    dcf_implied_return: Optional[float] = None
    analyst_implied_return: Optional[float] = None

    # Scoring (detailed breakdown)
    industry_score: float = 50  # 0-100
    fundamental_quality_score: float = 50  # 0-100
    valuation_score: float = 50  # 0-100
    technical_confirmation_score: float = 50  # 0-100
    overall_score: float = 50  # 0-100

    # Score weights (for transparency)
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    # Classification
    classification: str = "Avoid"  # Strong Buy / Buy / Watchlist / Avoid

    # Investment thesis
    thesis: str = ""

    # Analysis timestamp
    analyzed_at: datetime = field(default_factory=datetime.now)


class DCFValuationModel:
    """Discounted Cash Flow valuation model with flexible assumptions"""

    def __init__(self,
                 revenue_growth_rates: List[float],  # Next 5 years
                 fcf_margin: float,
                 wacc: float = 0.08,
                 terminal_growth: float = 0.025,
                 shares_outstanding: Optional[float] = None,
                 net_debt: float = 0,
                 description: str = "Base Case"):
        """
        Args:
            revenue_growth_rates: Annual revenue growth for next 5 years
            fcf_margin: Free cash flow as % of revenue
            wacc: Weighted average cost of capital
            terminal_growth: Terminal growth rate (should be < WACC)
            shares_outstanding: Number of shares for per-share valuation
            net_debt: Net debt to adjust enterprise value
            description: Name of this scenario (e.g., "Conservative", "Base Case", "Optimistic")
        """
        self.revenue_growth_rates = revenue_growth_rates
        self.fcf_margin = fcf_margin
        self.wacc = wacc
        self.terminal_growth = terminal_growth
        self.shares_outstanding = shares_outstanding
        self.net_debt = net_debt
        self.description = description

    def calculate(self, current_revenue: float) -> DCFResult:
        """
        Calculate intrinsic value using DCF model

        Returns:
            DCFResult with detailed breakdown
        """
        try:
            if current_revenue <= 0 or self.wacc <= self.terminal_growth:
                return DCFResult(
                    per_share_value=None,
                    enterprise_value=None,
                    pv_fcf=0,
                    pv_terminal=0,
                    terminal_value=0,
                    assumptions=self._get_assumptions()
                )

            # Project free cash flows for next 5 years
            fcf_projections = []
            projected_revenue = current_revenue

            for growth_rate in self.revenue_growth_rates:
                projected_revenue *= (1 + growth_rate)
                fcf = projected_revenue * self.fcf_margin
                fcf_projections.append(fcf)

            # Calculate present value of projected FCFs
            pv_fcf = 0
            for year, fcf in enumerate(fcf_projections, 1):
                pv = fcf / ((1 + self.wacc) ** year)
                pv_fcf += pv

            # Terminal value (perpetuity growth model)
            terminal_fcf = fcf_projections[-1] * (1 + self.terminal_growth)
            terminal_value = terminal_fcf / (self.wacc - self.terminal_growth)
            pv_terminal = terminal_value / ((1 + self.wacc) ** len(self.revenue_growth_rates))

            # Enterprise value
            enterprise_value = pv_fcf + pv_terminal

            # Equity value (adjust for net debt)
            equity_value = enterprise_value - self.net_debt

            # Per-share value
            per_share_value = None
            if self.shares_outstanding and self.shares_outstanding > 0:
                per_share_value = equity_value / self.shares_outstanding

            return DCFResult(
                per_share_value=per_share_value,
                enterprise_value=enterprise_value,
                pv_fcf=pv_fcf,
                pv_terminal=pv_terminal,
                terminal_value=terminal_value,
                assumptions=self._get_assumptions()
            )
        except Exception as e:
            logger.warning(f"DCF calculation failed: {e}")
            return DCFResult(
                per_share_value=None,
                enterprise_value=None,
                pv_fcf=0,
                pv_terminal=0,
                terminal_value=0,
                assumptions=self._get_assumptions()
            )

    def _get_assumptions(self) -> Dict:
        return {
            'description': self.description,
            'revenue_growth_rates': self.revenue_growth_rates,
            'fcf_margin': self.fcf_margin,
            'wacc': self.wacc,
            'terminal_growth': self.terminal_growth,
            'shares_outstanding': self.shares_outstanding,
            'net_debt': self.net_debt
        }


class IndustryAnalyzer:
    """Analyzes industry strength, growth potential, and structural attractiveness"""

    INDUSTRY_CHARACTERISTICS = {
        'Technology': {
            'long_description': 'Software, semiconductors, cloud computing, AI, and hardware innovation',
            'growth_potential': 0.92,  # High secular growth
            'rd_intensity': 0.95,  # Massive R&D spending
            'structural_tailwinds': 0.88,  # Digital transformation, AI adoption
            'market_expansion': 0.85,  # TAM expansion from AI, cloud
            'competitive_positioning': 0.75,  # Winner-take-most dynamics
            'disruption_risk': 0.70,  # Rapid change
            'regulatory_risk': 0.45,  # Growing but manageable
            'real_world_adoption': 0.90,  # Proven, widespread
            'keywords': ['software', 'semiconductor', 'cloud', 'ai', 'it', 'computer', 'tech', 'saas', 'data']
        },
        'Healthcare': {
            'long_description': 'Pharmaceuticals, biotech, medical devices, diagnostics',
            'growth_potential': 0.85,
            'rd_intensity': 0.90,
            'structural_tailwinds': 0.88,  # Aging population, personalized medicine
            'market_expansion': 0.80,
            'competitive_positioning': 0.70,
            'disruption_risk': 0.60,
            'regulatory_risk': 0.85,  # FDA approval, pricing pressures
            'real_world_adoption': 0.95,  # Essential, proven
            'keywords': ['pharma', 'biotech', 'medical', 'health', 'healthcare', 'biotech', 'vaccine']
        },
        'Semiconductors': {
            'long_description': 'Chip design and manufacturing, foundries',
            'growth_potential': 0.88,
            'rd_intensity': 0.98,
            'structural_tailwinds': 0.92,  # AI, automotive, IoT demand
            'market_expansion': 0.88,
            'competitive_positioning': 0.65,  # Highly competitive
            'disruption_risk': 0.75,
            'regulatory_risk': 0.50,
            'real_world_adoption': 1.0,
            'keywords': ['semiconductor', 'chip', 'foundry', 'wafer', 'processor', 'gpu', 'cpu']
        },
        'Green Energy': {
            'long_description': 'Solar, wind, battery storage, EV infrastructure',
            'growth_potential': 0.90,
            'rd_intensity': 0.80,
            'structural_tailwinds': 0.95,  # Climate transition, policy support
            'market_expansion': 0.92,  # Rapidly growing market
            'competitive_positioning': 0.70,
            'disruption_risk': 0.60,
            'regulatory_risk': 0.40,  # Government supportive
            'real_world_adoption': 0.85,
            'keywords': ['renewable', 'solar', 'wind', 'battery', 'ev', 'electric vehicle', 'clean energy']
        },
        'Financial Services': {
            'long_description': 'Banks, fintech, payments, insurance',
            'growth_potential': 0.60,
            'rd_intensity': 0.65,
            'structural_tailwinds': 0.55,  # Fintech disruption
            'market_expansion': 0.50,
            'competitive_positioning': 0.60,
            'disruption_risk': 0.80,  # Fintech threat
            'regulatory_risk': 0.95,  # Heavy regulation
            'real_world_adoption': 0.90,
            'keywords': ['bank', 'finance', 'insurance', 'payment', 'fintech', 'crypto']
        },
        'Consumer Discretionary': {
            'long_description': 'Retail, automotive, luxury goods, entertainment',
            'growth_potential': 0.50,
            'rd_intensity': 0.40,
            'structural_tailwinds': 0.45,
            'market_expansion': 0.40,
            'competitive_positioning': 0.50,
            'disruption_risk': 0.75,  # E-commerce, economic sensitivity
            'regulatory_risk': 0.35,
            'real_world_adoption': 0.85,
            'keywords': ['retail', 'auto', 'consumer', 'luxury', 'apparel', 'fashion']
        },
        'Industrials': {
            'long_description': 'Manufacturing, aerospace, machinery, automation',
            'growth_potential': 0.55,
            'rd_intensity': 0.55,
            'structural_tailwinds': 0.60,  # Automation, infrastructure
            'market_expansion': 0.50,
            'competitive_positioning': 0.55,
            'disruption_risk': 0.60,
            'regulatory_risk': 0.60,
            'real_world_adoption': 0.85,
            'keywords': ['industrial', 'manufacturing', 'aerospace', 'automation', 'machinery']
        },
        'Energy': {
            'long_description': 'Oil, gas, coal (traditional energy)',
            'growth_potential': 0.25,
            'rd_intensity': 0.40,
            'structural_tailwinds': 0.15,  # Energy transition headwind
            'market_expansion': 0.20,
            'competitive_positioning': 0.50,
            'disruption_risk': 0.95,  # Secular decline
            'regulatory_risk': 0.90,
            'real_world_adoption': 0.90,
            'keywords': ['energy', 'oil', 'gas', 'coal', 'upstream']
        },
    }

    @classmethod
    def classify_industry(cls, company_name: str, sector: str = None) -> Tuple[str, float, Dict]:
        """
        Classify company into industry and calculate attractiveness score.
        Returns: (industry_name, attractiveness_score_0_100, characteristics_dict)
        """
        text = f"{company_name} {sector or ''}".lower()
        best_industry = 'Other'
        best_score = 0.5
        best_chars = None

        for industry, chars in cls.INDUSTRY_CHARACTERISTICS.items():
            if any(kw in text for kw in chars['keywords']):
                # Calculate weighted industry attractiveness
                # Emphasize growth, R&D, and structural tailwinds
                score = (
                    chars['growth_potential'] * 0.25 +
                    chars['rd_intensity'] * 0.20 +
                    chars['structural_tailwinds'] * 0.25 +
                    chars['market_expansion'] * 0.10 +
                    chars['competitive_positioning'] * 0.05 +
                    chars['real_world_adoption'] * 0.10 -
                    chars['disruption_risk'] * 0.02 -
                    chars['regulatory_risk'] * 0.03
                )
                if score > best_score:
                    best_score = score
                    best_industry = industry
                    best_chars = chars

        if best_chars is None:
            best_chars = {
                'long_description': 'Other/Uncategorized',
                'growth_potential': 0.5,
                'rd_intensity': 0.5,
                'structural_tailwinds': 0.5,
                'market_expansion': 0.5,
                'competitive_positioning': 0.5,
                'disruption_risk': 0.5,
                'regulatory_risk': 0.5,
                'real_world_adoption': 0.5,
            }

        # Normalize to 0-100
        attractiveness_score = max(0, min(100, best_score * 100))

        return best_industry, attractiveness_score, best_chars

    @classmethod
    def get_industry_rank(cls, symbols_analyses: List['StockAnalysis']) -> Dict[str, Dict]:
        """
        Rank industries based on stocks in the provided list.
        Returns dict with industry stats including average fundamentals.
        """
        industry_data = {}

        for analysis in symbols_analyses:
            if analysis.industry not in industry_data:
                industry_data[analysis.industry] = {
                    'count': 0,
                    'avg_growth': [],
                    'avg_pe': [],
                    'avg_roe': [],
                    'industry_score': analysis.industry_score,
                }

            data = industry_data[analysis.industry]
            data['count'] += 1

            if analysis.revenue_growth_3y is not None:
                data['avg_growth'].append(analysis.revenue_growth_3y)
            if analysis.valuation.pe_ratio is not None:
                data['avg_pe'].append(analysis.valuation.pe_ratio)
            if analysis.roe is not None:
                data['avg_roe'].append(analysis.roe)

        # Calculate averages
        for industry, data in industry_data.items():
            data['avg_growth'] = np.mean(data['avg_growth']) if data['avg_growth'] else None
            data['avg_pe'] = np.mean(data['avg_pe']) if data['avg_pe'] else None
            data['avg_roe'] = np.mean(data['avg_roe']) if data['avg_roe'] else None

        return industry_data


class RiskAssessment:
    """Comprehensive risk assessment framework with detailed categorization"""

    @staticmethod
    def assess_risks(symbol: str,
                    pe_ratio: Optional[float],
                    forward_pe: Optional[float],
                    debt_to_equity: Optional[float],
                    current_ratio: Optional[float],
                    revenue_growth: Optional[float],
                    roe: Optional[float],
                    industry: str,
                    market_cap: Optional[float] = None) -> RiskProfile:
        """
        Comprehensive risk assessment returning categorized risks and rating.
        Returns RiskProfile with detailed breakdown.
        """
        risk_factors = []
        temporary_risks = []
        structural_risks = []
        risk_score = 0
        invalidation_factors = []

        # === VALUATION RISKS ===
        if pe_ratio and pe_ratio > 50:
            structural_risks.append("Extremely high valuation - limited margin of safety")
            invalidation_factors.append("Revenue growth deceleration")
            risk_score += 25
        elif pe_ratio and pe_ratio > 35:
            risk_factors.append("High P/E ratio - company valued for significant future growth")
            temporary_risks.append("Multiple compression if growth slows")
            risk_score += 15
        elif pe_ratio and pe_ratio > 0 and pe_ratio < 5:
            temporary_risks.append("Low valuation may indicate temporary headwinds")
            risk_score += 8

        # Forward P/E expansion risk
        if forward_pe and pe_ratio and forward_pe > pe_ratio * 1.3:
            temporary_risks.append("Forward P/E significantly higher - earnings growth must accelerate")
            risk_score += 10

        # === FINANCIAL HEALTH RISKS ===
        if debt_to_equity and debt_to_equity > 3:
            structural_risks.append("Extremely high leverage - significant financial distress risk")
            invalidation_factors.append("Economic recession or interest rate shock")
            risk_score += 30
        elif debt_to_equity and debt_to_equity > 2:
            risk_factors.append("High leverage - elevated financial risk")
            temporary_risks.append("Rising interest rates could pressure profitability")
            risk_score += 18

        if current_ratio and current_ratio < 1:
            structural_risks.append("Liquidity crisis - current liabilities exceed current assets")
            risk_score += 20

        # === GROWTH TRAJECTORY RISKS ===
        if revenue_growth and revenue_growth < -0.05:
            structural_risks.append("Declining revenue - fundamental business deterioration")
            invalidation_factors.append("Continued revenue contraction")
            risk_score += 28
        elif revenue_growth and revenue_growth < 0:
            risk_factors.append("Flat or negative revenue growth")
            risk_score += 15
        elif revenue_growth and revenue_growth < 0.03:
            temporary_risks.append("Weak growth - below typical long-term expectations")
            risk_score += 8

        # === PROFITABILITY RISKS ===
        if roe and roe < 0:
            structural_risks.append("Negative ROE - destroying shareholder value")
            invalidation_factors.append("Failure to return to profitability")
            risk_score += 22

        if roe and roe > 0 and roe < 0.05:
            risk_factors.append("Low ROE - inefficient capital deployment")
            risk_score += 10

        # === INDUSTRY & COMPETITIVE RISKS ===
        if 'Energy' in industry:
            risk_factors.append("Energy transition headwinds - secular industry decline")
            structural_risks.append("Fossil fuel demand declining long-term")
            risk_score += 12
        elif 'Technology' in industry:
            risk_factors.append("Technology sector - rapid disruption and competitive threats")
            temporary_risks.append("Product obsolescence or competitive displacement")
            risk_score += 8

        if 'Financial' in industry:
            risk_factors.append("Financial services - regulatory and economic sensitivity")
            temporary_risks.append("Interest rate or credit cycle downturn")
            risk_score += 10

        # === BUSINESS SIZE & STABILITY RISKS ===
        if market_cap and market_cap < 1e9:
            risk_factors.append("Small-cap stock - lower liquidity, higher volatility")
            risk_score += 5

        # === DEFAULT GENERIC RISKS ===
        risk_factors.extend([
            "Macroeconomic risk - market downturn or recession",
            "Execution risk - management's ability to deliver on strategy",
        ])

        # Determine overall risk rating
        if risk_score >= 60:
            risk_rating = "Critical"
        elif risk_score >= 45:
            risk_rating = "High"
        elif risk_score >= 30:
            risk_rating = "Medium"
        else:
            risk_rating = "Low"

        return RiskProfile(
            risk_factors=risk_factors,
            risk_score=min(100, risk_score),
            temporary_risks=temporary_risks,
            structural_risks=structural_risks,
            risk_rating=risk_rating,
            invalidation_factors=invalidation_factors
        )


class LongTermStockPicker:
    """
    Main long-term stock picker engine.

    Comprehensive framework that prioritizes:
    - Fundamental strength (revenue growth, profitability, margins)
    - Reasonable valuation (DCF analysis, P/E comparison, upside potential)
    - Risk-adjusted return potential (>25% annual baseline)
    - Industry attractiveness and structural tailwinds
    - Technical confirmation as secondary validation

    Philosophy: Avoid hype-driven picks; focus on sustainable competitive advantages
    and real economic growth with margin of safety.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize with optional configuration.

        Config options:
            - min_annual_return: Minimum expected annual return for "Buy" (default: 0.25 = 25%)
            - watchlist_return_threshold: Minimum return for "Watchlist" (default: 0.15)
            - score_weights: Dict with 'industry', 'fundamental', 'valuation', 'technical', 'risk'
            - dcf_scenarios: List of (growth_rates, fcf_margin, description) tuples for scenario analysis
            - dcf_wacc: Discount rate for DCF (default: 0.08)
            - dcf_terminal_growth: Terminal growth rate (default: 0.025)
            - high_growth_threshold: Revenue growth threshold for "high growth" classification
            - quality_threshold: Minimum fundamental quality score for consideration
        """
        self.config = config or {}

        # Return thresholds
        self.min_annual_return = self.config.get('min_annual_return', 0.25)
        self.watchlist_return_threshold = self.config.get('watchlist_return_threshold', 0.15)

        # Scoring weights (must sum to 1.0)
        default_weights = {
            'industry': 0.15,
            'fundamental': 0.35,
            'valuation': 0.30,
            'technical': 0.10,
            'risk_adjustment': 0.10,
        }
        self.weights = self.config.get('score_weights', default_weights)

        # DCF parameters
        self.dcf_wacc = self.config.get('dcf_wacc', 0.08)
        self.dcf_terminal_growth = self.config.get('dcf_terminal_growth', 0.025)

        # DCF scenarios: conservative, base, and optimistic
        self.dcf_scenarios = self.config.get('dcf_scenarios', {
            'conservative': {
                'revenue_growth_rates': [0.08, 0.07, 0.06, 0.05, 0.04],
                'fcf_margin': 0.10,
                'description': 'Conservative'
            },
            'base': {
                'revenue_growth_rates': [0.15, 0.12, 0.10, 0.08, 0.06],
                'fcf_margin': 0.15,
                'description': 'Base Case'
            },
            'optimistic': {
                'revenue_growth_rates': [0.25, 0.20, 0.15, 0.12, 0.08],
                'fcf_margin': 0.18,
                'description': 'Optimistic'
            }
        })

        # Quality thresholds
        self.high_growth_threshold = self.config.get('high_growth_threshold', 0.15)  # 15% annual
        self.quality_threshold = self.config.get('quality_threshold', 40)  # Minimum fundamental score

    async def analyze_stock(self, symbol: str, use_scenario: str = 'base') -> Optional[StockAnalysis]:
        """
        Perform comprehensive analysis on a single stock using the full framework.

        Returns: StockAnalysis with complete breakdown of all components, or None if data unavailable
        """
        try:
            # Fetch stock data
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or info.get('regularMarketPrice', 0) == 0:
                logger.warning(f"Could not fetch data for {symbol}")
                return None

            # === DATA EXTRACTION ===
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            company_name = info.get('longName', symbol)
            sector = info.get('sector')
            market_cap = info.get('marketCap')

            # Get historical data for technical analysis
            hist = ticker.history(period='2y')

            # === VALUATION METRICS ===
            pe_ratio = info.get('trailingPE')
            forward_pe = info.get('forwardPE')
            pb_ratio = info.get('priceToBook')
            ps_ratio = info.get('priceToSalesTrailing12Months')
            peg_ratio = info.get('pegRatio')

            # === FUNDAMENTALS ===
            revenue_growth_ttm = info.get('revenueGrowth')
            revenue_growth_3y = info.get('revenueGrowth')  # Approximation
            net_margin = info.get('profitMargins')
            roe = info.get('returnOnEquity')
            roa = info.get('returnOnAssets')
            debt_to_equity = info.get('debtToEquity')
            current_ratio = info.get('currentRatio')

            # === INDUSTRY CLASSIFICATION ===
            industry, industry_score, industry_chars = IndustryAnalyzer.classify_industry(
                company_name, sector
            )

            # === TECHNICAL INDICATORS ===
            tech = self._calculate_technical_indicators(hist) if not hist.empty else TechnicalIndicators(
                rsi=None, adx=None, momentum=None, price_above_200ma=None, trend_direction="neutral"
            )

            # === RISK ASSESSMENT ===
            risk_profile = RiskAssessment.assess_risks(
                symbol=symbol,
                pe_ratio=pe_ratio,
                forward_pe=forward_pe,
                debt_to_equity=debt_to_equity,
                current_ratio=current_ratio,
                revenue_growth=revenue_growth_ttm,
                roe=roe,
                industry=industry,
                market_cap=market_cap
            )

            # === DCF VALUATION (SCENARIO-BASED) ===
            dcf_result = self._perform_dcf_valuation(
                info, symbol, use_scenario
            )
            intrinsic_value = dcf_result.per_share_value
            undervaluation_pct = None
            if intrinsic_value and current_price:
                undervaluation_pct = ((intrinsic_value - current_price) / current_price) * 100

            # === ANALYST DATA ===
            analyst_target_price = info.get('targetMeanPrice')
            analyst_upside_pct = None
            analyst_implied_return = None
            if analyst_target_price and current_price:
                analyst_upside_pct = ((analyst_target_price - current_price) / current_price) * 100
                analyst_implied_return = analyst_upside_pct

            # === SCORING ===
            scores = self._calculate_scores(
                industry_score=industry_score,
                revenue_growth=revenue_growth_ttm,
                roe=roe,
                net_margin=net_margin,
                debt_to_equity=debt_to_equity,
                pe_ratio=pe_ratio,
                forward_pe=forward_pe,
                undervaluation_pct=undervaluation_pct,
                technical_indicators=tech,
                risk_profile=risk_profile
            )

            # === RETURN ESTIMATION ===
            estimated_annual_return = self._estimate_annual_return(
                current_price=current_price,
                intrinsic_value=intrinsic_value,
                analyst_upside=analyst_upside_pct,
                revenue_growth=revenue_growth_ttm,
                undervaluation=undervaluation_pct
            )

            # === CLASSIFICATION ===
            classification = self._classify_stock(
                overall_score=scores['overall'],
                estimated_return=estimated_annual_return,
                risk_rating=risk_profile.risk_rating,
                min_return_threshold=self.min_annual_return
            )

            # === INVESTMENT THESIS ===
            thesis = self._generate_investment_thesis(
                symbol=symbol,
                company_name=company_name,
                industry=industry,
                classification=classification,
                revenue_growth=revenue_growth_ttm,
                undervaluation_pct=undervaluation_pct,
                estimated_return=estimated_annual_return,
                risk_profile=risk_profile,
                analyst_upside=analyst_upside_pct
            )

            # === BUILD VALUATION METRICS OBJECT ===
            valuation = ValuationMetrics(
                current_price=current_price,
                pe_ratio=pe_ratio,
                forward_pe=forward_pe,
                pb_ratio=pb_ratio,
                ps_ratio=ps_ratio,
                peg_ratio=peg_ratio,
                industry_pe=None,  # Would calculate from peer comparison
                pe_percentile=None,  # Would calculate from historical
                pe_historical_range=None
            )

            # === BUILD COMPLETE ANALYSIS ===
            return StockAnalysis(
                symbol=symbol,
                company_name=company_name,
                industry=industry,
                sector=sector,
                valuation=valuation,
                dcf=dcf_result,
                undervaluation_pct=undervaluation_pct,
                intrinsic_value=intrinsic_value,
                revenue_growth_3y=revenue_growth_3y,
                revenue_growth_ttm=revenue_growth_ttm,
                fcf_margin=self.dcf_scenarios[use_scenario]['fcf_margin'],
                net_margin=net_margin,
                debt_to_equity=debt_to_equity,
                roe=roe,
                roa=roa,
                current_ratio=current_ratio,
                technical=tech,
                risk_profile=risk_profile,
                analyst_target_price=analyst_target_price,
                analyst_upside_pct=analyst_upside_pct,
                analyst_implied_return=analyst_implied_return,
                estimated_annual_return=estimated_annual_return,
                dcf_implied_return=undervaluation_pct,
                industry_score=scores['industry'],
                fundamental_quality_score=scores['fundamental'],
                valuation_score=scores['valuation'],
                technical_confirmation_score=scores['technical'],
                overall_score=scores['overall'],
                score_breakdown=scores,
                classification=classification,
                thesis=thesis
            )

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
            return None

    def _calculate_technical_indicators(self, hist) -> TechnicalIndicators:
        """Calculate technical indicators for secondary confirmation"""
        try:
            close_prices = hist['Close']

            # RSI
            rsi = self._calculate_rsi(close_prices)

            # ADX
            adx = self._calculate_adx(hist)

            # Momentum
            momentum = ((close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0]) * 100 if len(close_prices) > 0 else None

            # Price above 200-day MA
            ma_200 = close_prices.rolling(window=200).mean()
            price_above_200ma = close_prices.iloc[-1] > ma_200.iloc[-1] if not ma_200.empty else None

            # Trend direction
            if adx and adx > 20:
                if close_prices.iloc[-1] > ma_200.iloc[-1]:
                    trend_direction = "uptrend"
                else:
                    trend_direction = "downtrend"
            else:
                trend_direction = "neutral"

            return TechnicalIndicators(
                rsi=rsi,
                adx=adx,
                momentum=momentum,
                price_above_200ma=price_above_200ma,
                trend_direction=trend_direction
            )
        except Exception as e:
            logger.warning(f"Technical analysis calculation failed: {e}")
            return TechnicalIndicators(
                rsi=None, adx=None, momentum=None, price_above_200ma=None, trend_direction="neutral"
            )

    def _calculate_rsi(self, prices, period=14) -> Optional[float]:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not rsi.empty and not np.isnan(rsi.iloc[-1]) else None
        except:
            return None

    def _calculate_adx(self, hist) -> Optional[float]:
        """Calculate ADX (Average Directional Index)"""
        try:
            high = hist['High']
            low = hist['Low']
            close = hist['Close']

            # True Range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Directional Indicators
            plus_dm = high.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm = -low.diff()
            minus_dm[minus_dm < 0] = 0

            # Calculate DI+, DI-
            tr_ma14 = tr.rolling(window=14).mean()
            plus_di = 100 * (plus_dm.rolling(window=14).mean() / tr_ma14)
            minus_di = 100 * (minus_dm.rolling(window=14).mean() / tr_ma14)

            # Calculate ADX
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=14).mean()

            return float(adx.iloc[-1]) if not adx.empty and not np.isnan(adx.iloc[-1]) else None
        except:
            return None

    def _perform_dcf_valuation(self, info: Dict, symbol: str, scenario: str = 'base') -> DCFResult:
        """Perform DCF valuation using specified scenario"""
        try:
            revenue = info.get('totalRevenue')
            if not revenue or revenue <= 0:
                return DCFResult(
                    per_share_value=None,
                    enterprise_value=None,
                    pv_fcf=0,
                    pv_terminal=0,
                    terminal_value=0,
                    assumptions={}
                )

            shares = info.get('sharesOutstanding', 1)
            if shares <= 0:
                shares = 1

            # Get scenario parameters
            scenario_config = self.dcf_scenarios.get(scenario, self.dcf_scenarios['base'])

            # Determine growth rates based on actual revenue growth
            actual_growth = info.get('revenueGrowth')
            growth_rates = scenario_config['revenue_growth_rates']

            # Adjust growth rates if actual growth is significantly lower
            if actual_growth and actual_growth < 0.05:
                growth_rates = [rate * 0.7 for rate in growth_rates]

            model = DCFValuationModel(
                revenue_growth_rates=growth_rates,
                fcf_margin=scenario_config['fcf_margin'],
                wacc=self.dcf_wacc,
                terminal_growth=self.dcf_terminal_growth,
                shares_outstanding=shares,
                net_debt=info.get('totalDebt', 0) - info.get('totalCash', 0),
                description=scenario_config['description']
            )

            return model.calculate(revenue)
        except Exception as e:
            logger.warning(f"DCF calculation failed for {symbol}: {e}")
            return DCFResult(
                per_share_value=None,
                enterprise_value=None,
                pv_fcf=0,
                pv_terminal=0,
                terminal_value=0,
                assumptions={}
            )

    def _calculate_scores(self, **metrics) -> Dict[str, float]:
        """
        Calculate comprehensive scoring breakdown with transparency.

        Returns dict with individual component scores and overall score.
        """
        # Extract metrics
        industry_score = metrics.get('industry_score', 50)
        revenue_growth = metrics.get('revenue_growth')
        roe = metrics.get('roe')
        net_margin = metrics.get('net_margin')
        debt_to_equity = metrics.get('debt_to_equity')
        pe_ratio = metrics.get('pe_ratio')
        forward_pe = metrics.get('forward_pe')
        undervaluation_pct = metrics.get('undervaluation_pct')
        technical_indicators = metrics.get('technical_indicators')
        risk_profile = metrics.get('risk_profile')

        # === FUNDAMENTAL QUALITY SCORE (35% weight) ===
        fundamental_score = 50
        if revenue_growth:
            if revenue_growth > 0.20:
                fundamental_score += 25
            elif revenue_growth > 0.15:
                fundamental_score += 20
            elif revenue_growth > 0.10:
                fundamental_score += 15
            elif revenue_growth > 0.05:
                fundamental_score += 10
            elif revenue_growth < 0:
                fundamental_score -= 30

        if roe:
            if roe > 0.25:
                fundamental_score += 20
            elif roe > 0.20:
                fundamental_score += 15
            elif roe > 0.15:
                fundamental_score += 10
            elif roe < 0:
                fundamental_score -= 25

        if net_margin:
            if net_margin > 0.20:
                fundamental_score += 10
            elif net_margin < 0:
                fundamental_score -= 15

        if debt_to_equity:
            if debt_to_equity < 1:
                fundamental_score += 10
            elif debt_to_equity > 3:
                fundamental_score -= 20
            elif debt_to_equity > 2:
                fundamental_score -= 15

        fundamental_score = max(0, min(100, fundamental_score))

        # === VALUATION SCORE (30% weight) ===
        valuation_score = 50
        if undervaluation_pct is not None:
            if undervaluation_pct > 40:
                valuation_score = 95
            elif undervaluation_pct > 30:
                valuation_score = 90
            elif undervaluation_pct > 20:
                valuation_score = 85
            elif undervaluation_pct > 10:
                valuation_score = 75
            elif undervaluation_pct > 0:
                valuation_score = 65
            elif undervaluation_pct > -15:
                valuation_score = 55
            else:
                valuation_score = max(0, 50 + undervaluation_pct)

        if pe_ratio:
            if pe_ratio > 50:
                valuation_score -= 20
            elif pe_ratio > 35:
                valuation_score -= 10

        valuation_score = max(0, min(100, valuation_score))

        # === TECHNICAL CONFIRMATION SCORE (10% weight, secondary) ===
        technical_score = 50
        if technical_indicators:
            if technical_indicators.adx and technical_indicators.adx > 25:
                technical_score += 15
            if technical_indicators.rsi:
                if 40 < technical_indicators.rsi < 60:
                    technical_score += 10
                elif 30 < technical_indicators.rsi < 70:
                    technical_score += 5
            if technical_indicators.momentum and technical_indicators.momentum > 0:
                technical_score += 10
            if technical_indicators.price_above_200ma:
                technical_score += 5

        technical_score = max(0, min(100, technical_score))

        # === RISK ADJUSTMENT (10% weight) ===
        risk_adjustment = 100 - risk_profile.risk_score if risk_profile else 50

        # === CALCULATE OVERALL SCORE ===
        overall_score = (
            industry_score * self.weights['industry'] +
            fundamental_score * self.weights['fundamental'] +
            valuation_score * self.weights['valuation'] +
            technical_score * self.weights['technical'] +
            risk_adjustment * self.weights['risk_adjustment']
        )

        return {
            'industry': industry_score,
            'fundamental': fundamental_score,
            'valuation': valuation_score,
            'technical': technical_score,
            'risk_adjustment': risk_adjustment,
            'overall': overall_score
        }

    def _estimate_annual_return(self,
                               current_price: float,
                               intrinsic_value: Optional[float],
                               analyst_upside: Optional[float],
                               revenue_growth: Optional[float],
                               undervaluation: Optional[float]) -> float:
        """
        Estimate expected annual return potential using multiple methods.

        Combines DCF-implied returns, analyst targets, and fundamental growth.
        """
        if not current_price or current_price <= 0:
            return 0

        returns = []

        # DCF-implied return (primary)
        if intrinsic_value and intrinsic_value > 0:
            dcf_return = ((intrinsic_value - current_price) / current_price) * 100
            returns.append(dcf_return * 0.5)  # 50% weight

        # Analyst upside (secondary)
        if analyst_upside:
            returns.append(analyst_upside * 0.3)  # 30% weight

        # Revenue growth as proxy for fundamental return (tertiary)
        if revenue_growth and revenue_growth > 0:
            growth_return = revenue_growth * 100 * 0.4  # 40% of revenue growth, 20% total weight
            returns.append(growth_return * 0.2)

        # Valuation mean reversion (if undervalued)
        if undervaluation and undervaluation > 10:
            # Mean reversion opportunity (conservative estimate)
            reversion_return = undervaluation * 0.5  # Assumes 50% reversion over time
            returns.append(reversion_return * 0.2)

        if not returns:
            return 0

        estimated = sum(returns) / 100
        return max(0, estimated * 100)

    def _classify_stock(self, overall_score: float, estimated_return: float,
                       risk_rating: str, min_return_threshold: float) -> str:
        """
        Classify stock based on composite framework.

        Strong Buy / Buy / Watchlist / Avoid
        """
        # Critical risk overrides everything
        if risk_rating == "Critical":
            return "Avoid"

        # High risk is very constraining
        if risk_rating == "High" and overall_score < 75:
            return "Avoid"

        # Below minimum return threshold = Watchlist or Avoid
        if estimated_return < min_return_threshold:
            if overall_score > 75:
                return "Watchlist"
            else:
                return "Avoid"

        # Strong Buy: Exceptional score + strong return
        if overall_score > 80 and estimated_return > (min_return_threshold * 1.5):
            return "Strong Buy"

        # Buy: Good score + meets return threshold
        if overall_score > 75 and estimated_return >= min_return_threshold:
            return "Buy"

        if overall_score > 70 and estimated_return >= (min_return_threshold * 1.2):
            return "Buy"

        # Watchlist: Good thesis but just below Buy threshold
        if overall_score > 65 and estimated_return >= (min_return_threshold * 0.8):
            return "Watchlist"

        return "Avoid"

    def _generate_investment_thesis(self, symbol: str, company_name: str, industry: str,
                                    classification: str, revenue_growth: Optional[float],
                                    undervaluation_pct: Optional[float],
                                    estimated_return: float,
                                    risk_profile: RiskProfile,
                                    analyst_upside: Optional[float]) -> str:
        """
        Generate comprehensive investment thesis covering:
        - Why this company
        - Why this industry
        - Why the valuation
        - Why the risk profile supports the thesis
        - Expected return and invalidation factors
        """
        parts = []

        # Company context
        parts.append(f"**{symbol}** ({company_name}) operates in {industry}")

        # Industry thesis
        parts.append(f"– an industry with structural growth tailwinds")

        # Valuation thesis
        if undervaluation_pct and undervaluation_pct > 0:
            parts.append(f"Trading at {abs(undervaluation_pct):.0f}% discount to DCF intrinsic value")
        elif undervaluation_pct:
            parts.append(f"Trading at fair value with {estimated_return:.0f}% upside from growth")
        else:
            parts.append(f"Valuation provides {estimated_return:.0f}% annual return potential")

        # Growth driver
        if revenue_growth and revenue_growth > 0.15:
            parts.append(f"driven by {revenue_growth*100:.0f}% YoY revenue growth")
        elif revenue_growth and revenue_growth > 0:
            parts.append(f"supported by {revenue_growth*100:.0f}% revenue growth")

        # Analyst view
        if analyst_upside:
            parts.append(f"Analyst price target implies {analyst_upside:.0f}% upside")

        # Risk summary
        if risk_profile.risk_rating == "Low":
            parts.append("Risk profile is low with stable fundamentals")
        elif risk_profile.risk_rating == "Medium":
            if risk_profile.temporary_risks:
                temp_risk = risk_profile.temporary_risks[0]
                parts.append(f"Risk profile is manageable; primary risk is {temp_risk.lower()}")
        elif risk_profile.structural_risks:
            struct_risk = risk_profile.structural_risks[0]
            parts.append(f"⚠️ Key risk: {struct_risk}")

        # Invalidation triggers
        if risk_profile.invalidation_factors:
            inv_factors = " / ".join(risk_profile.invalidation_factors[:2])
            parts.append(f"Thesis breaks if: {inv_factors}")

        thesis = ". ".join(parts) + "."
        return thesis

    async def rank_stocks(self, symbols: List[str]) -> List[StockAnalysis]:
        """
        Analyze and rank a list of stocks.
        Returns sorted by overall score, with industry ranking.
        """
        analyses = []

        for symbol in symbols:
            analysis = await self.analyze_stock(symbol)
            if analysis:
                analyses.append(analysis)

        # Sort by overall score (descending) then by classification
        classification_order = {"Strong Buy": 0, "Buy": 1, "Watchlist": 2, "Avoid": 3}
        analyses.sort(
            key=lambda x: (
                -x.overall_score,
                classification_order.get(x.classification, 4)
            )
        )

        return analyses

    def get_config(self) -> Dict:
        """Return current configuration for transparency"""
        return {
            'min_annual_return': self.min_annual_return,
            'watchlist_return_threshold': self.watchlist_return_threshold,
            'weights': self.weights,
            'dcf': {
                'wacc': self.dcf_wacc,
                'terminal_growth': self.dcf_terminal_growth,
                'scenarios': self.dcf_scenarios
            },
            'quality_threshold': self.quality_threshold,
            'high_growth_threshold': self.high_growth_threshold
        }

    def update_config(self, updates: Dict):
        """Update configuration with new parameters"""
        if 'min_annual_return' in updates:
            self.min_annual_return = updates['min_annual_return']
        if 'watchlist_return_threshold' in updates:
            self.watchlist_return_threshold = updates['watchlist_return_threshold']
        if 'score_weights' in updates:
            self.weights = updates['score_weights']
        if 'dcf' in updates:
            dcf_updates = updates['dcf']
            if 'wacc' in dcf_updates:
                self.dcf_wacc = dcf_updates['wacc']
            if 'terminal_growth' in dcf_updates:
                self.dcf_terminal_growth = dcf_updates['terminal_growth']
            if 'scenarios' in dcf_updates:
                self.dcf_scenarios = dcf_updates['scenarios']
        if 'quality_threshold' in updates:
            self.quality_threshold = updates['quality_threshold']

        logger.info(f"Long-term stock picker config updated")
