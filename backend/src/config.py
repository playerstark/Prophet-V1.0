import os
from pydantic import BaseModel

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://prophet:password@localhost:5433/prophet_db")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "da0kh8pr01qh1noo1hcgda0kh8pr01qh1noo1hd0")
    zerodha_api_key: str = os.getenv("ZERODHA_API_KEY", "")
    zerodha_api_secret: str = os.getenv("ZERODHA_API_SECRET", "")
    zerodha_request_token: str = os.getenv("ZERODHA_REQUEST_TOKEN", "")
    rapidapi_key: str = os.getenv("RAPIDAPI_KEY", "46b52785c5mshbd0587aaddce47bp173894jsn2f9f7cf3c025")
    rapidapi_host: str = os.getenv("RAPIDAPI_HOST", "live-stock-market.p.rapidapi.com")
    twelvedata_api_key: str = os.getenv("TWELVE_DATA_API_KEY", "928aeaa835444deaa17117be193ebe36")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()
