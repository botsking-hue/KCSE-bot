"""
kcse_bot.bot - simplified webhook-compatible bot logic
This module provides `handle_update` which accepts the raw Telegram update (dict)
and replies using telegram.Bot. It keeps a cleaned subset of original bot features:
- /start command
- /help command
- basic admin panel trigger (/admin)
- payment code detection (simple regex)
- echo fallback

This design avoids running a polling loop and is safe for serverless platforms.
"""
import re
import asyncio
from typing import Dict, Any, Optional
from telegram import Bot, Update
from telegram.error import TelegramError
from .config import BOT_TOKEN, MAIN_ADMIN
from .data_manager import DataManager

data_manager = DataManager()
bot = Bot(token=BOT_TOKEN)

PAYMENT_CODE_RE = re.compile(r'^[A-Z0-9]{6,12}$', re.IGNORECASE)

async def _send_message(chat_id: int, text: str, reply_to: Optional[int] = None):
    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=reply_to)
    except TelegramError as e:
        # Logging is intentionally minimal for serverless environment
        print("TelegramError while sending message:", e)

async def handle_start(chat_id: int, from_user: Dict[str, Any]):
    name = from_user.get("first_name") or from_user.get("username") or "there"
    text = f"👋 Hi {name}! Welcome to the KCSE bot.\n\nUse /help to see available commands."
    await _send_message(chat_id, text)

async def handle_help(chat_id: int):
    text = (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - This help\n"
        "/admin - Admin panel (admin only)\n\n"
        "You can also send your payment code and the bot will validate it."
    )
    await _send_message(chat_id, text)

async def handle_admin(chat_id: int, from_user: Dict[str, Any]):
    user_id = int(from_user.get("id") or 0)
    if user_id != MAIN_ADMIN:
        await _send_message(chat_id, "⛔ You are not authorized to use admin commands.")
        return
    stats = data_manager.data.get("user_stats", {"total_users": 0})
    pending = data_manager.get_pending_payments()
    text = f"🔒 Admin Panel\nTotal users: {stats.get('total_users',0)}\nPending payments: {len(pending)}"
    await _send_message(chat_id, text)

async def handle_payment_code(chat_id: int, from_user: Dict[str, Any], code: str):
    # Very simple handling: mark as pending payment entry in data manager
    user_id = int(from_user.get("id") or 0)
    data_manager.add_pending_payment({"user_id": user_id, "code": code})
    await _send_message(chat_id, f"✅ Payment code received: `{code}`\nAn admin will verify it shortly.")

async def handle_echo(chat_id: int, text: str):
    # simple fallback
    await _send_message(chat_id, f"You said: {text}")

async def handle_update(update_dict: Dict[str, Any]):
    """
    Main entrypoint used by the webhook. Accepts the raw JSON update payload.
    """
    # Determine update type
    if "message" in update_dict:
        msg = update_dict["message"]
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        from_user = msg.get("from", {})
        text = msg.get("text") or msg.get("caption") or ""

        # Ensure minimal validation
        if not chat_id:
            return {"ok": False, "error": "missing chat id"}

        # Simple commands routing
        if text.startswith("/"):
            cmd = text.split()[0].lower()
            if cmd == "/start":
                await handle_start(chat_id, from_user)
                return {"ok": True}
            if cmd == "/help":
                await handle_help(chat_id)
                return {"ok": True}
            if cmd == "/admin":
                await handle_admin(chat_id, from_user)
                return {"ok": True}

        # payment code detection
        if text and PAYMENT_CODE_RE.match(text.strip()):
            await handle_payment_code(chat_id, from_user, text.strip())
            return {"ok": True}

        # fallback echo
        if text:
            await handle_echo(chat_id, text)
            return {"ok": True}

    elif "callback_query" in update_dict:
        # Minimal support: answer callback with a short message
        cq = update_dict["callback_query"]
        data = cq.get("data", "")
        from_user = cq.get("from", {})
        chat = cq.get("message", {}).get("chat", {})
        chat_id = chat.get("id")
        if chat_id:
            await _send_message(chat_id, f"Callback received: {data}")

    return {"ok": True}
