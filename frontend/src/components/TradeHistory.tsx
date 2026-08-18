interface Trade {
  id: number
  symbol: string
  horizon: string
  direction: string
  entry_price: number
  exit_price: number | null
  stop_loss: number
  target_price: number
  quantity: number
  status: string
  entry_time: string
  exit_time: string | null
  pnl: number | null
  pnl_percent: number | null
}

interface TradeHistoryProps {
  trades: Trade[]
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function TradeHistory({ trades }: TradeHistoryProps) {
  if (!trades || trades.length === 0) {
    return (
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-12 text-center">
        <p className="text-gold-500 text-lg font-bold mb-2">📋 Trade History</p>
        <p className="text-gray-400">No trades yet. Start executing trades to see them here.</p>
      </div>
    )
  }

  const closedTrades = trades.filter(t => t.status === 'closed')
  const openTrades = trades.filter(t => t.status === 'open')

  return (
    <div className="space-y-8">
      <h3 className="text-2xl font-black text-gold-500 tracking-wide">📊 Trade Log</h3>

      {/* Open Trades */}
      {openTrades.length > 0 && (
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gold-500 border-opacity-20 bg-black bg-opacity-30">
            <h4 className="text-gold-500 font-bold uppercase text-sm tracking-wider">🔴 Open Positions ({openTrades.length})</h4>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-black bg-opacity-30 border-b border-gold-500 border-opacity-20">
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Symbol</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Side</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Qty</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Entry</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">S/L</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Target</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Entry Time</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Horizon</th>
                </tr>
              </thead>
              <tbody>
                {openTrades.map((trade) => (
                  <tr key={trade.id} className="border-b border-gold-500 border-opacity-20 hover:bg-black hover:bg-opacity-20 transition-colors">
                    <td className="px-4 py-3 font-bold text-gold-400">{trade.symbol}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-bold px-2 py-1 rounded ${
                        trade.direction === 'long' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                      }`}>
                        {trade.direction === 'long' ? '📈 LONG' : '📉 SHORT'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-300">{trade.quantity}</td>
                    <td className="px-4 py-3 text-gray-300">${trade.entry_price.toFixed(2)}</td>
                    <td className="px-4 py-3 text-red-400 font-bold">${trade.stop_loss.toFixed(2)}</td>
                    <td className="px-4 py-3 text-green-400 font-bold">${trade.target_price.toFixed(2)}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{formatDate(trade.entry_time)}</td>
                    <td className="px-4 py-3">
                      <span className="text-xs font-bold text-gold-300 uppercase">{trade.horizon}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Closed Trades */}
      {closedTrades.length > 0 && (
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gold-500 border-opacity-20 bg-black bg-opacity-30">
            <h4 className="text-gold-500 font-bold uppercase text-sm tracking-wider">✅ Closed Trades ({closedTrades.length})</h4>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-black bg-opacity-30 border-b border-gold-500 border-opacity-20">
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Symbol</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Side</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Entry</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Exit</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">P&L</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Return %</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Duration</th>
                  <th className="px-4 py-3 text-left text-gold-300 font-bold uppercase text-xs tracking-widest">Horizon</th>
                </tr>
              </thead>
              <tbody>
                {closedTrades.map((trade) => {
                  const duration = trade.exit_time
                    ? Math.round((new Date(trade.exit_time).getTime() - new Date(trade.entry_time).getTime()) / (1000 * 60 * 60 * 24))
                    : 0
                  const isProfit = trade.pnl && trade.pnl >= 0

                  return (
                    <tr
                      key={trade.id}
                      className={`border-b border-gold-500 border-opacity-20 hover:bg-black hover:bg-opacity-20 transition-colors ${
                        isProfit ? 'bg-green-950 bg-opacity-20' : 'bg-red-950 bg-opacity-20'
                      }`}
                    >
                      <td className="px-4 py-3 font-bold text-gold-400">{trade.symbol}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs font-bold px-2 py-1 rounded ${
                          trade.direction === 'long' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                        }`}>
                          {trade.direction === 'long' ? '📈' : '📉'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-300">${trade.entry_price.toFixed(2)}</td>
                      <td className="px-4 py-3 text-gray-300">${trade.exit_price?.toFixed(2) || 'N/A'}</td>
                      <td className="px-4 py-3 font-bold">
                        <span className={isProfit ? 'text-green-400' : 'text-red-400'}>
                          {isProfit && trade.pnl ? '+' : ''}{trade.pnl?.toFixed(2) || 'N/A'}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-bold">
                        <span className={isProfit ? 'text-green-400' : 'text-red-400'}>
                          {isProfit && trade.pnl_percent ? '+' : ''}{trade.pnl_percent?.toFixed(2) || 'N/A'}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-xs">{duration} days</td>
                      <td className="px-4 py-3 text-xs font-bold text-gold-300 uppercase">{trade.horizon}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
