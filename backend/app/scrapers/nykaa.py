import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from fake_useragent import UserAgent
import logging
import json

logger = logging.getLogger(__name__)

class NykaaScraper:
    def __init__(self):
        self.base_url = "https://www.nykaa.com"
        self.search_url = f"{self.base_url}/search/result"
        self.ua = UserAgent()
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with random user agent for Nykaa"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.nykaa.com/',
        }
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from price text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                return None
        return None
    
    def _clean_title(self, title: str) -> str:
        """Clean product title"""
        if not title:
            return ""
        
        # Remove extra whitespace and common unnecessary text
        title = re.sub(r'\s+', ' ', title.strip())
        title = re.sub(r'(?i)\s*\|\s*nykaa.*$', '', title)
        title = re.sub(r'(?i)\s*-\s*buy.*$', '', title)
        title = re.sub(r'(?i)\s*online.*$', '', title)
        
        return title.strip()
    
    def _extract_product_info(self, product_element) -> Optional[Dict]:
        """Extract product information from product element"""
        try:
            # Try different selectors for Nykaa's structure
            title_selectors = [
                'h3', 'h4', '.product-title', '.item-title', 
                '[data-testid="product-name"]', '.product-name',
                '.css-1qvtqmx', '.css-xrzmfa', '.product-item-name'
            ]
            
            price_selectors = [
                '.price', '.product-price', '[data-testid="price"]',
                '.current-price', '.selling-price', '.item-price',
                '.css-1d0jf8e', '.css-111z9ua', '.final-price'
            ]
            
            image_selectors = [
                'img', '.product-image img', '[data-testid="product-image"]',
                '.css-11gn9r6 img', '.product-img'
            ]
            
            link_selectors = [
                'a', '.product-link', '[data-testid="product-link"]',
                '.css-qlopj4'
            ]
            
            # Extract title
            title = None
            for selector in title_selectors:
                title_elem = product_element.select_one(selector)
                if title_elem:
                    title = self._clean_title(title_elem.get_text(strip=True))
                    if title and len(title) > 5:  # Ensure meaningful title
                        break
            
            if not title:
                return None
            
            # Extract price
            price = None
            for selector in price_selectors:
                price_elem = product_element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price(price_text)
                    if price and price > 0:
                        break
            
            # Extract image
            image_url = None
            for selector in image_selectors:
                img_elem = product_element.select_one(selector)
                if img_elem:
                    image_url = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
                    if image_url and not image_url.startswith('http'):
                        image_url = f"{self.base_url}{image_url}" if image_url.startswith('/') else None
                    break
            
            # Extract product link
            product_link = None
            for selector in link_selectors:
                link_elem = product_element.select_one(selector)
                if link_elem:
                    href = link_elem.get('href')
                    if href:
                        product_link = href if href.startswith('http') else f"{self.base_url}{href}"
                        break
            
            # Only return if we have essential information
            if title and (price or price == 0):
                return {
                    'title': title,
                    'price': price,
                    'image_url': image_url,
                    'product_url': product_link or f"{self.base_url}/search/result/?q={title.replace(' ', '%20')}"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting Nykaa product info: {e}")
            return None
    
    async def search_product(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for products on Nykaa"""
        try:
            logger.info(f"Searching Nykaa for: {query}")
            
            # Prepare search parameters
            params = {
                'q': query,
                'sort': 'popularity'
            }
            
            headers = self._get_headers()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                
                # Make search request
                async with session.get(
                    self.search_url,
                    params=params,
                    headers=headers
                ) as response:
                    
                    if response.status == 403:
                        logger.warning("Nykaa search failed with status 403 (blocked)")
                        return []
                    elif response.status == 429:
                        logger.warning("Nykaa search failed with status 429 (rate limited)")
                        return []
                    elif response.status != 200:
                        logger.warning(f"Nykaa search failed with status {response.status}")
                        return []
                    
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Try different product container selectors for Nykaa
                    product_selectors = [
                        '.product-card', '.item-card', '.product-item',
                        '[data-testid="product-card"]', '.search-result-item',
                        '.product', '.item', '.listing-item',
                        '.css-xrzmfa', '.css-1qvtqmx'
                    ]
                    
                    products = []
                    for selector in product_selectors:
                        product_elements = soup.select(selector)
                        if product_elements:
                            logger.info(f"Found {len(product_elements)} products with selector: {selector}")
                            break
                    else:
                        # Fallback: look for any div with product-like attributes
                        product_elements = soup.find_all('div', class_=re.compile(r'product|item|card', re.I))
                        logger.info(f"Fallback: Found {len(product_elements)} potential product elements")
                    
                    # Extract product information
                    for element in product_elements[:max_results * 2]:  # Get more to filter better results
                        product_info = self._extract_product_info(element)
                        if product_info:
                            products.append(product_info)
                            
                        if len(products) >= max_results:
                            break
                    
                    logger.info(f"Successfully extracted {len(products)} products from Nykaa")
                    return products[:max_results]
                    
        except asyncio.TimeoutError:
            logger.error("Nykaa search timed out")
            return []
        except Exception as e:
            logger.error(f"Error searching Nykaa: {e}")
            return []

# Create global instance
nykaa_scraper = NykaaScraper()
