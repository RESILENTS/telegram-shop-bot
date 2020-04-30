import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
admin_id = int(os.getenv("ADMIN_ID"))
db_user = os.getenv("PG_USER")
db_pass = os.getenv("PG_PASS")
channel = os.getenv("CHANNEL")
admin_group = os.getenv("ADMIN_GROUP")
host = os.getenv("PGHOST")


I18N_DOMAIN = 'tg-bot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'
