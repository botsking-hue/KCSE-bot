"""
Configuration settings for the Telegram bot.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Bot configuration settings."""
    
    # Bot Token from @BotFather
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    # Main Admin Telegram ID
    MAIN_ADMIN = int(os.getenv('MAIN_ADMIN', '6501240419'))
    
    # Database configuration
    DATABASE_FILE = os.getenv('DATABASE_FILE', 'data/bot_data.json')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')
    
    # Payment configuration
    PAYMENT_TIMEOUT = int(os.getenv('PAYMENT_TIMEOUT', '300'))  # 5 minutes
    
    def validate(self) -> bool:
        """Validate configuration."""
        if self.BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            raise ValueError("BOT_TOKEN not set in .env file")
        return True