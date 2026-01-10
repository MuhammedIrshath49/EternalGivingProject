"""Friday Khutbah scheduler

MUIS Khutbah Repository:
https://www.muis.gov.sg/resources/khutbah-and-religious-advice/khutbah/

Features:
- Nearly 1,000 khutbah articles
- Available as readable text online and downloadable PDFs
- Filters by language (English, Malay, Tamil) and date
- Updated regularly for Jumu'ah prayers
- Topics: filial piety, divine assistance, Aidiladha reflections, etc.

How to Use:
1. Visit the MUIS Khutbah page above
2. Filter by: Year=2026, Language=English
3. Download the latest Friday khutbah PDF
4. Upload to your storage (Google Drive, Dropbox, etc.)
5. Set KHUTBAH_PDF_URL to the direct download link
6. Bot automatically distributes every Friday at 10:00 AM SGT
"""

import logging
import aiohttp
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.types import FSInputFile, BufferedInputFile
from sqlalchemy import select
import database.db
from database.models import UserSettings
from config import KHUTBAH_PDF_URL, KHUTBAH_ENABLED, KHUTBAH_MUIS_PAGE
import os

logger = logging.getLogger(__name__)


async def download_khutbah_pdf() -> tuple[bytes | None, str]:
    """
    Download the latest Friday Khutbah PDF
    Automatically fetches from MUIS website or uses manual URL
    
    Returns:
        Tuple of (PDF bytes, filename) or (None, "") if failed
    """
    # Try automated fetching from MUIS website first
    try:
        from bot.utils.khutbah_fetcher import get_latest_khutbah_pdf_url
        
        logger.info("Attempting to auto-fetch latest khutbah from MUIS website...")
        pdf_bytes, filename = await get_latest_khutbah_pdf_url()
        
        if pdf_bytes:
            logger.info(f"✅ Successfully auto-fetched khutbah from MUIS: {filename}")
            return pdf_bytes, filename
        else:
            logger.warning("Auto-fetch from MUIS failed, trying manual URL fallback...")
    except Exception as e:
        logger.warning(f"Auto-fetch error: {e}, trying manual URL fallback...")
    
    # Fallback to manual URL if auto-fetch fails
    if not KHUTBAH_PDF_URL:
        logger.error("Auto-fetch failed and KHUTBAH_PDF_URL not configured")
        return None, ""
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(KHUTBAH_PDF_URL, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    pdf_bytes = await response.read()
                    
                    # Generate filename with current date
                    today = datetime.now()
                    filename = f"Friday_Khutbah_{today.strftime('%Y%m%d')}.pdf"
                    
                    logger.info(f"Downloaded Friday Khutbah PDF from manual URL: {filename}")
                    return pdf_bytes, filename
                else:
                    logger.error(f"Failed to download Khutbah PDF: HTTP {response.status}")
                    return None, ""
    except Exception as e:
        logger.error(f"Error downloading Khutbah PDF: {e}")
        return None, ""


async def send_friday_khutbah(bot: Bot):
    """Send Friday Khutbah PDF to all subscribed users"""
    if not KHUTBAH_ENABLED:
        logger.info("Friday Khutbah distribution is disabled")
        return
    
    try:
        # Download the PDF
        pdf_bytes, filename = await download_khutbah_pdf()
        
        if not pdf_bytes:
            logger.error("Could not download Khutbah PDF, skipping distribution")
            return
        
        # Get all users who want to receive Friday Khutbah
        # For now, send to all active users
        if not database.db.async_session_maker:
            logger.warning("Database session maker not initialized yet")
            return
        
        async with database.db.async_session_maker() as session:
            result = await session.execute(select(UserSettings))
            all_users = result.scalars().all()
            
            success_count = 0
            fail_count = 0
            
            for settings in all_users:
                try:
                    # Create BufferedInputFile from bytes
                    document = BufferedInputFile(pdf_bytes, filename=filename)
                    
                    caption = (
                        "🕌 *Jumʿah Mubārak!* 🕌\n\n"
                        "Here is this week's Friday Khutbah.\n\n"
                        "May Allah accept our ṣalāh and grant us beneficial knowledge 🤲\n\n"
                        "﴿ يَـٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُوٓا۟ إِذَا نُودِىَ لِلصَّلَوٰةِ مِن يَوْمِ ٱلْجُمُعَةِ فَٱسْعَوْا۟ إِلَىٰ ذِكْرِ ٱللَّهِ ﴾\n"
                        "_O believers! When the call to prayer is made on Friday, then proceed to the remembrance of Allah..._"
                    )
                    
                    await bot.send_document(
                        chat_id=settings.user_id,
                        document=document,
                        caption=caption,
                        parse_mode="Markdown"
                    )
                    
                    success_count += 1
                    logger.info(f"Sent Friday Khutbah to user {settings.user_id}")
                    
                except Exception as e:
                    fail_count += 1
                    logger.error(f"Error sending Khutbah to user {settings.user_id}: {e}")
            
            logger.info(f"Friday Khutbah distribution complete: {success_count} successful, {fail_count} failed")
            
    except Exception as e:
        logger.error(f"Error in Friday Khutbah distribution: {e}")


def setup_khutbah_scheduler(scheduler: AsyncIOScheduler, bot: Bot):
    """Setup Friday Khutbah distribution scheduler"""
    if not KHUTBAH_ENABLED:
        logger.info("Friday Khutbah scheduler disabled")
        return
    
    # Schedule for every Friday at 12:00 PM Singapore time (safer - ensures khutbah is published)
    scheduler.add_job(
        send_friday_khutbah,
        'cron',
        day_of_week='fri',
        hour=12,
        minute=0,
        timezone='Asia/Singapore',
        args=[bot],
        id='friday_khutbah',
        replace_existing=True
    )
    
    logger.info("Friday Khutbah scheduler setup complete - will send every Friday at 12:00 PM SGT")
