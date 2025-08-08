# 🛍️ CompareKart

**"Compare prices. Shop smart. Save more."**

CompareKart is an AI-powered price comparison tool built for the #BuildWithPuch Hackathon that automatically matches products across multiple e-commerce platforms using NLP and provides side-by-side pricing with savings highlights.

## 🚀 Features

- **🧠 AI-Powered Product Matching**: Uses OpenAI embeddings to semantically match products across platforms
- **⚡ Lightning Fast**: Concurrent scraping across Amazon, Flipkart, and Blinkit
- **💰 Smart Savings**: Automatic savings calculation and best deal highlighting
- **🔗 Direct Purchase Links**: One-click access to buy from any platform
- **📱 Modern UI**: Beautiful, responsive React frontend with Tailwind CSS
- **🔍 Smart Search**: Natural language query support

## 🏗️ Architecture

```
User → React App → FastAPI Backend → Web Scrapers
                                 → AI Matcher (OpenAI) → Product Comparison
```

## 🛠️ Tech Stack

### Frontend
- **React 18** with modern hooks
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Router** for navigation
- **Axios** for API calls

### Backend
- **FastAPI** (Python) for high-performance API
- **AsyncIO** for concurrent operations
- **BeautifulSoup & aiohttp** for web scraping
- **OpenAI API** for embeddings and AI matching
- **Pydantic** for data validation

### AI/ML
- **OpenAI Embeddings** (text-embedding-3-small)
- **Scikit-learn** for similarity calculations
- **Semantic search** for product matching

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Backend Setup

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Start the FastAPI server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the React development server**
   ```bash
   npm start
   ```

The app will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 API Endpoints

### Core Endpoints
- `GET /compare?product={query}` - Compare prices across platforms
- `GET /search/{platform}?product={query}` - Search specific platform
- `GET /platforms` - Get supported platforms
- `GET /health` - Health check
- `GET /test-scrapers` - Test scraper functionality

### Example Usage
```bash
# Compare iPhone prices across all platforms
curl "http://localhost:8000/compare?product=iPhone%2015&max_results=5"

# Search only Amazon
curl "http://localhost:8000/search/amazon?product=maggi%20noodles"
```

## 🎯 Supported Platforms

| Platform | Type | Delivery | Status |
|----------|------|----------|--------|
| **Amazon India** | E-commerce | 1-2 days | ✅ Active |
| **Flipkart** | E-commerce | 1-3 days | ✅ Active |
| **Blinkit** | Quick Commerce | 10-30 mins | ✅ Active |

## 🧪 Testing

### Test the API
```bash
# Health check
curl http://localhost:8000/health

# Test scrapers
curl http://localhost:8000/test-scrapers

# Sample product search
curl "http://localhost:8000/compare?product=maggi%20noodles"
```

### Test the Frontend
1. Open http://localhost:3000
2. Search for "iPhone 15" or "Maggi noodles"
3. View comparison results with pricing and savings

## 🚀 Deployment

### Backend (Railway/Fly.io)
```bash
# Using Railway
railway login
railway init
railway up

# Using Fly.io
flyctl auth login
flyctl launch
flyctl deploy
```

### Frontend (Vercel)
```bash
# Using Vercel CLI
npm install -g vercel
vercel --prod

# Or connect GitHub repo to Vercel dashboard
```

## 📊 Project Structure

```
comparekart/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py   # API endpoints
│   │   ├── scrapers/       # Platform scrapers
│   │   │   ├── amazon.py
│   │   │   ├── flipkart.py
│   │   │   └── blinkit.py
│   │   ├── ai/
│   │   │   └── matcher.py  # AI product matching
│   │   └── main.py         # FastAPI app
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── App.js
│   ├── package.json
│   └── tailwind.config.js
├── .env.example
└── README.md
```

## 🎨 UI Screenshots

### Homepage
- Clean, modern design with search functionality
- Popular search suggestions
- Platform badges and feature highlights

### Comparison Results
- Side-by-side price comparison
- Best deal highlighting with savings percentage
- Direct purchase links for each platform
- AI-matched product groupings

## 🔮 Future Enhancements

- **📈 Price History**: Track price trends over time
- **🔔 Price Alerts**: Notify when prices drop
- **🌐 Browser Extension**: Quick price comparison while browsing
- **📱 Mobile App**: Native iOS/Android apps
- **🤖 Telegram Bot**: Price comparison via chat
- **🎯 Personalized Deals**: ML-based deal recommendations

## 🏆 Hackathon Submission

**Event**: #BuildWithPuch Hackathon  
**Category**: AI/ML Application  
**Timeline**: 48 hours (MVP Phase)  

### Key Achievements
- ✅ Working MVP with 3 platform integrations
- ✅ AI-powered semantic product matching
- ✅ Modern, responsive web interface
- ✅ Real-time price comparison
- ✅ Automated savings calculation

## 📝 Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
PINECONE_API_KEY=your_pinecone_key_here
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost/db
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is built for the #BuildWithPuch Hackathon. Feel free to use and modify for educational purposes.

## 🙏 Acknowledgments

- **Puch AI** for hosting the hackathon
- **OpenAI** for powerful embeddings API
- **React & FastAPI** communities for excellent documentation
- **Tailwind CSS** for beautiful, utility-first styling

---

**Built with ❤️ for #BuildWithPuch Hackathon**

*CompareKart - Because every rupee saved is a rupee earned!* 💰
