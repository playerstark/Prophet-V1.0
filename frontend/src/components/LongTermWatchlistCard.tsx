interface Pick {
  id: number
  symbol: string
  direction: string
  current_price: number
  rsi: number
  adx: number
  momentum: number
  added_at: string
}

interface Props {
  picks: Pick[]
}

export default function LongTermWatchlistCard({ picks }: Props) {
  if (!picks || picks.length === 0) {
    return (
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-8">
        <h3 className="text-2xl font-black text-gold-500 mb-6 uppercase tracking-wide">Long-term Picks</h3>
        <p className="text-gray-400 text-center py-8">No picks available</p>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-8 hover:border-opacity-50 transition-all duration-300">
      <h3 className="text-2xl font-black text-gold-500 mb-6 uppercase tracking-wide">Long-term Picks ({picks.length})</h3>
      <div className="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
        {picks.map((pick) => (
          <div
            key={pick.id}
            className={`relative group rounded-lg p-4 border transition-all duration-300 overflow-hidden cursor-pointer ${
              pick.direction === 'long'
                ? 'bg-gradient-to-br from-green-950 to-charcoal-800 border-green-500 border-opacity-30 hover:border-opacity-100 hover:shadow-[0_0_15px_rgba(34,197,94,0.2)]'
                : 'bg-gradient-to-br from-red-950 to-charcoal-800 border-red-500 border-opacity-30 hover:border-opacity-100 hover:shadow-[0_0_15px_rgba(239,68,68,0.2)]'
            }`}
          >
            <div className={`absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-10 transition-opacity duration-300 ${
              pick.direction === 'long' ? 'from-green-500 to-transparent' : 'from-red-500 to-transparent'
            }`}></div>

            <div className="relative z-10">
              <div className="flex justify-between items-center mb-3">
                <span className="font-bold text-lg" style={{color: pick.direction === 'long' ? '#4ade80' : '#f87171'}}>
                  {pick.symbol}
                </span>
                <span className={`text-xs font-black px-2.5 py-1 rounded-full ${
                  pick.direction === 'long'
                    ? 'bg-green-900 bg-opacity-70 text-green-300'
                    : 'bg-red-900 bg-opacity-70 text-red-300'
                }`}>
                  {pick.direction === 'long' ? '📈 LONG' : '📉 SHORT'}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-black bg-opacity-30 rounded px-2 py-1.5">
                  <p className="text-gray-400 uppercase text-xs font-semibold mb-0.5">Price</p>
                  <p className="text-gold-300 font-bold">${pick.current_price.toFixed(2)}</p>
                </div>
                <div className="bg-black bg-opacity-30 rounded px-2 py-1.5">
                  <p className="text-gray-400 uppercase text-xs font-semibold mb-0.5">RSI</p>
                  <p className="text-gold-300 font-bold">{pick.rsi.toFixed(1)}</p>
                </div>
                <div className="bg-black bg-opacity-30 rounded px-2 py-1.5">
                  <p className="text-gray-400 uppercase text-xs font-semibold mb-0.5">ADX</p>
                  <p className="text-gold-300 font-bold">{pick.adx.toFixed(1)}</p>
                </div>
                <div className="bg-black bg-opacity-30 rounded px-2 py-1.5">
                  <p className="text-gray-400 uppercase text-xs font-semibold mb-0.5">Momentum</p>
                  <p className="text-gold-300 font-bold">{pick.momentum.toFixed(2)}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
