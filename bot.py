import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from collections import defaultdict

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]
OWNER_ID = 5346705141
IMAGE_WORDS = ["ছবি দে", "ছবি দাও", "image of", "picture of", "photo of", "draw", "আঁক", "ছবি"]

conversation_history = defaultdict(list)

def ask_groq(q, user_id, is_owner=False):
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

        history = conversation_history[user_id][-6:]
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": q}]

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "max_tokens": 300,
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
            "num": 1,
            "safe": "off"
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "images_results" in data and data["images_results"]:
            return data["images_results"][0]["original"]
        else:
            return None
    except Exception:
        return None

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "bn"
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("main"):
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            return f"{city} এর আবহাওয়া:\nতাপমাত্রা: {temp}°C\nঅনুভূতি: {feels}°C\nআকাশ: {desc}\nআর্দ্রতা: {humidity}%"
        else:
            return "শহর খুঁজে পেলাম না ভাই!"
    except Exception as e:
        return f"Error: {str(e)}"

def get_news():
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "bd",
            "apiKey": NEWS_API_KEY,
            "pageSize": 5
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("articles"):
            news = "🔥 Latest News:\n\n"
            for i, article in enumerate(data["articles"][:5], 1):
                news += f"{i}. {article['title']}\n\n"
            return news
        else:
            return "নিউজ পেলাম না ভাই!"
    except Exception as e:
        return f"Error: {str(e)}"

def get_youtube(query):
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "youtube",
            "search_query": query,
            "api_key": SERPAPI_KEY
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "video_results" in data and data["video_results"]:
            video = data["video_results"][0]
            return f"{video['title']}\n{video['link']}"
        else:
            return "গান খুঁজে পেলাম না ভাই!"
    except Exception as e:
        return f"Error: {str(e)}"

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
                {"role": "system", "content": "তুমি একজন translator। যে text দেওয়া হবে সেটা বাংলা হলে English এ, English হলে বাংলায় translate করো। শুধু translation দাও, অন্য কিছু না।"},
                {"role": "user", "content": text}
            ],
            "max_tokens": 300
        }
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        data = r.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return "Translate করতে পারলাম না!"
    except Exception as e:
        return f"Error: {str(e)}"

def get_joke():
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "তুমি একটা মজাদার বাংলাদেশি। একটা মজার বাংলা জোকস বলো।"},
                {"role": "user", "content": "একটা মজার জোকস বলো"}
            ],
            "max_tokens": 200
        }
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        data = r.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return "জোকস পেলাম না!"
    except Exception as e:
        return f"Error: {str(e)}"

def roast_user(name):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "তুমি একটা বাংলাদেশি পোলা যে মানুষকে মজার ভাবে রোস্ট করে। বাংলা Banglish মিক্স করে রোস্ট করো, গালি দাও।"},
                {"role": "user", "content": f"{name} কে রোস্ট করো"}
            ],
            "max_tokens": 200,
            "temperature": 1.0
        }
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        data = r.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return "রোস্ট করতে পারলাম না!"
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

    if not any(word in msg for word in TRIGGER_WORDS):
        return

    # ছবি
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

    # আবহাওয়া
    elif "আবহাওয়া" in msg or "weather" in msg:
        city = msg.replace("dick", "").replace("আবহাওয়া", "").replace("weather", "").replace("@broke_rules69_bot", "").strip()
        if not city:
            city = "Dhaka"
        await update.message.reply_text(get_weather(city))

    # নিউজ
    elif "নিউজ" in msg or "news" in msg:
        await update.message.reply_text(get_news())

    # গান
    elif "গান" in msg or "song" in msg or "music" in msg:
        query = msg.replace("dick", "").replace("গান দে", "").replace("গান", "").replace("song", "").replace("music", "").replace("@broke_rules69_bot", "").strip()
        if not query:
            query = "bangla song"
        await update.message.reply_text(get_youtube(query))

    # ট্রান্সলেট
    elif "translate" in msg or "অনুবাদ" in msg:
        text = original.replace("dick", "").replace("translate", "").replace("অনুবাদ", "").replace("@broke_rules69_bot", "").strip()
        await update.message.reply_text(translate_text(text))

    # জোকস
    elif "জোকস" in msg or "joke" in msg or "হাসি" in msg:
        await update.message.reply_text(get_joke())

    # রোস্ট
    elif "রোস্ট" in msg or "roast" in msg:
        name = msg.replace("dick", "").replace("রোস্ট কর", "").replace("রোস্ট", "").replace("roast", "").replace("@broke_rules69_bot", "").strip()
        if not name:
            name = "এই মানুষটাকে"
        await update.message.reply_text(roast_user(name))

    # সাধারণ কথা
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
