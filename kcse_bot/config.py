import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MAIN_ADMIN = int(os.getenv("MAIN_ADMIN", "6501240419"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment")
