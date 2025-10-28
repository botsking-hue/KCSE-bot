"""
Callback query handlers for inline keyboards.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.user_handlers import UserHandlers
from src.handlers.admin_handlers import AdminHandlers

logger = logging.getLogger(__name__)


class CallbackHandlers:
    """Handles all inline keyboard callbacks."""
    
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.user_handlers = UserHandlers(db, config)
        self.admin_handlers = AdminHandlers(db, config)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard callbacks."""
        query = update.callback_query
        await query.answer()
        
        command = query.data
        logger.info("Callback received: %s", command)
        
        # Map callback commands to handler functions
        handler_map = {
            # User commands
            '/book': self.user_handlers.book,
            '/dashboard': self.user_handlers.dashboard,
            '/mypapers': self.user_handlers.mypapers,
            '/pastpapers': self.user_handlers.pastpapers,
            '/checkpayment': self.user_handlers.check_payment,
            '/support': self.user_handlers.support,
            '/mynotifications': self.user_handlers.mynotifications,
            
            # Admin commands
            '/viewpayments': self.admin_handlers.view_payments,
            '/editpackages': self.admin_handlers.edit_packages,
            '/broadcast': self.admin_handlers.broad