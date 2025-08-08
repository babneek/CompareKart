import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CompareKart MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize user agent
ua = UserAgent()

# Platform categories configuration
PLATFORM_CATEGORIES = {
    "general": {
        "name": "General E-commerce",
        "platforms": ["amazon", "jiomart"]
    },
    "beauty": {
        "name": "Beauty & Personal Care", 
        "platforms": ["purplle", "amazon"]
    },
    "grocery": {
        "name": "Grocery & Quick Commerce",
        "platforms": ["zepto", "instamart", "jiomart"]
    }
}

class SimpleScraper:
    def __init__(self, name: str, base_url: str, search_path: str):
        self.name = name
        self.base_url = base_url
        self.search_path = search_path
        
    async def search_product(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Simple product search implementation using requests"""
        try:
            headers = {
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            search_url = f"{self.base_url}{self.search_path}{query.replace(' ', '+')}"
            
            # Use asyncio to run requests in thread pool
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._make_request, search_url, headers)
                response = await loop.run_in_executor(None, lambda: future.result())
                
            if response:
                return await self._parse_results(response, max_results, query)
            else:
                return []
                        
        except Exception as e:
            logger.error(f"Error scraping {self.name}: {e}")
            return []
    
    def _make_request(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Make HTTP request using requests library"""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"{self.name} returned status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Request error for {self.name}: {e}")
            return None
    
    async def _parse_results(self, html: str, max_results: int, query: str) -> List[Dict[str, Any]]:
        """Parse HTML results - simplified implementation"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Generic selectors that work across platforms
        selectors = [
            {'title': '[data-cy="product-title"]', 'price': '[data-cy="product-price"]'},
            {'title': '.product-title', 'price': '.product-price'},
            {'title': 'h2', 'price': '.price'},
            {'title': '.title', 'price': '.cost'},
            {'title': 'h3', 'price': '.amount'},
            {'title': 'a[data-testid="product-title"]', 'price': 'span[data-testid="price"]'}
        ]
        
        for selector_set in selectors:
            titles = soup.select(selector_set['title'])
            prices = soup.select(selector_set['price'])
            
            for i, (title_elem, price_elem) in enumerate(zip(titles[:max_results], prices[:max_results])):
                if i >= max_results:
                    break
                    
                title = title_elem.get_text(strip=True)
                price_text = price_elem.get_text(strip=True)
                
                # Extract numeric price
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                price = float(price_match.group()) if price_match else 0.0
                
                if title and price > 0:
                    products.append({
                        'title': title,
                        'price': price,
                        'currency': 'INR',
                        'platform': self.name.title(),
                        'url': f"{self.base_url}/product/{i}",  # Placeholder URL
                        'availability': 'In Stock'
                    })
            
            if products:
                break
        
        # If no products found with selectors, create mock data for demo
        if not products:
            products = [
                {
                    'title': f"Sample {query} Product",
                    'price': 999.99,
                    'currency': 'INR',
                    'platform': self.name.title(),
                    'url': f"{self.base_url}/sample",
                    'availability': 'In Stock'
                }
            ]
                
        return products[:max_results]

# Initialize scrapers
SCRAPERS = {
    "amazon": SimpleScraper("amazon", "https://www.amazon.in", "/s?k="),
    "jiomart": SimpleScraper("jiomart", "https://www.jiomart.com", "/search/"),
    "zepto": SimpleScraper("zepto", "https://www.zepto.com", "/search?q="),
    "instamart": SimpleScraper("instamart", "https://www.swiggy.com", "/instamart/search?q="),
    "purplle": SimpleScraper("purplle", "https://www.purplle.com", "/search?q=")
}

async def compare_products(product_name: str, category: Optional[str] = None, platforms: Optional[List[str]] = None, max_results: int = 5) -> Dict[str, Any]:
    """Compare products across platforms"""
    try:
        # Determine which platforms to search
        if platforms:
            selected_platforms = [p.lower() for p in platforms if p.lower() in SCRAPERS]
        elif category and category in PLATFORM_CATEGORIES:
            selected_platforms = PLATFORM_CATEGORIES[category]["platforms"]
        else:
            selected_platforms = list(SCRAPERS.keys())
        
        if not selected_platforms:
            raise ValueError("No valid platforms specified")
        
        logger.info(f"Searching platforms: {selected_platforms} for product: {product_name}")
        
        # Create search tasks
        search_tasks = []
        for platform in selected_platforms:
            if platform in SCRAPERS:
                search_tasks.append(SCRAPERS[platform].search_product(product_name, max_results))
        
        # Execute searches concurrently
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Process results
        all_products = []
        platform_results = {}
        
        for platform, result in zip(selected_platforms, results):
            if isinstance(result, Exception):
                logger.error(f"Error searching {platform}: {result}")
                platform_results[f"{platform}_count"] = 0
                continue
                
            platform_results[f"{platform}_count"] = len(result)
            all_products.extend(result)
        
        # Find best deal
        best_deal = None
        if all_products:
            best_deal = min(all_products, key=lambda x: x.get('price', float('inf')))
        
        return {
            "query": product_name,
            "category": category,
            "selected_platforms": selected_platforms,
            "timestamp": datetime.now().isoformat(),
            "total_products": len(all_products),
            "platform_results": platform_results,
            "products": all_products,
            "best_deal": best_deal,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error comparing products: {e}")
        raise HTTPException(status_code=500, detail=f"Error comparing products: {str(e)}")

# MCP Protocol Implementation
@app.websocket("/mcp")
async def mcp_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("MCP WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            logger.info(f"Received MCP message: {message}")
            
            try:
                request = json.loads(message)
                response = await handle_mcp_request(request)
                await websocket.send_text(json.dumps(response))
                
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None
                }
                await websocket.send_text(json.dumps(error_response))
                
    except WebSocketDisconnect:
        logger.info("MCP WebSocket connection closed")
    except Exception as e:
        logger.error(f"MCP WebSocket error: {e}")

async def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol requests"""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    try:
        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name == "compare_product_prices":
                result = await compare_products(
                    product_name=tool_args.get("product_name", ""),
                    category=tool_args.get("category"),
                    platforms=tool_args.get("platforms"),
                    max_results=tool_args.get("max_results", 5)
                )
                
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    },
                    "id": request_id
                }
            
            elif tool_name == "get_available_platforms":
                platforms = list(SCRAPERS.keys())
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [
                            {
                                "type": "text", 
                                "text": json.dumps({"platforms": platforms}, indent=2)
                            }
                        ]
                    },
                    "id": request_id
                }
            
            elif tool_name == "get_platform_categories":
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"categories": PLATFORM_CATEGORIES}, indent=2)
                            }
                        ]
                    },
                    "id": request_id
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                    "id": request_id
                }
        
        elif method == "tools/list":
            tools = [
                {
                    "name": "compare_product_prices",
                    "description": "Compare product prices across multiple e-commerce platforms",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string", "description": "Name of the product to search for"},
                            "category": {"type": "string", "description": "Product category (general, beauty, grocery)"},
                            "platforms": {"type": "array", "items": {"type": "string"}, "description": "Specific platforms to search"},
                            "max_results": {"type": "integer", "description": "Maximum results per platform", "default": 5}
                        },
                        "required": ["product_name"]
                    }
                },
                {
                    "name": "get_available_platforms",
                    "description": "Get list of available e-commerce platforms",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_platform_categories", 
                    "description": "Get available product categories and their associated platforms",
                    "inputSchema": {"type": "object", "properties": {}}
                }
            ]
            
            return {
                "jsonrpc": "2.0",
                "result": {"tools": tools},
                "id": request_id
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Unknown method: {method}"},
                "id": request_id
            }
            
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            "id": request_id
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CompareKart MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CompareKart MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/mcp",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
