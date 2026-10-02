import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project Root is the parent of the app directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Default SQLite database path
DEFAULT_DB_FILE = DATA_DIR / "catalog.db"

# Fetch DATABASE_URL from environment or fallback
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"

# Normalize SQLite URL if it was provided as a raw filesystem path
if not DATABASE_URL.startswith("sqlite:///"):
    if DATABASE_URL.startswith("sqlite:"):
        DATABASE_URL = DATABASE_URL
    else:
        # User passed a raw path like /app/data/catalog.db or ./data/catalog.db
        DATABASE_URL = f"sqlite:///{DATABASE_URL.lstrip('/')}"

# Server network settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
