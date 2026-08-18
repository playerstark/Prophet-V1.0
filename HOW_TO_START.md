# PROPHET V1.0 - Application Startup Guide

## Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose installed
- Node.js 18+ installed
- npm installed
- Python 3.9+ (optional, if running backend locally)

### Option 1: Run with Docker (Recommended)

```bash
# 1. Navigate to project root
cd /home/cyberwarrior/Desktop/AI\ Job\ Prep/Prophet_V1_0_Eddie_Rebuilt

# 2. Start backend with Docker Compose
docker-compose up -d

# 3. Start frontend in another terminal
cd frontend
npm install  # Only needed first time
npm run dev

# 4. Access the application
# Frontend: http://localhost:8003
# Backend: http://localhost:8001
```

### Option 2: Run Backend Locally (Python)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your API keys:
# DEEPSEEK_API_KEY=your_key
# FINNHUB_API_KEY=your_key

# 5. Start backend server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 6. In another terminal, start frontend
cd ../frontend
npm install  # Only needed first time
npm run dev

# 7. Access the application
# Frontend: http://localhost:8003
# Backend: http://localhost:8000
```

---

## Detailed Setup Instructions

### Backend Setup

#### Prerequisites
- PostgreSQL (via Docker or local installation)
- Python 3.9+
- pip or conda

#### Step 1: Environment Configuration

```bash
cd backend

# Create .env file (or copy from .env.example)
cat > .env << EOF
DATABASE_URL=postgresql://prophet:password@localhost:5433/prophet_db
DEEPSEEK_API_KEY=your_deepseek_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here
DEBUG=True
EOF
```

**Required API Keys:**
- **DEEPSEEK_API_KEY**: For AI-powered analysis
  - Get from: https://platform.deepseek.com/
- **FINNHUB_API_KEY**: For stock data
  - Get from: https://finnhub.io/

#### Step 2: Start PostgreSQL Database

**Option A: Docker (Recommended)**
```bash
# From project root, start PostgreSQL
docker-compose up -d postgres

# Wait for PostgreSQL to be ready (check logs)
docker-compose logs postgres
```

**Option B: Local PostgreSQL**
```bash
# Make sure PostgreSQL is running
# Create database and user
psql -U postgres -c "CREATE DATABASE prophet_db;"
psql -U postgres -c "CREATE USER prophet WITH PASSWORD 'password';"
psql -U postgres -c "ALTER ROLE prophet WITH SUPERUSER;"

# Update DATABASE_URL in .env to point to your local instance
```

#### Step 3: Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

#### Step 4: Start Backend Server

```bash
cd backend

# Activate virtual environment if not already active
source venv/bin/activate

# Run the server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend should start at:** `http://localhost:8000`

**Check backend health:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

---

### Frontend Setup

#### Prerequisites
- Node.js 18+ or higher
- npm 9+ or higher

#### Step 1: Install Dependencies

```bash
cd frontend

npm install
```

#### Step 2: Start Development Server

```bash
npm run dev
```

**Frontend will start at:** `http://localhost:8003` (or next available port if 8003 is in use)

#### Step 3: Build for Production (Optional)

```bash
npm run build
npm run preview
```

---

## Full Stack Startup (All at Once)

### Using Docker Compose (Easiest)

```bash
# Navigate to project root
cd /home/cyberwarrior/Desktop/AI\ Job\ Prep/Prophet_V1_0_Eddie_Rebuilt

# Start all services (PostgreSQL + Backend)
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Stop all services
docker-compose down
```

### Using Terminal Scripts

**Terminal 1 - Start Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Terminal 3 - Monitor Database (Optional):**
```bash
# Connect to PostgreSQL if running locally
psql -U prophet -d prophet_db -h localhost
```

---

## Access the Application

Once both backend and frontend are running:

### Main Application
- **URL:** http://localhost:8003
- **Pages:**
  - **Home**: Dashboard with portfolio overview
  - **Eddie Intraday**: Intraday trading analysis
  - **Stock Analyzer**: Technical analysis with AI predictions
    - Short-Term analysis
    - Swing trade predictions (with hold time & gain forecast)
    - Long-Term fundamental analysis
  - **P&L Tracking**: Zerodha broker integration

### API Documentation
- **Backend Health:** http://localhost:8000/health
- **API Base:** http://localhost:8000/api

---

## Environment Variables Reference

### Backend (.env file)

```ini
# Database Configuration
DATABASE_URL=postgresql://prophet:password@localhost:5433/prophet_db

# API Keys (Required for full functionality)
DEEPSEEK_API_KEY=sk-your-key-here
FINNHUB_API_KEY=your-finnhub-key-here

# Server Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Frontend (Automatic)
Frontend automatically connects to backend at `http://localhost:8000`

---

## Port Configuration

| Service | Default Port | Used For |
|---------|--------------|----------|
| Frontend | 8003 | Web application |
| Backend | 8000 | API server |
| Backend (Docker) | 8001 | API server (when using docker-compose) |
| PostgreSQL | 5433 | Database |
| PostgreSQL (Local) | 5432 | Database (if local) |

**If ports are in use:**
- Backend: Edit `docker-compose.yml` or change port in startup command
- Frontend: Vite will automatically use next available port

---

## Common Issues & Troubleshooting

### Issue: "Connection refused" on backend

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, restart:
# Terminal 1 - Kill existing process
lsof -i :8000
kill -9 <PID>

# Restart backend
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue: PostgreSQL connection error

**Solution:**
```bash
# Check if PostgreSQL is running (Docker)
docker-compose ps postgres

# If not running
docker-compose up -d postgres

# Check logs
docker-compose logs postgres
```

### Issue: Frontend can't reach backend

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check frontend console for errors (F12 → Console)
3. Restart frontend: `npm run dev`

### Issue: "Port already in use"

**Solution:**
```bash
# For port 8000 (Backend)
lsof -i :8000
kill -9 <PID>

# For port 5433 (PostgreSQL Docker)
docker-compose down
docker-compose up -d

# For port 8003 (Frontend)
# Just run npm run dev, it will use next available port
```

### Issue: API Keys not working

**Solution:**
1. Get API keys from:
   - DeepSeek: https://platform.deepseek.com/
   - Finnhub: https://finnhub.io/
2. Update .env file with correct keys
3. Restart backend server

---

## Stopping the Application

### Docker Compose
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Manual Processes
```bash
# Kill backend (find port 8000)
lsof -i :8000
kill -9 <PID>

# Kill frontend
# Press Ctrl+C in the terminal running npm run dev
```

---

## Data & Configuration Files

### Important Files
```
project-root/
├── backend/
│   ├── .env                          # Backend configuration (REQUIRED)
│   ├── requirements.txt               # Python dependencies
│   ├── prophet.db                    # SQLite database (if used)
│   └── src/
│       ├── main.py                   # FastAPI entry point
│       └── routes/                   # API endpoints
│
├── frontend/
│   ├── src/
│   │   ├── pages/                    # Page components
│   │   ├── components/               # Reusable components
│   │   └── App.tsx                   # Main app component
│   └── package.json                  # Node dependencies
│
└── docker-compose.yml                # Docker service configuration
```

### Database Location
- **Docker:** Inside PostgreSQL container (persistent via volume)
- **Local:** Connect via `psql` command or PostgreSQL client

---

## Next Steps

1. **Configure API Keys**
   - Add your DeepSeek API key
   - Add your Finnhub API key

2. **Populate Test Data** (Optional)
   ```bash
   cd backend
   python seed_eddie_watchlist.py
   python populate_test_data.py
   ```

3. **Start Using**
   - Go to http://localhost:8003
   - Try Stock Analyzer → Swing mode
   - Add stocks to watchlist
   - Check P&L Tracking with Zerodha integration

---

## Support & Documentation

- **Stock Analyzer**: See `QUICK_START_STOCK_ANALYZER.md`
- **Implementation Details**: See `IMPLEMENTATION_CHECKLIST.md`
- **Integration Guide**: See `INTEGRATION_SUMMARY.md`
- **Long-term Strategy**: See `LONG_TERM_STOCK_PICKER_SUMMARY.md`

---

## Version Information

- **Prophet V1.0**
- **Backend:** FastAPI + PostgreSQL
- **Frontend:** React 18 + Vite + TypeScript
- **AI Engine:** DeepSeek
- **Market Data:** Finnhub API

---

**Last Updated:** August 18, 2026

For issues or questions, check the logs:
```bash
# Backend logs (Docker)
docker-compose logs -f backend

# Frontend logs (Browser console)
# Press F12 → Console tab
```
