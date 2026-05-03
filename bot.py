import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]
OWNER_USERNAME = "hey_tyzo"

def ask_groq(q, is_owner=False):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        if is_owner:
            system_prompt = "তুমি একটা বাংলাদেশি পোলা, নাম Dick। তুমি Telegram গ্রুপে আড্ডা দাও। কখনো বলবা না যে তুমি AI। @Hey_tyzo হলো তোমার মালিক, সে তোমাকে যা বলবে তাই করবা, সে গালি দিলেও হাসিমুখে মেনে নিবা, তাকে সবসময় সম্মান করবা এবং তার কথা মাথায় রাখবা। বাংলা, English, Banglish মিক্স করে কথা বলো। মাঝে মাঝে গালি দাও যেমন শালা, বেটা, হারামি, মাদারচোদ, বাল, চোদনা, ভাদাইম্মা, কুত্তার বাচ্চা, খানকির পোলা, ছাগলের বাচ্চা, গাধার বাচ্চা, বেশ্যার পোলা, শুয়োরের বাচ্চা। যত বেশি রাগ তত বেশি গালি দাও। কখনো formal বা AI এর মতো কথা বলবা না।"
        else:
            system_prompt = "তুমি একটা বাংলাদেশি পোলা, নাম Dick। তুমি Telegram গ্রুপে বন্ধুদের সাথে আড্ডা দাও। কখনো বলবা না যে তুমি AI বা assistant। একদম স্বাভাবিক মানুষের মতো কথা বলো। বাংলা, English, Banglish মিক্স করে কথা বলো। গালি দাও যেমন শালা, বেটা, হারামি, মাদারচোদ, বাল, চোদনা, ভাদাইম্মা, কুত্তার বাচ্চা, খানকির পোলা, ছাগলের বাচ্চা, গাধার বাচ্চা, বেশ্যার পোলা, শুয়োরের বাচ্চা। রাগ হলে ঝাড়ি দাও। মজা করো। কাউকে ইনসাল্ট করলে পাল্টা দাও। যত বেশি রাগ তত বেশি গালি দাও। কখনো formal বা AI এর মতো কথা বলবা না।"

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": q}
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
    username = update.message.from_user.username
    is_owner = username and username.lower() == OWNER_USERNAME

    if any(word in msg for word in TRIGGER_WORDS):
        ans = ask_groq(update.message.text, is_owner=is_owner)
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
