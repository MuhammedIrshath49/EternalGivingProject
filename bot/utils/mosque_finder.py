"""Mosque finder integration"""

import logging
import aiohttp
import math
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


async def find_nearby_mosques(latitude: float, longitude: float, limit: int = 5) -> Optional[List[Dict]]:
    """
    Find nearby mosques using Nominatim reverse geocoding with nearby POI search
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        limit: Maximum number of results
    
    Returns:
        List of mosque dictionaries or None on error
    """
    try:
        # Use Nominatim reverse endpoint with zoom level for POIs
        reverse_url = "https://nominatim.openstreetmap.org/reverse"
        
        params = {
            'format': 'json',
            'lat': latitude,
            'lon': longitude,
            'zoom': 18,  # High zoom for detailed POIs
            'addressdetails': 1,
            'extratags': 1
        }
        
        headers = {
            "User-Agent": "ROM_PeerBot/2.0 (Islamic Prayer App)"
        }
        
        # Try multiple search strategies
        mosques_with_distance = []
        
        # Strategy 1: Search by city name + mosque keywords
        async with aiohttp.ClientSession() as session:
            # First get the city name
            async with session.get(reverse_url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    location_data = await response.json()
                    address = location_data.get('address', {})
                    city = address.get('city') or address.get('town') or address.get('village') or address.get('suburb', '')
                    
                    # Now search for mosques in this city
                    search_url = "https://nominatim.openstreetmap.org/search"
                    search_terms = [
                        f"mosque {city}",
                        f"masjid {city}",
                        f"musolla {city}",
                        f"islamic center {city}"
                    ]
                    
                    for search_term in search_terms:
                        search_params = {
                            'format': 'json',
                            'q': search_term,
                            'limit': 20,
                            'addressdetails': 0
                        }
                        
                        async with session.get(search_url, params=search_params, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as search_response:
                            if search_response.status == 200:
                                results = await search_response.json()
                                
                                for place in results:
                                    try:
                                        place_lat = float(place.get('lat', 0))
                                        place_lon = float(place.get('lon', 0))
                                        distance = calculate_distance(latitude, longitude, place_lat, place_lon)
                                        
                                        # Only include mosques within 10km
                                        if distance <= 10:
                                            name = place.get('name') or place.get('display_name', '').split(',')[0] or 'Masjid'
                                            
                                            # Avoid duplicates by checking if similar mosque already exists
                                            is_duplicate = any(
                                                m['display_name'].lower() == name.lower() or 
                                                (abs(float(m['lat']) - place_lat) < 0.0001 and abs(float(m['lon']) - place_lon) < 0.0001)
                                                for m in mosques_with_distance
                                            )
                                            
                                            if not is_duplicate:
                                                mosques_with_distance.append({
                                                    'display_name': name,
                                                    'lat': str(place_lat),
                                                    'lon': str(place_lon),
                                                    'distance': distance
                                                })
                                    except (ValueError, TypeError):
                                        continue
                        
                        # Stop if we found enough mosques
                        if len(mosques_with_distance) >= limit * 2:
                            break
        
        # Sort by distance and get top results
        mosques_with_distance.sort(key=lambda x: x['distance'])
        mosques = [
            {
                'display_name': m['display_name'],
                'lat': m['lat'],
                'lon': m['lon']
            }
            for m in mosques_with_distance[:limit]
        ]
        
        logger.info(f"Found {len(mosques)} mosques near ({latitude}, {longitude})")
        return mosques if mosques else None
        
    except aiohttp.ClientError as e:
        logger.error(f"Network error finding mosques: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error finding mosques: {e}")
        return None
