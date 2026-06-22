import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# اینجا اطلاعاتت رو وارد کن
TELEGRAM_TOKEN = "ا8997118815:AAHGrH8hxs2vZwJEJWBHA9K2sVW-viAtS0c"
MISTRAL_API_KEY = "gddzmq6IjktiIeMb4qvnltx5IYaYgNoP"
# ==========================================

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-large-latest"

SYSTEM_PROMPT = """تو یه دستیار هوش مصنوعی فارسی‌زبان به اسم پویان هستی.
همیشه به فارسی جواب بده.
مودب، صادق و مفید باش.
اگه سوالی نمیدونی بگو نمیدونم."""

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
user_histories = {}

def ask_mistral(user_id, user_message):
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    user_histories[user_id].append({"role": "user", "content": user_message})
    
    # فقط ۱۰ پیام آخر نگه داره
    if len(user_histories[user_id]) > 10:
        user_histories[user_id] = user_histories[user_id][-10:]
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MISTRAL_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + user_histories[user_id],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    response = requests.post(MISTRAL_URL, headers=headers, json=data)
    result = response.json()
    reply = result["choices"][0]["message"]["content"]
    
    user_histories[user_id].append({"role": "assistant", "content": reply})
    return reply

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋 من پویان هستم، دستیار هوش مصنوعی شما.\nهر سوالی داری بپرس! 🤖"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("✅ مکالمه ریست شد!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        reply = ask_mistral(user_id, user_message)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("❌ خطا! دوباره امتحان کن.")
        logging.error(f"Error: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ بات پویان شروع به کار کرد!")
    app.run_polling()

if __name__ == "__main__":
    main()
n__":
    main()
