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
                    # CSV times are in 12-hour format without AM/PM
                    # Subuh and Syuruk are AM (morning prayers)
                    # Zohor and Asar need +12 hours (afternoon prayers)  
                    # Maghrib and Isyak need +12 hours (evening prayers)
                    
                    # Helper function to convert to 24-hour format
                    def convert_to_24h(time_str: str, add_12: bool = False) -> str:
                        try:
                            hour, minute = time_str.split(':')
                            hour = int(hour)
                            if add_12 and hour != 12:
                                hour += 12
                            return f"{hour:02d}:{minute}"
                        except:
                            return time_str
                    
                    timings = {
                        'Fajr': row['Subuh'],  # Already AM
                        'Sunrise': row['Syuruk'],  # Already AM
                        'Dhuhr': convert_to_24h(row['Zohor'], add_12=True),  # Convert to PM
                        'Asr': convert_to_24h(row['Asar'], add_12=True),  # Convert to PM
                        'Maghrib': convert_to_24h(row['Maghrib'], add_12=True),  # Convert to PM
                        'Isha': convert_to_24h(row['Isyak'], add_12=True)  # Convert to PM
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
