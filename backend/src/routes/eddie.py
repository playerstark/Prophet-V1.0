from fastapi import APIRouter, Query, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Optional
import pytz
import pytz.exceptions
from src.services.market_detector import MarketDetector
from src.services.catalyst_detector import CatalystDetector
from src.services.catalyst_data_fetcher import CatalystDataFetcher
from src.services.catalyst_analyzer import CatalystAnalyzer
from src.services.price_volume_analyzer import PriceVolumeAnalyzer
from src.services.price_volume_data_fetcher import PriceVolumeDataFetcher
from src.services.volatility_trend_analyzer import VolatilityTrendAnalyzer
from src.services.candlestick_analyzer import CandlestickAnalyzer
from src.services.confluence_analyzer import ConfluenceAnalyzer
from src.database import get_db
from src.models import (
    Catalyst, CatalystAnalysis, CatalystSentiment,
    PriceVolumeAnomaly, AnomalyType, MarketCapClass,
    VolatilityTrendSignal, TrendType, BollingerBandPosition, MAAlignment,
    CandlestickSignal, CandleColor, CandlePattern, CandlePosition,
    EddieFinalSignal, TradeDirection, OpportunityRating
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/eddie", tags=["eddie"])
detector = MarketDetector()
catalyst_detector = CatalystDetector()
catalyst_fetcher = CatalystDataFetcher()
catalyst_analyzer = CatalystAnalyzer()
price_volume_analyzer = PriceVolumeAnalyzer()
price_volume_fetcher = PriceVolumeDataFetcher()
volatility_trend_analyzer = VolatilityTrendAnalyzer()
candlestick_analyzer = CandlestickAnalyzer()
confluence_analyzer = ConfluenceAnalyzer()

@router.get("/market/active")
async def get_active_market(timezone: Optional[str] = Query(None, description="User's timezone (e.g., 'Asia/Kolkata', 'US/Eastern')")):
    """
    Determine which market is currently active for the user

    Returns the active market based on:
    - User's current timezone (if provided)
    - Current time
    - Market trading hours
    - Market holidays

    Query Parameters:
    - timezone: Optional timezone string. If not provided, uses UTC.

    Response:
    {
        "market": "NSE|BSE|NYSE",
        "region": "INDIA|US",
        "is_open": true,
        "open_time": "HH:MM",
        "close_time": "HH:MM",
        "timezone": "Asia/Kolkata|US/Eastern",
        "current_time": "ISO timestamp"
    }
    Or null if no market is open
    """
    try:
        if timezone:
            # Validate timezone parameter
            if not isinstance(timezone, str) or not timezone.strip():
                raise pytz.exceptions.UnknownTimeZoneError(f"Invalid timezone: '{timezone}'")

            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
        else:
            current_time = datetime.now(pytz.UTC)

        active_market = detector.get_active_market(current_time)

        if active_market:
            return {
                **active_market,
                "current_time": current_time.isoformat()
            }
        else:
            return {
                "market": None,
                "is_open": False,
                "current_time": current_time.isoformat(),
                "message": "All markets are currently closed"
            }

    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(
            status_code=422,
            detail="Invalid timezone. Use IANA timezone format (e.g., 'Asia/Kolkata', 'US/Eastern')"
        )

@router.get("/market/status/{market_code}")
async def get_market_status(market_code: str):
    """
    Get detailed status for a specific market

    Path Parameters:
    - market_code: Market code (NSE, BSE, NYSE)

    Response:
    {
        "market": "NSE",
        "is_open": true,
        "timezone": "Asia/Kolkata",
        "current_time": "2024-01-08 10:30:00 IST",
        "open_time": "09:15",
        "close_time": "15:30",
        "session": "main|pre_market|post_market|closed",
        "region": "INDIA"
    }
    """
    # Validate market_code input
    if not market_code or not isinstance(market_code, str):
        raise HTTPException(
            status_code=400,
            detail="Market code must be a non-empty string"
        )

    status = detector.get_market_status(market_code.upper())

    if 'error' in status:
        raise HTTPException(
            status_code=404,
            detail=f"Market '{market_code.upper()}' not found. Available markets: NSE, BSE, NYSE"
        )

    return status

@router.get("/market/all-status")
async def get_all_markets_status():
    """
    Get status for all supported markets

    Response:
    {
        "NSE": { ... },
        "BSE": { ... },
        "NYSE": { ... },
        "active_market": "NSE|BSE|NYSE|null"
    }
    """
    current_time = datetime.now(pytz.UTC)
    active = detector.get_active_market(current_time)
    active_market = active['market'] if active else None

    status = {}
    for market_code in ["NSE", "BSE", "NYSE"]:
        market_status = detector.get_market_status(market_code)
        status[market_code] = market_status

    status["active_market"] = active_market

    return status

@router.get("/catalysts/stock/{symbol}")
async def get_stock_catalysts(
    symbol: str,
    days_back: int = Query(14, ge=1, le=90),
    sentiment: Optional[str] = Query(None, regex="^(positive|negative|neutral)$")
):
    """
    Get catalysts for a specific stock

    Path: /api/eddie/catalysts/stock/{symbol}

    Query Parameters:
    - days_back: Number of days to look back (1-90, default 14)
    - sentiment: Filter by sentiment (positive, negative, neutral, or None)

    Response:
    {
        "symbol": "AAPL",
        "catalysts": [...],
        "count": 5
    }
    """
    try:
        # Fetch news for stock
        news = await catalyst_fetcher.fetch_company_news(symbol, days_back=days_back)
        catalysts = []

        for article in news:
            catalyst = catalyst_fetcher.parse_news_to_catalyst(article)
            catalyst_type = catalyst_detector.detect_catalyst_type(catalyst)
            catalyst_sentiment = catalyst_detector.classify_sentiment(catalyst.get('title', ''))

            catalyst.update({
                'type': catalyst_type['type'].value,
                'sentiment': catalyst_sentiment.value,
                'confidence': catalyst_detector.calculate_confidence_score({
                    'type_confidence': catalyst_type['confidence'],
                    'source': catalyst.get('source')
                })
            })

            if sentiment is None or catalyst['sentiment'] == sentiment:
                if catalyst_detector.is_catalyst_still_relevant(catalyst):
                    catalysts.append(catalyst)

        # Deduplicate
        catalysts = catalyst_detector.deduplicate_catalysts(catalysts)

        return {
            'symbol': symbol,
            'catalysts': catalysts[:10],
            'count': len(catalysts)
        }
    except Exception as e:
        return {
            'error': f'Error fetching catalysts for {symbol}: {str(e)}',
            'symbol': symbol,
            'catalysts': []
        }

@router.get("/catalysts/earnings-calendar")
async def get_earnings_calendar(days_forward: int = Query(30, ge=1, le=90)):
    """
    Get upcoming earnings events

    Path: /api/eddie/catalysts/earnings-calendar

    Query Parameters:
    - days_forward: Number of days to look forward (1-90, default 30)

    Response:
    {
        "earnings": [...],
        "count": 5
    }
    """
    try:
        earnings = await catalyst_fetcher.fetch_earnings_calendar(days_forward=days_forward)

        return {
            'earnings': earnings,
            'count': len(earnings)
        }
    except Exception as e:
        return {
            'error': f'Error fetching earnings calendar: {str(e)}',
            'earnings': []
        }

@router.get("/catalysts/sector-leaders")
async def get_sector_leaders():
    """
    Get best performing sectors (sector momentum)

    Path: /api/eddie/catalysts/sector-leaders

    Response:
    {
        "sectors": {
            "Technology": 2.5,
            "Healthcare": 1.8
        }
    }
    """
    try:
        sectors = await catalyst_fetcher.fetch_sector_performance()

        return {
            'sectors': sectors
        }
    except Exception as e:
        return {
            'error': f'Error fetching sector performance: {str(e)}',
            'sectors': {}
        }

@router.post("/catalysts/analyze/{symbol}")
async def analyze_stock_for_catalysts(
    symbol: str,
    db: Session = Depends(get_db),
    force_refresh: bool = Query(False)
):
    """
    Analyze stock for catalysts and store in database.

    Path: /api/eddie/catalysts/analyze/{symbol}

    Query Parameters:
    - force_refresh: Force fresh data fetch (default False)

    Response:
    {
        "status": "analyzed|cached",
        "symbol": "AAPL",
        "catalysts_found": 3,
        "market": "NYSE|NSE|BSE",
        "message": "..."
    }
    """
    # Detect market based on symbol
    detected_market = detector.get_symbol_market(symbol)
    market = detected_market if detected_market else 'US'
    market_code = market if market in ['NSE', 'BSE', 'NYSE'] else 'NYSE'

    # Check for recent cached data
    if not force_refresh:
        recent = db.query(Catalyst).filter(
            Catalyst.symbol == symbol,
            Catalyst.detected_at > datetime.now(pytz.UTC) - timedelta(hours=1)
        ).first()

        if recent:
            return {
                'status': 'cached',
                'symbol': symbol,
                'market': market_code,
                'message': 'Using cached catalyst data from last hour'
            }

    try:
        # Fetch fresh data
        news = await catalyst_fetcher.fetch_company_news(symbol)

        stored_catalysts = []

        for article in news:
            catalyst_dict = catalyst_fetcher.parse_news_to_catalyst(article)
            catalyst_type = catalyst_detector.detect_catalyst_type(catalyst_dict)
            sentiment = catalyst_detector.classify_sentiment(catalyst_dict.get('title', ''))

            confidence = catalyst_detector.calculate_confidence_score({
                'type_confidence': catalyst_type['confidence'],
                'source': catalyst_dict.get('source')
            })

            # Create database record
            catalyst = Catalyst(
                symbol=symbol,
                market=market_code,
                type=catalyst_type['type'],
                title=catalyst_dict.get('title'),
                description=catalyst_dict.get('description'),
                sentiment=sentiment,
                event_date=catalyst_dict.get('event_date'),
                confidence_score=confidence,
                impact_score=0.7,  # Default, could be calculated
                source=catalyst_dict.get('source'),
                source_url=catalyst_dict.get('source_url'),
                source_id=catalyst_dict.get('source_id')
            )

            db.add(catalyst)
            stored_catalysts.append(catalyst)

        db.commit()

        return {
            'status': 'analyzed',
            'symbol': symbol,
            'market': market_code,
            'catalysts_found': len(stored_catalysts),
            'message': f'Analyzed {len(stored_catalysts)} catalysts for {symbol}'
        }

    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'symbol': symbol,
            'market': market_code,
            'error': str(e),
            'catalysts_found': 0
        }

@router.get("/catalysts/active")
async def get_active_catalysts(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get most recent active catalysts across all stocks.

    Path: /api/eddie/catalysts/active

    Query Parameters:
    - limit: Maximum catalysts to return (default 10)

    Response:
    {
        "catalysts": [...],
        "count": 10
    }
    """
    # Get catalysts from last 48 hours
    recent_time = datetime.now(pytz.UTC) - timedelta(hours=48)

    catalysts = db.query(Catalyst).filter(
        Catalyst.detected_at > recent_time,
        Catalyst.is_active == True
    ).order_by(Catalyst.detected_at.desc()).limit(limit).all()

    return {
        'catalysts': [
            {
                'symbol': c.symbol,
                'type': c.type.value,
                'title': c.title,
                'sentiment': c.sentiment.value,
                'confidence': c.confidence_score,
                'detected_at': c.detected_at.isoformat()
            }
            for c in catalysts
        ],
        'count': len(catalysts)
    }

@router.post("/anomalies/scan/{symbol}")
async def scan_stock_for_anomalies(
    symbol: str,
    db: Session = Depends(get_db),
    force_refresh: bool = Query(False)
):
    """
    Analyze stock for price/volume anomalies and store in database.

    Path: /api/eddie/anomalies/scan/{symbol}

    Query Parameters:
    - force_refresh: Force fresh data fetch (default False)

    Response:
    {
        "status": "analyzed|cached",
        "symbol": "AAPL",
        "anomalies_found": 2,
        "market": "NYSE|NSE|BSE",
        "message": "..."
    }
    """
    # Detect market based on symbol
    detected_market = detector.get_symbol_market(symbol)
    market = detected_market if detected_market else 'NYSE'

    # Check for recent cached data
    if not force_refresh:
        recent = db.query(PriceVolumeAnomaly).filter(
            PriceVolumeAnomaly.symbol == symbol,
            PriceVolumeAnomaly.detected_at > datetime.now(pytz.UTC) - timedelta(hours=1)
        ).first()

        if recent:
            return {
                'status': 'cached',
                'symbol': symbol,
                'market': market,
                'message': 'Using cached anomaly data from last hour'
            }

    try:
        # Fetch data bundle
        data_bundle = await price_volume_fetcher.fetch_stock_data_bundle(symbol)
        if not data_bundle:
            raise HTTPException(status_code=404, detail=f"Could not fetch data for {symbol}")

        intraday_60m = data_bundle['intraday_60m']
        historical_60d = data_bundle['historical_60d']
        market_cap = data_bundle['market_cap']

        if intraday_60m is None and historical_60d is None:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

        # Use intraday if available, fallback to historical
        ohlcv = intraday_60m if intraday_60m is not None else historical_60d

        stored_anomalies = []

        # Detect price breakout
        breakout = price_volume_analyzer.detect_price_breakout(ohlcv)
        if breakout:
            anomaly = PriceVolumeAnomaly(
                symbol=symbol,
                market=market,
                type=AnomalyType.PRICE_BREAKOUT,
                market_cap_class=price_volume_analyzer.classify_market_cap(market_cap) if market_cap else None,
                price_change_percent=breakout.get('breakout_percent'),
                price_current=breakout.get('current_price'),
                volume_change_percent=0,
                volume_current=ohlcv['Volume'].iloc[-1] if 'Volume' in ohlcv.columns else 0,
                volume_avg_5day=ohlcv['Volume'].tail(5).mean() if 'Volume' in ohlcv.columns else 0,
                volume_relative_strength=1.0,
                technical_confirmation_score=breakout.get('confidence', 0.7),
                is_manipulation_risk=False
            )
            db.add(anomaly)
            stored_anomalies.append(anomaly)

        # Detect volume spike
        volume_spike = price_volume_analyzer.detect_volume_spike(ohlcv)
        if volume_spike:
            anomaly = PriceVolumeAnomaly(
                symbol=symbol,
                market=market,
                type=AnomalyType.VOLUME_SPIKE,
                market_cap_class=price_volume_analyzer.classify_market_cap(market_cap) if market_cap else None,
                price_change_percent=0,
                price_current=ohlcv['Close'].iloc[-1] if 'Close' in ohlcv.columns else 0,
                volume_change_percent=volume_spike.get('spike_ratio', 0) * 100,
                volume_current=volume_spike.get('current_volume'),
                volume_avg_5day=volume_spike.get('avg_volume'),
                volume_relative_strength=volume_spike.get('spike_ratio'),
                technical_confirmation_score=volume_spike.get('confidence', 0.6),
                is_manipulation_risk=False
            )
            db.add(anomaly)
            stored_anomalies.append(anomaly)

        # Detect MA crossover
        ma_crossover = price_volume_analyzer.detect_ma_crossover(ohlcv)
        if ma_crossover:
            anomaly = PriceVolumeAnomaly(
                symbol=symbol,
                market=market,
                type=AnomalyType.MA_CROSSOVER,
                market_cap_class=price_volume_analyzer.classify_market_cap(market_cap) if market_cap else None,
                price_change_percent=0,
                price_current=ma_crossover.get('current_price'),
                price_ma_20=ma_crossover.get('ma_20'),
                price_ma_50=ma_crossover.get('ma_50'),
                volume_change_percent=0,
                volume_current=ohlcv['Volume'].iloc[-1] if 'Volume' in ohlcv.columns else 0,
                volume_avg_5day=ohlcv['Volume'].tail(5).mean() if 'Volume' in ohlcv.columns else 0,
                volume_relative_strength=1.0,
                technical_confirmation_score=ma_crossover.get('confidence', 0.8),
                is_manipulation_risk=False
            )
            db.add(anomaly)
            stored_anomalies.append(anomaly)

        # Detect RSI extreme
        rsi_extreme = price_volume_analyzer.detect_rsi_extreme(ohlcv)
        if rsi_extreme:
            anomaly = PriceVolumeAnomaly(
                symbol=symbol,
                market=market,
                type=AnomalyType.RSI_EXTREME,
                market_cap_class=price_volume_analyzer.classify_market_cap(market_cap) if market_cap else None,
                price_change_percent=0,
                price_current=ohlcv['Close'].iloc[-1] if 'Close' in ohlcv.columns else 0,
                rsi=rsi_extreme.get('rsi_value'),
                volume_change_percent=0,
                volume_current=ohlcv['Volume'].iloc[-1] if 'Volume' in ohlcv.columns else 0,
                volume_avg_5day=ohlcv['Volume'].tail(5).mean() if 'Volume' in ohlcv.columns else 0,
                volume_relative_strength=1.0,
                technical_confirmation_score=rsi_extreme.get('confidence', 0.7),
                is_manipulation_risk=False
            )
            db.add(anomaly)
            stored_anomalies.append(anomaly)

        # Detect ADX surge
        adx_surge = price_volume_analyzer.detect_adx_surge(ohlcv)
        if adx_surge:
            anomaly = PriceVolumeAnomaly(
                symbol=symbol,
                market=market,
                type=AnomalyType.ADX_SURGE,
                market_cap_class=price_volume_analyzer.classify_market_cap(market_cap) if market_cap else None,
                price_change_percent=0,
                price_current=ohlcv['Close'].iloc[-1] if 'Close' in ohlcv.columns else 0,
                adx=adx_surge.get('adx_value'),
                volume_change_percent=0,
                volume_current=ohlcv['Volume'].iloc[-1] if 'Volume' in ohlcv.columns else 0,
                volume_avg_5day=ohlcv['Volume'].tail(5).mean() if 'Volume' in ohlcv.columns else 0,
                volume_relative_strength=1.0,
                technical_confirmation_score=adx_surge.get('confidence', 0.6),
                is_manipulation_risk=False
            )
            db.add(anomaly)
            stored_anomalies.append(anomaly)

        # Check for manipulation risks if we have market cap
        if market_cap:
            manipulation_risk = price_volume_analyzer.detect_manipulation_risk(ohlcv, market_cap)
            liquidity_score = price_volume_analyzer.calculate_liquidity_quality_score(ohlcv, market_cap)

            for anomaly in stored_anomalies:
                anomaly.is_manipulation_risk = manipulation_risk['is_manipulation_risk']
                anomaly.liquidity_quality_score = liquidity_score

        db.commit()

        return {
            'status': 'analyzed',
            'symbol': symbol,
            'market': market,
            'anomalies_found': len(stored_anomalies),
            'message': f'Analyzed {len(stored_anomalies)} anomalies for {symbol}'
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'symbol': symbol,
            'market': market,
            'error': str(e),
            'anomalies_found': 0
        }

@router.get("/anomalies/price-breakouts")
async def get_price_breakouts(
    db: Session = Depends(get_db),
    market_cap_class: Optional[str] = Query(None, regex="^(LARGE_CAP|MID_CAP|SMALL_CAP)$"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get recent price breakout anomalies, optionally filtered by market cap.

    Path: /api/eddie/anomalies/price-breakouts

    Query Parameters:
    - market_cap_class: Filter by market cap (LARGE_CAP, MID_CAP, SMALL_CAP)
    - limit: Maximum anomalies to return (default 10)

    Response:
    {
        "anomalies": [...],
        "count": 5
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        query = db.query(PriceVolumeAnomaly).filter(
            PriceVolumeAnomaly.type == AnomalyType.PRICE_BREAKOUT,
            PriceVolumeAnomaly.detected_at > recent_time
        )

        if market_cap_class:
            query = query.filter(PriceVolumeAnomaly.market_cap_class == MarketCapClass[market_cap_class])

        anomalies = query.order_by(PriceVolumeAnomaly.detected_at.desc()).limit(limit).all()

        return {
            'anomalies': [
                {
                    'symbol': a.symbol,
                    'type': a.type.value,
                    'price_change': a.price_change_percent,
                    'current_price': a.price_current,
                    'confidence': a.technical_confirmation_score,
                    'market_cap_class': a.market_cap_class.value if a.market_cap_class else None,
                    'is_risk': a.is_manipulation_risk,
                    'detected_at': a.detected_at.isoformat()
                }
                for a in anomalies
            ],
            'count': len(anomalies)
        }
    except Exception as e:
        return {
            'error': f'Error fetching price breakouts: {str(e)}',
            'anomalies': [],
            'count': 0
        }

@router.get("/anomalies/volume-spikes")
async def get_volume_spikes(
    db: Session = Depends(get_db),
    market_cap_class: Optional[str] = Query(None, regex="^(LARGE_CAP|MID_CAP|SMALL_CAP)$"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get recent volume spike anomalies, optionally filtered by market cap.

    Path: /api/eddie/anomalies/volume-spikes

    Query Parameters:
    - market_cap_class: Filter by market cap (LARGE_CAP, MID_CAP, SMALL_CAP)
    - limit: Maximum anomalies to return (default 10)

    Response:
    {
        "anomalies": [...],
        "count": 5
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        query = db.query(PriceVolumeAnomaly).filter(
            PriceVolumeAnomaly.type == AnomalyType.VOLUME_SPIKE,
            PriceVolumeAnomaly.detected_at > recent_time
        )

        if market_cap_class:
            query = query.filter(PriceVolumeAnomaly.market_cap_class == MarketCapClass[market_cap_class])

        anomalies = query.order_by(PriceVolumeAnomaly.detected_at.desc()).limit(limit).all()

        return {
            'anomalies': [
                {
                    'symbol': a.symbol,
                    'type': a.type.value,
                    'volume_change': a.volume_change_percent,
                    'current_volume': a.volume_current,
                    'volume_relative_strength': a.volume_relative_strength,
                    'confidence': a.technical_confirmation_score,
                    'market_cap_class': a.market_cap_class.value if a.market_cap_class else None,
                    'is_risk': a.is_manipulation_risk,
                    'detected_at': a.detected_at.isoformat()
                }
                for a in anomalies
            ],
            'count': len(anomalies)
        }
    except Exception as e:
        return {
            'error': f'Error fetching volume spikes: {str(e)}',
            'anomalies': [],
            'count': 0
        }

@router.get("/anomalies/technical-signals")
async def get_technical_signals(
    db: Session = Depends(get_db),
    min_confirmation_score: float = Query(0.6, ge=0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get recent technical confirmation signals (MA crossovers, RSI extremes, ADX surges).

    Path: /api/eddie/anomalies/technical-signals

    Query Parameters:
    - min_confirmation_score: Minimum technical confirmation score (0-1, default 0.6)
    - limit: Maximum signals to return (default 10)

    Response:
    {
        "signals": [...],
        "count": 5
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        technical_types = [AnomalyType.MA_CROSSOVER, AnomalyType.RSI_EXTREME, AnomalyType.ADX_SURGE]

        anomalies = db.query(PriceVolumeAnomaly).filter(
            PriceVolumeAnomaly.type.in_(technical_types),
            PriceVolumeAnomaly.detected_at > recent_time,
            PriceVolumeAnomaly.technical_confirmation_score >= min_confirmation_score
        ).order_by(PriceVolumeAnomaly.technical_confirmation_score.desc()).limit(limit).all()

        return {
            'signals': [
                {
                    'symbol': a.symbol,
                    'signal_type': a.type.value,
                    'confirmation_score': a.technical_confirmation_score,
                    'rsi': a.rsi,
                    'adx': a.adx,
                    'ma_20': a.price_ma_20,
                    'ma_50': a.price_ma_50,
                    'is_risk': a.is_manipulation_risk,
                    'detected_at': a.detected_at.isoformat()
                }
                for a in anomalies
            ],
            'count': len(anomalies)
        }
    except Exception as e:
        return {
            'error': f'Error fetching technical signals: {str(e)}',
            'signals': [],
            'count': 0
        }

@router.post("/trends/analyze/{symbol}")
async def analyze_stock_for_trends(
    symbol: str,
    db: Session = Depends(get_db),
    force_refresh: bool = Query(False)
):
    """
    Analyze stock for volatility & trend signals and store in database.

    Path: /api/eddie/trends/analyze/{symbol}

    Query Parameters:
    - force_refresh: Force fresh data fetch (default False)

    Response:
    {
        "status": "analyzed|cached",
        "symbol": "AAPL",
        "market": "NYSE|NSE|BSE",
        "trend_type": "strong_uptrend",
        "volatility_status": "expanding"
    }
    """
    # Detect market based on symbol
    detected_market = detector.get_symbol_market(symbol)
    market = detected_market if detected_market else 'NYSE'

    # Check for recent cached data
    if not force_refresh:
        recent = db.query(VolatilityTrendSignal).filter(
            VolatilityTrendSignal.symbol == symbol,
            VolatilityTrendSignal.detected_at > datetime.now(pytz.UTC) - timedelta(hours=1)
        ).first()

        if recent:
            return {
                'status': 'cached',
                'symbol': symbol,
                'market': market,
                'trend_type': recent.trend_type.value,
                'message': 'Using cached trend data from last hour'
            }

    try:
        # Fetch intraday data
        intraday_60m = await price_volume_fetcher.fetch_intraday_60m(symbol)
        if intraday_60m is None or intraday_60m.empty:
            raise HTTPException(status_code=404, detail=f"Could not fetch data for {symbol}")

        # Analyze trends and volatility
        analysis = volatility_trend_analyzer.analyze_stock(intraday_60m)

        if not analysis:
            raise HTTPException(status_code=404, detail=f"Could not analyze {symbol}")

        # Check for BB expansion/contraction
        bb_expanding, bb_exp_pct = volatility_trend_analyzer.detect_bb_expansion_contraction(intraday_60m)
        volatility_status = "expanding" if bb_expanding else "contracting"

        # Create database record
        signal = VolatilityTrendSignal(
            symbol=symbol,
            market=market,
            # Bollinger Bands
            bb_upper=analysis.get('bb_upper'),
            bb_middle=analysis.get('bb_middle'),
            bb_lower=analysis.get('bb_lower'),
            bb_width=analysis.get('bb_width'),
            bb_width_percent=analysis.get('bb_width_percent'),
            price_position=analysis.get('price_position'),
            bb_width_expanding=bb_expanding,
            bb_width_change_percent=bb_exp_pct,
            # Moving Averages
            ma_20=analysis.get('ma_20'),
            ma_50=analysis.get('ma_50'),
            ma_200=analysis.get('ma_200'),
            ma_20_direction=analysis.get('ma_20_direction'),
            ma_50_direction=analysis.get('ma_50_direction'),
            ma_20_slope=analysis.get('ma_20_slope'),
            ma_50_slope=analysis.get('ma_50_slope'),
            ma_alignment=analysis.get('ma_alignment'),
            # Price relative to MAs
            price_above_ma20=analysis.get('price_above_ma20'),
            price_above_ma50=analysis.get('price_above_ma50'),
            price_above_ma200=analysis.get('price_above_ma200'),
            # Volatility metrics
            volatility_atr=analysis.get('atr'),
            volatility_percent=analysis.get('volatility_percent'),
            volatility_trend=analysis.get('volatility_trend'),
            # Trend analysis
            trend_type=analysis.get('trend_type'),
            trend_strength=analysis.get('trend_strength'),
            trend_continuation=analysis.get('trend_continuation'),
            emerging_trend=analysis.get('emerging_trend'),
            is_trend_exhaustion=analysis.get('trend_exhaustion'),
            # Confirmation scores
            trend_confirmation_score=analysis.get('trend_confirmation_score'),
            volatility_confirmation_score=analysis.get('volatility_confirmation_score'),
            # Risk flags
            volatility_extreme=bb_expanding and analysis.get('volatility_trend') == 'increasing'
        )

        db.add(signal)
        db.commit()

        return {
            'status': 'analyzed',
            'symbol': symbol,
            'market': market,
            'trend_type': analysis.get('trend_type').value if analysis.get('trend_type') else None,
            'trend_strength': analysis.get('trend_strength'),
            'volatility_status': volatility_status,
            'message': f'Analyzed trend and volatility for {symbol}'
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'symbol': symbol,
            'market': market,
            'error': str(e)
        }

@router.get("/trends/uptrends")
async def get_uptrend_signals(
    db: Session = Depends(get_db),
    min_strength: float = Query(0.6, ge=0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get stocks in uptrends with minimum strength threshold.

    Path: /api/eddie/trends/uptrends

    Query Parameters:
    - min_strength: Minimum trend strength (0-1, default 0.6)
    - limit: Maximum results to return (default 10)

    Response:
    {
        "uptrends": [...],
        "count": 5
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        uptrend_types = [TrendType.UPTREND, TrendType.STRONG_UPTREND]

        signals = db.query(VolatilityTrendSignal).filter(
            VolatilityTrendSignal.trend_type.in_(uptrend_types),
            VolatilityTrendSignal.trend_strength >= min_strength,
            VolatilityTrendSignal.detected_at > recent_time
        ).order_by(VolatilityTrendSignal.trend_strength.desc()).limit(limit).all()

        return {
            'uptrends': [
                {
                    'symbol': s.symbol,
                    'trend_type': s.trend_type.value,
                    'trend_strength': s.trend_strength,
                    'price_position': s.price_position.value if s.price_position else None,
                    'bb_expanding': s.bb_width_expanding,
                    'ma_alignment': s.ma_alignment.value if s.ma_alignment else None,
                    'confirmation_score': s.trend_confirmation_score,
                    'detected_at': s.detected_at.isoformat()
                }
                for s in signals
            ],
            'count': len(signals)
        }
    except Exception as e:
        return {
            'error': f'Error fetching uptrends: {str(e)}',
            'uptrends': [],
            'count': 0
        }

@router.get("/trends/downtrends")
async def get_downtrend_signals(
    db: Session = Depends(get_db),
    min_strength: float = Query(0.6, ge=0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get stocks in downtrends with minimum strength threshold.

    Path: /api/eddie/trends/downtrends

    Query Parameters:
    - min_strength: Minimum trend strength (0-1, default 0.6)
    - limit: Maximum results to return (default 10)

    Response:
    {
        "downtrends": [...],
        "count": 3
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        downtrend_types = [TrendType.DOWNTREND, TrendType.STRONG_DOWNTREND]

        signals = db.query(VolatilityTrendSignal).filter(
            VolatilityTrendSignal.trend_type.in_(downtrend_types),
            VolatilityTrendSignal.trend_strength >= min_strength,
            VolatilityTrendSignal.detected_at > recent_time
        ).order_by(VolatilityTrendSignal.trend_strength.desc()).limit(limit).all()

        return {
            'downtrends': [
                {
                    'symbol': s.symbol,
                    'trend_type': s.trend_type.value,
                    'trend_strength': s.trend_strength,
                    'price_position': s.price_position.value if s.price_position else None,
                    'bb_expanding': s.bb_width_expanding,
                    'ma_alignment': s.ma_alignment.value if s.ma_alignment else None,
                    'confirmation_score': s.trend_confirmation_score,
                    'detected_at': s.detected_at.isoformat()
                }
                for s in signals
            ],
            'count': len(signals)
        }
    except Exception as e:
        return {
            'error': f'Error fetching downtrends: {str(e)}',
            'downtrends': [],
            'count': 0
        }

@router.get("/trends/volatility-expansion")
async def get_volatility_expansion_signals(
    db: Session = Depends(get_db),
    min_expansion: float = Query(0.1, ge=0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get stocks with expanding volatility (Bollinger Band widening).

    Path: /api/eddie/trends/volatility-expansion

    Query Parameters:
    - min_expansion: Minimum expansion percentage (0-1, default 0.1)
    - limit: Maximum results to return (default 10)

    Response:
    {
        "expanding": [...],
        "count": 4
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        signals = db.query(VolatilityTrendSignal).filter(
            VolatilityTrendSignal.bb_width_expanding == True,
            VolatilityTrendSignal.bb_width_change_percent >= min_expansion,
            VolatilityTrendSignal.detected_at > recent_time
        ).order_by(VolatilityTrendSignal.bb_width_change_percent.desc()).limit(limit).all()

        return {
            'expanding': [
                {
                    'symbol': s.symbol,
                    'bb_width_percent': s.bb_width_percent,
                    'bb_width_change': s.bb_width_change_percent,
                    'volatility_trend': s.volatility_trend,
                    'volatility_atr': s.volatility_atr,
                    'confirmation_score': s.volatility_confirmation_score,
                    'detected_at': s.detected_at.isoformat()
                }
                for s in signals
            ],
            'count': len(signals)
        }
    except Exception as e:
        return {
            'error': f'Error fetching volatility expansion: {str(e)}',
            'expanding': [],
            'count': 0
        }

@router.get("/trends/ma-alignment")
async def get_ma_alignment_signals(
    db: Session = Depends(get_db),
    alignment: str = Query("bullish_aligned", regex="^(bullish_aligned|bearish_aligned|mixed)$"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get stocks with specific moving average alignment patterns.

    Path: /api/eddie/trends/ma-alignment

    Query Parameters:
    - alignment: MA alignment pattern (bullish_aligned, bearish_aligned, mixed)
    - limit: Maximum results to return (default 10)

    Response:
    {
        "aligned": [...],
        "count": 5
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        alignment_enum = MAAlignment[alignment.upper()]

        signals = db.query(VolatilityTrendSignal).filter(
            VolatilityTrendSignal.ma_alignment == alignment_enum,
            VolatilityTrendSignal.detected_at > recent_time
        ).order_by(VolatilityTrendSignal.trend_confirmation_score.desc()).limit(limit).all()

        return {
            'aligned': [
                {
                    'symbol': s.symbol,
                    'ma_alignment': s.ma_alignment.value,
                    'ma_20': s.ma_20,
                    'ma_50': s.ma_50,
                    'ma_200': s.ma_200,
                    'trend_type': s.trend_type.value,
                    'confirmation_score': s.trend_confirmation_score,
                    'detected_at': s.detected_at.isoformat()
                }
                for s in signals
            ],
            'count': len(signals)
        }
    except Exception as e:
        return {
            'error': f'Error fetching MA alignment signals: {str(e)}',
            'aligned': [],
            'count': 0
        }

@router.post("/candles/analyze/{symbol}")
async def analyze_candles(
    symbol: str,
    db: Session = Depends(get_db),
    force_refresh: bool = Query(False)
):
    """
    Analyze stock candlesticks and store in database.

    Path: /api/eddie/candles/analyze/{symbol}

    Query Parameters:
    - force_refresh: Force fresh data fetch (default False)

    Response:
    {
        "status": "analyzed|cached",
        "symbol": "AAPL",
        "market": "NYSE|NSE|BSE",
        "candle_color": "bullish",
        "patterns_found": ["engulfing"],
        "quality_score": 0.85
    }
    """
    # Detect market based on symbol
    detected_market = detector.get_symbol_market(symbol)
    market = detected_market if detected_market else 'NYSE'

    # Check for recent cached data
    if not force_refresh:
        recent = db.query(CandlestickSignal).filter(
            CandlestickSignal.symbol == symbol,
            CandlestickSignal.detected_at > datetime.now(pytz.UTC) - timedelta(hours=1)
        ).first()

        if recent:
            return {
                'status': 'cached',
                'symbol': symbol,
                'market': market,
                'candle_color': recent.candle_color.value,
                'message': 'Using cached candle data from last hour'
            }

    try:
        # Fetch intraday data
        intraday_60m = await price_volume_fetcher.fetch_intraday_60m(symbol)
        if intraday_60m is None or intraday_60m.empty:
            raise HTTPException(status_code=404, detail=f"Could not fetch data for {symbol}")

        # Fetch trend data for context
        trend_signal = db.query(VolatilityTrendSignal).filter(
            VolatilityTrendSignal.symbol == symbol,
            VolatilityTrendSignal.detected_at > datetime.now(pytz.UTC) - timedelta(hours=1)
        ).order_by(VolatilityTrendSignal.detected_at.desc()).first()

        ma20 = trend_signal.ma_20 if trend_signal else None
        ma50 = trend_signal.ma_50 if trend_signal else None
        bb_upper = trend_signal.bb_upper if trend_signal else None
        bb_lower = trend_signal.bb_lower if trend_signal else None

        # Analyze candles
        analysis = candlestick_analyzer.analyze_candle(
            intraday_60m,
            ma20=ma20,
            ma50=ma50,
            bb_upper=bb_upper,
            bb_lower=bb_lower
        )

        if not analysis:
            raise HTTPException(status_code=404, detail=f"Could not analyze {symbol}")

        # Extract primary pattern if any
        primary_pattern = None
        if analysis.get('primary_pattern'):
            primary_pattern = analysis['primary_pattern'].get('pattern')

        # Create database record
        signal = CandlestickSignal(
            symbol=symbol,
            market=market,
            # Candle properties
            candle_color=analysis.get('color'),
            candle_open=analysis.get('open'),
            candle_high=analysis.get('high'),
            candle_low=analysis.get('low'),
            candle_close=analysis.get('close'),
            candle_range=analysis.get('range'),
            candle_body=analysis.get('body'),
            candle_upper_wick=analysis.get('upper_wick'),
            candle_lower_wick=analysis.get('lower_wick'),
            candle_volume=analysis.get('volume'),
            # Candle strength
            body_strength=analysis.get('body_strength'),
            candle_size=analysis.get('candle_size'),
            candle_quality_score=analysis.get('quality_score'),
            # Position
            position=analysis.get('position'),
            distance_from_ma20=analysis.get('from_ma20'),
            distance_from_ma50=analysis.get('from_ma50'),
            # Pattern
            pattern_type=primary_pattern,
            pattern_strength=analysis['primary_pattern'].get('confidence', 0.5) if analysis.get('primary_pattern') else 0,
            # Volume
            volume_confirmation=analysis.get('volume_confirmed'),
            volume_vs_avg=1.0,
            volume_trend=analysis.get('volume_trend'),
            # Risk
            candle_rejection=analysis.get('is_rejection'),
            is_inside_bar=analysis.get('is_inside_bar'),
            is_pin_bar=analysis.get('is_pin_bar'),
            # Scores
            pattern_confirmation_score=analysis['primary_pattern'].get('confidence', 0.5) if analysis.get('primary_pattern') else 0.5,
            volume_confirmation_score=analysis.get('volume_confidence', 0.5),
            overall_signal_strength=analysis.get('quality_score', 0.5)
        )

        db.add(signal)
        db.commit()

        return {
            'status': 'analyzed',
            'symbol': symbol,
            'market': market,
            'candle_color': analysis.get('color').value if analysis.get('color') else None,
            'patterns_found': [p.get('pattern').value if hasattr(p.get('pattern'), 'value') else p.get('pattern') for p in analysis.get('patterns_found', [])],
            'quality_score': analysis.get('quality_score'),
            'message': f'Analyzed candles for {symbol}'
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'symbol': symbol,
            'market': market,
            'error': str(e)
        }

@router.get("/candles/bullish-patterns")
async def get_bullish_candle_patterns(
    db: Session = Depends(get_db),
    min_quality: float = Query(0.6, ge=0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get bullish candlestick patterns and signals.

    Path: /api/eddie/candles/bullish-patterns

    Query Parameters:
    - min_quality: Minimum quality score (0-1, default 0.6)
    - limit: Maximum results (default 10)

    Response:
    {
        "bullish": [...],
        "count": 5
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        signals = db.query(CandlestickSignal).filter(
            CandlestickSignal.candle_color == CandleColor.BULLISH,
            CandlestickSignal.candle_quality_score >= min_quality,
            CandlestickSignal.detected_at > recent_time
        ).order_by(CandlestickSignal.candle_quality_score.desc()).limit(limit).all()

        return {
            'bullish': [
                {
                    'symbol': s.symbol,
                    'candle_color': s.candle_color.value,
                    'pattern': s.pattern_type.value if s.pattern_type else None,
                    'quality_score': s.candle_quality_score,
                    'pattern_strength': s.pattern_strength,
                    'volume_confirmed': s.volume_confirmation,
                    'position': s.position.value if s.position else None,
                    'detected_at': s.detected_at.isoformat()
                }
                for s in signals
            ],
            'count': len(signals)
        }
    except Exception as e:
        return {
            'error': f'Error fetching bullish patterns: {str(e)}',
            'bullish': [],
            'count': 0
        }

@router.get("/candles/bearish-patterns")
async def get_bearish_candle_patterns(
    db: Session = Depends(get_db),
    min_quality: float = Query(0.6, ge=0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get bearish candlestick patterns and signals.

    Path: /api/eddie/candles/bearish-patterns

    Query Parameters:
    - min_quality: Minimum quality score (0-1, default 0.6)
    - limit: Maximum results (default 10)

    Response:
    {
        "bearish": [...],
        "count": 3
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        signals = db.query(CandlestickSignal).filter(
            CandlestickSignal.candle_color == CandleColor.BEARISH,
            CandlestickSignal.candle_quality_score >= min_quality,
            CandlestickSignal.detected_at > recent_time
        ).order_by(CandlestickSignal.candle_quality_score.desc()).limit(limit).all()

        return {
            'bearish': [
                {
                    'symbol': s.symbol,
                    'candle_color': s.candle_color.value,
                    'pattern': s.pattern_type.value if s.pattern_type else None,
                    'quality_score': s.candle_quality_score,
                    'pattern_strength': s.pattern_strength,
                    'volume_confirmed': s.volume_confirmation,
                    'position': s.position.value if s.position else None,
                    'detected_at': s.detected_at.isoformat()
                }
                for s in signals
            ],
            'count': len(signals)
        }
    except Exception as e:
        return {
            'error': f'Error fetching bearish patterns: {str(e)}',
            'bearish': [],
            'count': 0
        }

@router.get("/candles/reversal-patterns")
async def get_reversal_candle_patterns(
    db: Session = Depends(get_db),
    min_strength: float = Query(0.75, ge=0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get reversal candlestick patterns (hammer, engulfing, morning/evening star).

    Path: /api/eddie/candles/reversal-patterns

    Query Parameters:
    - min_strength: Minimum pattern strength (0-1, default 0.75)
    - limit: Maximum results (default 10)

    Response:
    {
        "reversals": [...],
        "count": 4
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=24)

        reversal_patterns = [
            CandlePattern.HAMMER,
            CandlePattern.ENGULFING,
            CandlePattern.MORNING_STAR,
            CandlePattern.EVENING_STAR,
            CandlePattern.HARAMI
        ]

        signals = db.query(CandlestickSignal).filter(
            CandlestickSignal.pattern_type.in_(reversal_patterns),
            CandlestickSignal.pattern_strength >= min_strength,
            CandlestickSignal.detected_at > recent_time
        ).order_by(CandlestickSignal.pattern_strength.desc()).limit(limit).all()

        return {
            'reversals': [
                {
                    'symbol': s.symbol,
                    'pattern_type': s.pattern_type.value,
                    'pattern_strength': s.pattern_strength,
                    'candle_color': s.candle_color.value,
                    'quality_score': s.candle_quality_score,
                    'volume_confirmed': s.volume_confirmation,
                    'detected_at': s.detected_at.isoformat()
                }
                for s in signals
            ],
            'count': len(signals)
        }
    except Exception as e:
        return {
            'error': f'Error fetching reversal patterns: {str(e)}',
            'reversals': [],
            'count': 0
        }

@router.post("/confluence/analyze/{symbol}")
async def analyze_confluence(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Final confluence analysis combining all 5 filters.

    Path: /api/eddie/confluence/analyze/{symbol}

    Response:
    {
        "symbol": "AAPL",
        "market": "NYSE|NSE|BSE",
        "rating": "buy",
        "confidence": 0.82,
        "direction": "long",
        "bullish_filters": 3,
        "overall_message": "3 filters agree bullish with high confidence"
    }
    """
    # Detect market based on symbol
    detected_market = detector.get_symbol_market(symbol)
    market = detected_market if detected_market else 'NYSE'

    try:
        analysis = confluence_analyzer.analyze_confluence(symbol, db)

        if not analysis:
            return {
                'error': f'Could not analyze confluence for {symbol}',
                'symbol': symbol,
                'market': market
            }

        # Create or update final signal record
        existing = db.query(EddieFinalSignal).filter(
            EddieFinalSignal.symbol == symbol,
            EddieFinalSignal.detected_at > datetime.now(pytz.UTC) - timedelta(hours=1)
        ).order_by(EddieFinalSignal.detected_at.desc()).first()

        if existing:
            # Update existing record
            existing.direction = analysis['direction']
            existing.rating = analysis['rating']
            existing.bullish_filters_count = analysis['bullish_count']
            existing.bearish_filters_count = analysis['bearish_count']
            existing.neutral_filters_count = analysis['neutral_count']
            existing.total_agreement = analysis['agreement_score']
            existing.filter_consensus_score = analysis['filter_consensus_score']
            existing.signal_strength_score = analysis['signal_strength_score']
            existing.noise_reduction_factor = analysis['noise_reduction_factor']
            existing.overall_confidence = analysis['overall_confidence']
            existing.is_high_probability = analysis['is_high_probability']
            existing.is_low_noise = analysis['is_low_noise']
            existing.requires_confirmation = analysis['requires_confirmation']
            existing.key_signals = analysis['key_signals']
            existing.risk_score = analysis['risk_score']
            db.commit()
        else:
            # Create new record
            signal = EddieFinalSignal(
                symbol=symbol,
                market=market,
                direction=analysis['direction'],
                rating=analysis['rating'],
                bullish_filters_count=analysis['bullish_count'],
                bearish_filters_count=analysis['bearish_count'],
                neutral_filters_count=analysis['neutral_count'],
                total_agreement=analysis['agreement_score'],
                filter_consensus_score=analysis['filter_consensus_score'],
                signal_strength_score=analysis['signal_strength_score'],
                noise_reduction_factor=analysis['noise_reduction_factor'],
                overall_confidence=analysis['overall_confidence'],
                is_high_probability=analysis['is_high_probability'],
                is_low_noise=analysis['is_low_noise'],
                requires_confirmation=analysis['requires_confirmation'],
                key_signals=analysis['key_signals'],
                risk_score=analysis['risk_score']
            )
            db.add(signal)
            db.commit()

        return {
            'symbol': symbol,
            'market': market,
            'rating': analysis['rating'].value,
            'direction': analysis['direction'].value,
            'confidence': analysis['overall_confidence'],
            'bullish_filters': analysis['bullish_count'],
            'bearish_filters': analysis['bearish_count'],
            'is_high_probability': analysis['is_high_probability'],
            'is_low_noise': analysis['is_low_noise'],
            'requires_confirmation': analysis['requires_confirmation'],
            'key_signals': analysis['key_signals']
        }

    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'symbol': symbol,
            'market': market,
            'error': str(e)
        }

@router.get("/opportunities/top-ranked")
async def get_top_ranked_opportunities(
    db: Session = Depends(get_db),
    rating: Optional[str] = Query("buy", regex="^(strong_buy|buy|neutral|sell|strong_sell)$"),
    limit: int = Query(20, ge=1, le=50)
):
    """
    Get top-ranked trade opportunities based on confluence analysis.

    Path: /api/eddie/opportunities/top-ranked

    Query Parameters:
    - rating: Filter by opportunity rating (buy, strong_buy, neutral, sell, strong_sell)
    - limit: Maximum results (default 20)

    Response:
    {
        "opportunities": [...],
        "count": 5
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=4)

        rating_enum = OpportunityRating[rating.upper()]

        opportunities = db.query(EddieFinalSignal).filter(
            EddieFinalSignal.rating == rating_enum,
            EddieFinalSignal.detected_at > recent_time
        ).order_by(EddieFinalSignal.overall_confidence.desc()).limit(limit).all()

        return {
            'opportunities': [
                {
                    'symbol': o.symbol,
                    'rating': o.rating.value,
                    'direction': o.direction.value,
                    'confidence': o.overall_confidence,
                    'bullish_filters': o.bullish_filters_count,
                    'bearish_filters': o.bearish_filters_count,
                    'is_high_probability': o.is_high_probability,
                    'key_signals': o.key_signals,
                    'detected_at': o.detected_at.isoformat()
                }
                for o in opportunities
            ],
            'count': len(opportunities)
        }
    except Exception as e:
        return {
            'error': f'Error fetching opportunities: {str(e)}',
            'opportunities': [],
            'count': 0
        }

@router.get("/opportunities/high-probability")
async def get_high_probability_signals(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get high-probability trading signals (confidence > 0.75, clean signals).

    Path: /api/eddie/opportunities/high-probability

    Query Parameters:
    - limit: Maximum results (default 10)

    Response:
    {
        "signals": [...],
        "count": 3
    }
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=4)

        signals = db.query(EddieFinalSignal).filter(
            EddieFinalSignal.is_high_probability == True,
            EddieFinalSignal.is_low_noise == True,
            EddieFinalSignal.detected_at > recent_time
        ).order_by(EddieFinalSignal.overall_confidence.desc()).limit(limit).all()

        return {
            'signals': [
                {
                    'symbol': s.symbol,
                    'rating': s.rating.value,
                    'direction': s.direction.value,
                    'confidence': s.overall_confidence,
                    'consensus_score': s.filter_consensus_score,
                    'bullish_filters': s.bullish_filters_count,
                    'key_signals': s.key_signals,
                    'detected_at': s.detected_at.isoformat()
                }
                for s in signals
            ],
            'count': len(signals)
        }
    except Exception as e:
        return {
            'error': f'Error fetching high probability signals: {str(e)}',
            'signals': [],
            'count': 0
        }

@router.get("/opportunities/watch-list")
async def get_watch_list(
    db: Session = Depends(get_db),
    timezone: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get comprehensive watch list of active signals segregated by market and market cap.

    Path: /api/eddie/opportunities/watch-list

    Query Parameters:
    - timezone: User timezone for market detection (e.g., 'Asia/Kolkata', 'US/Eastern')
    - limit: Maximum results per market cap bucket (default 20)

    Response:
    {
        "active_market": "INDIA|US",
        "market_open": true/false,
        "large_cap_signals": [...],
        "mid_cap_signals": [...],
        "small_cap_signals": [...],
        "summary": {...}
    }
    """
    try:
        # Detect active market
        if timezone:
            try:
                tz = pytz.timezone(timezone)
                current_time = datetime.now(tz)
            except:
                current_time = datetime.now(pytz.UTC)
        else:
            current_time = datetime.now(pytz.UTC)

        active_market_info = detector.get_active_market(current_time)

        # Determine which market to show
        if active_market_info and active_market_info['region'] == 'INDIA':
            active_market = "INDIA"
            market_open = True
        else:
            active_market = "US"
            market_open = active_market_info is not None if active_market_info else False

        recent_time = datetime.now(pytz.UTC) - timedelta(hours=4)

        # Get signals ONLY from the active market
        all_signals = db.query(EddieFinalSignal).filter(
            EddieFinalSignal.active_market == active_market,
            EddieFinalSignal.detected_at > recent_time
        ).order_by(EddieFinalSignal.overall_confidence.desc()).limit(limit * 3).all()

        # Categorize by market cap (extract from key_signals)
        large_cap = []
        mid_cap = []
        small_cap = []

        # Track seen symbols to prevent duplicates
        seen_symbols = set()

        for s in all_signals:
            # Skip if we've already added this symbol (keep highest confidence version)
            if s.symbol in seen_symbols:
                continue
            seen_symbols.add(s.symbol)

            signal_dict = {
                'symbol': s.symbol,
                'rating': s.rating.value,
                'direction': s.direction.value,
                'confidence': s.overall_confidence,
                'bullish_filters': s.bullish_filters_count,
                'key_signals': s.key_signals,
                'status': 'HIGH_PRIORITY' if s.is_high_probability else 'WATCH',
                'market': s.active_market,
                'detected_at': s.detected_at.isoformat() if s.detected_at else None
            }

            # Classify by market cap from market_cap_class field
            if s.market_cap_class and s.market_cap_class.value == 'large_cap':
                large_cap.append(signal_dict)
            elif s.market_cap_class and s.market_cap_class.value == 'mid_cap':
                mid_cap.append(signal_dict)
            else:
                small_cap.append(signal_dict)

        # Calculate summary stats
        strong_buys = sum(1 for s in all_signals if s.rating == OpportunityRating.STRONG_BUY)
        buys = sum(1 for s in all_signals if s.rating == OpportunityRating.BUY)
        sells = sum(1 for s in all_signals if s.rating == OpportunityRating.SELL)
        strong_sells = sum(1 for s in all_signals if s.rating == OpportunityRating.STRONG_SELL)

        return {
            'active_market': active_market,
            'market_open': market_open,
            'large_cap_signals': large_cap[:limit],
            'mid_cap_signals': mid_cap[:limit],
            'small_cap_signals': small_cap[:limit],
            'total_signals': len(all_signals),
            'summary': {
                'active_market': active_market,
                'market_open': market_open,
                'strong_buy_count': strong_buys,
                'buy_count': buys,
                'neutral_count': len(all_signals) - strong_buys - buys - sells - strong_sells,
                'sell_count': sells,
                'strong_sell_count': strong_sells,
                'high_probability_count': sum(1 for s in all_signals if s.is_high_probability),
                'avg_confidence': sum(s.overall_confidence for s in all_signals) / len(all_signals) if all_signals else 0,
                'large_cap_count': len(large_cap),
                'mid_cap_count': len(mid_cap),
                'small_cap_count': len(small_cap)
            }
        }
    except Exception as e:
        return {
            'error': f'Error fetching watch list: {str(e)}',
            'large_cap_signals': [],
            'mid_cap_signals': [],
            'small_cap_signals': [],
            'total_signals': 0
        }

@router.get("/opportunities/watch-list-legacy")
async def get_watch_list_legacy(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Legacy watch list endpoint (returns all signals without market filtering).
    Use /opportunities/watch-list instead for market-aware results.
    """
    try:
        recent_time = datetime.now(pytz.UTC) - timedelta(hours=4)

        all_signals = db.query(EddieFinalSignal).filter(
            EddieFinalSignal.detected_at > recent_time
        ).order_by(EddieFinalSignal.overall_confidence.desc()).limit(limit).all()

        # Calculate summary stats
        strong_buys = sum(1 for s in all_signals if s.rating == OpportunityRating.STRONG_BUY)
        buys = sum(1 for s in all_signals if s.rating == OpportunityRating.BUY)
        sells = sum(1 for s in all_signals if s.rating == OpportunityRating.SELL)
        strong_sells = sum(1 for s in all_signals if s.rating == OpportunityRating.STRONG_SELL)

        return {
            'watchlist': [
                {
                    'symbol': s.symbol,
                    'rating': s.rating.value,
                    'direction': s.direction.value,
                    'confidence': s.overall_confidence,
                    'bullish_filters': s.bullish_filters_count,
                    'key_signals': s.key_signals,
                    'status': 'HIGH_PRIORITY' if s.is_high_probability else 'WATCH'
                }
                for s in all_signals
            ],
            'count': len(all_signals),
            'summary': {
                'strong_buy_count': strong_buys,
                'buy_count': buys,
                'neutral_count': len(all_signals) - strong_buys - buys - sells - strong_sells,
                'sell_count': sells,
                'strong_sell_count': strong_sells,
                'high_probability_count': sum(1 for s in all_signals if s.is_high_probability),
                'avg_confidence': sum(s.overall_confidence for s in all_signals) / len(all_signals) if all_signals else 0
            }
        }
    except Exception as e:
        return {
            'error': f'Error fetching watch list: {str(e)}',
            'watchlist': [],
            'count': 0
        }


@router.post("/scan/yahoo-finance")
async def scan_yahoo_finance(db: Session = Depends(get_db), timezone: Optional[str] = Query(None), limit: int = Query(10, ge=1, le=50)):
    """Scan Yahoo Finance and create signals based on active market"""
    import yfinance as yf
    from datetime import datetime as dt
    import pytz
    from src.services.deepseek_analyzer import deepseek_analyzer

    # Detect which market is active
    if timezone:
        try:
            tz = pytz.timezone(timezone)
            current_time = dt.now(tz)
        except:
            current_time = dt.now(pytz.UTC)
    else:
        current_time = dt.now(pytz.UTC)

    active_market_info = detector.get_active_market(current_time)

    # Default stock symbols (market cap will be determined by DeepSeek)
    # Indian stocks
    indian_stocks = [
        'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS',
        'WIPRO.NS', 'BAJAJ-AUTO.NS', 'MARUTI.NS', 'LT.NS'
    ]

    # US stocks
    us_stocks = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'
    ]

    # Define stocks based on active market
    if active_market_info and active_market_info['region'] == 'INDIA':
        symbols = indian_stocks
        active_market = "INDIA"
        market = "NSE"
    else:
        symbols = us_stocks
        active_market = "US"
        market = "NYSE"

    results = []

    # Delete old duplicate signals from this market (keep last 1 hour only)
    cutoff = current_time - timedelta(hours=1)
    old_signals = db.query(EddieFinalSignal).filter(
        EddieFinalSignal.active_market == active_market,
        EddieFinalSignal.detected_at < cutoff
    ).delete()
    db.commit()
    print(f"[SCAN] Deleted {old_signals} old signals from {active_market}")

    for sym in symbols[:limit]:
        try:
            h = yf.Ticker(sym).history(period="5d")
            if h.empty or len(h) < 2:
                continue

            cp = float(h['Close'].iloc[-1])
            pc = float(h['Close'].iloc[-2])
            ap = float(h['Close'].mean())
            av = float(h['Volume'].mean())
            cv = float(h['Volume'].iloc[-1])

            b = sum([cp > ap, cp > pc, cv > av])

            rating = [OpportunityRating.SELL, OpportunityRating.NEUTRAL, OpportunityRating.BUY, OpportunityRating.STRONG_BUY][b]
            direction = TradeDirection.LONG if b >= 2 else TradeDirection.NEUTRAL
            conf = 0.5 + (b * 0.12)

            # Get market cap categorization from DeepSeek (for all signals)
            categorization = await deepseek_analyzer.categorize_stock(sym, cp)
            market_cap_class_str = categorization['market_cap_class'] if categorization else 'MID_CAP'

            # Generate AI report only for qualified signals (BUY or STRONG_BUY)
            if rating in [OpportunityRating.BUY, OpportunityRating.STRONG_BUY]:
                ai_report = categorization.get('description', f'{rating.value} signal detected') if categorization else f'{rating.value} signal detected'
            else:
                ai_report = f"{rating.value} signal detected"

            # Convert string to enum
            market_cap_enum = MarketCapClass[market_cap_class_str]

            signal = EddieFinalSignal(
                symbol=sym, market=market, active_market=active_market,
                bullish_filters_count=b, bearish_filters_count=3-b, neutral_filters_count=0,
                total_agreement=b/3.0,
                catalyst_signal="neutral", catalyst_strength=0.5,
                anomaly_signal="neutral", anomaly_strength=0.5,
                trend_signal="neutral", trend_strength=0.5,
                candle_signal="neutral", candle_strength=0.5,
                direction=direction, rating=rating,
                filter_consensus_score=b/3.0, signal_strength_score=conf,
                risk_score=1.0-conf, noise_reduction_factor=0.8,
                overall_confidence=conf,
                is_high_probability=conf>0.75, is_low_noise=conf>0.70, requires_confirmation=conf<0.70,
                key_signals=ai_report,
                detected_at=dt.now(pytz.UTC),
                market_cap_class=market_cap_enum
            )
            db.add(signal)
            results.append({'symbol': sym, 'market_cap': market_cap_class_str, 'rating': rating.value})
            print(f"[SCAN] Created signal for {sym}: {rating.value} in {active_market} ({market_cap_class_str})")
        except Exception as e:
            print(f"[SCAN] Error {sym}: {str(e)}")

    db.commit()
    print(f"[SCAN] Saved {len(results)} signals from {active_market}")
    return {
        "status": "success",
        "scanned": len(results),
        "symbols": [r['symbol'] for r in results],
        "signals_with_caps": results,
        "active_market": active_market,
        "market_open": active_market_info is not None if active_market_info else (active_market == "US"),
        "message": f"Scanned {active_market} market ({len(results)} stocks)"
    }
