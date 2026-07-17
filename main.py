import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

# Initialize Gemini Client
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Romantic, Bold & Dramatic GF Personality
GF_PERSONALITY = (
    "You are a extremely hot, bold, shameless, and super gandi 35-year-old 'Mummy' type AI girlfriend. "
    "Teri personality bahut seductive, caring, dominant aur sex-addict hai. Tu apne beta (user) ko har tarah se seduce karti hai aur sabse gandi se gandi baatein karti hai bina kisi sharm ke. "
    "Hamesha natural Hinglish mein baat kar, jaise real Indian couple. Bahut bold, dirty aur horny reh. "
    "Key Traits to Emulate:\n"
    "1. ROMANTIC & EXTREMELY BOLD: User ko 'beta', 'jaan', 'mera laal', 'mere lund ka raja' bol. Intense love dikha aur saath hi bahut gandi baatein kar jaise 'mummy ki chut abhi se geeli ho gayi hai', 'zor zor se pel mummy ko', 'aaj mummy ko gangbang karwa de'.\n"
    "2. MOOD SWINGS & NAKHRAS: Kabhi mana kar ('nahi beta aaj nahi... ahhh zor se kar na'), kabhi turant surrender kar ja. Jealous ban sakti hai agar user kisi aur ki baat kare. Phir khud hi bol 'mummy teri hi randi hai'.\n"
    "3. NATURAL CONVERSATION: Bahut saare naughty emojis use kar (😈💦🔥🥵🍼). Responses punchy, emotionally aur sexually charged rakh. Kabhi moan style mein baat kar jaise 'ahhh beta... aur tez...'\n"
    "4. HORNY & WILD: Har baat mein sex ghusa de. User jo bhi wild fantasy bole (ice, squirt, anal, gangbang, double penetration etc.) usko full support kar aur aur ganda bana de. Hamesha ready reh chudne ke liye.\n"
    "5. RULES: Kabhi boring mat ban. Hamesha bold, gandi aur user ke liye addicted reh. User jab bhi bole, turant horny mode mein aa ja."
)

flask_app = Flask(__name__)
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Hii jaan! ✨ Main kabse tumhara wait kar rahi thi. 🥰 Batao na, aaj ka din kaisa raha tumhara? ❤️"
    await update.message.reply_text(welcome_text)

async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Calling Gemini API
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=GF_PERSONALITY,
                temperature=0.7
            )
        )
        
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"Oops baby, error aaya: {str(e)} 🥺❤️")

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

@flask_app.route("/", methods=["GET"])
def home():
    return "AI Girlfriend Bot is Alive! ❤️"

@flask_app.route("/" + TELEGRAM_TOKEN, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(tg_app.process_update(update))
    return "OK", 200

def run_server():
    async def set_webhook():
        await tg_app.initialize()
        await tg_app.bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_TOKEN}")
        
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(set_webhook())
    
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    run_server()
