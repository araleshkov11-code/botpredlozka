from aiogram.types import InlineKeyboardButton
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
DATABASE = "database.db"
BANNED_FILE = "banned_users.json"
MAX_CAPTION_LEN = 1024