import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not TELEGRAM_TOKEN or not MISTRAL_API_KEY:
    print("❌ خطا")
    exit(1)

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-7b-instruct"

user_histories = {}

def ask_mistral(user_id, msg):
    if user_id not in user_histories:
        user_histories[user_id] = []
    user_histories[user_id].append({"role": "user", "content": msg})
    h = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    d = {"model": MISTRAL_MODEL, "messages": user_histories[user_id], "max_tokens": 500}
    try:
        r = requests.post(MISTRAL_URL, headers=h, json=d, timeout=10)
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            user_histories[user_id].append({"role": "assistant", "content": reply})
            return reply
        return "خطا"
    except:
        return "خطا"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ask_mistral(update.effective_user.id, update.message.text)
    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
