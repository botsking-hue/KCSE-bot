# Vercel serverless function: api/webhook.py
from fastapi import FastAPI, Request, Response
import asyncio
import json
from kcse_bot import handle_update
app = FastAPI()

@app.post("/api/webhook")
async def webhook(request: Request):
    payload = await request.json()
    # Call bot handler
    try:
        result = await handle_update(payload)
    except Exception as e:
        # Log error for debugging on Vercel dashboard
        print("Error in handle_update:", e)
        return Response(content=json.dumps({"ok": False, "error": str(e)}), media_type="application/json", status_code=500)
    return Response(content=json.dumps(result), media_type="application/json")
