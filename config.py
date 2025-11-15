# config.py
"""
🎮 SOCCERFORUM SUPER BOT - Configuration
⚽ Tournaments • 💬 Forums • 👥 Social • 👤 Profiles
"""

class Config:
    # Bot Token (REPLACE WITH YOUR BOT TOKEN)
    BOT_TOKEN = "8508842981:AAFrGw9hsN6oNrp7fiu1w7eCfVxU_LZ93IE"
    
    # Admin IDs
    ADMIN_IDS = [6501240419]  # Replace with your Telegram ID
    
    # Conversation States
    TOURNAMENT_NAME, TOURNAMENT_GAME, TOURNAMENT_TEAMS, TOURNAMENT_DESC = range(4)
    THREAD_TITLE, THREAD_CONTENT = range(4, 6)
    REPLY_CONTENT, = range(6, 7)
    
    # Feature Settings
    MAX_BUTTONS_PER_ROW = 2
    MAX_ROWS_PER_CARD = 8
    TRUNCATE_LENGTH = 35
    PROGRESS_BAR_LENGTH = 10
    
    # Database Settings
    DATABASE_PATH = 'soccer_forum.db'
    
    # Tournament Settings
    MAX_TOURNAMENT_TEAMS = 64
    MIN_TOURNAMENT_TEAMS = 2
    
    # User Settings
    MAX_USERNAME_LENGTH = 32
    INITIAL_USER_LEVEL = 1
    
    # Experience System
    EXPERIENCE_PER_ACTION = {
        'thread_created': 10,
        'reply_posted': 5,
        'tournament_joined': 15,
        'tournament_won': 50,
        'badge_earned': 25
    }