import os
import sys
import logging
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

# --------------------
# Logging setup
# --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --------------------
# Load config
# --------------------
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Singapore")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "Singapore")
PORT = int(os.getenv("PORT", "8080"))

if not API_TOKEN:
    logger.error("API_TOKEN not set in environment variables")
    raise RuntimeError("API_TOKEN not set in .env")

logger.info(f"Bot starting with default city: {DEFAULT_CITY}")
bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# --------------------
# Health check server (for Render)
# --------------------
app = Flask(__name__)

@app.route('/')
def health_check():
    return {'status': 'ok', 'message': 'ROM PeerBot is running'}, 200

@app.route('/health')
def health():
    return {'status': 'healthy', 'bot': 'active'}, 200

def run_flask():
    """Run Flask server in a separate thread"""
    logger.info(f"Flask server starting on 0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False, threaded=True)

# --------------------
# Helpers
# --------------------
PRAYER_API = "https://api.aladhan.com/v1/timingsByCity"

def get_prayer_times(city, country):
    try:
        params = {
            "city": city,
            "country": country,
            "method": 3
        }
        res = requests.get(PRAYER_API, params=params, timeout=10)
        if res.status_code != 200:
            logger.warning(f"Prayer API returned status {res.status_code}")
            return None
        data = res.json()
        logger.info(f"Successfully fetched prayer times for {city}, {country}")
        return data["data"]["timings"]
    except Exception as e:
        logger.error(f"Error fetching prayer times: {e}")
        return None

# --------------------
# /start & /help
# --------------------
@bot.message_handler(commands=["start", "help"])
def start(message):
    text = (
        "🌹 *ٱلسَّلَامُ عَلَيْكُمْ وَرَحْمَةُ ٱللَّٰهِ وَبَرَكَاتُهُ*\n\n"
        "Welcome to *ROM PeerBot* 🤍\n"
        "A gentle companion to help us stay consistent with *Ṣalāh*, *Dhikr*, and *ʿAmal*.\n\n"
        "🕌 *Available Commands*\n\n"
        "• /prayertimes — View today’s ṣalāh times\n"
        "• /praywhere — Find nearby masājid\n"
        "• /remind — Enable ṣalāh reminders\n"
        "• /unremind — Disable ṣalāh reminders\n"
        "• /tasbih — Dhikr & remembrance\n"
        "• /tabung — Support ʿAmal Jāriyah\n"
        "• /feedback — Share feedback\n\n"
        "You can also use the *Menu* button below ⬇️\n\n"
        "May Allah place barakah in our intentions 🌙"
    )
    bot.reply_to(message, text)

# --------------------
# /prayertimes
# --------------------
@bot.message_handler(commands=["prayertimes"])
def prayer_times(message):
    timings = get_prayer_times(DEFAULT_CITY, DEFAULT_COUNTRY)

    if not timings:
        bot.reply_to(message, "❌ Unable to fetch ṣalāh times right now.")
        return

    text = (
        f"🕋 *Ṣalāh Times Today ({DEFAULT_CITY})*\n\n"
        f"🌅 Fajr: {timings['Fajr']}\n"
        f"☀️ Dhuhr: {timings['Dhuhr']}\n"
        f"🌤 Asr: {timings['Asr']}\n"
        f"🌇 Maghrib: {timings['Maghrib']}\n"
        f"🌙 Isha: {timings['Isha']}\n\n"
        "May Allah accept our ṣalāh 🤲"
    )
    bot.reply_to(message, text)

# --------------------
# /praywhere
# --------------------
@bot.message_handler(commands=["praywhere"])
def pray_where(message):
    text = (
        "📍 *Find Nearby Masājid & Musollahs*\n\n"
        "Please share your location using Telegram’s 📎 attachment button:\n"
        "➡️ Attach → Location\n\n"
        "إِنْ شَاءَ ٱللَّٰهُ, I’ll help you find a place to pray."
    )
    bot.reply_to(message, text)

# --------------------
# /remind
# --------------------
@bot.message_handler(commands=["remind"])
def remind(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ Enable Reminders", callback_data="remind_on"),
        InlineKeyboardButton("❌ Disable Reminders", callback_data="remind_off")
    )

    text = (
        "🔔 *Ṣalāh Reminder Settings*\n\n"
        "Choose your preference:"
    )
    bot.reply_to(message, text, reply_markup=markup)

# --------------------
# /unremind
# --------------------
@bot.message_handler(commands=["unremind"])
def unremind(message):
    text = (
        "❌ *Ṣalāh Reminders Disabled*\n\n"
        "You will no longer receive ṣalāh reminders.\n"
        "You may re-enable them anytime using /remind."
    )
    bot.reply_to(message, text)

# --------------------
# /tasbih
# --------------------
@bot.message_handler(commands=["tasbih"])
def tasbih(message):
    text = (
        "📿 *Tasbih Time*\n\n"
        "• *أَسْتَغْفِرُ ٱللَّٰهَ* (100×)\n"
        "• *ٱللَّٰهُ ٱللَّٰهُ*\n"
        "• *ٱللَّهُمَّ صَلِّ عَلَىٰ مُحَمَّدٍ ﷺ*\n\n"
        "﴿ أَلَا بِذِكْرِ ٱللَّٰهِ تَطْمَئِنُّ ٱلْقُلُوبُ ﴾\n"
        "_Verily, in the remembrance of Allah do hearts find rest._ (13:28)"
    )
    bot.reply_to(message, text)

# --------------------
# /tabung
# --------------------
@bot.message_handler(commands=["tabung"])
def tabung(message):
    text = (
        "💚 *ʿAmal Jāriyah – Ongoing Projects*\n\n"
        "Support beneficial projects in:\n"
        "• Cambodia\n"
        "• Philippines\n"
        "• India\n"
        "• Bangladesh\n\n"
        "May Allah multiply your rewards 🤲"
    )
    bot.reply_to(message, text)

# --------------------
# /feedback
# --------------------
@bot.message_handler(commands=["feedback"])
def feedback(message):
    text = (
        "📩 *We Value Your Feedback*\n\n"
        "🔗 Google Form: https://forms.gle/LMtXXfuKVbW6USor7\n\n"
        "📧 Email: rompeerbot@email.com\n\n"
        "JazakAllahu khair 🌹"
    )
    bot.reply_to(message, text)

# --------------------
# Callback handler (ONLY for reminder toggles)
# --------------------
@bot.callback_query_handler(func=lambda call: call.data in ["remind_on", "remind_off"])
def handle_reminder_toggle(call):
    bot.answer_callback_query(call.id)

    if call.data == "remind_on":
        text = (
            "🔔 *Ṣalāh Reminders Enabled*\n\n"
            "You will receive reminders:\n"
            "• 10 minutes before ṣalāh\n"
            "• At exact ṣalāh time\n\n"
            "May Allah help us remain steadfast 🤍"
        )
    else:
        text = (
            "❌ *Ṣalāh Reminders Disabled*\n\n"
            "You will no longer receive ṣalāh reminders."
        )

    bot.send_message(call.message.chat.id, text)

# --------------------
# Fallback
# --------------------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(
        message,
        "❓ I didn’t understand that.\n\nPlease use the Menu button below ⬇️ or /help."
    )

# --------------------
# Start polling
# --------------------
if __name__ == "__main__":
    try:
        # Start Flask health check server in background thread FIRST
        logger.info(f"Starting health check server on 0.0.0.0:{PORT}")
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Give Flask a moment to start and bind to the port
        import time
        time.sleep(2)
        logger.info(f"Health check server should be running at http://0.0.0.0:{PORT}")
        
        # Start bot polling
        logger.info("🤖 ROM PeerBot is starting...")
        logger.info("Bot is now running and polling for messages")
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise
