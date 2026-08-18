import { useState, useEffect } from 'react'
import axios from 'axios'

interface NewsItem {
  title: string
  link: string
  published: string
  summary: string
  source: string
  region: string
  sentiment: string
}

export default function NewsTabsDashboard() {
  const [activeTab, setActiveTab] = useState<'india' | 'global'>('india')
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchNews()
    const interval = setInterval(fetchNews, 60000)
    return () => clearInterval(interval)
  }, [activeTab])

  const fetchNews = async () => {
    try {
      setLoading(true)
      const endpoint = activeTab === 'india' ? '/api/watchlist/news/indian' : '/api/watchlist/news/global'
      const response = await axios.get(`${endpoint}?limit=10`, { timeout: 60000 })
      setNews(response.data.news || [])
      setError(null)
    } catch (err) {
      setError(`Failed to load ${activeTab} news`)
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-500 bg-opacity-10 border-green-500 text-green-400'
      case 'negative':
        return 'bg-red-500 bg-opacity-10 border-red-500 text-red-400'
      default:
        return 'bg-gold-500 bg-opacity-10 border-gold-500 text-gold-400'
    }
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return '📈'
      case 'negative':
        return '📉'
      default:
        return '📰'
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-black text-gold-500 tracking-wide">MARKET NEWS</h2>
        <p className="text-gold-300 text-sm">Latest market updates from India and global markets</p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-gradient-to-r from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl overflow-hidden">
        <div className="flex">
          {(['india', 'global'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 px-6 py-4 font-bold uppercase text-xs tracking-widest transition-all ${
                activeTab === tab
                  ? 'bg-gold-500 bg-opacity-20 border-b-2 border-gold-500 text-gold-500'
                  : 'text-gold-300 hover:text-gold-400 border-b border-gold-500 border-opacity-20'
              }`}
            >
              {tab === 'india' ? '🇮🇳 India' : '🌍 Global'}
            </button>
          ))}
        </div>
      </div>

      {/* News Content */}
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
        {loading && (
          <div className="text-center py-8">
            <p className="text-gold-300 text-sm">Loading news...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {!loading && !error && news.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gold-300 text-sm">No news available</p>
          </div>
        )}

        {!loading && !error && news.length > 0 && (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {news.map((item, idx) => (
              <a
                key={idx}
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
                className="block group"
              >
                <div className="bg-charcoal-900 bg-opacity-50 border border-gold-500 border-opacity-20 rounded-lg p-4 hover:border-gold-500 hover:border-opacity-50 transition-all">
                  <div className="flex items-start gap-3 mb-2">
                    <span className="text-xl">{getSentimentIcon(item.sentiment)}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-gold-400 text-sm font-semibold group-hover:text-gold-300 line-clamp-2">
                        {item.title}
                      </p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded border whitespace-nowrap ${getSentimentColor(item.sentiment)}`}>
                      {item.sentiment.toUpperCase()}
                    </span>
                  </div>

                  <p className="text-gold-300 text-xs line-clamp-1 mb-2">
                    {item.summary || 'Click to read more'}
                  </p>

                  <div className="flex items-center justify-between text-xs text-gold-300">
                    <span>{item.source}</span>
                    <span className="text-gold-400">Read Article →</span>
                  </div>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
