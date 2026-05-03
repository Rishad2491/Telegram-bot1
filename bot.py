import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# কনফিগারেশন
TELEGRAM_TOKEN = "8371594326:AAHPuCl6rKF-r6I-2H8iw7p5fRrqIc84Tqg"
GEMINI_API_KEY = "AIzaSyAu3klFKuD0sVpr9QriY-VuEOqScsvpmDk"
TRIGGER_WORDS = ["dick", "@broke_rules69_bot"]

def ask_gemini(q):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"তুমি একটি বাংলাদেশি Telegram গ্রুপের মজাদার AI assistant। স্বাভাবিকভাবে বাংলায় কথা বলো। প্রশ্ন: {q}"
                }]
            }],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        r = requests.post(url, json=payload)
        data = r.json()

        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Fuck"
            
    except Exception as e:
        return "Fuck"  # ✅ ঠিক করা হয়েছে

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    msg = update.message.text.lower()
    
    if any(word in msg for word in TRIGGER_WORDS):
        ans = ask_gemini(update.message.text)
        await update.message.reply_text(ans)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    print("বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
