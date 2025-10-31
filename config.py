import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8041016194:AAF3Wt88MlIihZbkmqGxZ_-jG7FxzxCf484')
MAIN_ADMIN = int(os.getenv('MAIN_ADMIN', '6501240419'))

# Initial packages
INITIAL_PACKAGES = {
    "single": {"name": "Single Paper", "price": 2000},
    "package_5": {"name": "5 Papers Package", "price": 8000},
    "subscription": {"name": "All Papers Subscription", "price": 15000},
    "school": {"name": "School Package", "price": 30000},
    "early_bird": {"name": "Early Bird Special", "price": 1500}
}
