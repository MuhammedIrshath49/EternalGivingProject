"""Prayer times API integration"""

import logging
import aiohttp
from typing import Optional, Tuple, Dict
from config import PRAYER_API_URL, PRAYER_METHOD

logger = logging.getLogger(__name__)


async def get_prayer_times(city: str, country: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    """
    Fetch prayer times for a given city and country
    
    Args:
        city: City name
        country: Country name
    
    Returns:
        Tuple of (timings dict, readable date string) or (None, None) on error
    """
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
