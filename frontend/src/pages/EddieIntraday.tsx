import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

interface Signal {
  symbol: string
  price: number
  momentum: number
  rating: string
  confidence: number
  market_cap: string
  key_signals: string[]
}

interface SignalsData {
  market: string | null
  session: string | null
  current_time_ist: string
  status: string
  large_cap: Signal[]
  mid_cap: Signal[]
  small_cap: Signal[]
}

const EddieIntraday = () => {
  const navigate = useNavigate()
  const [signals, setSignals] = useState<SignalsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [marketStatus, setMarketStatus] = useState<string>('Detecting market...')

  // Fetch signals on component mount and setup auto-refresh
  useEffect(() => {
    fetchSignals()
    
    // Refresh every 30 minutes
    const interval = setInterval(fetchSignals, 30 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  // Fetch market status
  useEffect(() => {
    fetchMarketStatus()
    const interval = setInterval(fetchMarketStatus, 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const fetchMarketStatus = async () => {
    try {
      const response = await axios.get('/api/eddie-intraday/market-status')
      const market = response.data.market
      const status = response.data.status
      
      if (status === 'market_closed') {
        setMarketStatus(`${market || 'Market'} - CLOSED`)
      } else {
        setMarketStatus(`${market} - ACTIVE`)
      }
    } catch (err) {
      setMarketStatus('Unable to detect market')
    }
  }

  const fetchSignals = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await axios.get('/api/eddie-intraday/signals')
      setSignals(response.data)
    } catch (err) {
      setError('Failed to load Eddie Intraday signals')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleStockClick = (symbol: string) => {
    // Navigate to Stock Analyzer with symbol and short-term mode
    navigate(`/stock-analyzer?symbol=${symbol}&mode=short-term`)
  }

  const getRatingColor = (rating: string): string => {
    switch(rating) {
      case 'strong_buy': return 'text-green-400'
      case 'buy': return 'text-green-300'
      case 'neutral': return 'text-yellow-400'
      case 'sell': return 'text-red-300'
      case 'strong_sell': return 'text-red-500'
      default: return 'text-gray-300'
    }
  }

  const getRatingBg = (rating: string): string => {
    switch(rating) {
      case 'strong_buy': return 'bg-green-900/30'
      case 'buy': return 'bg-green-900/20'
      case 'neutral': return 'bg-yellow-900/20'
      case 'sell': return 'bg-red-900/20'
      case 'strong_sell': return 'bg-red-900/30'
      default: return 'bg-gray-900/20'
    }
  }

  const SignalCard = ({ signal }: { signal: Signal }) => (
    <div
      onClick={() => handleStockClick(signal.symbol)}
      className={`p-3 rounded-lg cursor-pointer transition hover:scale-102 ${getRatingBg(signal.rating)} border border-gray-700 hover:border-yellow-500/50`}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-bold text-white">{signal.symbol}</h3>
        <span className={`text-sm font-semibold ${getRatingColor(signal.rating)}`}>
          {signal.rating.toUpperCase()}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-xs text-gray-300 mb-2">
        <div>Price: ${signal.price.toFixed(2)}</div>
        <div className={signal.momentum > 0 ? 'text-green-400' : 'text-red-400'}>
          Momentum: {signal.momentum.toFixed(1)}%
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <div className="w-full bg-gray-900 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${getRatingColor(signal.rating)}`}
            style={{ width: `${signal.confidence * 100}%` }}
          />
        </div>
        <span className="text-xs font-semibold text-gray-400 min-w-fit">
          {(signal.confidence * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  )

  const CapSection = ({ title, signals: capSignals }: { title: string; signals: Signal[] }) => (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <h2 className="text-2xl font-bold text-yellow-400 mb-4 flex items-center gap-2">
        <span className="text-yellow-500">●</span>
        {title}
        <span className="text-sm text-gray-400 font-normal ml-auto">
          {capSignals.length} signals
        </span>
      </h2>
      
      {capSignals.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No signals available for {title}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {capSignals.map((signal) => (
            <SignalCard key={signal.symbol} signal={signal} />
          ))}
        </div>
      )}
    </div>
  )

  return (
    <div className="min-h-screen bg-charcoal-950 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-4xl">⚡</span>
          <h1 className="text-4xl font-bold text-yellow-400">EDDIE INTRADAY</h1>
        </div>
        <p className="text-gray-400">
          Real-time 6-filter confluence analysis • Automatic opportunity ranking
        </p>
      </div>

      {/* Market Status */}
      <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/50 rounded-xl p-4 mb-8">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-gray-400 text-sm">Market Status</p>
            <p className="text-white font-bold text-lg">{marketStatus}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm">Current Time (IST)</p>
            <p className="text-white font-mono text-sm">
              {signals?.current_time_ist ? new Date(signals.current_time_ist).toLocaleTimeString('en-IN') : 'Loading...'}
            </p>
          </div>
          <div className="text-right">
            <button
              onClick={fetchSignals}
              disabled={loading}
              className="bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-600 text-black font-bold py-2 px-4 rounded-lg transition"
            >
              {loading ? 'Refreshing...' : 'Refresh Now'}
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-900/30 border border-red-500 text-red-200 p-4 rounded-lg mb-8">
          {error}
        </div>
      )}

      {/* Signals by Market Cap */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-400">Loading Eddie Intraday signals...</p>
        </div>
      ) : signals ? (
        <div className="space-y-8">
          <CapSection title="Large Cap" signals={signals.large_cap} />
          <CapSection title="Mid Cap" signals={signals.mid_cap} />
          <CapSection title="Small Cap" signals={signals.small_cap} />
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          No signals available. Please check back later.
        </div>
      )}

      {/* Footer Info */}
      <div className="mt-12 text-center text-gray-500 text-sm">
        <p>Click any stock to view detailed short-term analysis in Stock Analyzer</p>
        <p>Data from Yahoo Finance • Updated every 30 minutes</p>
      </div>
    </div>
  )
}

export default EddieIntraday
