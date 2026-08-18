# Long-Term Stock Picker - Complete Guide

## Overview

The **Long-Term Stock Picker** is a sophisticated, production-ready framework for identifying and ranking undervalued stocks with strong long-term growth potential. It implements a comprehensive multi-factor model combining:

- **Industry Analysis** - Structural growth assessment
- **Fundamental Analysis** - Revenue growth, profitability, quality
- **Valuation Modeling** - DCF analysis with scenario sensitivity
- **Risk Assessment** - Comprehensive risk profiling
- **Technical Confirmation** - Trend and momentum validation
- **Return Estimation** - Expected annual return projections

### Key Philosophy

**Avoid hype-driven stock picking. Focus on:**
1. Real, sustainable revenue growth supported by market adoption
2. Reasonable valuations with margin of safety
3. Strong R&D and competitive moats
4. Risk-adjusted return potential >25% annually
5. Industry tailwinds and structural growth opportunities

---

## Quick Start

### Installation

The model is part of the Prophet V1.0 backend services. Ensure dependencies are installed:

```bash
pip install yfinance pandas numpy
```

### 5-Minute Example

```python
import asyncio
from long_term_picker import LongTermStockPicker

async def main():
    # Initialize picker
    picker = LongTermStockPicker()
    
    # Analyze stocks
    stocks = ['MSFT', 'NVDA', 'AAPL']
    analyses = await picker.rank_stocks(stocks)
    
    # Display results
    for analysis in analyses:
        print(f"{analysis.symbol}: {analysis.classification}")
        print(f"  Score: {analysis.overall_score:.0f}/100")
        print(f"  Return: {analysis.estimated_annual_return:.1f}%")
        print(f"  Industry: {analysis.industry}")
        print(f"  Thesis: {analysis.thesis}\n")

asyncio.run(main())
```

---

## Files in This System

### Core Implementation

#### `long_term_picker.py` (Main Module)
The complete implementation including:
- `DCFValuationModel` - Discounted Cash Flow analysis
- `IndustryAnalyzer` - Industry-level assessment
- `RiskAssessment` - Risk profiling and categorization
- `LongTermStockPicker` - Main orchestration engine
- Data classes for structured results

**Classes:**
- `StockAnalysis` - Complete analysis results
- `ValuationMetrics` - Valuation component
- `DCFResult` - DCF analysis output
- `RiskProfile` - Risk assessment output
- `TechnicalIndicators` - Technical analysis output

### Documentation

#### `LONG_TERM_PICKER_DOCS.md` (Comprehensive Guide)
Complete technical documentation covering:
- Architecture and components
- Scoring methodology
- Risk assessment framework
- Configuration options
- Return estimation model
- Usage examples
- Integration points
- Limitations and disclaimers

**Read this for:** In-depth understanding of how everything works

#### `CONFIG_GUIDE.md` (Configuration Reference)
Practical guide for customizing the system:
- Pre-built configuration presets (Conservative, Balanced, Growth, Aggressive)
- Parameter explanations and effects
- Customization examples by investor type
- Dynamic adjustment strategies
- Common mistakes to avoid

**Read this for:** Configuring the system for your needs

#### `LONG_TERM_PICKER_README.md` (This File)
Entry point and navigation guide

### Examples & Testing

#### `long_term_picker_example.py` (Code Examples)
Seven comprehensive examples demonstrating:
1. Basic analysis and ranking
2. Custom configuration
3. Industry analysis
4. Risk assessment deep-dive
5. Scenario analysis (DCF sensitivity)
6. Scoring breakdown transparency
7. Portfolio construction

**Run this for:** Hands-on learning and testing

---

## Core Concepts

### 1. The Five-Factor Scoring Model

Overall Score combines:

```
Overall Score = (Industry × 15%) + (Fundamental × 35%) + 
                (Valuation × 30%) + (Technical × 10%) + (Risk × 10%)
```

**Component Breakdown:**

| Factor | Weight | Focus | Lower = | Higher = |
|--------|--------|-------|---------|----------|
| Industry | 15% | Structural opportunity | No tailwinds | Strong growth |
| Fundamental | 35% | Quality & growth | Deteriorating | Excellent |
| Valuation | 30% | Discount to fair value | Overpriced | Deep value |
| Technical | 10% | Trend confirmation | Downtrend | Strong uptrend |
| Risk | 10% | Downside protection | High risk | Low risk |

### 2. Classification System

Four-tier ranking based on score and return potential:

| Classification | Score | Return | Action |
|----------------|-------|--------|--------|
| **Strong Buy** | >80 | >37.5% | Accumulate |
| **Buy** | >75 | >25% | Build position |
| **Watchlist** | >65 | >15% | Monitor |
| **Avoid** | <65 | <15% | Skip or wait |

### 3. Valuation Framework

Multi-method approach:

1. **DCF (Primary)** - Intrinsic value from cash flows
2. **Analyst Targets** - Professional consensus
3. **Comparative Multiples** - P/E, P/S, PEG ratios
4. **Mean Reversion** - Historical valuation levels

**Return Estimate** = Weighted average of all methods

### 4. Risk Assessment

**Three Categories:**

- **Temporary Risks** - Short-term headwinds (interest rates, supply chain)
- **Structural Risks** - Long-term challenges (industry decline, disruption)
- **Quality Risks** - Financial health concerns (debt, margins, growth)

**Four Risk Ratings:**
- Low (0-20 score)
- Medium (20-45 score)
- High (45-60 score)
- Critical (60+ score)

### 5. Industry Attractiveness

Ranks industries by structural opportunity:

**Tier 1 (Most Attractive)**
- Technology (0.92/1.0) - AI, cloud, semiconductors
- Semiconductors (0.88/1.0) - Chip design and fab
- Green Energy (0.90/1.0) - Renewable and storage

**Tier 2 (Attractive)**
- Healthcare (0.85/1.0) - Pharma, biotech, devices
- Industrials (0.55/1.0) - Manufacturing, automation

**Tier 3 (Challenged)**
- Financial Services (0.60/1.0) - Fintech disruption risk
- Consumer Discretionary (0.50/1.0) - Mature market

**Tier 4 (Unattractive)**
- Energy (0.25/1.0) - Fossil fuel decline

---

## Input & Output

### Input: Stock Symbol(s)

```python
# Single stock
analysis = await picker.analyze_stock('MSFT')

# Multiple stocks (ranked)
analyses = await picker.rank_stocks(['MSFT', 'NVDA', 'AAPL'])
```

### Output: Complete Analysis

```python
StockAnalysis:
  symbol: str                    # Stock ticker
  company_name: str              # Full company name
  industry: str                  # Industry classification
  
  valuation: ValuationMetrics    # P/E, P/S, DCF value
  intrinsic_value: float         # Fair value per DCF
  undervaluation_pct: float      # % below/above intrinsic
  
  revenue_growth_ttm: float      # Annual revenue growth
  roe: float                     # Return on equity
  debt_to_equity: float          # Leverage ratio
  
  technical: TechnicalIndicators # RSI, ADX, momentum, trend
  
  risk_profile: RiskProfile      # Risks, rating, invalidation factors
  
  estimated_annual_return: float # Expected % annual return
  
  industry_score: float          # Component scores
  fundamental_quality_score: float
  valuation_score: float
  technical_confirmation_score: float
  overall_score: float           # Composite 0-100
  
  classification: str            # Strong Buy / Buy / Watchlist / Avoid
  thesis: str                    # Investment thesis narrative
```

---

## Usage Patterns

### Pattern 1: Quick Stock Check

```python
picker = LongTermStockPicker()
analysis = await picker.analyze_stock('MSFT')

if analysis:
    print(f"{analysis.classification}: {analysis.thesis}")
```

### Pattern 2: Portfolio Screening

```python
# Screen universe of stocks
universe = ['MSFT', 'NVDA', 'AAPL', 'JPM', 'JNJ', ...]
analyses = await picker.rank_stocks(universe)

# Filter by classification
strong_buys = [a for a in analyses if a.classification == 'Strong Buy']
watchlist = [a for a in analyses if a.classification == 'Watchlist']
```

### Pattern 3: Scenario Analysis

```python
# Test different growth assumptions
conservative = await picker.analyze_stock('NVDA', use_scenario='conservative')
base = await picker.analyze_stock('NVDA', use_scenario='base')
optimistic = await picker.analyze_stock('NVDA', use_scenario='optimistic')

# Compare results
print(f"Conservative: ${conservative.intrinsic_value}")
print(f"Base:         ${base.intrinsic_value}")
print(f"Optimistic:   ${optimistic.intrinsic_value}")
```

### Pattern 4: Custom Configuration

```python
# Create growth-focused picker
config = {
    'min_annual_return': 0.20,
    'score_weights': {
        'fundamental': 0.30,
        'valuation': 0.40,
        ...
    },
    'dcf_wacc': 0.07,
}

picker = LongTermStockPicker(config=config)
analyses = await picker.rank_stocks(stocks)
```

### Pattern 5: Configuration Adjustment

```python
picker = LongTermStockPicker()

# Tighten risk filter
picker.update_config({
    'score_weights': {
        ...
        'risk_adjustment': 0.15,  # From 0.10
    }
})

# Re-analyze with new settings
analyses = await picker.rank_stocks(stocks)
```

---

## Configuration Presets

### Use Default (Balanced)
```python
picker = LongTermStockPicker()
```
Best for: Most investors, general-purpose screening

### Conservative (Preserve Capital)
```python
from CONFIG_GUIDE import conservative_config
picker = LongTermStockPicker(config=conservative_config)
```
Best for: Capital preservation, dividend investors, retirees

### Growth (Capital Appreciation)
```python
from CONFIG_GUIDE import growth_config
picker = LongTermStockPicker(config=growth_config)
```
Best for: Long-term growth, tech-focused, younger investors

### Aggressive (Maximum Returns)
```python
from CONFIG_GUIDE import aggressive_config
picker = LongTermStockPicker(config=aggressive_config)
```
Best for: High risk tolerance, experienced investors, turnaround plays

See `CONFIG_GUIDE.md` for complete preset definitions and customization.

---

## Key Features

### 1. Transparent Scoring
Every component score is calculated and visible:
```python
print(analysis.score_breakdown)
# {
#     'industry': 75.0,
#     'fundamental': 82.0,
#     'valuation': 70.0,
#     'technical': 65.0,
#     'risk_adjustment': 80.0,
#     'overall': 76.3
# }
```

### 2. Detailed Risk Profiling
Understand what could go wrong:
```python
risk = analysis.risk_profile
print(f"Risk Rating: {risk.risk_rating}")
print(f"Risk Score: {risk.risk_score}")
print(f"Temporary Risks: {risk.temporary_risks}")
print(f"Structural Risks: {risk.structural_risks}")
print(f"Invalidation Factors: {risk.invalidation_factors}")
```

### 3. DCF Scenario Analysis
Test sensitivity to assumptions:
```python
# Three scenarios built-in
# Conservative: Lower growth, lower margins, higher discount rate
# Base Case: Moderate assumptions
# Optimistic: Higher growth, higher margins, lower discount rate

# Pick which to use
analysis = await picker.analyze_stock('MSFT', use_scenario='conservative')
```

### 4. Industry Ranking
Identify best sectors first:
```python
industry_stats = IndustryAnalyzer.get_industry_rank(analyses)
# Ranks industries by average metrics within your stock list
```

### 5. Configurable Return Threshold
Adjust minimum return requirement:
```python
config['min_annual_return'] = 0.30  # Require 30% annual return
config['watchlist_return_threshold'] = 0.20  # Watchlist at 20%
```

### 6. Investment Thesis Generation
Structured narrative explaining the opportunity:
```python
# Thesis covers: company, industry, valuation, risks, return potential
print(analysis.thesis)
```

---

## Common Use Cases

### Screening for Long-Term Portfolio

1. Load list of 50-200 stocks
2. Rank by overall score
3. Focus on "Strong Buy" and "Buy" classifications
4. Review industry breakdown (ensure diversification)
5. Check risk ratings (reject "Critical" risk)
6. Build position allocation

### Finding Undervalued Growth

1. Filter stocks with >20% revenue growth
2. Look for valuation score >75
3. Check undervaluation_pct >10%
4. Ensure fundamental quality >70
5. Verify industry attractiveness

### Portfolio Rebalancing

1. Analyze current holdings quarterly
2. Identify deteriorating names (score declining)
3. Monitor watchlist for buying opportunities
4. Compare relative valuations within sector
5. Adjust allocation based on updated scores

### Risk Management

1. Set high quality_threshold (70+)
2. Increase risk_adjustment weight
3. Lower dcf_wacc (conservative valuation)
4. Filter out risk_rating="High" or "Critical"
5. Verify invalidation factors are well-understood

---

## Integration with Prophet Platform

### API Endpoints (Future)

```
POST /api/stocks/analyze
  Input: symbol, config
  Output: Complete StockAnalysis

POST /api/stocks/rank
  Input: symbols, config
  Output: List[StockAnalysis] sorted

POST /api/config/update
  Input: config_updates
  Output: Updated configuration

GET /api/industries
  Output: Industry attractiveness rankings
```

### Database Integration

Analyze once, store results for quick retrieval:

```python
# Save analysis to database
db.save_analysis(analysis)

# Later, retrieve stored analyses
stored = db.get_analysis('MSFT')
```

### Scheduled Analysis

Run nightly to keep recommendations fresh:

```python
# Nightly job: analyze all holdings + watchlist
for symbol in portfolio_universe:
    analysis = await picker.analyze_stock(symbol)
    db.save_analysis(analysis)
    
    # Alert on major changes
    if analysis.classification changed:
        send_alert(f"{symbol}: {old} → {new}")
```

---

## Performance Expectations

### By Classification

- **Strong Buy**: 35-50% annual return (high conviction)
- **Buy**: 25-35% annual return (good candidates)
- **Watchlist**: 15-25% annual return (wait for better entry)
- **Avoid**: <15% or negative return (skip)

### Portfolio Composition (Recommended)

- 30-40% Strong Buy + Buy positions (core holdings)
- 20-30% Watchlist positions (building / monitoring)
- Remaining in cash for new opportunities

### Backtesting Performance

For historical validation (to come):
- Expected accuracy of return estimates
- Hit rate of classification signals
- Sector selection quality
- Risk prediction accuracy

---

## Limitations & Disclaimers

### Model Assumptions

The model uses assumptions about:
- Future revenue growth rates
- Free cash flow margins
- Discount rates (WACC)
- Terminal growth rates

**These are estimates.** Actual outcomes may differ significantly.

### Data Dependency

Results are only as good as underlying financial data from Yahoo Finance. Missing or incorrect data will compromise analysis.

### Market Conditions

- DCF models are sensitive to interest rate environment
- Speculative bubbles can keep overvalued stocks inflated
- Black swan events can invalidate thesis

### Not Financial Advice

This tool is for:
✓ Educational purposes
✓ Research and idea generation
✓ Due diligence framework
✓ Decision support

✗ Do NOT rely as sole investment signal
✗ Do NOT ignore qualitative factors
✗ Do NOT substitute for professional advice

### Historical Performance

Past stock picks do not guarantee future returns. Each stock must be evaluated in current market context.

---

## Next Steps

### For Immediate Use

1. Review `long_term_picker_example.py` for working code
2. Test with familiar stocks you understand well
3. Verify output makes sense to you
4. Run portfolio screening on your watchlist
5. Monitor recommendations over time

### For Deeper Understanding

1. Read `LONG_TERM_PICKER_DOCS.md` for architecture
2. Study `CONFIG_GUIDE.md` for customization
3. Backtest your configuration if possible
4. Adjust settings based on market experience
5. Refine rules based on performance

### For Integration

1. Define API endpoints needed
2. Create database schema for storing analyses
3. Set up scheduled daily/weekly analysis
4. Build alerting for major changes
5. Create web UI for browsing recommendations

---

## Support Resources

### Documentation
- `LONG_TERM_PICKER_DOCS.md` - Complete technical reference
- `CONFIG_GUIDE.md` - Configuration and customization
- `long_term_picker_example.py` - Seven working examples

### Code Reference
- `long_term_picker.py` - Main implementation (well-commented)
- Dataclasses at top define all output structures

### Questions?
Refer to docstrings in the code - every class and method is documented.

---

## Architecture at a Glance

```
LongTermStockPicker (Main Engine)
├── analyze_stock(symbol)
│   ├── Fetch data via yfinance
│   ├── IndustryAnalyzer.classify_industry()
│   ├── Calculate technical indicators (RSI, ADX, momentum)
│   ├── RiskAssessment.assess_risks()
│   ├── DCFValuationModel.calculate()
│   ├── Score components (fundamental, valuation, etc.)
│   └── Generate investment thesis
│
├── rank_stocks(symbols)
│   ├── Analyze each stock
│   ├── Sort by overall_score
│   └── Return ranked list
│
└── Configuration Management
    ├── get_config()
    └── update_config()
```

---

## Version Info

- **Framework Version**: 1.0
- **Compatible with**: Python 3.8+
- **Dependencies**: yfinance, pandas, numpy
- **Status**: Production-ready

---

## Future Enhancements

Planned improvements:
- Peer company comparison metrics
- Historical P/E percentile ranks
- Sentiment analysis integration
- Cash flow statement deep-dive analysis
- Competitive moat quantification
- ESG factor integration
- ML-based parameter optimization
- Real-time data streaming
- Backtesting framework
- Interactive web dashboard

---

## Summary

The Long-Term Stock Picker provides a **transparent, auditable framework** for finding undervalued stocks with strong growth potential, appropriate for long-term portfolio construction. It combines quantitative rigor with practical configuration flexibility, avoiding hype-driven decisions while remaining actionable for investment professionals.

**Start with:** `long_term_picker_example.py`

**For details:** `LONG_TERM_PICKER_DOCS.md`

**For config:** `CONFIG_GUIDE.md`

Happy investing! 📈
