import { useState } from 'react'
import './App.css'
import Home from './pages/Home'
import EddieIntraday from './pages/EddieIntraday'
import Analyzer from './pages/Analyzer'
import PnL from './pages/PnL'

function App() {
  const [activeTab, setActiveTab] = useState('home')

  const tabs = [
    { id: 'home', label: 'Home', icon: '◆' },
    { id: 'eddie-intraday', label: 'Eddie Intraday', icon: '⚡' },
    { id: 'analyzer', label: 'Stock Analyzer', icon: '📊' },
    { id: 'pnl', label: 'P&L Tracking', icon: '💰' }
  ]

  return (
    <div className="min-h-screen bg-charcoal-900">
      {/* Premium Header */}
      <header className="relative bg-gradient-to-b from-charcoal-800 to-charcoal-900 border-b-2 border-gold-500 border-opacity-50 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Logo Section */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-4xl font-black glow-gold">◆</span>
              <h1 className="text-4xl font-black tracking-wider">
                <span className="text-gold-500">PROPHET</span>
                <span className="text-gold-300 text-2xl ml-2">V1.0</span>
              </h1>
            </div>
            <p className="text-gold-300 text-xs font-bold uppercase tracking-widest ml-1">
              Multi-Market Stock Intelligence
            </p>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex gap-2 border-t border-gold-500 border-opacity-20 pt-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative group px-6 py-3 font-bold uppercase text-xs tracking-wider transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'text-gold-500 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-gradient-to-r after:from-gold-500 after:to-gold-700'
                    : 'text-gray-400 hover:text-gold-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-10">
        {activeTab === 'home' && <Home />}
        {activeTab === 'eddie-intraday' && <EddieIntraday />}
        {activeTab === 'analyzer' && <Analyzer />}
        {activeTab === 'pnl' && <PnL />}
      </main>
    </div>
  )
}

export default App
