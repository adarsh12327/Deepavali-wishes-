import os
import json
import hmac
from fastapi import FastAPI, Header, HTTPException, Request
from aiogram.types import Update
from bot import bot, dp

app = FastAPI(title="Instagram Profile Helper Bot")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")


@app.get("/")
async def health():
    return {"ok": True, "service": "Instagram Profile Helper Bot"}


@app.post("/")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret is not configured")

    provided = x_telegram_bot_api_secret_token or ""
    if not hmac.compare_digest(provided, WEBHOOK_SECRET):
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    try:
        payload = await request.json()
        update = Update.model_validate(payload, context={"bot": bot})
        await dp.feed_update(bot, update)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid Telegram update") from exc
    except Exception as exc:
        # Avoid exposing internal exception details to public callers.
        raise HTTPException(status_code=500, detail="Webhook processing failed") from exc

    return {"ok": True}
