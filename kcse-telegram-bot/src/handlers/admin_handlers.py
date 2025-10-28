"""
Admin command handlers
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class AdminHandlers:
    def __init__(self, db, config):
        self.db = db
        self.config = config
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        admins = self.db.get_bot_prop("admins", [self.config.MAIN_ADMIN])
        return user_id in admins
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /adminpanel command"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("🚫 Admin access only.")
            return
        
        stats = self.db.get_bot_prop("user_stats", {"total_users": self.db.get_total_users()})
        payments = self.db.get_bot_prop("pending_payments", [])
        total_pending = len(payments)
        
        msg = (
            f"👑 *Admin Dashboard*\n\n"
            f"👥 Total Users: {stats['total_users']}\n"
            f"💳 Pending Payments: {total_pending}\n\n"
            f"Select an action below:"
        )
        
        keyboard = [
            [InlineKeyboardButton("💰 View Payments", callback_data="/viewpayments")],
            [InlineKeyboardButton("📦 Edit Packages", callback_data="/editpackages")],
            [InlineKeyboardButton("📢 Broadcast Message", callback_data="/broadcast")],
            [InlineKeyboardButton("➕ Add Admin", callback_data="/addadmin")],
            [InlineKeyboardButton("➖ Remove Admin", callback_data="/removeadmin")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def view_payments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /viewpayments command"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("🚫 Admin access only.")
            return
        
        payments = self.db.get_bot_prop("pending_payments", [])
        if not payments:
            await update.message.reply_text("✅ No pending payments at the moment.")
            return
        
        msg = "💳 *Pending Payments*\n\n"
        for i, p in enumerate(payments):
            msg += f"{i + 1}. 👤 {p['name']}\n🆔 {p['user_id']}\n📦 {p['package']}\n💵 {p['price']}\n💳 {p['code']}\n\n"
        
        msg += "Use /approve <user_id> or /reject <user_id> to process."
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def edit_packages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /editpackages command"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("🚫 Admin access only.")
            return
        
        packages = self.db.get_bot_prop("pricing_packages", {})
        msg = "📦 *Current Packages*\n\n"
        for key, package in packages.items():
            msg += f"• {package['name']} - KES {package['price']}\n"
        
        msg += "\n\nTo update a price, use:\n`/setprice <package_key> <new_price>`"
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def set_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setprice command"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("🚫 Admin access only.")
            return
        
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("⚙️ Usage: `/setprice <package_key> <new_price>`", parse_mode='Markdown')
            return
        
        key = context.args[0]
        try:
            new_price = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Price must be a number.")
            return
        
        packages = self.db.get_bot_prop("pricing_packages", {})
        if key not in packages:
            await update.message.reply_text("❌ Package not found.")
            return
        
        packages[key]["price"] = new_price
        self.db.set_bot_prop("pricing_packages", packages)
        await update.message.reply_text(f"✅ Updated *{key}* package price to *KES {new_price}*", parse_mode='Markdown')
    
    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("🚫 Admin access only.")
            return
        
        await update.message.reply_text("📢 Please send the message you want to broadcast to all users:")
        self.db.set_bot_prop("awaiting_broadcast_message", user_id)
    
    async def add_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addadmin command"""
        user_id = update.effective_user.id
        
        if user_id != self.config.MAIN_ADMIN:
            await update.message.reply_text("🚫 Only the main admin can add new admins.")
            return
        
        if not context.args:
            await update.message.reply_text("⚙️ Usage: `/addadmin <telegram_id>`", parse_mode='Markdown')
            return
        
        try:
            new_admin = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Telegram ID must be a number.")
            return
        
        admins = self.db.get_bot_prop("admins", [self.config.MAIN_ADMIN])
        if new_admin in admins:
            await update.message.reply_text("⚠️ That user is already an admin.")
            return
        
        admins.append(new_admin)
        self.db.set_bot_prop("admins", admins)
        await update.message.reply_text(f"✅ Added new admin: {new_admin}")
    
    async def remove_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removeadmin command"""
        user_id = update.effective_user.id
        
        if user_id != self.config.MAIN_ADMIN:
            await update.message.reply_text("🚫 Only the main admin can remove admins.")
            return
        
        if not context.args:
            await update.message.reply_text("⚙️ Usage: `/removeadmin <telegram_id>`", parse_mode='Markdown')
            return
        
        try:
            target = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Telegram ID must be a number.")
            return
        
        admins = self.db.get_bot_prop("admins", [self.config.MAIN_ADMIN])
        new_list = [admin for admin in admins if admin != target]
        self.db.set_bot_prop("admins", new_list)
        await update.message.reply_text(f"✅ Removed admin: {target}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle admin-related messages. Returns True if handled."""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check if we're awaiting broadcast message
        awaiting_broadcast = self.db.get_bot_prop("awaiting_broadcast_message")
        if awaiting_broadcast == user_id:
            self.db.set_bot_prop("awaiting_broadcast_message", None)
            users = self.db.get_all_users()
            
            await update.message.reply_text(f"🚀 Broadcasting to {len(users)} users...")
            
            for user in users:
                try:
                    await context.bot.send_message(chat_id=user, text=message_text)
                except Exception as e:
                    logger.error(f"Failed to send message to {user}: {e}")
            
            await update.message.reply_text("✅ Broadcast completed successfully!")
            return True
        
        return False