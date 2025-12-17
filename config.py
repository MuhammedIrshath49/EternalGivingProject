"""Configuration management"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN not set in .env")

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "rom_peerbot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Construct PostgreSQL URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Prayer Configuration
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Singapore")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "Singapore")
PRAYER_API_URL = "https://api.aladhan.com/v1/timingsByCity"
PRAYER_METHOD = 3  # Muslim World League

# Amal Jariah Configuration
AMAL_JARIAH_MONTH = os.getenv("AMAL_JARIAH_MONTH", "DEC 2025")
# Multiple countries can be comma-separated (e.g., "GAZA/PALESTINE, LEBANON")
AMAL_JARIAH_COUNTRY = os.getenv("AMAL_JARIAH_COUNTRY", "PHILIPPINES")
AMAL_JARIAH_PRICE = os.getenv("AMAL_JARIAH_PRICE", "$50/slot")
AMAL_JARIAH_CONTACT = os.getenv("AMAL_JARIAH_CONTACT", "82681357")
AMAL_JARIAH_WEBSITE = os.getenv("AMAL_JARIAH_WEBSITE", "https://roseofmadinah.com/")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Admin Configuration (optional - for broadcast features)
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
