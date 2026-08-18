import { useState, useEffect, Suspense, lazy } from 'react'
import axios from 'axios'
import HoldingsCard from '../components/HoldingsCard'
import CustomWatchlistCard from '../components/CustomWatchlistCard'

// Lazy load news dashboard to prevent blocking home dashboard
const LazyNewsTabsDashboard = lazy(() => import('../components/LazyNewsTabsDashboard'))

interface HomeData {
  portfolio: {
    holdings: any[]
    total_value: number
    total_pnl: number
    total_pnl_percent: number
    holdings_count: number
  }
  custom_watchlist: {
    tickers: any[]
    count: number
  }
}

export default function Home() {
  const [data, setData] = useState<HomeData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchHomeData()
    const interval = setInterval(fetchHomeData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchHomeData = async () => {
    try {
      const response = await axios.get('/api/home', { timeout: 60000 })
      setData(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="animate-pulse mb-4">
            <div className="text-gold-500 text-4xl">◆</div>
          </div>
          <p className="text-gold-500 text-lg font-semibold">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-950 border-2 border-red-500 rounded-xl p-6 text-center">
        <p className="text-red-300 text-lg">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Portfolio Summary */}
      <div className="space-y-2">
        <h1 className="text-4xl font-black text-gold-500 tracking-wide">PROPHET DASHBOARD</h1>
        <p className="text-gold-300 text-sm">Real-time portfolio and market intelligence</p>
      </div>

      {/* Portfolio Cards */}
      {data?.portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-2">
            <p className="text-gold-300 text-xs uppercase tracking-widest">Total Value</p>
            <p className="text-4xl font-black text-gold-500">${(data.portfolio.total_value || 0).toLocaleString('en-US', { maximumFractionDigits: 2, minimumFractionDigits: 2 })}</p>
          </div>

          <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-2">
            <p className="text-gold-300 text-xs uppercase tracking-widest">Unrealised P&L</p>
            <p className={`text-4xl font-black ${data.portfolio.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              ${Math.abs(data.portfolio.total_pnl || 0).toLocaleString('en-US', { maximumFractionDigits: 2, minimumFractionDigits: 2 })}
            </p>
          </div>

          <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-2">
            <p className="text-gold-300 text-xs uppercase tracking-widest">Return %</p>
            <p className={`text-4xl font-black ${data.portfolio.total_pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {(data.portfolio.total_pnl_percent || 0).toFixed(2)}%
            </p>
          </div>

          <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-2">
            <p className="text-gold-300 text-xs uppercase tracking-widest">Holdings</p>
            <p className="text-4xl font-black text-gold-500">{data.portfolio.holdings_count}</p>
          </div>
        </div>
      )}

      {/* Watchlist Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {data?.custom_watchlist && (
          <CustomWatchlistCard tickers={data.custom_watchlist.tickers} onAddTicker={fetchHomeData} />
        )}
        {data?.portfolio && (
          <HoldingsCard holdings={data.portfolio.holdings.slice(0, 5)} />
        )}
      </div>

      {/* Lazy-loaded Market News - loads separately after main dashboard */}
      <Suspense fallback={<div className="text-center py-8 text-gold-300">Loading market news...</div>}>
        <LazyNewsTabsDashboard />
      </Suspense>
    </div>
  )
}
