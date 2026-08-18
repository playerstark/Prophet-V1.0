import { useState, useEffect } from 'react'
import axios from 'axios'
import WatchlistLane from '../components/WatchlistLane'
import WatchlistAnalyticsDashboard from '../components/WatchlistAnalyticsDashboard'
import StockDetailModal from '../components/StockDetailModal'

interface FilterState {
  horizon: string | null
  minAdx: number | null
  minRsi: number | null
  maxRsi: number | null
}

interface WatchlistEntry {
  id: number
  symbol: string
  market: string
  horizon: string
  direction: string
  current_price: number
  rsi: number
  adx: number
  momentum: number
  volume_ratio: number
  breakout_timestamp: string | null
}

interface WatchlistData {
  long_candidates: WatchlistEntry[]
  short_candidates: WatchlistEntry[]
  count: number
}

export default function Watchlist() {
  const [data, setData] = useState<WatchlistData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedStock, setSelectedStock] = useState<string | null>(null)
  const [filters, setFilters] = useState<FilterState>({
    horizon: 'intraday',
    minAdx: null,
    minRsi: null,
    maxRsi: null
  })

  useEffect(() => {
    fetchWatchlist()
    const interval = setInterval(fetchWatchlist, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchWatchlist = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.horizon) params.append('horizon', filters.horizon)
      if (filters.minAdx !== null) params.append('min_adx', String(filters.minAdx))
      if (filters.minRsi !== null) params.append('min_rsi', String(filters.minRsi))
      if (filters.maxRsi !== null) params.append('max_rsi', String(filters.maxRsi))

      const response = await axios.get(`/api/watchlist?${params}`, { timeout: 60000 })
      setData(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load watchlist')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    const updated = { ...filters, ...newFilters }
    setFilters(updated)
  }

  useEffect(() => {
    if (!loading) {
      fetchWatchlist()
    }
  }, [filters])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="animate-pulse mb-4">
            <div className="text-gold-500 text-4xl">◆</div>
          </div>
          <p className="text-gold-500 text-lg font-semibold">Scanning markets...</p>
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
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-3xl font-black text-gold-500 tracking-wide">EDDIE'S WATCHLIST</h2>
        <p className="text-gold-300 text-sm">Live screening engine - Real-time breakout and breakdown detection</p>
      </div>

      {/* Finnhub Analytics Dashboard */}
      <div className="bg-charcoal-800 rounded-xl p-6 border border-gold-500 border-opacity-20">
        <h3 className="text-gold-500 font-bold uppercase text-sm tracking-wider mb-6">📊 Market Analytics</h3>
        <WatchlistAnalyticsDashboard />
      </div>

      {/* Filter Controls */}
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
        <h3 className="text-gold-500 font-bold uppercase text-sm tracking-wider">Filters</h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Horizon Filter */}
          <div>
            <label className="block text-gold-300 text-xs font-bold uppercase tracking-widest mb-2">
              Horizon
            </label>
            <select
              value={filters.horizon || ''}
              onChange={(e) => handleFilterChange({ horizon: e.target.value || null })}
              className="w-full bg-charcoal-900 border border-gold-500 border-opacity-30 rounded px-3 py-2 text-gold-300 text-sm focus:outline-none focus:border-gold-500"
            >
              <option value="">All Horizons</option>
              <option value="intraday">Intraday</option>
              <option value="swing">Swing</option>
            </select>
          </div>

          {/* Min ADX */}
          <div>
            <label className="block text-gold-300 text-xs font-bold uppercase tracking-widest mb-2">
              Min ADX
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="5"
              placeholder="20"
              value={filters.minAdx ?? ''}
              onChange={(e) => handleFilterChange({ minAdx: e.target.value ? parseFloat(e.target.value) : null })}
              className="w-full bg-charcoal-900 border border-gold-500 border-opacity-30 rounded px-3 py-2 text-gold-300 text-sm focus:outline-none focus:border-gold-500"
            />
          </div>

          {/* Min RSI */}
          <div>
            <label className="block text-gold-300 text-xs font-bold uppercase tracking-widest mb-2">
              Min RSI
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="5"
              placeholder="30"
              value={filters.minRsi ?? ''}
              onChange={(e) => handleFilterChange({ minRsi: e.target.value ? parseFloat(e.target.value) : null })}
              className="w-full bg-charcoal-900 border border-gold-500 border-opacity-30 rounded px-3 py-2 text-gold-300 text-sm focus:outline-none focus:border-gold-500"
            />
          </div>

          {/* Max RSI */}
          <div>
            <label className="block text-gold-300 text-xs font-bold uppercase tracking-widest mb-2">
              Max RSI
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="5"
              placeholder="70"
              value={filters.maxRsi ?? ''}
              onChange={(e) => handleFilterChange({ maxRsi: e.target.value ? parseFloat(e.target.value) : null })}
              className="w-full bg-charcoal-900 border border-gold-500 border-opacity-30 rounded px-3 py-2 text-gold-300 text-sm focus:outline-none focus:border-gold-500"
            />
          </div>
        </div>
      </div>

      {/* Watchlist Lanes - Now Clickable */}
      <div className="space-y-6">
        {/* Long Candidates */}
        <div
          onClick={() => data?.long_candidates.length === 1 && setSelectedStock(data.long_candidates[0].symbol)}
        >
          <WatchlistLane
            title="Long Setups"
            subtitle="Bullish breakouts above RSI bands"
            candidates={data?.long_candidates || []}
            direction="long"
            icon="🟢"
            onSymbolClick={setSelectedStock}
          />
        </div>

        {/* Short Candidates */}
        <div
          onClick={() => data?.short_candidates.length === 1 && setSelectedStock(data.short_candidates[0].symbol)}
        >
          <WatchlistLane
            title="Short Setups"
            subtitle="Bearish breakdowns below RSI bands"
            candidates={data?.short_candidates || []}
            direction="short"
            icon="🔴"
            onSymbolClick={setSelectedStock}
          />
        </div>
      </div>

      {/* Summary */}
      {data && (
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6">
          <p className="text-gold-300 text-sm text-center">
            <span className="font-bold text-gold-500">{data.long_candidates.length}</span> long setups •{' '}
            <span className="font-bold text-gold-500">{data.short_candidates.length}</span> short setups •{' '}
            <span className="font-bold text-gold-500">{data.count}</span> total candidates
          </p>
        </div>
      )}

      {/* Stock Detail Modal */}
      <StockDetailModal
        symbol={selectedStock || ''}
        isOpen={!!selectedStock}
        onClose={() => setSelectedStock(null)}
      />
    </div>
  )
}
