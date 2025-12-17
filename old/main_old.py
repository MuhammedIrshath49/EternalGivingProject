import os
import sys
import logging
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Singapore")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "Singapore")

if not API_TOKEN:
    raise RuntimeError("API_TOKEN not set in .env")

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
scheduler = BackgroundScheduler()

PRAYER_API = "https://api.aladhan.com/v1/timingsByCity"
MOSQUE_API = "https://nominatim.openstreetmap.org/search"

user_settings = {}

def get_prayer_times(city, country):
    try:
        res = requests.get(PRAYER_API, params={"city": city, "country": country, "method": 3}, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return data["data"]["timings"], data["data"]["date"]["readable"]
        return None, None
    except Exception as e:
        logger.error(f"Error fetching prayer times: {e}")
        return None, None

def find_nearby_mosques(lat, lon):
    try:
        res = requests.get(MOSQUE_API, params={"format": "json", "q": "mosque", "lat": lat, "lon": lon, "limit": 5}, headers={"User-Agent": "ROM_PeerBot/1.0"}, timeout=10)
        return res.json() if res.status_code == 200 else None
    except Exception as e:
        logger.error(f"Error finding mosques: {e}")
        return None

def schedule_prayer_reminders(user_id):
    timings, _ = get_prayer_times(DEFAULT_CITY, DEFAULT_COUNTRY)
    if not timings:
        return
    
    for prayer in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
        time_str = timings[prayer]
        prayer_time = datetime.strptime(time_str, "%H:%M").replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        
        if prayer_time > datetime.now():
            reminder_time = prayer_time - timedelta(minutes=10)
            if reminder_time > datetime.now():
                scheduler.add_job(
                    func=lambda p=prayer, u=user_id: send_prayer_reminder(u, p, "10 minutes"),
                    trigger='date',
                    run_date=reminder_time,
                    id=f"prayer_reminder_{user_id}_{prayer}_10min",
                    replace_existing=True
                )
            scheduler.add_job(
                func=lambda p=prayer, u=user_id: send_prayer_reminder(u, p, "entered"),
                trigger='date',
                run_date=prayer_time,
                id=f"prayer_time_{user_id}_{prayer}",
                replace_existing=True
            )

def send_prayer_reminder(user_id, prayer, status):
    try:
        if status == "10 minutes":
            bot.send_message(user_id, f"🔔 {prayer} prayer in 10 minutes")
        else:
            bot.send_message(user_id, f"🕌 {prayer} prayer time has entered")
    except Exception as e:
        logger.error(f"Error sending prayer reminder to {user_id}: {e}")

@bot.message_handler(commands=["start", "help"])
def start(message):
    text = (
        "🌹 *ٱلسَّلَامُ عَلَيْكُمْ وَرَحْمَةُ ٱللَّٰهِ وَبَرَكَاتُهُ*\n\n"
        "Welcome to *ROM PeerBot — Your Personal Islamic Companion 💚* 🤍\n"
        "A gentle companion to help us stay consistent with *Ṣalāh*, *Dhikr*, and *Awrad*.\n\n"
        "🕌 *Available Commands*\n\n"
        "• /morningadkar — Enable Morning Adkar Reminder\n"
        "• /eveningadkar — Enable Evening Adkar Reminder\n"
        "• /adkarbeforesleep — Enable Adkar before Sleep\n"
        "• /allahuallah — Activate Allahu Allah Dhikr\n"
        "• /prayertimes — View today's ṣalāh times\n"
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

@bot.message_handler(commands=["prayertimes"])
def prayer_times(message):
    timings, date = get_prayer_times(DEFAULT_CITY, DEFAULT_COUNTRY)
    if not timings:
        bot.reply_to(message, "❌ Unable to fetch ṣalāh times right now.")
        return
    text = f"🕋 *Ṣalāh Times Today ({DEFAULT_CITY})*\n{date}\n\n🌅 Fajr: {timings['Fajr']}\n🌄 Sunrise: {timings['Sunrise']}\n☀️ Dhuhr: {timings['Dhuhr']}\n🌤 Asr: {timings['Asr']}\n🌇 Maghrib: {timings['Maghrib']}\n🌙 Isha: {timings['Isha']}\n\nMay Allah accept our ṣalāh 🤲"
    bot.reply_to(message, text)

@bot.message_handler(commands=["praywhere"])
def pray_where(message):
    bot.reply_to(message, "📍 *Find Nearby Masājid & Musollahs*\n\nPlease share your location using Telegram's 📎 attachment button:\n➡️ Attach → Location\n\nإِنْ شَاءَ ٱللَّٰهُ, I'll help you find a place to pray.")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    mosques = find_nearby_mosques(message.location.latitude, message.location.longitude)
    if not mosques:
        bot.reply_to(message, "❌ No masājid found nearby. Try a different location.")
        return
    text = "🕌 *Nearby Masājid*\n\n"
    for i, m in enumerate(mosques[:5], 1):
        text += f"{i}. {m.get('display_name', 'Unknown').split(',')[0]}\n   📍 [View on Map](https://www.google.com/maps?q={m.get('lat')},{m.get('lon')})\n\n"
    bot.reply_to(message, text + "May Allah make it easy for you 🤲")

@bot.message_handler(commands=["remind"])
def remind(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("✅ Enable", callback_data="remind_on"), InlineKeyboardButton("❌ Disable", callback_data="remind_off"))
    bot.reply_to(message, "🔔 *Ṣalāh Reminder Settings*\n\nChoose your preference:", reply_markup=markup)

@bot.message_handler(commands=["unremind"])
def unremind(message):
    user_settings.setdefault(message.from_user.id, {})['prayer_reminders'] = False
    bot.reply_to(message, "❌ *Ṣalāh Reminders Disabled*\n\nYou will no longer receive ṣalāh reminders.\nYou may re-enable them anytime using /remind.")

@bot.message_handler(commands=["morningadkar"])
def morning_adkar(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("✅ Enable", callback_data="morning_on"), InlineKeyboardButton("❌ Disable", callback_data="morning_off"))
    bot.reply_to(message, "🌅 *Morning Adkar Reminder*\n\nEnable daily morning adkar 15 mins after Fajr?", reply_markup=markup)

@bot.message_handler(commands=["eveningadkar"])
def evening_adkar(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("✅ Enable", callback_data="evening_on"), InlineKeyboardButton("❌ Disable", callback_data="evening_off"))
    bot.reply_to(message, "🌇 *Evening Adkar Reminder*\n\nEnable daily evening adkar 30 mins after Asr?", reply_markup=markup)

@bot.message_handler(commands=["adkarbeforesleep"])
def adkar_sleep(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("✅ Enable", callback_data="sleep_on"), InlineKeyboardButton("❌ Disable", callback_data="sleep_off"))
    bot.reply_to(message, "😴 *Adkar Before Sleep*\n\nEnable nightly adkar 1 hour after Isha?", reply_markup=markup)

@bot.message_handler(commands=["allahuallah"])
def allahu_allah(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Every 2 hours", callback_data="allah_2h"), InlineKeyboardButton("Every 4 hours", callback_data="allah_4h"), InlineKeyboardButton("Every 6 hours", callback_data="allah_6h"))
    markup.row(InlineKeyboardButton("❌ Disable", callback_data="allah_off"))
    bot.reply_to(message, "💝 *Allahu Allah Dhikr Reminder*\n\nHow often would you like reminders?", reply_markup=markup)

@bot.message_handler(commands=["tasbih"])
def tasbih(message):
    bot.reply_to(message, "📿 *Tasbih Time*\n\n• *أَسْتَغْفِرُ ٱللَّٰهَ* (100×)\n• *ٱللَّٰهُ ٱللَّٰهُ*\n• *ٱللَّهُمَّ صَلِّ عَلَىٰ مُحَمَّدٍ ﷺ*\n\n﴿ أَلَا بِذِكْرِ ٱللَّٰهِ تَطْمَئِنُّ ٱلْقُلُوبُ ﴾\n_Verily, in the remembrance of Allah do hearts find rest._ (13:28)")

@bot.message_handler(commands=["tabung"])
def tabung(message):
    bot.reply_to(message, "💚 *ʿAmal Jāriyah – Ongoing Projects*\n\nSupport beneficial projects in:\n• Cambodia\n• Philippines\n• India\n• Bangladesh\n\nMay Allah multiply your rewards 🤲")

@bot.message_handler(commands=["feedback"])
def feedback(message):
    bot.reply_to(message, "📩 *We Value Your Feedback*\n\n🔗 Google Form: https://forms.gle/LMtXXfuKVbW6USor7\n📧 Email: rompeerbot@email.com\n\nJazakAllahu khair 🌹")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_settings.setdefault(user_id, {})
    
    if call.data == "remind_on":
        user_settings[user_id]['prayer_reminders'] = True
        schedule_prayer_reminders(user_id)
        bot.send_message(call.message.chat.id, "🔔 *Ṣalāh Reminders Enabled*\n\nYou will receive reminders:\n• 10 minutes before ṣalāh\n• At exact ṣalāh time\n\nMay Allah help us remain steadfast 🤍")
    elif call.data == "remind_off":
        user_settings[user_id]['prayer_reminders'] = False
        bot.send_message(call.message.chat.id, "❌ *Ṣalāh Reminders Disabled*")
    elif call.data == "morning_on":
        user_settings[user_id]['morning_adkar'] = True
        bot.send_message(call.message.chat.id, "🌅 *Morning Adkar Enabled*\n\nYou will receive morning adkar 15 mins after Fajr.")
    elif call.data == "morning_off":
        user_settings[user_id]['morning_adkar'] = False
        bot.send_message(call.message.chat.id, "❌ *Morning Adkar Disabled*")
    elif call.data == "evening_on":
        user_settings[user_id]['evening_adkar'] = True
        bot.send_message(call.message.chat.id, "🌇 *Evening Adkar Enabled*\n\nYou will receive evening adkar 30 mins after Asr.")
    elif call.data == "evening_off":
        user_settings[user_id]['evening_adkar'] = False
        bot.send_message(call.message.chat.id, "❌ *Evening Adkar Disabled*")
    elif call.data == "sleep_on":
        user_settings[user_id]['sleep_adkar'] = True
        bot.send_message(call.message.chat.id, "😴 *Adkar Before Sleep Enabled*\n\nYou will receive adkar 1 hour after Isha.")
    elif call.data == "sleep_off":
        user_settings[user_id]['sleep_adkar'] = False
        bot.send_message(call.message.chat.id, "❌ *Adkar Before Sleep Disabled*")
    elif call.data in ["allah_2h", "allah_4h", "allah_6h"]:
        interval = {"allah_2h": 2, "allah_4h": 4, "allah_6h": 6}[call.data]
        user_settings[user_id]['allahu_allah'] = interval
        schedule_allahu_allah(user_id, interval)
        bot.send_message(call.message.chat.id, f"💝 *Allahu Allah Dhikr Enabled*\n\nYou will receive reminders every {interval} hours.")
    elif call.data == "allah_off":
        user_settings[user_id]['allahu_allah'] = None
        schedule_allahu_allah(user_id, None)
        bot.send_message(call.message.chat.id, "❌ *Allahu Allah Dhikr Disabled*")

def send_morning_adkar():
    timings, _ = get_prayer_times(DEFAULT_CITY, DEFAULT_COUNTRY)
    sunrise_time = timings.get('Sunrise', 'N/A') if timings else 'N/A'
    text = (
        "🌅 *Morning Dhikr*\n\n"
        "الْحَمْدُ لِلَّهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا وَإِلَيْهِ النُّشُورُ\n"
        "_All praise is for Allah who gave us life after causing us to die, and unto Him is the resurrection._\n\n"
        "• Set your intention (Niyyah): seek closeness to Allah and purify your heart\n"
        "• To Complete Wirdu Amm of the following below:\n"
        "  - 100 Istighfar\n"
        "  - 500 Salawat upon the Prophet ﷺ\n"
        "  - 125 La Ilaha Illallah\n"
        "• Upon reciting Wirdu Amm, Recite Surah Yaseen or Quran with tafsir: min. 1 page\n"
        f"• Remember to pray Solat Ishraq prayers 15-20mins after Syuruk (Today's Syuruk is at: {sunrise_time})\n"
        "• To recite Awrad Zuhooriyah: https://tinyurl.com/awradzuhooriyah\n"
        "• Morning supplication for divine help:\n"
        "  *Allahumma inni ala zikrika wa shukrika wa husni ibadatika*\n"
        "  _(O Allah, help me to remember You, to be grateful to You, and to worship You in an excellent manner)_"
    )
    for user_id, settings in user_settings.items():
        if settings.get('morning_adkar'):
            try:
                bot.send_message(user_id, text)
            except Exception as e:
                logger.error(f"Error sending morning adkar to {user_id}: {e}")

def send_evening_adkar():
    text = (
        "🌇 *Evening Adkar Dhikr*\n\n"
        "• Try to perform prayers in congregation\n"
        "• Surah Al-Waqi'ah recitation\n"
        "• Recite Hizbul Bahr\n"
        "• Perform 1 set of Wird (Istighfar, Tahlil, Salawat, Muraqabah) 10–100x\n"
        "• Evening charity reminder\n"
        "• Reflection: pause and feel Allah's presence for 1–2 minutes\n"
        "• Reminder to finish Wirdu Amm"
    )
    for user_id, settings in user_settings.items():
        if settings.get('evening_adkar'):
            try:
                bot.send_message(user_id, text)
            except Exception as e:
                logger.error(f"Error sending evening adkar to {user_id}: {e}")

def send_sleep_adkar():
    text = (
        "😴 *Before Sleep*\n\n"
        "• Perform Istighfar, Tahlil, Salawat, Muraqabah: 10–100x\n"
        "• Reflect on death (Mawt) and your deeds\n"
        "• Forgive anyone you hold grudges against\n"
        "• Mindfulness cue: feel gratitude and presence of Allah\n"
        "• Perform Solat Sunnah Taubah and recite Surah As-Sajdah & Surah Mulk\n"
        "• Dua: ask Allah for protection, forgiveness, and peaceful rest\n"
        "• Sleep with good intentions to gain strength to worship and seek Allah's pleasure\n"
        "• Continuous Dhikr — every breath can be remembrance of Allah"
    )
    for user_id, settings in user_settings.items():
        if settings.get('sleep_adkar'):
            try:
                bot.send_message(user_id, text)
            except Exception as e:
                logger.error(f"Error sending sleep adkar to {user_id}: {e}")

def send_allahu_allah_to_user(user_id):
    text = (
        "💝 *Allahu Allah Reminder*\n\n"
        "Continuous Dhikr — every breath can be remembrance of Allah:\n"
        "• Breathe *Allahu Allah* silently and connect your breath to Allah\n"
        "• Ask Allah for help in maintaining this Dhikr and staying mindful throughout the day\n"
        "• Renew your intention (Niyyah) with every pause and breath\n"
        "• Take a deep breath, feel gratitude for Allah's blessings\n"
        "• Optional: Add a short personal dua from your heart\n"
        "• Let this Dhikr inspire patience, sincerity, and mindfulness in all actions"
    )
    try:
        bot.send_message(user_id, text)
    except Exception as e:
        logger.error(f"Error sending Allahu Allah reminder to {user_id}: {e}")

def schedule_allahu_allah(user_id, interval_hours):
    # Remove existing job if any
    try:
        scheduler.remove_job(f"allahu_allah_{user_id}")
    except:
        pass
    
    if interval_hours:
        scheduler.add_job(
            func=lambda: send_allahu_allah_to_user(user_id),
            trigger='interval',
            hours=interval_hours,
            id=f"allahu_allah_{user_id}",
            replace_existing=True
        )
        logger.info(f"Scheduled Allahu Allah reminder for user {user_id} every {interval_hours} hours")

def schedule_daily_reminders():
    timings, _ = get_prayer_times(DEFAULT_CITY, DEFAULT_COUNTRY)
    if timings:
        fajr_time = datetime.strptime(timings['Fajr'], "%H:%M")
        asr_time = datetime.strptime(timings['Asr'], "%H:%M")
        isha_time = datetime.strptime(timings['Isha'], "%H:%M")
        
        # Morning adkar: 15 mins after Fajr
        morning_hour = fajr_time.hour
        morning_minute = (fajr_time.minute + 15) % 60
        if fajr_time.minute + 15 >= 60:
            morning_hour = (morning_hour + 1) % 24
        
        # Evening adkar: 30 mins after Asr
        evening_hour = asr_time.hour
        evening_minute = (asr_time.minute + 30) % 60
        if asr_time.minute + 30 >= 60:
            evening_hour = (evening_hour + 1) % 24
        
        # Sleep adkar: 1 hour after Isha
        sleep_hour = (isha_time.hour + 1) % 24
        sleep_minute = isha_time.minute
        
        scheduler.add_job(
            send_morning_adkar, 'cron',
            hour=morning_hour, minute=morning_minute,
            id="morning_adkar_daily", replace_existing=True
        )
        scheduler.add_job(
            send_evening_adkar, 'cron',
            hour=evening_hour, minute=evening_minute,
            id="evening_adkar_daily", replace_existing=True
        )
        scheduler.add_job(
            send_sleep_adkar, 'cron',
            hour=sleep_hour, minute=sleep_minute,
            id="sleep_adkar_daily", replace_existing=True
        )
        
        logger.info(f"Scheduled daily reminders - Morning: {morning_hour:02d}:{morning_minute:02d}, Evening: {evening_hour:02d}:{evening_minute:02d}, Sleep: {sleep_hour:02d}:{sleep_minute:02d}")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "❓ I didn't understand that.\n\nPlease use /help to see available commands.")

if __name__ == "__main__":
    try:
        scheduler.start()
        schedule_daily_reminders()
        logger.info("🤖 ROM PeerBot is starting...")
        bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise
