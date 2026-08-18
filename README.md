# Prophet-V1.0
A market intelligence tool
# Prophet V1.0 - AI-Powered Stock Analysis & Trading Platform

**An intelligent stock analysis system combining technical analysis, fundamental research, and AI predictions for swing trading and long-term investment decisions.**

![Prophet V1.0](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/Status-Active-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

Prophet V1.0 is a comprehensive stock analysis platform designed for Indian retail investors and day traders. It combines:

- **Real-time Market Data** from Finnhub, Twelve Data, and yfinance
- **AI-Powered Analysis** using DeepSeek AI for intelligent insights
- **Technical Analysis** with swing trade predictions and hold time forecasts
- **Fundamental Analysis** for long-term investment decisions
- **Portfolio Tracking** with Zerodha broker integration
- **Intraday Trading Signals** through the Eddie Intraday module

The platform provides a user-friendly web interface for analyzing stocks, managing watchlists, and tracking portfolio performance.

---

## ✨ Key Features

### 1. **Stock Analyzer Module**
- **Short-Term Analysis**: Technical analysis for immediate trading opportunities
- **Swing Trade Predictions**: AI-generated predictions with hold time estimates and gain forecasts
- **Long-Term Fundamental Analysis**: Company metrics, financial health, and growth potential
- **AI Insights**: Powered by DeepSeek for intelligent market analysis

### 2. **Eddie Intraday Module**
- Real-time intraday trading signals
- Technical indicators (RSI, MACD, Bollinger Bands)
- Support and resistance levels
- Entry/exit point recommendations

### 3. **Portfolio Management**
- Watchlist management with custom tracking
- P&L tracking with Zerodha integration
- Performance analytics and historical data
- Multi-stock portfolio overview

### 4. **Market Intelligence**
- Live price updates
- Historical price data and trends
- Market news integration
- Technical indicators and charts

### 5. **Dashboard**
- Portfolio overview with key metrics
- Quick access to analysis tools
- Recent activity and notifications
- Performance statistics

---

## 🛠 Technology Stack

### **Backend**
| Technology | Purpose | Version |
|-----------|---------|---------|
| FastAPI | Web framework | 0.104.1 |
| PostgreSQL | Database | 16 |
| SQLAlchemy | ORM | 2.0.23 |
| Python | Language | 3.9+ |
| uvicorn | ASGI server | 0.24.0 |
| pandas | Data analysis | 2.0.0+ |
| numpy | Numerical computing | 1.24.3+ |
| yfinance | Market data | 1.6.0+ |
| APScheduler | Task scheduling | 3.10.4+ |

### **Frontend**
| Technology | Purpose | Version |
|-----------|---------|---------|
| React | UI framework | 18.2.0 |
| TypeScript | Type safety | 5.2.2 |
| Vite | Build tool | 5.0.8 |
| Tailwind CSS | Styling | 3.3.6 |
| Recharts | Charts & graphs | 2.10.3 |
| React Router | Navigation | 7.18.2 |
| Axios | HTTP client | 1.6.1 |

### **Infrastructure**
| Technology | Purpose |
|-----------|---------|
| Docker | Containerization |
| Docker Compose | Orchestration |
| WebSockets | Real-time updates |

### **APIs**
- **Finnhub** - Stock market data and news
- **Twelve Data** - Premium market data (optional)
- **DeepSeek** - AI-powered analysis
- **Zerodha** - Broker integration (optional)

---

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended)
  - OR **Python 3.9+** and **Node.js 18+**
- **API Keys** (get from respective providers):
  - DeepSeek: https://platform.deepseek.com/
  - Finnhub: https://finnhub.io/

### Option 1: Docker (Recommended - 5 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1

# Create .env file with your API keys
cp .env.example .env
# Edit .env and add your API keys
nano .env

# Start all services
docker-compose up -d

# Wait for services to start (check with: docker-compose ps)
# Then in another terminal, start the frontend:
cd frontend
npm install
npm run dev

# Access the application
# Frontend: http://localhost:8003
# Backend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Option 2: Local Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1

# Set up Backend (Terminal 1)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Start backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Set up Frontend (Terminal 2)
cd frontend
npm install
npm run dev

# Application URL: http://localhost:8003
```

---

## 📖 Detailed Setup

### Backend Setup

#### Step 1: Environment Configuration
```bash
cd backend

# Copy and customize environment file
cp .env.example .env

# Required environment variables
cat > .env << EOF
DATABASE_URL=postgresql://prophet:password@localhost:5433/prophet_db
DEEPSEEK_API_KEY=your_deepseek_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here
DEBUG=True
EOF
```

#### Step 2: Database Setup

**Using Docker (Recommended):**
```bash
# From project root
docker-compose up -d postgres

# Verify PostgreSQL is running
docker-compose ps postgres

# Check logs if needed
docker-compose logs postgres
```

**Using Local PostgreSQL:**
```bash
# Create database and user
psql -U postgres -c "CREATE DATABASE prophet_db;"
psql -U postgres -c "CREATE USER prophet WITH PASSWORD 'password';"
psql -U postgres -c "ALTER ROLE prophet WITH SUPERUSER;"
```

#### Step 3: Install Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Step 4: Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Check Health:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "1.0.0"}
```

### Frontend Setup

#### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

#### Step 2: Start Development Server
```bash
npm run dev
# Frontend will be available at http://localhost:8003
```

#### Step 3: Build for Production (Optional)
```bash
npm run build
npm run preview
```

### Populate Sample Data (Optional)

```bash
cd backend
python seed_eddie_watchlist.py      # Seed Eddie Intraday stocks
python populate_test_data.py        # Add test market data
```

---

## 📁 Project Structure

```
prophet-v1/
├── backend/                          # FastAPI backend
│   ├── src/
│   │   ├── main.py                  # Application entry point
│   │   ├── config.py                # Configuration settings
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── stock.py
│   │   │   ├── watchlist.py
│   │   │   └── trade.py
│   │   ├── routes/                  # API endpoints
│   │   │   ├── stocks.py
│   │   │   ├── analysis.py
│   │   │   ├── watchlist.py
│   │   │   ├── eddie.py
│   │   │   └── pnl.py
│   │   ├── services/                # Business logic
│   │   │   ├── stock_service.py
│   │   │   ├── analysis_service.py
│   │   │   ├── ai_service.py
│   │   │   └── zerodha_service.py
│   │   └── utils/                   # Utilities
│   │       ├── data_fetcher.py
│   │       ├── technical_analysis.py
│   │       └── cache.py
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   ├── Dockerfile                   # Docker configuration
│   └── seed_eddie_watchlist.py     # Sample data script
│
├── frontend/                         # React TypeScript frontend
│   ├── src/
│   │   ├── pages/                   # Page components
│   │   │   ├── Home.tsx
│   │   │   ├── StockAnalyzer.tsx
│   │   │   ├── EddieIntraday.tsx
│   │   │   ├── Watchlist.tsx
│   │   │   └── PnL.tsx
│   │   ├── components/              # Reusable components
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── StockChart.tsx
│   │   │   ├── PredictionCard.tsx
│   │   │   └── AnalysisPanel.tsx
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── services/                # API service layer
│   │   ├── types/                   # TypeScript types
│   │   ├── App.tsx                  # Root component
│   │   └── main.tsx                 # Entry point
│   ├── public/                      # Static assets
│   ├── package.json                 # Node dependencies
│   ├── tailwind.config.js           # Tailwind configuration
│   ├── tsconfig.json                # TypeScript configuration
│   └── vite.config.ts               # Vite configuration
│
├── docs/                            # Documentation
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── EDDIE_IMPLEMENTATION_COMPLETE.md
│   ├── LONG_TERM_PICKER.md
│   ├── FRONTEND_SUMMARY.md
│   └── EDDIE_CODE_REFERENCE.md
│
├── tests/                           # Test suite
│   ├── test_stock_analyzer.py
│   ├── test_api_endpoints.py
│   └── conftest.py
│
├── docker-compose.yml               # Docker services orchestration
├── Dockerfile                       # Backend Docker image
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
└── LICENSE                          # MIT License
```

---

## 🔌 API Documentation

### Base URL
- **Local**: `http://localhost:8000`
- **Docker**: `http://localhost:8001`

### Interactive API Docs
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Health Check
```
GET /health
```

#### Stock Analysis
```
GET /api/stocks/{symbol}
GET /api/stocks/search?query={symbol}
GET /api/analysis/{symbol}
```

#### Predictions
```
GET /api/predict/swing/{symbol}
GET /api/predict/long-term/{symbol}
```

#### Watchlist
```
GET /api/watchlist
POST /api/watchlist
DELETE /api/watchlist/{id}
```

#### Eddie Intraday
```
GET /api/eddie/signals
GET /api/eddie/stocks
POST /api/eddie/analyze/{symbol}
```

#### P&L Tracking
```
GET /api/pnl/portfolio
GET /api/pnl/trades
POST /api/pnl/trades
```

---

## 💡 Usage Guide

### 1. Getting Started with Stock Analyzer

1. Navigate to **Stock Analyzer** from the main menu
2. Enter a stock symbol (e.g., "RELIANCE", "TCS", "INFY")
3. View three analysis options:
   - **Short-Term**: Quick technical analysis
   - **Swing Mode**: AI predictions with hold time and gain forecast
   - **Long-Term**: Fundamental analysis for investments

### 2. Using Eddie Intraday

1. Open **Eddie Intraday** tab
2. View real-time intraday signals for selected stocks
3. Check technical indicators:
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Bollinger Bands
4. Review support/resistance levels and entry/exit points

### 3. Managing Watchlist

1. Go to **Watchlist** section
2. Click "Add Stock" to add symbols
3. Monitor price changes and set alerts
4. Remove stocks when no longer needed

### 4. Portfolio P&L Tracking

1. Open **P&L Tracking**
2. Link your Zerodha account (if available)
3. View:
   - Current holdings and P&L
   - Trade history and performance
   - Portfolio analytics

### 5. Dashboard Overview

- View portfolio summary
- Quick links to analysis tools
- Recent activity feed
- Key market metrics

---

## 🔧 Configuration

### Environment Variables

**Backend (.env file):**
```ini
# Database
DATABASE_URL=postgresql://prophet:password@localhost:5433/prophet_db

# API Keys
DEEPSEEK_API_KEY=sk-your-key-here
FINNHUB_API_KEY=your-finnhub-key-here
TWELVE_DATA_API_KEY=your-twelve-data-key-here

# Optional: Zerodha Integration
ZERODHA_API_KEY=your-zerodha-key-here
ZERODHA_API_SECRET=your-zerodha-secret-here

# Server
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Port Configuration

| Service | Default | Usage |
|---------|---------|-------|
| Frontend | 8003 | Web UI |
| Backend (Local) | 8000 | API Server |
| Backend (Docker) | 8001 | API Server |
| PostgreSQL | 5433 | Database |

---

## 🐛 Troubleshooting

### Backend Issues

**Issue: "Connection refused" on backend**
```bash
# Check if running
curl http://localhost:8000/health

# Kill existing process
lsof -i :8000
kill -9 <PID>

# Restart
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Issue: PostgreSQL connection error**
```bash
# Check PostgreSQL status (Docker)
docker-compose ps postgres

# Restart PostgreSQL
docker-compose down
docker-compose up -d postgres

# Check logs
docker-compose logs postgres
```

**Issue: API keys not working**
1. Verify keys are correct in `.env` file
2. Check API key permissions on provider websites
3. Restart backend server after updating keys
4. Ensure keys don't have leading/trailing spaces

### Frontend Issues

**Issue: Frontend can't reach backend**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Open browser console (F12) and check for errors
3. Verify ports match configuration
4. Restart frontend: `npm run dev`

**Issue: "Port already in use"**
```bash
# For backend port 8000
lsof -i :8000
kill -9 <PID>

# For PostgreSQL port 5433 (Docker)
docker-compose down
docker-compose up -d

# For frontend port 8003
# Vite will automatically use next available port
npm run dev
```

**Issue: Blank frontend or style not loading**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database Issues

**Issue: Database connection timeout**
```bash
# Check if PostgreSQL container is healthy
docker-compose logs postgres

# If not healthy, rebuild
docker-compose down -v
docker-compose up -d postgres
```

**Issue: "Database does not exist"**
```bash
# Create database manually
docker exec -it prophet-postgres psql -U prophet -c \
  "CREATE DATABASE prophet_db;"
```

### Docker Issues

**Issue: Docker containers not starting**
```bash
# Check for port conflicts
docker ps -a

# Clean up old containers
docker-compose down -v
docker-compose up -d
```

**Issue: Permission denied errors**
```bash
# May need sudo (Linux)
sudo docker-compose up -d

# Or add user to docker group
sudo usermod -aG docker $USER
```

---

## 📊 Sample Data & Testing

### Populate Sample Data
```bash
cd backend
python seed_eddie_watchlist.py
python populate_test_data.py
```

### Run Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Test Coverage
```bash
python -m pytest tests/ --cov=src
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

### Development Workflow

**Backend Development:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend Development:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📚 Additional Documentation

- **[HOW_TO_START.md](./HOW_TO_START.md)** - Detailed startup guide
- **[INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)** - Module integration details
- **[QUICK_START_STOCK_ANALYZER.md](./QUICK_START_STOCK_ANALYZER.md)** - Stock Analyzer guide
- **[LONG_TERM_STOCK_PICKER_SUMMARY.md](./LONG_TERM_STOCK_PICKER_SUMMARY.md)** - Long-term analysis
- **[SETUP_NOTES.md](./SETUP_NOTES.md)** - Additional setup information
- **[docs/](./docs/)** - Complete documentation folder

---

## 📦 Deployment

### Docker Deployment
```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Production Deployment
1. Update `.env` with production API keys
2. Set `DEBUG=False` in environment
3. Use a production-grade database (not Docker volume)
4. Configure reverse proxy (Nginx/Apache)
5. Enable HTTPS/SSL certificates
6. Set up monitoring and logging

---

## 🔒 Security Notes

- **Never commit** `.env` file with real API keys
- **Use** environment variables for sensitive data
- **Rotate** API keys regularly
- **Enable** HTTPS in production
- **Use** strong database passwords
- **Keep** dependencies updated

```bash
# Check for vulnerable dependencies
pip audit
npm audit
```

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](./LICENSE) file for details.

---

## 💬 Support & Community

### Getting Help
- Check [Troubleshooting](#troubleshooting) section
- Review [Additional Documentation](#additional-documentation)
- Open an GitHub Issue for bugs
- Start a Discussion for questions

### Reporting Issues
Please provide:
- Detailed error message
- Steps to reproduce
- System information (OS, Python version, Node version)
- Relevant logs or screenshots

### Feature Requests
Submit feature requests via GitHub Issues with:
- Clear description of the feature
- Use case and benefits
- Implementation suggestions (optional)

---

## 🙏 Acknowledgments

- **DeepSeek** for AI analysis capabilities
- **Finnhub** for market data
- **FastAPI** for the backend framework
- **React** for the frontend UI

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Backend Language | Python 3.9+ |
| Frontend Framework | React 18 |
| Database | PostgreSQL 16 |
| API Framework | FastAPI |
| Test Coverage | Configurable |
| License | MIT |
| Version | 1.0.0 |

---

## 🎯 Roadmap

- [ ] Advanced technical indicators
- [ ] Machine learning predictions
- [ ] Multi-broker integration
- [ ] Mobile application
- [ ] Real-time alerts
- [ ] Portfolio optimization
- [ ] Advanced charting
- [ ] Community features

---

## ✅ Version History

### v1.0.0 (Current)
- ✨ Stock analysis with AI predictions
- ✨ Eddie Intraday trading signals
- ✨ Long-term fundamental analysis
- ✨ Watchlist management
- ✨ P&L tracking (Zerodha integration)
- ✨ Dashboard and portfolio overview
- ✨ Real-time market data
- ✨ Docker deployment support

---

## 📅 Last Updated

**August 18, 2026**

---

**Made with ❤️ for retail investors and traders.**

For questions or support, please open an issue on GitHub or check the documentation.
