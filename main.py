"""
ROM PeerBot - Your Personal Islamic Companion
Main entry point with aiogram
"""

import sys
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import API_TOKEN, LOG_LEVEL
from database import init_db, close_db
from bot.handlers import start, prayer, adkar, misc
from bot.schedulers.prayer_scheduler import setup_prayer_scheduler, schedule_all_prayer_reminders
from bot.schedulers.adkar_scheduler import setup_adkar_scheduler, schedule_all_adkar
from bot.schedulers.khutbah_scheduler import setup_khutbah_scheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, scheduler: AsyncIOScheduler):
    """Actions to perform on bot startup"""
    logger.info("Initializing ROM PeerBot...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Setup bot commands menu
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help message"),
        BotCommand(command="prayertimes", description="Get prayer times"),
        BotCommand(command="setlocation", description="Set your city for prayer times"),
        BotCommand(command="praywhere", description="Find nearby mosques"),
        BotCommand(command="remind", description="Toggle prayer reminders"),
        BotCommand(command="morningadkar", description="Configure morning adkar"),
        BotCommand(command="eveningadkar", description="Configure evening adkar"),
        BotCommand(command="adkarbeforesleep", description="Configure sleep adkar"),
        BotCommand(command="allahuallah", description="Configure Allahu Allah reminders"),
        BotCommand(command="tasbih", description="Get tasbih reminder"),
        BotCommand(command="amaljariah", description="Support the project"),
        BotCommand(command="mydonations", description="Manage recurring donations"),
        BotCommand(command="resources", description="Access Islamic resources"),
        BotCommand(command="feedback", description="Send feedback"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands menu configured")
    
    # Setup schedulers
    setup_prayer_scheduler(scheduler, bot)
    setup_adkar_scheduler(scheduler, bot)
    setup_khutbah_scheduler(scheduler, bot)
    
    # Schedule initial reminders
    await schedule_all_prayer_reminders(scheduler, bot)
    await schedule_all_adkar(scheduler, bot)
    
    logger.info("✅ ROM PeerBot is ready!")


async def on_shutdown():
    """Actions to perform on bot shutdown"""
    logger.info("Shutting down ROM PeerBot...")
    await close_db()
    logger.info("ROM PeerBot stopped")


async def main():
    """Main bot function"""
    # Initialize bot with default properties
    bot = Bot(
        token=API_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Initialize dispatcher with memory storage
    dp = Dispatcher(storage=MemoryStorage())
    
    # Initialize scheduler
    scheduler = AsyncIOScheduler(timezone="Asia/Singapore")
    
    # Set scheduler reference in adkar handler for immediate rescheduling
    from bot.handlers.adkar import set_scheduler
    set_scheduler(scheduler)
    
    # Register handlers
    dp.include_router(start.router)
    dp.include_router(prayer.router)
    dp.include_router(adkar.router)
    dp.include_router(misc.router)
    
    # Middleware to inject session into handlers
    from sqlalchemy.ext.asyncio import AsyncSession
    import database.db
    
    @dp.update.middleware()
    async def db_session_middleware(handler, event, data):
        async with database.db.async_session_maker() as session:
            data['session'] = session
            return await handler(event, data)
    
    try:
        # Start scheduler
        scheduler.start()
        logger.info("Scheduler started")
        
        # Run startup actions
        await on_startup(bot, scheduler)
        
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            handle_signals=True
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        scheduler.shutdown()
        await on_shutdown()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting...")
