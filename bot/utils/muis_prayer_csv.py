"""MUIS Prayer Times CSV Reader - Official MUIS Data"""

import csv
import logging
from datetime import datetime
from typing import Optional, Dict
import os

logger = logging.getLogger(__name__)


def get_prayer_times_from_csv(date: Optional[datetime] = None) -> Optional[Dict[str, str]]:
    """
    Get prayer times from the official MUIS CSV file
    
    Args:
        date: The date to get prayer times for (defaults to today)
    
    Returns:
        Dictionary with prayer times or None if not found
    """
    if date is None:
        date = datetime.now()
    
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
                    timings = {
                        'Fajr': row['Subuh'],
                        'Sunrise': row['Syuruk'],
                        'Dhuhr': row['Zohor'],
                        'Asr': row['Asar'],
                        'Maghrib': row['Maghrib'],
                        'Isha': row['Isyak']
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
        date: The date (defaults to today)
    
    Returns:
        Formatted date string
    """
    if date is None:
        date = datetime.now()
    
    return date.strftime("%d %b %Y")
