import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

class FlipkartScraper:
    def __init__(self):
        self.base_url = "https://www.flipkart.com"
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
            title_element = product_element.find('div', class_='_4rR01T') or \
                          product_element.find('a', class_='_1fQZEK')
            
            title = title_element.get_text(strip=True) if title_element else "Unknown Product"
            
            # Extract price
            price_element = product_element.find('div', class_='_30jeq3') or \
                          product_element.find('div', class_='_25b18c')
            
            price_text = price_element.get_text(strip=True) if price_element else ""
            price = self._extract_price(price_text)
            
            # Extract product URL
            link_element = product_element.find('a', class_='_1fQZEK') or \
                         product_element.find('a', class_='_2rpwqI')
            product_url = ""
            if link_element and link_element.get('href'):
                product_url = self.base_url + link_element['href']
            
            # Extract image
            img_element = product_element.find('img', class_='_396cs4')
            image_url = img_element.get('src', '') if img_element else ""
            
            # Extract rating
            rating_element = product_element.find('div', class_='_3LWZlK')
            rating = None
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                rating = float(rating_match.group(1)) if rating_match else None
            
            # Extract number of reviews
            reviews_element = product_element.find('span', class_='_2_R_DZ')
            reviews_count = 0
            if reviews_element:
                reviews_text = reviews_element.get_text(strip=True)
                reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
                reviews_count = int(reviews_match.group(1)) if reviews_match else 0
            
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
                'delivery_info': 'Standard Delivery'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Flipkart product: {e}")
            return None
    
    async def search_product(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for products on Flipkart"""
        try:
            params = {
                'q': query,
                'sort': 'relevance'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.search_url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Flipkart search failed with status {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find product containers
                    products = []
                    product_containers = soup.find_all('div', class_='_1AtVbE') or \
                                       soup.find_all('div', class_='_2kHMtA')
                    
                    for container in product_containers[:max_results]:
                        product_data = self._parse_product(container)
                        if product_data:
                            products.append(product_data)
                    
                    logger.info(f"Found {len(products)} products on Flipkart for query: {query}")
                    return products
                    
        except asyncio.TimeoutError:
            logger.error("Flipkart search timeout")
            return []
        except Exception as e:
            logger.error(f"Error searching Flipkart: {e}")
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
                    title_element = soup.find('span', class_='B_NuCI')
                    title = title_element.get_text(strip=True) if title_element else "Unknown Product"
                    
                    price_element = soup.find('div', class_='_30jeq3')
                    price_text = price_element.get_text(strip=True) if price_element else ""
                    price = self._extract_price(price_text)
                    
                    return {
                        'title': title,
                        'price': price,
                        'currency': 'INR',
                        'url': product_url,
                        'platform': 'Flipkart'
                    }
                    
        except Exception as e:
            logger.error(f"Error getting Flipkart product details: {e}")
            return None
