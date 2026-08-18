interface Holding {
  id: number
  symbol: string
  quantity: number
  average_price: number
  current_price: number
  market_value: number
  unrealised_pnl: number
  unrealised_pnl_percent: number
}

interface Props {
  holdings: Holding[]
}

export default function HoldingsCard({ holdings }: Props) {
  if (!holdings || holdings.length === 0) {
    return (
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-8">
        <h3 className="text-2xl font-black text-gold-500 mb-4 uppercase tracking-wide">Current Holdings</h3>
        <p className="text-gray-400 text-center py-8">No active holdings</p>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-8 hover:border-opacity-50 transition-all duration-300">
      <h3 className="text-2xl font-black text-gold-500 mb-6 uppercase tracking-wide">Current Holdings ({holdings.length})</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-gold-500 border-opacity-50">
              <th className="text-left py-3 px-4 text-gold-400 font-bold uppercase text-xs tracking-wider">Symbol</th>
              <th className="text-right py-3 px-4 text-gold-400 font-bold uppercase text-xs tracking-wider">Qty</th>
              <th className="text-right py-3 px-4 text-gold-400 font-bold uppercase text-xs tracking-wider">Avg Price</th>
              <th className="text-right py-3 px-4 text-gold-400 font-bold uppercase text-xs tracking-wider">Current</th>
              <th className="text-right py-3 px-4 text-gold-400 font-bold uppercase text-xs tracking-wider">Value</th>
              <th className="text-right py-3 px-4 text-gold-400 font-bold uppercase text-xs tracking-wider">P&L</th>
              <th className="text-right py-3 px-4 text-gold-400 font-bold uppercase text-xs tracking-wider">%</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((holding, idx) => (
              <tr key={holding.id} className={`border-b border-gray-700 border-opacity-50 hover:bg-charcoal-600 hover:bg-opacity-50 transition-colors duration-200 ${
                idx % 2 === 0 ? 'bg-charcoal-800 bg-opacity-30' : ''
              }`}>
                <td className="py-4 px-4 font-bold text-gold-300">{holding.symbol}</td>
                <td className="text-right py-4 px-4 text-gray-200 font-semibold">{holding.quantity}</td>
                <td className="text-right py-4 px-4 text-gray-300">${holding.average_price.toFixed(2)}</td>
                <td className="text-right py-4 px-4 text-gray-200 font-semibold">${holding.current_price.toFixed(2)}</td>
                <td className="text-right py-4 px-4 text-gold-300 font-bold">${holding.market_value.toFixed(2)}</td>
                <td className={`text-right py-4 px-4 font-black ${
                  holding.unrealised_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  <span className={`inline-block px-2 py-1 rounded-md ${
                    holding.unrealised_pnl >= 0 ? 'bg-green-950 bg-opacity-50' : 'bg-red-950 bg-opacity-50'
                  }`}>
                    {holding.unrealised_pnl >= 0 ? '+' : ''} ${holding.unrealised_pnl.toFixed(2)}
                  </span>
                </td>
                <td className={`text-right py-4 px-4 font-black ${
                  holding.unrealised_pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  <span className={`inline-block px-2 py-1 rounded-md ${
                    holding.unrealised_pnl_percent >= 0 ? 'bg-green-950 bg-opacity-50' : 'bg-red-950 bg-opacity-50'
                  }`}>
                    {holding.unrealised_pnl_percent >= 0 ? '+' : ''} {holding.unrealised_pnl_percent.toFixed(2)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
