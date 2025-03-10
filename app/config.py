import os

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "1mpca$(2)")
    PORT = int(os.getenv("PORT", 4000))
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb://localhost:27017/")

settings = Settings()
