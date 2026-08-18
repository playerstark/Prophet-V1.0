# Prophet V1.0 - Complete Setup Manual

**Complete step-by-step guide to get Prophet V1.0 running on your machine**

---

## 📋 Prerequisites Checklist

Before starting, ensure you have these installed:

- [ ] **Git** - Version control
  - Windows: `choco install git` or download from https://git-scm.com
  - Mac: `brew install git`
  - Linux: `sudo apt-get install git`

- [ ] **Docker & Docker Compose** (Recommended)
  - Download: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version && docker-compose --version`

- [ ] **Node.js 18+** (For frontend)
  - Download: https://nodejs.org/
  - Verify: `node --version && npm --version`

- [ ] **Python 3.9+** (For backend - if running locally)
  - Download: https://www.python.org/downloads/
  - Verify: `python --version`

- [ ] **API Keys** (Free accounts)
  - DeepSeek: https://platform.deepseek.com/
  - Finnhub: https://finnhub.io/
  - Zerodha (optional): https://kite.zerodha.com/

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1

# Navigate to project directory
pwd  # Should show: /path/to/prophet-v1
```

### Step 2: Set Up Environment File

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# For Windows (PowerShell): notepad .env
# For Mac/Linux: nano .env

# Add your API keys:
# DEEPSEEK_API_KEY=sk-your-actual-key-here
# FINNHUB_API_KEY=your-actual-key-here
```

### Step 3: Start with Docker (Recommended)

```bash
# Start all services (PostgreSQL + Backend)
docker-compose up -d

# Wait 10 seconds for services to start
sleep 10

# Check if services are running
docker-compose ps
# You should see 2 services: postgres and backend

# Start frontend in new terminal
cd frontend
npm install
npm run dev

# Access application
# Frontend: http://localhost:8003
# Backend API: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Done! 🎉

Your Prophet V1.0 application is now running!

---

## 📖 Detailed Setup Instructions

### Option A: Docker Setup (EASIEST)

#### Prerequisites Check
```bash
docker --version      # Should show Docker version
docker-compose --version  # Should show Docker Compose version
```

#### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1
```

#### Step 2: Configure Environment
```bash
# Create .env file from template
cp .env.example .env

# Edit with your keys (use any text editor)
# Windows (PowerShell): 
#   notepad .env
# Mac:
#   nano .env
# Linux:
#   nano .env
```

#### Step 3: Start Backend Services
```bash
# From project root directory
docker-compose up -d

# Monitor startup (wait for "healthy")
docker-compose ps

# Check logs (watch for "Application startup complete")
docker-compose logs -f backend

# Once you see "Application startup complete", proceed to Step 4
```

Expected output:
```
NAME                    COMMAND                  SERVICE      STATUS
prophet-postgres        postgres                 postgres     Up (healthy)
prophet-backend         uvicorn src.main:app ... backend      Up
```

#### Step 4: Start Frontend
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# You should see: "VITE v5.x.x  ready in xxx ms"
# Local: http://localhost:8003
```

#### Step 5: Verify Everything Works
```bash
# Test backend
curl http://localhost:8001/health
# Expected: {"status": "healthy", "version": "1.0.0"}

# Open browser
# Frontend: http://localhost:8003
# API Docs: http://localhost:8001/docs
```

#### Stopping Services
```bash
# Stop Docker services
docker-compose down

# Stop frontend (press Ctrl+C in terminal)
```

#### Troubleshooting Docker Setup

**Issue: Port already in use**
```bash
# Kill process on port 8001 (macOS/Linux)
lsof -i :8001
kill -9 <PID>

# Or use Docker restart
docker-compose restart backend
```

**Issue: Database connection error**
```bash
# Restart PostgreSQL
docker-compose down
docker-compose up -d postgres
sleep 10
docker-compose up -d backend
```

**Issue: Out of memory**
```bash
# Increase Docker memory in settings, then:
docker-compose down -v
docker-compose up -d
```

---

### Option B: Local Development Setup

#### Prerequisites Check
```bash
python --version      # Should be 3.9+
node --version        # Should be 18+
npm --version         # Should be 9+
```

#### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1
```

#### Step 2: Backend Setup

**Terminal 1 - Backend:**
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
#   .\venv\Scripts\Activate.ps1
# Windows (CMD):
#   venv\Scripts\activate
# Mac/Linux:
#   source venv/bin/activate

# Verify activation (prompt should show "(venv)")

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor

# Start backend server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# You should see: "Application startup complete"
# Backend ready at: http://localhost:8000
```

#### Step 3: Database Setup

**Option A: PostgreSQL with Docker**
```bash
# Start just PostgreSQL (from project root)
docker-compose up -d postgres

# Verify it's healthy
docker-compose logs postgres | grep "ready to accept connections"
```

**Option B: Local PostgreSQL**
```bash
# macOS
brew install postgresql
brew services start postgresql

# Linux
sudo apt-get install postgresql
sudo systemctl start postgresql

# Windows
# Download and install from: https://www.postgresql.org/download/windows/

# Create database and user
psql -U postgres -c "CREATE DATABASE prophet_db;"
psql -U postgres -c "CREATE USER prophet WITH PASSWORD 'password';"
psql -U postgres -c "ALTER ROLE prophet WITH SUPERUSER;"

# Verify (should show "prophet_db")
psql -U postgres -l
```

#### Step 4: Frontend Setup

**Terminal 2 - Frontend:**
```bash
# Navigate to frontend directory
cd prophet-v1/frontend

# Install Node dependencies
npm install

# Start development server
npm run dev

# You should see: "VITE vX.X.X ready in XXX ms"
# Frontend ready at: http://localhost:8003
```

#### Step 5: Verify Installation
```bash
# Test Backend Health (Terminal 1 should show output)
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "1.0.0"}

# Open browser
# Frontend: http://localhost:8003
# API Documentation: http://localhost:8000/docs
```

#### Troubleshooting Local Setup

**Issue: "ModuleNotFoundError" in backend**
```bash
# Ensure venv is activated (prompt shows "(venv)")
# If not, activate it:
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: "Cannot connect to database"**
```bash
# Check PostgreSQL status
# Mac: brew services list | grep postgres
# Linux: sudo systemctl status postgresql
# Windows: Check Services for PostgreSQL

# Or if using Docker:
docker-compose ps postgres
```

**Issue: Frontend blank or styles not loading**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Issue: Port already in use**
```bash
# Mac/Linux - Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Windows - Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# For frontend port 8003, just restart: npm run dev
```

---

## 🔑 Getting API Keys

### 1. DeepSeek API Key

1. Go to https://platform.deepseek.com/
2. Sign up for free account
3. Navigate to API Settings
4. Create new API key
5. Copy the key (starts with "sk-")
6. Paste in `.env`: `DEEPSEEK_API_KEY=sk-your-key-here`

### 2. Finnhub API Key

1. Go to https://finnhub.io/
2. Sign up for free account
3. Dashboard → API Keys section
4. Copy your token (32 character string)
5. Paste in `.env`: `FINNHUB_API_KEY=your-key-here`

### 3. Zerodha API (Optional)

For P&L tracking integration:

1. Go to https://kite.zerodha.com/
2. Create account
3. Settings → API Tokens → Generate Token
4. Add to `.env`:
   ```
   ZERODHA_API_KEY=your-key
   ZERODHA_API_SECRET=your-secret
   ZERODHA_REQUEST_TOKEN=your-token
   ```

---

## 📝 Environment File Configuration

### Complete .env Example

```ini
# DATABASE CONFIGURATION
DATABASE_URL=postgresql://prophet:password@localhost:5433/prophet_db

# API KEYS (Get these from provider websites)
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
FINNHUB_API_KEY=your-finnhub-key-here

# OPTIONAL: Zerodha Integration
ZERODHA_API_KEY=your-zerodha-key-here
ZERODHA_API_SECRET=your-zerodha-secret-here
ZERODHA_REQUEST_TOKEN=your-zerodha-token-here

# SERVER CONFIGURATION
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Important Notes:
- ⚠️ **NEVER** commit `.env` with real keys to Git
- ✅ `.env` is automatically excluded via `.gitignore`
- ✅ Only `.env.example` is version controlled
- 🔒 Keep API keys private and rotate regularly

---

## 🧪 Loading Sample Data (Optional)

Populate the database with test stock data:

```bash
cd backend

# Activate virtual environment (if not active)
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Seed Eddie Intraday stocks
python seed_eddie_watchlist.py

# Populate test market data
python populate_test_data.py

# Verify (query database)
python -c "from src.database import SessionLocal; \
           from src.models import Stock; \
           db = SessionLocal(); \
           print(f'Total stocks: {db.query(Stock).count()}')"
```

---

## 🧪 Running Tests (Optional)

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Mac/Linux

# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=src

# Run specific test
python -m pytest tests/test_stock_analyzer.py -v
```

---

## 📊 Accessing the Application

### URLs After Startup

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8003 | Main web application |
| Backend API | http://localhost:8000 | REST API (local run) |
| Backend API | http://localhost:8001 | REST API (Docker) |
| API Docs | http://localhost:8001/docs | Interactive API documentation |
| ReDoc | http://localhost:8001/redoc | Alternative API docs |
| Database Health | `curl http://localhost:8001/health` | Check API status |

### First Time Using the Application

1. **Open Frontend**: http://localhost:8003
2. **Navigate to Stock Analyzer**
3. **Search for a stock** (e.g., "RELIANCE", "TCS", "INFY")
4. **View predictions** in Swing or Long-Term mode
5. **Add to Watchlist** to track your favorite stocks
6. **Explore Eddie Intraday** for intraday signals

---

## 🛑 Stopping the Application

### If Using Docker:
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean database)
docker-compose down -v
```

### If Running Locally:

**Terminal 1 (Backend):**
```bash
# Press Ctrl+C to stop uvicorn server
```

**Terminal 2 (Frontend):**
```bash
# Press Ctrl+C to stop npm dev server
```

**If PostgreSQL running locally:**
```bash
# macOS
brew services stop postgresql

# Linux
sudo systemctl stop postgresql

# Windows - Stop from Services or:
# net stop postgresql-x64-15
```

---

## 🔄 Restarting the Application

### Quick Restart (Docker)
```bash
# Stop and restart
docker-compose restart

# Or full restart
docker-compose down
docker-compose up -d
sleep 10
cd frontend && npm run dev
```

### Development Restart (Local)
```bash
# Kill backend (Ctrl+C in Terminal 1)
# Kill frontend (Ctrl+C in Terminal 2)

# Restart backend
cd backend && source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Restart frontend (new terminal)
cd frontend && npm run dev
```

---

## 📦 Project Structure Quick Reference

```
prophet-v1/
├── backend/              # Python/FastAPI backend
│   ├── src/             # Source code
│   ├── tests/           # Test suite
│   ├── requirements.txt # Python dependencies
│   └── .env            # ⚠️ Config (gitignored)
├── frontend/           # React/TypeScript frontend
│   ├── src/           # Source code
│   ├── package.json  # Node dependencies
│   └── vite.config.ts # Build config
├── docs/              # Documentation
├── .env.example       # Template (committed)
├── docker-compose.yml # Docker config
├── README.md          # Project readme
└── SETUP_MANUAL.md    # This file
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend running: `curl http://localhost:8001/health` returns success
- [ ] Frontend accessible: http://localhost:8003 loads
- [ ] API docs visible: http://localhost:8001/docs loads
- [ ] Can search stock: Try "RELIANCE" in Stock Analyzer
- [ ] Database connected: No connection errors in logs
- [ ] API keys working: Predictions load correctly
- [ ] No console errors: Open browser F12 → Console tab

---

## 🆘 Common Issues & Solutions

### Issue: "EADDRINUSE: address already in use :::8003"
**Solution:**
```bash
# Find process on port 8003
lsof -i :8003
kill -9 <PID>

# Then restart: npm run dev
```

### Issue: "Failed to connect to database"
**Solution:**
- Verify DATABASE_URL in .env is correct
- Check PostgreSQL is running
- For Docker: `docker-compose logs postgres`

### Issue: "Invalid API key" errors
**Solution:**
- Verify keys in .env are correct (no spaces)
- Check key permissions on provider website
- Restart backend after updating keys

### Issue: "CORS error" or "Cannot reach backend"
**Solution:**
- Ensure backend is running
- Check both services are on correct ports
- Verify .env has correct database URL

### Issue: Node/Python version conflicts
**Solution:**
```bash
# Check versions
node --version      # Should be 18+
npm --version       # Should be 9+
python --version    # Should be 3.9+

# Update if needed:
# Node: https://nodejs.org/
# Python: https://www.python.org/
```

---

## 🎓 Next Steps

After successful setup:

1. **Explore Features**
   - Try Stock Analyzer with different symbols
   - Check Eddie Intraday signals
   - Add stocks to Watchlist

2. **Configure Integrations** (Optional)
   - Link Zerodha account for P&L tracking
   - Set up portfolio monitoring

3. **Read Documentation**
   - See [README.md](./README.md) for feature overview
   - See [HOW_TO_START.md](./HOW_TO_START.md) for detailed usage
   - Check [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md) for architecture

4. **Customize**
   - Modify watchlist
   - Adjust analysis parameters
   - Add custom indicators

---

## 📞 Getting Help

### If you encounter issues:

1. **Check Logs**
   ```bash
   # Backend logs (Docker)
   docker-compose logs -f backend
   
   # Frontend console
   # Press F12 in browser → Console tab
   ```

2. **Verify Prerequisites**
   - All required software installed
   - API keys are valid
   - Ports are available
   - Sufficient disk space

3. **Reset Everything**
   ```bash
   # Clean Docker
   docker-compose down -v
   docker-compose up -d
   
   # Clean Node
   rm -rf frontend/node_modules package-lock.json
   npm install
   npm run dev
   ```

4. **Check Documentation**
   - README.md - Project overview
   - HOW_TO_START.md - Detailed guide
   - INTEGRATION_SUMMARY.md - Architecture
   - docs/ folder - Additional docs

---

## 🎉 Success!

You've successfully set up Prophet V1.0!

**What's Next?**
1. Explore the application at http://localhost:8003
2. Try analyzing a stock with the Stock Analyzer
3. Set up your watchlist
4. Check real-time intraday signals with Eddie Intraday
5. Connect Zerodha for portfolio tracking

**Happy Trading! 📈**

---

**Version**: 1.0.0  
**Last Updated**: August 18, 2026  
**Status**: Production Ready

