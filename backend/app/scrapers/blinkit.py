import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

class BlinkitScraper:
    def __init__(self):
        self.base_url = "https://blinkit.com"
        self.search_url = f"{self.base_url}/search"
        self.ua = UserAgent()
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with random user agent"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from price text"""
        if not price_text:
            return None
            
        # Remove currency symbols and commas
        price_clean = re.sub(r'[₹,\s]', '', price_text)
        
        # Extract numeric value
        price_match = re.search(r'(\d+(?:\.\d{2})?)', price_clean)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                return None
        return None
    
    def _parse_product(self, product_element) -> Optional[Dict]:
        """Parse individual product from search results"""
        try:
            # Extract title
            title_element = product_element.find('div', class_='Product__UpdatedTitle') or \
                          product_element.find('div', class_='plp-product__name')
            
            title = title_element.get_text(strip=True) if title_element else "Unknown Product"
            
            # Extract price
            price_element = product_element.find('div', class_='Product__UpdatedPrice') or \
                          product_element.find('div', class_='plp-product__price')
            
            price_text = price_element.get_text(strip=True) if price_element else ""
            price = self._extract_price(price_text)
            
            # Extract product URL
            link_element = product_element.find('a')
            product_url = ""
            if link_element and link_element.get('href'):
                href = link_element['href']
                product_url = self.base_url + href if href.startswith('/') else href
            
            # Extract image
            img_element = product_element.find('img')
            image_url = img_element.get('src', '') if img_element else ""
            
            # For Blinkit, rating and reviews are less common
            rating = None
            reviews_count = 0
            
            if price is None:
                return None
                
            return {
                'title': title,
                'price': price,
                'currency': 'INR',
                'url': product_url,
                'image': image_url,
                'rating': rating,
                'reviews_count': reviews_count,
                'availability': 'In Stock',
                'delivery_info': '10-30 mins'  # Blinkit's quick delivery
            }
            
        except Exception as e:
            logger.error(f"Error parsing Blinkit product: {e}")
            return None
    
    async def search_product(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for products on Blinkit"""
        try:
            params = {
                'q': query
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.search_url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Blinkit search failed with status {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find product containers
                    products = []
                    product_containers = soup.find_all('div', class_='Product__UpdatedC') or \
                                       soup.find_all('div', class_='plp-product')
                    
                    for container in product_containers[:max_results]:
                        product_data = self._parse_product(container)
                        if product_data:
                            products.append(product_data)
                    
                    logger.info(f"Found {len(products)} products on Blinkit for query: {query}")
                    return products
                    
        except asyncio.TimeoutError:
            logger.error("Blinkit search timeout")
            return []
        except Exception as e:
            logger.error(f"Error searching Blinkit: {e}")
            return []
    
    async def get_product_details(self, product_url: str) -> Optional[Dict]:
        """Get detailed product information from product page"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    product_url,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract detailed information
                    title_element = soup.find('h1', class_='pdp-product-name')
                    title = title_element.get_text(strip=True) if title_element else "Unknown Product"
                    
                    price_element = soup.find('div', class_='pdp-price')
                    price_text = price_element.get_text(strip=True) if price_element else ""
                    price = self._extract_price(price_text)
                    
                    return {
                        'title': title,
                        'price': price,
                        'currency': 'INR',
                        'url': product_url,
                        'platform': 'Blinkit'
                    }
                    
        except Exception as e:
            logger.error(f"Error getting Blinkit product details: {e}")
            return None
