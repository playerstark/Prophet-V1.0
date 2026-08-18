import { formatDistanceToNow } from 'date-fns'

interface WatchlistEntry {
  id: number
  symbol: string
  horizon: string
  direction: string
  current_price: number
  rsi: number
  adx: number
  momentum: number
  volume_ratio: number
  breakout_timestamp: string | null
  market?: string
}

const formatPrice = (price: number, symbol: string): string => {
  const isIndian = symbol.includes('.NS') || symbol.includes('.BO')
  const currency = isIndian ? '₹' : '$'
  return `${currency}${price.toLocaleString('en-IN', { maximumFractionDigits: 2, minimumFractionDigits: 2 })}`
}

interface WatchlistLaneProps {
  title: string
  subtitle: string
  candidates: WatchlistEntry[]
  direction: 'long' | 'short'
  icon: string
  onSymbolClick?: (symbol: string) => void
}

export default function WatchlistLane({ title, subtitle, candidates, direction, icon, onSymbolClick }: WatchlistLaneProps) {
  const isLong = direction === 'long'
  const borderColor = isLong ? 'border-green-500' : 'border-red-500'
  const bgColor = isLong ? 'from-green-950' : 'from-red-950'
  const textAccent = isLong ? 'text-green-400' : 'text-red-400'
  const badgeColor = isLong ? 'bg-green-900' : 'bg-red-900'

  const getRSIStatus = (rsi: number) => {
    if (isLong && rsi < 30) return { label: 'Oversold ↑', color: 'text-green-400' }
    if (!isLong && rsi > 70) return { label: 'Overbought ↓', color: 'text-red-400' }
    return { label: 'Neutral', color: 'text-gray-400' }
  }

  const getADXStrength = (adx: number) => {
    if (adx >= 25) return { label: 'Strong', color: 'text-gold-400' }
    if (adx >= 20) return { label: 'Fair', color: 'text-yellow-400' }
    return { label: 'Weak', color: 'text-gray-400' }
  }

  return (
    <div className={`bg-gradient-to-br ${bgColor} to-charcoal-800 border ${borderColor} border-opacity-40 rounded-xl overflow-hidden`}>
      {/* Lane Header */}
      <div className={`px-6 py-4 border-b ${borderColor} border-opacity-30 bg-black bg-opacity-30`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{icon}</span>
            <div>
              <h3 className={`font-black text-lg tracking-wide ${textAccent}`}>{title}</h3>
              <p className="text-gray-400 text-xs">{subtitle}</p>
            </div>
          </div>
          <div className={`text-4xl font-black ${textAccent}`}>{candidates.length}</div>
        </div>
      </div>

      {/* Candidates Table */}
      {candidates.length === 0 ? (
        <div className="px-6 py-12 text-center">
          <p className="text-gray-400">No {direction} setups detected at the moment</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className={`bg-black bg-opacity-30 border-b ${borderColor} border-opacity-20`}>
                <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Symbol</th>
                <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Price</th>
                <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">RSI</th>
                <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">ADX</th>
                <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Momentum</th>
                <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Vol Ratio</th>
                <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Breakout</th>
                <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Horizon</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((entry) => {
                const rsiStatus = getRSIStatus(entry.rsi)
                const adxStrength = getADXStrength(entry.adx)
                const timeAgo = entry.breakout_timestamp ? formatDistanceToNow(new Date(entry.breakout_timestamp), { addSuffix: true }) : 'N/A'

                return (
                  <tr
                    key={entry.id}
                    onClick={() => onSymbolClick?.(entry.symbol)}
                    className={`border-b ${borderColor} border-opacity-20 hover:bg-black hover:bg-opacity-30 transition-colors ${onSymbolClick ? 'cursor-pointer' : ''}`}
                  >
                    <td className="px-4 py-3">
                      <span className="font-bold text-gold-400">{entry.symbol}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-bold ${textAccent}`}>{formatPrice(entry.current_price, entry.symbol)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-300">{entry.rsi.toFixed(1)}</span>
                        <span className={`text-xs font-bold ${rsiStatus.color}`}>{rsiStatus.label}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-300">{entry.adx.toFixed(1)}</span>
                        <span className={`text-xs font-bold ${adxStrength.color}`}>{adxStrength.label}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-bold ${entry.momentum >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {entry.momentum.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-bold ${entry.volume_ratio >= 1 ? 'text-green-400' : 'text-orange-400'}`}>
                        {entry.volume_ratio.toFixed(2)}x
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{timeAgo}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-bold px-2 py-1 rounded ${badgeColor} text-white uppercase`}>
                        {entry.horizon}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
