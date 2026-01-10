"""Miscellaneous command handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import (
    AMAL_JARIAH_MONTH,
    AMAL_JARIAH_COUNTRY,
    AMAL_JARIAH_PRICE,
    AMAL_JARIAH_CONTACT,
    AMAL_JARIAH_WEBSITE,
    INSTITUTE_NAME,
    DONATION_PAYNOW_NUMBER,
    DONATION_CONTACT_WHATSAPP,
    STANDING_INSTRUCTION_ENABLED
)
from bot.utils.resources_api import get_resource_categories, get_resources_by_category
from database.models import StandingInstruction, DonationType, DonationFrequency

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
    keyboard_buttons = [
        [InlineKeyboardButton(text="🌹 AMAL JARIAH PROJECTS", callback_data="amal_jariah")],
        [InlineKeyboardButton(text="🎁 HADIAH", callback_data="amal_hadiah")],
        [InlineKeyboardButton(text="📚 CLASS FEES", callback_data="amal_class")],
        [InlineKeyboardButton(text="📢 DAWAH PROJECTS", callback_data="amal_dawah")],
        [InlineKeyboardButton(text="👶 SPONSOR A ORPHAN", callback_data="amal_orphan")]
    ]
    
    # Add standing instruction option if enabled
    if STANDING_INSTRUCTION_ENABLED:
        keyboard_buttons.append(
            [InlineKeyboardButton(text="🔄 SETUP STANDING INSTRUCTION", callback_data="setup_standing_instruction")]
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    text = (
        "                           ۞﷽۞\n\n"
        f"Thank you for your interest in contributing to the *{INSTITUTE_NAME}*!\n\n"
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
        f"Thank you for your interest in contributing to the *{INSTITUTE_NAME}* - *{project_name}*!\n\n"
        "To make your donation, please follow these steps:\n\n"
        f"1. *PayNow Transfer*: Use PayNow to transfer to *{DONATION_PAYNOW_NUMBER}*\n"
        "   You can scan the QR code below or enter the number directly.\n\n"
        f"2. *Send Confirmation*: After your transfer, send a WhatsApp message to *{DONATION_CONTACT_WHATSAPP}* with:\n"
        "   • A screenshot of the donation transfer\n"
        f"   • The project name: *{project_name}*\n"
        f"   • Your name (as registered in the bot)\n\n"
        "This will help us track your contribution and ensure it is allocated correctly to the project.\n\n"
        "💡 *Note:* All donations support the growth and operational needs of our institute, "
        "including resources, printing materials, and educational programs.\n\n"
        "For queries regarding Sadaqah, Wakaf, or Infaq contributions, "
        f"please contact *{DONATION_CONTACT_WHATSAPP}*.\n\n"
        "جَزَاكَ ٱللَّٰهُ خَيْرًا for your generous support! 🤲"
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


@router.callback_query(F.data == "setup_standing_instruction")
async def callback_setup_standing_instruction(callback: CallbackQuery):
    """Handle standing instruction setup"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌹 Amal Jariah Project", callback_data="si_amal_jariah")],
        [InlineKeyboardButton(text="🎁 Hadiah to Teacher", callback_data="si_amal_hadiah")],
        [InlineKeyboardButton(text="📚 Class Fees", callback_data="si_amal_class")],
        [InlineKeyboardButton(text="📢 Dawah Projects", callback_data="si_amal_dawah")],
        [InlineKeyboardButton(text="👶 Sponsor A Orphan", callback_data="si_amal_orphan")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_main_amal")]
    ])
    
    text = (
        f"🔄 *Setup Standing Instruction*\n\n"
        f"Set up a recurring monthly donation to support the *{INSTITUTE_NAME}* continuously!\n\n"
        "Benefits:\n"
        "• Automated reminders for your monthly donations\n"
        "• Consistent support for Islamic education\n"
        "• Track your ongoing contributions\n\n"
        "Please select which project you'd like to support regularly:"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("si_"))
async def callback_standing_instruction_project(callback: CallbackQuery):
    """Handle standing instruction project selection"""
    project_key = callback.data.replace("si_", "")
    
    project_names = {
        "amal_jariah": "Amal Jariah Project",
        "amal_hadiah": "Hadiah to Teacher",
        "amal_class": "Class Fees",
        "amal_dawah": "Dawah Projects",
        "amal_orphan": "Sponsor A Orphan"
    }
    
    project_name = project_names.get(project_key, "Unknown Project")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Monthly ($10)", callback_data=f"si_freq_{project_key}_monthly_10")],
        [InlineKeyboardButton(text="📅 Monthly ($20)", callback_data=f"si_freq_{project_key}_monthly_20")],
        [InlineKeyboardButton(text="📅 Monthly ($50)", callback_data=f"si_freq_{project_key}_monthly_50")],
        [InlineKeyboardButton(text="📅 Monthly (Custom Amount)", callback_data=f"si_custom_{project_key}_monthly")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="setup_standing_instruction")]
    ])
    
    text = (
        f"🔄 *Standing Instruction Setup*\n\n"
        f"Project: *{project_name}*\n\n"
        "Please select your monthly donation amount:\n\n"
        "💡 You will receive a reminder each month to make your donation.\n"
        "You can cancel or modify your standing instruction anytime using /mydonations"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("si_freq_"))
async def callback_confirm_standing_instruction(callback: CallbackQuery, session: AsyncSession):
    """Confirm and save standing instruction"""
    from datetime import datetime, timedelta
    
    # Parse callback data: si_freq_{project}_{frequency}_{amount}
    parts = callback.data.replace("si_freq_", "").split("_")
    project_key = parts[0]
    frequency = parts[1]
    amount = parts[2]
    
    project_names = {
        "amal_jariah": "Amal Jariah Project",
        "amal_hadiah": "Hadiah to Teacher",
        "amal_class": "Class Fees",
        "amal_dawah": "Dawah Projects",
        "amal_orphan": "Sponsor A Orphan"
    }
    
    donation_type_map = {
        "amal_jariah": DonationType.AMAL_JARIAH,
        "amal_hadiah": DonationType.HADIAH,
        "amal_class": DonationType.CLASS_FEES,
        "amal_dawah": DonationType.DAWAH,
        "amal_orphan": DonationType.ORPHAN_SPONSORSHIP
    }
    
    project_name = project_names.get(project_key, "Unknown")
    donation_type = donation_type_map.get(project_key, DonationType.GENERAL)
    
    try:
        # Create standing instruction
        standing_instruction = StandingInstruction(
            user_id=callback.from_user.id,
            donation_type=donation_type,
            amount=float(amount),
            frequency=DonationFrequency.MONTHLY,
            is_active=True,
            next_donation_date=datetime.now() + timedelta(days=30)
        )
        
        session.add(standing_instruction)
        await session.commit()
        
        text = (
            f"✅ *Standing Instruction Activated!*\n\n"
            f"Project: *{project_name}*\n"
            f"Amount: *${amount}*\n"
            f"Frequency: *Monthly*\n\n"
            f"You will receive a reminder next month to make your donation via PayNow to *{DONATION_PAYNOW_NUMBER}*.\n\n"
            "Use /mydonations to view or manage your standing instructions.\n\n"
            "جَزَاكَ ٱللَّٰهُ خَيْرًا for your commitment to continuous support! 🤲"
        )
        
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error creating standing instruction: {e}")
        await callback.message.edit_text(
            "❌ Sorry, there was an error setting up your standing instruction. Please try again later.",
            parse_mode="Markdown"
        )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_main_amal")
async def callback_back_to_main_amal(callback: CallbackQuery):
    """Go back to main amal menu"""
    keyboard_buttons = [
        [InlineKeyboardButton(text="🌹 AMAL JARIAH PROJECTS", callback_data="amal_jariah")],
        [InlineKeyboardButton(text="🎁 HADIAH", callback_data="amal_hadiah")],
        [InlineKeyboardButton(text="📚 CLASS FEES", callback_data="amal_class")],
        [InlineKeyboardButton(text="📢 DAWAH PROJECTS", callback_data="amal_dawah")],
        [InlineKeyboardButton(text="👶 SPONSOR A ORPHAN", callback_data="amal_orphan")]
    ]
    
    if STANDING_INSTRUCTION_ENABLED:
        keyboard_buttons.append(
            [InlineKeyboardButton(text="🔄 SETUP STANDING INSTRUCTION", callback_data="setup_standing_instruction")]
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    text = (
        "                           ۞﷽۞\n\n"
        f"Thank you for your interest in contributing to the *{INSTITUTE_NAME}*!\n\n"
        "To make your donation, Please select which project you are interested in contributing to:"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.message(Command("mydonations"))
async def cmd_my_donations(message: Message, session: AsyncSession):
    """View and manage standing instructions"""
    user_id = message.from_user.id
    
    try:
        result = await session.execute(
            select(StandingInstruction).where(
                StandingInstruction.user_id == user_id,
                StandingInstruction.is_active == True
            )
        )
        instructions = result.scalars().all()
        
        if not instructions:
            text = (
                "📊 *Your Donations*\n\n"
                "You don't have any active standing instructions yet.\n\n"
                "Use /amaljariah to set up recurring donations!"
            )
            await message.answer(text, parse_mode="Markdown")
            return
        
        text = "📊 *Your Active Standing Instructions*\n\n"
        
        for inst in instructions:
            text += (
                f"• *{inst.donation_type.value.replace('_', ' ').title()}*\n"
                f"  Amount: ${inst.amount}\n"
                f"  Frequency: {inst.frequency.value.title()}\n"
                f"  Next: {inst.next_donation_date.strftime('%d %b %Y') if inst.next_donation_date else 'Not scheduled'}\n\n"
            )
        
        text += "\nUse /amaljariah to add more or modify your donations."
        
        await message.answer(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error fetching donations for user {user_id}: {e}")
        await message.answer(
            "❌ Sorry, there was an error retrieving your donations.",
            parse_mode="Markdown"
        )


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
        "Virtues of Islamic Months": "✨",
        "Friday Khutbah": "🕌"
    }
    
    # Add Friday Khutbah as first category
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="🕌 FRIDAY KHUTBAH", 
            callback_data="resource_cat_Friday Khutbah"
        )
    ])
    
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
    
    # Special handling for Friday Khutbah
    if category == "Friday Khutbah":
        from config import KHUTBAH_MUIS_PAGE
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Access MUIS Khutbah Repository", url=KHUTBAH_MUIS_PAGE)],
            [InlineKeyboardButton(text="⬅️ Back to Categories", callback_data="resource_back")]
        ])
        
        text = (
            "🕌 *Friday Khutbah*\n\n"
            "Welcome to the Friday Khutbah section!\n\n"
            "*Automatic Delivery:*\n"
            "• You will receive the latest Friday Khutbah PDF automatically every Friday at 12:00 PM SGT\n"
            "• The khutbah is sourced from MUIS (Majlis Ugama Islam Singapura)\n\n"
            "*Access Full Repository:*\n"
            "• Click the button below to browse nearly 1,000 khutbah articles\n"
            "• Available in English, Malay, and Tamil\n"
            "• Topics include filial piety, divine assistance, Islamic celebrations, and more\n\n"
            "May Allah grant us beneficial knowledge 🤲"
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        return
    
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
        "Virtues of Islamic Months": "✨",
        "Friday Khutbah": "🕌"
    }
    
    # Add Friday Khutbah as first category
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="🕌 FRIDAY KHUTBAH", 
            callback_data="resource_cat_Friday Khutbah"
        )
    ])
    
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


@router.message(F.text)
async def fallback_handler(message: Message):
    """Handle unknown commands and messages (text only)"""
    await message.answer(
        "❓ I didn't understand that.\n\nPlease use /help to see available commands.",
        parse_mode="Markdown"
    )
