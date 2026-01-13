"""MUIS Prayer Times CSV Reader - Official MUIS Data"""

import csv
import logging
from datetime import datetime
from typing import Optional, Dict
import os
import pytz

logger = logging.getLogger(__name__)

# Singapore timezone
SINGAPORE_TZ = pytz.timezone('Asia/Singapore')


def get_prayer_times_from_csv(date: Optional[datetime] = None) -> Optional[Dict[str, str]]:
    """
    Get prayer times from the official MUIS CSV file
    
    Args:
        date: The date to get prayer times for (defaults to today in Singapore timezone)
    
    Returns:
        Dictionary with prayer times or None if not found
    """
    if date is None:
        date = datetime.now(SINGAPORE_TZ)
    
    # Format date to match CSV format (YYYY-MM-DD)
    date_str = date.strftime("%Y-%m-%d")
    
    # Get path to CSV file (in utils folder alongside this script)
    csv_path = os.path.join(
        os.path.dirname(__file__),
        'MuslimPrayerTimetable2026.csv'
    )
    
    if not os.path.exists(csv_path):
        logger.error(f"MUIS CSV file not found at {csv_path}")
        return None
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                if row['Date'] == date_str:
                    # Map MUIS column names to our expected format
                    # CSV times use 12-hour format: 01:10 = 1:10 PM, 12:59 = 12:59 PM
                    # Need to add 12 to hours 01-11 for afternoon/evening prayers
                    
                    def convert_to_24h(time_str: str) -> str:
                        hour, minute = time_str.split(':')
                        hour = int(hour)
                        if hour < 12:  # 01:xx to 11:xx becomes 13:xx to 23:xx
                            hour += 12
                        return f"{hour:02d}:{minute}"
                    
                    timings = {
                        'Fajr': row['Subuh'],
                        'Sunrise': row['Syuruk'],
                        'Dhuhr': convert_to_24h(row['Zohor']),
                        'Asr': convert_to_24h(row['Asar']),
                        'Maghrib': convert_to_24h(row['Maghrib']),
                        'Isha': convert_to_24h(row['Isyak'])
                    }
                    
                    logger.info(f"Retrieved MUIS prayer times from CSV for {date_str}")
                    return timings
        
        logger.warning(f"Date {date_str} not found in MUIS CSV")
        return None
        
    except Exception as e:
        logger.error(f"Error reading MUIS CSV: {e}")
        return None


def get_readable_date(date: Optional[datetime] = None) -> str:
    """
    Get a human-readable date string
    
    Args:
        date: The date (defaults to today in Singapore timezone)
    
    Returns:
        Formatted date string
    """
    if date is None:
        date = datetime.now(SINGAPORE_TZ)
    
    return date.strftime("%d %b %Y")
