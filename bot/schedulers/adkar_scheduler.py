"""Adkar scheduler for morning, evening, sleep, and Allahu Allah reminders"""

import logging
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from sqlalchemy import select
import database.db
from database.models import UserSettings
from bot.utils.prayer_api import get_prayer_times
from config import DEFAULT_CITY, DEFAULT_COUNTRY

SINGAPORE_TZ = pytz.timezone('Asia/Singapore')

logger = logging.getLogger(__name__)


async def send_morning_adkar(bot: Bot, user_id: int):
    """Send morning adkar reminder"""
    try:
        timings, _ = await get_prayer_times(DEFAULT_CITY, DEFAULT_COUNTRY)
        sunrise_time = timings.get('Sunrise', 'N/A') if timings else 'N/A'
        
        text = (
            "🌅 *Morning Dhikr & Daily Adhkar*\n\n"
            "🤲 *Dua Upon Waking Up*\n\n"
            "الْحَمْدُ لِلَّهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا وَإِلَيْهِ النُّشُورُ\n"
            "_All praise is for Allah who gave us life after causing us to die, and unto Him is the resurrection._\n"
            "_Al-hamdu lillahi alladhi ahyana ba'da ma amatana wa ilayhin-nushoor_\n\n"
            "📋 *Daily Checklist:*\n"
            "🤍 *Niyyah:* Seek closeness to Allah & purify the heart.\n"
            "📿 *Wirdu Amm:*\n"
            "  • 100x Istighfar\n"
            "  • 500x Salawat upon the Prophet ﷺ\n"
            "  • 125x La Ilaha Illallah\n"
            "📖 *Quran:* Surah Yaseen OR min. 1 page Tafsir.\n"
            f"🕌 *Ishraq:* Pray 15-20mins after Syuruk (Today: {sunrise_time})\n"
            "🔗 *Awrad Zuhooriyah:* https://tinyurl.com/awradzuhooriyah\n\n"
            "📿 *After Every Fard Prayer*\n"
            "اللَّهُمَّ أَعِنِّي عَلَى ذِكْرِكَ، وَشُكْرِكَ، وَحُسْنِ عِبَادَتِكَ\n"
            "_Allahumma a'inni 'ala dhikrika, wa shukrika, wa husni 'ibadatika_\n"
            "_(O Allah, help me to remember You, to be grateful to You, and to worship You in an excellent manner)_"
        )
        
        await bot.send_message(user_id, text, parse_mode="Markdown")
        logger.info(f"Sent morning adkar to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending morning adkar to {user_id}: {e}")


async def send_evening_adkar(bot: Bot, user_id: int):
    """Send evening adkar reminder"""
    try:
        text = (
            "🌇 *Evening Dhikr*\n\n"
            "📿 *Adhkar:* Istighfar, Tahlil, Salawat, Muraqabah (10–100x)\n"
            "🕯️ *Muhasabah:* Reflect on your day and your deeds.\n"
            "🤍 *Forgiveness:* Forgive anyone you hold grudges against.\n"
            "🍃 *Mindfulness:* Feel gratitude & the presence of Allah.\n"
            "🕌 *Worship:* Engage in dhikr and remembrance\n\n"
            "📖 *Evening Adhkar:*\n"
            "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ\n"
            "_We have entered the evening and with it all the dominion is Allah's_\n"
            "_Amsayna wa amsal-mulku lillah_\n\n"
            "الْحَمْدُ لِلَّهِ الَّذِي عَافَانِي فِي جَسَدِي\n"
            "_All praise is for Allah who has restored to me my health_\n"
            "_Alhamdu lillahil-lazi 'afani fi jasadi_\n\n"
            "🌬️ *Continuous Dhikr:* Make every breath a remembrance of Allah with Allahu Allah."
        )
        
        await bot.send_message(user_id, text, parse_mode="Markdown")
        logger.info(f"Sent evening adkar to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending evening adkar to {user_id}: {e}")


async def send_sleep_adkar(bot: Bot, user_id: int):
    """Send sleep adkar reminder"""
    try:
        text = (
            "😴 *Before Sleep*\n\n"
            "📿 *Adhkar:* Istighfar, Tahlil, Salawat, Muraqabah (10–100x)\n"
            "🕯️ *Muhasabah:* Reflect on death (Mawt) & your deeds.\n"
            "🤍 *Forgiveness:* Forgive anyone you hold grudges against.\n"
            "🍃 *Mindfulness:* Feel gratitude & the presence of Allah.\n"
            "🕌 *Worship:* Solat Sunnah Taubah + Surah As-Sajdah & Al-Mulk.\n"
            "🤲 *Dua before sleeping:*\n"
            "اللهم باسمك أموت وأحيا\n"
            "_O Allah, with Your Name will I die and live (wake up)_\n"
            "_Allahumma bismika amutu wa ahya_\n\n"
            "Recite Last three verse of Surah Baqarah before sleeping.\n\n"
            "🌙 *Niyyah:* Sleep with many good intentions of what you want to perform the next day.\n"
            "🌬️ *Continuous Dhikr:* Make every breath a remembrance of Allah. Sleep with Allahu Allah."
        )
        
        await bot.send_message(user_id, text, parse_mode="Markdown")
        logger.info(f"Sent sleep adkar to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending sleep adkar to {user_id}: {e}")


async def send_allahu_allah(bot: Bot, user_id: int):
    """Send Allahu Allah dhikr reminder"""
    try:
        text = (
            "💝 *Allahu Allah (Dhikr Anfus) Reminder*\n\n"
            "Continuous Dhikr — every breath can be remembrance of Allah:\n"
            "• Breathe Allahu Allah silently and connect your breath to Allah\n"
            "  To be in a state of gratitude for Allah for his providence of each breath\n"
            "  And for one to recognise the neediness in each one is in every moment.\n\n"
            "_From Allah, By Allah, With Allah, For Allah, Back to Allah._\n\n"
            "• Ask Allah for help in maintaining this Dhikr and staying mindful throughout the day\n"
            "• To also sleep with Allahu Allah"
        )
        
        await bot.send_message(user_id, text, parse_mode="Markdown")
        logger.info(f"Sent Allahu Allah reminder to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending Allahu Allah reminder to {user_id}: {e}")


async def schedule_adkar_for_user(scheduler: AsyncIOScheduler, bot: Bot, user_id: int, settings: UserSettings):
    """Schedule adkar reminders for a specific user"""
    # Remove existing jobs for this user first
    for job_id in [f"morning_adkar_{user_id}", f"evening_adkar_{user_id}", 
                   f"sleep_adkar_{user_id}", f"allahu_allah_{user_id}"]:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
    
    # Get prayer times to calculate adkar timings
    timings, _ = await get_prayer_times(DEFAULT_CITY, DEFAULT_COUNTRY)
    if not timings:
        logger.error(f"Could not fetch prayer times for user {user_id}")
        return
    
    # Morning adkar: 15 mins after Fajr (Subuh azan)
    if settings.morning_adkar:
        try:
            fajr_time = datetime.strptime(timings['Fajr'], "%H:%M")
            # Add 15 minutes
            morning_time = fajr_time + timedelta(minutes=15)
            morning_hour = morning_time.hour
            morning_minute = morning_time.minute
            
            scheduler.add_job(
                send_morning_adkar,
                trigger=CronTrigger(hour=morning_hour, minute=morning_minute, timezone="Asia/Singapore"),
                args=[bot, user_id],
                id=f"morning_adkar_{user_id}",
                replace_existing=True
            )
            logger.info(f"Scheduled morning adkar for user {user_id} at {morning_hour:02d}:{morning_minute:02d} (Fajr: {timings['Fajr']})")
        except Exception as e:
            logger.error(f"Error scheduling morning adkar for user {user_id}: {e}")
    
    # Evening adkar: 30 mins after Asr
    if settings.evening_adkar:
        try:
            asr_time = datetime.strptime(timings['Asr'], "%H:%M")
            # Add 30 minutes
            evening_time = asr_time + timedelta(minutes=30)
            evening_hour = evening_time.hour
            evening_minute = evening_time.minute
            
            scheduler.add_job(
                send_evening_adkar,
                trigger=CronTrigger(hour=evening_hour, minute=evening_minute, timezone="Asia/Singapore"),
                args=[bot, user_id],
                id=f"evening_adkar_{user_id}",
                replace_existing=True
            )
            logger.info(f"Scheduled evening adkar for user {user_id} at {evening_hour:02d}:{evening_minute:02d} (Asr: {timings['Asr']})")
        except Exception as e:
            logger.error(f"Error scheduling evening adkar for user {user_id}: {e}")
    
    # Sleep adkar: 1 hour after Isha
    if settings.sleep_adkar:
        try:
            isha_time = datetime.strptime(timings['Isha'], "%H:%M")
            # Add 1 hour
            sleep_time = isha_time + timedelta(hours=1)
            sleep_hour = sleep_time.hour
            sleep_minute = sleep_time.minute
            
            scheduler.add_job(
                send_sleep_adkar,
                trigger=CronTrigger(hour=sleep_hour, minute=sleep_minute, timezone="Asia/Singapore"),
                args=[bot, user_id],
                id=f"sleep_adkar_{user_id}",
                replace_existing=True
            )
            logger.info(f"Scheduled sleep adkar for user {user_id} at {sleep_hour:02d}:{sleep_minute:02d} (Isha: {timings['Isha']})")
        except Exception as e:
            logger.error(f"Error scheduling sleep adkar for user {user_id}: {e}")
    
    # Allahu Allah dhikr: interval-based (start immediately when enabled)
    if settings.allahu_allah_interval:
        try:
            # Send immediately when enabled
            await send_allahu_allah(bot, user_id)
            # Then schedule recurring
            scheduler.add_job(
                send_allahu_allah,
                trigger=IntervalTrigger(hours=settings.allahu_allah_interval, timezone="Asia/Singapore"),
                args=[bot, user_id],
                id=f"allahu_allah_{user_id}",
                replace_existing=True
            )
            logger.info(f"Scheduled Allahu Allah for user {user_id} every {settings.allahu_allah_interval} hours")
        except Exception as e:
            logger.error(f"Error scheduling Allahu Allah for user {user_id}: {e}")


async def schedule_all_adkar(scheduler: AsyncIOScheduler, bot: Bot):
    """Schedule adkar reminders for all users"""
    try:
        if not database.db.async_session_maker:
            logger.warning("Database session maker not initialized yet")
            return
        async with database.db.async_session_maker() as session:
            result = await session.execute(select(UserSettings))
            all_settings = result.scalars().all()
            
            for settings in all_settings:
                if any([settings.morning_adkar, settings.evening_adkar, 
                       settings.sleep_adkar, settings.allahu_allah_interval]):
                    await schedule_adkar_for_user(scheduler, bot, settings.user_id, settings)
            
            logger.info(f"Scheduled adkar for {len(all_settings)} users")
    except Exception as e:
        logger.error(f"Error scheduling adkar: {e}")


def setup_adkar_scheduler(scheduler: AsyncIOScheduler, bot: Bot):
    """Setup daily adkar reminder scheduling"""
    # Refresh adkar schedules daily at midnight Singapore time (prayer times change daily)
    scheduler.add_job(
        schedule_all_adkar,
        'cron',
        hour=0,
        minute=1,
        timezone="Asia/Singapore",
        args=[scheduler, bot],
        id='daily_adkar_refresh',
        replace_existing=True
    )
    logger.info("Adkar scheduler setup complete - daily refresh at 00:01 SGT")
