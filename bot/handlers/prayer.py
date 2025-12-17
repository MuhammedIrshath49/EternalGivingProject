"""Prayer-related command handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Location
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import UserSettings
from bot.utils.prayer_api import get_prayer_times
from bot.utils.mosque_finder import find_nearby_mosques
from config import DEFAULT_CITY, DEFAULT_COUNTRY

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("prayertimes"))
async def cmd_prayer_times(message: Message, session: AsyncSession):
    """Handle /prayertimes command"""
    user_id = message.from_user.id
    
    # Get user's city/country settings
    result = await session.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()
    
    city = settings.city if settings else DEFAULT_CITY
    country = settings.country if settings else DEFAULT_COUNTRY
    
    timings, date = await get_prayer_times(city, country)
    
    if not timings:
        await message.answer("❌ Unable to fetch ṣalāh times right now. Please try again later.", parse_mode="Markdown")
        return
    
    text = (
        f"🕋 *Ṣalāh Times Today ({city})*\n"
        f"{date}\n\n"
        f"🌅 Fajr: {timings['Fajr']}\n"
        f"🌄 Sunrise: {timings['Sunrise']}\n"
        f"☀️ Dhuhr: {timings['Dhuhr']}\n"
        f"🌤 Asr: {timings['Asr']}\n"
        f"🌇 Maghrib: {timings['Maghrib']}\n"
        f"🌙 Isha: {timings['Isha']}\n\n"
        "May Allah accept our ṣalāh 🤲"
    )
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("praywhere"))
async def cmd_pray_where(message: Message):
    """Handle /praywhere command"""
    text = (
        "📍 *Find Nearby Masājid & Musollahs*\n\n"
        "Please share your location using Telegram's 📎 attachment button:\n"
        "➡️ Attach → Location\n\n"
        "💡 *Tip:* Your location will also be saved for accurate prayer times!\n\n"
        "إِنْ شَاءَ ٱللَّٰهُ, I'll help you find a place to pray."
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("setlocation"))
async def cmd_set_location(message: Message, session: AsyncSession):
    """Handle /setlocation command to manually set city"""
    # Extract city from command (e.g., /setlocation London, UK)
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "📍 *Set Your Location*\n\n"
            "To set your location for accurate prayer times, use:\n"
            "`/setlocation City, Country`\n\n"
            "*Examples:*\n"
            "• `/setlocation Singapore, Singapore`\n"
            "• `/setlocation London, United Kingdom`\n"
            "• `/setlocation Dubai, UAE`\n"
            "• `/setlocation New York, USA`",
            parse_mode="Markdown"
        )
        return
    
    # Parse city and country
    location_parts = args[1].split(',')
    city = location_parts[0].strip()
    country = location_parts[1].strip() if len(location_parts) > 1 else city
    
    user_id = message.from_user.id
    
    try:
        # Update user settings
        result = await session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = UserSettings(user_id=user_id)
            session.add(settings)
        
        settings.city = city
        settings.country = country
        await session.commit()
        
        logger.info(f"Location updated for user {user_id}: {city}, {country}")
        
        # Fetch and show prayer times for the new location
        timings, date = await get_prayer_times(city, country)
        
        if timings:
            text = (
                f"✅ *Location Updated!*\n\n"
                f"🕋 *Ṣalāh Times for {city}, {country}*\n"
                f"{date}\n\n"
                f"🌅 Fajr: {timings['Fajr']}\n"
                f"🌄 Sunrise: {timings['Sunrise']}\n"
                f"☀️ Dhuhr: {timings['Dhuhr']}\n"
                f"🌤 Asr: {timings['Asr']}\n"
                f"🌇 Maghrib: {timings['Maghrib']}\n"
                f"🌙 Isha: {timings['Isha']}\n\n"
                f"May Allah accept our ṣalāh 🤲"
            )
        else:
            text = (
                f"✅ *Location set to {city}, {country}*\n\n"
                f"⚠️ Could not fetch prayer times. Please verify the location is correct."
            )
        
        await message.answer(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error setting location for {user_id}: {e}")
        await session.rollback()
        await message.answer("❌ Error updating location. Please try again.", parse_mode="Markdown")


@router.message(F.content_type == "location")
async def handle_location(message: Message, session: AsyncSession):
    """Handle location sharing - auto-save location and find mosques"""
    latitude = message.location.latitude
    longitude = message.location.longitude
    user_id = message.from_user.id
    
    # Use reverse geocoding to get city/country from coordinates
    import aiohttp
    city, country = None, None
    
    try:
        nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "json",
            "lat": latitude,
            "lon": longitude,
            "zoom": 10,
            "addressdetails": 1
        }
        headers = {"User-Agent": "ROM_PeerBot/2.0"}
        
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(nominatim_url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    address = data.get('address', {})
                    
                    # Try to get city from various fields
                    city = (address.get('city') or 
                           address.get('town') or 
                           address.get('village') or 
                           address.get('state') or 
                           None)
                    country = address.get('country', None)
                    
                    if city and country:
                        # Update user settings with location
                        result = await session.execute(
                            select(UserSettings).where(UserSettings.user_id == user_id)
                        )
                        settings = result.scalar_one_or_none()
                        
                        if not settings:
                            settings = UserSettings(user_id=user_id)
                            session.add(settings)
                        
                        settings.city = city
                        settings.country = country
                        await session.commit()
                        
                        logger.info(f"Location auto-saved for user {user_id}: {city}, {country}")
                        
                        await message.answer(
                            f"📍 *Location Saved*\n{city}, {country}\n\nSearching for nearby masājid...",
                            parse_mode="Markdown"
                        )
    except Exception as e:
        logger.error(f"Reverse geocoding error: {e}")
    
    # Find nearby mosques
    if not city:
        await message.answer("🕌 *Searching for Nearby Masājid*\n\nPlease wait...", parse_mode="Markdown")
    
    mosques = await find_nearby_mosques(latitude, longitude)
    
    if not mosques:
        await message.answer("❌ No masājid found nearby. Try a different location.", parse_mode="Markdown")
        return
    
    # Send each mosque as a venue (with pin on map)
    for i, mosque in enumerate(mosques[:5], 1):
        name = mosque.get('display_name', 'Unknown').split(',')[0]
        address = mosque.get('display_name', 'Unknown')
        lat = float(mosque.get('lat'))
        lon = float(mosque.get('lon'))
        
        try:
            await message.answer_venue(
                latitude=lat,
                longitude=lon,
                title=f"{i}. {name}",
                address=address[:60] if len(address) > 60 else address
            )
        except Exception as e:
            logger.error(f"Error sending venue: {e}")
    
    await message.answer("May Allah make it easy for you 🤲")


@router.message(Command("remind"))
async def cmd_remind(message: Message):
    """Handle /remind command"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Enable", callback_data="remind_on"),
            InlineKeyboardButton(text="❌ Disable", callback_data="remind_off")
        ]
    ])
    
    await message.answer(
        "🔔 *Ṣalāh Reminder Settings*\n\nChoose your preference:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(Command("unremind"))
async def cmd_unremind(message: Message, session: AsyncSession):
    """Handle /unremind command"""
    user_id = message.from_user.id
    
    try:
        result = await session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if settings:
            settings.prayer_reminders = False
            await session.commit()
            logger.info(f"Prayer reminders disabled for user {user_id}")
    except Exception as e:
        logger.error(f"Error disabling reminders for {user_id}: {e}")
        await session.rollback()
    
    await message.answer(
        "❌ *Ṣalāh Reminders Disabled*\n\n"
        "You will no longer receive ṣalāh reminders.\n"
        "You may re-enable them anytime using /remind.",
        parse_mode="Markdown"
    )


@router.callback_query(F.data.in_(["remind_on", "remind_off"]))
async def callback_remind(callback: CallbackQuery, session: AsyncSession):
    """Handle remind enable/disable callbacks"""
    user_id = callback.from_user.id
    enable = callback.data == "remind_on"
    
    try:
        result = await session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = UserSettings(user_id=user_id)
            session.add(settings)
        
        settings.prayer_reminders = enable
        await session.commit()
        
        if enable:
            # Schedule prayer reminders (will be handled by scheduler)
            logger.info(f"Prayer reminders enabled for user {user_id}")
            text = (
                "🔔 *Ṣalāh Reminders Enabled*\n\n"
                "You will receive reminders:\n"
                "• 10 minutes before ṣalāh\n"
                "• At exact ṣalāh time\n\n"
                "May Allah help us remain steadfast 🤍"
            )
        else:
            logger.info(f"Prayer reminders disabled for user {user_id}")
            text = "❌ *Ṣalāh Reminders Disabled*"
        
        await callback.message.answer(text, parse_mode="Markdown")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error handling remind callback for {user_id}: {e}")
        await session.rollback()
        await callback.answer("An error occurred. Please try again.", show_alert=True)
