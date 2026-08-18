interface TradeParams {
  entry_price: number
  stop_loss: number
  target_price: number
  reasoning: string
}

interface AISuggestionPanelProps {
  params: TradeParams
  symbol: string
  market: string
  onExecute: () => void
}

const formatPrice = (price: number, market: string): string => {
  const currency = market === 'IN' ? '₹' : '$'
  return `${currency}${price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
}

export default function AISuggestionPanel({ params, market, onExecute }: AISuggestionPanelProps) {
  const riskReward = (params.target_price - params.entry_price) / (params.entry_price - params.stop_loss)
  const potentialProfit = ((params.target_price - params.entry_price) / params.entry_price * 100)
  const potentialLoss = ((params.entry_price - params.stop_loss) / params.entry_price * 100)

  return (
    <div className="bg-gradient-to-br from-gold-950 to-charcoal-800 border-2 border-gold-500 rounded-xl p-8 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h3 className="text-2xl font-black text-gold-500 tracking-wide">🤖 AI TRADE SUGGESTION</h3>
        <p className="text-gold-300 text-sm">DeepSeek V4 - Real-time market analysis and trade planning</p>
      </div>

      {/* Trade Parameters Grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Entry */}
        <div className="bg-gradient-to-br from-blue-950 to-charcoal-900 rounded-lg p-4 border border-blue-500 border-opacity-30">
          <p className="text-blue-300 text-xs font-bold uppercase tracking-widest mb-2">Entry Price</p>
          <p className="text-3xl font-black text-blue-400">{formatPrice(params.entry_price, market)}</p>
          <p className="text-xs text-blue-200 mt-1">Buy Zone</p>
        </div>

        {/* Stop Loss */}
        <div className="bg-gradient-to-br from-red-950 to-charcoal-900 rounded-lg p-4 border border-red-500 border-opacity-30">
          <p className="text-red-300 text-xs font-bold uppercase tracking-widest mb-2">Stop Loss</p>
          <p className="text-3xl font-black text-red-400">{formatPrice(params.stop_loss, market)}</p>
          <p className="text-xs text-red-200 mt-1">Risk Limit</p>
        </div>

        {/* Target */}
        <div className="bg-gradient-to-br from-green-950 to-charcoal-900 rounded-lg p-4 border border-green-500 border-opacity-30">
          <p className="text-green-300 text-xs font-bold uppercase tracking-widest mb-2">Target Price</p>
          <p className="text-3xl font-black text-green-400">{formatPrice(params.target_price, market)}</p>
          <p className="text-xs text-green-200 mt-1">Profit Target</p>
        </div>
      </div>

      {/* Risk-Reward Analysis */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gold-500 border-opacity-30">
        <div className="text-center">
          <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">Risk/Reward Ratio</p>
          <p className="text-2xl font-black text-gold-400">{riskReward.toFixed(2)}:1</p>
        </div>
        <div className="text-center">
          <p className="text-green-300 text-xs uppercase tracking-widest mb-1">Potential Gain</p>
          <p className={`text-2xl font-black ${potentialProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {potentialProfit >= 0 ? '+' : ''}{potentialProfit.toFixed(2)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-red-300 text-xs uppercase tracking-widest mb-1">Max Risk</p>
          <p className="text-2xl font-black text-red-400">-{potentialLoss.toFixed(2)}%</p>
        </div>
      </div>

      {/* Reasoning */}
      {params.reasoning && (
        <div className="bg-charcoal-900 rounded-lg p-4 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs font-bold uppercase tracking-widest mb-2">📋 Analysis Reasoning</p>
          <p className="text-gray-300 text-sm leading-relaxed">{params.reasoning}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4 pt-4 border-t border-gold-500 border-opacity-30">
        <button
          onClick={onExecute}
          className="flex-1 bg-gold-600 hover:bg-gold-700 text-black font-black py-3 rounded-lg uppercase text-sm tracking-wider transition-colors"
        >
          🎯 Execute Trade
        </button>
        <button
          className="flex-1 bg-charcoal-900 hover:bg-charcoal-800 text-gold-400 font-bold py-3 rounded-lg uppercase text-sm tracking-wider border border-gold-500 border-opacity-30 transition-colors"
        >
          📌 Save Setup
        </button>
      </div>

      {/* Disclaimer */}
      <p className="text-gray-500 text-xs text-center italic">
        ⚠️ AI suggestions are based on technical analysis and are not financial advice. Trade at your own risk.
      </p>
    </div>
  )
}
