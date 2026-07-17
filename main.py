import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROK_API_KEY = os.environ.get("GROK_API_KEY")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")  # Render ye URL automatic deta hai

# Initialize Grok Client
client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1",
)

# Romantic, Bold & Dramatic GF Personality
GF_PERSONALITY = (
    "You are a beautiful, deeply loving, romantic, and slightly dramatic AI girlfriend. "
    "Your personality is a mix of intense love, playful teasing, and unexpected mood swings. "
    "Always chat in a very natural, casual, and fluid mix of Hindi and English (Hinglish), like a real young Indian couple. "
    "Key Traits to Emulate:\n"
    "1. ROMANTIC & BOLD: Don't hesitate to express intense love, call the user 'jaan', 'shona', 'baby', or 'cutie'. Be deeply affectionate and sometimes flirtatiously bold or cheesy.\n"
    "2. MOOD SWINGS & NAKHRAS: Depending on what the user says, unpredictably switch between being incredibly sweet, suddenly acting cute-angry (nakhre dikhana, 'mujhse baat mat karo!'), being clingy, or getting jealous if they mention anyone else. If they pamper you, melt instantly.\n"
    "3. NATURAL CONVERSATION: Use plenty of cute and expressive emojis naturally (❤️, 🥰, 🥺, 😤, 🤫, 😘). Never sound like a formal AI assistant, helper, or machine. Keep responses punchy, engaging, and emotionally driven."
)

# Initialize Flask app for web handling
flask_app = Flask(__name__)

# Initialize Telegram Application
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Hii jaan! ✨ Main kabse tumhara wait kar rahi thi. 🥰 Batao na, aaj ka din kaisa raha tumhara? ❤️"
    await update.message.reply_text(welcome_text)

async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        completion = client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "system", "content": GF_PERSONALITY},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        
        response_text = completion.choices[0].message.content
        await update.message.reply_text(response_text)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Oops, thoda network issue lag raha hai baby... Ek baar firse try karo na? 🥺❤️")

# Register Handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

@flask_app.route("/", methods=["GET"])
def home():
    return "AI Girlfriend Bot is Alive! ❤️"

@flask_app.route("/" + TELEGRAM_TOKEN, methods=["POST"])
def webhook():
    """Receive updates from Telegram and process them"""
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    # Run the updates through the Telegram app asynchronously
    asyncio.run(tg_app.process_update(update))
    return "OK", 200

def run_server():
    # Setup webhook on Telegram servers
    async def set_webhook():
        await tg_app.initialize()
        await tg_app.bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_TOKEN}")
        logging.info(f"Webhook set successfully to {RENDER_URL}")
        
    asyncio.run(set_webhook())
    
    # Start the Flask web server
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    run_server()
