"""
Payment-related handlers
"""
import re
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class PaymentHandlers:
    def __init__(self, db, config):
        self.db = db
        self.config = config
    
    async def check_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /checkpayment command"""
        user_id = update.effective_user.id
        user_data = self.db.get_user_data(user_id)
        
        if user_data.get("paid"):
            await update.message.reply_text(
                "✅ You have already been verified as *PAID*. You can access your booked papers in /mypapers",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text(
            "💳 *Payment Verification*\n\nPlease enter your *M-Pesa transaction code* (e.g., QJD7H4XYZ1) below:",
            parse_mode='Markdown'
        )
        self.db.set_bot_prop("awaiting_payment_code", user_id)
    
    async def approve_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /approve command"""
        user_id = update.effective_user.id
        
        if user_id != self.config.MAIN_ADMIN:
            await update.message.reply_text("🚫 Admin access only.")
            return
        
        if not context.args:
            await update.message.reply_text("⚙️ Usage: `/approve <user_id>`", parse_mode='Markdown')
            return
        
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ User ID must be a number.")
            return
        
        # Update user status
        self.db.set_user_prop(target_id, "paid", True)
        
        # Remove from pending payments
        payments = self.db.get_bot_prop("pending_payments", [])
        payments = [p for p in payments if p["user_id"] != target_id]
        self.db.set_bot_prop("pending_payments", payments)
        
        # Notify user
        await context.bot.send_message(
            chat_id=target_id,
            text="🎉 *Payment Approved!*\n\nYou now have full access to your booked papers.\nUse /mypapers to continue.",
            parse_mode='Markdown'
        )
        
        await update.message.reply_text(f"✅ Approved payment for user ID: {target_id}")
    
    async def reject_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reject command"""
        user_id = update.effective_user.id
        
        if user_id != self.config.MAIN_ADMIN:
            await update.message.reply_text("🚫 Admin access only.")
            return
        
        if not context.args:
            await update.message.reply_text("⚙️ Usage: `/reject <user_id>`", parse_mode='Markdown')
            return
        
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ User ID must be a number.")
            return
        
        # Remove from pending payments
        payments = self.db.get_bot_prop("pending_payments", [])
        payments = [p for p in payments if p["user_id"] != target_id]
        self.db.set_bot_prop("pending_payments", payments)
        
        # Notify user
        await context.bot.send_message(
            chat_id=target_id,
            text="❌ Your payment could not be verified. Please recheck your transaction code and try again."
        )
        
        await update.message.reply_text(f"🚫 Rejected payment for user ID: {target_id}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle payment-related messages. Returns True if handled."""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check if we're awaiting payment code
        awaiting_payment = self.db.get_bot_prop("awaiting_payment_code")
        if awaiting_payment == user_id:
            code = message_text
            if not re.match(r'^[A-Z0-9]{8,12}$', code):
                await update.message.reply_text("⚠️ Invalid code format. Please send the correct M-Pesa code (e.g., QJD7H4XYZ1).")
                return True
            
            self.db.set_bot_prop("awaiting_payment_code", None)
            
            user_data = self.db.get_user_data(user_id)
            package_key = user_data.get("pending_package", "single")
            packages = self.db.get_bot_prop("pricing_packages", {})
            pkg = packages.get(package_key, {})
            price = pkg.get("price", "Unknown")
            
            # Store payment request
            payment = {
                "user_id": user_id,
                "name": update.effective_user.first_name,
                "code": code,
                "package": package_key,
                "price": price,
                "timestamp": update.message.date.timestamp()
            }
            
            payments = self.db.get_bot_prop("pending_payments", [])
            payments.append(payment)
            self.db.set_bot_prop("pending_payments", payments)
            
            # Notify admin
            await context.bot.send_message(
                chat_id=self.config.MAIN_ADMIN,
                text=(
                    f"💰 *Payment Pending Review*\n"
                    f"👤 {update.effective_user.first_name}\n"
                    f"🆔 {user_id}\n"
                    f"📦 {package_key}\n"
                    f"💳 Code: {code}\n"
                    f"💵 Amount: {price}"
                ),
                parse_mode='Markdown'
            )
            
            await update.message.reply_text(
                "✅ Thank you! Your payment has been received and is pending confirmation by the admin.\n\n"
                "You will be notified once verified."
            )
            return True
        
        return False