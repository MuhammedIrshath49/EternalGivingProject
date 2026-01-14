"""Google Sheets integration for resources"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Mock data structure until Google Sheets API is integrated
# In production, this would fetch from Google Sheets API
# Resource structure matches Google Sheets: Resource Type | TITLE | Resource Link | File Type
RESOURCES_DATA = {
    "DUA": [
        {"title": "Dua for Parents", "url": "https://www.youtube.com/shorts/7ucoiiJwzuk", "type": "Video"},
        {"title": "Dua when Travelling", "url": "https://youtube.com/shorts/aJkPte7I3Zg?si=eEijFurbHWnmZAvW", "type": "Video"}
    ],
    "Awrad": [
        {"title": "Awrad Zuhooriyah", "url": "https://go.fliplink.me/view/umrah", "type": "PDF"}
    ],
    "Books": [
        {"title": "Umrah Booklet", "url": "https://go.fliplink.me/view/umrah", "type": "PDF"},
        {"title": "Essential Guide to Prayer", "url": "https://go.fliplink.me/view/solat-handbook", "type": "PDF"},
        {"title": "Roses for the Soul Volume 1", "url": "https://go.fliplink.me/view/roses4soul1", "type": "PDF"}
    ],
    "Virtues": [
        {"title": "Laylatul Qadr", "url": "https://go.fliplink.me/view/1A95F1BE-0476-44CC-A9A3-C8077569BB4C", "type": "PDF"},
        {"title": "Laylal Jaizah", "url": "https://go.fliplink.me/view/1A95F1BE-0476-44CC-A9A3-C8077569BB4C", "type": "PDF"}
    ]
}


async def get_resource_categories() -> List[str]:
    """Get list of resource categories"""
    return list(RESOURCES_DATA.keys())


async def get_resources_by_category(category: str) -> List[Dict[str, str]]:
    """Get resources for a specific category
    
    Args:
        category: The resource category (e.g., "Duas", "Awrad", etc.)
        
    Returns:
        List of resource dictionaries with 'title', 'url', and 'type'
    """
    return RESOURCES_DATA.get(category, [])


# TODO: Implement Google Sheets API integration
# Example structure for future implementation:
# 
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# 
# async def fetch_resources_from_sheets(sheet_id: str, range_name: str):
#     """Fetch resources from Google Sheets"""
#     # Set up credentials
#     creds = service_account.Credentials.from_service_account_file(
#         'path/to/credentials.json',
#         scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
#     )
#     
#     # Build service
#     service = build('sheets', 'v4', credentials=creds)
#     sheet = service.spreadsheets()
#     
#     # Fetch data
#     result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
#     values = result.get('values', [])
#     
#     # Parse data (expecting columns: Resource Type | TITLE | Resource Link | File Type)
#     resources = {}
#     for row in values[1:]:  # Skip header row
#         if len(row) >= 4:
#             resource_type = row[0]
#             if resource_type not in resources:
#                 resources[resource_type] = []
#             resources[resource_type].append({
#                 'title': row[1],
#                 'url': row[2],
#                 'type': row[3]
#             })
#     
#     return resources
