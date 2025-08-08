import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the backend directory to Python path to import CompareKart modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.api.routes import compare_prices, get_categories, get_platforms
from app.scrapers.amazon import amazon_scraper
from app.scrapers.jiomart import jiomart_scraper
from app.scrapers.zepto import zepto_scraper
from app.scrapers.instamart import instamart_scraper
from app.scrapers.purplle import purplle_scraper
from app.scrapers.tira import tira_scraper
from app.scrapers.mamaearth import mamaearth_scraper
from app.utils.ai_matcher import product_matcher

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

# Available scrapers mapping
SCRAPERS = {
    "amazon": amazon_scraper,
    "jiomart": jiomart_scraper,
    "zepto": zepto_scraper,
    "instamart": instamart_scraper,
    "purplle": purplle_scraper,
    "tira": tira_scraper,
    "mamaearth": mamaearth_scraper,
}

# Platform categories
PLATFORM_CATEGORIES = {
    "general": {
        "name": "General E-commerce",
        "platforms": ["amazon", "jiomart"]
    },
    "beauty": {
        "name": "Beauty & Personal Care", 
        "platforms": ["purplle", "tira", "mamaearth", "amazon"]
    },
    "grocery": {
        "name": "Groceries & Food",
        "platforms": ["jiomart", "amazon"]
    },
    "quick_commerce": {
        "name": "Quick Commerce",
        "platforms": ["zepto", "instamart"]
    }
}

class MCPServer:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New MCP client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"MCP client disconnected. Total connections: {len(self.active_connections)}")
    
    async def handle_tool_request(self, request_data: dict) -> dict:
        """Handle tool requests from Puch AI"""
        try:
            tool_name = request_data.get("tool")
            parameters = request_data.get("parameters", {})
            
            if tool_name == "compare_product_prices":
                return await self.compare_product_prices(parameters)
            elif tool_name == "get_available_platforms":
                return await self.get_available_platforms()
            elif tool_name == "get_platform_categories":
                return await self.get_platform_categories()
            elif tool_name == "find_best_deal":
                return await self.find_best_deal(parameters)
            else:
                return {
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": ["compare_product_prices", "get_available_platforms", "get_platform_categories", "find_best_deal"]
                }
        
        except Exception as e:
            logger.error(f"Error handling tool request: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def compare_product_prices(self, parameters: dict) -> dict:
        """Compare prices across multiple platforms"""
        try:
            product_name = parameters.get("product_name")
            category = parameters.get("category")
            platforms = parameters.get("platforms")
            max_results = parameters.get("max_results", 5)
            
            if not product_name:
                return {"error": "product_name is required"}
            
            # Determine which platforms to search
            selected_platforms = []
            
            if platforms:
                selected_platforms = [p.strip().lower() for p in platforms.split(",")]
            elif category and category in PLATFORM_CATEGORIES:
                selected_platforms = PLATFORM_CATEGORIES[category]["platforms"]
            else:
                selected_platforms = list(SCRAPERS.keys())
            
            # Filter to only available scrapers
            available_platforms = [p for p in selected_platforms if p in SCRAPERS]
            
            if not available_platforms:
                return {"error": "No valid platforms specified"}
            
            logger.info(f"MCP: Searching platforms {available_platforms} for product: {product_name}")
            
            # Create search tasks
            search_tasks = []
            platform_names = []
            
            for platform in available_platforms:
                if platform in SCRAPERS:
                    search_tasks.append(SCRAPERS[platform].search_product(product_name, max_results))
                    platform_names.append(platform)
            
            # Execute searches concurrently
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Process results
            all_products = []
            platform_results = {}
            
            for i, (platform, result) in enumerate(zip(platform_names, results)):
                if isinstance(result, Exception):
                    logger.error(f"Error searching {platform}: {result}")
                    platform_results[f"{platform}_count"] = 0
                    continue
                    
                platform_results[f"{platform}_count"] = len(result)
                
                # Add platform identifier to each product
                for product_data in result:
                    product_data['platform'] = platform.title()
                    all_products.append(product_data)
            
            # Use AI to match similar products across platforms
            if all_products:
                matched_groups = await product_matcher.match_products_across_platforms(all_products)
            else:
                matched_groups = []
            
            # Find best overall deal
            best_deal = None
            total_savings = 0
            
            if all_products:
                best_deal = min(all_products, key=lambda x: x.get('price', float('inf')))
                
                if matched_groups:
                    for group in matched_groups:
                        total_savings += group['price_stats'].get('savings', 0) or 0
            
            return {
                "success": True,
                "query": product_name,
                "category": category,
                "platforms_searched": [p.title() for p in available_platforms],
                "total_products_found": len(all_products),
                "platform_results": platform_results,
                "best_deal": best_deal,
                "total_savings": round(total_savings, 2),
                "matched_groups": matched_groups[:3] if matched_groups else [],  # Limit for MCP response
                "all_products": all_products[:10]  # Limit for MCP response
            }
            
        except Exception as e:
            logger.error(f"Error in compare_product_prices: {e}")
            return {"error": f"Price comparison failed: {str(e)}"}
    
    async def get_available_platforms(self) -> dict:
        """Get list of available platforms organized by category"""
        return {
            "success": True,
            "platforms_by_category": PLATFORM_CATEGORIES,
            "all_platforms": list(SCRAPERS.keys()),
            "total_platforms": len(SCRAPERS)
        }
    
    async def get_platform_categories(self) -> dict:
        """Get list of platform categories"""
        return {
            "success": True,
            "categories": {
                category: {
                    "name": data["name"],
                    "platforms": data["platforms"],
                    "platform_count": len(data["platforms"])
                }
                for category, data in PLATFORM_CATEGORIES.items()
            }
        }
    
    async def find_best_deal(self, parameters: dict) -> dict:
        """Find the absolute best deal for a product"""
        try:
            # Use the same logic as compare_product_prices but focus on best deal
            comparison_result = await self.compare_product_prices(parameters)
            
            if comparison_result.get("success") and comparison_result.get("best_deal"):
                best_deal = comparison_result["best_deal"]
                return {
                    "success": True,
                    "query": parameters.get("product_name"),
                    "best_deal": best_deal,
                    "savings_info": f"Best price found: ₹{best_deal.get('price', 'N/A')} on {best_deal.get('platform', 'Unknown')}",
                    "direct_link": best_deal.get('url', '#')
                }
            else:
                return {
                    "success": False,
                    "error": "No deals found for the specified product"
                }
                
        except Exception as e:
            logger.error(f"Error in find_best_deal: {e}")
            return {"error": f"Best deal search failed: {str(e)}"}

# Create MCP server instance
mcp_server = MCPServer()

@app.websocket("/mcp")
async def websocket_endpoint(websocket: WebSocket):
    """Main MCP WebSocket endpoint for Puch AI"""
    await mcp_server.connect(websocket)
    try:
        while True:
            # Receive request from Puch AI
            data = await websocket.receive_text()
            request = json.loads(data)
            
            logger.info(f"Received MCP request: {request.get('tool', 'unknown')}")
            
            # Process the tool request
            response = await mcp_server.handle_tool_request(request)
            
            # Send response back to Puch AI
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        mcp_server.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        mcp_server.disconnect(websocket)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": "CompareKart MCP Server",
        "version": "1.0.0",
        "status": "active",
        "supported_tools": ["compare_product_prices", "get_available_platforms", "get_platform_categories", "find_best_deal"],
        "active_connections": len(mcp_server.active_connections)
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "scrapers_available": len(SCRAPERS),
        "categories_available": len(PLATFORM_CATEGORIES),
        "mcp_connections": len(mcp_server.active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
