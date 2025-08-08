from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.scrapers.amazon import AmazonScraper
from app.scrapers.zepto import ZeptoScraper
from app.scrapers.instamart import InstamartScraper
from app.scrapers.jiomart import JioMartScraper
from app.scrapers.myntra import MyntraScraper
from app.scrapers.bigbasket import BigBasketScraper
from app.scrapers.snapdeal import SnapdealScraper
from app.scrapers.purplle import PurplleScraper
from app.ai.matcher import ProductMatcher
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize scraper instances (added Purplle for beauty category)
amazon_scraper = AmazonScraper()
zepto_scraper = ZeptoScraper()
instamart_scraper = InstamartScraper()
jiomart_scraper = JioMartScraper()
myntra_scraper = MyntraScraper()
bigbasket_scraper = BigBasketScraper()
snapdeal_scraper = SnapdealScraper()
purplle_scraper = PurplleScraper()
product_matcher = ProductMatcher()

# Platform categories configuration (added Purplle to beauty category)
PLATFORM_CATEGORIES = {
    "general": {
        "name": "General E-commerce",
        "description": "Electronics, Books, General Items",
        "platforms": ["amazon", "snapdeal", "jiomart"],
        "icon": "🛒"
    },
    "fashion": {
        "name": "Fashion & Lifestyle", 
        "description": "Clothing, Accessories, Footwear",
        "platforms": ["myntra", "amazon", "snapdeal"],
        "icon": "👕"
    },
    "beauty": {
        "name": "Beauty & Personal Care",
        "description": "Cosmetics, Skincare, Personal Care",
        "platforms": ["purplle", "amazon"],
        "icon": "💄"
    },
    "grocery": {
        "name": "Groceries & Food",
        "description": "Food Items, Household Essentials",
        "platforms": ["bigbasket", "jiomart", "amazon"],
        "icon": "🥬"
    },
    "quick_commerce": {
        "name": "Quick Commerce",
        "description": "10-30 min delivery",
        "platforms": ["zepto", "instamart"],
        "icon": "⚡"
    }
}

# Scraper mapping (added Purplle)
SCRAPERS = {
    "amazon": amazon_scraper,
    "zepto": zepto_scraper,
    "instamart": instamart_scraper,
    "jiomart": jiomart_scraper,
    "myntra": myntra_scraper,
    "bigbasket": bigbasket_scraper,
    "snapdeal": snapdeal_scraper,
    "purplle": purplle_scraper
}

@router.get("/categories")
async def get_categories():
    """Get all available platform categories"""
    return {
        "categories": PLATFORM_CATEGORIES,
        "total": len(PLATFORM_CATEGORIES)
    }

@router.get("/compare")
async def compare_prices(
    product: str = Query(..., description="Product name to search for"),
    category: Optional[str] = Query(None, description="Category to filter platforms"),
    platforms: Optional[str] = Query(None, description="Comma-separated list of platforms"),
    max_results: int = Query(5, description="Maximum results per platform")
):
    try:
        # Determine which platforms to search
        selected_platforms = []
        
        if platforms:
            # User specified specific platforms
            selected_platforms = [p.strip().lower() for p in platforms.split(",")]
        elif category and category in PLATFORM_CATEGORIES:
            # User selected a category
            selected_platforms = PLATFORM_CATEGORIES[category]["platforms"]
        else:
            # Default: search all platforms
            selected_platforms = list(SCRAPERS.keys())
        
        # Filter to only available scrapers
        available_platforms = [p for p in selected_platforms if p in SCRAPERS]
        
        if not available_platforms:
            raise HTTPException(status_code=400, detail="No valid platforms specified")
        
        logger.info(f"Searching platforms: {available_platforms} for product: {product}")
        
        # Create search tasks for selected platforms
        search_tasks = []
        platform_names = []
        
        for platform in available_platforms:
            if platform in SCRAPERS:
                search_tasks.append(SCRAPERS[platform].search_product(product, max_results))
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
        
        # Process matched groups for response
        comparison_results = []
        best_overall_deal = None
        total_savings = 0
        
        if matched_groups:
            for group in matched_groups:
                comparison_results.append({
                    'product_name': group['title'],
                    'platforms': group['platforms'],
                    'price_stats': group['price_stats'],
                    'best_deal': group['best_deal'],
                    'savings_amount': group['price_stats']['savings'],
                    'savings_percentage': product_matcher.calculate_savings_percentage(
                        group['price_stats']['min_price'], 
                        group['price_stats']['max_price']
                    )
                })
                
                # Track best overall deal
                if group['best_deal'] and (not best_overall_deal or 
                    group['best_deal']['price'] < best_overall_deal['price']):
                    best_overall_deal = group['best_deal']
                
                total_savings += group['price_stats']['savings'] or 0
        
        # If no matches found, return individual products
        if not comparison_results and all_products:
            # Group results by platform
            platform_grouped = {}
            for platform in platform_names:
                platform_grouped[platform.title()] = [
                    p for p in all_products if p.get('platform', '').lower() == platform
                ]
            
            comparison_results = [{
                'product_name': f"Search results for '{product}'",
                'platforms': platform_grouped,
                'individual_products': all_products,
                'note': 'No similar products found across platforms'
            }]
            
            # Find best individual deal
            if all_products:
                best_overall_deal = min(all_products, key=lambda x: x.get('price', float('inf')))
        
        return {
            "query": product,
            "category": category,
            "selected_platforms": available_platforms,
            "timestamp": datetime.now().isoformat(),
            "total_comparisons": len(comparison_results),
            "platforms_searched": [p.title() for p in available_platforms],
            "platform_results": platform_results,
            "comparisons": comparison_results,
            "best_overall_deal": best_overall_deal,
            "total_savings": round(total_savings, 2),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error comparing prices: {e}")
        raise HTTPException(status_code=500, detail=f"Error comparing prices: {str(e)}")

@router.get("/search/{platform}")
async def search_platform(
    platform: str,
    product: str = Query(..., description="Product name to search for"),
    max_results: int = Query(5, description="Maximum results to return")
):
    """Search for products on a specific platform"""
    try:
        platform = platform.lower()
        
        if platform not in SCRAPERS:
            available_platforms = list(SCRAPERS.keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported platform: {platform}. Available: {available_platforms}"
            )
        
        results = await SCRAPERS[platform].search_product(product, max_results)
        
        # Add platform identifier to results
        for result in results:
            result['platform'] = platform.title()
        
        return {
            "platform": platform.title(),
            "query": product,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching {platform}: {str(e)}")

@router.get("/platforms")
async def get_platforms():
    """Get list of supported platforms with category information"""
    platforms_info = []
    
    for platform_id, scraper in SCRAPERS.items():
        # Find which categories this platform belongs to
        categories = []
        for cat_id, cat_info in PLATFORM_CATEGORIES.items():
            if platform_id in cat_info["platforms"]:
                categories.append({
                    "id": cat_id,
                    "name": cat_info["name"],
                    "icon": cat_info["icon"]
                })
        
        platforms_info.append({
            "name": platform_id.title(),
            "id": platform_id,
            "categories": categories,
            "status": "active"
        })
    
    return {
        "platforms": platforms_info,
        "total": len(platforms_info),
        "categories": PLATFORM_CATEGORIES
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "platforms_available": len(SCRAPERS),
        "categories_available": len(PLATFORM_CATEGORIES)
    }

@router.get("/test-scrapers")
async def test_scrapers():
    """Test all scrapers with a sample query"""
    test_query = "iPhone"
    results = {}
    
    for platform_id, scraper in SCRAPERS.items():
        try:
            test_results = await scraper.search_product(test_query, 2)
            results[platform_id] = {
                "status": "success",
                "count": len(test_results),
                "sample": test_results[:1] if test_results else []
            }
        except Exception as e:
            results[platform_id] = {
                "status": "error",
                "error": str(e)
            }
    
    return {
        "test_query": test_query,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
