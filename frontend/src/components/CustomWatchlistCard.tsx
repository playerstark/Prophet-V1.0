import { useState } from 'react'
import axios from 'axios'

interface Ticker {
  id: number
  symbol: string
  notes: string | null
  added_at: string
}

interface Props {
  tickers: Ticker[]
  onAddTicker: () => void
}

export default function CustomWatchlistCard({ tickers, onAddTicker }: Props) {
  const [showForm, setShowForm] = useState(false)
  const [symbol, setSymbol] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAddTicker = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!symbol.trim()) {
      setError('Symbol is required')
      return
    }

    setLoading(true)
    setError(null)

    try {
      await axios.post(
        `/api/home/custom-watchlist/${symbol.toUpperCase()}`,
        { notes: notes || null }
      )
      setSymbol('')
      setNotes('')
      setShowForm(false)
      onAddTicker()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add ticker')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveTicker = async (id: number) => {
    try {
      await axios.delete(`/api/home/custom-watchlist/${id}`, { timeout: 60000 })
      onAddTicker()
    } catch (err) {
      setError('Failed to remove ticker')
    }
  }

  return (
    <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-8 hover:border-opacity-50 transition-all duration-300">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-black text-gold-500 uppercase tracking-wide">My Watchlist ({tickers.length})</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="group relative px-6 py-2.5 bg-gradient-to-r from-gold-500 to-gold-700 text-charcoal-900 font-black uppercase text-xs tracking-wider rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.4)] transition-all duration-300 transform hover:scale-105"
        >
          <span className="relative flex items-center gap-2">
            <span className="text-lg">+</span> Add Ticker
          </span>
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleAddTicker} className="bg-gradient-to-br from-charcoal-800 to-charcoal-900 border-2 border-gold-500 border-opacity-50 rounded-lg p-6 mb-6 backdrop-blur-sm">
          <div className="space-y-4">
            <div>
              <label className="block text-gold-300 text-sm font-bold uppercase tracking-wider mb-2">Symbol</label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="e.g., AAPL or RELIANCE.NS"
                className="w-full bg-charcoal-900 border-2 border-gold-500 border-opacity-30 rounded-lg px-4 py-3 text-gray-200 placeholder-gray-600 focus:outline-none focus:border-opacity-100 focus:shadow-[0_0_15px_rgba(212,175,55,0.2)] transition"
              />
            </div>
            <div>
              <label className="block text-gold-300 text-sm font-bold uppercase tracking-wider mb-2">Notes (optional)</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any notes about this ticker..."
                rows={2}
                className="w-full bg-charcoal-900 border-2 border-gold-500 border-opacity-30 rounded-lg px-4 py-3 text-gray-200 placeholder-gray-600 focus:outline-none focus:border-opacity-100 focus:shadow-[0_0_15px_rgba(212,175,55,0.2)] transition"
              />
            </div>
            {error && <p className="text-red-400 text-sm font-semibold">{error}</p>}
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2.5 bg-gradient-to-r from-gold-500 to-gold-700 text-charcoal-900 font-black uppercase text-xs tracking-wider rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition disabled:opacity-50"
              >
                {loading ? '⏳ Adding...' : '✓ Add'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setSymbol('')
                  setNotes('')
                  setError(null)
                }}
                className="flex-1 px-4 py-2.5 bg-gray-700 bg-opacity-50 text-gray-200 font-bold uppercase text-xs tracking-wider rounded-lg hover:bg-opacity-70 transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      {tickers.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg font-semibold">No tickers in your watchlist yet</p>
          <p className="text-gray-500 text-sm mt-2">Add your first ticker to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {tickers.map((ticker) => (
            <div
              key={ticker.id}
              className="group relative bg-gradient-to-br from-charcoal-800 to-charcoal-900 border-2 border-gold-500 border-opacity-30 rounded-lg p-4 hover:border-opacity-100 hover:shadow-[0_0_20px_rgba(212,175,55,0.2)] transition-all duration-300 overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-gold-500 to-transparent opacity-0 group-hover:opacity-5 transition-opacity duration-300"></div>

              <div className="relative z-10">
                <div className="flex justify-between items-start mb-3">
                  <span className="font-black text-xl text-gold-400">{ticker.symbol}</span>
                  <button
                    onClick={() => handleRemoveTicker(ticker.id)}
                    className="text-gray-500 hover:text-red-400 transition text-xl font-bold hover:scale-125 transform"
                    title="Remove from watchlist"
                  >
                    ✕
                  </button>
                </div>

                {ticker.notes && (
                  <p className="text-xs text-gray-300 mb-3 line-clamp-2 italic">{ticker.notes}</p>
                )}

                <div className="bg-black bg-opacity-30 rounded px-3 py-2">
                  <p className="text-xs text-gold-300 font-semibold uppercase tracking-wider">
                    Added {new Date(ticker.added_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
