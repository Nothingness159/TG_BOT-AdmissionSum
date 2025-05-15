import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN") 
    DATA_FILE = "data/directions.xlsx"
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes") 
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 

if not Config.BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена.")
