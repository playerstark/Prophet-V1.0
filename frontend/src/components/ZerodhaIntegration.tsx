import { useState, useEffect } from 'react'
import axios from 'axios'

interface ZerodhaHolding {
  symbol: string
  quantity: number
  average_price: number
  current_price: number
  pnl: number
  pnl_percent: number
}

interface ZerodhaPosition {
  symbol: string
  quantity: number
  average_price: number
  current_price: number
  multiplier: number
  pnl: number
  pnl_percent: number
  overnight_quantity: number
  day_quantity: number
}

interface ZerodhaPortfolio {
  is_connected: boolean
  user_id?: string
  equity_balance?: number
  commodity_balance?: number
  used_margin?: number
  available_margin?: number
  holdings: ZerodhaHolding[]
  positions: ZerodhaPosition[]
}

export default function ZerodhaIntegration() {
  const [portfolio, setPortfolio] = useState<ZerodhaPortfolio | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [connectUrl, setConnectUrl] = useState<string | null>(null)

  useEffect(() => {
    fetchZerodhaData()
  }, [])

  const fetchZerodhaData = async () => {
    try {
      const response = await axios.get('/api/zerodha/portfolio')
      setPortfolio(response.data)
      setError(null)
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Zerodha not connected')
      } else {
        setError('Failed to load Zerodha data')
      }
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleConnectZerodha = async () => {
    try {
      const response = await axios.get('/api/zerodha/login-url')
      setConnectUrl(response.data.url)
    } catch (err) {
      console.error('Failed to get login URL:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="animate-pulse mb-4">
            <div className="text-gold-500 text-4xl">◆</div>
          </div>
          <p className="text-gold-500 text-lg font-semibold">Syncing with Zerodha...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-3xl font-black text-gold-500 tracking-wide flex items-center gap-3">
          <span className="text-4xl">⚡</span>
          ZERODHA INTEGRATION
        </h2>
        <p className="text-gold-300 text-sm">Real-time portfolio sync from Zerodha broker</p>
      </div>

      {/* Connection Status */}
      {!portfolio?.is_connected ? (
        <div className="bg-red-950 border-2 border-red-500 rounded-xl p-8 text-center">
          <p className="text-red-300 text-lg font-semibold mb-4">Zerodha Account Not Connected</p>
          <p className="text-red-300 text-sm mb-6">Connect your Zerodha account to sync portfolio data in real-time</p>
          {connectUrl ? (
            <a
              href={connectUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors"
            >
              Login with Zerodha
            </a>
          ) : (
            <button
              onClick={handleConnectZerodha}
              className="bg-gold-500 hover:bg-gold-600 text-charcoal-900 font-bold py-3 px-8 rounded-lg transition-colors"
            >
              Connect Zerodha Account
            </button>
          )}
        </div>
      ) : portfolio && (
        <>
          {/* Account Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-charcoal-800 border-2 border-gold-500 border-opacity-30 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase tracking-wider">Equity Balance</p>
              <p className="text-gold-500 text-2xl font-bold mt-2">₹{portfolio.equity_balance?.toFixed(2)}</p>
            </div>
            <div className="bg-charcoal-800 border-2 border-gold-500 border-opacity-30 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase tracking-wider">Available Margin</p>
              <p className="text-green-400 text-2xl font-bold mt-2">₹{portfolio.available_margin?.toFixed(2)}</p>
            </div>
            <div className="bg-charcoal-800 border-2 border-gold-500 border-opacity-30 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase tracking-wider">Used Margin</p>
              <p className="text-orange-400 text-2xl font-bold mt-2">₹{portfolio.used_margin?.toFixed(2)}</p>
            </div>
            <div className="bg-charcoal-800 border-2 border-gold-500 border-opacity-30 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase tracking-wider">Commodity Balance</p>
              <p className="text-blue-400 text-2xl font-bold mt-2">₹{portfolio.commodity_balance?.toFixed(2)}</p>
            </div>
          </div>

          {/* Holdings Section */}
          {portfolio.holdings.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xl font-bold text-gold-500">HOLDINGS</h3>
              <div className="bg-charcoal-800 border-2 border-gold-500 border-opacity-20 rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead className="bg-charcoal-900 border-b-2 border-gold-500 border-opacity-20">
                      <tr>
                        <th className="px-4 py-3 text-left text-gold-400 font-bold">SYMBOL</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">QUANTITY</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">AVG PRICE</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">CURRENT PRICE</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">P&L</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">RETURN %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.holdings.map((holding) => (
                        <tr
                          key={holding.symbol}
                          className="border-b border-gold-500 border-opacity-10 hover:bg-charcoal-700 transition-colors"
                        >
                          <td className="px-4 py-3 font-bold text-gold-300">{holding.symbol}</td>
                          <td className="px-4 py-3 text-right text-gray-300">{holding.quantity}</td>
                          <td className="px-4 py-3 text-right text-gray-300">₹{holding.average_price.toFixed(2)}</td>
                          <td className="px-4 py-3 text-right text-gray-300">₹{holding.current_price.toFixed(2)}</td>
                          <td className="px-4 py-3 text-right font-bold">
                            <span className={holding.pnl > 0 ? 'text-green-400' : 'text-red-400'}>
                              ₹{holding.pnl.toFixed(2)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right font-bold">
                            <span className={holding.pnl_percent > 0 ? 'text-green-400' : 'text-red-400'}>
                              {holding.pnl_percent.toFixed(2)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Positions Section */}
          {portfolio.positions.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xl font-bold text-gold-500">ACTIVE POSITIONS</h3>
              <div className="bg-charcoal-800 border-2 border-gold-500 border-opacity-20 rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead className="bg-charcoal-900 border-b-2 border-gold-500 border-opacity-20">
                      <tr>
                        <th className="px-4 py-3 text-left text-gold-400 font-bold">SYMBOL</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">QTY (DAY/OVERNIGHT)</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">AVG PRICE</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">CURRENT PRICE</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">P&L</th>
                        <th className="px-4 py-3 text-right text-gold-400 font-bold">RETURN %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.positions.map((position) => (
                        <tr
                          key={position.symbol}
                          className="border-b border-gold-500 border-opacity-10 hover:bg-charcoal-700 transition-colors"
                        >
                          <td className="px-4 py-3 font-bold text-gold-300">{position.symbol}</td>
                          <td className="px-4 py-3 text-right text-gray-300">
                            {position.day_quantity} / {position.overnight_quantity}
                          </td>
                          <td className="px-4 py-3 text-right text-gray-300">₹{position.average_price.toFixed(2)}</td>
                          <td className="px-4 py-3 text-right text-gray-300">₹{position.current_price.toFixed(2)}</td>
                          <td className="px-4 py-3 text-right font-bold">
                            <span className={position.pnl > 0 ? 'text-green-400' : 'text-red-400'}>
                              ₹{position.pnl.toFixed(2)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right font-bold">
                            <span className={position.pnl_percent > 0 ? 'text-green-400' : 'text-red-400'}>
                              {position.pnl_percent.toFixed(2)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Empty State */}
          {portfolio.holdings.length === 0 && portfolio.positions.length === 0 && (
            <div className="bg-charcoal-800 border-2 border-gold-500 border-opacity-20 rounded-xl p-8 text-center">
              <p className="text-gold-500 font-semibold mb-2">No Holdings or Positions</p>
              <p className="text-gold-300 text-sm">Your portfolio data will appear here once you have active holdings</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
