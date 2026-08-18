import { useState, useEffect } from 'react'
import axios from 'axios'

interface NewsItem {
  title: string
  sentiment: string
}

interface Props {
  symbol: string
  limit?: number
}

export default function NewsDashboard({ symbol, limit = 5 }: Props) {
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchNews()
  }, [symbol, limit])

  const fetchNews = async () => {
    try {
      const response = await axios.get(`/api/watchlist/dashboard/news/${symbol}?limit=${limit}`, { timeout: 60000 })
      setNews(response.data.news || [])
      setError(null)
    } catch (err) {
      setError('Failed to load news')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="animate-pulse h-40 bg-charcoal-700 rounded"></div>
  if (error || news.length === 0) return <div className="text-gold-300">{error || 'No news available'}</div>

  return (
    <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
      <h3 className="text-gold-500 font-bold uppercase text-sm">Latest News</h3>
      <div className="space-y-3">
        {news.slice(0, 5).map((item, idx) => (
          <div key={idx} className="bg-charcoal-900 bg-opacity-50 border border-gold-500 border-opacity-20 rounded-lg p-4">
            <p className="text-gold-400 text-sm font-semibold line-clamp-2">{item.title}</p>
            <span className="text-xs text-gold-300 mt-2 inline-block">{item.sentiment.toUpperCase()}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
