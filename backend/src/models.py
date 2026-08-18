from datetime import datetime, timedelta
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, Enum as SQLEnum, ForeignKey
import enum
from enum import Enum as PyEnum
from src.database import Base

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, index=True)
    name = Column(String(255))
    market = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

class TradeHorizon(str, enum.Enum):
    LONG_TERM = "long_term"
    SWING = "swing"
    INTRADAY = "intraday"

class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer)
    symbol = Column(String(20), index=True)
    horizon = Column(SQLEnum(TradeHorizon))
    direction = Column(String(10))
    rsi = Column(Float)
    adx = Column(Float)
    momentum = Column(Float)
    current_price = Column(Float)
    volume_ratio = Column(Float)
    breakout_timestamp = Column(DateTime)
    added_at = Column(DateTime, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    horizon = Column(SQLEnum(TradeHorizon))
    direction = Column(String(10))
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float)
    target_price = Column(Float)
    quantity = Column(Integer)
    status = Column(String(20))
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    quantity = Column(Integer)
    average_price = Column(Float)
    current_price = Column(Float)
    market_value = Column(Float)
    unrealised_pnl = Column(Float)
    unrealised_pnl_percent = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

class CustomWatchlist(Base):
    __tablename__ = "custom_watchlist"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(500), nullable=True)

class LongTermInvestmentClass(str, enum.Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    WATCHLIST = "watchlist"
    AVOID = "avoid"

class LongTermInvestmentAnalysis(Base):
    __tablename__ = "long_term_investment_analysis"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    company_name = Column(String(255))
    industry = Column(String(100))

    # Pricing
    current_price = Column(Float)
    pe_ratio = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    industry_pe = Column(Float, nullable=True)

    # DCF Valuation
    intrinsic_value = Column(Float, nullable=True)
    undervaluation_pct = Column(Float, nullable=True)

    # Fundamentals
    revenue_growth_3y = Column(Float, nullable=True)
    fcf_margin = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)

    # Technical
    rsi = Column(Float, nullable=True)
    adx = Column(Float, nullable=True)
    momentum = Column(Float, nullable=True)

    # Risk
    risk_factors = Column(String(1000), nullable=True)  # JSON string
    risk_score = Column(Float)

    # Analyst data
    analyst_target_price = Column(Float, nullable=True)
    analyst_upside_pct = Column(Float, nullable=True)

    # Scoring
    industry_score = Column(Float)
    fundamental_quality_score = Column(Float)
    dcf_score = Column(Float)
    technical_score = Column(Float)
    overall_score = Column(Float)

    # Return estimation
    estimated_annual_return = Column(Float)

    # Classification
    classification = Column(SQLEnum(LongTermInvestmentClass))

    # Investment thesis
    thesis = Column(String(1000))

    # Metadata
    analysis_date = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CatalystType(str, PyEnum):
    CORPORATE_EVENT = "corporate_event"
    SECTOR_MOMENTUM = "sector_momentum"
    NEWS_EVENT = "news_event"
    REGULATORY = "regulatory"
    EARNINGS = "earnings"
    THREAT = "threat"
    OPPORTUNITY = "opportunity"

class CatalystSentiment(str, PyEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"

class Catalyst(Base):
    __tablename__ = "catalysts"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    market = Column(String(10))  # NSE, BSE, NYSE

    # Catalyst details
    type = Column(SQLEnum(CatalystType), index=True)
    title = Column(String(500))
    description = Column(String(2000))
    sentiment = Column(SQLEnum(CatalystSentiment))

    # Timing
    event_date = Column(DateTime, nullable=True)
    announcement_date = Column(DateTime, nullable=True)
    discovery_date = Column(DateTime, default=datetime.utcnow)

    # Weighting
    confidence_score = Column(Float)
    impact_score = Column(Float)

    # Source tracking
    source = Column(String(100))
    source_url = Column(String(500), nullable=True)
    source_id = Column(String(100), nullable=True)

    # Context
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    price_impact_observed = Column(Boolean, default=False)
    volume_impact_observed = Column(Boolean, default=False)

    def __init__(self, **kwargs):
        """Initialize Catalyst with default values"""
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        if 'detected_at' not in kwargs:
            kwargs['detected_at'] = datetime.utcnow()
        if 'price_impact_observed' not in kwargs:
            kwargs['price_impact_observed'] = False
        if 'volume_impact_observed' not in kwargs:
            kwargs['volume_impact_observed'] = False
        super().__init__(**kwargs)

class CatalystAnalysis(Base):
    """DeepSeek analysis of catalyst quality and confidence"""
    __tablename__ = "catalyst_analysis"

    id = Column(Integer, primary_key=True)
    catalyst_id = Column(Integer, ForeignKey("catalysts.id"))

    analysis_text = Column(String(2000))
    reasoning_confidence = Column(Float)
    suggested_sentiment = Column(SQLEnum(CatalystSentiment))

    is_valid = Column(Boolean)
    relevance_score = Column(Float)

    analyzed_at = Column(DateTime, default=datetime.utcnow)

class AnomalyType(str, enum.Enum):
    PRICE_BREAKOUT = "price_breakout"
    VOLUME_SPIKE = "volume_spike"
    PRICE_VOLUME_CONFLUENCE = "confluence"
    RSI_EXTREME = "rsi_extreme"
    ADX_SURGE = "adx_surge"
    MA_CROSSOVER = "ma_crossover"

class MarketCapClass(str, enum.Enum):
    LARGE_CAP = "large_cap"
    MID_CAP = "mid_cap"
    SMALL_CAP = "small_cap"

class PriceVolumeAnomaly(Base):
    __tablename__ = "price_volume_anomalies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    market = Column(String(10))

    # Anomaly details
    type = Column(SQLEnum(AnomalyType), index=True)
    market_cap_class = Column(SQLEnum(MarketCapClass))

    # Price metrics
    price_change_percent = Column(Float)
    price_current = Column(Float)
    price_ma_20 = Column(Float, nullable=True)
    price_ma_50 = Column(Float, nullable=True)

    # Volume metrics
    volume_change_percent = Column(Float)
    volume_current = Column(Float)
    volume_avg_5day = Column(Float)
    volume_relative_strength = Column(Float)

    # Technical indicators
    rsi = Column(Float, nullable=True)
    adx = Column(Float, nullable=True)
    momentum = Column(Float, nullable=True)

    # Liquidity info
    liquidity_quality_score = Column(Float, nullable=True)
    volume_distribution_healthy = Column(Boolean, nullable=True)

    # Confirmation
    technical_confirmation_score = Column(Float)
    is_manipulation_risk = Column(Boolean, default=False)

    # Timing
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    timestamp = Column(DateTime)

    def __init__(self, **kwargs):
        """Initialize PriceVolumeAnomaly with default values"""
        if 'is_manipulation_risk' not in kwargs:
            kwargs['is_manipulation_risk'] = False
        if 'detected_at' not in kwargs:
            kwargs['detected_at'] = datetime.utcnow()
        super().__init__(**kwargs)

# Filter 4: Volatility & Trend Direction
class TrendType(str, enum.Enum):
    """Trend classification for stocks"""
    STRONG_UPTREND = "strong_uptrend"
    UPTREND = "uptrend"
    SIDEWAYS = "sideways"
    DOWNTREND = "downtrend"
    STRONG_DOWNTREND = "strong_downtrend"

class BollingerBandPosition(str, enum.Enum):
    """Position of price relative to Bollinger Bands"""
    ABOVE_UPPER = "above_upper"
    NEAR_UPPER = "near_upper"
    BETWEEN = "between"
    NEAR_LOWER = "near_lower"
    BELOW_LOWER = "below_lower"

class MAAlignment(str, enum.Enum):
    """Moving average alignment pattern"""
    BULLISH_ALIGNED = "bullish_aligned"        # MA20 > MA50 > MA200
    BEARISH_ALIGNED = "bearish_aligned"        # MA20 < MA50 < MA200
    MIXED = "mixed"                            # No clear alignment
    NOT_ENOUGH_DATA = "not_enough_data"        # Less than 200 bars

class VolatilityTrendSignal(Base):
    """
    Volatility & Trend Direction signals for Filter 4

    Tracks:
    - Bollinger Band width and position
    - Moving average direction and alignment
    - Trend type and strength
    - Volatility expansion/contraction
    - MA crossover signals
    """
    __tablename__ = "volatility_trend_signals"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    market = Column(String(10))

    # Bollinger Bands (20-period, 2 std dev)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    bb_width = Column(Float)
    bb_width_percent = Column(Float)                    # Width as % of middle
    price_position = Column(SQLEnum(BollingerBandPosition))

    # Bollinger Band dynamics
    bb_width_expanding = Column(Boolean)                # Volatility expanding?
    bb_width_change_percent = Column(Float)             # Change from previous bar

    # Moving Averages
    ma_20 = Column(Float)
    ma_50 = Column(Float)
    ma_200 = Column(Float, nullable=True)

    # MA direction
    ma_20_direction = Column(String(10))                # "up" or "down"
    ma_50_direction = Column(String(10))
    ma_20_slope = Column(Float)                         # Rate of change
    ma_50_slope = Column(Float)

    # MA alignment
    ma_alignment = Column(SQLEnum(MAAlignment))

    # Trend analysis
    trend_type = Column(SQLEnum(TrendType))
    trend_strength = Column(Float)                      # 0-1 scale

    # Price relative to MAs
    price_above_ma20 = Column(Boolean)
    price_above_ma50 = Column(Boolean)
    price_above_ma200 = Column(Boolean, nullable=True)

    # Volatility metrics
    volatility_atr = Column(Float)                      # Average True Range
    volatility_percent = Column(Float)                  # (H-L)/C percentage
    volatility_trend = Column(String(10))               # "increasing" or "decreasing"

    # Trend continuation vs emerging
    trend_continuation = Column(Boolean)                # Is current trend continuing?
    emerging_trend = Column(Boolean)                    # Is new trend forming?

    # Technical confirmation
    trend_confirmation_score = Column(Float)            # 0-1 scale based on MA agreement
    volatility_confirmation_score = Column(Float)       # 0-1 scale

    # Risk flags
    volatility_extreme = Column(Boolean)                # Unusual volatility?
    is_trend_exhaustion = Column(Boolean)               # Potential trend reversal?

    # Timing
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    timestamp = Column(DateTime)

    def __init__(self, **kwargs):
        """Initialize VolatilityTrendSignal with default values"""
        if 'detected_at' not in kwargs:
            kwargs['detected_at'] = datetime.utcnow()
        super().__init__(**kwargs)

# Filter 5: Candlestick Monitoring
class CandleColor(str, enum.Enum):
    """Candle color classification"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    DOJI = "doji"
    HAMMER = "hammer"
    HANGING_MAN = "hanging_man"

class CandlePattern(str, enum.Enum):
    """Candlestick pattern types"""
    ENGULFING = "engulfing"
    HARAMI = "harami"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"
    PIERCING_LINE = "piercing_line"
    DARK_CLOUD_COVER = "dark_cloud_cover"
    SPINNING_TOP = "spinning_top"
    NONE = "none"

class CandlePosition(str, enum.Enum):
    """Position of candle relative to technical levels"""
    ABOVE_UPPER_BB = "above_upper_bb"
    ABOVE_MA20 = "above_ma20"
    ABOVE_MA50 = "above_ma50"
    BETWEEN_MA20_MA50 = "between_ma20_ma50"
    BELOW_MA50 = "below_ma50"
    BELOW_LOWER_BB = "below_lower_bb"
    NEAR_SUPPORT = "near_support"
    NEAR_RESISTANCE = "near_resistance"

class CandlestickSignal(Base):
    """
    Candlestick analysis signals for Filter 5

    Tracks:
    - Current candle color (bullish/bearish/doji)
    - Multi-candle patterns (engulfing, harami, morning/evening star)
    - Price position relative to technical levels
    - Candle quality scoring
    - Pattern strength and reliability
    """
    __tablename__ = "candlestick_signals"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    market = Column(String(10))

    # Current Candle Properties
    candle_color = Column(SQLEnum(CandleColor))
    candle_open = Column(Float)
    candle_high = Column(Float)
    candle_low = Column(Float)
    candle_close = Column(Float)
    candle_range = Column(Float)                         # High - Low
    candle_body = Column(Float)                          # Close - Open
    candle_upper_wick = Column(Float)                    # High - max(Open, Close)
    candle_lower_wick = Column(Float)                    # min(Open, Close) - Low
    candle_volume = Column(Float)

    # Candle Strength
    body_strength = Column(Float)                        # Body / Range ratio
    wick_strength = Column(Float)                        # Wick / Body ratio
    candle_size = Column(String(10))                     # "large", "medium", "small"
    candle_quality_score = Column(Float)                 # 0-1 scale

    # Relative Position
    position = Column(SQLEnum(CandlePosition))
    distance_from_ma20 = Column(Float)                   # % distance
    distance_from_ma50 = Column(Float)
    distance_from_upper_bb = Column(Float)
    distance_from_lower_bb = Column(Float)

    # Pattern Detection
    pattern_type = Column(SQLEnum(CandlePattern))
    pattern_strength = Column(Float)                     # 0-1 scale
    is_continuation_pattern = Column(Boolean)            # vs reversal
    is_reversal_pattern = Column(Boolean)

    # Multi-candle signals (previous candles)
    prev_candle_color = Column(SQLEnum(CandleColor))     # Previous bar
    prev_candle_body = Column(Float)
    two_bar_pattern = Column(String(50))                 # e.g., "bullish_engulfing"
    three_bar_pattern = Column(String(50))               # e.g., "morning_star"

    # Volume Analysis
    volume_confirmation = Column(Boolean)                # Volume supports signal?
    volume_vs_avg = Column(Float)                        # Current / Average ratio
    volume_trend = Column(String(10))                    # "increasing", "decreasing"

    # Risk Assessment
    candle_rejection = Column(Boolean)                   # Price rejected at level?
    is_inside_bar = Column(Boolean)                      # Current bar inside previous?
    is_pin_bar = Column(Boolean)                         # Long wick rejection candle?

    # Confirmation Scores
    pattern_confirmation_score = Column(Float)           # 0-1 scale
    volume_confirmation_score = Column(Float)
    overall_signal_strength = Column(Float)              # Composite score

    # Timing
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    timestamp = Column(DateTime)

    def __init__(self, **kwargs):
        """Initialize CandlestickSignal with default values"""
        if 'detected_at' not in kwargs:
            kwargs['detected_at'] = datetime.utcnow()
        super().__init__(**kwargs)

# Filter 6: Confluence & Final Ranking
class OpportunityRating(str, enum.Enum):
    """Overall opportunity rating from confluence of signals"""
    STRONG_BUY = "strong_buy"           # 4+ filters agree, confidence > 0.80
    BUY = "buy"                         # 3+ filters agree, confidence > 0.65
    NEUTRAL = "neutral"                 # Mixed signals
    SELL = "sell"                       # 3+ filters agree negative
    STRONG_SELL = "strong_sell"         # 4+ filters agree negative, confidence > 0.80

class TradeDirection(str, enum.Enum):
    """Trade direction based on confluence"""
    LONG = "long"                       # Bullish confluence
    SHORT = "short"                     # Bearish confluence
    NEUTRAL = "neutral"                 # No clear direction

class EddieFinalSignal(Base):
    """
    Final confluence signal combining all 5 filters

    Aggregates:
    - Filter 1: Market detection (context)
    - Filter 2: Catalyst detection (fundamental)
    - Filter 3: Price/volume anomalies (technical)
    - Filter 4: Volatility & trend (directional)
    - Filter 5: Candlestick patterns (confirmation)

    Produces final opportunity ranking and confidence assessment
    """
    __tablename__ = "eddie_final_signals"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    market = Column(String(10))

    # Context
    active_market = Column(String(10))                   # Which market is active
    user_timezone = Column(String(50), nullable=True)
    market_cap_class = Column(SQLEnum(MarketCapClass), nullable=True)  # LARGE_CAP, MID_CAP, SMALL_CAP

    # Signal Agreement (Confluence)
    bullish_filters_count = Column(Integer)              # How many filters bullish
    bearish_filters_count = Column(Integer)              # How many filters bearish
    neutral_filters_count = Column(Integer)              # How many filters neutral
    total_agreement = Column(Float)                      # % filters agreeing (0-1)

    # Individual Filter Signals
    catalyst_signal = Column(String(20))                 # "bullish", "bearish", "neutral"
    catalyst_strength = Column(Float)

    anomaly_signal = Column(String(20))
    anomaly_strength = Column(Float)

    trend_signal = Column(String(20))
    trend_strength = Column(Float)

    candle_signal = Column(String(20))
    candle_strength = Column(Float)

    # Final Analysis
    direction = Column(SQLEnum(TradeDirection))
    rating = Column(SQLEnum(OpportunityRating))

    # Confidence Metrics
    filter_consensus_score = Column(Float)               # % of filters agreeing
    signal_strength_score = Column(Float)                # 0-1 scale
    risk_score = Column(Float)                           # Risk assessment (0-1)
    noise_reduction_factor = Column(Float)               # Signal clarity (0-1)

    # Final Confidence
    overall_confidence = Column(Float)                   # Final confidence (0-1)

    # Signal Quality
    is_high_probability = Column(Boolean)                # Confidence > 0.75?
    is_low_noise = Column(Boolean)                       # Clear signal > 0.70?
    requires_confirmation = Column(Boolean)              # Wait for more filters?

    # Key Levels for Trade
    entry_zone_low = Column(Float, nullable=True)
    entry_zone_high = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True)

    # Rationale
    key_signals = Column(String(500))                    # Comma-separated signal reasons
    risk_factors = Column(String(300))                   # Comma-separated risks
    confirmation_needed = Column(String(200))            # What would confirm

    # Timing
    signal_age_minutes = Column(Integer)                 # Minutes since freshest filter signal
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)                        # When signal expires

    def __init__(self, **kwargs):
        """Initialize EddieFinalSignal with default values"""
        if 'detected_at' not in kwargs:
            kwargs['detected_at'] = datetime.utcnow()
        # Signal expires in 24 hours
        if 'expires_at' not in kwargs:
            kwargs['expires_at'] = datetime.utcnow() + timedelta(hours=24)
        super().__init__(**kwargs)
