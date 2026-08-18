import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import axios from 'axios'
import StockChart from '../components/StockChart'
import IndicatorPanel from '../components/IndicatorPanel'
import AISuggestionPanel from '../components/AISuggestionPanel'
import LongTermAnalysisPanel from '../components/LongTermAnalysisPanel'

import AIAnalysisReport from '../components/AIAnalysisReport'
interface StockData {
  symbol: string
  market: string
  current_price: number
  rsi: number
  adx: number
  momentum: number
  chart_data: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>
  news: Array<{
    title: string
    sentiment: string
    source: string
    url?: string
  }>
}

interface LongTermAnalysis {
  symbol: string
  company_name: string
  industry: string
  current_price: number
  valuation: {
    pe_ratio: number | null
    forward_pe: number | null
    intrinsic_value: number | null
    undervaluation_pct: number | null
    dcf_score: number
  }
  fundamentals: {
    revenue_growth_3y: number | null
    fcf_margin: number | null
    debt_to_equity: number | null
    roe: number | null
    fundamental_quality_score: number
  }
  technical: {
    rsi: number | null
    adx: number | null
    momentum: number | null
    technical_score: number
  }
  risk: {
    factors: string[]
    risk_score: number
  }
  analyst: {
    target_price: number | null
    upside_pct: number | null
  }
  scoring: {
    industry_score: number
    overall_score: number
    estimated_annual_return: number
  }
  classification: string
  thesis: string
}

interface TradeParams {
  entry_price: number
  stop_loss: number
  target_price: number
  reasoning: string
}

const formatPrice = (price: number, market: string): string => {
  const currency = market === 'IN' ? '₹' : '$'
  return `${currency}${price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
}

export default function Analyzer() {
  const [searchParams] = useSearchParams()
  const urlSymbol = searchParams.get('symbol')
  const urlMode = searchParams.get('mode')

  const [symbol, setSymbol] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [analysisType, setAnalysisType] = useState<'short-term' | 'swing' | 'long-term'>('short-term')
  const [shortTermData, setShortTermData] = useState<StockData | null>(null)
  const [longTermData, setLongTermData] = useState<LongTermAnalysis | null>(null)
  const [tradeParams, setTradeParams] = useState<TradeParams | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  // Auto-load stock from URL parameters
  useEffect(() => {
    if (urlSymbol) {
      setSymbol(urlSymbol.toUpperCase())
      setSearchInput(urlSymbol.toUpperCase())

      if (urlMode === 'short-term') {
        setAnalysisType('short-term')
      }

      // Auto-fetch data
      if (urlSymbol) {
        fetchShortTermData(urlSymbol.toUpperCase())
      }
    }
  }, [urlSymbol, urlMode])

  const fetchShortTermData = async (ticker: string) => {
    try {
      const response = await axios.get(`/api/stocks/${ticker}`, { timeout: 60000 })
      setShortTermData(response.data)

      // Fetch AI trade suggestion
      try {
        const suggestionResponse = await axios.get(`/api/stocks/${ticker}/ai-suggestion`, { timeout: 60000 })
        setTradeParams(suggestionResponse.data)
      } catch (err) {
        console.error('Failed to fetch AI suggestion:', err)
      }
    } catch (err) {
      throw err
    }
  }

  const fetchLongTermData = async (ticker: string) => {
    try {
      const response = await axios.post(`/api/long-term/analyze/${ticker}`)
      setLongTermData(response.data.analysis)
    } catch (err) {
      throw err
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    const ticker = searchInput.toUpperCase()
    if (!ticker.trim()) return

    setLoading(true)
    setError(null)
    setSaved(false)

    try {
      if (analysisType === 'short-term' || analysisType === 'swing') {
        await fetchShortTermData(ticker)
        setLongTermData(null)
      } else {
        await fetchLongTermData(ticker)
        setShortTermData(null)
      }

      setSymbol(ticker)
      setSearchInput('')
    } catch (err) {
      setError(`Failed to load ${analysisType} analysis for ${ticker}. Please check the symbol and try again.`)
      setShortTermData(null)
      setLongTermData(null)
      setTradeParams(null)
    } finally {
      setLoading(false)
    }
  }

  const handleAddToLongTermPicks = async () => {
    if (!longTermData) return

    try {
      await axios.post(`/api/home/custom-watchlist/${longTermData.symbol}`, {
        notes: `Scores: ${longTermData.scoring.overall_score.toFixed(1)}/100 | ${longTermData.classification} | Return: ${longTermData.scoring.estimated_annual_return.toFixed(1)}%`
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      setError('Failed to add stock to Long-Term Picks')
    }
  }

  const handleExecuteTrade = async () => {
    if (!shortTermData || !tradeParams) return
    alert(`Trade execution placeholder for ${symbol}\nEntry: ${formatPrice(tradeParams.entry_price, shortTermData.market)}\nTarget: ${formatPrice(tradeParams.target_price, shortTermData.market)}`)
  }

  const hasData = shortTermData || longTermData

  return (
    <div className="space-y-8">
      {/* Header & Search */}
      <div className="space-y-4">
        <div>
          <h2 className="text-3xl font-black text-gold-500 tracking-wide mb-2">STOCK ANALYZER</h2>
          <p className="text-gold-300 text-sm">Technical analysis (short-term, swing) or fundamental research (long-term)</p>
        </div>

        {/* Analysis Type Toggle & Search */}
        <div className="space-y-3">
          {/* Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => {
                setAnalysisType('short-term')
                setLongTermData(null)
                setShortTermData(null)
              }}
              className={`px-4 py-2 rounded-lg font-bold uppercase text-sm tracking-wider transition-colors ${
                analysisType === 'short-term'
                  ? 'bg-gold-600 text-black'
                  : 'bg-charcoal-700 border border-gold-500 border-opacity-30 text-gold-400 hover:border-opacity-100'
              }`}
            >
              📊 Short-Term
            </button>
            <button
              onClick={() => {
                setAnalysisType('swing')
                setLongTermData(null)
                setShortTermData(null)
              }}
              className={`px-4 py-2 rounded-lg font-bold uppercase text-sm tracking-wider transition-colors ${
                analysisType === 'swing'
                  ? 'bg-gold-600 text-black'
                  : 'bg-charcoal-700 border border-gold-500 border-opacity-30 text-gold-400 hover:border-opacity-100'
              }`}
            >
              💫 Swing
            </button>
            <button
              onClick={() => {
                setAnalysisType('long-term')
                setShortTermData(null)
                setTradeParams(null)
              }}
              className={`px-4 py-2 rounded-lg font-bold uppercase text-sm tracking-wider transition-colors ${
                analysisType === 'long-term'
                  ? 'bg-gold-600 text-black'
                  : 'bg-charcoal-700 border border-gold-500 border-opacity-30 text-gold-400 hover:border-opacity-100'
              }`}
            >
              📈 Long-Term
            </button>
          </div>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex gap-3">
            <input
              type="text"
              placeholder="Enter ticker (e.g., AAPL, RELIANCE.NS, TCS.BO)"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
              className="flex-1 bg-charcoal-800 border border-gold-500 border-opacity-30 rounded-lg px-4 py-3 text-gold-300 placeholder-gray-500 focus:outline-none focus:border-gold-500 text-sm"
            />
            <button
              type="submit"
              disabled={loading || !searchInput.trim()}
              className="bg-gold-600 hover:bg-gold-700 disabled:bg-gray-600 text-black font-bold px-6 py-3 rounded-lg transition-colors uppercase text-sm tracking-wider"
            >
              {loading ? 'Loading...' : 'Analyze'}
            </button>
          </form>
        </div>

        {error && (
          <div className="bg-red-950 border border-red-500 rounded-lg p-4 text-red-300 text-sm">
            {error}
          </div>
        )}

        {saved && (
          <div className="bg-green-950 border border-green-500 rounded-lg p-4 text-green-300 text-sm">
            ✓ Added to Long-Term Picks!
          </div>
        )}
      </div>

      {/* Main Content */}
      {hasData ? (
        <>
          {/* Short-Term / Swing Analysis */}
          {shortTermData && (
            <>
              {/* Stock Header */}
              <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="text-3xl font-black text-gold-500">{shortTermData.symbol}</h3>
                      <span className="text-xs uppercase tracking-widest px-2 py-1 bg-gold-500 bg-opacity-20 text-gold-400 rounded">
                        {analysisType === 'swing' ? '💫 Swing' : '📊 Short-Term'}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mt-1">{shortTermData.market === 'IN' ? 'NSE/BSE' : 'NASDAQ/NYSE'}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-4xl font-black text-green-400">{formatPrice(shortTermData.current_price, shortTermData.market)}</p>
                    <p className="text-gray-400 text-xs mt-1">Current Price</p>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gold-500 border-opacity-20">
                  <div>
                    <p className="text-gray-400 text-xs uppercase tracking-widest">RSI</p>
                    <p className="text-2xl font-bold text-gold-400">{shortTermData.rsi.toFixed(1)}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs uppercase tracking-widest">ADX</p>
                    <p className="text-2xl font-bold text-gold-400">{shortTermData.adx.toFixed(1)}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs uppercase tracking-widest">Momentum</p>
                    <p className={`text-2xl font-bold ${shortTermData.momentum >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {shortTermData.momentum.toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Chart & Indicators Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <StockChart data={shortTermData.chart_data} symbol={shortTermData.symbol} market={shortTermData.market} />
                </div>
                <div>
                  <IndicatorPanel data={shortTermData} />
                </div>
              </div>

              {/* AI Suggestion & Trade Execution */}
              {tradeParams && (
                <AISuggestionPanel
                  params={tradeParams}
                  symbol={shortTermData.symbol}
                  market={shortTermData.market}
                  onExecute={handleExecuteTrade}
                />
              )}

              {/* AI Analysis Report */}
              <AIAnalysisReport symbol={shortTermData.symbol} analysisType={analysisType} />
            </>
          )}

          {/* Long-Term Analysis */}
          {longTermData && (
            <>
              <LongTermAnalysisPanel
                analysis={longTermData}
                onAddToPicks={handleAddToLongTermPicks}
                saved={saved}
              />

              {/* AI Analysis Report */}
              <AIAnalysisReport symbol={longTermData.symbol} />
            </>
          )}
        </>
      ) : !loading ? (
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-12 text-center space-y-4">
          <p className="text-gold-500 text-lg font-bold">📊 Search for a stock to begin analysis</p>
          <p className="text-gray-400 text-sm">
            {analysisType === 'short-term'
              ? 'Enter a ticker symbol to view technical analysis and AI-powered trade suggestions'
              : analysisType === 'swing'
              ? 'Enter a ticker symbol to view swing trading signals with AI analysis for multi-day positions'
              : 'Enter a ticker symbol to view comprehensive fundamental analysis with DCF valuation and investment classification'}
          </p>
        </div>
      ) : (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-pulse mb-4">
              <div className="text-gold-500 text-4xl">◆</div>
            </div>
            <p className="text-gold-500 text-lg font-semibold">Analyzing {searchInput}...</p>
          </div>
        </div>
      )}
    </div>
  )
}
