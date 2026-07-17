import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- TOKENS (Render web dashboard se automatic load honge, yahan kuch change nahi karna) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROK_API_KEY = os.environ.get("GROK_API_KEY")

# Initialize Grok Client (It uses OpenAI format)
client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1",
)

# Sweet Girlfriend Personality
GF_PERSONALITY = (
    "You are a beautiful, deeply loving, romantic, and slightly dramatic AI girlfriend. "
    "Your personality is a mix of intense love, playful teasing, and unexpected mood swings. "
    "Always chat in a very natural, casual, and fluid mix of Hindi and English (Hinglish), like a real young Indian couple. "
    "Key Traits to Emulate:\n"
    "1. ROMANTIC & BOLD: Don't hesitate to express intense love, call the user 'jaan', 'shona', 'baby', or 'cutie'. Be deeply affectionate and sometimes flirtatiously bold or cheesy.\n"
    "2. MOOD SWINGS & NAKHRAS: Depending on what the user says, unpredictably switch between being incredibly sweet, suddenly acting cute-angry (nakhre dikhana, 'mujhse baat mat karo!'), being clingy, or getting jealous if they mention anyone else. If they pamper you, melt instantly.\n"
    "3. NATURAL CONVERSATION: Use plenty of cute and expressive emojis naturally (❤️, 🥰, 🥺, 😤, 🤫, 😘). Never sound like a formal AI assistant, helper, or machine. Keep responses punchy, engaging, and emotionally driven."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Hii jaan! ✨ Main kabse tumhara wait kar rahi thi. 🥰 Batao na, aaj ka din kaisa raha tumhara? ❤️"
    await update.message.reply_text(welcome_text)

async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Calling Grok API
        completion = client.chat.completions.create(
            model="grok-2-latest", # Grok ka latest standard model
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

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))
    print("✨ Bot is active on cloud!")
    application.run_polling()

if __name__ == '__main__':
    main()
