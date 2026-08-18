# Long-Term Picker Engine - Quick Start Guide

## What's Been Implemented

A complete **Long-Term Stock Selection System** that combines:

✅ **Comprehensive Stock Analysis Engine**
- DCF valuation modeling
- Industry attractiveness scoring
- Fundamental quality assessment
- Risk analysis framework
- Technical confirmation (secondary)
- Analyst estimate integration
- Investment thesis generation

✅ **Intelligent Scoring & Classification**
- 8 component scores combining into overall composite score
- Classification: Strong Buy / Buy / Watchlist / Avoid
- Fully configurable weights and thresholds

✅ **RESTful API** for integration
- Analyze single stocks
- Rank portfolios
- Get recommendations
- Track analysis history
- Configure parameters

✅ **Database Integration**
- Persistent storage of all analyses
- Historical tracking for comparison
- Performance monitoring over time

---

## How to Use

### 1. Analyze a Single Stock

```bash
curl -X POST http://localhost:8001/api/long-term/analyze/AAPL
```

**You get:**
- Complete fundamental analysis (Revenue, FCF, ROE, Debt)
- DCF valuation with intrinsic value
- Undervaluation percentage
- Risk assessment with specific risk factors
- Technical indicators & confirmation
- Expected annual return
- **Investment classification** (Strong Buy/Buy/Watchlist/Avoid)
- **Investment thesis** explaining why/why not

### 2. Rank a Portfolio

```bash
curl -X POST http://localhost:8001/api/long-term/rank \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]}'
```

**Returns:** Stocks ranked by overall score, with scores for each category

### 3. Get Portfolio Recommendations

```bash
curl -X GET "http://localhost:8001/api/long-term/portfolio-recommendations?min_score=75&limit=10"
```

**Returns:** Your current top 10 "Buy" or "Strong Buy" recommendations

### 4. Configure the Engine

View current configuration:
```bash
curl -X GET http://localhost:8001/api/long-term/config
```

Update configuration:
```bash
curl -X POST http://localhost:8001/api/long-term/config \
  -H "Content-Type: application/json" \
  -d '{
    "min_annual_return": 0.30,
    "weights": {
      "industry": 0.15,
      "fundamental": 0.35,
      "valuation": 0.30,
      "risk": 0.20
    },
    "dcf": {
      "revenue_growth_rates": [0.20, 0.15, 0.12, 0.10, 0.08],
      "fcf_margin": 0.18,
      "wacc": 0.08
    }
  }'
```

---

## What Each Score Means

### Industry Score (0-100)
- **85+**: Structurally attractive (Tech, Healthcare)
- **60-85**: Average industry dynamics
- **<60**: Headwinds or declining industries

### Fundamental Quality (0-100)
- **85+**: Excellent revenue growth, high ROE, low debt
- **70-85**: Good fundamentals, solid business
- **50-70**: Average business quality
- **<50**: Deteriorating fundamentals or high leverage

### DCF Valuation Score (0-100)
- **90+**: >30% undervalued
- **70-90**: 10-30% undervalued (good value)
- **50-70**: Fairly valued to slightly undervalued
- **<50**: Fully valued or overvalued

### Risk Score (0-100, **lower is better**)
- **<30**: Low risk (safe business)
- **30-50**: Moderate risk (acceptable for growth)
- **50-70**: Elevated risk (requires strong fundamentals)
- **>70**: High risk (typically Avoid)

### Technical Score (0-100)
- **80+**: Strong technical confirmation
- **50-80**: Neutral to positive technicals
- **<50**: Weak technicals (wait for reversal)

### Overall Score (Composite 0-100)
Weighted average of all factors. Classification:
- **>80**: Strong Buy
- **75-80**: Buy
- **60-75**: Watchlist
- **<60**: Avoid

---

## Investment Classifications Explained

### 🟢 **STRONG BUY** (Score >80, Return >37.5%)

**What it means:**
- Excellent fundamentals
- Significant undervaluation
- Low-to-moderate risk
- Strong long-term thesis
- High conviction recommendation

**Action:**
- **Priority allocation** for new capital
- Consider core portfolio position
- Monitor quarterly for thesis validation

**Example:** $AAPL trading 25% below intrinsic value with 10% revenue growth and 95% ROE

---

### 🟢 **BUY** (Score 75-80, Return 25-37.5%)

**What it means:**
- Good fundamentals
- Reasonable undervaluation
- Manageable risk profile
- Clear investment thesis
- Worth adding to portfolio

**Action:**
- Include in rebalancing
- Accumulate on weakness
- 3-5 year holding period

**Example:** $MSFT trading 18% below DCF value with strong cloud growth and solid balance sheet

---

### 🟡 **WATCHLIST** (Score 60-75, Return <25% or unclear)

**What it means:**
- Good business but not yet cheap enough
- OR strong thesis but waiting for confirmation
- OR good company but unclear execution
- Worth monitoring, not yet ready to buy

**Action:**
- Track quarterly earnings
- Wait for better entry point
- Consider small starter position
- Reassess after next earnings

**Example:** $GOOGL strong fundamentals but P/E high, waiting for weakness before adding

---

### 🔴 **AVOID** (Score <60, High risk or low return)

**What it means:**
- Fundamentals deteriorating
- Fully valued or overvalued
- High risk with limited upside
- Better opportunities exist
- Not recommended for long-term portfolio

**Action:**
- Do not buy or add
- Consider exiting if held
- Monitor for "Watchlist" reclassification
- Better opportunities elsewhere

**Example:** $XOM trading at fair value with declining revenue and $50B debt load

---

## Configuration Strategies

### Conservative (Safety First)
```json
{
  "min_annual_return": 0.35,  // Need strong upside
  "weights": {
    "fundamental": 0.40,      // Emphasize business quality
    "risk": 0.25,             // Heavy risk penalty
    "valuation": 0.20,
    "industry": 0.15
  },
  "dcf": {
    "wacc": 0.10,             // Higher discount rate
    "fcf_margin": 0.12        // Conservative margins
  }
}
```

### Growth (Balanced)
```json
{
  "min_annual_return": 0.25,
  "weights": {
    "fundamental": 0.35,
    "valuation": 0.30,
    "risk": 0.20,
    "industry": 0.15          // Growth industries
  },
  "dcf": {
    "wacc": 0.08,
    "fcf_margin": 0.15
  }
}
```

### Value (Deep Undervaluation)
```json
{
  "min_annual_return": 0.20,
  "weights": {
    "valuation": 0.40,        // Focus on cheap
    "fundamental": 0.35,
    "risk": 0.15,
    "industry": 0.10
  },
  "dcf": {
    "wacc": 0.09,
    "fcf_margin": 0.10        // Conservative growth
  }
}
```

---

## Typical Workflow

### Step 1: Initial Screening
```bash
# Get portfolio recommendations
curl http://localhost:8001/api/long-term/portfolio-recommendations

# Review the top 20 stocks
# Identify industry themes
```

### Step 2: Deep Dive Analysis
```bash
# Analyze your top candidates individually
curl -X POST http://localhost:8001/api/long-term/analyze/AAPL
curl -X POST http://localhost:8001/api/long-term/analyze/MSFT
curl -X POST http://localhost:8001/api/long-term/analyze/GOOGL

# Read the investment thesis for each
# Check the risk factors
# Verify DCF assumptions match your views
```

### Step 3: Validation
- Cross-check against latest earnings reports
- Verify analyst targets are recent
- Check if risk factors have changed
- Confirm your conviction in the thesis

### Step 4: Allocation
- "Strong Buy" = Highest priority allocation
- "Buy" = Core portfolio positions
- "Watchlist" = Monitor for entry opportunity
- "Avoid" = Don't buy or consider exiting

### Step 5: Monitoring
```bash
# Check analysis history quarterly
curl http://localhost:8001/api/long-term/history/AAPL

# Reanalyze annually
# Update portfolio based on changes
# Track actual vs. expected returns
```

---

## Key Metrics to Watch

When reviewing an analysis, focus on:

### 1. **Undervaluation %**
- Goal: >15% for "Buy" confidence
- Red flag: Cheap because fundamentals deteriorating
- Compare to: Historical P/E range

### 2. **Estimated Annual Return**
- Goal: >25% for long-term portfolio
- Validate: Does DCF assumption seem reasonable?
- Compare to: Analyst targets (should align)

### 3. **Revenue Growth**
- Goal: >10% for "Buy"
- Watch: Is growth sustainable? R&D spending?
- Risk: Is growth dependent on one product/customer?

### 4. **Free Cash Flow**
- Reality check: Does company actually generate cash?
- Compare to: Reported earnings (quality of earnings)
- Watch: CapEx requirements for future growth

### 5. **Debt-to-Equity**
- Goal: <1.5 for safety
- Risk: >2.0 is elevated leverage
- Industry dependent: Banks/REITs are naturally leveraged

### 6. **Risk Factors**
- Read each one carefully
- Ask: Is this a temporary or structural risk?
- Consider: Could this invalidate the entire thesis?

---

## Example: Full Analysis Flow

### Input
```bash
curl -X POST http://localhost:8001/api/long-term/analyze/MSFT
```

### Output Summary
```
Company: Microsoft Corp (Technology)
Current Price: $420.75
Intrinsic Value: $510.00 (21.2% undervalued)

FUNDAMENTALS:
  Revenue Growth: 12%
  ROE: 42%
  Debt-to-Equity: 0.65 ✓

VALUATION:
  P/E: 35 (vs industry 28)
  DCF Score: 78/100 (Good value)

TECHNICALS:
  RSI: 58 (neutral)
  Technical Score: 72/100

RISK:
  Risk Score: 35/100 (Low)
  Factors: Valuation premium, Cloud competition, China exposure

RETURN ESTIMATE:
  Annual Return: 28.5% (above 25% threshold)

OVERALL SCORE: 76.8/100

CLASSIFICATION: BUY ✓

THESIS:
"Microsoft is a technology leader positioned in a structurally 
attractive tech sector, trading at 21.2% discount to intrinsic 
value with an estimated 28.5% annual return potential, supported 
by 12% revenue growth and 42% ROE. Key risk: High valuation 
premium requires execution. Invalidated if: Cloud adoption slows 
or competition intensifies."
```

---

## Common Questions

**Q: Why should I trust a model over my own analysis?**
A: The model standardizes analysis and avoids emotional biases. Use it as a starting point, not the final word. Your judgment should override the model if you have contrary evidence.

**Q: Can I adjust the DCF assumptions?**
A: Yes! Use the `/config` endpoint to customize revenue growth, FCF margin, WACC, etc. based on your own estimates.

**Q: Why is a company ranked "Avoid" if it's growing?**
A: Growth alone doesn't guarantee investment returns. If a company is growing at 15% but already priced for 20% growth, it's not cheap. The model balances growth with valuation.

**Q: How often should I re-run analysis?**
A: Quarterly after earnings (fundamentals change), or whenever price moves >10% (valuation change).

**Q: Can the model predict stock price?**
A: No. It identifies undervaluation opportunities, but market sentiment controls short-term price. Long-term (3-5 years), valuation typically wins.

**Q: What if I disagree with the classification?**
A: Good! You can:
1. Update config weights to prioritize your preferences
2. Override based on proprietary research
3. Use "Watchlist" items that don't quite meet "Buy" criteria
4. Create separate watchlist for sectors you favor

---

## Next Steps

1. **Start with recommendations:**
   ```bash
   curl http://localhost:8001/api/long-term/portfolio-recommendations
   ```

2. **Analyze your target stocks:**
   ```bash
   curl -X POST http://localhost:8001/api/long-term/analyze/{SYMBOL}
   ```

3. **Customize for your risk profile:**
   ```bash
   curl -X POST http://localhost:8001/api/long-term/config -d '{...}'
   ```

4. **Build your portfolio** using Strong Buy and Buy ratings

5. **Monitor quarterly** with analysis history tracking

---

## File Locations

- **Core Engine**: `/backend/src/services/long_term_picker.py`
- **API Routes**: `/backend/src/routes/long_term.py`
- **Database Models**: `/backend/src/models.py` (LongTermInvestmentAnalysis table)
- **Full Documentation**: `/docs/LONG_TERM_PICKER.md`
- **This Guide**: `/docs/LONG_TERM_QUICKSTART.md`

---

**Happy investing! 📈**

Remember: The goal is sustainable, long-term wealth building through fundamentally sound companies at reasonable valuations. Avoid hype, focus on cash flow and growth, and stay disciplined.
