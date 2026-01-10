"""Singapore Mosque Dataset - Curated from MUIS Official Data"""

import math
from typing import List, Dict, Optional

# Official MUIS Mosques in Singapore with coordinates
# Source: MUIS.gov.sg Official Directory (January 2026)
# Coordinates: OneMap.sg geocoding
SINGAPORE_MOSQUES = [
    # A
    {"name": "Masjid Abdul Aleem Siddique", "address": "90 Lorong K Telok Kurau, Singapore 425723", "lat": 1.3130, "lon": 103.9127, "contact": "63460153"},
    {"name": "Masjid Abdul Gafoor", "address": "41 Dunlop Street, Singapore 209369", "lat": 1.3034, "lon": 103.8573, "contact": "62954209"},
    {"name": "Masjid Abdul Hamid Kampung Pasiran", "address": "10 Gentle Road, Singapore 309194", "lat": 1.3068, "lon": 103.8606, "contact": "62512729"},
    {"name": "Masjid Ahmad", "address": "2 Lorong Sarhad, Singapore 119173", "lat": 1.2821, "lon": 103.8028, "contact": "64796442"},
    {"name": "Masjid Ahmad Ibrahim", "address": "15 Jalan Ulu Seletar, Singapore 769227", "lat": 1.3964, "lon": 103.8049, "contact": "64540848"},
    {"name": "Masjid Al-Abdul Razak", "address": "30 Jalan Ismail, Singapore 419285", "lat": 1.3155, "lon": 103.8990, "contact": "68468404"},
    {"name": "Masjid Al-Abrar", "address": "192 Telok Ayer Street, Singapore 068635", "lat": 1.2803, "lon": 103.8473, "contact": "62206306"},
    {"name": "Masjid Al-Amin", "address": "50 Telok Blangah Way, Singapore 098801", "lat": 1.2714, "lon": 103.8115, "contact": "62725309"},
    {"name": "Masjid Al-Ansar", "address": "155 Bedok North Avenue 1, Singapore 469751", "lat": 1.3327, "lon": 103.9290, "contact": "64492420"},
    {"name": "Masjid Al-Falah", "address": "22 Bideford Road #01-01, Singapore 229923", "lat": 1.3138, "lon": 103.8401, "contact": "62353172"},
    {"name": "Masjid Al-Firdaus", "address": "11 Jalan Ibadat, Singapore 698955", "lat": 1.3242, "lon": 103.8671, "contact": "67646334"},
    {"name": "Masjid Al-Huda", "address": "34 Jalan Haji Alias, Singapore 268534", "lat": 1.3185, "lon": 103.8683, "contact": "64684844"},
    {"name": "Masjid Al-Iman", "address": "10 Bukit Panjang Ring Road, Singapore 679943", "lat": 1.3808, "lon": 103.7699, "contact": "67690770"},
    {"name": "Masjid Al-Islah", "address": "30 Punggol Field, Singapore 828812", "lat": 1.3984, "lon": 103.9066, "contact": "63125194"},
    {"name": "Masjid Al-Istighfar", "address": "2 Pasir Ris Walk, Singapore 518239", "lat": 1.3711, "lon": 103.9492, "contact": "64267130"},
    {"name": "Masjid Al-Istiqamah", "address": "2 Serangoon North Avenue 2, Singapore 555876", "lat": 1.3522, "lon": 103.8701, "contact": "62814287"},
    {"name": "Masjid Alkaff Kampung Melayu", "address": "200 Bedok Reservoir Road, Singapore 479221", "lat": 1.3353, "lon": 103.9165, "contact": "62427244"},
    {"name": "Masjid Alkaff Upper Serangoon", "address": "66 Pheng Geck Avenue, Singapore 348261", "lat": 1.3603, "lon": 103.8816, "contact": "62800300"},
    {"name": "Masjid Al-Khair", "address": "1 Teck Whye Crescent, Singapore 688847", "lat": 1.3786, "lon": 103.7523, "contact": "67601139"},
    {"name": "Masjid Al-Mawaddah", "address": "151 Compassvale Bow, Singapore 544997", "lat": 1.3941, "lon": 103.9002, "contact": "64890224"},
    {"name": "Masjid Al-Mukminin", "address": "271 Jurong East Street 21, Singapore 609603", "lat": 1.3392, "lon": 103.7414, "contact": "65677777"},
    {"name": "Masjid Al-Muttaqin", "address": "5140 Ang Mo Kio Avenue 6, Singapore 569844", "lat": 1.3791, "lon": 103.8394, "contact": "64547472"},
    {"name": "Masjid Al-Taqua", "address": "11A Jalan Bilal, Singapore 468862", "lat": 1.3292, "lon": 103.9020, "contact": "64427704"},
    {"name": "Masjid Angullia", "address": "265 Serangoon Road, Singapore 218099", "lat": 1.3104, "lon": 103.8551, "contact": "62951478"},
    {"name": "Masjid An-Nahdhah", "address": "9A Bishan Street 14, Singapore 579786", "lat": 1.3518, "lon": 103.8468, "contact": "63543138"},
    {"name": "Masjid An-Nur", "address": "6 Admiralty Road, Singapore 739983", "lat": 1.4454, "lon": 103.8014, "contact": "63631383"},
    {"name": "Masjid Ar-Raudhah", "address": "30 Bukit Batok East Avenue 2, Singapore 659919", "lat": 1.3459, "lon": 103.7487, "contact": "68995840"},
    {"name": "Masjid Assyafaah", "address": "1 Admiralty Lane, Singapore 757620", "lat": 1.4405, "lon": 103.8013, "contact": "67563008"},
    {"name": "Masjid Assyakirin", "address": "550 Yung An Road, Singapore 618617", "lat": 1.3293, "lon": 103.7208, "contact": "62681846"},
    
    # B
    {"name": "Masjid Ba'alwie", "address": "2 Lewis Road, Singapore 258590", "lat": 1.3485, "lon": 103.8317, "contact": "67326795"},
    {"name": "Masjid Bencoolen", "address": "59 Bencoolen Street #01-01, Singapore 189630", "lat": 1.2990, "lon": 103.8508, "contact": "63333016"},
    {"name": "Masjid Burhani", "address": "39 Hill Street, Singapore 179364", "lat": 1.2935, "lon": 103.8508, "contact": "63343712"},
    
    # D
    {"name": "Masjid Darul Aman", "address": "1 Jalan Eunos, Singapore 419493", "lat": 1.3198, "lon": 103.9003, "contact": "67445544"},
    {"name": "Masjid Darul Ghufran", "address": "503 Tampines Avenue 5, Singapore 529651", "lat": 1.3535, "lon": 103.9428, "contact": "67865545"},
    {"name": "Masjid Darul Makmur", "address": "950 Yishun Avenue 2, Singapore 769099", "lat": 1.4182, "lon": 103.8361, "contact": "67521402"},
    {"name": "Masjid Darussalam", "address": "3002 Commonwealth Avenue West, Singapore 129579", "lat": 1.3037, "lon": 103.7650, "contact": "67770028"},
    
    # E
    {"name": "Masjid En-Naeem", "address": "120 Tampines Road, Singapore 535136", "lat": 1.3501, "lon": 103.9428, "contact": "69118140"},
    
    # H
    {"name": "Masjid Haji Mohd Salleh (Geylang)", "address": "245 Geylang Road, Singapore 389304", "lat": 1.3118, "lon": 103.8721, "contact": "68460857"},
    {"name": "Masjid Haji Muhammad Salleh (Palmer)", "address": "37 Palmer Road, Singapore 079424", "lat": 1.2789, "lon": 103.8380, "contact": "62209257"},
    {"name": "Masjid Haji Yusoff", "address": "2 Hillside Drive, Singapore 548920", "lat": 1.3143, "lon": 103.9091, "contact": "62845459"},
    {"name": "Masjid Hajjah Fatimah", "address": "4001 Beach Road, Singapore 199584", "lat": 1.3030, "lon": 103.8618, "contact": "62972774"},
    {"name": "Masjid Hajjah Rahimabi", "address": "76 Kim Keat Road, Singapore 328835", "lat": 1.3240, "lon": 103.8530, "contact": "62558262"},
    {"name": "Masjid Hang Jebat", "address": "100 Jalan Hang Jebat, Singapore 139533", "lat": 1.2905, "lon": 103.8245, "contact": "64710728"},
    {"name": "Masjid Hasanah", "address": "492 Teban Gardens, Singapore 608878", "lat": 1.3208, "lon": 103.7433, "contact": "65617990"},
    {"name": "Masjid Hussein Sulaiman", "address": "394 Pasir Panjang Road, Singapore 118730", "lat": 1.2859, "lon": 103.7878, "contact": "63591199"},
    
    # J
    {"name": "Masjid Jamae (Chulia)", "address": "218 South Bridge Road, Singapore 058767", "lat": 1.2834, "lon": 103.8451, "contact": "62214165"},
    {"name": "Masjid Jamek Queenstown", "address": "946 Margaret Drive, Singapore 149309", "lat": 1.2968, "lon": 103.8053, "contact": "69280442"},
    {"name": "Masjid Jamiyah Ar-Rabitah", "address": "601 Tiong Bahru Road, Singapore 158787", "lat": 1.2872, "lon": 103.8179, "contact": "62733848"},
    
    # K
    {"name": "Masjid Kampong Delta", "address": "10 Delta Avenue, Singapore 169831", "lat": 1.2985, "lon": 103.8227, "contact": "62721750"},
    {"name": "Masjid Kampung Siglap", "address": "451 Marine Parade Road, Singapore 449283", "lat": 1.3124, "lon": 103.9241, "contact": "62437060"},
    {"name": "Masjid Kassim", "address": "450 Changi Road, Singapore 419877", "lat": 1.3161, "lon": 103.9049, "contact": "64409434"},
    {"name": "Masjid Khadijah", "address": "583 Geylang Road, Singapore 389522", "lat": 1.3135, "lon": 103.8782, "contact": "67475607"},
    {"name": "Masjid Khalid", "address": "130 Joo Chiat Road, Singapore 427727", "lat": 1.3112, "lon": 103.9020, "contact": "63452884"},
    
    # M
    {"name": "Masjid Maarof", "address": "20 Jurong West Street 26, Singapore 648125", "lat": 1.3336, "lon": 103.7199, "contact": "65155033"},
    {"name": "Masjid Malabar", "address": "471 Victoria Street, Singapore 198370", "lat": 1.3060, "lon": 103.8572, "contact": "62943862"},
    {"name": "Masjid Moulana Mohd Ali", "address": "80 Raffles Place #B1-01, UOB Plaza, Singapore 048624", "lat": 1.2843, "lon": 103.8510, "contact": "65365238"},
    {"name": "Masjid Muhajirin", "address": "275 Braddell Road, Singapore 579704", "lat": 1.3451, "lon": 103.8568, "contact": "62561166"},
    {"name": "Masjid Mujahidin", "address": "590 Stirling Road, Singapore 148952", "lat": 1.2993, "lon": 103.8050, "contact": "64737400"},
    {"name": "Masjid Mydin", "address": "67 Jalan Lapang, Singapore 419007", "lat": 1.3139, "lon": 103.9024, "contact": "62432129"},
    
    # O
    {"name": "Masjid Omar Kampong Melaka", "address": "10 Keng Cheow Street, Singapore 059607", "lat": 1.2798, "lon": 103.8435, "contact": "65326764"},
    {"name": "Masjid Omar Salmah", "address": "441-B Jalan Mashor, Singapore 299173", "lat": 1.3550, "lon": 103.8279, "contact": "62500120"},
    
    # P
    {"name": "Masjid Petempatan Melayu Sembawang", "address": "27-B Jalan Mempurong, Singapore 759055", "lat": 1.4677, "lon": 103.8224, "contact": "62577614"},
    {"name": "Masjid Pulau Bukom", "address": "Pulau Bukom, Singapore 929292", "lat": 1.2306, "lon": 103.7472, "contact": "62634088"},
    {"name": "Masjid Pusara Aman", "address": "11 Lim Chu Kang Road, Singapore 719452", "lat": 1.4292, "lon": 103.7171, "contact": "67929378"},
    
    # S
    {"name": "Masjid Sallim Mattar", "address": "1 Mattar Road, Singapore 387725", "lat": 1.3235, "lon": 103.8609, "contact": "67492382"},
    {"name": "Sultan Mosque", "address": "3 Muscat Street, Singapore 198833", "lat": 1.3022, "lon": 103.8590, "contact": "62934405"},
    
    # T
    {"name": "Masjid Tasek Utara", "address": "46 Bristol Road, Singapore 219852", "lat": 1.3092, "lon": 103.8386, "contact": "62938351"},
    {"name": "Masjid Tentera Di Raja", "address": "81 Clementi Road, Singapore 129797", "lat": 1.3025, "lon": 103.7661, "contact": "67765612"},
    
    # W
    {"name": "Masjid Wak Tanjong", "address": "25 Paya Lebar Road, Singapore 409004", "lat": 1.3295, "lon": 103.8996, "contact": "67472743"},
    
    # Y
    {"name": "Masjid Yusof Ishak", "address": "10 Woodlands Drive 17, Singapore 737740", "lat": 1.4265, "lon": 103.7961, "contact": "68930093"},
]


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


def is_singapore_location(latitude: float, longitude: float) -> bool:
    """Check if coordinates are within Singapore bounds"""
    # Singapore bounding box: roughly 1.15°N to 1.47°N, 103.6°E to 104.0°E
    return (1.15 <= latitude <= 1.47 and 103.6 <= longitude <= 104.0)


def find_singapore_mosques(latitude: float, longitude: float, limit: int = 5, max_distance_km: float = 10.0) -> Optional[List[Dict]]:
    """
    Find nearest mosques in Singapore from curated dataset
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        limit: Maximum number of results to return
        max_distance_km: Maximum distance in kilometers
    
    Returns:
        List of mosque dictionaries sorted by distance, or None if none found within range
    """
    if not is_singapore_location(latitude, longitude):
        return None
    
    mosques_with_distance = []
    
    for mosque in SINGAPORE_MOSQUES:
        distance = calculate_distance(latitude, longitude, mosque['lat'], mosque['lon'])
        
        if distance <= max_distance_km:
            mosques_with_distance.append({
                'display_name': f"{mosque['name']}, {mosque['address']}",
                'lat': str(mosque['lat']),
                'lon': str(mosque['lon']),
                'distance': distance
            })
    
    # Sort by distance
    mosques_with_distance.sort(key=lambda x: x['distance'])
    
    # Return top N results
    result = mosques_with_distance[:limit]
    return result if result else None
