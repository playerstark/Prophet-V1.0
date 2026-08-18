# How to Clone & Deploy Prophet V1.0

**Quick reference for cloning the repository and getting started**

---

## 🚀 5-Minute Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1
```

### 2. Set Up Environment
```bash
cp .env.example .env

# Edit .env with your API keys
# Get free keys from:
# - DeepSeek: https://platform.deepseek.com/
# - Finnhub: https://finnhub.io/
nano .env  # or use your editor
```

### 3. Start Application

**Option A: Docker (Easiest)**
```bash
docker-compose up -d
cd frontend && npm install && npm run dev
```

**Option B: Local**
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:8003
- **API Docs**: http://localhost:8001/docs (Docker) or http://localhost:8000/docs (Local)

---

## 📥 Clone via HTTPS (No SSH Key Needed)

```bash
# Clone with HTTPS (works everywhere)
git clone https://github.com/yourusername/prophet-v1.git

# Navigate into project
cd prophet-v1

# Verify it's a git repository
git status
git log --oneline
```

---

## 🔑 Clone via SSH (If SSH Key Configured)

```bash
# Clone with SSH (faster if you have SSH key)
git clone git@github.com:yourusername/prophet-v1.git

# Navigate into project
cd prophet-v1
```

---

## 📋 What's Included in This Repository

### 📚 Documentation
- **README.md** - Comprehensive project overview and features
- **SETUP_MANUAL.md** - Complete step-by-step setup guide
- **HOW_TO_START.md** - Detailed startup instructions
- **QUICK_START_STOCK_ANALYZER.md** - Stock Analyzer guide
- **INTEGRATION_SUMMARY.md** - Module integration details
- **LONG_TERM_STOCK_PICKER_SUMMARY.md** - Long-term analysis guide
- **/docs** - Additional documentation and guides

### 💻 Source Code
- **/backend** - Python FastAPI backend
  - API endpoints
  - Stock analysis services
  - AI integration
  - Data fetching
- **/frontend** - React TypeScript frontend
  - Web interface
  - Stock analysis UI
  - Watchlist management
  - Portfolio tracking

### 🐳 Deployment
- **docker-compose.yml** - Complete stack orchestration
- **Dockerfile** - Backend container configuration
- **.dockerignore** - Docker build optimization

### ⚙️ Configuration
- **.env.example** - Environment template (copy to .env)
- **requirements.txt** - Python dependencies
- **package.json** - Node.js dependencies
- **.gitignore** - Git ignore rules

### 🧪 Testing
- **/tests** - Test suite (backend)
- **pytest.ini** - Test configuration

---

## 📖 Detailed Setup Path

### Step 1: Prerequisites (5 min)

Ensure these are installed:
```bash
# Check Git
git --version

# Check Docker (optional but recommended)
docker --version
docker-compose --version

# Check Node.js
node --version  # Should be 18+
npm --version   # Should be 9+

# Check Python (for local backend)
python --version  # Should be 3.9+
```

**If missing any, install from:**
- Git: https://git-scm.com/
- Docker: https://www.docker.com/products/docker-desktop
- Node.js: https://nodejs.org/
- Python: https://www.python.org/

### Step 2: Clone Repository (2 min)

```bash
# Choose one method:

# Method 1: HTTPS (works everywhere)
git clone https://github.com/yourusername/prophet-v1.git

# Method 2: SSH (if you have SSH key)
git clone git@github.com:yourusername/prophet-v1.git

# Navigate to project
cd prophet-v1

# Verify clone
git log --oneline  # Should show commits
git remote -v      # Should show origin URL
```

### Step 3: Configure Environment (3 min)

```bash
# Copy environment template
cp .env.example .env

# Edit with your editor
nano .env  # macOS/Linux
# or
code .env  # VS Code
# or
notepad .env  # Windows

# Add your API keys from:
# DEEPSEEK_API_KEY from https://platform.deepseek.com/
# FINNHUB_API_KEY from https://finnhub.io/
```

### Step 4: Start Application (5 min)

**Choose One:**

#### Docker Setup (Recommended)
```bash
# Start all services
docker-compose up -d

# Wait for services (30 seconds)
docker-compose ps

# Start frontend
cd frontend
npm install
npm run dev

# Open: http://localhost:8003
```

#### Local Setup
See [SETUP_MANUAL.md](./SETUP_MANUAL.md) → Option B: Local Development Setup

---

## 🔗 First-Time Setup Commands

Copy-paste these commands in order:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys (nano .env)

# 3. Start with Docker
docker-compose up -d

# 4. Wait for services to be ready
sleep 15

# 5. Start frontend
cd frontend
npm install
npm run dev

# 6. Open in browser
# Frontend: http://localhost:8003
# API Docs: http://localhost:8001/docs
```

---

## 📊 Directory Structure After Clone

```
prophet-v1/                          # Project root
├── README.md                         # Main documentation
├── SETUP_MANUAL.md                  # Setup guide
├── CLONE_INSTRUCTIONS.md            # This file
├── .env.example                     # Environment template
├── .env                             # Your config (gitignored)
├── docker-compose.yml               # Docker services
├── Dockerfile                       # Backend container
│
├── backend/                         # Python backend
│   ├── src/
│   │   ├── main.py                 # Entry point
│   │   ├── routes/                 # API endpoints
│   │   ├── services/               # Business logic
│   │   └── models.py               # Database models
│   ├── requirements.txt            # Dependencies
│   └── tests/                      # Test suite
│
├── frontend/                        # React frontend
│   ├── src/
│   │   ├── pages/                  # Page components
│   │   ├── components/             # UI components
│   │   └── App.tsx                 # Main app
│   ├── package.json                # Dependencies
│   └── public/                     # Static files
│
└── docs/                           # Documentation
    ├── IMPLEMENTATION_SUMMARY.md
    ├── EDDIE_IMPLEMENTATION_COMPLETE.md
    └── more guides...
```

---

## ✅ Verification After Clone

Run these checks to verify everything is set up correctly:

```bash
# 1. Check git repository
git status
git log --oneline | head -5

# 2. Check configuration
ls -la .env.example  # Should exist
ls -la .env          # Should exist
cat .env | grep -v "^#"  # Show your config (check for your keys)

# 3. Check Docker (if using Docker)
docker-compose ps
docker-compose logs backend | head -20

# 4. Test backend health
curl http://localhost:8001/health
# Expected: {"status": "healthy", "version": "1.0.0"}

# 5. Test frontend
# Open browser to http://localhost:8003
# Should see Prophet V1.0 application
```

---

## 🚦 Starting & Stopping

### Start Application

**Docker:**
```bash
docker-compose up -d          # Start backend + database
cd frontend && npm run dev    # Start frontend
```

**Local:**
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Stop Application

**Docker:**
```bash
docker-compose down  # Stop all services
```

**Local:**
```bash
# Press Ctrl+C in both terminals
```

---

## 🔄 Updating from Remote

After cloning, to get latest changes:

```bash
# Fetch latest changes
git fetch origin

# Update your local branch
git pull origin main

# If you made changes, stash first:
git stash
git pull origin main
git stash pop
```

---

## 🛠 Common Git Operations

```bash
# Check status
git status

# View commit history
git log --oneline

# View specific files changed
git log -p

# Check what branch you're on
git branch

# Create new branch
git checkout -b feature/your-feature

# Commit changes
git add .
git commit -m "Your message"

# Push to remote
git push origin main
```

---

## 🆘 Clone Troubleshooting

### Issue: "Permission denied (publickey)"
**Solution:** Use HTTPS instead of SSH
```bash
git clone https://github.com/yourusername/prophet-v1.git
```

### Issue: "Repository not found"
**Solution:** Check:
1. Repository URL is correct
2. Repository is public or you have access
3. Typo in username or repo name

```bash
# Try with HTTPS
git clone https://github.com/yourusername/prophet-v1.git
```

### Issue: "Shallow clone" or duplicate folder
**Solution:**
```bash
# Remove bad clone
rm -rf prophet-v1

# Clone again
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1
```

### Issue: ".env.example not found after clone"
**Solution:** Make sure you're in the project root
```bash
cd prophet-v1
ls -la  # Should show .env.example

# If not found, clone might be corrupted
cd ..
rm -rf prophet-v1
git clone https://github.com/yourusername/prophet-v1.git
cd prophet-v1
```

---

## 📚 Reading Order

After cloning, read documentation in this order:

1. **[README.md](./README.md)** - Overview of Prophet V1.0
2. **[CLONE_INSTRUCTIONS.md](./CLONE_INSTRUCTIONS.md)** - How to clone (this file)
3. **[SETUP_MANUAL.md](./SETUP_MANUAL.md)** - Detailed setup instructions
4. **[HOW_TO_START.md](./HOW_TO_START.md)** - Running the application
5. **[INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)** - How modules work together
6. **[docs/](./docs/)** - Additional guides and references

---

## 🎯 Next Steps

1. **Clone the repository** using the commands above
2. **Configure .env** with your API keys
3. **Start the application** (Docker recommended)
4. **Access http://localhost:8003** in your browser
5. **Explore the application** and try analyzing a stock
6. **Read [HOW_TO_START.md](./HOW_TO_START.md)** for detailed usage

---

## 📞 Getting Help

If you encounter issues:

1. Check [SETUP_MANUAL.md](./SETUP_MANUAL.md) → Troubleshooting section
2. Check logs:
   ```bash
   # Docker logs
   docker-compose logs -f backend
   docker-compose logs -f postgres
   
   # Browser console
   # Press F12 → Console tab
   ```
3. Verify prerequisites are installed
4. Check .env configuration is correct
5. Try resetting: `docker-compose down -v && docker-compose up -d`

---

## 📝 Notes

- ⚠️ **Never commit .env** with real API keys
- ✅ **.env is gitignored** automatically
- 🔒 **Keep API keys private** - rotate regularly
- 📦 **All dependencies locked** in requirements.txt and package-lock.json

---

**Version**: 1.0.0  
**Last Updated**: August 18, 2026  
**Status**: Ready for Production

Happy coding! 🚀
