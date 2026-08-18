# Configuration Guide - Long-Term Stock Picker

Quick reference for configuring the model to match your investment style and risk tolerance.

## Quick Start Presets

### 1. Conservative (Capital Preservation)

For investors prioritizing downside protection and quality:

```python
config = {
    'min_annual_return': 0.30,  # High hurdle rate
    'watchlist_return_threshold': 0.20,
    'score_weights': {
        'industry': 0.15,
        'fundamental': 0.40,      # ⬆️ Highest weight
        'valuation': 0.20,         # ⬇️ Lower weight
        'technical': 0.10,
        'risk_adjustment': 0.15,   # ⬆️ Higher weight
    },
    'dcf_wacc': 0.09,             # ⬆️ Higher discount rate = conservative
    'dcf_terminal_growth': 0.02,  # Lower terminal growth
    'quality_threshold': 50,
    'high_growth_threshold': 0.12,
}
```

**Effect**: Favors high-quality stable companies, requires steep discount to valuation, rejects risky bets.

### 2. Balanced (Default)

For investors seeking moderate risk/reward:

```python
config = {
    'min_annual_return': 0.25,
    'watchlist_return_threshold': 0.15,
    'score_weights': {
        'industry': 0.15,
        'fundamental': 0.35,       # Balanced weight
        'valuation': 0.30,         # Balanced weight
        'technical': 0.10,
        'risk_adjustment': 0.10,
    },
    'dcf_wacc': 0.08,              # Standard discount rate
    'dcf_terminal_growth': 0.025,
    'quality_threshold': 40,
    'high_growth_threshold': 0.15,
}
```

**Effect**: Equal balance between fundamentals and valuation, standard risk assessment, wide net.

### 3. Growth (Capital Appreciation)

For investors seeking higher returns, accepting moderate risk:

```python
config = {
    'min_annual_return': 0.20,    # Lower hurdle rate
    'watchlist_return_threshold': 0.10,
    'score_weights': {
        'industry': 0.15,
        'fundamental': 0.30,       # Lower weight
        'valuation': 0.40,         # ⬆️ Highest weight
        'technical': 0.12,
        'risk_adjustment': 0.08,   # ⬇️ Lower weight
    },
    'dcf_wacc': 0.07,              # ⬇️ Lower discount rate = optimistic
    'dcf_terminal_growth': 0.03,   # Higher terminal growth
    'quality_threshold': 30,
    'high_growth_threshold': 0.18,
}
```

**Effect**: Emphasizes valuation upside, accepts lower quality if undervalued, targets growth stocks.

### 4. Aggressive (High Growth)

For investors seeking maximum capital appreciation, higher risk tolerance:

```python
config = {
    'min_annual_return': 0.15,
    'watchlist_return_threshold': 0.05,
    'score_weights': {
        'industry': 0.10,          # Lower weight
        'fundamental': 0.25,       # Lower weight
        'valuation': 0.45,         # ⬆️ Highest weight
        'technical': 0.15,         # Higher weight for momentum
        'risk_adjustment': 0.05,   # ⬇️ Minimal risk constraint
    },
    'dcf_wacc': 0.06,
    'dcf_terminal_growth': 0.035,
    'quality_threshold': 20,
    'high_growth_threshold': 0.20,
}
```

**Effect**: Focuses on finding undervalued growth stories, minimal quality filter, high upside bias.

---

## Parameter Explanations

### Return Thresholds

#### `min_annual_return` (0.0 - 1.0)
**What it does**: Minimum expected annual return required for "Buy" classification

**Effect on analysis**:
- `0.15` (15%): Easy to reach "Buy" - accepts more marginal opportunities
- `0.25` (25%): Standard - good long-term baseline
- `0.35` (35%): Strict - rejects most stocks, only best opportunities
- `0.50` (50%): Very strict - ultra-selective, likely to miss good buys

**Recommendation**:
- Conservative: 0.30 - 0.35
- Balanced: 0.25
- Growth: 0.20 - 0.25
- Aggressive: 0.15 - 0.20

#### `watchlist_return_threshold` (0.0 - 1.0)
**What it does**: Minimum return for "Watchlist" classification

**Effect**: Should be 50-60% of min_annual_return

**Example**: If min is 25%, watchlist threshold should be 12-15%

---

### Scoring Weights

#### `fundamental` (Quality Score)
Weight for fundamental analysis (revenue growth, ROE, margins, debt levels)

**0.25**: De-emphasize fundamentals, focus on valuation
**0.35**: Standard weight, fundamentals important
**0.45+**: Emphasize quality, prefer stable over growth

**Use Case**:
- High weight: Dividend investors, quality-focused
- Low weight: Value investors, turnaround plays

#### `valuation` (DCF & Multiples)
Weight for valuation analysis (DCF, P/E, undervaluation %)

**0.20**: Minimal valuation filter, price matters less
**0.30**: Standard weight, balanced
**0.40+**: Emphasize valuation, seek steep discounts

**Use Case**:
- High weight: Value investors, deep discount focus
- Low weight: Growth investors, accept premium valuation

#### `industry` (Structural Opportunity)
Weight for industry attractiveness

**0.10**: Industry doesn't matter much
**0.15**: Standard - ensure positive industry tailwinds
**0.20+**: Require strong industry, avoid declining sectors

**Use Case**:
- High weight: Sector rotators, thematic investors
- Low weight: Stock-pickers, ignore macro

#### `technical` (Confirmation Layer)
Weight for technical indicators (RSI, ADX, momentum)

**0.05**: Minimal technical emphasis
**0.10**: Standard - confirmation only
**0.15+**: Strong technical requirement

**Use Case**:
- High weight: Momentum traders, trend followers
- Low weight: Fundamentalists, ignore technicals

#### `risk_adjustment` (Risk Profile)
Weight for risk assessment and downside protection

**0.05**: Minimal risk filter
**0.10**: Standard - reject only highest risk
**0.15+**: Strong risk filter, capital preservation focus

**Use Case**:
- High weight: Conservative, capital preservation
- Low weight: Aggressive, accept volatility

### DCF Parameters

#### `dcf_wacc` (0.05 - 0.12)
Weighted Average Cost of Capital - discount rate used in DCF

**What it represents**: The required rate of return on equity

**Lower WACC → Higher valuations**:
- 0.06: Optimistic assumptions, higher intrinsic values
- 0.08: Standard assumption
- 0.10: Conservative, lower intrinsic values

**How to think about it**:
- S&P 500 historical return: ~10%
- Risk-free rate (T-bills): ~5%
- Stock-specific risk premium: +1-3%
- So typical WACC: 7-9%

**Use Case**:
- Conservative: 0.09 - 0.11 (higher required return)
- Balanced: 0.08
- Growth: 0.07 - 0.08 (lower required return)

#### `dcf_terminal_growth` (0.01 - 0.04)
Long-term perpetual growth rate after explicit forecast period

**Constraints**: Must be less than WACC

**Meaning**:
- 0.02: Company grows at 2% forever (conservative)
- 0.025: Company grows at 2.5% forever (GDP-like growth)
- 0.03: Company grows at 3% forever (above GDP)
- 0.04: Company grows at 4% forever (optimistic)

**Use Case**:
- Conservative: 0.015 - 0.02
- Balanced: 0.025
- Growth: 0.03 - 0.035

### Quality Thresholds

#### `quality_threshold` (0 - 100)
Minimum fundamental quality score to consider stock

**Score breakdown**:
- 0-30: Poor quality, high risk
- 30-50: Acceptable, some concerns
- 50-70: Good quality, solid fundamentals
- 70+: Excellent quality, best-in-class

**Use Case**:
- Conservative: 50-60
- Balanced: 35-45
- Growth: 20-30
- Aggressive: 0-20

#### `high_growth_threshold` (0.0 - 0.50)
Minimum revenue growth rate to classify as "high growth"

**Affects**: Scoring and sector classification

**Common thresholds**:
- 0.10: 10% annual growth
- 0.15: 15% annual growth (typical high-growth threshold)
- 0.20: 20% annual growth (very high growth)

**Use Case**:
- Conservative: 0.12 - 0.15 (high bar for growth)
- Balanced: 0.15
- Growth: 0.18 - 0.25 (accept slower growth)

---

## Customization Examples

### Example 1: Small-Cap Value Investor

Looking for undervalued small-cap growth stocks:

```python
config = {
    'min_annual_return': 0.22,
    'score_weights': {
        'industry': 0.10,        # Industry less important
        'fundamental': 0.25,     # Pick good ones, not perfect
        'valuation': 0.45,       # EMPHASIZE VALUE
        'technical': 0.10,
        'risk_adjustment': 0.10,
    },
    'dcf_wacc': 0.10,            # Higher discount for small-cap risk
    'quality_threshold': 25,     # Allow imperfect companies
}
```

### Example 2: Tech-Focused Growth Investor

Investing in software, semiconductors, AI:

```python
config = {
    'min_annual_return': 0.20,
    'score_weights': {
        'industry': 0.20,        # EMPHASIZE TECH INDUSTRY TAILWINDS
        'fundamental': 0.30,     # Growth matters more than margins
        'valuation': 0.30,       # Accept premium on growth
        'technical': 0.12,       # Momentum matters
        'risk_adjustment': 0.08,
    },
    'dcf_wacc': 0.07,            # Optimistic for high-growth tech
    'high_growth_threshold': 0.20,  # Tech should grow faster
}
```

### Example 3: Income/Dividend Investor

Seeking stable companies with dividends:

```python
config = {
    'min_annual_return': 0.12,   # Lower return hurdle (focused on dividends)
    'score_weights': {
        'industry': 0.10,
        'fundamental': 0.50,     # EMPHASIZE QUALITY & STABILITY
        'valuation': 0.20,
        'technical': 0.05,
        'risk_adjustment': 0.15,
    },
    'dcf_wacc': 0.06,            # Stable mature companies, lower hurdle
    'quality_threshold': 70,     # ONLY BEST QUALITY
    'high_growth_threshold': 0.05,  # Accept slow growth
}
```

### Example 4: Contrarian Investor

Finding overlooked or out-of-favor stocks:

```python
config = {
    'min_annual_return': 0.25,
    'score_weights': {
        'industry': 0.05,         # Ignore industry trends
        'fundamental': 0.20,      # Might have deteriorated
        'valuation': 0.50,        # MASSIVE DISCOUNT REQUIRED
        'technical': 0.08,        # Ignore momentum
        'risk_adjustment': 0.17,  # Higher risk tolerance
    },
    'dcf_wacc': 0.07,             # Assume recovery possible
    'quality_threshold': 15,      # Accept distressed situations
}
```

### Example 5: Portfolio Insurance / de-risking

Reducing exposure to risky stocks:

```python
config = {
    'min_annual_return': 0.30,   # HIGH BAR
    'score_weights': {
        'industry': 0.15,
        'fundamental': 0.40,
        'valuation': 0.15,        # Less emphasis on price
        'technical': 0.05,
        'risk_adjustment': 0.25,  # MAXIMUM RISK FILTER
    },
    'dcf_wacc': 0.10,             # CONSERVATIVE
    'quality_threshold': 70,      # ONLY HIGHEST QUALITY
}
```

---

## Dynamic Adjustment Strategy

### Quarterly Reviews

Adjust config based on market conditions:

```python
# Q1 2024: Risk-off environment
if market_volatility_high and credit_spreads_wide:
    config['dcf_wacc'] = 0.10  # Increase discount rate
    config['risk_adjustment'] = 0.15  # Stricter risk filter
    config['min_annual_return'] = 0.30  # Higher hurdle

# Q2 2024: Risk-on environment
elif market_optimism_high and credit_spreads_tight:
    config['dcf_wacc'] = 0.07  # Decrease discount rate
    config['risk_adjustment'] = 0.08  # Loosen risk filter
    config['min_annual_return'] = 0.20  # Lower hurdle
```

### Sector-Based Adjustments

Adjust weights based on rotation:

```python
# Favor tech: increase industry weight and lower quality threshold
# Favor value: increase valuation weight and WACC
# Favor growth: decrease WACC and increase technical weight
# Favor quality: increase quality_threshold
```

---

## Testing Your Configuration

### Step 1: Run against known stocks

Test your config against stocks you understand well:

```python
picker = LongTermStockPicker(config=your_config)

# Analyze familiar stocks
result = await picker.analyze_stock('MSFT')

# Does classification match your thesis?
# Is return estimate reasonable?
# Do component scores make sense?
```

### Step 2: Backtest with historical data

If you have historical data, verify:
- Did "Buy" signals outperform?
- Were return estimates accurate?
- Did "Avoid" signals protect against downside?

### Step 3: Sensitivity analysis

Test extremes:
- What happens if revenue growth is half?
- If margins compress 30%?
- If WACC rises 200bps?

---

## Common Mistakes to Avoid

1. **Too Many Constraints**: Combining all strictest settings = no stocks ever qualify
2. **Ignoring Risk**: Setting risk_adjustment too low leaves you exposed
3. **Unrealistic Returns**: Expecting 50%+ annual returns is unrealistic
4. **Over-Optimization**: Don't fine-tune to past performance ("overfitting")
5. **Ignoring Qualitative**: Model is tool, not oracle; still do due diligence

---

## Support

For questions about what config to use, refer to:
- `LONG_TERM_PICKER_DOCS.md` - Full documentation
- `long_term_picker_example.py` - Code examples
- Preset examples above - Starting points
