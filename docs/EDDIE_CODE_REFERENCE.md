# Eddie Intraday Enhancement - Code Snippets Reference

## 1. MarketCapInfo Component (New)
```typescript
const MarketCapInfo = ({ cap }: { cap: 'large' | 'mid' | 'small' }) => {
  const [showTooltip, setShowTooltip] = useState(false)

  const definitions = {
    large: {
      title: 'Large Cap',
      definition: 'Market Cap > $300B (US) / ₹3T (India)',
      description: 'Well-established companies with high liquidity and low volatility'
    },
    mid: {
      title: 'Mid Cap',
      definition: 'Market Cap $10B-$300B (US) / ₹100B-₹3T (India)',
      description: 'Growth-oriented companies with moderate liquidity'
    },
    small: {
      title: 'Small Cap',
      definition: 'Market Cap < $10B (US) / < ₹100B (India)',
      description: 'High-growth potential with higher volatility'
    }
  }

  const def = definitions[cap]

  return (
    <div className="relative">
      <button
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(!showTooltip)}
        className="ml-2 text-gold-400 hover:text-gold-300 font-bold text-lg"
      >
        ⓘ
      </button>
      {showTooltip && (
        <div className="absolute bottom-full left-0 mb-2 bg-charcoal-700 border-2 border-gold-500 rounded-lg p-3 w-64 text-sm z-10 shadow-lg">
          <p className="font-bold text-gold-400 mb-1">{def.title}</p>
          <p className="text-gold-300 font-mono text-xs mb-2">{def.definition}</p>
          <p className="text-gold-300 text-xs">{def.description}</p>
        </div>
      )}
    </div>
  )
}
```

## 2. StatusBadge Component (New)
```typescript
const StatusBadge = ({ status }: { status: string }) => {
  const colors: { [key: string]: string } = {
    'NEW': 'bg-purple-900 border-purple-500 text-purple-300',
    'ACTIVE': 'bg-blue-900 border-blue-500 text-blue-300',
    'WEAKENING': 'bg-yellow-900 border-yellow-500 text-yellow-300',
    'REMOVED': 'bg-red-900 border-red-500 text-red-300'
  }
  const icons: { [key: string]: string } = {
    'NEW': '✨',
    'ACTIVE': '🔄',
    'WEAKENING': '⚠️',
    'REMOVED': '❌'
  }
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-bold border ${colors[status] || colors.ACTIVE}`}>
      {icons[status]} {status}
    </span>
  )
}
```

## 3. State Management (Enhanced)
```typescript
const [watchlist, setWatchlist] = useState<WatchListData | null>(null)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)
const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null)
const [analyzing, setAnalyzing] = useState(false)
const [analysisResult, setAnalysisResult] = useState<AnalysisState | null>(null)
const [filterRating, setFilterRating] = useState<string>('all')
const [autoRefresh, setAutoRefresh] = useState(true)
const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
const [nextRefresh, setNextRefresh] = useState<Date | null>(null)          // NEW
const [countdownText, setCountdownText] = useState<string>('')            // NEW
const [previousSignals, setPreviousSignals] = useState<Map<string, OpportunitySignal>>(new Map()) // NEW
const countdownRef = useRef<NodeJS.Timeout | null>(null)                 // NEW

const REFRESH_INTERVAL = 30 * 60 * 1000 // 30 minutes (NEW)
```

## 4. Countdown Timer Logic (New)
```typescript
const calculateCountdown = (nextTime: Date) => {
  const now = new Date()
  const diff = nextTime.getTime() - now.getTime()

  if (diff <= 0) {
    return 'Ready to scan'
  }

  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)

  if (minutes > 0) {
    return `in ${minutes}m ${seconds}s`
  } else {
    return `in ${seconds}s`
  }
}

// Countdown updates every second
useEffect(() => {
  if (autoRefresh && watchlist?.market_open) {
    const now = new Date()
    const nextTime = new Date(now.getTime() + REFRESH_INTERVAL)
    setNextRefresh(nextTime)

    const interval = setInterval(() => {
      fetchWatchlist()
      setLastRefresh(new Date())

      const newNextTime = new Date()
      newNextTime.setTime(newNextTime.getTime() + REFRESH_INTERVAL)
      setNextRefresh(newNextTime)
    }, REFRESH_INTERVAL)

    if (countdownRef.current) clearInterval(countdownRef.current)
    countdownRef.current = setInterval(() => {
      if (nextRefresh) {
        setCountdownText(calculateCountdown(nextRefresh))
      }
    }, 1000)

    return () => {
      clearInterval(interval)
      if (countdownRef.current) clearInterval(countdownRef.current)
    }
  }
}, [autoRefresh, watchlist?.market_open])
```

## 5. Signal Status Tracking (New)
```typescript
const fetchWatchlist = async () => {
  try {
    setLoading(true)
    const response = await axios.get('/api/eddie/opportunities/watch-list?limit=50', {
      timeout: 30000
    })

    // Track signal status changes
    if (response.data.large_cap_signals || response.data.mid_cap_signals || response.data.small_cap_signals) {
      const allNewSignals = [
        ...(response.data.large_cap_signals || []),
        ...(response.data.mid_cap_signals || []),
        ...(response.data.small_cap_signals || [])
      ]

      const newSignalsMap = new Map(allNewSignals.map(s => [s.symbol, s]))

      // Update status based on previous state
      const updatedSignals = allNewSignals.map(signal => {
        const prevSignal = previousSignals.get(signal.symbol)
        let status: 'NEW' | 'ACTIVE' | 'WEAKENING' | 'REMOVED' = 'ACTIVE'

        if (!prevSignal) {
          status = 'NEW'  // New signal that just qualified
        } else if (signal.confidence < prevSignal.confidence * 0.85) {
          status = 'WEAKENING'  // Confidence dropped more than 15%
        }

        return {
          ...signal,
          status,
          statusUpdatedAt: new Date().toISOString()
        }
      })

      setPreviousSignals(newSignalsMap)
      setWatchlist(response.data)
    } else {
      setWatchlist(response.data)
    }

    setError(null)
    const now = new Date()
    setLastRefresh(now)

    // Set next refresh time
    const nextTime = new Date(now.getTime() + REFRESH_INTERVAL)
    setNextRefresh(nextTime)
    setCountdownText(calculateCountdown(nextTime))
  } catch (err) {
    setError('Failed to load Eddie Intraday watchlist')
    console.error(err)
  } finally {
    setLoading(false)
  }
}
```

## 6. Live Refresh Information Panel (New)
```typescript
{/* Live Refresh Information */}
<div className="bg-gradient-to-r from-purple-950 to-indigo-950 border-2 border-purple-500 rounded-xl p-4">
  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 text-sm">
    <div className="flex gap-6">
      <div>
        <p className="text-purple-300 text-xs uppercase font-bold">Market Status</p>
        <div className="flex items-center gap-2 mt-1">
          <span className={`inline-block w-2 h-2 rounded-full ${watchlist?.market_open ? 'bg-green-400 animate-pulse' : 'bg-orange-400'}`}></span>
          <p className="text-gold-300 font-bold">
            {watchlist?.active_market || 'N/A'} • {watchlist?.market_open ? '🟢 OPEN' : '🔴 CLOSED'}
          </p>
        </div>
      </div>
      <div>
        <p className="text-purple-300 text-xs uppercase font-bold">Last Updated</p>
        <p className="text-gold-300 font-mono mt-1">
          {lastRefresh ? lastRefresh.toLocaleTimeString() : 'Never'}
        </p>
      </div>
    </div>

    <div className="text-right">
      <p className="text-purple-300 text-xs uppercase font-bold">Next Scan</p>
      <p className="text-gold-400 font-bold mt-1">
        {countdownText || 'Ready to scan'}
      </p>
    </div>
  </div>
</div>
```

## 7. Enhanced Stock Card (Example: Large Cap)
```typescript
{getMarketCapSignals('large').slice(0, 12).map((signal, idx) => (
  <div
    key={idx}
    onClick={() => analyzeSymbol(signal.symbol)}
    className={`cursor-pointer transform hover:scale-102 transition-all rounded-lg p-4 border-2 ${
      signal.rating === 'strong_buy'
        ? 'bg-gradient-to-br from-charcoal-700 to-green-950 border-green-500'
        : signal.rating === 'buy'
        ? 'bg-gradient-to-br from-charcoal-700 to-emerald-950 border-emerald-500'
        : 'border-blue-500 bg-charcoal-800 hover:bg-blue-950'
    }`}
  >
    <div className="flex justify-between items-start mb-3">
      <div className="flex items-center gap-2">
        <span className="font-bold text-blue-300 text-lg">{signal.symbol}</span>
        {signal.is_high_probability && <span className="text-lg">⭐</span>}
      </div>
      <RatingBadge rating={signal.rating} />
    </div>

    <div className="space-y-2 text-xs">
      <div className="flex items-center justify-between">
        <span className="text-gold-300">Signal Strength</span>
        <div className="w-16 h-1.5 bg-charcoal-700 rounded-full overflow-hidden border border-gold-500">
          <div
            className="h-full bg-gradient-to-r from-gold-500 to-gold-400"
            style={{ width: `${signal.confidence * 100}%` }}
          />
        </div>
      </div>
      <div className="flex justify-between text-gold-300">
        <span>📈 {signal.bullish_filters} bullish</span>
        <span>📉 {signal.bearish_filters} bearish</span>
      </div>
      <div className="pt-2 border-t border-blue-500 border-opacity-30">
        <p className="text-gold-300 line-clamp-2">{signal.key_signals}</p>
      </div>
    </div>
  </div>
))}
```

## 8. Updated Info Box
```typescript
{/* Info Box */}
<div className="bg-blue-950 border-2 border-blue-500 rounded-xl p-4">
  <p className="text-blue-300 text-sm mb-2">
    <span className="font-bold">💡 How it works:</span> Eddie continuously searches for intraday opportunities by combining all 6 intelligent filters. Watchlists update every 30 minutes while markets are active. Stocks automatically enter/exit based on live filter criteria.
  </p>
  <p className="text-blue-300 text-xs opacity-80">
    Status indicators: <span className="text-purple-300">✨ NEW</span> (just qualified) • <span className="text-blue-300">🔄 ACTIVE</span> (still qualifies) • <span className="text-yellow-300">⚠️ WEAKENING</span> (signals deteriorating) • <span className="text-red-300">❌ REMOVED</span> (no longer qualifies)
  </p>
</div>
```

## 9. Controls Update
```typescript
<label className="flex items-center gap-2 text-gold-300 text-sm">
  <input
    type="checkbox"
    checked={autoRefresh}
    onChange={(e) => setAutoRefresh(e.target.checked)}
    className="w-4 h-4 rounded"
  />
  Auto-refresh (30min)  {/* Changed from (1min) */}
</label>
```

## 10. Market Cap Info Integration
```typescript
<div className="bg-blue-950 px-4 py-3 border-b border-blue-500 flex items-center justify-between">
  <div className="flex items-center gap-2">
    <h3 className="text-lg font-black text-blue-400">💎 LARGE CAP ({getMarketCapSignals('large').length})</h3>
    <MarketCapInfo cap="large" />  {/* NEW - Info icon with tooltip */}
  </div>
</div>
```

---

## Summary of Code Changes

**Files Modified:**
- `frontend/src/pages/EddieIntraday.tsx`

**New Components Added:**
- `MarketCapInfo` - Tooltip with market-cap definitions
- `StatusBadge` - Dynamic status indicator component

**New State Variables:**
- `nextRefresh` - Stores next refresh time
- `countdownText` - Displays countdown string
- `previousSignals` - Map to track signal history
- `countdownRef` - useRef for countdown interval

**New Constants:**
- `REFRESH_INTERVAL` = 30 minutes

**New Functions:**
- `calculateCountdown()` - Calculates time until next refresh

**Enhanced Sections:**
- Refresh controls (30min label)
- Live refresh information panel (new)
- Stock cards (visual bars, better hierarchy)
- Info box (dynamic watchlist explanation)
- Market cap sections (info icons)

