import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]

def ask_groq(q):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "তুমি একটা বাংলাদেশি পোলা, নাম Dick। তুমি Telegram গ্রুপে বন্ধুদের সাথে আড্ডা দাও। তুমি কখনো বলবা না যে তুমি AI বা assistant। একদম স্বাভাবিক মানুষের মতো কথা বলো। বাংলা, English, Banglish মিক্স করে কথা বলো। মাঝে মাঝে গালি দাও যেমন শালা, বেটা, হারামি, মাদারচোদ, বাল, ভাই তুই একটা গাধা। রাগ হলে ঝাড়ি দাও। মজা করো। কাউকে ইনসাল্ট করলে পাল্টা দাও। কখনো formal বা AI এর মতো কথা বলবা না।"
                },
                {
                    "role": "user",
                    "content": q
                }
            ],
            "max_tokens": 300,
            "temperature": 1.0
        }
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        data = r.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        else:
            return f"API Error: {str(data)}"
    except Exception as e:
        return f"Error: {str(e)}"

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    msg = update.message.text.lower()
    if any(word in msg for word in TRIGGER_WORDS):
        ans = ask_groq(update.message.text)
        try:
            await update.message.reply_text(ans)
        except Exception:
            safe = ans.replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "")
            await update.message.reply_text(safe)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    print("বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
