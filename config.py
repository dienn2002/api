# config.py
from dotenv import load_dotenv
import os

# load .env từ thư mục hiện tại
load_dotenv()

class Settings:
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    # Chuyển sang int, với giá trị mặc định 8000 nếu không có trong .env
    try:
        APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    except ValueError:
        APP_PORT: int = 8000
    APP_RELOAD: bool = os.getenv("APP_RELOAD", "False").lower() in ("true", "1", "yes")

settings = Settings()
