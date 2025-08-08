import openai
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
import os
from dotenv import load_dotenv
import asyncio
from sklearn.metrics.pairwise import cosine_similarity
import re

load_dotenv()
logger = logging.getLogger(__name__)

class ProductMatcher:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://openrouter.ai/api/v1"  # OpenRouter endpoint
        )
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "openai/gpt-3.5-turbo"  # OpenRouter model format
        self.similarity_threshold = 0.75  # Minimum similarity score to consider products as matches
        
    def _clean_product_title(self, title: str) -> str:
        """Clean and normalize product title for better matching"""
        if not title:
            return ""
            
        # Convert to lowercase
        title = title.lower()
        
        # Remove common noise words and patterns
        noise_patterns = [
            r'\b(pack of|set of|\d+\s*pack|\d+\s*pcs?)\b',
            r'\b(free delivery|fast delivery|same day delivery)\b',
            r'\b(bestseller|best seller|top rated)\b',
            r'\b(amazon|flipkart|blinkit|zepto|instamart)\b',
            r'\([^)]*\)',  # Remove content in parentheses
            r'\[[^\]]*\]',  # Remove content in square brackets
            r'[^\w\s]',     # Remove special characters except spaces
        ]
        
        for pattern in noise_patterns:
            title = re.sub(pattern, ' ', title)
        
        # Clean up extra spaces
        title = ' '.join(title.split())
        
        return title.strip()
    
    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts - temporarily disabled due to OpenRouter format issues"""
        try:
            logger.info("AI embeddings temporarily disabled - using fallback matching")
            # Return zero embeddings as fallback for now
            return [[0.0] * 1536 for _ in texts]
            
            # TODO: Fix OpenRouter API response format
            # Original code commented out until OpenRouter format is resolved
            """
            # Clean and prepare texts
            clean_texts = [self._clean_product_title(text) for text in texts]
            
            # Get embeddings from OpenRouter
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=clean_texts
            )
            
            # Debug: Log the response type and structure
            logger.info(f"OpenRouter response type: {type(response)}")
            
            # Handle different response types
            embeddings = []
            
            # Check if response is a string (error case)
            if isinstance(response, str):
                logger.error(f"Received string response from OpenRouter: {response[:200]}...")
                return [[0.0] * 1536 for _ in texts]
            
            # Try to access the data attribute safely
            try:
                if hasattr(response, 'data') and response.data:
                    logger.info("Using standard OpenAI response format")
                    embeddings = [item.embedding for item in response.data]
                elif hasattr(response, '__iter__') and not isinstance(response, str):
                    # Response is iterable but not string
                    logger.info("Response is iterable format")
                    for item in response:
                        if hasattr(item, 'embedding'):
                            embeddings.append(item.embedding)
                        elif isinstance(item, dict) and 'embedding' in item:
                            embeddings.append(item['embedding'])
                else:
                    logger.warning(f"Unexpected response format: {type(response)}")
                    # Try to convert response to dict if possible
                    if hasattr(response, '__dict__'):
                        response_dict = response.__dict__
                        logger.info(f"Response dict keys: {list(response_dict.keys())}")
                    
            except AttributeError as attr_error:
                logger.error(f"AttributeError accessing response: {attr_error}")
                logger.error(f"Response object: {response}")
                
            # Fallback if no embeddings extracted
            if not embeddings:
                logger.warning("No embeddings extracted, using fallback zero vectors")
                embeddings = [[0.0] * 1536 for _ in texts]
            
            logger.info(f"Successfully extracted {len(embeddings)} embeddings")
            return embeddings
            """
            
        except Exception as e:
            logger.error(f"Error getting batch embeddings: {e}")
            logger.error(f"Exception type: {type(e)}")
            # Return zero embeddings as fallback
            return [[0.0] * 1536 for _ in texts]
    
    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for a text using OpenAI API"""
        try:
            if not text.strip():
                return None
                
            response = await self._get_embeddings([text])
            
            return response[0]
            
        except Exception as e:
            logger.error(f"Error getting embedding for text '{text}': {e}")
            return None
    
    async def find_similar_products(self, products: List[Dict]) -> List[List[Dict]]:
        """Group similar products together using embeddings"""
        try:
            if not products:
                return []
            
            # Clean titles and get embeddings
            cleaned_titles = [self._clean_product_title(product.get('title', '')) for product in products]
            embeddings = await self._get_embeddings(cleaned_titles)
            
            # Filter out products without embeddings
            valid_products = []
            valid_embeddings = []
            
            for i, (product, embedding) in enumerate(zip(products, embeddings)):
                if embedding is not None:
                    valid_products.append(product)
                    valid_embeddings.append(embedding)
            
            if not valid_products:
                return [[product] for product in products]  # Return individual products if no embeddings
            
            # Group similar products
            grouped_products = []
            used_indices = set()
            
            for i, (product1, embedding1) in enumerate(zip(valid_products, valid_embeddings)):
                if i in used_indices:
                    continue
                
                # Start a new group with this product
                current_group = [product1]
                used_indices.add(i)
                
                # Find similar products
                for j, (product2, embedding2) in enumerate(zip(valid_products, valid_embeddings)):
                    if j in used_indices or i == j:
                        continue
                    
                    similarity = self._calculate_similarity(embedding1, embedding2)
                    
                    if similarity >= self.similarity_threshold:
                        current_group.append(product2)
                        used_indices.add(j)
                
                grouped_products.append(current_group)
            
            return grouped_products
            
        except Exception as e:
            logger.error(f"Error finding similar products: {e}")
            return [[product] for product in products]  # Return individual products on error
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(vec1, vec2)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    async def match_products_across_platforms(self, all_products: List[Dict]) -> List[Dict]:
        """Match products across platforms and return comparison data"""
        try:
            # Group similar products
            product_groups = await self.find_similar_products(all_products)
            
            matched_products = []
            
            for group in product_groups:
                if len(group) <= 1:
                    # Single product, no comparison possible
                    continue
                
                # Create comparison data for this group
                platforms = {}
                for product in group:
                    platform = product.get('platform', 'Unknown')
                    if platform not in platforms:
                        platforms[platform] = []
                    platforms[platform].append(product)
                
                # Only include groups with products from multiple platforms
                if len(platforms) > 1:
                    # Find the best representative title
                    titles = [product.get('title', '') for product in group]
                    representative_title = max(titles, key=len) if titles else "Product Comparison"
                    
                    # Calculate price statistics
                    prices = [product.get('price') for product in group if product.get('price')]
                    min_price = min(prices) if prices else None
                    max_price = max(prices) if prices else None
                    avg_price = sum(prices) / len(prices) if prices else None
                    
                    # Find best deal
                    best_deal = None
                    if prices:
                        best_deal = min(group, key=lambda x: x.get('price', float('inf')))
                    
                    matched_products.append({
                        'title': representative_title,
                        'platforms': platforms,
                        'price_stats': {
                            'min_price': min_price,
                            'max_price': max_price,
                            'avg_price': avg_price,
                            'savings': max_price - min_price if min_price and max_price else 0
                        },
                        'best_deal': best_deal,
                        'total_products': len(group)
                    })
            
            return matched_products
            
        except Exception as e:
            logger.error(f"Error matching products across platforms: {e}")
            return []
    
    def calculate_savings_percentage(self, min_price: float, max_price: float) -> float:
        """Calculate savings percentage"""
        if not min_price or not max_price or max_price == 0:
            return 0.0
        
        return ((max_price - min_price) / max_price) * 100
    
    async def smart_search_query_parser(self, query: str) -> Dict:
        """Parse natural language queries into structured filters"""
        try:
            # Use OpenAI to parse the query
            system_prompt = """
            You are a smart query parser for an e-commerce price comparison tool.
            Parse the user's natural language query and extract:
            1. Product name/category
            2. Price range (if mentioned)
            3. Brand preferences
            4. Any other filters
            
            Return a JSON object with these fields:
            - product: main product/category
            - max_price: maximum price if mentioned
            - min_price: minimum price if mentioned  
            - brand: preferred brand if mentioned
            - keywords: additional relevant keywords
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this query: {query}"}
                ],
                temperature=0.1
            )
            
            # Try to parse the JSON response
            import json
            try:
                parsed_query = json.loads(response.choices[0].message.content)
                return parsed_query
            except json.JSONDecodeError:
                # Fallback to simple parsing
                return {
                    "product": query,
                    "max_price": None,
                    "min_price": None,
                    "brand": None,
                    "keywords": [query]
                }
                
        except Exception as e:
            logger.error(f"Error parsing smart query: {e}")
            return {
                "product": query,
                "max_price": None,
                "min_price": None,
                "brand": None,
                "keywords": [query]
            }
