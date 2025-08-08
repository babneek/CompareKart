# 🚀 CompareKart MCP Server - Render Deployment Guide

**Deploy your CompareKart MCP server on Render in 5 minutes!**

## 📋 Prerequisites

- GitHub account
- Render account (free at [render.com](https://render.com))
- Your code pushed to GitHub

## 🛠 Step 1: Push to GitHub

```bash
# Navigate to your project
cd "c:\Users\BABNEEK\OneDrive\Desktop\projects\FLOW AI"

# Add and commit all changes
git add .
git commit -m "Add CompareKart MCP Server for Puch AI"

# Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/comparekart-mcp.git
git branch -M main
git push -u origin main
```

## 🎯 Step 2: Deploy on Render

1. **Go to [render.com](https://render.com)** and sign up/login with GitHub
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository** `comparekart-mcp`
4. **Configure deployment settings:**
   - **Name**: `comparekart-mcp`
   - **Root Directory**: `mcp_server`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (perfect for hackathon)

5. **Click "Create Web Service"**

## ⚡ Step 3: Automatic Deployment

Render will automatically:
- ✅ Detect your `requirements.txt`
- ✅ Install dependencies
- ✅ Start your FastAPI server
- ✅ Provide HTTPS URL
- ✅ Enable auto-deploys on git push

## 🔗 Step 4: Get Your URL

Once deployed, you'll get a URL like:
```
https://comparekart-mcp.onrender.com
```

## 📝 Step 5: Update Config

Update your `config.json` with the Render URL:

```bash
# In your mcp_server directory
python -c "
import json
from pathlib import Path

# Replace with your actual Render URL
render_url = 'https://comparekart-mcp.onrender.com'

config_path = Path('config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# Update WebSocket endpoint
config['entrypoint'] = render_url.replace('https', 'wss') + '/mcp'

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f'✅ Updated config.json with: {config[\"entrypoint\"]}')
"
```

## 🧪 Step 6: Test Your Deployment

```bash
# Test health endpoint (replace with your URL)
curl https://comparekart-mcp.onrender.com/health

# Expected response:
# {"status":"healthy","scrapers_available":7,"categories_available":4}
```

## 🎯 Step 7: Submit to Puch AI

1. **Push updated config.json** to GitHub
2. **Go to Puch AI MCP Server Submission**
3. **Submit your config URL**:
   ```
   https://raw.githubusercontent.com/YOUR_USERNAME/comparekart-mcp/main/mcp_server/config.json
   ```
4. **Wait for approval**
5. **Track usage on leaderboard!**

## 🚀 Why Render is Perfect

- ✅ **Free tier** with 750 hours/month
- ✅ **Automatic HTTPS** and SSL certificates
- ✅ **Auto-deploys** on git push
- ✅ **WebSocket support** for MCP protocol
- ✅ **Built-in monitoring** and logs
- ✅ **Zero configuration** needed

## 🔧 Troubleshooting

**If deployment fails:**
1. Check Render logs in dashboard
2. Ensure `requirements.txt` is in `mcp_server/` directory
3. Verify `server.py` imports work correctly
4. Check that all scraper dependencies are included

**Health check URL:**
```
https://your-app.onrender.com/health
```

**MCP WebSocket endpoint:**
```
wss://your-app.onrender.com/mcp
```

## 🎉 Success!

Your CompareKart MCP server is now live and ready for Puch AI users to discover amazing deals across Indian e-commerce platforms!

**Next:** Submit to Puch AI directory and dominate the hackathon leaderboard! 🏆
