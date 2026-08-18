# 📈 Prophet V1.0 - Complete Setup Guide

**An AI-Powered Stock Analysis Platform for Modern Investors**

---

## Table of Contents
- [Quick Overview](#quick-overview)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Quick Overview

**Prophet V1.0** is a full-stack stock analysis platform that combines:
- Real-time technical analysis for swing trading
- Fundamental analysis for long-term investing
- AI-powered insights and recommendations
- Interactive dashboard with real-time data
- Portfolio tracking and watchlist management

### Technology Stack
- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: React 18 with TypeScript
- **Database**: PostgreSQL 14+
- **Real-time Data**: yfinance, Finnhub, Twelve Data APIs
- **Deployment**: Docker-ready, cloud-compatible

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 20.04+
- **RAM**: 4GB (8GB recommended)
- **Disk**: 2GB free space
- **Network**: Internet connection required

### Required Software

#### Python 3.9+
```bash
# macOS
brew install python@3.9

# Ubuntu/Debian
sudo apt-get install python3.9 python3.9-venv python3-pip

# Windows
# Download from https://www.python.org/downloads/
```

#### Node.js 18+ & npm
```bash
# macOS
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# Download from https://nodejs.org/
```

#### PostgreSQL 14+
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows
# Download from https://www.postgresql.org/download/windows/
```

#### Git
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt-get install git

# Windows
# Download from https://git-scm.com/download/win
```

---

## Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Prophet-V1.0.git
cd Prophet-V1.0
```

### Step 2: Backend Setup

#### 2.1 Create Python Virtual Environment

**macOS / Linux:**
```bash
cd backend
python3.9 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
```

#### 2.2 Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt
```

#### 2.3 Setup Database

**Option A: Manual PostgreSQL Setup**

```bash
# Start PostgreSQL service
# macOS:
brew services start postgresql

# Ubuntu:
sudo systemctl start postgresql

# Windows:
# PostgreSQL starts automatically when installed
```

Create database and user:

**macOS / Linux:**
```bash
# Open psql
psql -U postgres

# In psql:
CREATE DATABASE prophet_db;
CREATE USER prophet_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE prophet_db TO prophet_user;
\q  # Quit psql
```

**Windows:**
```bash
# Open Command Prompt and run:
psql -U postgres

# Then same commands as above
```

**Option B: Docker Setup (Recommended for Beginners)**

```bash
# If Docker is installed:
docker run -d \
  --name prophet-postgres \
  -e POSTGRES_DB=prophet_db \
  -e POSTGRES_USER=prophet_user \
  -e POSTGRES_PASSWORD=secure_password_here \
  -p 5432:5432 \
  -v prophet_data:/var/lib/postgresql/data \
  postgres:16
```

#### 2.4 Configure Environment Variables

```bash
# Copy example config
cp .env.example .env

# Edit the .env file with your settings
# On macOS/Linux:
nano .env

# On Windows (use any text editor):
# - Notepad, VS Code, or any text editor
```

**Update these values in `.env`:**
```
# Database Connection
DATABASE_URL=postgresql://prophet_user:secure_password_here@localhost:5432/prophet_db

# API Keys (get from respective services)
DEEPSEEK_API_KEY=your_api_key_here
FINNHUB_API_KEY=your_api_key_here

# Security (change these!)
SECRET_KEY=your-super-secret-key-change-this

# Development Settings
DEBUG=True
ENVIRONMENT=development
```

#### 2.5 Initialize Database

```bash
# Create tables
python -c "from src.config import Base, engine; Base.metadata.create_all(bind=engine)"

# (Optional) Seed sample data
python populate_test_data.py
```

#### 2.6 Verify Backend Setup

```bash
# Run a quick test
pytest

# Start the backend server
uvicorn src.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 3: Frontend Setup

#### 3.1 Install Node Dependencies

```bash
cd ../frontend  # Go back to main directory first

npm install
# or
yarn install
```

#### 3.2 Configure Frontend Environment

```bash
# Copy example config
cp .env.example .env.local

# Edit if needed (defaults usually work)
# nano .env.local
```

**Environment variables (.env.local):**
```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_MAX_REQUESTS_PER_MINUTE=60
```

#### 3.3 Start Frontend Development Server

```bash
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

---

## Configuration

### API Keys Setup

The application uses several optional API services:

#### 1. **Finnhub** (Recommended - Free Tier Available)
- Sign up at: https://finnhub.io/
- Free tier: 60 API calls/minute
- Add to `.env`: `FINNHUB_API_KEY=your_key_here`

#### 2. **Twelve Data** (Premium Provider)
- Sign up at: https://twelvedata.com/
- Best data quality and reliability
- Add to `.env`: `TWELVE_DATA_API_KEY=your_key_here`

#### 3. **DeepSeek API** (For AI Features)
- Sign up at: https://api.deepseek.com/
- Powers AI-generated insights
- Add to `.env`: `DEEPSEEK_API_KEY=your_key_here`

**Note**: The app will work without these keys using yfinance (free, but slower)

### Database Configuration

#### PostgreSQL Connection String
Format: `postgresql://username:password@host:port/database`

Example:
- Local: `postgresql://prophet_user:password@localhost:5432/prophet_db`
- Remote: `postgresql://user:pass@db.example.com:5432/prophet`

#### Test Database Queries
```bash
psql -U prophet_user -d prophet_db

# List tables
\dt

# View schema
\d stock_analysis

# Exit
\q
```

---

## Running the Application

### Development Mode (Recommended for Testing)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate.bat  # Windows

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the App:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production Mode

**Build Frontend:**
```bash
cd frontend
npm run build
```

**Start Backend (Production):**
```bash
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Compose (All-in-One)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

---

## Troubleshooting

### Backend Issues

#### "ModuleNotFoundError: No module named 'src'"
```bash
# Make sure you're in the backend directory with venv activated
cd backend
source venv/bin/activate
# Then run the command with python -m
python -m pytest
```

#### "Error: Database connection failed"
```bash
# Check PostgreSQL is running
psql -U postgres

# Verify DATABASE_URL in .env is correct
# Format: postgresql://user:password@host:port/database

# Test connection
psql -U prophet_user -d prophet_db -c "SELECT 1"
```

#### "Port 8000 already in use"
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill it
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn src.main:app --port 8001 --reload
```

#### "Dependencies not installed"
```bash
# Reinstall everything
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

### Frontend Issues

#### "npm install fails"
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json

# Reinstall
npm install

# If still fails, try yarn
npm install -g yarn
yarn install
```

#### "Port 5173 already in use"
```bash
# Use different port
npm run dev -- --port 3000
```

#### "Cannot find module errors after npm install"
```bash
# Rebuild
rm -rf node_modules dist
npm install
npm run build
```

#### "Vite build fails"
```bash
# Clear cache and rebuild
rm -rf dist
npm run build

# Check for errors in src/
npm run build -- --debug
```

### Database Issues

#### "PostgreSQL service not running"
```bash
# macOS
brew services start postgresql
brew services status postgresql

# Ubuntu
sudo systemctl start postgresql
sudo systemctl status postgresql

# Windows
# Go to Services (services.msc) and start PostgreSQL
```

#### "Cannot create database (permission denied)"
```bash
# Use postgres superuser to create
psql -U postgres

# Then in psql:
CREATE DATABASE prophet_db;
CREATE USER prophet_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE prophet_db TO prophet_user;
```

#### "Tables don't exist in database"
```bash
# Recreate tables
python -c "from src.config import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"

# Or use migrations if available
alembic upgrade head
```

### General Issues

#### "API requests timing out"
- Check internet connection
- Verify API keys are correct
- Check if API service is down
- Increase timeout in `.env`: `VITE_API_TIMEOUT=60000`

#### "CORS errors in browser console"
- Backend CORS is likely misconfigured
- Check `src/main.py` for CORS settings
- Should include: `http://localhost:5173` in allowed origins

---

## Next Steps

### 1. **Get API Keys** (Optional but Recommended)
- Sign up for Finnhub (free): https://finnhub.io/
- Add your key to `backend/.env`

### 2. **Explore the Features**
- Add stocks to watchlist
- Analyze a stock symbol
- Check the dashboard

### 3. **Customize**
- Edit watchlist stocks
- Configure preferred analysis providers
- Customize dashboard layout

### 4. **Deploy** (When Ready)
- See `docs/DEPLOYMENT.md` for production deployment
- Or use Docker for quick deployment

### 5. **Learn More**
- Check `docs/API.md` for API reference
- Read `docs/ARCHITECTURE.md` for system design
- Review example API calls in `docs/examples/`

---

## Project Structure Overview

```
Prophet-V1.0/
├── backend/
│   ├── src/
│   │   ├── main.py              # App entry point
│   │   ├── config.py            # Configuration
│   │   ├── models/              # Database models
│   │   ├── api/                 # API endpoints
│   │   ├── services/            # Business logic
│   │   └── utils/               # Helper functions
│   ├── tests/                   # Test files
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Example config
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── types/               # TypeScript types
│   │   └── styles/              # Tailwind CSS
│   ├── public/                  # Static assets
│   ├── package.json             # NPM dependencies
│   └── vite.config.ts           # Vite config
│
├── docs/                        # Documentation
├── docker-compose.yml           # Docker setup
└── README.md                    # Main README
```

---

## Performance Tips

### Backend Optimization
- Use connection pooling for database
- Cache API responses
- Enable gzip compression
- Use indexes on frequently queried columns

### Frontend Optimization
- Enable code splitting
- Lazy load components
- Minimize bundle size
- Use React.memo for expensive components

### Database Optimization
- Add indexes to stock symbols and dates
- Archive old data periodically
- Use EXPLAIN ANALYZE for slow queries

---

## Security Checklist

- [ ] Never commit `.env` files with real credentials
- [ ] Use strong database passwords
- [ ] Keep API keys private
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Validate all user inputs
- [ ] Keep dependencies updated
- [ ] Use environment-specific configs

---

## Quick Command Reference

```bash
# Backend
cd backend
source venv/bin/activate                    # Activate venv
pip install -r requirements.txt             # Install deps
uvicorn src.main:app --reload              # Run server
pytest                                      # Run tests

# Frontend
cd frontend
npm install                                 # Install deps
npm run dev                                 # Dev server
npm run build                               # Production build
npm run preview                             # Preview build

# Database
psql -U prophet_user -d prophet_db         # Connect to DB
docker-compose up -d                        # Start Docker stack
```

---

## Need Help?

1. **Check existing documentation** in `docs/` folder
2. **Search GitHub Issues** for similar problems
3. **Review API docs** at http://localhost:8000/docs
4. **Check logs** for error messages
5. **Try clean installation** if all else fails

---

**✅ You're all set! Start with the [Quick Start](#running-the-application) section above.**

Last Updated: August 2026
