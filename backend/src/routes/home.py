from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Holding, WatchlistEntry, CustomWatchlist, TradeHorizon
from datetime import datetime

router = APIRouter(prefix="/api/home", tags=["home"])

@router.get("")
async def get_home_data(db: Session = Depends(get_db)):
    """Get Home dashboard data: current holdings, long-term watchlist, custom watchlist"""

    # Current holdings (from Zerodha)
    holdings = db.query(Holding).all()
    holdings_data = [
        {
            'id': h.id,
            'symbol': h.symbol,
            'quantity': h.quantity,
            'average_price': h.average_price,
            'current_price': h.current_price,
            'market_value': h.market_value,
            'unrealised_pnl': h.unrealised_pnl,
            'unrealised_pnl_percent': h.unrealised_pnl_percent,
        }
        for h in holdings
    ]

    # Long-term watchlist (Eddie's slow-cadence picks)
    long_term_picks = db.query(WatchlistEntry).filter(
        WatchlistEntry.horizon == TradeHorizon.LONG_TERM,
        WatchlistEntry.removed_at == None
    ).all()
    long_term_data = [
        {
            'id': e.id,
            'symbol': e.symbol,
            'direction': e.direction,
            'current_price': e.current_price,
            'rsi': e.rsi,
            'adx': e.adx,
            'momentum': e.momentum,
            'added_at': e.added_at.isoformat() if e.added_at else None,
        }
        for e in long_term_picks
    ]

    # Custom watchlist (user's personal tickers)
    custom_picks = db.query(CustomWatchlist).all()
    custom_data = [
        {
            'id': c.id,
            'symbol': c.symbol,
            'notes': c.notes,
            'added_at': c.added_at.isoformat() if c.added_at else None,
        }
        for c in custom_picks
    ]

    # Portfolio summary
    total_portfolio_value = sum(h.market_value for h in holdings) if holdings else 0
    total_portfolio_pnl = sum(h.unrealised_pnl for h in holdings) if holdings else 0
    portfolio_pnl_percent = (total_portfolio_pnl / total_portfolio_value * 100) if total_portfolio_value > 0 else 0

    return {
        'portfolio': {
            'holdings': holdings_data,
            'total_value': total_portfolio_value,
            'total_pnl': total_portfolio_pnl,
            'total_pnl_percent': portfolio_pnl_percent,
            'holdings_count': len(holdings_data),
        },
        'long_term_watchlist': {
            'picks': long_term_data,
            'count': len(long_term_data),
        },
        'custom_watchlist': {
            'tickers': custom_data,
            'count': len(custom_data),
        }
    }

@router.post("/custom-watchlist/{symbol}")
async def add_custom_watchlist(symbol: str, notes: str = None, db: Session = Depends(get_db)):
    """Add a ticker to custom watchlist"""
    existing = db.query(CustomWatchlist).filter(CustomWatchlist.symbol == symbol).first()
    if existing:
        return {'status': 'already_exists', 'symbol': symbol}

    custom = CustomWatchlist(symbol=symbol, notes=notes)
    db.add(custom)
    db.commit()
    return {'status': 'added', 'symbol': symbol, 'id': custom.id}

@router.delete("/custom-watchlist/{watchlist_id}")
async def remove_custom_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    """Remove a ticker from custom watchlist"""
    custom = db.query(CustomWatchlist).get(watchlist_id)
    if not custom:
        return {'status': 'not_found'}
    db.delete(custom)
    db.commit()
    return {'status': 'removed', 'id': watchlist_id}
