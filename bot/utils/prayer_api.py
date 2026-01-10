"""Prayer times API integration with MUIS (Singapore) support"""

import logging
import aiohttp
from typing import Optional, Tuple, Dict
from datetime import datetime
from config import PRAYER_API_URL, PRAYER_METHOD
from bot.utils.muis_prayer_csv import get_prayer_times_from_csv, get_readable_date

logger = logging.getLogger(__name__)


async def get_muis_prayer_times() -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    """
    Get prayer times from MUIS (Majlis Ugama Islam Singapura) official CSV data
    This is the authoritative source for Singapore prayer times - directly from MUIS timetable.
    
    Returns:
        Tuple of (timings dict, readable date string) or (None, None) on error
    """
    try:
        today = datetime.now()
        timings = get_prayer_times_from_csv(today)
        
        if timings:
            readable_date = get_readable_date(today)
            logger.info(f"Retrieved MUIS prayer times from official CSV for {readable_date}")
            return timings, readable_date
        else:
            logger.error("Failed to retrieve prayer times from MUIS CSV")
            return None, None
            
    except Exception as e:
        logger.error(f"Error fetching MUIS prayer times from CSV: {e}")
        return None, None


async def get_prayer_times(city: str, country: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    """
    Fetch prayer times for a given city and country
    For Singapore, uses MUIS official CSV data; for other locations, uses Aladhan API
    
    Args:
        city: City name
        country: Country name
    
    Returns:
        Tuple of (timings dict, readable date string) or (None, None) on error
    """
    # Use MUIS CSV data for Singapore for 100% accuracy
    if city.lower() == "singapore" or country.lower() == "singapore":
        timings, date = await get_muis_prayer_times()
        if timings:
            return timings, date
        # Fall back to Aladhan if MUIS CSV reading fails
        logger.warning("MUIS CSV reading failed, falling back to Aladhan API")
    
    # Use Aladhan API for other locations
    try:
        params = {
            "city": city,
            "country": country,
            "method": PRAYER_METHOD
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(PRAYER_API_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    timings = data["data"]["timings"]
                    readable_date = data["data"]["date"]["readable"]
                    logger.info(f"Fetched prayer times for {city}, {country}")
                    return timings, readable_date
                else:
                    logger.error(f"Failed to fetch prayer times: HTTP {response.status}")
                    return None, None
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching prayer times: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error fetching prayer times: {e}")
        return None, None
