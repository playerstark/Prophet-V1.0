import { useState, useEffect } from 'react'
import axios from 'axios'

interface Quote {
  current_price: number
  previous_close: number
  change: number
  change_percent: number
  day_high: number
  day_low: number
  open: number
  volume: number
  bid: number
  ask: number
  bid_size: number
  ask_size: number
}

interface Props {
  symbol: string
}

export default function QuoteDashboard({ symbol }: Props) {
  const [quote, setQuote] = useState<Quote | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchQuote()
    const interval = setInterval(fetchQuote, 5000)
    return () => clearInterval(interval)
  }, [symbol])

  const fetchQuote = async () => {
    try {
      const response = await axios.get(`/api/watchlist/dashboard/quote/${symbol}`, { timeout: 60000 })
      setQuote(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load quote')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="animate-pulse h-32 bg-charcoal-700 rounded"></div>
  if (error || !quote) return <div className="text-red-400">{error}</div>

  const isPositive = quote.change >= 0
  const changeColor = isPositive ? 'text-green-400' : 'text-red-400'
  const formatVolume = (v: number) => v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : `${(v / 1e3).toFixed(1)}K`

  return (
    <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-6">
      <div className="space-y-3">
        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-black text-gold-500">${quote.current_price.toFixed(2)}</span>
          <span className={`text-xl font-bold ${changeColor}`}>
            {isPositive ? '↑' : '↓'} {Math.abs(quote.change).toFixed(2)} ({quote.change_percent.toFixed(2)}%)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-3 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs uppercase mb-1">Open</p>
          <p className="text-gold-500 font-bold">${quote.open.toFixed(2)}</p>
        </div>
        <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-3 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs uppercase mb-1">Volume</p>
          <p className="text-gold-500 font-bold">{formatVolume(quote.volume)}</p>
        </div>
        <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-3 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs uppercase mb-1">Day High</p>
          <p className="text-gold-500 font-bold">${quote.day_high.toFixed(2)}</p>
        </div>
        <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-3 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs uppercase mb-1">Day Low</p>
          <p className="text-gold-500 font-bold">${quote.day_low.toFixed(2)}</p>
        </div>
      </div>
    </div>
  )
}
