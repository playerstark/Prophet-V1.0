import { useState } from 'react'
import ZerodhaIntegration from '../components/ZerodhaIntegration'

export default function PnL() {
  const [showApiConfig, setShowApiConfig] = useState(false)
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [accessToken, setAccessToken] = useState('')
  const [configSaved, setConfigSaved] = useState(false)

  const handleSaveConfig = () => {
    // TODO: Save API configuration to backend
    if (apiKey && apiSecret && accessToken) {
      setConfigSaved(true)
      setTimeout(() => setConfigSaved(false), 3000)
    }
  }

  return (
    <div className="space-y-8">
      {/* Zerodha API Configuration */}
      <div className="bg-charcoal-800 border-2 border-gold-500 border-opacity-30 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-gold-500">Zerodha API Configuration</h3>
          <button
            onClick={() => setShowApiConfig(!showApiConfig)}
            className="text-gold-300 hover:text-gold-500 text-sm font-semibold transition-colors"
          >
            {showApiConfig ? '▼ Hide' : '▶ Show'}
          </button>
        </div>

        {showApiConfig && (
          <div className="space-y-4 mt-4 border-t border-gold-500 border-opacity-20 pt-4">
            <div>
              <label className="block text-gray-400 text-sm font-semibold mb-2">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter Zerodha API Key"
                className="w-full bg-charcoal-700 border-2 border-gold-500 border-opacity-30 rounded-lg px-4 py-2 text-gold-300 placeholder-gray-500 focus:outline-none focus:border-gold-500 focus:border-opacity-100 transition-all"
              />
              <p className="text-gray-500 text-xs mt-1">Your Zerodha API key for authentication</p>
            </div>

            <div>
              <label className="block text-gray-400 text-sm font-semibold mb-2">API Secret</label>
              <input
                type="password"
                value={apiSecret}
                onChange={(e) => setApiSecret(e.target.value)}
                placeholder="Enter Zerodha API Secret"
                className="w-full bg-charcoal-700 border-2 border-gold-500 border-opacity-30 rounded-lg px-4 py-2 text-gold-300 placeholder-gray-500 focus:outline-none focus:border-gold-500 focus:border-opacity-100 transition-all"
              />
              <p className="text-gray-500 text-xs mt-1">Your Zerodha API secret key</p>
            </div>

            <div>
              <label className="block text-gray-400 text-sm font-semibold mb-2">Access Token</label>
              <input
                type="password"
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                placeholder="Enter Zerodha Access Token"
                className="w-full bg-charcoal-700 border-2 border-gold-500 border-opacity-30 rounded-lg px-4 py-2 text-gold-300 placeholder-gray-500 focus:outline-none focus:border-gold-500 focus:border-opacity-100 transition-all"
              />
              <p className="text-gray-500 text-xs mt-1">Your Zerodha session access token</p>
            </div>

            <button
              onClick={handleSaveConfig}
              className="w-full bg-gold-500 hover:bg-gold-600 text-charcoal-900 font-bold py-2 px-4 rounded-lg transition-colors mt-4"
            >
              {configSaved ? '✓ Configuration Saved' : 'Save Configuration'}
            </button>

            {configSaved && (
              <div className="bg-green-950 border-2 border-green-500 rounded-lg p-3 text-center">
                <p className="text-green-300 text-sm font-semibold">API credentials saved successfully!</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Zerodha Integration */}
      <ZerodhaIntegration />
    </div>
  )
}
