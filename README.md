# KCSE Bot - Vercel Webhook Version

This project converts your Telegram bot to webhook mode and packages it for Vercel (serverless).
Deploy the zip to Vercel or push to a Git repo connected to Vercel.

How it works
- Vercel serves /api/webhook (FastAPI) as a serverless endpoint.
- Telegram POSTs updates to /api/webhook after you configure the webhook.
- kcse_bot.handle_update processes updates and replies via the Bot API.

Deployment
1. Create a new Vercel project and upload this repository or connect via Git.
2. Add Environment Variables on Vercel:
   - BOT_TOKEN - your Telegram bot token
   - MAIN_ADMIN - admin Telegram id (default: 6501240419)
3. Deploy.
4. Set the webhook:

https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<your-vercel-app>.vercel.app/api/webhook

Notes
- Serverless functions are ephemeral. The data file bot_data.json is created in the function's working directory if used, but it may not persist between invocations. For persistent storage, configure an external DB or object storage and update kcse_bot/data_manager.py accordingly.
- This conversion keeps the core user flows (start/help/admin/payment code). If you want the full original command set migrated, I can port more handlers.
