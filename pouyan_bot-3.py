import logging
import requests
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not TELEGRAM_TOKEN or not MISTRAL_API_KEY:
    print("❌ Token یا API Key وارد نشده!")
    exit(1)

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-7b-instruct"

SYSTEM_PROMPT = "تو دستیار هوش مصنوعی پویان هستی"

user_histories = {}

def ask_mistral(user_id, user_message):
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    user_histories[user_id].append({"role": "user", "content": user_message})
    
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {"model": MISTRAL_MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + user_histories[user_id], "max_tokens": 500}
    
    try:
        response = requests.post(MISTRAL_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            user_histories[user_id].append({"role": "assistant", "content": reply})
            return reply
        return "خطا"
    except:
        return "خطا در اتصال"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋 من پویان هستم")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = ask_mistral(user_id, user_message)
    await update.message.reply_text(reply)

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ بات شروع شد!")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
