# Long-Term Investment Picker Engine

## Overview

The **Long-Term Investment Picker** is a sophisticated, rule-based stock selection system designed to identify fundamentally strong companies trading at reasonable valuations with strong long-term growth potential.

This system avoids hype-driven picks and instead applies rigorous fundamental analysis, valuation modeling, and risk assessment to identify stocks with genuine long-term investment merit.

---

## Framework & Methodology

### 1. Industry Analysis

The engine identifies the strongest industries first, scoring them on:

- **Growth Potential (30%)** — Structural demand growth and market expansion
- **R&D Intensity (20%)** — Innovation capabilities and competitive moats
- **Structural Tailwinds (30%)** — Long-term secular trends supporting growth
- **Disruption Risk (-10%)** — Risk of technological disruption
- **Regulatory Risk (-10%)** — Compliance and policy risks

#### Industry Scoring Examples:

| Industry | Score | Rationale |
|----------|-------|-----------|
| **Technology** | 85/100 | Strong growth, high R&D, AI/cloud tailwinds |
| **Healthcare** | 80/100 | Aging population, strong innovation |
| **Financials** | 60/100 | Moderate growth, fintech disruption risk |
| **Energy** | 30/100 | Low growth, high regulation/disruption risk |

---

### 2. Valuation Analysis

#### 2a. Relative Valuation

The system compares:
- Current P/E ratio
- Forward P/E ratio
- Historical P/E range (5-year)
- Industry average P/E
- Price-to-Book, Price-to-Sales (where relevant)

#### 2b. DCF (Discounted Cash Flow) Valuation

A comprehensive DCF model calculates intrinsic value using:

```
Intrinsic Value = PV(FCF Years 1-5) + PV(Terminal Value)

Where:
  FCF = Revenue × FCF Margin (assumed 15% default)
  Terminal Value = Final Year FCF × (1 + terminal growth) / (WACC - terminal growth)
  WACC = Weighted Average Cost of Capital (default 8%)
  Terminal Growth = 2.5% (conservative perpetuity growth)
```

**Default DCF Assumptions** (configurable):
- Revenue Growth: [15%, 12%, 10%, 8%, 6%] (next 5 years)
- FCF Margin: 15%
- WACC: 8%
- Terminal Growth: 2.5%

#### 2c. Undervaluation Calculation

```
Undervaluation % = (Intrinsic Value - Current Price) / Current Price × 100
```

**Valuation Score:**
- \> 30% undervalued: 90/100
- 20-30% undervalued: 80/100
- 10-20% undervalued: 70/100
- 0-10% undervalued: 60/100
- Fairly valued: 50/100

---

### 3. Fundamental Quality Assessment

The system scores companies on:

| Metric | Excellent | Good | Average | Poor |
|--------|-----------|------|---------|------|
| **Revenue Growth** | \>15% | 10-15% | 5-10% | <5% or negative |
| **Return on Equity (ROE)** | \>20% | 15-20% | 10-15% | <10% |
| **Debt-to-Equity** | <1.0 | 1.0-1.5 | 1.5-2.0 | >2.0 |
| **Free Cash Flow Margin** | \>15% | 10-15% | 5-10% | <5% |

**Fundamental Quality Score:**
- Excellent: 85-100/100
- Good: 70-84/100
- Average: 50-69/100
- Poor: <50/100

---

### 4. Risk Assessment

The engine identifies and scores risks across multiple dimensions:

#### Risk Categories

1. **Valuation Risk**
   - High P/E (>40): Priced for unrealistic growth
   - Very Low P/E (<5): Deteriorating fundamentals

2. **Financial Risk**
   - High Leverage (D/E >2): Vulnerable to economic stress
   - Negative/Declining FCF: Unsustainable business model

3. **Business Risk**
   - Revenue Decline: Deteriorating market position
   - Margin Compression: Competitive pressure

4. **Industry Risk**
   - Disruption (Energy, traditional retail): Structural decline
   - Regulatory (Healthcare, Financials): Policy risk
   - Cyclicality: Economic sensitivity

5. **Execution Risk**
   - Management changes
   - Product pipeline risk
   - Geographic concentration

#### Risk Scoring

**Risk Score (0-100, lower is better):**
- Score <30: Low risk
- Score 30-50: Moderate risk
- Score 50-70: Elevated risk
- Score >70: High risk (typically "Avoid")

---

### 5. Technical Analysis (Secondary Confirmation)

Technical analysis serves as a **secondary confirmation layer**, not the primary driver.

**Technical Indicators Monitored:**

| Indicator | Bullish Signal | Confirmation |
|-----------|----------------|----------------|
| **RSI (14)** | 40-60 (not overbought/oversold) | +10 points |
| **ADX (14)** | >20 (strong trend) | +15 points |
| **Momentum (10-day)** | Positive slope | +10 points |
| **Price Trend** | Above 200-day MA | +5 points |

**Technical Score:**
- Strong confirmation: 80-100/100
- Moderate confirmation: 60-79/100
- Weak confirmation: 40-59/100
- Bearish technicals: <40/100

---

### 6. Analyst Estimates & Market Consensus

The system incorporates analyst research:

- **Analyst Target Price**: Average price target from major research firms
- **Analyst Upside %**: Implied return from current price to target
- **Analyst Rating Consensus**: Buy/Hold/Sell distribution

**Note:** Analyst targets are **compared against** DCF valuation, not used to replace it.

---

### 7. Expected Return Calculation

The system estimates annualized return potential using:

```
Expected Annual Return = (DCF Return × 0.5) + (Analyst Upside × 0.3) + (Growth Rate × 0.2)

Where:
  DCF Return = (Intrinsic Value - Current Price) / Current Price
  Analyst Upside = (Analyst Target - Current Price) / Current Price
  Growth Rate = Revenue Growth × 0.5 (conservative extrapolation)
```

**Return Threshold for Selection:**

The system targets stocks with **>25% annualized return potential** for "Buy" ratings, but will classify promising undervalued companies as "Watchlist" if they fall short, provided fundamentals are strong.

---

## Comprehensive Scoring System

### Overall Score Formula

```
Overall Score = (Industry Score × 0.15) 
              + (Fundamental Score × 0.35) 
              + (DCF/Valuation Score × 0.30) 
              + ((100 - Risk Score) × 0.20)
```

**Weight Rationale:**
- **35% Fundamentals**: Core business quality matters most for long-term
- **30% Valuation**: Need reasonable entry price, but not the only factor
- **20% Risk Management**: Avoid blow-ups and value traps
- **15% Industry**: Benefit from structural tailwinds

### Classification System

| Classification | Overall Score | Est. Return | Risk Profile | Thesis Strength |
|---------------|---------------|-------------|--------------|-----------------|
| **Strong Buy** | >80 | >37.5% | Low-Moderate | Excellent fundamentals, significant undervaluation |
| **Buy** | 75-80 | 25-37.5% | Moderate | Good fundamentals, reasonable undervaluation |
| **Watchlist** | 60-75 | <25% or unclear | Moderate-High | Promising but waiting for better entry or clarity |
| **Avoid** | <60 | <15% or negative | High | Deteriorating fundamentals, fully valued, or high risk |

---

## Configuration & Customization

### Adjustable Parameters

```json
{
  "min_annual_return": 0.25,  // Minimum 25% for "Buy" classification
  "weights": {
    "industry": 0.15,
    "fundamental": 0.35,
    "valuation": 0.30,
    "risk": 0.20
  },
  "dcf": {
    "revenue_growth_rates": [0.15, 0.12, 0.10, 0.08, 0.06],
    "fcf_margin": 0.15,
    "wacc": 0.08,  // Discount rate
    "terminal_growth": 0.025
  }
}
```

### API Endpoints for Configuration

**Get Current Config:**
```bash
GET /api/long-term/config
```

**Update Config:**
```bash
POST /api/long-term/config
{
  "min_annual_return": 0.30,
  "weights": { ... },
  "dcf": { ... }
}
```

---

## API Endpoints

### 1. Analyze Single Stock

```bash
POST /api/long-term/analyze/{symbol}
```

**Response:**
```json
{
  "status": "success",
  "analysis": {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "industry": "Technology",
    "current_price": 185.50,
    "valuation": {
      "pe_ratio": 28.5,
      "intrinsic_value": 220.0,
      "undervaluation_pct": 18.6,
      "dcf_score": 75
    },
    "fundamentals": {
      "revenue_growth_3y": 0.12,
      "roe": 0.95,
      "debt_to_equity": 1.2,
      "fundamental_quality_score": 82
    },
    "technical": {
      "rsi": 58.2,
      "adx": 24.5,
      "momentum": 12.3,
      "technical_score": 72
    },
    "risk": {
      "factors": ["High valuations", "Competition", "China exposure"],
      "risk_score": 35
    },
    "analyst": {
      "target_price": 210.0,
      "upside_pct": 13.1
    },
    "scoring": {
      "industry_score": 88,
      "overall_score": 78.4,
      "estimated_annual_return": 32.1
    },
    "classification": "Buy",
    "thesis": "Apple is a technology leader positioned in a structurally attractive tech sector, trading at 18.6% discount to intrinsic value with an estimated 32.1% annual return potential..."
  }
}
```

### 2. Rank Multiple Stocks

```bash
POST /api/long-term/rank
{
  "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA"],
  "min_score": 70,
  "classification": "buy"
}
```

**Response:** Ranked list of stocks by overall score

### 3. Get Portfolio Recommendations

```bash
GET /api/long-term/portfolio-recommendations?min_score=70&limit=20
```

**Returns:** Latest "Strong Buy" and "Buy" recommendations

### 4. Analysis History

```bash
GET /api/long-term/history/{symbol}?limit=10
```

**Returns:** Historical analysis showing how scores have evolved

### 5. Dashboard Summary

```bash
GET /api/long-term/dashboard
```

**Returns:** Summary metrics and top picks

---

## Investment Thesis Format

Each analyzed stock receives an investment thesis explaining:

```
"[SYMBOL] ([Company]) is a [Industry] company positioned in a structurally 
attractive [Industry] sector, trading at [X]% discount to intrinsic value 
with an estimated [Y]% annual return potential, supported by [Z]% revenue 
growth. Key risk: [Primary Risk]. Invalidated if: [What would break the thesis]."
```

**Example:**
```
"AAPL (Apple Inc.) is a Technology company positioned in a structurally 
attractive Technology sector, trading at 18.6% discount to intrinsic value 
with an estimated 32.1% annual return potential, supported by 12% revenue 
growth. Key risk: High valuations relative to peers. Invalidated if: 
iPhone demand deteriorates or China restrictions accelerate."
```

---

## Avoiding Hype-Driven Picks

The system is explicitly designed to avoid speculation:

### ✅ What's Favored

- **Fundamental strength**: High ROE, growing revenue, improving margins
- **Reasonable valuations**: Not priced for perfection
- **Real tailwinds**: AI adoption, aging population, digital transformation
- **Proven business models**: Recurring revenue, strong cash flow
- **Long-term secular trends**: Structural demand growth

### ❌ What's Penalized

- **Extreme valuations**: P/E >50 or trading at huge premiums to peers
- **Deteriorating fundamentals**: Falling revenue, margin compression
- **Speculative narratives**: "Next unicorn," unproven technologies
- **High debt + uncertain growth**: Financial risk without upside
- **Disruption without defensibility**: Vulnerable to technological change

---

## Usage Examples

### Example 1: Tech Stock Analysis

```bash
curl -X POST http://localhost:8001/api/long-term/analyze/NVDA
```

**Expected Output:**
- Industry Score: 88/100 (AI/semiconductor tailwinds)
- Valuation: P/E 60, but 25% DCF upside if AI adoption continues
- Fundamentals: Excellent (ROE 60%, Revenue +50%)
- Risk: High (Valuation risk, China exposure)
- Overall: **Buy** (strong fundamentals justify premium valuation IF growth continues)

### Example 2: Value Stock Analysis

```bash
curl -X POST http://localhost:8001/api/long-term/analyze/XOM
```

**Expected Output:**
- Industry Score: 35/100 (energy transition risk)
- Valuation: P/E 8, appears cheap
- Fundamentals: Moderate (declining revenue, high debt)
- Risk: Very High (structural decline, regulatory risk)
- Overall: **Avoid** (value trap, not genuine opportunity)

### Example 3: Portfolio Recommendations

```bash
curl -X GET "http://localhost:8001/api/long-term/portfolio-recommendations?min_score=75&limit=10"
```

**Returns:** Top 10 stocks rated "Buy" or "Strong Buy" with >75 overall score

---

## Best Practices

### For Stock Selection:

1. **Don't chase momentum** — Wait for technical confirmation of fundamental thesis
2. **Require margin of safety** — Target >15% DCF undervaluation for "Buy" rating
3. **Review risk factors** — Ensure you understand what could invalidate the thesis
4. **Monitor quarterly** — Track actual results vs. DCF assumptions
5. **Rebalance annually** — Update analysis with new data and adjust portfolio

### For Configuration:

1. **Conservative approach:** Higher min_annual_return (30-35%), higher fundamental weight
2. **Growth approach:** Lower min_annual_return (20%), higher industry/valuation weights
3. **Value approach:** Higher undervaluation requirement, stricter risk criteria
4. **Custom WACC:** Adjust based on your required rate of return (typically 8-12%)

### For Use Cases:

- **Long-term buy-and-hold:** Use "Buy" and "Strong Buy" classifications
- **Accumulation strategy:** Add to "Watchlist" on weakness
- **Tactical rebalancing:** Monitor analysis history to catch deterioration early
- **Portfolio screening:** Rank 100+ stocks to identify top candidates

---

## Integration with Prophet Platform

### Eddie's Watchlist Integration

The Long-Term Picker feeds recommendations to **Eddie's Watchlist**:

1. **Daily screening** runs at market close
2. **Highest-scored stocks** are added to watchlist
3. **Historical data** tracks how scores evolve
4. **Portfolio impact** displayed on dashboard

### Real-Time Monitoring

- Technical indicators update 5x daily
- Fundamental data refreshes quarterly (earnings)
- Analyst estimates update monthly
- Overall scores recalculated when data changes

---

## Database Schema

### LongTermInvestmentAnalysis Table

```sql
symbol              VARCHAR(20)    -- Stock ticker
company_name        VARCHAR(255)   -- Company name
industry            VARCHAR(100)   -- Industry classification
current_price       FLOAT          -- Current stock price
intrinsic_value     FLOAT          -- DCF-derived intrinsic value
undervaluation_pct  FLOAT          -- % undervalued
overall_score       FLOAT          -- 0-100 composite score
classification      ENUM           -- Strong Buy, Buy, Watchlist, Avoid
estimated_annual_return FLOAT      -- Expected % return
risk_score          FLOAT          -- Risk assessment 0-100
analysis_date       DATETIME       -- When analysis was performed
thesis              VARCHAR(1000)  -- Investment thesis
```

---

## Limitations & Caveats

1. **Historical data bias**: Past growth doesn't guarantee future growth
2. **DCF sensitivity**: Small changes in WACC/growth assumptions create large valuation changes
3. **Analyst herding**: Analyst targets often cluster and can be wrong
4. **Black swan events**: System cannot predict unpredictable events
5. **Market psychology**: Valuation multiples can remain irrational longer than fundamentals suggest
6. **Data quality**: Analysis only as good as underlying financial data

---

## Performance Monitoring

Track the system's actual picks against predictions:

```
Expected Return: 25%
Actual Return (6 months): 15%
Actual Return (1 year): 28%
```

Use this feedback to calibrate:
- DCF assumptions
- Risk thresholds
- Classification criteria
- Weight allocations

---

## Contact & Support

For questions about the Long-Term Picker methodology:
- See DASHBOARD_FEATURES.md for feature overview
- Review config examples in /backend/config/
- Check API logs for data issues

---

**Version**: 1.0  
**Last Updated**: August 2026  
**Status**: Production Ready
