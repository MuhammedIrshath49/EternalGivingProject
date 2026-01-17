"""Automated MUIS Khutbah Fetcher

Automatically fetches the latest Friday Khutbah from MUIS website.
No manual download needed!
"""

import logging
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

# MUIS Khutbah page with filters for 2026 English khutbahs
MUIS_KHUTBAH_URL = "https://www.muis.gov.sg/resources/khutbah-and-religious-advice/khutbah/"
MUIS_BASE_URL = "https://www.muis.gov.sg"


async def get_latest_khutbah_pdf_url() -> tuple[bytes | None, str]:
    """
    Automatically fetch the latest Friday Khutbah PDF from MUIS website
    
    Returns:
        Tuple of (PDF bytes, filename) or (None, "") if failed
    """
    try:
        # Headers to mimic a real browser and avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            # Step 1: Fetch the khutbah listing page
            params = {
                'filters': '[{"id":"year","items":[{"id":"2026"}]},{"id":"category","items":[{"id":"english"}]}]',
                'page': '1'
            }
            
            logger.info("Fetching MUIS Khutbah page...")
            async with session.get(MUIS_KHUTBAH_URL, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch MUIS page: HTTP {response.status}")
                    return None, ""
                
                html = await response.text()
            
            # Step 2: Parse HTML to find the latest khutbah
            soup = BeautifulSoup(html, 'html.parser')
            
            logger.debug(f"HTML length: {len(html)} bytes")
            
            # Find the first khutbah article (most recent)
            # Based on the MUIS website structure from screenshot
            khutbah_link = None
            
            # Try multiple selectors to find the khutbah link
            # The website shows article cards with links
            selectors = [
                'article a',
                'a[href*="khutbah"]',
                '.card a',
                '.article-card a',
                'h3 a',
                'h2 a',
                '.title a'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                logger.debug(f"Selector '{selector}' found {len(links)} links")
                if links:
                    for link in links[:10]:  # Check first 10 links with this selector
                        href = link.get('href')
                        logger.debug(f"  Link href: {href}")
                        # Skip directory links, we want article links only
                        if href and 'khutbah' in href.lower():
                            if href.endswith('/khutbah/') or href.endswith('/khutbah') or href == '/resources/khutbah-and-religious-advice/':
                                logger.debug(f"  Skipping directory link: {href}")
                                continue
                            khutbah_link = href
                            break
                if khutbah_link:
                    break
            
            # If specific selectors fail, try finding any link with khutbah in href
            if not khutbah_link:
                all_links = soup.find_all('a', href=True)
                logger.debug(f"Total links on page: {len(all_links)}")
                for link in all_links[:20]:  # Check first 20 links
                    href = link.get('href')
                    # Look for article links (not the main page)
                    # Article links will have more path segments, like: /resources/khutbah-and-religious-advice/khutbah/article-title
                    if href and 'khutbah' in href.lower():
                        # Skip general directory links
                        if href.endswith('/khutbah/') or href.endswith('/khutbah') or href == '/resources/khutbah-and-religious-advice/':
                            continue
                        
                        # Check if the link is associated with English language
                        # Look at the link's parent elements for language indicators
                        parent_text = link.parent.get_text() if link.parent else ""
                        if 'Tamil' in parent_text or 'Malay' in parent_text:
                            logger.debug(f"Skipping non-English khutbah: {href}")
                            continue
                        
                        # Check if there's a language badge/label near the link
                        article_container = link.find_parent(['article', 'div', 'li'])
                        if article_container:
                            container_text = article_container.get_text()
                            if 'Tamil' in container_text and 'English' not in container_text:
                                logger.debug(f"Skipping Tamil khutbah based on container: {href}")
                                continue
                            if 'Malay' in container_text and 'English' not in container_text:
                                logger.debug(f"Skipping Malay khutbah based on container: {href}")
                                continue
                        
                        logger.debug(f"Found potential khutbah link: {href}")
                        khutbah_link = href
                        break
            
            if not khutbah_link:
                logger.error("Could not find khutbah article link on MUIS page")
                logger.debug(f"Sample HTML: {html[:2000]}")
                return None, ""
            
            # Ensure full URL
            if not khutbah_link.startswith('http'):
                khutbah_link = MUIS_BASE_URL + khutbah_link
            
            logger.info(f"Found khutbah page: {khutbah_link}")
            
            # Step 3: Fetch the khutbah detail page
            async with session.get(khutbah_link, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch khutbah detail page: HTTP {response.status}")
                    return None, ""
                
                detail_html = await response.text()
            
            # Step 4: Find the PDF download link
            detail_soup = BeautifulSoup(detail_html, 'html.parser')
            
            # Verify this is an English khutbah
            page_text = detail_soup.get_text()
            if 'Tamil' in page_text and 'English' not in page_text[:1000]:
                logger.warning("Retrieved Tamil khutbah instead of English, skipping")
                return None, ""
            
            # Look for PDF download link
            pdf_link = None
            pdf_selectors = [
                'a[href$=".pdf"]',
                'a[download]',
                '.download-link',
                'a:contains("Download")'
            ]
            
            for selector in pdf_selectors:
                pdf_links = detail_soup.select(selector)
                for link in pdf_links:
                    href = link.get('href')
                    if href and '.pdf' in href.lower():
                        pdf_link = href
                        break
                if pdf_link:
                    break
            
            if not pdf_link:
                logger.error("Could not find PDF download link")
                return None, ""
            
            # Ensure full URL
            if not pdf_link.startswith('http'):
                pdf_link = MUIS_BASE_URL + pdf_link
            
            logger.info(f"Found PDF link: {pdf_link}")
            
            # Step 5: Download the PDF
            async with session.get(pdf_link, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    logger.error(f"Failed to download PDF: HTTP {response.status}")
                    return None, ""
                
                pdf_bytes = await response.read()
            
            # Generate filename
            today = datetime.now()
            filename = f"Friday_Khutbah_{today.strftime('%Y%m%d')}.pdf"
            
            logger.info(f"Successfully downloaded khutbah PDF: {filename} ({len(pdf_bytes)} bytes)")
            return pdf_bytes, filename
            
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching khutbah: {e}")
        return None, ""
    except Exception as e:
        logger.error(f"Unexpected error fetching khutbah: {e}")
        return None, ""


async def get_latest_khutbah_info() -> dict | None:
    """
    Get information about the latest khutbah without downloading
    
    Returns:
        Dictionary with title, date, url, etc. or None if failed
    """
    try:
        # Headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            params = {
                'filters': '[{"id":"year","items":[{"id":"2026"}]},{"id":"category","items":[{"id":"english"}]}]',
                'page': '1'
            }
            
            async with session.get(MUIS_KHUTBAH_URL, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract khutbah info (title, date, etc.)
            # This will depend on the actual MUIS website structure
            info = {
                'title': 'Latest Friday Khutbah',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'MUIS',
                'language': 'English'
            }
            
            return info
            
    except Exception as e:
        logger.error(f"Error getting khutbah info: {e}")
        return None
