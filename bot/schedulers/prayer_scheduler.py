"""Prayer time scheduler"""

import logging
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot
from sqlalchemy import select
import database.db
from database.models import UserSettings
from bot.utils.prayer_api import get_prayer_times
from config import DEFAULT_CITY, DEFAULT_COUNTRY

SINGAPORE_TZ = pytz.timezone('Asia/Singapore')

logger = logging.getLogger(__name__)


async def send_prayer_reminder(bot: Bot, user_id: int, prayer: str, status: str):
    """Send prayer reminder to user"""
    try:
        if status == "10 minutes":
            text = f"🔔 {prayer} prayer in 10 minutes"
        else:
            text = f"🕌 {prayer} prayer time has entered"
        
        await bot.send_message(user_id, text)
        logger.info(f"Sent {prayer} reminder ({status}) to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending prayer reminder to {user_id}: {e}")


async def schedule_user_prayer_reminders(scheduler: AsyncIOScheduler, bot: Bot, user_id: int):
    """Schedule prayer reminders for a specific user"""
    timings, _ = await get_prayer_times(DEFAULT_CITY, DEFAULT_COUNTRY)
    if not timings:
        logger.error(f"Could not fetch prayer times for user {user_id}")
        return
    
    now = datetime.now(SINGAPORE_TZ)
    
    for prayer in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
        time_str = timings[prayer]
        prayer_time = SINGAPORE_TZ.localize(datetime.strptime(time_str, "%H:%M").replace(
            year=now.year,
            month=now.month,
            day=now.day
        ))
        
        # If prayer time has passed, schedule for tomorrow
        if prayer_time < now:
            prayer_time += timedelta(days=1)
        
        # Schedule 10-minute reminder
        reminder_time = prayer_time - timedelta(minutes=10)
        if reminder_time > now:
            scheduler.add_job(
                send_prayer_reminder,
                trigger=DateTrigger(run_date=reminder_time),
                args=[bot, user_id, prayer, "10 minutes"],
                id=f"prayer_reminder_{user_id}_{prayer}_10min",
                replace_existing=True
            )
        
        # Schedule prayer time notification
        scheduler.add_job(
            send_prayer_reminder,
            trigger=DateTrigger(run_date=prayer_time),
            args=[bot, user_id, prayer, "entered"],
            id=f"prayer_time_{user_id}_{prayer}",
            replace_existing=True
        )
    
    logger.info(f"Scheduled prayer reminders for user {user_id}")


async def schedule_all_prayer_reminders(scheduler: AsyncIOScheduler, bot: Bot):
    """Schedule prayer reminders for all users with prayer_reminders enabled"""
    try:
        if not database.db.async_session_maker:
            logger.warning("Database session maker not initialized yet")
            return
        async with database.db.async_session_maker() as session:
            result = await session.execute(
                select(UserSettings).where(UserSettings.prayer_reminders == True)
            )
            users = result.scalars().all()
            
            for settings in users:
                await schedule_user_prayer_reminders(scheduler, bot, settings.user_id)
            
            logger.info(f"Scheduled prayer reminders for {len(users)} users")
    except Exception as e:
        logger.error(f"Error scheduling prayer reminders: {e}")


def setup_prayer_scheduler(scheduler: AsyncIOScheduler, bot: Bot):
    """Setup daily prayer reminder scheduling"""
    # Schedule prayer reminders to be refreshed daily at midnight Singapore time
    scheduler.add_job(
        schedule_all_prayer_reminders,
        'cron',
        hour=0,
        minute=0,
        timezone="Asia/Singapore",
        args=[scheduler, bot],
        id='daily_prayer_refresh',
        replace_existing=True
    )
    logger.info("Prayer scheduler setup complete - daily refresh at 00:00 SGT")
