"""Start and help command handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, UserSettings

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start", "help"))
async def cmd_start(message: Message, session: AsyncSession):
    """Handle /start and /help commands"""
    user_id = message.from_user.id
    
    # Create or update user in database
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
            
            # Create default settings
            settings = UserSettings(user_id=user_id)
            session.add(settings)
            
            await session.commit()
            logger.info(f"New user registered: {user_id}")
        else:
            # Update user info if changed
            user.username = message.from_user.username
            user.first_name = message.from_user.first_name
            user.last_name = message.from_user.last_name
            await session.commit()
    except Exception as e:
        logger.error(f"Error creating/updating user {user_id}: {e}")
        await session.rollback()
    
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
        "• /setlocation — Set your city for prayer times\n"
        "• /praywhere — Find nearby masājid\n"
        "• /remind — Enable ṣalāh reminders\n"
        "• /unremind — Disable ṣalāh reminders\n"
        "• /tasbih — Dhikr & remembrance\n"
        "• /amaljariah — Support ʿAmal Jāriyah\n"
        "• /feedback — Share feedback\n\n"
        "You can also use the *Menu* button below ⬇️\n\n"
        "May Allah place barakah in our intentions 🌙"
    )
    
    await message.answer(text, parse_mode="Markdown")
