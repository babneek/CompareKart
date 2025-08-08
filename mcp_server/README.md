# CompareKart MCP Server

🚀 **AI-powered price comparison tool for Puch AI ecosystem**

CompareKart MCP Server brings comprehensive Indian e-commerce price comparison directly to Puch AI users through the Model Context Protocol (MCP). Find the best deals across major platforms like Amazon, JioMart, Zepto, Instamart, Purplle, Tira, and Mamaearth with intelligent category-based filtering.

## 🌟 Features

- **Multi-Platform Price Comparison**: Search across 7+ major Indian e-commerce platforms
- **Category-Based Filtering**: Target specific product categories (Beauty, Grocery, Fashion, Quick Commerce)
- **AI-Powered Product Matching**: Intelligent matching of similar products across platforms
- **Best Deal Identification**: Automatically find the lowest prices and calculate savings
- **Real-Time Results**: Live scraping with concurrent platform searches
- **Direct Purchase Links**: Get direct links to buy products on each platform

## 🛠 Supported Platforms

### General E-commerce
- **Amazon India** - Wide product range
- **JioMart** - Reliance's e-commerce platform

### Beauty & Personal Care
- **Purplle** - Beauty and cosmetics specialist
- **Tira** - Reliance's premium beauty platform
- **Mamaearth** - Natural and organic products
- **Amazon** - Beauty section

### Quick Commerce
- **Zepto** - 10-minute grocery delivery
- **Instamart** - Swiggy's instant delivery

### Groceries & Food
- **JioMart** - Grocery and essentials
- **Amazon** - Pantry and grocery items

## 🔧 MCP Tools Available

### 1. `compare_product_prices`
Compare prices of a product across multiple platforms with category filtering.

**Parameters:**
- `product_name` (required): Product to search for
- `category` (optional): Filter by category (general, beauty, grocery, fashion, quick_commerce)
- `platforms` (optional): Comma-separated list of specific platforms
- `max_results` (optional): Maximum results per platform (default: 5)

**Example:**
```json
{
  "tool": "compare_product_prices",
  "parameters": {
    "product_name": "Lakme lipstick",
    "category": "beauty",
    "max_results": 3
  }
}
```

### 2. `get_available_platforms`
Get list of all available platforms organized by category.

### 3. `get_platform_categories`
Get list of all product categories and their associated platforms.

### 4. `find_best_deal`
Find the absolute best deal for a specific product across all platforms.

**Parameters:**
- `product_name` (required): Product to find best deal for
- `category` (optional): Filter by category

## 🚀 Deployment

### Railway Deployment (Recommended)

1. **Connect GitHub Repository**
   ```bash
   # Push your code to GitHub
   git add .
   git commit -m "Add CompareKart MCP Server"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Select the `mcp_server` directory
   - Railway will auto-detect FastAPI and deploy

3. **Configure Environment**
   - Set `PORT=8001` in Railway environment variables
   - Update `config.json` with your deployed URL

### Alternative: Render Deployment

1. **Create Render Account**
   - Go to [Render.com](https://render.com)
   - Connect GitHub repository

2. **Configure Web Service**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.11+

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server
python server.py

# Server will be available at:
# HTTP: http://localhost:8001
# WebSocket: ws://localhost:8001/mcp
```

## 📝 Registering with Puch AI

1. **Update config.json**
   ```json
   {
     "entrypoint": "wss://your-deployed-server.com/mcp"
   }
   ```

2. **Submit to Puch AI**
   - Go to Puch AI MCP Server Submission page
   - Submit your `config.json` URL
   - Wait for approval and testing

3. **Monitor Usage**
   - Track usage on Puch AI's public leaderboard
   - Monitor server logs for performance

## 🔍 Usage Examples

### Through Puch AI Chat

**Find best beauty deals:**
```
"Find the cheapest Lakme lipstick across beauty platforms"
```

**Compare grocery prices:**
```
"Compare prices for Maggi noodles on grocery platforms"
```

**Get platform information:**
```
"Show me all available e-commerce platforms by category"
```

## 📊 Response Format

```json
{
  "success": true,
  "query": "iPhone 15",
  "platforms_searched": ["Amazon", "JioMart"],
  "total_products_found": 8,
  "best_deal": {
    "title": "Apple iPhone 15 128GB",
    "price": 79999,
    "platform": "Amazon",
    "url": "https://amazon.in/...",
    "rating": 4.5
  },
  "total_savings": 5000,
  "matched_groups": [...],
  "all_products": [...]
}
```

## 🛡 Error Handling

The MCP server includes comprehensive error handling:
- Platform timeout protection
- Anti-scraping detection and fallbacks
- Invalid parameter validation
- Graceful degradation when platforms are unavailable

## 🏆 Hackathon Integration

This MCP server is designed for Puch AI's hackathon:
- **Leaderboard Tracking**: Usage automatically tracked
- **Public Directory**: Listed in Puch's MCP directory
- **Real-time Monitoring**: Server health and connection metrics
- **Scalable Architecture**: Handles multiple concurrent users

## 📞 Support

For issues or questions:
- Check server health at `/health` endpoint
- Monitor logs for debugging
- Ensure all scrapers are functioning properly

---

**Built for Puch AI Hackathon 2024** 🚀
*Bringing the power of CompareKart to the Puch AI ecosystem*
