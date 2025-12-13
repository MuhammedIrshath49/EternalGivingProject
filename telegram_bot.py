import os
import requests
import telebot
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
        "🕌 *What can I help you with?*\n\n"
        "• /prayertimes — View today’s prayer times\n"
        "• /praywhere — Find nearby mosques & musollahs\n"
        "• /remind — Enable prayer reminders\n"
        "• /unremind — Disable prayer reminders\n"
        "• /tasbih — Pause & remember Allah ﷻ\n"
        "• /tabung — Support Amal Jariah projects\n"
        "• /feedback — Share suggestions or improvements\n\n"
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
        bot.reply_to(message, "❌ Unable to fetch prayer times right now.")
        return

    text = (
        f"🕋 *Prayer Times Today ({DEFAULT_CITY})*\n\n"
        f"🌅 Fajr: {timings['Fajr']}\n"
        f"☀️ Dhuhr: {timings['Dhuhr']}\n"
        f"🌤 Asr: {timings['Asr']}\n"
        f"🌇 Maghrib: {timings['Maghrib']}\n"
        f"🌙 Isha: {timings['Isha']}\n\n"
        "May Allah accept our prayers 🤲"
    )
    bot.reply_to(message, text)

# --------------------
# /praywhere
# --------------------
@bot.message_handler(commands=["praywhere"])
def pray_where(message):
    text = (
        "📍 *Find Nearby Mosques & Musollahs*\n\n"
        "Please share your location using Telegram’s 📎 attachment button:\n"
        "➡️ Attach → Location\n\n"
        "In shā’ Allāh, I’ll help you find a place to pray."
    )
    bot.reply_to(message, text)

# --------------------
# /remind
# --------------------
@bot.message_handler(commands=["remind"])
def remind(message):
    text = (
        "🔔 *Prayer Reminders Enabled*\n\n"
        "You will receive:\n"
        "• A reminder *10 minutes before* prayer time\n"
        "• A reminder *at the exact prayer time*\n\n"
        "May Allah help us stay steadfast 🤍"
    )
    bot.reply_to(message, text)

# --------------------
# /unremind
# --------------------
@bot.message_handler(commands=["unremind"])
def unremind(message):
    text = (
        "❌ *Prayer Reminders Disabled*\n\n"
        "You will no longer receive prayer reminders.\n"
        "You can re-enable anytime using /remind."
    )
    bot.reply_to(message, text)

# --------------------
# /tasbih
# --------------------
@bot.message_handler(commands=["tasbih"])
def tasbih(message):
    text = (
        "📿 *Tasbih Time*\n\n"
        "Take a moment to remember Allah ﷻ\n\n"
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
        "💚 *Amal Jariah – Ongoing Projects*\n\n"
        "Support beneficial projects in:\n"
        "• Cambodia\n"
        "• Philippines\n"
        "• India\n"
        "• Bangladesh\n\n"
        "📌 *How it works:*\n"
        "1️⃣ Scan the QR code\n"
        "2️⃣ Make your donation\n"
        "3️⃣ Screenshot your receipt\n"
        "4️⃣ Submit when instructed\n\n"
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
        "If you have suggestions, ideas, or notice an issue:\n\n"
        "🔗 Google Form: (add link here)\n"
        "📧 Email: roseofmadinah@email.com\n\n"
        "JazakAllahu khair for helping us improve 🌹"
    )
    bot.reply_to(message, text)

# --------------------
# Fallback
# --------------------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(
        message,
        "❓ I didn’t understand that.\n\nUse /help to see available commands."
    )

# --------------------
# Start polling
# --------------------
print("🤖 ROM PeerBot is running...")
bot.infinity_polling()
