interface Analysis {
  symbol: string
  company_name: string
  industry: string
  current_price: number
  valuation: {
    pe_ratio: number | null
    forward_pe: number | null
    intrinsic_value: number | null
    undervaluation_pct: number | null
    dcf_score: number
  }
  fundamentals: {
    revenue_growth_3y: number | null
    fcf_margin: number | null
    debt_to_equity: number | null
    roe: number | null
    fundamental_quality_score: number
  }
  technical: {
    rsi: number | null
    adx: number | null
    momentum: number | null
    technical_score: number
  }
  risk: {
    factors: string[]
    risk_score: number
  }
  analyst: {
    target_price: number | null
    upside_pct: number | null
  }
  scoring: {
    industry_score: number
    overall_score: number
    estimated_annual_return: number
  }
  classification: string
  thesis: string
}

interface Props {
  analysis: Analysis
  onAddToPicks: () => void
  saved: boolean
}

const getClassificationColor = (classification: string) => {
  switch (classification.toLowerCase()) {
    case 'strong_buy':
      return 'bg-green-900 border-green-500 text-green-300'
    case 'buy':
      return 'bg-green-900 border-green-500 text-green-300'
    case 'watchlist':
      return 'bg-yellow-900 border-yellow-500 text-yellow-300'
    default:
      return 'bg-red-900 border-red-500 text-red-300'
  }
}

const getClassificationIcon = (classification: string) => {
  switch (classification.toLowerCase()) {
    case 'strong_buy':
      return '🟢'
    case 'buy':
      return '🟢'
    case 'watchlist':
      return '🟡'
    default:
      return '🔴'
  }
}

export default function LongTermAnalysisPanel({ analysis, onAddToPicks, saved }: Props) {
  const canAddToWatchlist = analysis.scoring.estimated_annual_return >= 20

  return (
    <div className="space-y-6">
      {/* Header with Classification */}
      <div className={`border-2 rounded-xl p-8 space-y-4 ${getClassificationColor(analysis.classification)}`}>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">{getClassificationIcon(analysis.classification)}</span>
              <h3 className="text-2xl font-black uppercase tracking-wide">{analysis.classification.replace('_', ' ')}</h3>
            </div>
            <p className="text-sm opacity-90">{analysis.company_name} • {analysis.industry}</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-black">${analysis.current_price.toFixed(2)}</p>
            <p className="text-sm opacity-90">Current Price</p>
          </div>
        </div>

        {/* Add to Watchlist Button */}
        {canAddToWatchlist && (
          <button
            onClick={onAddToPicks}
            disabled={saved}
            className={`w-full py-3 rounded-lg font-bold uppercase tracking-wider transition-colors ${
              saved
                ? 'bg-green-600 text-black cursor-default'
                : 'bg-gold-600 hover:bg-gold-700 text-black hover:scale-105 transform'
            }`}
          >
            {saved ? '✓ Added to Long-Term Picks' : '+ Add to Long-Term Picks'}
          </button>
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Valuation Analysis */}
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
          <h4 className="text-gold-500 font-black uppercase tracking-wider">💰 Valuation</h4>

          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">P/E Ratio</span>
              <span className="text-gold-300 font-bold">{analysis.valuation.pe_ratio?.toFixed(1) ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Forward P/E</span>
              <span className="text-gold-300 font-bold">{analysis.valuation.forward_pe?.toFixed(1) ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Intrinsic Value (DCF)</span>
              <span className="text-gold-300 font-bold">${analysis.valuation.intrinsic_value?.toFixed(2) ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center pt-3 border-t border-gold-500 border-opacity-20">
              <span className="text-gray-400">Undervaluation</span>
              <span className={`font-bold ${(analysis.valuation.undervaluation_pct ?? 0) > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {analysis.valuation.undervaluation_pct?.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">DCF Score</span>
              <span className="text-gold-300 font-bold">{analysis.valuation.dcf_score.toFixed(0)}/100</span>
            </div>
          </div>
        </div>

        {/* Fundamentals */}
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
          <h4 className="text-gold-500 font-black uppercase tracking-wider">📊 Fundamentals</h4>

          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Revenue Growth (3Y)</span>
              <span className="text-gold-300 font-bold">{analysis.fundamentals.revenue_growth_3y ? `${(analysis.fundamentals.revenue_growth_3y * 100).toFixed(1)}%` : 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">ROE</span>
              <span className="text-gold-300 font-bold">{analysis.fundamentals.roe ? `${(analysis.fundamentals.roe * 100).toFixed(1)}%` : 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Debt-to-Equity</span>
              <span className="text-gold-300 font-bold">{analysis.fundamentals.debt_to_equity?.toFixed(2) ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">FCF Margin</span>
              <span className="text-gold-300 font-bold">{analysis.fundamentals.fcf_margin ? `${(analysis.fundamentals.fcf_margin * 100).toFixed(1)}%` : 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center pt-3 border-t border-gold-500 border-opacity-20">
              <span className="text-gray-400">Quality Score</span>
              <span className="text-gold-300 font-bold">{analysis.fundamentals.fundamental_quality_score.toFixed(0)}/100</span>
            </div>
          </div>
        </div>

        {/* Technical Analysis */}
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
          <h4 className="text-gold-500 font-black uppercase tracking-wider">📈 Technical</h4>

          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">RSI (14)</span>
              <span className="text-gold-300 font-bold">{analysis.technical.rsi?.toFixed(1) ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">ADX (14)</span>
              <span className="text-gold-300 font-bold">{analysis.technical.adx?.toFixed(1) ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Momentum</span>
              <span className={`font-bold ${(analysis.technical.momentum ?? 0) > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {analysis.technical.momentum?.toFixed(2) ?? 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center pt-3 border-t border-gold-500 border-opacity-20">
              <span className="text-gray-400">Technical Score</span>
              <span className="text-gold-300 font-bold">{analysis.technical.technical_score.toFixed(0)}/100</span>
            </div>
          </div>
        </div>

        {/* Risk Assessment */}
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
          <h4 className="text-gold-500 font-black uppercase tracking-wider">⚠️ Risk</h4>

          <div className="space-y-2">
            {analysis.risk.factors.slice(0, 4).map((factor, idx) => (
              <p key={idx} className="text-gray-400 text-sm">• {factor}</p>
            ))}
          </div>

          <div className="pt-4 border-t border-gold-500 border-opacity-20 flex justify-between items-center">
            <span className="text-gray-400">Risk Score</span>
            <span className={`font-bold ${analysis.risk.risk_score < 40 ? 'text-green-400' : analysis.risk.risk_score < 60 ? 'text-yellow-400' : 'text-red-400'}`}>
              {analysis.risk.risk_score.toFixed(0)}/100
            </span>
          </div>
        </div>
      </div>

      {/* Scoring Summary */}
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6">
        <h4 className="text-gold-500 font-black uppercase tracking-wider mb-6">🎯 Overall Score Breakdown</h4>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-2">Industry</p>
            <p className="text-3xl font-black text-gold-400">{analysis.scoring.industry_score.toFixed(0)}</p>
            <p className="text-xs text-gray-500 mt-1">/ 100</p>
          </div>
          <div className="text-center">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-2">Overall</p>
            <p className="text-3xl font-black text-gold-400">{analysis.scoring.overall_score.toFixed(1)}</p>
            <p className="text-xs text-gray-500 mt-1">/ 100</p>
          </div>
          <div className="text-center">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-2">Est. Return</p>
            <p className={`text-3xl font-black ${analysis.scoring.estimated_annual_return > 25 ? 'text-green-400' : analysis.scoring.estimated_annual_return > 20 ? 'text-yellow-400' : 'text-red-400'}`}>
              {analysis.scoring.estimated_annual_return.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">/ year</p>
          </div>
          <div className="text-center">
            <p className="text-gray-400 text-xs uppercase tracking-widest mb-2">Analyst Target</p>
            <p className="text-3xl font-black text-gold-400">{analysis.analyst.upside_pct?.toFixed(1) ?? 'N/A'}%</p>
            <p className="text-xs text-gray-500 mt-1">upside</p>
          </div>
        </div>
      </div>

      {/* Investment Thesis */}
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-8 space-y-4">
        <h4 className="text-gold-500 font-black uppercase tracking-wider">💡 Investment Thesis</h4>
        <p className="text-gray-300 leading-relaxed">{analysis.thesis}</p>
      </div>

      {/* Recommendation Footer */}
      <div className={`rounded-xl p-6 text-center space-y-2 ${
        analysis.classification.toLowerCase() === 'strong_buy'
          ? 'bg-green-900 border border-green-500 text-green-100'
          : analysis.classification.toLowerCase() === 'buy'
          ? 'bg-green-900 border border-green-500 text-green-100'
          : analysis.classification.toLowerCase() === 'watchlist'
          ? 'bg-yellow-900 border border-yellow-500 text-yellow-100'
          : 'bg-red-900 border border-red-500 text-red-100'
      }`}>
        <p className="font-bold text-lg">
          {analysis.classification === 'strong_buy'
            ? '✓ Strong conviction buy - excellent fundamentals and valuation'
            : analysis.classification === 'buy'
            ? '✓ Recommended for long-term portfolio - good value'
            : analysis.classification === 'watchlist'
            ? '⊘ Monitor for better entry point or thesis confirmation'
            : '✗ Not recommended - avoid at current valuation'}
        </p>
      </div>
    </div>
  )
}
