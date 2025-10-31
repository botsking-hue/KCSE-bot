import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
import re

from config import BOT_TOKEN, MAIN_ADMIN
from data_manager import DataManager

# Initialize data manager
data_manager = DataManager()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ================================
# Helper Functions
# ================================
async def send_admin_only_message(update: Update):
    await update.message.reply_text("🚫 Admin access only.")

def is_admin(user_id: int) -> bool:
    return data_manager.is_admin(user_id)

# ================================
# Command Handlers
# ================================

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_manager.update_user_stats()
    
    await update.message.reply_text(
        "👋 Welcome to *KCSE 2025 Prediction Papers Bot!*\n\n"
        "📅 Book daily prediction papers based on the official KCSE timetable.\n\n"
        "📂 Use /dashboard to manage your account.",
        parse_mode="Markdown"
    )

# Dashboard command
async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = data_manager.get_user(user.id)
    
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
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# Book command
async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    packages = data_manager.get_packages()
    
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
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# Admin Panel
async def adminpanel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_admin_only_message(update)
        return
    
    stats = data_manager.data.get("user_stats", {"total_users": 0})
    payments = data_manager.get_pending_payments()
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
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# View Payments
async def viewpayments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_admin_only_message(update)
        return
    
    payments = data_manager.get_pending_payments()
    
    if not payments:
        await update.message.reply_text("✅ No pending payments at the moment.")
        return
    
    msg = "💳 *Pending Payments*\n\n"
    for i, p in enumerate(payments, 1):
        msg += (
            f"{i}. 👤 {p.get('name', 'N/A')}\n"
            f"🆔 {p.get('user_id', 'N/A')}\n"
            f"📦 {p.get('package', 'N/A')}\n"
            f"💵 {p.get('price', 'N/A')}\n"
            f"💳 {p.get('code', 'N/A')}\n\n"
        )
    
    msg += "Use /approve <user_id> or /reject <user_id> to process."
    await update.message.reply_text(msg, parse_mode="Markdown")

# Edit Packages
async def editpackages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_admin_only_message(update)
        return
    
    packages = data_manager.get_packages()
    msg = "📦 *Current Packages*\n\n"
    
    for key, package in packages.items():
        msg += f"• {package['name']} - KES {package['price']}\n"
    
    msg += "\n\nTo update a price, use:\n`/setprice <package_key> <new_price>`"
    await update.message.reply_text(msg, parse_mode="Markdown")

# Set Price
async def setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_admin_only_message(update)
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("⚙️ Usage: `/setprice <package_key> <new_price>`", parse_mode="Markdown")
        return
    
    key = context.args[0]
    try:
        new_price = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Price must be a number.")
        return
    
    packages = data_manager.get_packages()
    if key not in packages:
        await update.message.reply_text("❌ Package not found.")
        return
    
    if data_manager.update_package_price(key, new_price):
        await update.message.reply_text(f"✅ Updated *{key}* package price to *KES {new_price}*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Failed to update package price.")

# Broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_admin_only_message(update)
        return
    
    data_manager.set_awaiting_broadcast(True)
    await update.message.reply_text("📢 Please send the message you want to broadcast to all users:")

# Add Admin
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id != MAIN_ADMIN:
        await update.message.reply_text("🚫 Only the main admin can add new admins.")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("⚙️ Usage: `/addadmin <telegram_id>`", parse_mode="Markdown")
        return
    
    try:
        new_admin = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Telegram ID must be a number.")
        return
    
    if data_manager.add_admin(new_admin):
        await update.message.reply_text(f"✅ Added new admin: {new_admin}")
    else:
        await update.message.reply_text("⚠️ That user is already an admin.")

# Remove Admin
async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id != MAIN_ADMIN:
        await update.message.reply_text("🚫 Only the main admin can remove admins.")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("⚙️ Usage: `/removeadmin <telegram_id>`", parse_mode="Markdown")
        return
    
    try:
        target = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Telegram ID must be a number.")
        return
    
    if data_manager.remove_admin(target):
        await update.message.reply_text(f"✅ Removed admin: {target}")
    else:
        await update.message.reply_text("❌ Failed to remove admin.")

# Check Payment
async def checkpayment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = data_manager.get_user(user.id)
    
    if user_data.get("paid"):
        await update.message.reply_text(
            "✅ You have already been verified as *PAID*. You can access your booked papers in /mypapers",
            parse_mode="Markdown"
        )
        return
    
    data_manager.set_awaiting_payment_code(user.id, True)
    await update.message.reply_text(
        "💳 *Payment Verification*\n\nPlease enter your *M-Pesa transaction code* (e.g., QJD7H4XYZ1) below:",
        parse_mode="Markdown"
    )

# Approve Payment
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id != MAIN_ADMIN:
        await send_admin_only_message(update)
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("⚙️ Usage: `/approve <user_id>`", parse_mode="Markdown")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ User ID must be a number.")
        return
    
    # Update user status
    data_manager.set_user_prop(target_id, "paid", True)
    data_manager.remove_pending_payment(target_id)
    
    # Notify user
    try:
        await context.bot.send_message(
            target_id,
            "🎉 *Payment Approved!*\n\nYou now have full access to your booked papers.\nUse /mypapers to continue.",
            parse_mode="Markdown"
        )
    except:
        pass  # User might have blocked the bot
    
    await update.message.reply_text(f"✅ Approved payment for user ID: {target_id}")

# Reject Payment
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id != MAIN_ADMIN:
        await send_admin_only_message(update)
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("⚙️ Usage: `/reject <user_id>`", parse_mode="Markdown")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ User ID must be a number.")
        return
    
    data_manager.remove_pending_payment(target_id)
    
    # Notify user
    try:
        await context.bot.send_message(
            target_id,
            "❌ Your payment could not be verified. Please recheck your transaction code and try again."
        )
    except:
        pass  # User might have blocked the bot
    
    await update.message.reply_text(f"🚫 Rejected payment for user ID: {target_id}")

# ================================
# Message Handlers
# ================================

# Handle broadcast message
async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data_manager.is_awaiting_broadcast():
        return
    
    data_manager.set_awaiting_broadcast(False)
    message_to_send = update.message.text
    users = data_manager.get_all_users()
    
    await update.message.reply_text(f"🚀 Broadcasting to {len(users)} users...")
    
    success_count = 0
    for user_id in users:
        try:
            await context.bot.send_message(user_id, message_to_send)
            success_count += 1
        except:
            continue
    
    await update.message.reply_text(f"✅ Broadcast completed! Sent to {success_count}/{len(users)} users.")

# Handle payment code
async def handle_payment_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not data_manager.is_awaiting_payment_code(user.id):
        return
    
    code = update.message.text
    if not re.match(r'^[A-Z0-9]{8,12}$', code):
        await update.message.reply_text("⚠️ Invalid code format. Please send the correct M-Pesa code (e.g., QJD7H4XYZ1).")
        return
    
    data_manager.set_awaiting_payment_code(user.id, False)
    
    user_data = data_manager.get_user(user.id)
    package_key = user_data.get("pending_package", "single")
    packages = data_manager.get_packages()
    pkg = packages.get(package_key, {})
    price = pkg.get("price", "Unknown")
    
    # Store payment request
    payment = {
        "user_id": user.id,
        "name": user.first_name,
        "code": code,
        "package": package_key,
        "price": price,
        "timestamp": update.message.date.timestamp()
    }
    
    data_manager.add_pending_payment(payment)
    
    # Notify admin
    try:
        await context.bot.send_message(
            MAIN_ADMIN,
            f"💰 *Payment Pending Review*\n"
            f"👤 {user.first_name}\n"
            f"🆔 {user.id}\n"
            f"📦 {package_key}\n"
            f"💳 Code: {code}\n"
            f"💵 Amount: {price}",
            parse_mode="Markdown"
        )
    except:
        pass
    
    await update.message.reply_text(
        "✅ Thank you! Your payment has been received and is pending confirmation by the admin.\n\n"
        "You will be notified once verified."
    )

# Handle callback queries (inline keyboard)
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    command = query.data
    
    # Map callback data to command handlers
    if command == "/dashboard":
        await dashboard(update, context)
    elif command == "/book":
        await book(update, context)
    elif command == "/viewpayments":
        await viewpayments(update, context)
    elif command == "/editpackages":
        await editpackages(update, context)
    elif command == "/broadcast":
        await broadcast(update, context)
    elif command == "/addadmin":
        await addadmin(update, context)
    elif command == "/removeadmin":
        await removeadmin(update, context)
    elif command == "/checkpayment":
        await checkpayment(update, context)
    # Add more callback handlers as needed

# ================================
# Main Function
# ================================

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dashboard", dashboard))
    application.add_handler(CommandHandler("book", book))
    application.add_handler(CommandHandler("adminpanel", adminpanel))
    application.add_handler(CommandHandler("viewpayments", viewpayments))
    application.add_handler(CommandHandler("editpackages", editpackages))
    application.add_handler(CommandHandler("setprice", setprice))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("addadmin", addadmin))
    application.add_handler(CommandHandler("removeadmin", removeadmin))
    application.add_handler(CommandHandler("checkpayment", checkpayment))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("reject", reject))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_code))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
