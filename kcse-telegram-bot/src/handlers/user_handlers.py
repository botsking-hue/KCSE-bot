"""
User command handlers
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class UserHandlers:
    def __init__(self, db, config):
        self.db = db
        self.config = config
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        # Update user stats
        stats = self.db.get_bot_prop("user_stats", {})
        stats["total_users"] = self.db.get_total_users()
        self.db.set_bot_prop("user_stats", stats)
        
        await update.message.reply_text(
            "👋 Welcome to *KCSE 2025 Prediction Papers Bot!*\n\n"
            "📅 Book daily prediction papers based on the official KCSE timetable.\n\n"
            "📂 Use /dashboard to manage your account.",
            parse_mode='Markdown'
        )
    
    async def dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dashboard command"""
        user = update.effective_user
        user_id = user.id
        
        user_data = self.db.get_user_data(user_id)
        name = user_data.get("full_name", user.first_name)
        booked = user_data.get("bookings", [])
        paid = "✅ Paid" if user_data.get("paid") else "❌ Not Paid"
        user_package = user_data.get("package", "None")
        
        msg = (
            f"📊 *Your Dashboard*\n"
            f"👤 Name: {name}\n"
            f"🏫 Class: Form 4\n"
            f"📦 Package: {user_package}\n"
            f"📚 Booked: {', '.join(booked) if booked else 'None'}\n"
            f"💳 Status: {paid}"
        )
        
        keyboard = [
            [InlineKeyboardButton("📘 Book Papers", callback_data="/book")],
            [InlineKeyboardButton("📄 My Papers", callback_data="/mypapers")],
            [InlineKeyboardButton("📚 Past Papers", callback_data="/pastpapers")],
            [InlineKeyboardButton("💰 Check Payment", callback_data="/checkpayment")],
            [InlineKeyboardButton("🛠️ Support", callback_data="/support")],
            [InlineKeyboardButton("🔔 Notifications", callback_data="/mynotifications")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def book(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /book command"""
        packages = self.db.get_bot_prop("pricing_packages", {
            "single": {"name": "Single Paper", "price": 2000},
            "package_5": {"name": "5 Papers Package", "price": 8000},
            "subscription": {"name": "All Papers Subscription", "price": 15000},
            "school": {"name": "School Package", "price": 30000},
            "early_bird": {"name": "Early Bird Special", "price": 1500}
        })
        
        self.db.set_bot_prop("pricing_packages", packages)
        
        keyboard = [
            [InlineKeyboardButton(f"📘 Single Paper - KES {packages['single']['price']}", callback_data="/book_single")],
            [InlineKeyboardButton(f"📚 5 Papers - KES {packages['package_5']['price']}", callback_data="/book_package_5")],
            [InlineKeyboardButton(f"🗂️ All Papers - KES {packages['subscription']['price']}", callback_data="/book_subscription")],
            [InlineKeyboardButton(f"🏫 School Package - KES {packages['school']['price']}", callback_data="/book_school")],
            [InlineKeyboardButton(f"🐦 Early Bird - KES {packages['early_bird']['price']}", callback_data="/book_early_bird")],
            [InlineKeyboardButton("🔙 Back", callback_data="/dashboard")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📦 *Choose Your Package*\n\n🎯 Special discounts available for schools and early birds!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def mypapers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mypapers command"""
        await update.message.reply_text("📄 Your papers will be available here after payment verification.")
    
    async def pastpapers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pastpapers command"""
        await update.message.reply_text("📚 Past papers feature coming soon!")
    
    async def support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /support command"""
        await update.message.reply_text("🛠️ Contact support at: support@kcsepredictions.com")
    
    async def mynotifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mynotifications command"""
        await update.message.reply_text("🔔 Notification settings coming soon!")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        command = query.data
        
        # Map callback commands to handler functions
        handler_map = {
            '/book': self.book,
            '/dashboard': self.dashboard,
            '/mypapers': self.mypapers,
            '/pastpapers': self.pastpapers,
            '/checkpayment': self.check_payment,
            '/support': self.support,
            '/mynotifications': self.mynotifications,
        }
        
        if command in handler_map:
            # Create a fake update object for the callback
            from copy import copy
            fake_update = copy(update)
            fake_update.message = query.message
            await handler_map[command](fake_update, context)
    
    async def check_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /checkpayment command - redirect to payment handlers"""
        from src.handlers.payment_handlers import PaymentHandlers
        payment_handler = PaymentHandlers(self.db, self.config)
        await payment_handler.check_payment(update, context)