"""Adkar-related command handlers"""

import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import UserSettings
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)
router = Router()

# Global scheduler reference (will be set during initialization)
_scheduler: AsyncIOScheduler = None

def set_scheduler(scheduler: AsyncIOScheduler):
    """Set the scheduler reference for use in handlers"""
    global _scheduler
    _scheduler = scheduler


@router.message(Command("morningadkar"))
async def cmd_morning_adkar(message: Message):
    """Handle /morningadkar command"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Enable", callback_data="morning_on"),
            InlineKeyboardButton(text="❌ Disable", callback_data="morning_off")
        ]
    ])
    
    await message.answer(
        "🌅 *Morning Adkar Reminder*\n\nEnable daily morning adkar 15 mins after Fajr?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(Command("eveningadkar"))
async def cmd_evening_adkar(message: Message):
    """Handle /eveningadkar command"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Enable", callback_data="evening_on"),
            InlineKeyboardButton(text="❌ Disable", callback_data="evening_off")
        ]
    ])
    
    await message.answer(
        "🌇 *Evening Adkar Reminder*\n\nEnable daily evening adkar 30 mins after Asr?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(Command("adkarbeforesleep"))
async def cmd_adkar_sleep(message: Message):
    """Handle /adkarbeforesleep command"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Enable", callback_data="sleep_on"),
            InlineKeyboardButton(text="❌ Disable", callback_data="sleep_off")
        ]
    ])
    
    await message.answer(
        "😴 *Adkar Before Sleep*\n\nEnable nightly adkar 1 hour after Isha?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(Command("allahuallah"))
async def cmd_allahu_allah(message: Message):
    """Handle /allahuallah command"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Every 2 hours", callback_data="allah_2h"),
            InlineKeyboardButton(text="Every 4 hours", callback_data="allah_4h"),
            InlineKeyboardButton(text="Every 6 hours", callback_data="allah_6h")
        ],
        [
            InlineKeyboardButton(text="❌ Disable", callback_data="allah_off")
        ]
    ])
    
    await message.answer(
        "💝 *Allahu Allah Dhikr Reminder*\n\nHow often would you like reminders?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.in_(["morning_on", "morning_off"]))
async def callback_morning_adkar(callback: CallbackQuery, session: AsyncSession):
    """Handle morning adkar callbacks"""
    user_id = callback.from_user.id
    enable = callback.data == "morning_on"
    bot: Bot = callback.bot
    
    try:
        result = await session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = UserSettings(user_id=user_id)
            session.add(settings)
        
        settings.morning_adkar = enable
        await session.commit()
        
        # Reschedule immediately
        if _scheduler:
            from bot.schedulers.adkar_scheduler import schedule_adkar_for_user
            await schedule_adkar_for_user(_scheduler, bot, user_id, settings)
        
        if enable:
            logger.info(f"Morning adkar enabled for user {user_id}")
            text = "🌅 *Morning Adkar Enabled*\n\nYou will receive morning adkar 15 mins after Subuh azan (Fajr time)."
        else:
            logger.info(f"Morning adkar disabled for user {user_id}")
            text = "❌ *Morning Adkar Disabled*"
        
        await callback.message.answer(text, parse_mode="Markdown")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error handling morning adkar callback for {user_id}: {e}")
        await session.rollback()
        await callback.answer("An error occurred. Please try again.", show_alert=True)


@router.callback_query(F.data.in_(["evening_on", "evening_off"]))
async def callback_evening_adkar(callback: CallbackQuery, session: AsyncSession):
    """Handle evening adkar callbacks"""
    user_id = callback.from_user.id
    enable = callback.data == "evening_on"
    bot: Bot = callback.bot
    
    try:
        result = await session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = UserSettings(user_id=user_id)
            session.add(settings)
        
        settings.evening_adkar = enable
        await session.commit()
        
        # Reschedule immediately
        if _scheduler:
            from bot.schedulers.adkar_scheduler import schedule_adkar_for_user
            await schedule_adkar_for_user(_scheduler, bot, user_id, settings)
        
        if enable:
            logger.info(f"Evening adkar enabled for user {user_id}")
            text = "🌇 *Evening Adkar Enabled*\n\nYou will receive evening adkar 30 mins after Asr."
        else:
            logger.info(f"Evening adkar disabled for user {user_id}")
            text = "❌ *Evening Adkar Disabled*"
        
        await callback.message.answer(text, parse_mode="Markdown")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error handling evening adkar callback for {user_id}: {e}")
        await session.rollback()
        await callback.answer("An error occurred. Please try again.", show_alert=True)


@router.callback_query(F.data.in_(["sleep_on", "sleep_off"]))
async def callback_sleep_adkar(callback: CallbackQuery, session: AsyncSession):
    """Handle sleep adkar callbacks"""
    user_id = callback.from_user.id
    enable = callback.data == "sleep_on"
    bot: Bot = callback.bot
    
    try:
        result = await session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = UserSettings(user_id=user_id)
            session.add(settings)
        
        settings.sleep_adkar = enable
        await session.commit()
        
        # Reschedule immediately
        if _scheduler:
            from bot.schedulers.adkar_scheduler import schedule_adkar_for_user
            await schedule_adkar_for_user(_scheduler, bot, user_id, settings)
        
        if enable:
            logger.info(f"Sleep adkar enabled for user {user_id}")
            text = "😴 *Adkar Before Sleep Enabled*\n\nYou will receive adkar 1 hour after Isha."
        else:
            logger.info(f"Sleep adkar disabled for user {user_id}")
            text = "❌ *Adkar Before Sleep Disabled*"
        
        await callback.message.answer(text, parse_mode="Markdown")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error handling sleep adkar callback for {user_id}: {e}")
        await session.rollback()
        await callback.answer("An error occurred. Please try again.", show_alert=True)


@router.callback_query(F.data.in_(["allah_2h", "allah_4h", "allah_6h", "allah_off"]))
async def callback_allahu_allah(callback: CallbackQuery, session: AsyncSession):
    """Handle Allahu Allah dhikr callbacks"""
    user_id = callback.from_user.id
    bot: Bot = callback.bot
    
    interval_map = {
        "allah_2h": 2,
        "allah_4h": 4,
        "allah_6h": 6,
        "allah_off": None
    }
    interval = interval_map[callback.data]
    
    try:
        result = await session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = UserSettings(user_id=user_id)
            session.add(settings)
        
        settings.allahu_allah_interval = interval
        await session.commit()
        
        # Reschedule immediately (this will also send immediate message if enabled)
        if _scheduler:
            from bot.schedulers.adkar_scheduler import schedule_adkar_for_user
            await schedule_adkar_for_user(_scheduler, bot, user_id, settings)
        
        if interval:
            logger.info(f"Allahu Allah dhikr enabled for user {user_id} - every {interval} hours")
            text = f"💝 *Allahu Allah Dhikr Enabled*\n\nYou have received your first reminder. You will continue to receive reminders every {interval} hours."
        else:
            logger.info(f"Allahu Allah dhikr disabled for user {user_id}")
            text = "❌ *Allahu Allah Dhikr Disabled*"
        
        await callback.message.answer(text, parse_mode="Markdown")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error handling Allahu Allah callback for {user_id}: {e}")
        await session.rollback()
        await callback.answer("An error occurred. Please try again.", show_alert=True)
