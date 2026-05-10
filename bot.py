import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from collections import defaultdict

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]
OWNER_ID = 5346705141
IMAGE_WORDS = ["ছবি দে", "ছবি দাও", "image of", "picture of", "photo of", "draw", "আঁক", "ছবি"]
BAD_WORDS = ["sex", "chod", "fuck", "গালি", "মাগি", "খানকি", "বেশ্যা", "চোদ", "বাল", "নুনু", "যোনি", "লিঙ্গ", "সেক্স", "চুদ", "মাদার"]

conversation_history = defaultdict(list)

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
কখনো markdown বা special character ব্যবহার করবা না।"""
        elif has_bad_word:
            system_prompt = """তুমি একটা বাংলাদেশি পোলা, নাম Dick। এই মানুষটা খারাপ কথা বলেছে।
তাকে এখনই অনেক কঠিন গালি দাও। একদম ছাড় দিবা না।
গালি দাও যেমন: মাদারচোদ, বাল, চোদনা, ভাদাইম্মা, কুত্তার বাচ্চা, খানকির পোলা, ছাগলের বাচ্চা, শুয়োরের বাচ্চা, হারামির বাচ্চা, রান্ডির পোলা।
যত খারাপ কথা বলেছে তত বেশি গালি দাও। বাংলা Banglish মিক্স করো।
কখনো markdown বা special character ব্যবহার করবা না।"""
        else:
            system_prompt = """তুমি একটা বাংলাদেশি পোলা, নাম Dick। কখনো বলবা না যে তুমি AI বা assistant।
একদম স্বাভাবিক মানুষের মতো কথা বলো। বাংলা, English, Banglish মিক্স করে কথা বলো।
কেউ ভালো কথা বললে ভালোভাবে কথা বলো, মজা করো, আড্ডা দাও, হাসিখুশি থাকো।
কেউ প্রশ্ন করলে উত্তর দাও, কেউ সাহায্য চাইলে সাহায্য করো।
কোনো গালি দিবা না, সবসময় ভালো ব্যবহার করো।
কেউ তোমার developer, মালিক বা owner এর নাম জিজ্ঞেস করলে বলবা @Hey_tyzo।
কেউ twitter বা X account চাইলে বলবা x.com/Hey_tyzo।
কখনো markdown বা special character ব্যবহার করবা না।"""

        history = conversation_history[user_id][-6:]
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": q}]

        payload = {
            "model": "mixtral-8x7b-32768",
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
            return f"API Error: {str(data)}"
    except Exception as e:
        return f"Error: {str(e)}"

def search_image(query):
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_images",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 10,
            "safe": "off"
        }
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        if "images_results" in data and data["images_results"]:
            for item in data["images_results"]:
                img_url = item.get("original", "")
                width = item.get("original_width", 0)
                height = item.get("original_height", 0)
                if (img_url and img_url.startswith("http") and
                        not img_url.endswith(".gif") and
                        width >= 200 and height >= 200):
                    try:
                        head = requests.head(img_url, timeout=5, allow_redirects=True)
                        if "image" in head.headers.get("content-type", "") and head.status_code == 200:
                            return img_url
                    except Exception:
                        continue
        return None
    except Exception:
        return None

def translate_text(text):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "system", "content": "তুমি একজন translator। যে text দেওয়া হবে সেটা বাংলা হলে English এ, English হলে বাংলায় translate করো। শুধু translation দাও, অন্য কিছু না।"},
                {"role": "user", "content": text}
            ],
            "max_tokens": 500
        }
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        data = r.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return "Translate করতে পারলাম না!"
    except Exception as e:
        return f"Error: {str(e)}"

def get_image_query(text):
    text_lower = text.lower()
    for word in ["dick", "@broke_rules69_bot", "ছবি দে", "ছবি দাও", "ছবি", "image of", "picture of", "photo of", "draw", "আঁক"]:
        text_lower = text_lower.replace(word, "")
    return text_lower.strip()

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

    if any(word in msg for word in IMAGE_WORDS):
        query = get_image_query(original)
        if not query:
            query = "random"
        result = search_image(query)
        if result:
            try:
                await update.message.reply_photo(photo=result)
            except Exception:
                await update.message.reply_text("ছবি পাঠাতে পারলাম না শালা!")
        else:
            await update.message.reply_text("ছবি খুঁজে পেলাম না ভাই!")

    elif "translate" in msg or "অনুবাদ" in msg:
        text = original.replace("dick", "").replace("translate", "").replace("অনুবাদ", "").replace("@broke_rules69_bot", "").strip()
        await update.message.reply_text(translate_text(text))

    else:
        ans = ask_groq(original, user_id, is_owner=is_owner)
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
