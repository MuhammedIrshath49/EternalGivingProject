"""Miscellaneous command handlers"""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import (
    AMAL_JARIAH_MONTH,
    AMAL_JARIAH_COUNTRY,
    AMAL_JARIAH_PRICE,
    AMAL_JARIAH_CONTACT,
    AMAL_JARIAH_WEBSITE
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("tasbih"))
async def cmd_tasbih(message: Message):
    """Handle /tasbih command"""
    text = (
        "📿 *Tasbih Time*\n\n"
        "• *أَسْتَغْفِرُ ٱللَّٰهَ* (100×)\n"
        "• *ٱللَّٰهُ ٱللَّٰهُ*\n"
        "• *ٱللَّهُمَّ صَلِّ عَلَىٰ مُحَمَّدٍ ﷺ*\n\n"
        "﴿ أَلَا بِذِكْرِ ٱللَّٰهِ تَطْمَئِنُّ ٱلْقُلُوبُ ﴾\n"
        "_Verily, in the remembrance of Allah do hearts find rest._ (13:28)"
    )
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("tabung"))
async def cmd_tabung(message: Message):
    """Handle /tabung command"""
    # Handle multiple countries (comma-separated)
    countries = [c.strip() for c in AMAL_JARIAH_COUNTRY.split(',')]
    
    if len(countries) > 1:
        country_text = "🌍 *COUNTRIES:*\n"
        for country in countries:
            country_text += f"   • {country}\n"
    else:
        country_text = f"🌍 *COUNTRY:* {AMAL_JARIAH_COUNTRY}\n"
    
    text = (
        "۞﷽۞\n"
        "🌹 *ROSE MADINAH SG*\n"
        "*AMAL JARIAH & DAWAH PROJECTS*\n\n"
        f"📅 *MONTH:* {AMAL_JARIAH_MONTH}\n"
        f"{country_text}\n"
        f"💰 *Price:* {AMAL_JARIAH_PRICE} (fixed)\n\n"
        "_JazakamAllah Khairan to all sponsors_\n\n"
        f"📞 *Register:* PM {AMAL_JARIAH_CONTACT}\n"
        f"🔗 *Website:* {AMAL_JARIAH_WEBSITE}\n\n"
        "May Allah multiply your rewards 🤲\n"
        "_Amal Jariah Projects that benefit the ummah continuously._"
    )
    
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)


@router.message(Command("feedback"))
async def cmd_feedback(message: Message):
    """Handle /feedback command"""
    text = (
        "📩 *We Value Your Feedback*\n\n"
        "🔗 Google Form: https://forms.gle/LMtXXfuKVbW6USor7\n"
        "📧 Email: rompeerbot@email.com\n\n"
        "JazakAllahu khair 🌹"
    )
    
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)


@router.message()
async def fallback_handler(message: Message):
    """Handle unknown commands and messages"""
    await message.answer(
        "❓ I didn't understand that.\n\nPlease use /help to see available commands.",
        parse_mode="Markdown"
    )
