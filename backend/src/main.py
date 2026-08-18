from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.routes import stocks, watchlist, portfolio, home, long_term, eddie, eddie_intraday
# from src.jobs.polling_engine import PollingEngine
from src.database import engine, Base
from src import models

app = FastAPI(
    title="Prophet V1.0",
    description="Multi-market stock intelligence & AI trading platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home.router)
app.include_router(stocks.router)
app.include_router(watchlist.router)
app.include_router(portfolio.router)
app.include_router(long_term.router)
app.include_router(eddie.router)
app.include_router(eddie_intraday.router)

# polling_engine = PollingEngine()

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    # polling_engine.start()

@app.on_event("shutdown")
async def shutdown_event():
    pass
    # polling_engine.scheduler.shutdown()

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
