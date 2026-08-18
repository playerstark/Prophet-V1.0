interface StockData {
  symbol: string
  market: string
  current_price: number
  rsi: number
  adx: number
  momentum: number
  news: Array<{
    title: string
    sentiment: string
    source: string
    url?: string
  }>
}

interface IndicatorPanelProps {
  data: StockData
}

export default function IndicatorPanel({ data }: IndicatorPanelProps) {
  const getRSIStatus = (rsi: number) => {
    if (rsi > 70) return { label: 'Overbought', color: 'text-red-400', bg: 'bg-red-950' }
    if (rsi < 30) return { label: 'Oversold', color: 'text-green-400', bg: 'bg-green-950' }
    return { label: 'Neutral', color: 'text-gray-400', bg: 'bg-gray-900' }
  }

  const getADXStrength = (adx: number) => {
    if (adx >= 25) return { label: 'Strong Trend', color: 'text-gold-400' }
    if (adx >= 20) return { label: 'Fair Trend', color: 'text-yellow-400' }
    return { label: 'Weak Trend', color: 'text-gray-400' }
  }

  const getMomentumDirection = (momentum: number) => {
    if (momentum > 0) return { label: 'Bullish', color: 'text-green-400', icon: '📈' }
    if (momentum < 0) return { label: 'Bearish', color: 'text-red-400', icon: '📉' }
    return { label: 'Neutral', color: 'text-gray-400', icon: '➡️' }
  }

  const rsiStatus = getRSIStatus(data.rsi)
  const adxStatus = getADXStrength(data.adx)
  const momentumStatus = getMomentumDirection(data.momentum)

  return (
    <div className="space-y-4">
      {/* Indicators */}
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
        <h3 className="text-gold-500 font-bold uppercase text-sm tracking-wider">📊 Technical Indicators</h3>

        {/* RSI */}
        <div className={`${rsiStatus.bg} rounded-lg p-4 border border-gold-500 border-opacity-20`}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-xs uppercase tracking-widest">RSI (14)</p>
            <span className={`text-xs font-bold px-2 py-1 rounded ${rsiStatus.color}`}>{rsiStatus.label}</span>
          </div>
          <div className="flex items-end gap-3">
            <p className="text-3xl font-black text-gold-400">{data.rsi.toFixed(1)}</p>
            <div className="flex-1">
              <div className="w-full bg-charcoal-900 rounded h-2">
                <div
                  className={`h-2 rounded ${data.rsi > 70 ? 'bg-red-500' : data.rsi < 30 ? 'bg-green-500' : 'bg-gold-500'}`}
                  style={{ width: `${Math.min(100, (data.rsi / 100) * 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>50</span>
                <span>100</span>
              </div>
            </div>
          </div>
        </div>

        {/* ADX */}
        <div className="bg-charcoal-900 rounded-lg p-4 border border-gold-500 border-opacity-20">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-xs uppercase tracking-widest">ADX (14)</p>
            <span className={`text-xs font-bold ${adxStatus.color}`}>{adxStatus.label}</span>
          </div>
          <div className="flex items-end gap-3">
            <p className="text-3xl font-black text-gold-400">{data.adx.toFixed(1)}</p>
            <div className="flex-1">
              <div className="w-full bg-charcoal-800 rounded h-2">
                <div
                  className="h-2 rounded bg-gold-500"
                  style={{ width: `${Math.min(100, (data.adx / 50) * 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>25</span>
                <span>50</span>
              </div>
            </div>
          </div>
        </div>

        {/* Momentum */}
        <div className="bg-charcoal-900 rounded-lg p-4 border border-gold-500 border-opacity-20">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-xs uppercase tracking-widest">Momentum</p>
            <span className={`text-xs font-bold ${momentumStatus.color}`}>{momentumStatus.icon} {momentumStatus.label}</span>
          </div>
          <p className={`text-3xl font-black ${data.momentum >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {data.momentum >= 0 ? '+' : ''}{data.momentum.toFixed(2)}
          </p>
        </div>
      </div>

      {/* News & Sentiment */}
      {data.news && data.news.length > 0 && (
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-3">
          <h3 className="text-gold-500 font-bold uppercase text-sm tracking-wider">📰 Latest News</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {data.news.slice(0, 5).map((item, idx) => (
              <div key={idx} className="bg-charcoal-900 rounded p-3 border border-gold-500 border-opacity-10">
                <p className="text-gray-300 text-xs leading-tight mb-1">{item.title}</p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">{item.source}</span>
                  <span className={`px-2 py-0.5 rounded text-white font-bold ${
                    item.sentiment === 'positive' ? 'bg-green-700' :
                    item.sentiment === 'negative' ? 'bg-red-700' :
                    'bg-gray-700'
                  }`}>
                    {item.sentiment}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
