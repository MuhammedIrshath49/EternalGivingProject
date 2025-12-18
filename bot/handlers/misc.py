"""Miscellaneous command handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    AMAL_JARIAH_MONTH,
    AMAL_JARIAH_COUNTRY,
    AMAL_JARIAH_PRICE,
    AMAL_JARIAH_CONTACT,
    AMAL_JARIAH_WEBSITE
)
from bot.utils.resources_api import get_resource_categories, get_resources_by_category

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("tasbih"))
async def cmd_tasbih(message: Message):
    """Handle /tasbih command"""
    text = (
        "                    📿 *Tasbih Time*\n\n"
        "• *أَسْتَغْفِرُ ٱللَّٰهَ* (100×)\n"
        "• *ٱللَّٰهُ ٱللَّٰهُ*\n"
        "• *ٱللَّهُمَّ صَلِّ عَلَىٰ مُحَمَّدٍ ﷺ*\n\n"
        "﴿ أَلَا بِذِكْرِ ٱللَّٰهِ تَطْمَئِنُّ ٱلْقُلُوبُ ﴾\n"
        "_Verily, in the remembrance of Allah do hearts find rest._ (13:28)"
    )
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("amaljariah"))
async def cmd_amaljariah(message: Message):
    """Handle /amaljariah command"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌹 AMAL JARIAH PROJECTS", callback_data="amal_jariah")],
        [InlineKeyboardButton(text="🎁 HADIAH", callback_data="amal_hadiah")],
        [InlineKeyboardButton(text="📚 CLASS FEES", callback_data="amal_class")],
        [InlineKeyboardButton(text="📢 DAWAH PROJECTS", callback_data="amal_dawah")],
        [InlineKeyboardButton(text="👶 SPONSOR A ORPHAN", callback_data="amal_orphan")]
    ])
    
    text = (
        "                           ۞﷽۞\n\n"
        "Thank you for your interest in contributing to the Rose of Madinah Amal Project!\n\n"
        "To make your donation, Please select which project you are interested in contributing to:"
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.in_(["amal_jariah", "amal_hadiah", "amal_class", "amal_dawah", "amal_orphan"]))
async def callback_amal_jariah(callback: CallbackQuery):
    """Handle Amal Jariah project selection"""
    from aiogram.types import FSInputFile
    import os
    
    project_names = {
        "amal_jariah": "Amal Jariah Project",
        "amal_hadiah": "Hadiah to Teacher",
        "amal_class": "Class Fees",
        "amal_dawah": "Dawah Projects",
        "amal_orphan": "Sponsor A Orphan"
    }
    
    project_name = project_names[callback.data]
    
    # QR code instructions text
    text = (
        f"Thank you for your interest in contributing to the Rose of Madinah *{project_name}*!\n\n"
        "To make your donation, please follow these steps:\n\n"
        "1. *Scan the QR Code*: You can save the QR code below and make your PayNow transfer by scanning it.\n\n"
        "2. *Send a WhatsApp Message*: After your transfer, kindly send a WhatsApp message to *82681357* with:\n"
        "   • A screenshot of the donation transfer\n"
        f"   • The project name: *{project_name}*\n\n"
        "This will help us track your contribution and ensure it is allocated correctly to the project.\n\n"
        "For any queries regarding Sadaqah, Wakaf, or Infaq contributions to any project, "
        "please don't hesitate to contact *82681357*.\n\n"
        "Thank you for your generous support!"
    )
    
    # Send the QR code image
    qr_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "qrcode.png")
    
    try:
        if os.path.exists(qr_path):
            photo = FSInputFile(qr_path)
            await callback.message.answer_photo(photo=photo, caption=text, parse_mode="Markdown")
        else:
            # Fallback if QR code file not found
            await callback.message.answer(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending QR code: {e}")
        await callback.message.answer(text, parse_mode="Markdown")
    
    await callback.answer()


@router.message(Command("resources"))
async def cmd_resources(message: Message):
    """Handle /resources command"""
    categories = await get_resource_categories()
    
    # Create buttons for each category
    keyboard_buttons = []
    category_icons = {
        "Duas": "🤲",
        "Surahs": "📖",
        "Iqra": "📚",
        "Latest Articles": "📰",
        "Awrad": "🌙",
        "Handbooks": "📕",
        "Virtues of Islamic Months": "✨"
    }
    
    for category in categories:
        icon = category_icons.get(category, "📄")
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {category.upper()}", 
                callback_data=f"resource_cat_{category}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    text = (
        "📚 *Islamic Resources*\n\n"
        "Please select a category to explore our collection of Islamic resources:"
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("resource_cat_"))
async def callback_resource_category(callback: CallbackQuery):
    """Handle resource category selection"""
    category = callback.data.replace("resource_cat_", "")
    resources = await get_resources_by_category(category)
    
    if not resources:
        await callback.message.answer(
            f"No resources found for *{category}*. Please check back later!",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # Create buttons for each resource in the category
    keyboard_buttons = []
    for resource in resources:
        # Add file type emoji
        type_icon = "📄"
        if resource['type'].lower() == "video":
            type_icon = "🎥"
        elif resource['type'].lower() == "pdf":
            type_icon = "📄"
        elif resource['type'].lower() == "audio":
            type_icon = "🎵"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{type_icon} {resource['title']}", 
                url=resource['url']
            )
        ])
    
    # Add back button
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Categories", callback_data="resource_back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    text = (
        f"📚 *{category}*\n\n"
        "Select a resource to access:"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "resource_back")
async def callback_resource_back(callback: CallbackQuery):
    """Handle back to categories button"""
    categories = await get_resource_categories()
    
    # Create buttons for each category
    keyboard_buttons = []
    category_icons = {
        "Duas": "🤲",
        "Surahs": "📖",
        "Iqra": "📚",
        "Latest Articles": "📰",
        "Awrad": "🌙",
        "Handbooks": "📕",
        "Virtues of Islamic Months": "✨"
    }
    
    for category in categories:
        icon = category_icons.get(category, "📄")
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {category.upper()}", 
                callback_data=f"resource_cat_{category}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    text = (
        "📚 *Islamic Resources*\n\n"
        "Please select a category to explore our collection of Islamic resources:"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


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
