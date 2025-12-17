"""Mosque finder integration"""

import logging
import aiohttp
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


async def find_nearby_mosques(latitude: float, longitude: float, limit: int = 5) -> Optional[List[Dict]]:
    """
    Find nearby mosques using OpenStreetMap Overpass API
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        limit: Maximum number of results
    
    Returns:
        List of mosque dictionaries or None on error
    """
    try:
        # Use Overpass API for accurate nearby search
        # Search within 5km radius
        radius = 5000  # meters
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Overpass query to find mosques within radius
        overpass_query = f"""
        [out:json];
        (
          node["amenity"="place_of_worship"]["religion"="muslim"](around:{radius},{latitude},{longitude});
          way["amenity"="place_of_worship"]["religion"="muslim"](around:{radius},{latitude},{longitude});
        );
        out center {limit};
        """
        
        headers = {
            "User-Agent": "ROM_PeerBot/2.0"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(overpass_url, data={"data": overpass_query}, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    elements = data.get('elements', [])
                    
                    # Convert to our format
                    mosques = []
                    for element in elements[:limit]:
                        lat = element.get('lat') or element.get('center', {}).get('lat')
                        lon = element.get('lon') or element.get('center', {}).get('lon')
                        
                        if lat and lon:
                            name = element.get('tags', {}).get('name', 'Mosque')
                            mosques.append({
                                'display_name': name,
                                'lat': str(lat),
                                'lon': str(lon)
                            })
                    
                    logger.info(f"Found {len(mosques)} mosques near ({latitude}, {longitude})")
                    return mosques
                else:
                    logger.error(f"Failed to fetch mosques: HTTP {response.status}")
                    return None
    except aiohttp.ClientError as e:
        logger.error(f"Network error finding mosques: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error finding mosques: {e}")
        return None
