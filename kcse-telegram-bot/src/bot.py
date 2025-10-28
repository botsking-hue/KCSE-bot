"""
Main Telegram bot application for KCSE Prediction Papers.
"""
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from src.config import Config
from src.database import Database
from src.handlers import UserHandlers, AdminHandlers, PaymentHandlers, CallbackHandlers

logger = logging.getLogger(__name__)


class KCSETelegramBot:
    """Main bot class that orchestrates all handlers."""
    
    def __init__(self):
        self.config = Config()
        self.db = Database(self.config.DATABASE_FILE)
        
        # Initialize all handlers
        self.user_handlers = UserHandlers(self.db, self.config)
        self.admin_handlers = AdminHandlers(self.db, self.config)
        self.payment_handlers = PaymentHandlers(self.db, self.config)
        self.callback_handlers = CallbackHandlers(self.db, self.config)
        
        # Create application
        self.application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Setup all command and message handlers."""
        # User commands
        self.application.add_handler(CommandHandler("start", self.user_handlers.start))
        self.application.add_handler(CommandHandler("dashboard", self.user_handlers.dashboard))
        self.application.add_handler(CommandHandler("book", self.user_handlers.book))
        self.application.add_handler(CommandHandler("mypapers", self.user_handlers.mypapers))
        self.application.add_handler(CommandHandler("pastpapers", self.user_handlers.pastpapers))
        self.application.add_handler(CommandHandler("support", self.user_handlers.support))
        self.application.add_handler(CommandHandler("mynotifications", self.user_handlers.mynotifications))
        
        # Payment commands
        self.application.add_handler(CommandHandler("checkpayment", self.payment_handlers.check_payment))
        self.application.add_handler(CommandHandler("approve", self.payment_handlers.approve_payment))
        self.application.add_handler(CommandHandler("reject", self.payment_handlers.reject_payment))
        
        # Admin commands
        self.application.add_handler(CommandHandler("adminpanel", self.admin_handlers.admin_panel))
        self.application.add_handler(CommandHandler("viewpayments", self.admin_handlers.view_payments))
        self.application.add_handler(CommandHandler("editpackages", self.admin_handlers.edit_packages))
        self.application.add_handler(CommandHandler("setprice", self.admin_handlers.set_price))
        self.application.add_handler(CommandHandler("broadcast", self.admin_handlers.broadcast))
        self.application.add_handler(CommandHandler("addadmin", self.admin_handlers.add_admin))
        self.application.add_handler(CommandHandler("removeadmin", self.admin_handlers.remove_admin))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.callback_handlers.handle_callback))
        
        # Message handlers
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self._handle_message
            )
        )
    
    async def _handle_message(self, update: Update, context) -> None:
        """Handle regular text messages."""
        # Try payment handlers first
        if await self.payment_handlers.handle_payment_message(update, context):
            return
        
        # Try admin handlers next
        if await self.admin_handlers.handle_broadcast_message(update, context):
            return
        
        # Default message handler
        await update.message.reply_text(
            "🤔 I didn't understand that. Use /dashboard to see available commands."
        )
    
    def run(self) -> None:
        """Start the bot."""
        logger.info("🚀 Starting KCSE Telegram Bot...")
        logger.info("👑 Main Admin: %s", self.config.MAIN_ADMIN)
        self.application.run_polling()