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
    Find nearby mosques using Overpass API (OpenStreetMap query service)
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        limit: Maximum number of results
    
    Returns:
        List of mosque dictionaries or None on error
    """
    try:
        # Use Overpass API to find mosques within 5km radius
        # Overpass is specifically designed for POI queries and doesn't have the same rate limits
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Search radius in meters (5000m = 5km)
        radius = 5000
        
        # Overpass QL query to find mosques
        # amenity=place_of_worship + religion=muslim covers most mosques
        overpass_query = f"""
        [out:json][timeout:10];
        (
          node["amenity"="place_of_worship"]["religion"="muslim"](around:{radius},{latitude},{longitude});
          way["amenity"="place_of_worship"]["religion"="muslim"](around:{radius},{latitude},{longitude});
          node["building"="mosque"](around:{radius},{latitude},{longitude});
          way["building"="mosque"](around:{radius},{latitude},{longitude});
        );
        out center;
        """
        
        headers = {
            "User-Agent": "ROM_PeerBot/2.0 (Islamic Prayer App)"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                overpass_url, 
                data={"data": overpass_query},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    elements = data.get('elements', [])
                    
                    if not elements:
                        logger.warning(f"No mosques found via Overpass API near ({latitude}, {longitude})")
                        return None
                    
                    mosques_with_distance = []
                    seen_coords = set()
                    
                    for element in elements:
                        try:
                            # Get coordinates (handle both nodes and ways)
                            if element['type'] == 'node':
                                place_lat = float(element['lat'])
                                place_lon = float(element['lon'])
                            elif element['type'] == 'way' and 'center' in element:
                                place_lat = float(element['center']['lat'])
                                place_lon = float(element['center']['lon'])
                            else:
                                continue
                            
                            # Avoid duplicates by coordinate
                            coord_key = (round(place_lat, 4), round(place_lon, 4))
                            if coord_key in seen_coords:
                                continue
                            seen_coords.add(coord_key)
                            
                            # Calculate distance
                            distance = calculate_distance(latitude, longitude, place_lat, place_lon)
                            
                            # Get name from tags
                            tags = element.get('tags', {})
                            name = (tags.get('name') or 
                                   tags.get('name:en') or 
                                   tags.get('name:ms') or 
                                   tags.get('name:ar') or
                                   'Mosque')
                            
                            # Build address from available tags
                            address_parts = [name]
                            if tags.get('addr:street'):
                                address_parts.append(tags.get('addr:street'))
                            if tags.get('addr:postcode'):
                                address_parts.append(tags.get('addr:postcode'))
                            
                            display_name = ', '.join(address_parts)
                            
                            mosques_with_distance.append({
                                'display_name': display_name,
                                'lat': str(place_lat),
                                'lon': str(place_lon),
                                'distance': distance
                            })
                            
                        except (ValueError, TypeError, KeyError) as e:
                            logger.debug(f"Error processing element: {e}")
                            continue
                    
                    # Sort by distance and return top results
                    mosques_with_distance.sort(key=lambda x: x['distance'])
                    mosques = mosques_with_distance[:limit]
                    
                    logger.info(f"Found {len(mosques)} mosques via Overpass API near ({latitude}, {longitude})")
                    return mosques if mosques else None
                    
                elif response.status == 429:
                    logger.error("Overpass API rate limit exceeded")
                    return None
                else:
                    logger.error(f"Overpass API returned status {response.status}")
                    return None
        
    except aiohttp.ClientError as e:
        logger.error(f"Network error finding mosques: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error finding mosques: {e}", exc_info=True)
        return None
