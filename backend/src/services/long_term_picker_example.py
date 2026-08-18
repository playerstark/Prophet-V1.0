"""
Long-Term Stock Picker - Usage Examples and Integration Guide

This example demonstrates how to use the comprehensive long-term stock selection model
for building a high-quality investment portfolio.

Key Features:
- Industry-level analysis with structural growth assessment
- Multi-method valuation (DCF, P/E, analyst targets)
- Comprehensive risk profiling (temporary vs structural risks)
- Technical confirmation as secondary layer
- Transparent scoring with detailed breakdowns
- Configurable thresholds and assumptions
"""

import asyncio
from long_term_picker import LongTermStockPicker, IndustryAnalyzer


# ============================================================================
# EXAMPLE 1: Basic Usage - Analyze and Rank a Stock List
# ============================================================================

async def example_basic_analysis():
    """Simple example: analyze a list of stocks and get rankings"""

    # Initialize the picker with default configuration
    picker = LongTermStockPicker()

    # List of stocks to analyze
    symbols = ['MSFT', 'NVDA', 'JPM', 'TSM', 'TSLA', 'CRM']

    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Stock Analysis and Ranking")
    print("="*80)

    # Analyze all stocks
    analyses = await picker.rank_stocks(symbols)

    # Display results
    for analysis in analyses:
        print(f"\n{'='*60}")
        print(f"Stock: {analysis.symbol} - {analysis.company_name}")
        print(f"{'='*60}")
        print(f"Industry:             {analysis.industry}")
        print(f"Classification:       {analysis.classification}")
        print(f"Overall Score:        {analysis.overall_score:.0f}/100")
        print(f"Estimated Annual Return: {analysis.estimated_annual_return:.1f}%")
        print(f"Risk Rating:          {analysis.risk_profile.risk_rating if analysis.risk_profile else 'N/A'}")
        print(f"\nCurrent Price:        ${analysis.valuation.current_price:.2f}" if analysis.valuation else "N/A")
        print(f"DCF Intrinsic Value:  ${analysis.intrinsic_value:.2f}" if analysis.intrinsic_value else "N/A")
        print(f"Undervaluation:       {analysis.undervaluation_pct:.1f}%" if analysis.undervaluation_pct else "N/A")
        print(f"P/E Ratio:            {analysis.valuation.pe_ratio:.1f}x" if analysis.valuation and analysis.valuation.pe_ratio else "N/A")
        print(f"Revenue Growth:       {analysis.revenue_growth_ttm*100:.1f}%" if analysis.revenue_growth_ttm else "N/A")
        print(f"ROE:                  {analysis.roe*100:.1f}%" if analysis.roe else "N/A")
        print(f"\nThesis:\n{analysis.thesis}")


# ============================================================================
# EXAMPLE 2: Custom Configuration - Adjust Thresholds and Weights
# ============================================================================

async def example_custom_config():
    """Example: customize the picker for different risk profiles"""

    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Configuration")
    print("="*80)

    # Conservative configuration (higher return threshold, less weight on valuation)
    conservative_config = {
        'min_annual_return': 0.30,  # 30% minimum return
        'watchlist_return_threshold': 0.20,
        'score_weights': {
            'industry': 0.20,
            'fundamental': 0.40,  # Higher weight on fundamentals
            'valuation': 0.20,
            'technical': 0.10,
            'risk_adjustment': 0.10,
        },
        'dcf_wacc': 0.09,  # Higher discount rate = more conservative
        'quality_threshold': 50,  # Minimum fundamental score
    }

    # Aggressive configuration (lower return threshold, more weight on upside)
    aggressive_config = {
        'min_annual_return': 0.20,  # 20% minimum return
        'watchlist_return_threshold': 0.10,
        'score_weights': {
            'industry': 0.15,
            'fundamental': 0.30,
            'valuation': 0.35,  # Higher weight on valuation
            'technical': 0.12,
            'risk_adjustment': 0.08,
        },
        'dcf_wacc': 0.07,  # Lower discount rate = more optimistic
        'quality_threshold': 30,
    }

    # Use conservative picker
    conservative_picker = LongTermStockPicker(config=conservative_config)
    print("\n✓ Conservative Picker Created")
    print("  - Minimum annual return: 30%")
    print("  - Higher emphasis on fundamental quality")
    print("  - Higher discount rate (more margin of safety)")

    # Use aggressive picker
    aggressive_picker = LongTermStockPicker(config=aggressive_config)
    print("\n✓ Aggressive Picker Created")
    print("  - Minimum annual return: 20%")
    print("  - Higher emphasis on valuation upside")
    print("  - Lower discount rate (higher upside potential)")

    # Analyze single stock with both configurations
    symbol = 'NVDA'
    print(f"\n\nAnalyzing {symbol} with different configurations:")
    print(f"{'-'*60}")

    conservative = await conservative_picker.analyze_stock(symbol)
    aggressive = await aggressive_picker.analyze_stock(symbol)

    if conservative and aggressive:
        print(f"\nConservative Picker:")
        print(f"  Classification: {conservative.classification}")
        print(f"  Overall Score:  {conservative.overall_score:.0f}/100")
        print(f"  Estimated Return: {conservative.estimated_annual_return:.1f}%")

        print(f"\nAggressive Picker:")
        print(f"  Classification: {aggressive.classification}")
        print(f"  Overall Score:  {aggressive.overall_score:.0f}/100")
        print(f"  Estimated Return: {aggressive.estimated_annual_return:.1f}%")


# ============================================================================
# EXAMPLE 3: Industry Analysis and Peer Comparison
# ============================================================================

async def example_industry_analysis():
    """Example: analyze industries and compare companies within sectors"""

    print("\n" + "="*80)
    print("EXAMPLE 3: Industry Analysis")
    print("="*80)

    # Analyze a portfolio of AI/semiconductor stocks
    ai_stocks = ['NVDA', 'TSM', 'AMD', 'ASML', 'QCOM']

    picker = LongTermStockPicker()
    analyses = await picker.rank_stocks(ai_stocks)

    if analyses:
        # Get industry statistics
        industry_stats = IndustryAnalyzer.get_industry_rank(analyses)

        print("\nIndustry Breakdown:")
        print(f"{'-'*60}")

        for industry, stats in industry_stats.items():
            print(f"\n{industry}")
            print(f"  Number of stocks: {stats['count']}")
            print(f"  Avg Revenue Growth: {stats['avg_growth']*100:.1f}%" if stats['avg_growth'] else "  Avg Revenue Growth: N/A")
            print(f"  Avg P/E Ratio: {stats['avg_pe']:.1f}x" if stats['avg_pe'] else "  Avg P/E Ratio: N/A")
            print(f"  Avg ROE: {stats['avg_roe']*100:.1f}%" if stats['avg_roe'] else "  Avg ROE: N/A")
            print(f"  Industry Score: {stats['industry_score']:.0f}/100")

        # Show ranking within industry
        print(f"\n{'-'*60}")
        print("Ranking within Semiconductor Industry:")
        print(f"{'-'*60}")
        for i, analysis in enumerate(analyses, 1):
            if 'Semiconductor' in analysis.industry:
                print(f"{i}. {analysis.symbol:6} - Score: {analysis.overall_score:5.0f}, "
                      f"Return: {analysis.estimated_annual_return:5.1f}%, "
                      f"Classification: {analysis.classification}")


# ============================================================================
# EXAMPLE 4: Risk Assessment Deep Dive
# ============================================================================

async def example_risk_analysis():
    """Example: detailed risk analysis for investment decision-making"""

    print("\n" + "="*80)
    print("EXAMPLE 4: Risk Assessment Deep Dive")
    print("="*80)

    picker = LongTermStockPicker()

    # Analyze a growth stock with higher risk profile
    symbol = 'TSLA'
    analysis = await picker.analyze_stock(symbol)

    if analysis and analysis.risk_profile:
        print(f"\nComprehensive Risk Analysis for {symbol}")
        print(f"{'-'*60}")

        risk = analysis.risk_profile

        print(f"\nRisk Rating: {risk.risk_rating}")
        print(f"Risk Score: {risk.risk_score:.0f}/100 (lower is better)")

        print(f"\n📊 Risk Factors:")
        for i, factor in enumerate(risk.risk_factors, 1):
            print(f"  {i}. {factor}")

        print(f"\n⏱️  Temporary Risks (short-term headwinds):")
        if risk.temporary_risks:
            for risk_item in risk.temporary_risks:
                print(f"  • {risk_item}")
        else:
            print("  None identified")

        print(f"\n🔴 Structural Risks (long-term challenges):")
        if risk.structural_risks:
            for risk_item in risk.structural_risks:
                print(f"  • {risk_item}")
        else:
            print("  None identified")

        print(f"\n❌ Thesis Invalidation Factors:")
        if risk.invalidation_factors:
            for factor in risk.invalidation_factors:
                print(f"  • {factor}")
        else:
            print("  None identified")


# ============================================================================
# EXAMPLE 5: Scenario Analysis - Conservative vs Optimistic
# ============================================================================

async def example_scenario_analysis():
    """Example: run DCF analysis under different growth scenarios"""

    print("\n" + "="*80)
    print("EXAMPLE 5: Scenario Analysis (DCF Sensitivity)")
    print("="*80)

    picker = LongTermStockPicker()

    symbol = 'MSFT'
    print(f"\nAnalyzing {symbol} under different growth scenarios:")
    print(f"{'-'*60}")

    scenarios = ['conservative', 'base', 'optimistic']

    for scenario in scenarios:
        analysis = await picker.analyze_stock(symbol, use_scenario=scenario)

        if analysis:
            print(f"\n{scenario.upper()} CASE")
            print(f"  Intrinsic Value: ${analysis.intrinsic_value:.2f}" if analysis.intrinsic_value else "  N/A")
            print(f"  Undervaluation:  {analysis.undervaluation_pct:.1f}%" if analysis.undervaluation_pct else "  N/A")
            print(f"  Expected Return: {analysis.estimated_annual_return:.1f}%")
            if analysis.dcf:
                print(f"  FCF Margin Assumption: {analysis.dcf.assumptions.get('fcf_margin', 'N/A'):.1%}")
                print(f"  Growth Rates: {analysis.dcf.assumptions.get('revenue_growth_rates', 'N/A')}")


# ============================================================================
# EXAMPLE 6: Scoring Breakdown - Understand How Scores are Calculated
# ============================================================================

async def example_scoring_breakdown():
    """Example: understand the component scoring system"""

    print("\n" + "="*80)
    print("EXAMPLE 6: Scoring Breakdown")
    print("="*80)

    picker = LongTermStockPicker()
    config = picker.get_config()

    print("\nScoring Weights:")
    print(f"{'-'*60}")
    weights = config.get('weights', config.get('score_weights', {}))
    for component, weight in weights.items():
        print(f"  {component:20} {weight:.0%}")
    print(f"  {'TOTAL':20} {sum(weights.values()):.0%}")

    symbol = 'AAPL'
    analysis = await picker.analyze_stock(symbol)

    if analysis:
        print(f"\n\nScore Breakdown for {symbol}:")
        print(f"{'-'*60}")

        breakdown = analysis.score_breakdown
        print(f"  Industry Score:             {breakdown.get('industry', 0):5.0f}/100")
        print(f"  Fundamental Quality Score:  {breakdown.get('fundamental', 0):5.0f}/100")
        print(f"  Valuation Score:            {breakdown.get('valuation', 0):5.0f}/100")
        print(f"  Technical Confirmation:     {breakdown.get('technical', 0):5.0f}/100")
        print(f"  Risk Adjustment Factor:     {breakdown.get('risk_adjustment', 0):5.0f}/100")
        print(f"  {'-'*40}")
        print(f"  OVERALL SCORE:              {breakdown.get('overall', 0):5.0f}/100")

        print(f"\n\nContribution to Overall Score:")
        print(f"{'-'*60}")
        for component, weight in weights.items():
            score = breakdown.get(component, 0)
            contribution = score * weight
            print(f"  {component:20} = {score:5.0f} × {weight:.0%} = {contribution:6.1f}")


# ============================================================================
# EXAMPLE 7: Build a Long-Term Portfolio
# ============================================================================

async def example_portfolio_building():
    """Example: use the picker to build a diversified long-term portfolio"""

    print("\n" + "="*80)
    print("EXAMPLE 7: Portfolio Construction")
    print("="*80)

    picker = LongTermStockPicker()

    # Diversified universe of stocks across sectors
    portfolio_universe = [
        # Technology
        'MSFT', 'NVDA', 'TSM', 'AAPL',
        # Healthcare
        'JNJ', 'UNH', 'NOVO',
        # Industrials
        'LMT', 'RTX',
        # Consumer
        'LVMH',
        # Financial
        'JPM',
    ]

    print(f"\nAnalyzing {len(portfolio_universe)} stocks for portfolio construction...")
    analyses = await picker.rank_stocks(portfolio_universe)

    # Filter by classification
    strong_buys = [a for a in analyses if a.classification == "Strong Buy"]
    buys = [a for a in analyses if a.classification == "Buy"]
    watchlist = [a for a in analyses if a.classification == "Watchlist"]

    print(f"\n{'='*60}")
    print("PORTFOLIO RECOMMENDATIONS")
    print(f"{'='*60}")

    print(f"\n🟢 STRONG BUY ({len(strong_buys)} stocks) - Highest conviction")
    print(f"{'-'*60}")
    for analysis in strong_buys:
        print(f"  {analysis.symbol:6} | Return: {analysis.estimated_annual_return:5.1f}% | "
              f"Score: {analysis.overall_score:5.0f} | {analysis.industry}")

    print(f"\n🟡 BUY ({len(buys)} stocks) - Good candidates")
    print(f"{'-'*60}")
    for analysis in buys:
        print(f"  {analysis.symbol:6} | Return: {analysis.estimated_annual_return:5.1f}% | "
              f"Score: {analysis.overall_score:5.0f} | {analysis.industry}")

    print(f"\n⚪ WATCHLIST ({len(watchlist)} stocks) - Monitor for better entry")
    print(f"{'-'*60}")
    for analysis in watchlist:
        print(f"  {analysis.symbol:6} | Return: {analysis.estimated_annual_return:5.1f}% | "
              f"Score: {analysis.overall_score:5.0f} | {analysis.industry}")

    # Summary metrics
    if analyses:
        avg_return = sum(a.estimated_annual_return for a in analyses) / len(analyses)
        avg_score = sum(a.overall_score for a in analyses) / len(analyses)

        print(f"\n{'='*60}")
        print("PORTFOLIO STATISTICS")
        print(f"{'='*60}")
        print(f"  Total candidates analyzed: {len(analyses)}")
        print(f"  Avg estimated return: {avg_return:.1f}%")
        print(f"  Avg overall score: {avg_score:.0f}/100")


# ============================================================================
# Main Runner
# ============================================================================

async def main():
    """Run all examples"""

    try:
        await example_basic_analysis()
        await example_custom_config()
        await example_industry_analysis()
        await example_risk_analysis()
        await example_scenario_analysis()
        await example_scoring_breakdown()
        await example_portfolio_building()

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("LONG-TERM STOCK PICKER - COMPREHENSIVE EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates the full capabilities of the long-term")
    print("stock selection framework for building fundamental-driven,")
    print("low-hype investment portfolios.")

    asyncio.run(main())

    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80)
