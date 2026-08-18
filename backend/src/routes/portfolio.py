from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Holding, Trade
from typing import List

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

@router.get("/holdings")
async def get_holdings(db: Session = Depends(get_db)):
    """Get current holdings"""
    holdings = db.query(Holding).all()
    total_value = sum(h.market_value for h in holdings) if holdings else 0
    total_pnl = sum(h.unrealised_pnl for h in holdings) if holdings else 0
    return {
        'holdings': holdings,
        'total_value': total_value,
        'total_pnl': total_pnl,
        'total_pnl_percent': (total_pnl / total_value * 100) if total_value > 0 else 0
    }

@router.get("/trades")
async def get_trades(db: Session = Depends(get_db)):
    """Get trade history"""
    trades = db.query(Trade).order_by(Trade.entry_time.desc()).all()

    closed_trades = [t for t in trades if t.status == 'closed']
    total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
    win_count = sum(1 for t in closed_trades if t.pnl and t.pnl > 0)
    win_rate = (win_count / len(closed_trades) * 100) if closed_trades else 0

    best_trade = max(closed_trades, key=lambda t: t.pnl, default=None) if closed_trades else None

    return {
        'trades': trades,
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'best_trade': best_trade,
    }

@router.get("/pnl")
async def get_pnl(db: Session = Depends(get_db)):
    """Get comprehensive P&L statistics"""
    trades = db.query(Trade).all()

    # Separate closed and open trades
    closed_trades = [t for t in trades if t.status == 'closed']
    open_trades = [t for t in trades if t.status == 'open']

    # Calculate P&L metrics
    realized_pnl = sum(t.pnl for t in closed_trades if t.pnl)
    unrealized_pnl = sum(t.pnl for t in open_trades if t.pnl)
    total_pnl = realized_pnl + unrealized_pnl

    # Win rate
    winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
    losing_trades = [t for t in closed_trades if t.pnl and t.pnl < 0]
    total_trades = len(closed_trades)
    win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0

    # Best and worst trades
    best_trade = max(closed_trades, key=lambda t: t.pnl or 0, default=None) if closed_trades else None
    worst_trade = min(closed_trades, key=lambda t: t.pnl or 0, default=None) if closed_trades else None

    total_value = realized_pnl + unrealized_pnl
    total_pnl_percent = (total_pnl / abs(total_value) * 100) if total_value != 0 else 0

    # Convert trades to dicts
    trades_list = []
    for t in trades:
        trades_list.append({
            'id': t.id,
            'symbol': t.symbol,
            'horizon': t.horizon.value if t.horizon else None,
            'direction': t.direction,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'stop_loss': t.stop_loss,
            'target_price': t.target_price,
            'quantity': t.quantity,
            'status': t.status,
            'entry_time': t.entry_time.isoformat() if t.entry_time else None,
            'exit_time': t.exit_time.isoformat() if t.exit_time else None,
            'pnl': t.pnl,
            'pnl_percent': t.pnl_percent
        })

    return {
        'realized_pnl': float(realized_pnl),
        'unrealized_pnl': float(unrealized_pnl),
        'total_pnl': float(total_pnl),
        'total_pnl_percent': float(total_pnl_percent),
        'win_rate': float(win_rate),
        'total_trades': total_trades,
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'best_trade': {
            'symbol': best_trade.symbol,
            'pnl': best_trade.pnl,
            'pnl_percent': best_trade.pnl_percent
        } if best_trade else None,
        'worst_trade': {
            'symbol': worst_trade.symbol,
            'pnl': worst_trade.pnl,
            'pnl_percent': worst_trade.pnl_percent
        } if worst_trade else None,
        'trades': trades_list
    }

@router.post("/trades")
async def create_trade(trade_data: dict, db: Session = Depends(get_db)):
    """Create a new trade"""
    trade = Trade(**trade_data)
    db.add(trade)
    db.commit()
    return {'status': 'created', 'trade_id': trade.id}
