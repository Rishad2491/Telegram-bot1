import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

TELEGRAM_TOKEN = "8371594326:AAHPuCl6rKF-r6I-2H8iw7p5fRrqIc84Tqg"
GEMINI_API_KEY = "AIzaSyAu3klFKuD0sVpr9QriY-VuEOqScsvpmDk"

TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]

def ask_gemini(q):
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
        json={"contents":[{"parts":[{"text":f"তুমি একটি বাংলাদেশি Telegram গ্রুপের মজাদার AI assistant। স্বাভাবিকভাবে বাংলায় কথা বলো। প্রশ্ন: {q}"}]}]}
    )
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

async def handle(update, context):
    if not update.message or not update.message.text:
        return
    msg = update.message.text
    if not any(word in msg.lower() for word in TRIGGER_WORDS):
        return
    ans = ask_gemini(msg)
    await update.message.reply_text(ans)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle))
    print("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
