#!/usr/bin/env python3
"""
Main entry point for KCSE Telegram Bot
"""
import logging
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.bot import KCSETelegramBot

def setup_logging():
    """Setup logging configuration."""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    """Start the bot."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Starting KCSE Telegram Bot...")
        bot = KCSETelegramBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()