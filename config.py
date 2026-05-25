import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DB_PATH = os.getenv("DB_PATH", "salon.db")

# ── Інформація про салон ──
SALON_NAME = "✨ Beauty Studio"
SALON_ADDRESS = "м. Київ, вул. Хрещатик, 1"
SALON_PHONE = "+380 (44) 123-45-67"
SALON_INSTAGRAM = "@beauty_studio_demo"
SALON_MAPS_LINK = "https://maps.google.com/?q=50.4501,30.5234"
SALON_LATITUDE = 50.4501
SALON_LONGITUDE = 30.5234

# ── Робочі години ──
WORK_START_HOUR = 9
WORK_END_HOUR = 19
SLOT_DURATION_MINUTES = 60

# ── Нагадування ──
REMINDER_HOURS_BEFORE = 2
