import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("1543845399:AAGMq9rrQW7xSvgAPnXUjpjBNVfw6G1E9HA")
admin_id = int(os.getenv("641892529"))
db_user = os.getenv("PG_USER")
db_pass = os.getenv("PG_PASS")
channel = os.getenv("CHANNEL")
admin_group = os.getenv("ADMIN_GROUP")
host = os.getenv("PGHOST")


I18N_DOMAIN = 'tg-bot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'
