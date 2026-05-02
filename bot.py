import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# কনফিগারেশন
TELEGRAM_TOKEN = "8371594326:AAHPuCl6rKF-r6I-2H8iw7p5fRrqIc84Tqg"
GEMINI_API_KEY = "AIzaSyAu3klFKuD0sVpr9QriY-VuEOqScsvpmDk"
TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]

def ask_gemini(q):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"তুমি একটি বাংলাদেশি Telegram গ্রুপের মজাদার AI assistant। স্বাভাবিকভাবে বাংলায় কথা বলো। প্রশ্ন: {q}"
                }]
            }]
        }
        r = requests.post(url, json=payload)
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return "দুঃখিত, এখন উত্তর দিতে পারছি না।"

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    msg = update.message.text.lower()
    
    # ট্রিগার ওয়ার্ড চেক করা হচ্ছে
    if any(word in msg for word in TRIGGER_WORDS):
        # একটি প্রসেসিং মেসেজ দিলে ভালো দেখায়
        ans = ask_gemini(update.message.text)
        await update.message.reply_text(ans)

def main():
    # অ্যাপ্লিকেশন বিল্ড করা
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # হ্যান্ডলার অ্যাড করা (গ্রুপের মেসেজ পড়ার জন্য)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    
    print("বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
