from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import WatchlistEntry, TradeHorizon
from src.services.yahoo_finance_dashboard import YahooFinanceDashboard
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])
dashboard = YahooFinanceDashboard()

def entry_to_dict(entry: WatchlistEntry):
    """Convert watchlist entry to dict with formatted data"""
    market = 'IN' if entry.symbol.endswith(('.NS', '.BO')) else 'US'
    return {
        'id': entry.id,
        'symbol': entry.symbol,
        'market': market,
        'horizon': entry.horizon.value if entry.horizon else None,
        'direction': entry.direction,
        'current_price': entry.current_price,
        'rsi': entry.rsi,
        'adx': entry.adx,
        'momentum': entry.momentum,
        'volume_ratio': entry.volume_ratio,
        'breakout_timestamp': entry.breakout_timestamp.isoformat() if entry.breakout_timestamp else None,
        'added_at': entry.added_at.isoformat() if entry.added_at else None
    }

@router.get("")
async def get_watchlist(
    db: Session = Depends(get_db),
    horizon: Optional[str] = Query(None),
    market: Optional[str] = Query(None),
    min_adx: Optional[float] = Query(None),
    min_rsi: Optional[float] = Query(None),
    max_rsi: Optional[float] = Query(None)
):
    """Get current watchlist entries with optional filters"""
    query = db.query(WatchlistEntry).filter(WatchlistEntry.removed_at == None)

    if horizon:
        try:
            horizon_enum = TradeHorizon(horizon)
            query = query.filter(WatchlistEntry.horizon == horizon_enum)
        except ValueError:
            pass

    if min_adx is not None:
        query = query.filter(WatchlistEntry.adx >= min_adx)

    if min_rsi is not None:
        query = query.filter(WatchlistEntry.rsi >= min_rsi)

    if max_rsi is not None:
        query = query.filter(WatchlistEntry.rsi <= max_rsi)

    entries = query.all()

    return {
        'long_candidates': [entry_to_dict(e) for e in entries if e.direction == 'long'],
        'short_candidates': [entry_to_dict(e) for e in entries if e.direction == 'short'],
        'count': len(entries)
    }

@router.get("/dashboard/overview")
async def get_watchlist_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive dashboards for all watchlist entries"""
    entries = db.query(WatchlistEntry).filter(WatchlistEntry.removed_at == None).all()
    symbols = list(set([e.symbol for e in entries]))

    dashboard_data = await dashboard.get_watchlist_dashboard(symbols)
    return dashboard_data

@router.get("/dashboard/company/{symbol}")
async def get_company_dashboard(symbol: str):
    """Get company profile and overview"""
    profile = await dashboard.get_company_profile(symbol)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Company data not found for {symbol}")
    return profile

@router.get("/dashboard/quote/{symbol}")
async def get_quote_dashboard(symbol: str):
    """Get real-time quote data"""
    quote = await dashboard.get_real_time_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote data not found for {symbol}")
    return quote

@router.get("/dashboard/news/{symbol}")
async def get_news_dashboard(symbol: str, limit: int = Query(5, ge=1, le=20)):
    """Get latest company news with sentiment"""
    news = await dashboard.get_company_news(symbol, limit=limit)
    return {'symbol': symbol, 'news': news}

@router.get("/dashboard/statistics/{symbol}")
async def get_statistics_dashboard(symbol: str):
    """Get key financial statistics"""
    stats = await dashboard.get_key_statistics(symbol)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Statistics not found for {symbol}")
    return stats

@router.get("/news/indian")
async def get_indian_news(limit: int = Query(10, ge=1, le=50)):
    """Get Indian market news"""
    news = await dashboard.get_indian_news(limit=limit)
    return {'region': 'India', 'news': news, 'count': len(news)}

@router.get("/news/global")
async def get_global_news(limit: int = Query(10, ge=1, le=50)):
    """Get global market news"""
    news = await dashboard.get_global_news(limit=limit)
    return {'region': 'Global', 'news': news, 'count': len(news)}

@router.post("/{symbol}")
async def add_to_watchlist(symbol: str, horizon: str, db: Session = Depends(get_db)):
    """Add stock to watchlist"""
    try:
        horizon_enum = TradeHorizon(horizon)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid horizon: {horizon}")

    entry = WatchlistEntry(
        symbol=symbol,
        horizon=horizon_enum,
        direction='long'
    )
    db.add(entry)
    db.commit()
    return {'status': 'added', 'symbol': symbol}

@router.delete("/{entry_id}")
async def remove_from_watchlist(entry_id: int, db: Session = Depends(get_db)):
    """Remove from watchlist"""
    entry = db.query(WatchlistEntry).get(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {'status': 'removed'}


@router.get("/eddie/stocks")
async def get_eddie_watchlist(
    db: Session = Depends(get_db),
    market: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    min_adx: Optional[float] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    """Get Eddie's Multi-Market Watchlist (S&P 500, Nifty 500, etc.)"""
    query = db.query(WatchlistEntry).filter(
        WatchlistEntry.horizon == TradeHorizon.LONG_TERM,
        WatchlistEntry.removed_at == None
    ).order_by(WatchlistEntry.added_at.desc())

    if market:
        market = market.upper()
        if market == 'US':
            query = query.filter(~WatchlistEntry.symbol.ilike('%[.]NS%'),
                               ~WatchlistEntry.symbol.ilike('%[.]BO%'))
        elif market == 'INDIA':
            query = query.filter((WatchlistEntry.symbol.ilike('%[.]NS%')) |
                               (WatchlistEntry.symbol.ilike('%[.]BO%')))

    if direction:
        query = query.filter(WatchlistEntry.direction == direction.upper())

    if min_adx is not None:
        query = query.filter(WatchlistEntry.adx >= min_adx)

    entries = query.limit(limit).all()

    return {
        'count': len(entries),
        'stocks': [entry_to_dict(e) for e in entries]
    }


@router.post("/eddie/refresh")
async def refresh_eddie_watchlist(db: Session = Depends(get_db)):
    """Manually trigger Eddie's Watchlist scan"""
    from src.services.stock_screener import StockScreener

    screener = StockScreener()
    try:
        # Run the screening directly (async)
        results = await screener.screen_all_markets()

        added = 0
        for result in results:
            existing = db.query(WatchlistEntry).filter(
                WatchlistEntry.symbol == result['symbol'],
                WatchlistEntry.horizon == TradeHorizon.LONG_TERM,
                WatchlistEntry.removed_at == None
            ).first()

            if not existing:
                entry = WatchlistEntry(
                    symbol=result['symbol'],
                    horizon=TradeHorizon.LONG_TERM,
                    direction=result['direction'],
                    rsi=result.get('rsi'),
                    adx=result.get('adx'),
                    momentum=result.get('momentum'),
                    current_price=result['current_price'],
                    volume_ratio=result.get('volume_ratio', 1.0),
                    breakout_timestamp=datetime.utcnow()
                )
                db.add(entry)
                added += 1

        db.commit()
        return {'status': 'success', 'added': added}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
