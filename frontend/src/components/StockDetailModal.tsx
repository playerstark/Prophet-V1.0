import QuoteDashboard from './QuoteDashboard'
import CompanyProfileDashboard from './CompanyProfileDashboard'
import NewsDashboard from './NewsDashboard'
import AnalysisDashboard from './AnalysisDashboard'

interface Props {
  symbol: string
  isOpen: boolean
  onClose: () => void
}

export default function StockDetailModal({ symbol, isOpen, onClose }: Props) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4">
      <div className="bg-charcoal-900 border-2 border-gold-500 rounded-2xl max-w-4xl w-full max-h-screen overflow-y-auto">
        <div className="sticky top-0 bg-gradient-to-r from-charcoal-900 to-charcoal-800 border-b border-gold-500 border-opacity-30 p-6 flex items-center justify-between">
          <h2 className="text-3xl font-black text-gold-500">{symbol}</h2>
          <button
            onClick={onClose}
            className="text-gold-400 hover:text-gold-300 text-2xl font-bold"
          >
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          <QuoteDashboard symbol={symbol} />
          <CompanyProfileDashboard symbol={symbol} />
          <NewsDashboard symbol={symbol} limit={10} />
          <AnalysisDashboard symbol={symbol} />
        </div>

        <div className="border-t border-gold-500 border-opacity-30 bg-charcoal-800 p-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 rounded-lg border border-gold-500 text-gold-400 hover:bg-gold-500 hover:bg-opacity-10"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
