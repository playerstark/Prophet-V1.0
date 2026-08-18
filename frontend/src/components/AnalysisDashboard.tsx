import { useState, useEffect } from 'react'
import axios from 'axios'

interface Analysis {
  symbol: string
  price_target: any
  earnings: any
  recommendations: any[]
}

interface Props {
  symbol: string
  currentPrice?: number
}

export default function AnalysisDashboard({ symbol }: Props) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAnalysis()
  }, [symbol])

  const fetchAnalysis = async () => {
    try {
      const response = await axios.get(`/api/watchlist/dashboard/analysis/${symbol}`, { timeout: 60000 })
      setAnalysis(response.data)
    } catch (err) {
      setError('Failed to load analysis')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="animate-pulse h-40 bg-charcoal-700 rounded"></div>
  if (error || !analysis) return <div className="text-red-400">{error}</div>

  return (
    <div className="space-y-6">
      {analysis.price_target && (
        <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
          <h3 className="text-gold-500 font-bold uppercase text-sm">Analyst Targets</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-4 border border-gold-500 border-opacity-20">
              <p className="text-gold-300 text-xs uppercase mb-2">Target (Mean)</p>
              <p className="text-green-400 font-bold">${analysis.price_target.target_mean?.toFixed(2) || 'N/A'}</p>
            </div>
            <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-4 border border-gold-500 border-opacity-20">
              <p className="text-gold-300 text-xs uppercase mb-2">Range</p>
              <p className="text-gold-400 text-sm">${analysis.price_target.target_low?.toFixed(2)} - ${analysis.price_target.target_high?.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
