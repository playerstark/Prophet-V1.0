import { useState, useEffect } from 'react'
import axios from 'axios'

export default function WatchlistAnalyticsDashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboard()
    const interval = setInterval(fetchDashboard, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboard = async () => {
    try {
      const response = await axios.get('/api/watchlist/dashboard/overview')
      setDashboardData(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="grid grid-cols-4 gap-4"><div className="h-24 bg-charcoal-700 rounded animate-pulse col-span-4"></div></div>
  if (error) return <div className="text-red-400">{error}</div>

  const stocks = dashboardData?.stocks || []
  const validStocks = stocks.filter((s: any) => s.quote && s.quote.current_price)

  if (validStocks.length === 0) return <div className="text-gold-300">No data available</div>

  const avgChange = validStocks.reduce((sum: number, s: any) => sum + (s.quote?.change_percent || 0), 0) / validStocks.length
  const totalVolume = validStocks.reduce((sum: number, s: any) => sum + (s.quote?.volume || 0), 0)
  const positiveStocks = validStocks.filter((s: any) => (s.quote?.change_percent || 0) > 0).length

  const formatVolume = (v: number) => {
    if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`
    if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`
    return `${(v / 1e3).toFixed(1)}K`
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-2">
          <p className="text-gold-300 text-xs uppercase">Watchlist Stocks</p>
          <p className="text-4xl font-black text-gold-500">{validStocks.length}</p>
          <p className="text-gold-300 text-xs">{positiveStocks} gaining</p>
        </div>

        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-2">
          <p className="text-gold-300 text-xs uppercase">Avg Daily Change</p>
          <p className={`text-4xl font-black ${avgChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {avgChange >= 0 ? '+' : ''}{avgChange.toFixed(2)}%
          </p>
        </div>

        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-2">
          <p className="text-gold-300 text-xs uppercase">Total Volume</p>
          <p className="text-4xl font-black text-gold-500">{formatVolume(totalVolume)}</p>
        </div>

        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-2">
          <p className="text-gold-300 text-xs uppercase">Status</p>
          <p className="text-4xl font-black text-gold-500">Live</p>
          <p className="text-gold-300 text-xs">Real-time updates</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6">
        <h3 className="text-gold-500 font-bold uppercase text-sm mb-4">Watchlist Overview</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {validStocks.slice(0, 10).map((stock: any, idx: number) => (
            <div key={idx} className="flex justify-between bg-charcoal-900 bg-opacity-50 rounded-lg p-3 border border-gold-500 border-opacity-20">
              <div>
                <p className="text-gold-400 font-semibold text-sm">{stock.symbol}</p>
                <p className="text-gold-300 text-xs">{stock.profile?.sector || 'N/A'}</p>
              </div>
              <div className="text-right">
                <p className="text-gold-400 font-semibold text-sm">${stock.quote.current_price.toFixed(2)}</p>
                <p className={`text-xs font-bold ${(stock.quote.change_percent || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {Math.abs(stock.quote.change_percent || 0).toFixed(2)}%
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
