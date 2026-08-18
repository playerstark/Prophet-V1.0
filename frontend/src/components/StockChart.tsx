import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface ChartDataPoint {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface StockChartProps {
  data: ChartDataPoint[]
  symbol: string
  market: string
}

export default function StockChart({ data }: StockChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-12 text-center h-[400px] flex items-center justify-center">
        <div>
          <p className="text-gold-500 font-bold mb-2">📈 Price Chart</p>
          <p className="text-gray-400 text-sm">No chart data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-charcoal-700 to-charcoal-800 border border-gold-500 border-opacity-30 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-gold-500 font-bold uppercase text-sm tracking-wider">📈 Price Chart</h3>
        <span className="text-gray-400 text-xs">{data.length} candles</span>
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(212,175,55,0.1)" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
            stroke="rgba(212,175,55,0.2)"
          />
          <YAxis
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
            stroke="rgba(212,175,55,0.2)"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1a2e',
              border: '1px solid #d4af37',
              borderRadius: '8px',
              color: '#d4af37'
            }}
            formatter={(value: number) => value.toFixed(2)}
            labelStyle={{ color: '#d4af37' }}
          />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#d4af37"
            dot={false}
            strokeWidth={2}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gold-500 border-opacity-20 text-xs">
        <div>
          <p className="text-gray-400">High</p>
          <p className="text-gold-400 font-bold">{Math.max(...data.map(d => d.high)).toFixed(2)}</p>
        </div>
        <div>
          <p className="text-gray-400">Low</p>
          <p className="text-gold-400 font-bold">{Math.min(...data.map(d => d.low)).toFixed(2)}</p>
        </div>
        <div>
          <p className="text-gray-400">Avg Volume</p>
          <p className="text-gold-400 font-bold">{(data.reduce((sum, d) => sum + d.volume, 0) / data.length).toLocaleString()}</p>
        </div>
        <div>
          <p className="text-gray-400">Change</p>
          <p className={`font-bold ${data[data.length - 1].close >= data[0].close ? 'text-green-400' : 'text-red-400'}`}>
            {((data[data.length - 1].close - data[0].close) / data[0].close * 100).toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  )
}
