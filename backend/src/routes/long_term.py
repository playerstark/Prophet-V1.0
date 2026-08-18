"""Long-term investment picker API routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import LongTermInvestmentAnalysis, LongTermInvestmentClass
from src.services.long_term_picker import LongTermStockPicker
from typing import List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/long-term", tags=["long-term-investing"])

# Global picker instance (would be better in dependency injection)
picker = LongTermStockPicker()


@router.get("/config")
async def get_configuration():
    """Get current long-term picker configuration"""
    return {
        'status': 'success',
        'config': picker.get_config()
    }


@router.post("/config")
async def update_configuration(updates: dict):
    """Update long-term picker configuration"""
    try:
        picker.update_config(updates)
        return {
            'status': 'success',
            'message': 'Configuration updated',
            'config': picker.get_config()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze/{symbol}")
async def analyze_stock(symbol: str, db: Session = Depends(get_db)):
    """
    Perform comprehensive long-term analysis on a single stock

    Returns detailed analysis with scores, valuation, fundamentals, and investment thesis
    """
    try:
        # Run analysis
        analysis = await picker.analyze_stock(symbol)

        if not analysis:
            raise HTTPException(status_code=404, detail=f"Could not analyze {symbol}")

        # Store in database
        existing = db.query(LongTermInvestmentAnalysis).filter(
            LongTermInvestmentAnalysis.symbol == symbol
        ).order_by(LongTermInvestmentAnalysis.analysis_date.desc()).first()

        # Extract values from nested structures and convert numpy types
        valuation = analysis.valuation or {}
        technical = analysis.technical or {}
        risk_profile = analysis.risk_profile or {}

        # Helper to convert numpy types to Python types
        def to_python_type(val):
            if val is None:
                return None
            if hasattr(val, 'item'):  # numpy scalar
                return float(val.item())
            return val

        db_entry = LongTermInvestmentAnalysis(
            symbol=analysis.symbol,
            company_name=analysis.company_name,
            industry=analysis.industry,
            current_price=float(valuation.current_price if valuation else 0),
            pe_ratio=to_python_type(valuation.pe_ratio) if valuation else None,
            forward_pe=to_python_type(valuation.forward_pe) if valuation else None,
            industry_pe=to_python_type(valuation.industry_pe) if valuation else None,
            intrinsic_value=to_python_type(analysis.intrinsic_value),
            undervaluation_pct=to_python_type(analysis.undervaluation_pct),
            revenue_growth_3y=to_python_type(analysis.revenue_growth_3y),
            fcf_margin=to_python_type(analysis.fcf_margin),
            debt_to_equity=to_python_type(analysis.debt_to_equity),
            roe=to_python_type(analysis.roe),
            rsi=to_python_type(technical.rsi if technical else None),
            adx=to_python_type(technical.adx if technical else None),
            momentum=to_python_type(technical.momentum if technical else None),
            risk_factors=json.dumps(risk_profile.risk_factors if risk_profile else []),
            risk_score=float(risk_profile.risk_score if risk_profile else 0),
            analyst_target_price=to_python_type(analysis.analyst_target_price),
            analyst_upside_pct=to_python_type(analysis.analyst_upside_pct),
            industry_score=float(analysis.industry_score),
            fundamental_quality_score=float(analysis.fundamental_quality_score),
            dcf_score=float(analysis.valuation_score),
            technical_score=float(analysis.technical_confirmation_score),
            overall_score=float(analysis.overall_score),
            estimated_annual_return=float(analysis.estimated_annual_return),
            classification=LongTermInvestmentClass(analysis.classification.lower().replace(' ', '_')),
            thesis=analysis.thesis,
            analysis_date=datetime.utcnow()
        )

        db.add(db_entry)
        db.commit()

        # Extract nested values
        valuation = analysis.valuation or {}
        technical = analysis.technical or {}
        risk_profile = analysis.risk_profile or {}

        return {
            'status': 'success',
            'analysis': {
                'symbol': analysis.symbol,
                'company_name': analysis.company_name,
                'industry': analysis.industry,
                'current_price': valuation.current_price if valuation else 0,
                'valuation': {
                    'pe_ratio': valuation.pe_ratio if valuation else None,
                    'forward_pe': valuation.forward_pe if valuation else None,
                    'intrinsic_value': analysis.intrinsic_value,
                    'undervaluation_pct': analysis.undervaluation_pct,
                    'dcf_score': round(analysis.valuation_score, 1),
                },
                'fundamentals': {
                    'revenue_growth_3y': analysis.revenue_growth_3y,
                    'fcf_margin': analysis.fcf_margin,
                    'debt_to_equity': analysis.debt_to_equity,
                    'roe': analysis.roe,
                    'fundamental_quality_score': round(analysis.fundamental_quality_score, 1),
                },
                'technical': {
                    'rsi': technical.rsi if technical else None,
                    'adx': technical.adx if technical else None,
                    'momentum': technical.momentum if technical else None,
                    'technical_score': round(analysis.technical_confirmation_score, 1),
                },
                'risk': {
                    'factors': risk_profile.risk_factors if risk_profile else [],
                    'risk_score': round(risk_profile.risk_score if risk_profile else 0, 1),
                },
                'analyst': {
                    'target_price': analysis.analyst_target_price,
                    'upside_pct': analysis.analyst_upside_pct,
                },
                'scoring': {
                    'industry_score': round(analysis.industry_score, 1),
                    'overall_score': round(analysis.overall_score, 1),
                    'estimated_annual_return': round(analysis.estimated_annual_return, 2),
                },
                'classification': analysis.classification,
                'thesis': analysis.thesis,
            }
        }

    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/rank")
async def rank_stocks(
    symbols: List[str],
    min_score: Optional[float] = Query(None),
    classification: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Analyze and rank multiple stocks

    Returns stocks ranked by overall score
    """
    try:
        analyses = await picker.rank_stocks(symbols)

        # Filter results
        if min_score:
            analyses = [a for a in analyses if a.overall_score >= min_score]

        if classification:
            analyses = [a for a in analyses if a.classification.lower() == classification.lower()]

        # Format results
        results = []
        for analysis in analyses:
            valuation = analysis.valuation or {}
            risk_profile = analysis.risk_profile or {}

            results.append({
                'symbol': analysis.symbol,
                'company_name': analysis.company_name,
                'industry': analysis.industry,
                'current_price': valuation.current_price if valuation else 0,
                'classification': analysis.classification,
                'overall_score': round(analysis.overall_score, 1),
                'estimated_annual_return': round(analysis.estimated_annual_return, 2),
                'industry_score': round(analysis.industry_score, 1),
                'valuation_score': round(analysis.valuation_score, 1),
                'fundamental_score': round(analysis.fundamental_quality_score, 1),
                'risk_score': round(risk_profile.risk_score if risk_profile else 0, 1),
                'undervaluation_pct': analysis.undervaluation_pct,
                'thesis': analysis.thesis,
            })

        return {
            'status': 'success',
            'count': len(results),
            'stocks': results
        }

    except Exception as e:
        logger.error(f"Error ranking stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")


@router.get("/history/{symbol}")
async def get_analysis_history(
    symbol: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get historical analysis for a stock

    Shows how the analysis score has changed over time
    """
    analyses = db.query(LongTermInvestmentAnalysis).filter(
        LongTermInvestmentAnalysis.symbol == symbol
    ).order_by(
        LongTermInvestmentAnalysis.analysis_date.desc()
    ).limit(limit).all()

    if not analyses:
        raise HTTPException(status_code=404, detail=f"No analysis history for {symbol}")

    return {
        'status': 'success',
        'symbol': symbol,
        'history': [
            {
                'analysis_date': a.analysis_date.isoformat(),
                'current_price': a.current_price,
                'intrinsic_value': a.intrinsic_value,
                'overall_score': round(a.overall_score, 1),
                'estimated_annual_return': round(a.estimated_annual_return, 2),
                'classification': a.classification,
            }
            for a in analyses
        ]
    }


@router.get("/portfolio-recommendations")
async def get_portfolio_recommendations(
    min_score: float = Query(70, ge=0, le=100),
    classification: str = Query("buy", regex="^(strong_buy|buy|watchlist|avoid)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get current portfolio recommendations

    Shows latest analysis for stocks rated Strong Buy or Buy
    """
    # Get latest analysis for each symbol
    latest_analyses = db.query(
        LongTermInvestmentAnalysis
    ).filter(
        LongTermInvestmentAnalysis.overall_score >= min_score,
        LongTermInvestmentAnalysis.classification.in_([
            LongTermInvestmentClass.STRONG_BUY,
            LongTermInvestmentClass.BUY
        ]) if classification.lower() in ['strong_buy', 'buy'] else True
    ).order_by(
        LongTermInvestmentAnalysis.overall_score.desc(),
        LongTermInvestmentAnalysis.analysis_date.desc()
    ).limit(limit).all()

    if not latest_analyses:
        latest_analyses = []

    return {
        'status': 'success',
        'recommendations': [
            {
                'symbol': a.symbol,
                'company_name': a.company_name,
                'industry': a.industry,
                'current_price': a.current_price,
                'intrinsic_value': a.intrinsic_value,
                'undervaluation_pct': round(a.undervaluation_pct, 1) if a.undervaluation_pct else None,
                'overall_score': round(a.overall_score, 1),
                'estimated_annual_return': round(a.estimated_annual_return, 2),
                'classification': a.classification,
                'thesis': a.thesis,
                'analysis_date': a.analysis_date.isoformat(),
            }
            for a in latest_analyses
        ],
        'count': len(latest_analyses)
    }


@router.get("/dashboard")
async def get_long_term_dashboard(db: Session = Depends(get_db)):
    """
    Get dashboard summary of long-term investment analysis

    Shows portfolio metrics and top recommendations
    """
    # Get latest analyses
    latest = db.query(LongTermInvestmentAnalysis).order_by(
        LongTermInvestmentAnalysis.analysis_date.desc()
    ).limit(50).all()

    if not latest:
        return {
            'status': 'success',
            'summary': {
                'total_analyzed': 0,
                'avg_score': 0,
                'strong_buy_count': 0,
                'buy_count': 0,
                'watchlist_count': 0,
                'avoid_count': 0,
            },
            'top_picks': []
        }

    # Calculate metrics
    unique_symbols = set(a.symbol for a in latest)
    strong_buy = len([a for a in latest if a.classification == LongTermInvestmentClass.STRONG_BUY])
    buy = len([a for a in latest if a.classification == LongTermInvestmentClass.BUY])
    watchlist = len([a for a in latest if a.classification == LongTermInvestmentClass.WATCHLIST])
    avoid = len([a for a in latest if a.classification == LongTermInvestmentClass.AVOID])

    avg_score = sum(a.overall_score for a in latest) / len(latest) if latest else 0

    # Top picks
    top_picks = sorted(latest, key=lambda x: x.overall_score, reverse=True)[:5]

    return {
        'status': 'success',
        'summary': {
            'total_analyzed': len(unique_symbols),
            'avg_score': round(avg_score, 1),
            'strong_buy_count': strong_buy,
            'buy_count': buy,
            'watchlist_count': watchlist,
            'avoid_count': avoid,
        },
        'top_picks': [
            {
                'symbol': p.symbol,
                'company_name': p.company_name,
                'classification': p.classification,
                'overall_score': round(p.overall_score, 1),
                'estimated_annual_return': round(p.estimated_annual_return, 2),
            }
            for p in top_picks
        ]
    }
