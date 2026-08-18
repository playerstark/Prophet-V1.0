interface PnLData {
  realized_pnl: number
  unrealized_pnl: number
  total_pnl: number
  total_pnl_percent: number
  win_rate: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  best_trade: {
    symbol: string
    pnl: number
    pnl_percent: number
  } | null
  worst_trade: {
    symbol: string
    pnl: number
    pnl_percent: number
  } | null
}

interface PnLStatsProps {
  data: PnLData
}

export default function PnLStats({ data }: PnLStatsProps) {
  const formatCurrency = (value: number) => {
    const currency = '$'
    return `${currency}${value.toLocaleString('en-US', { maximumFractionDigits: 2 })}`
  }

  return (
    <div className="space-y-6">
      {/* Main P&L Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Total P&L Card */}
        <div className={`group relative rounded-xl p-8 border-2 transition-all duration-300 overflow-hidden ${
          data.total_pnl >= 0
            ? 'bg-gradient-to-br from-green-950 to-charcoal-800 border-green-500 hover:border-green-400 hover:shadow-[0_0_20px_rgba(34,197,94,0.3)]'
            : 'bg-gradient-to-br from-red-950 to-charcoal-800 border-red-500 hover:border-red-400 hover:shadow-[0_0_20px_rgba(239,68,68,0.3)]'
        }`}>
          <div className={`absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-5 transition-opacity duration-300 ${
            data.total_pnl >= 0 ? 'from-green-500 to-transparent' : 'from-red-500 to-transparent'
          }`}></div>
          <div className="relative z-10">
            <p className={`text-xs font-bold uppercase tracking-widest mb-3 ${data.total_pnl >= 0 ? 'text-green-300' : 'text-red-300'}`}>
              Total P&L
            </p>
            <div className="space-y-2">
              <p className={`text-4xl font-black ${data.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {data.total_pnl >= 0 ? '+' : ''}{formatCurrency(data.total_pnl)}
              </p>
              <p className={`text-lg font-bold ${data.total_pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {data.total_pnl_percent >= 0 ? '+' : ''}{data.total_pnl_percent.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>

        {/* Realized vs Unrealized */}
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-8 space-y-4">
          <p className="text-gold-300 text-xs font-bold uppercase tracking-widest mb-3">Breakdown</p>

          <div className="space-y-3">
            {/* Realized */}
            <div className="flex items-center justify-between p-3 bg-charcoal-900 rounded-lg border border-gold-500 border-opacity-20">
              <p className="text-gray-400 text-sm font-bold">Realized P&L</p>
              <p className={`text-lg font-black ${data.realized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {data.realized_pnl >= 0 ? '+' : ''}{formatCurrency(data.realized_pnl)}
              </p>
            </div>

            {/* Unrealized */}
            <div className="flex items-center justify-between p-3 bg-charcoal-900 rounded-lg border border-gold-500 border-opacity-20">
              <p className="text-gray-400 text-sm font-bold">Unrealized P&L</p>
              <p className={`text-lg font-black ${data.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {data.unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(data.unrealized_pnl)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Trade Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {/* Win Rate */}
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-4">
          <p className="text-gold-300 text-xs font-bold uppercase tracking-widest mb-2">Win Rate</p>
          <p className="text-3xl font-black text-gold-400">{data.win_rate.toFixed(1)}%</p>
          <p className="text-xs text-gray-400 mt-1">{data.winning_trades} of {data.total_trades}</p>
        </div>

        {/* Total Trades */}
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-4">
          <p className="text-gold-300 text-xs font-bold uppercase tracking-widest mb-2">Total Trades</p>
          <p className="text-3xl font-black text-gold-400">{data.total_trades}</p>
          <p className="text-xs text-gray-400 mt-1">Closed positions</p>
        </div>

        {/* Wins */}
        <div className="bg-gradient-to-br from-green-950 to-charcoal-800 border border-green-500 border-opacity-30 rounded-xl p-4">
          <p className="text-green-300 text-xs font-bold uppercase tracking-widest mb-2">Winning Trades</p>
          <p className="text-3xl font-black text-green-400">{data.winning_trades}</p>
        </div>

        {/* Losses */}
        <div className="bg-gradient-to-br from-red-950 to-charcoal-800 border border-red-500 border-opacity-30 rounded-xl p-4">
          <p className="text-red-300 text-xs font-bold uppercase tracking-widest mb-2">Losing Trades</p>
          <p className="text-3xl font-black text-red-400">{data.losing_trades}</p>
        </div>

        {/* Avg Win-Loss Ratio */}
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-4">
          <p className="text-gold-300 text-xs font-bold uppercase tracking-widest mb-2">Efficiency</p>
          <p className="text-3xl font-black text-gold-400">
            {data.total_trades > 0 ? (data.winning_trades / (data.total_trades || 1)).toFixed(2) : '0.00'}
          </p>
          <p className="text-xs text-gray-400 mt-1">Win/Total</p>
        </div>
      </div>

      {/* Best & Worst Trades */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Best Trade */}
        <div className="bg-gradient-to-br from-green-950 to-charcoal-800 border border-green-500 border-opacity-30 rounded-xl p-6">
          <p className="text-green-300 text-xs font-bold uppercase tracking-widest mb-4">🏆 Best Trade</p>
          {data.best_trade ? (
            <div>
              <p className="text-2xl font-black text-green-400">{data.best_trade.symbol}</p>
              <p className="text-lg font-bold text-green-300 mt-2">+{formatCurrency(data.best_trade.pnl)}</p>
              <p className="text-xs text-green-200 mt-1">+{data.best_trade.pnl_percent.toFixed(2)}% Return</p>
            </div>
          ) : (
            <p className="text-gray-400">No trades yet</p>
          )}
        </div>

        {/* Worst Trade */}
        <div className="bg-gradient-to-br from-red-950 to-charcoal-800 border border-red-500 border-opacity-30 rounded-xl p-6">
          <p className="text-red-300 text-xs font-bold uppercase tracking-widest mb-4">⚠️ Worst Trade</p>
          {data.worst_trade ? (
            <div>
              <p className="text-2xl font-black text-red-400">{data.worst_trade.symbol}</p>
              <p className="text-lg font-bold text-red-300 mt-2">{formatCurrency(data.worst_trade.pnl)}</p>
              <p className="text-xs text-red-200 mt-1">{data.worst_trade.pnl_percent.toFixed(2)}% Loss</p>
            </div>
          ) : (
            <p className="text-gray-400">No losing trades</p>
          )}
        </div>
      </div>
    </div>
  )
}
