interface FinancialMetrics {
  pe_ratio?: number
  forward_pe?: number
  price_to_book?: number
  eps?: number
  dividend_yield?: number
  debt_to_equity?: number
  return_on_equity?: number
  profit_margin?: number
  revenue_per_share?: number
  market_cap?: number
  fifty_two_week_high?: number
  fifty_two_week_low?: number
}

interface Props {
  metrics: FinancialMetrics
  symbol: string
  currentPrice: number
}

const formatMetric = (value: number | undefined): string => {
  if (value === undefined || value === null) return 'N/A'
  if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(2)}B`
  if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(2)}M`
  if (value % 1 === 0) return value.toString()
  return value.toFixed(2)
}

const formatPercent = (value: number | undefined): string => {
  if (value === undefined || value === null) return 'N/A'
  return `${(value * 100).toFixed(2)}%`
}

export default function StockFinancialMetrics({ metrics, currentPrice }: Props) {
  return (
    <div className="space-y-6">
      {/* Valuation Metrics */}
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6">
        <h3 className="text-gold-500 font-bold uppercase text-sm tracking-wider mb-4">💰 Valuation</h3>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">P/E Ratio</p>
            <p className="text-xl font-bold text-gold-400">{formatMetric(metrics.pe_ratio)}</p>
            <p className="text-gray-500 text-xs mt-1">Trailing</p>
          </div>

          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">Forward P/E</p>
            <p className="text-xl font-bold text-gold-400">{formatMetric(metrics.forward_pe)}</p>
            <p className="text-gray-500 text-xs mt-1">Next 12M</p>
          </div>

          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">P/B Ratio</p>
            <p className="text-xl font-bold text-gold-400">{formatMetric(metrics.price_to_book)}</p>
            <p className="text-gray-500 text-xs mt-1">Book Value</p>
          </div>

          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">EPS</p>
            <p className="text-xl font-bold text-green-400">${formatMetric(metrics.eps)}</p>
            <p className="text-gray-500 text-xs mt-1">Earnings</p>
          </div>

          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">Div Yield</p>
            <p className="text-xl font-bold text-blue-400">{formatPercent(metrics.dividend_yield)}</p>
            <p className="text-gray-500 text-xs mt-1">Annual</p>
          </div>

          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">Market Cap</p>
            <p className="text-xl font-bold text-purple-400">{formatMetric(metrics.market_cap)}</p>
            <p className="text-gray-500 text-xs mt-1">Total</p>
          </div>
        </div>
      </div>

      {/* Profitability & Efficiency */}
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6">
        <h3 className="text-gold-500 font-bold uppercase text-sm tracking-wider mb-4">📈 Profitability</h3>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">Profit Margin</p>
            <p className="text-xl font-bold text-green-400">{formatPercent(metrics.profit_margin)}</p>
            <p className="text-gray-500 text-xs mt-1">Net</p>
          </div>

          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">ROE</p>
            <p className="text-xl font-bold text-green-400">{formatPercent(metrics.return_on_equity)}</p>
            <p className="text-gray-500 text-xs mt-1">Equity Return</p>
          </div>

          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">D/E Ratio</p>
            <p className="text-xl font-bold text-yellow-400">{formatMetric(metrics.debt_to_equity)}</p>
            <p className="text-gray-500 text-xs mt-1">Leverage</p>
          </div>

          <div className="bg-charcoal-900 rounded-lg p-3">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">Revenue/Share</p>
            <p className="text-xl font-bold text-blue-400">${formatMetric(metrics.revenue_per_share)}</p>
            <p className="text-gray-500 text-xs mt-1">Annual</p>
          </div>
        </div>
      </div>

      {/* 52-Week Range */}
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6">
        <h3 className="text-gold-500 font-bold uppercase text-sm tracking-wider mb-4">📊 52-Week Range</h3>

        <div className="space-y-3">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-gray-400 text-sm">Low</span>
              <span className="text-gold-400 font-bold">${formatMetric(metrics.fifty_two_week_low)}</span>
            </div>
            <div className="w-full bg-charcoal-900 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-gold-600 to-gold-400 h-2 rounded-full"
                style={{
                  width: `${
                    metrics.fifty_two_week_high && metrics.fifty_two_week_low
                      ? ((currentPrice - metrics.fifty_two_week_low) /
                          (metrics.fifty_two_week_high - metrics.fifty_two_week_low)) *
                        100
                      : 50
                  }%`,
                }}
              />
            </div>
            <div className="flex justify-between mt-2">
              <span className="text-gray-400 text-sm">High</span>
              <span className="text-gold-400 font-bold">${formatMetric(metrics.fifty_two_week_high)}</span>
            </div>
          </div>
          <div className="text-center">
            <p className="text-gray-400 text-xs">Current: <span className="text-gold-400 font-bold">${currentPrice.toFixed(2)}</span></p>
          </div>
        </div>
      </div>
    </div>
  )
}
