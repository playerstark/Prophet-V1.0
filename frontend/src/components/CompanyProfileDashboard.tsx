import { useState, useEffect } from 'react'
import axios from 'axios'

interface CompanyProfile {
  symbol: string
  name: string
  sector: string
  market_cap: number
  pe_ratio: number
  dividend_yield: number
  website: string
  logo: string
  country: string
  ipo_date: string
}

interface Props {
  symbol: string
}

export default function CompanyProfileDashboard({ symbol }: Props) {
  const [profile, setProfile] = useState<CompanyProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchProfile()
  }, [symbol])

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`/api/watchlist/dashboard/company/${symbol}`, { timeout: 60000 })
      setProfile(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load company profile')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 animate-pulse">
        <div className="h-40 bg-charcoal-600 rounded"></div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="bg-charcoal-700 border border-red-500 border-opacity-30 rounded-xl p-4 text-red-300 text-sm">
        {error || 'No data available'}
      </div>
    )
  }

  const formatMarketCap = (value: number) => {
    if (!value) return 'N/A'
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    return `$${value.toFixed(2)}`
  }

  return (
    <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-6">
      <div className="flex items-start gap-4">
        {profile.logo && (
          <img src={profile.logo} alt={profile.name} className="w-12 h-12 rounded-lg" />
        )}
        <div className="flex-1">
          <h3 className="text-gold-500 font-bold text-lg">{profile.name}</h3>
          <p className="text-gold-300 text-xs">{profile.sector || 'N/A'}</p>
          <p className="text-gold-300 text-xs">{profile.country || 'N/A'}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-4 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs uppercase tracking-widest mb-2">Market Cap</p>
          <p className="text-gold-500 font-bold text-sm">{formatMarketCap(profile.market_cap)}</p>
        </div>

        <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-4 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs uppercase tracking-widest mb-2">P/E Ratio</p>
          <p className="text-gold-500 font-bold text-sm">{profile.pe_ratio ? profile.pe_ratio.toFixed(2) : 'N/A'}</p>
        </div>

        <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-4 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs uppercase tracking-widest mb-2">Dividend Yield</p>
          <p className="text-gold-500 font-bold text-sm">{profile.dividend_yield ? (profile.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</p>
        </div>

        <div className="bg-charcoal-900 bg-opacity-50 rounded-lg p-4 border border-gold-500 border-opacity-20">
          <p className="text-gold-300 text-xs uppercase tracking-widest mb-2">IPO Date</p>
          <p className="text-gold-500 font-bold text-sm text-xs">{profile.ipo_date || 'N/A'}</p>
        </div>
      </div>

      {profile.website && (
        <div className="pt-4 border-t border-gold-500 border-opacity-20">
          <a
            href={profile.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-gold-400 text-sm hover:text-gold-300 transition-colors"
          >
            → Visit Website
          </a>
        </div>
      )}
    </div>
  )
}
