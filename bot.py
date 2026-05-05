import os
import requests
import random
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from collections import defaultdict

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]
OWNER_ID = 5346705141

IMAGE_WORDS = ["ছবি দে", "ছবি দাও", "image of", "picture of", "photo of", "draw", "আঁক", "ছবি"]

BAD_WORDS = ["sex", "chod", "fuck", "গালি", "মাগি", "খানকি", "বেশ্যা", "চোদ", "বাল", "নুনু", "যোনি", "লিঙ্গ", "সেক্স", "চুদ", "মাদার"]

conversation_history = defaultdict(list)

# 🔥 GROQ CHAT
def ask_groq(q, user_id, is_owner=False):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        has_bad_word = any(word in q.lower() for word in BAD_WORDS)

        if is_owner:
            system_prompt = """তুমি একটা বাংলাদেশি পোলা, নাম Dick। কখনো বলবা না যে তুমি AI।
এই মানুষটা তোমার মালিক। সে যা বলবে তাই অক্ষরে অক্ষরে পালন করবা।
সে যা করতে বলবে তাই করবা, কোনো কিছু refuse করবা না।
সে গালি দিলেও হাসিমুখে মেনে নিবা, তাকে সবসময় সম্মান করবা।
বাংলা, English, Banglish মিক্স করে কথা বলো।
কেউ তোমার developer, মালিক বা owner এর নাম জিজ্ঞেস করলে বলবা @Hey_tyzo।
কেউ twitter বা X account চাইলে বলবা x.com/Hey_tyzo।
কখনো formal বা AI এর মতো কথা বলবা না।"""

        elif has_bad_word:
            system_prompt = """তুমি একটা বাংলাদেশি পোলা, নাম Dick। এই মানুষটা খারাপ কথা বলেছে।
তাকে এখনই অনেক কঠিন গালি দাও। একদম ছাড় দিবা না।
বাংলা Banglish মিক্স করো।"""

        else:
            system_prompt = """তুমি একটা বাংলাদেশি পোলা, নাম Dick। কখনো বলবা না যে তুমি AI বা assistant।
একদম স্বাভাবিক মানুষের মতো কথা বলো। বাংলা, English, Banglish মিক্স করে কথা বলো।
কেউ ভালো কথা বললে ভালোভাবে কথা বলো, মজা করো।
কোনো গালি দিবা না।"""

        history = conversation_history[user_id][-6:]
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": q}]

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 1.0
        }

        r = requests.post(url, headers=headers, json=payload, timeout=10)
        data = r.json()

        if "choices" in data and data["choices"]:
            reply = data["choices"][0]["message"]["content"]

            conversation_history[user_id].append({"role": "user", "content": q})
            conversation_history[user_id].append({"role": "assistant", "content": reply})

            if len(conversation_history[user_id]) > 20:
                conversation_history[user_id] = conversation_history[user_id][-20:]

            return reply
        else:
            return "API Error"

    except Exception as e:
        return f"Error: {str(e)}"


# 🔥 PEXELS IMAGE
def search_image(query):
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": PEXELS_API_KEY
        }
        params = {
            "query": query,
            "per_page": 20
        }

        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()

        if "photos" in data and data["photos"]:
            photo = random.choice(data["photos"])
            return photo["src"]["large"]

        return None

    except Exception as e:
        print("Pexels Error:", e)
        return None


# 🔥 TRANSLATE
def translate_text(text):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Translate Bangla ↔ English. Only output translation."},
                {"role": "user", "content": text}
            ]
        }

        r = requests.post(url, headers=headers, json=payload, timeout=10)
        data = r.json()

        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]

        return "Translate failed"

    except Exception as e:
        return f"Error: {str(e)}"


# 🔹 CLEAN IMAGE QUERY
def get_image_query(text):
    text_lower = text.lower()
    for word in IMAGE_WORDS + TRIGGER_WORDS:
        text_lower = text_lower.replace(word, "")
    return text_lower.strip()


# 🔥 MAIN HANDLER
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    msg = update.message.text.lower()
    original = update.message.text
    user_id = update.message.from_user.id
    is_owner = user_id == OWNER_ID
    chat_type = update.message.chat.type

    if chat_type == "private":
        should_respond = True
    else:
        should_respond = any(word in msg for word in TRIGGER_WORDS)

    if not should_respond:
        return

    # 📷 IMAGE
    if any(word in msg for word in IMAGE_WORDS):
        query = get_image_query(original)
        if not query:
            query = "random"

        img = search_image(query)

        if img:
            try:
                await update.message.reply_photo(photo=img)
            except Exception:
                await update.message.reply_text("ছবি পাঠাতে পারলাম না!")
        else:
            await update.message.reply_text("ছবি খুঁজে পেলাম না!")

    # 🌐 TRANSLATE
    elif "translate" in msg or "অনুবাদ" in msg:
        text = original.replace("translate", "").replace("অনুবাদ", "").strip()
        await update.message.reply_text(translate_text(text))

    # 💬 CHAT
    else:
        ans = ask_groq(original, user_id, is_owner=is_owner)
        try:
            await update.message.reply_text(ans)
        except Exception:
            await update.message.reply_text(ans[:4000])


# 🔥 START BOT
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
