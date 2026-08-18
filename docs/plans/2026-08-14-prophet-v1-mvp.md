# Prophet V1.0 MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use godmode:delegated-execution or godmode:task-runner to implement this plan task-by-task.

**Goal:** Build a multi-market stock intelligence platform that screens stocks across three horizons (long-term, swing, intraday), generates AI-assisted trade suggestions, and integrates with Zerodha for portfolio tracking and execution.

**Architecture:** 
- **Backend (Python/FastAPI):** REST API with background jobs for stock screening, indicator calculation, news ingestion, and AI trade suggestions. Database stores watchlists, trades, holdings.
- **Frontend (React/TypeScript):** Dashboard with four main sections (Home, Eddie's Watchlist, Stock Analyzer, P&L). WebSocket connection for real-time updates.
- **Data Layer:** yfinance for OHLCV, Finnhub for US news, Google News RSS for Indian/geo news, Zerodha Kite Connect for portfolio sync, DeepSeek V4 for sentiment/AI suggestions.
- **Real-time Scanning:** Background polling job fetches 1-min candles every 30-60s, calculates indicators, flags RSI/ADX breaches into watchlist.

**Tech Stack:** Python 3.11, FastAPI, PostgreSQL, SQLAlchemy, React 18, TypeScript, TailwindCSS, WebSocket, Docker

---

## Phase 1: Project Setup & Core Infrastructure

### Task 1: Backend Project Setup

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/.env.example`
- Create: `backend/src/__init__.py`
- Create: `backend/src/config.py`
- Create: `backend/src/main.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "prophet-v1"
version = "1.0.0"
description = "Multi-market stock intelligence & AI trading platform"
requires-python = ">=3.11"
dependencies = [
    "fastapi==0.104.1",
    "uvicorn==0.24.0",
    "sqlalchemy==2.0.23",
    "psycopg2-binary==2.9.9",
    "yfinance==0.2.32",
    "pandas==2.1.3",
    "pandas-ta==0.3.14b",
    "requests==2.31.0",
    "feedparser==6.0.10",
    "httpx==0.25.1",
    "pydantic==2.5.0",
    "python-dotenv==1.0.0",
    "apscheduler==3.10.4",
    "pytest==7.4.3",
    "pytest-asyncio==0.21.1",
]

[project.optional-dependencies]
dev = [
    "black==23.12.0",
    "flake8==6.1.0",
    "mypy==1.7.0",
]
```

**Step 2: Create requirements.txt**

```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
yfinance==0.2.32
pandas==2.1.3
pandas-ta==0.3.14b
requests==2.31.0
feedparser==6.0.10
httpx==0.25.1
pydantic==2.5.0
python-dotenv==1.0.0
apscheduler==3.10.4
pytest==7.4.3
pytest-asyncio==0.21.1
```

**Step 3: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/src ./src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Step 4: Create .env.example**

```
DATABASE_URL=postgresql://prophet:password@localhost:5432/prophet_db
DEEPSEEK_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
ZERODHA_API_KEY=your_key_here
ZERODHA_API_SECRET=your_secret_here
ZERODHA_REQUEST_TOKEN=your_token_here
DEBUG=True
```

**Step 5: Create backend/src/config.py**

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://prophet:password@localhost:5432/prophet_db")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")
    zerodha_api_key: str = os.getenv("ZERODHA_API_KEY", "")
    zerodha_api_secret: str = os.getenv("ZERODHA_API_SECRET", "")
    zerodha_request_token: str = os.getenv("ZERODHA_REQUEST_TOKEN", "")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 6: Create backend/src/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

app = FastAPI(
    title="Prophet V1.0",
    description="Multi-market stock intelligence & AI trading platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Step 7: Create backend/src/__init__.py**

```python
__version__ = "1.0.0"
```

**Step 8: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add backend/ docs/
git commit -m "chore: initialize backend project structure with FastAPI"
```

---

### Task 2: Database Setup

**Files:**
- Create: `backend/src/database.py`
- Create: `backend/src/models.py`
- Create: `docker-compose.yml`

**Step 1: Create backend/src/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: Create backend/src/models.py**

```python
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, index=True)
    name = Column(String(255))
    market = Column(String(10))  # "US" or "IN"
    created_at = Column(DateTime, default=datetime.utcnow)

class TradeHorizon(str, enum.Enum):
    LONG_TERM = "long_term"
    SWING = "swing"
    INTRADAY = "intraday"

class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer)
    symbol = Column(String(20), index=True)
    horizon = Column(SQLEnum(TradeHorizon))
    direction = Column(String(10))  # "long" or "short"
    rsi = Column(Float)
    adx = Column(Float)
    momentum = Column(Float)
    current_price = Column(Float)
    volume_ratio = Column(Float)  # current / avg
    breakout_timestamp = Column(DateTime)
    added_at = Column(DateTime, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    horizon = Column(SQLEnum(TradeHorizon))
    direction = Column(String(10))  # "long" or "short"
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float)
    target_price = Column(Float)
    quantity = Column(Integer)
    status = Column(String(20))  # "open", "closed", "cancelled"
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)

class Holding(Base):
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    quantity = Column(Integer)
    average_price = Column(Float)
    current_price = Column(Float)
    market_value = Column(Float)
    unrealised_pnl = Column(Float)
    unrealised_pnl_percent = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

class CustomWatchlist(Base):
    __tablename__ = "custom_watchlist"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(500), nullable=True)
```

**Step 3: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: prophet
      POSTGRES_PASSWORD: password
      POSTGRES_DB: prophet_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U prophet"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://prophet:password@postgres:5432/prophet_db
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      FINNHUB_API_KEY: ${FINNHUB_API_KEY}
      DEBUG: "True"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

**Step 4: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add backend/src/database.py backend/src/models.py docker-compose.yml
git commit -m "feat: add database models and docker-compose setup"
```

---

### Task 3: Frontend Project Setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/index.html`

**Step 1: Create frontend/package.json**

```json
{
  "name": "prophet-v1",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .ts,.tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.10.3",
    "axios": "^1.6.1",
    "ws": "^8.15.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31"
  }
}
```

**Step 2: Create frontend/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "resolveJsonModule": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleResolution": "node"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

**Step 3: Create frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

**Step 4: Create frontend/tailwind.config.js**

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#fefef5',
          100: '#fdfce8',
          300: '#faf77d',
          500: '#d4af37',
          700: '#997f1a',
        },
        charcoal: {
          900: '#1a1a1a',
          800: '#2d2d2d',
          700: '#404040',
        },
      },
    },
  },
  plugins: [],
}
```

**Step 5: Create frontend/index.html**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Prophet V1.0 - Stock Intelligence Platform</title>
  </head>
  <body class="bg-charcoal-900 text-white">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Step 6: Create frontend/src/main.tsx**

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**Step 7: Create frontend/src/App.tsx**

```typescript
import { useState } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('home')

  return (
    <div className="min-h-screen bg-charcoal-900">
      <nav className="bg-charcoal-800 border-b-2 border-gold-500 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gold-500 mb-6">Prophet V1.0</h1>
          <div className="flex gap-6">
            {['home', 'watchlist', 'analyzer', 'pnl'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-semibold transition-colors ${
                  activeTab === tab
                    ? 'text-gold-500 border-b-2 border-gold-500'
                    : 'text-gray-300 hover:text-gold-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        {activeTab === 'home' && <div className="text-gray-300">Home Dashboard - Coming Soon</div>}
        {activeTab === 'watchlist' && <div className="text-gray-300">Eddie's Watchlist - Coming Soon</div>}
        {activeTab === 'analyzer' && <div className="text-gray-300">Stock Analyzer - Coming Soon</div>}
        {activeTab === 'pnl' && <div className="text-gray-300">P&L Tracking - Coming Soon</div>}
      </main>
    </div>
  )
}

export default App
```

**Step 8: Create frontend/src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

**Step 9: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add frontend/
git commit -m "chore: initialize React frontend with Vite and TailwindCSS"
```

---

## Phase 2: Data Layer & Core Services

### Task 4: Indicator Calculation Service

**Files:**
- Create: `backend/src/services/indicators.py`
- Create: `backend/tests/test_indicators.py`

**Step 1: Write failing test**

```python
# backend/tests/test_indicators.py
import pytest
import pandas as pd
from src.services.indicators import IndicatorCalculator

@pytest.fixture
def sample_ohlcv():
    return pd.DataFrame({
        'Open': [100, 101, 102, 103, 104, 105],
        'High': [102, 103, 104, 105, 106, 107],
        'Low': [99, 100, 101, 102, 103, 104],
        'Close': [101, 102, 103, 104, 105, 106],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500],
    }, index=pd.date_range('2024-01-01', periods=6))

def test_rsi_calculation(sample_ohlcv):
    calc = IndicatorCalculator()
    rsi = calc.calculate_rsi(sample_ohlcv['Close'], period=14)
    assert len(rsi) == len(sample_ohlcv)
    assert rsi.iloc[-1] > 0 and rsi.iloc[-1] < 100

def test_adx_calculation(sample_ohlcv):
    calc = IndicatorCalculator()
    adx = calc.calculate_adx(sample_ohlcv, period=14)
    assert len(adx) == len(sample_ohlcv)
    assert adx.iloc[-1] >= 0 and adx.iloc[-1] <= 100

def test_momentum_calculation(sample_ohlcv):
    calc = IndicatorCalculator()
    momentum = calc.calculate_momentum(sample_ohlcv['Close'], period=10)
    assert len(momentum) == len(sample_ohlcv)
```

**Step 2: Run test to verify failure**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
python -m pytest backend/tests/test_indicators.py -v
```

Expected: FAIL (IndicatorCalculator not defined)

**Step 3: Implement indicator service**

```python
# backend/src/services/indicators.py
import pandas as pd
import numpy as np

class IndicatorCalculator:
    """Calculate technical indicators: RSI, ADX, Momentum"""
    
    @staticmethod
    def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
        """RSI = 100 - (100 / (1 + RS)) where RS = avg gain / avg loss"""
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_adx(ohlc: pd.DataFrame, period: int = 14) -> pd.Series:
        """ADX = directional movement indicator"""
        high = ohlc['High']
        low = ohlc['Low']
        close = ohlc['Close']
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        return adx
    
    @staticmethod
    def calculate_momentum(close: pd.Series, period: int = 10) -> pd.Series:
        """Momentum = close - close[n periods ago]"""
        return close - close.shift(period)
```

**Step 4: Run test to verify pass**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
python -m pytest backend/tests/test_indicators.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add backend/src/services/ backend/tests/
git commit -m "feat: implement RSI, ADX, Momentum indicator calculations"
```

---

### Task 5: Data Fetcher Service

**Files:**
- Create: `backend/src/services/data_fetcher.py`
- Create: `backend/tests/test_data_fetcher.py`

**Step 1: Write failing test**

```python
# backend/tests/test_data_fetcher.py
import pytest
from unittest.mock import patch, MagicMock
from src.services.data_fetcher import DataFetcher

@pytest.mark.asyncio
async def test_fetch_ohlcv_data():
    fetcher = DataFetcher()
    with patch('yfinance.download') as mock_download:
        mock_download.return_value = MagicMock()
        result = await fetcher.fetch_ohlcv('AAPL', period='1d')
        assert result is not None

@pytest.mark.asyncio
async def test_fetch_news_finnhub():
    fetcher = DataFetcher()
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'news': []}
        result = await fetcher.fetch_news_finnhub('AAPL')
        assert isinstance(result, list)

@pytest.mark.asyncio
async def test_fetch_news_google_rss():
    fetcher = DataFetcher()
    with patch('feedparser.parse') as mock_parse:
        mock_parse.return_value = {'entries': []}
        result = await fetcher.fetch_news_google_rss('TCS')
        assert isinstance(result, list)
```

**Step 2: Run test to verify failure**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
python -m pytest backend/tests/test_data_fetcher.py -v
```

Expected: FAIL (DataFetcher not defined)

**Step 3: Implement data fetcher**

```python
# backend/src/services/data_fetcher.py
import asyncio
import yfinance
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from src.config import settings

class DataFetcher:
    """Fetch OHLCV data and news from multiple sources"""
    
    async def fetch_ohlcv(self, symbol: str, period: str = '1d', interval: str = '1m') -> Optional[pd.DataFrame]:
        """Fetch OHLCV data using yfinance"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: yfinance.download(
                    symbol,
                    period=period,
                    interval=interval,
                    progress=False
                )
            )
            return data if not data.empty else None
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return None
    
    async def fetch_news_finnhub(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Fetch US company news from Finnhub"""
        if not settings.finnhub_api_key:
            return []
        
        try:
            url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&limit={limit}&token={settings.finnhub_api_key}"
            response = await asyncio.to_thread(requests.get, url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching Finnhub news: {e}")
            return []
    
    async def fetch_news_google_rss(self, ticker: str, limit: int = 10) -> List[Dict]:
        """Fetch news from Google News RSS (Indian + geopolitical coverage)"""
        try:
            url = f"https://news.google.com/rss/search?q={ticker}&hl=en-IN&gl=IN&ceid=IN:en"
            feed = await asyncio.to_thread(feedparser.parse, url)
            
            news = []
            for entry in feed.entries[:limit]:
                news.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'summary': entry.get('summary', '')
                })
            return news
        except Exception as e:
            print(f"Error fetching Google News RSS: {e}")
            return []
    
    async def fetch_earnings_calendar(self, market: str = 'US') -> List[Dict]:
        """Fetch upcoming earnings using Finnhub"""
        if not settings.finnhub_api_key:
            return []
        
        try:
            today = datetime.now().date()
            from_date = today
            to_date = today + timedelta(days=30)
            
            url = f"https://finnhub.io/api/v1/calendar/earnings?from={from_date}&to={to_date}&token={settings.finnhub_api_key}"
            response = await asyncio.to_thread(requests.get, url, timeout=5)
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching earnings calendar: {e}")
            return []
```

**Step 4: Run test to verify pass**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
python -m pytest backend/tests/test_data_fetcher.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add backend/src/services/data_fetcher.py backend/tests/test_data_fetcher.py
git commit -m "feat: implement data fetcher for OHLCV, news, earnings calendar"
```

---

### Task 6: AI Trade Suggestion Service (DeepSeek V4)

**Files:**
- Create: `backend/src/services/ai_engine.py`
- Create: `backend/tests/test_ai_engine.py`

**Step 1: Write failing test**

```python
# backend/tests/test_ai_engine.py
import pytest
from unittest.mock import patch, AsyncMock
from src.services.ai_engine import AIEngine

@pytest.mark.asyncio
async def test_generate_trade_suggestion():
    engine = AIEngine()
    
    market_data = {
        'symbol': 'AAPL',
        'current_price': 150.00,
        'rsi': 65,
        'adx': 25,
        'momentum': 5.2,
        'volatility': 0.18,
    }
    
    news_sentiment = {
        'bullish_count': 3,
        'bearish_count': 1,
        'sentiment_score': 0.65,
    }
    
    with patch.object(engine, '_call_deepseek_api', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = {
            'entry_price': 149.50,
            'stop_loss': 148.00,
            'target_exit': 155.00,
            'confidence': 0.75,
            'rationale': 'Bullish RSI divergence with positive earnings sentiment'
        }
        
        result = await engine.generate_trade_suggestion(market_data, news_sentiment)
        assert 'entry_price' in result
        assert 'stop_loss' in result
        assert 'target_exit' in result
```

**Step 2: Run test to verify failure**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
python -m pytest backend/tests/test_ai_engine.py -v
```

Expected: FAIL

**Step 3: Implement AI engine**

```python
# backend/src/services/ai_engine.py
import httpx
import json
from typing import Dict, Optional
from src.config import settings

class AIEngine:
    """AI-powered trade suggestions using DeepSeek V4"""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = "https://api.deepseek.com/v1"
    
    async def generate_trade_suggestion(
        self,
        market_data: Dict,
        news_sentiment: Dict,
        horizon: str = "intraday"
    ) -> Dict:
        """Generate AI-powered trade entry/exit/stop-loss using DeepSeek V4"""
        
        prompt = self._build_prompt(market_data, news_sentiment, horizon)
        
        try:
            response = await self._call_deepseek_api(prompt)
            return self._parse_response(response)
        except Exception as e:
            print(f"Error generating trade suggestion: {e}")
            return self._fallback_suggestion(market_data)
    
    def _build_prompt(self, market_data: Dict, news_sentiment: Dict, horizon: str) -> str:
        """Build the prompt for DeepSeek V4"""
        return f"""
        Analyze this stock and generate a trade recommendation:
        
        Symbol: {market_data.get('symbol')}
        Current Price: ${market_data.get('current_price')}
        RSI: {market_data.get('rsi')}
        ADX: {market_data.get('adx')}
        Momentum: {market_data.get('momentum')}
        Volatility: {market_data.get('volatility')}
        
        News Sentiment:
        Bullish Headlines: {news_sentiment.get('bullish_count')}
        Bearish Headlines: {news_sentiment.get('bearish_count')}
        Sentiment Score: {news_sentiment.get('sentiment_score')}
        
        Trading Horizon: {horizon}
        
        Provide a JSON response with:
        {{
            "entry_price": <float>,
            "stop_loss": <float>,
            "target_exit": <float>,
            "confidence": <0-1>,
            "rationale": "<brief explanation>"
        }}
        """
    
    async def _call_deepseek_api(self, prompt: str) -> str:
        """Call DeepSeek V4 API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "deepseek-v4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                }
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
    
    def _parse_response(self, response: str) -> Dict:
        """Parse DeepSeek JSON response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Error parsing DeepSeek response: {e}")
        
        return self._fallback_suggestion({})
    
    def _fallback_suggestion(self, market_data: Dict) -> Dict:
        """Fallback suggestion when API fails"""
        price = market_data.get('current_price', 100)
        return {
            'entry_price': price * 0.99,
            'stop_loss': price * 0.95,
            'target_exit': price * 1.05,
            'confidence': 0.5,
            'rationale': 'Fallback suggestion - API unavailable'
        }
```

**Step 4: Run test to verify pass**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
python -m pytest backend/tests/test_ai_engine.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add backend/src/services/ai_engine.py backend/tests/test_ai_engine.py
git commit -m "feat: implement AI trade suggestion engine with DeepSeek V4"
```

---

## Phase 3: Stock Screening Logic

### Task 7: Stock Screening Service

**Files:**
- Create: `backend/src/services/screening.py`
- Create: `backend/tests/test_screening.py`

**Step 1: Write failing test**

```python
# backend/tests/test_screening.py
import pytest
import pandas as pd
from src.services.screening import StockScreener

@pytest.fixture
def sample_ohlcv():
    return pd.DataFrame({
        'Open': [100 + i for i in range(50)],
        'High': [102 + i for i in range(50)],
        'Low': [99 + i for i in range(50)],
        'Close': [101 + i for i in range(50)],
        'Volume': [1000 + i*100 for i in range(50)],
    }, index=pd.date_range('2024-01-01', periods=50))

def test_screen_intraday_breakout(sample_ohlcv):
    screener = StockScreener()
    candidates = screener.screen_intraday_breakout(sample_ohlcv, 'AAPL')
    assert isinstance(candidates, list)

def test_screen_swing_trading(sample_ohlcv):
    screener = StockScreener()
    candidates = screener.screen_swing_trading(sample_ohlcv, 'AAPL')
    assert isinstance(candidates, list)

def test_screen_long_term(sample_ohlcv):
    screener = StockScreener()
    candidates = screener.screen_long_term(sample_ohlcv, 'AAPL')
    assert isinstance(candidates, list)
```

**Step 2: Run test to verify failure**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
python -m pytest backend/tests/test_screening.py -v
```

Expected: FAIL

**Step 3: Implement screening service**

```python
# backend/src/services/screening.py
import pandas as pd
from typing import List, Dict, Optional
from src.services.indicators import IndicatorCalculator

class StockScreener:
    """Screen stocks across three horizons using technical indicators"""
    
    def __init__(self):
        self.calc = IndicatorCalculator()
        self.rsi_upper_band = 70
        self.rsi_lower_band = 30
        self.adx_threshold = 20
        self.volume_threshold_multiplier = 1.2
    
    def screen_intraday_breakout(self, ohlcv: pd.DataFrame, symbol: str) -> List[Dict]:
        """Screen for intraday RSI breakouts with ADX confirmation"""
        candidates = []
        
        if len(ohlcv) < 30:
            return candidates
        
        rsi = self.calc.calculate_rsi(ohlcv['Close'])
        adx = self.calc.calculate_adx(ohlcv)
        
        current_rsi = rsi.iloc[-1]
        current_adx = adx.iloc[-1]
        current_price = ohlcv['Close'].iloc[-1]
        current_volume = ohlcv['Volume'].iloc[-1]
        avg_volume = ohlcv['Volume'].iloc[-20:].mean()
        
        rsi_breakout_up = (rsi.iloc[-2] <= self.rsi_upper_band) and (current_rsi > self.rsi_upper_band)
        rsi_breakout_down = (rsi.iloc[-2] >= self.rsi_lower_band) and (current_rsi < self.rsi_lower_band)
        volume_confirmed = current_volume > (avg_volume * self.volume_threshold_multiplier)
        adx_confirmed = current_adx > self.adx_threshold
        
        if rsi_breakout_up and adx_confirmed and volume_confirmed:
            candidates.append({
                'symbol': symbol,
                'direction': 'long',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'volume_ratio': float(current_volume / avg_volume),
                'breakout_type': 'RSI_UPPER_BAND'
            })
        
        if rsi_breakout_down and adx_confirmed and volume_confirmed:
            candidates.append({
                'symbol': symbol,
                'direction': 'short',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'volume_ratio': float(current_volume / avg_volume),
                'breakout_type': 'RSI_LOWER_BAND'
            })
        
        return candidates
    
    def screen_swing_trading(self, ohlcv: pd.DataFrame, symbol: str) -> List[Dict]:
        """Screen for swing trading: RSI + ADX + Momentum"""
        candidates = []
        
        if len(ohlcv) < 30:
            return candidates
        
        rsi = self.calc.calculate_rsi(ohlcv['Close'])
        adx = self.calc.calculate_adx(ohlcv)
        momentum = self.calc.calculate_momentum(ohlcv['Close'])
        
        current_rsi = rsi.iloc[-1]
        current_adx = adx.iloc[-1]
        current_momentum = momentum.iloc[-1]
        current_price = ohlcv['Close'].iloc[-1]
        
        # Bullish swing setup
        if (30 < current_rsi < 70) and (current_adx > self.adx_threshold) and (current_momentum > 0):
            candidates.append({
                'symbol': symbol,
                'direction': 'long',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'momentum': float(current_momentum),
                'pattern': 'BULLISH_SWING'
            })
        
        # Bearish swing setup
        if (30 < current_rsi < 70) and (current_adx > self.adx_threshold) and (current_momentum < 0):
            candidates.append({
                'symbol': symbol,
                'direction': 'short',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'momentum': float(current_momentum),
                'pattern': 'BEARISH_SWING'
            })
        
        return candidates
    
    def screen_long_term(self, ohlcv: pd.DataFrame, symbol: str) -> List[Dict]:
        """Screen for long-term investing: trend + momentum + fundamentals check"""
        candidates = []
        
        if len(ohlcv) < 200:
            return candidates
        
        rsi = self.calc.calculate_rsi(ohlcv['Close'], period=14)
        adx = self.calc.calculate_adx(ohlcv, period=14)
        momentum = self.calc.calculate_momentum(ohlcv['Close'], period=50)
        
        sma_50 = ohlcv['Close'].rolling(window=50).mean()
        sma_200 = ohlcv['Close'].rolling(window=200).mean()
        
        current_price = ohlcv['Close'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_adx = adx.iloc[-1]
        current_momentum = momentum.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        current_sma_200 = sma_200.iloc[-1]
        
        # Bullish long-term setup
        if (current_price > current_sma_50 > current_sma_200) and (40 < current_rsi < 80) and (current_adx > 15):
            candidates.append({
                'symbol': symbol,
                'direction': 'long',
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'adx': float(current_adx),
                'momentum': float(current_momentum),
                'pattern': 'UPTREND_SMA_CROSS'
            })
        
        return candidates
```

**Step 4: Run test to verify pass**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
python -m pytest backend/tests/test_screening.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add backend/src/services/screening.py backend/tests/test_screening.py
git commit -m "feat: implement three-horizon stock screening logic"
```

---

## Phase 4: API Endpoints & WebSocket

### Task 8: RESTful API Endpoints

**Files:**
- Create: `backend/src/routes/__init__.py`
- Create: `backend/src/routes/stocks.py`
- Create: `backend/src/routes/watchlist.py`
- Create: `backend/src/routes/portfolio.py`
- Modify: `backend/src/main.py`

**Step 1: Create backend/src/routes/__init__.py**

```python
# Empty init file
```

**Step 2: Create backend/src/routes/stocks.py**

```python
# backend/src/routes/stocks.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Stock
from src.services.data_fetcher import DataFetcher
from src.services.indicators import IndicatorCalculator
from src.services.ai_engine import AIEngine
from typing import Dict, List

router = APIRouter(prefix="/api/stocks", tags=["stocks"])
fetcher = DataFetcher()
calc = IndicatorCalculator()
ai_engine = AIEngine()

@router.get("/{symbol}/indicators")
async def get_stock_indicators(symbol: str):
    """Fetch OHLCV and calculate technical indicators"""
    try:
        ohlcv = await fetcher.fetch_ohlcv(symbol, period='60d', interval='1d')
        if ohlcv is None or ohlcv.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        rsi = calc.calculate_rsi(ohlcv['Close'])
        adx = calc.calculate_adx(ohlcv)
        momentum = calc.calculate_momentum(ohlcv['Close'])
        
        return {
            'symbol': symbol,
            'current_price': float(ohlcv['Close'].iloc[-1]),
            'rsi': float(rsi.iloc[-1]),
            'adx': float(adx.iloc[-1]),
            'momentum': float(momentum.iloc[-1]),
            'volume': int(ohlcv['Volume'].iloc[-1]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{symbol}/news")
async def get_stock_news(symbol: str):
    """Fetch news for a stock"""
    try:
        news = await fetcher.fetch_news_finnhub(symbol, limit=10)
        return {'symbol': symbol, 'news': news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{symbol}/trade-suggestion")
async def generate_trade_suggestion(symbol: str):
    """Generate AI trade suggestion"""
    try:
        ohlcv = await fetcher.fetch_ohlcv(symbol, period='60d', interval='1d')
        if ohlcv is None or ohlcv.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        rsi = calc.calculate_rsi(ohlcv['Close'])
        adx = calc.calculate_adx(ohlcv)
        volatility = ohlcv['Close'].pct_change().std()
        
        market_data = {
            'symbol': symbol,
            'current_price': float(ohlcv['Close'].iloc[-1]),
            'rsi': float(rsi.iloc[-1]),
            'adx': float(adx.iloc[-1]),
            'volatility': float(volatility),
        }
        
        news = await fetcher.fetch_news_finnhub(symbol, limit=5)
        bullish = sum(1 for n in news if 'up' in n.get('headline', '').lower())
        bearish = sum(1 for n in news if 'down' in n.get('headline', '').lower())
        
        news_sentiment = {
            'bullish_count': bullish,
            'bearish_count': bearish,
            'sentiment_score': (bullish - bearish) / (bullish + bearish + 1)
        }
        
        suggestion = await ai_engine.generate_trade_suggestion(market_data, news_sentiment)
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 3: Create backend/src/routes/watchlist.py**

```python
# backend/src/routes/watchlist.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import WatchlistEntry, TradeHorizon
from typing import List

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

@router.get("")
async def get_watchlist(db: Session = Depends(get_db)):
    """Get current watchlist entries"""
    entries = db.query(WatchlistEntry).filter(WatchlistEntry.removed_at == None).all()
    return {
        'long_candidates': [e for e in entries if e.direction == 'long'],
        'short_candidates': [e for e in entries if e.direction == 'short'],
        'count': len(entries)
    }

@router.post("/{symbol}")
async def add_to_watchlist(symbol: str, horizon: TradeHorizon, db: Session = Depends(get_db)):
    """Add stock to watchlist"""
    entry = WatchlistEntry(
        symbol=symbol,
        horizon=horizon,
        direction='long'
    )
    db.add(entry)
    db.commit()
    return {'status': 'added', 'symbol': symbol}

@router.delete("/{entry_id}")
async def remove_from_watchlist(entry_id: int, db: Session = Depends(get_db)):
    """Remove from watchlist"""
    entry = db.query(WatchlistEntry).get(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {'status': 'removed'}
```

**Step 4: Create backend/src/routes/portfolio.py**

```python
# backend/src/routes/portfolio.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Holding, Trade
from typing import List

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

@router.get("/holdings")
async def get_holdings(db: Session = Depends(get_db)):
    """Get current holdings"""
    holdings = db.query(Holding).all()
    total_value = sum(h.market_value for h in holdings)
    total_pnl = sum(h.unrealised_pnl for h in holdings)
    return {
        'holdings': holdings,
        'total_value': total_value,
        'total_pnl': total_pnl,
        'total_pnl_percent': (total_pnl / total_value * 100) if total_value > 0 else 0
    }

@router.get("/trades")
async def get_trades(db: Session = Depends(get_db)):
    """Get trade history"""
    trades = db.query(Trade).order_by(Trade.entry_time.desc()).all()
    
    closed_trades = [t for t in trades if t.status == 'closed']
    total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
    win_count = sum(1 for t in closed_trades if t.pnl and t.pnl > 0)
    win_rate = (win_count / len(closed_trades) * 100) if closed_trades else 0
    
    best_trade = max(closed_trades, key=lambda t: t.pnl, default=None)
    
    return {
        'trades': trades,
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'best_trade': best_trade,
    }

@router.post("/trades")
async def create_trade(trade_data: dict, db: Session = Depends(get_db)):
    """Create a new trade"""
    trade = Trade(**trade_data)
    db.add(trade)
    db.commit()
    return {'status': 'created', 'trade_id': trade.id}
```

**Step 5: Update backend/src/main.py to include routes**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.routes import stocks, watchlist, portfolio

app = FastAPI(
    title="Prophet V1.0",
    description="Multi-market stock intelligence & AI trading platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(watchlist.router)
app.include_router(portfolio.router)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Step 6: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add backend/src/routes/ backend/src/main.py
git commit -m "feat: add RESTful API endpoints for stocks, watchlist, portfolio"
```

---

### Task 9: Background Polling Job

**Files:**
- Create: `backend/src/jobs/__init__.py`
- Create: `backend/src/jobs/polling_engine.py`
- Modify: `backend/src/main.py`

**Step 1: Create backend/src/jobs/__init__.py**

```python
# Empty init file
```

**Step 2: Create backend/src/jobs/polling_engine.py**

```python
# backend/src/jobs/polling_engine.py
import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.services.data_fetcher import DataFetcher
from src.services.screening import StockScreener
from src.services.indicators import IndicatorCalculator
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import WatchlistEntry, TradeHorizon
import pandas as pd

class PollingEngine:
    """Background job that continuously polls and screens stocks"""
    
    def __init__(self):
        self.fetcher = DataFetcher()
        self.screener = StockScreener()
        self.calc = IndicatorCalculator()
        self.ticker_universe = [
            'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN',  # US
            'TCS.BO', 'INFY.BO', 'RELIANCE.NS', 'HDFC.BO'  # Indian
        ]
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """Start background polling"""
        self.scheduler.add_job(
            self.scan_intraday,
            'interval',
            seconds=45,
            id='intraday_scan',
            name='Intraday Breakout Scan'
        )
        
        self.scheduler.add_job(
            self.scan_swing,
            'interval',
            minutes=15,
            id='swing_scan',
            name='Swing Trading Scan'
        )
        
        self.scheduler.add_job(
            self.scan_long_term,
            'interval',
            hours=1,
            id='longterm_scan',
            name='Long-term Investing Scan'
        )
        
        self.scheduler.start()
    
    async def scan_intraday(self):
        """Scan for intraday breakouts"""
        print("[POLL] Starting intraday scan...")
        
        for symbol in self.ticker_universe:
            try:
                ohlcv = await self.fetcher.fetch_ohlcv(symbol, period='5d', interval='1m')
                if ohlcv is None or ohlcv.empty:
                    continue
                
                candidates = self.screener.screen_intraday_breakout(ohlcv, symbol)
                
                if candidates:
                    db = SessionLocal()
                    for candidate in candidates:
                        existing = db.query(WatchlistEntry).filter(
                            WatchlistEntry.symbol == symbol,
                            WatchlistEntry.horizon == TradeHorizon.INTRADAY,
                            WatchlistEntry.removed_at == None
                        ).first()
                        
                        if not existing:
                            entry = WatchlistEntry(
                                symbol=symbol,
                                horizon=TradeHorizon.INTRADAY,
                                direction=candidate['direction'],
                                rsi=candidate['rsi'],
                                adx=candidate['adx'],
                                current_price=candidate['current_price'],
                                volume_ratio=candidate['volume_ratio'],
                                breakout_timestamp=datetime.utcnow()
                            )
                            db.add(entry)
                    
                    db.commit()
                    db.close()
                    print(f"  Found {len(candidates)} intraday candidate(s) for {symbol}")
            
            except Exception as e:
                print(f"  Error scanning {symbol}: {e}")
    
    async def scan_swing(self):
        """Scan for swing trading opportunities"""
        print("[POLL] Starting swing trading scan...")
        # Similar to intraday but uses screen_swing_trading()
    
    async def scan_long_term(self):
        """Scan for long-term investing opportunities"""
        print("[POLL] Starting long-term investing scan...")
        # Similar to intraday but uses screen_long_term()
```

**Step 2: Update main.py to start polling**

```python
# Add to backend/src/main.py
from src.jobs.polling_engine import PollingEngine

polling_engine = PollingEngine()

@app.on_event("startup")
async def startup_event():
    polling_engine.start()

@app.on_event("shutdown")
async def shutdown_event():
    polling_engine.scheduler.shutdown()
```

**Step 3: Commit**

```bash
cd "/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0"
git add backend/src/jobs/ backend/src/main.py
git commit -m "feat: implement background polling engine for continuous stock screening"
```

---

## Execution Options

**Plan saved to:** `/home/cyberwarrior/Desktop/AI Job Prep/Prophet V1.0/docs/plans/2026-08-14-prophet-v1-mvp.md`

---

**Now, two execution options:**

1. **Delegated Execution (this session)** — I dispatch fresh subagents per task, review between tasks for rapid iteration
2. **Separate Session** — You open a new session with `godmode:task-runner` for batch execution with checkpoints

**Which would you prefer?**