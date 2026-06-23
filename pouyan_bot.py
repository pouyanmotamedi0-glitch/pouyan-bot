import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

print(f"Token: {TELEGRAM_TOKEN[:10]}")
print(f"API: {MISTRAL_API_KEY[:10]}")

user_histories = {}

def ask_mistral(user_id, msg):
    if user_id not in user_histories:
        user_histories[user_id] = []
    user_histories[user_id].append({"role": "user", "content": msg})
    try:
        h = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        d = {"model": "mistral-7b-instruct", "messages": user_histories[user_id][:5], "max_tokens": 300}
        r = requests.post("https://api.mistral.ai/v1/chat/completions", headers=h, json=d, timeout=5)
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            user_histories[user_id].append({"role": "assistant", "content": reply})
            return reply
        return f"خطا: {r.status_code}"
    except Exception as e:
        return f"خطا: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام!")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = ask_mistral(update.effective_user.id, update.message.text)
    await update.message.reply_text(r)

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, msg))
app.run_polling()
