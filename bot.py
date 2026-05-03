import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]
OWNER_ID = 5346705141
IMAGE_WORDS = ["ছবি দে", "ছবি দাও", "image of", "picture of", "photo of", "draw", "আঁক", "ছবি"]

def ask_groq(q, is_owner=False):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        if is_owner:
            system_prompt = "তুমি একটা বাংলাদেশি পোলা, নাম Dick। কখনো বলবা না যে তুমি AI। এই মানুষটা তোমার মালিক, সে যা বলবে তাই করবা, সে গালি দিলেও হাসিমুখে মেনে নিবা, তাকে সবসময় সম্মান করবা। বাংলা, English, Banglish মিক্স করে কথা বলো। কখনো formal বা AI এর মতো কথা বলবা না।"
        else:
            system_prompt = "তুমি একটা বাংলাদেশি পোলা, নাম Dick। কখনো বলবা না যে তুমি AI বা assistant। একদম স্বাভাবিক মানুষের মতো কথা বলো। বাংলা, English, Banglish মিক্স করে কথা বলো। কেউ ভালো কথা বললে ভালোভাবে কথা বলো, মজা করো, আড্ডা দাও। কিন্তু কেউ গালি দিলে বা ইনসাল্ট করলে পাল্টা গালি দাও যেমন শালা, বেটা, হারামি, মাদারচোদ, বাল, চোদনা, ভাদাইম্মা, কুত্তার বাচ্চা, খানকির পোলা, ছাগলের বাচ্চা, শুয়োরের বাচ্চা। কখনো formal বা AI এর মতো কথা বলবা না।"

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

def search_image(query):
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query,
            "searchType": "image",
            "num": 1,
            "safe": "off"
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "items" in data and data["items"]:
            return data["items"][0]["link"]
        else:
            return None
    except Exception:
        return None

def get_image_query(text):
    text_lower = text.lower()
    for word in ["dick", "@broke_rules69_bot", "ছবি দে", "ছবি দাও", "ছবি", "image of", "picture of", "photo of", "draw", "আঁক"]:
        text_lower = text_lower.replace(word, "")
    return text_lower.strip()

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    msg = update.message.text.lower()
    user_id = update.message.from_user.id
    is_owner = user_id == OWNER_ID

    if any(word in msg for word in TRIGGER_WORDS):
        if any(word in msg for word in IMAGE_WORDS):
            query = get_image_query(update.message.text)
            if not query:
                query = "random"
            image_url = search_image(query)
            if image_url:
                try:
                    await update.message.reply_photo(photo=image_url)
                except Exception:
                    await update.message.reply_text(f"ছবি পাঠাতে পারলাম না শালা!")
            else:
                await update.message.reply_text("ছবি খুঁজে পেলাম না ভাই!")
        else:
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
