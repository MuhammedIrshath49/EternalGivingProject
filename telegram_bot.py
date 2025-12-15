import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# --------------------
# Load config
# --------------------
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Singapore")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "Singapore")

if not API_TOKEN:
    raise RuntimeError("API_TOKEN not set in .env")

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# --------------------
# Helpers
# --------------------
PRAYER_API = "https://api.aladhan.com/v1/timingsByCity"

def get_prayer_times(city, country):
    params = {
        "city": city,
        "country": country,
        "method": 3
    }
    res = requests.get(PRAYER_API, params=params, timeout=10)
    if res.status_code != 200:
        return None
    data = res.json()
    return data["data"]["timings"]

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
        "🔗 Google Form: (add link)\n"
        "📧 Email: roseofmadinah@email.com\n\n"
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
print("🤖 ROM PeerBot is running...")
bot.infinity_polling(skip_pending=True)
