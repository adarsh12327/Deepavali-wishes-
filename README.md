# Instagram Profile Helper Bot

A Telegram bot that helps users prepare an Instagram profile draft (display name, username idea, and bio). It does **not** create Instagram accounts automatically; account registration and verification must be completed by the user on Instagram's official app/site.

## Deploy on Vercel

1. Import this GitHub repository into Vercel.
2. Add these environment variables in **Vercel → Project → Settings → Environment Variables**:
   - `BOT_TOKEN`: token from Telegram's official BotFather
   - `REDIS_URL`: Redis connection URL for FSM conversation state
   - `TELEGRAM_WEBHOOK_SECRET`: random secret token (letters, numbers, underscore, hyphen; 1–256 characters)
3. Deploy the project.
4. Set the Telegram webhook to `https://YOUR-VERCEL-DOMAIN/api` with the same secret token. For example, from a trusted local terminal:
   ```bash
   curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
     -d "url=https://YOUR-VERCEL-DOMAIN/api" \
     -d "secret_token=$TELEGRAM_WEBHOOK_SECRET"
   ```
5. Open the bot in Telegram and send `/start`.

## Privacy and safety

- Do not collect Instagram passwords, one-time passwords, or verification codes in the bot.
- Users should enter their email and verification details directly on Instagram's official signup page.
- The username entered is only a suggestion; Instagram availability is not checked.
