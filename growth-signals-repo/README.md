# 🚀 Growth Signals Dashboard

AI-powered B2B growth intelligence platform for identifying high-intent prospects through social media analysis.

![Growth Signals Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![React](https://img.shields.io/badge/React-19.0.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.1-green)
![MongoDB](https://img.shields.io/badge/MongoDB-4.5.0-green)

## ✨ Features

- **AI-Powered Intent Analysis**: GPT-4 powered detection of 30+ B2B growth signals
- **Real-time Social Monitoring**: Live Twitter/X integration for GTM activities
- **Smart Lead Scoring**: Automatic lead prioritization (0-10 scale)
- **Advanced Filtering**: Role, geography, priority, and score-based filtering
- **Market Intelligence**: Real-time financial market data
- **Responsive Design**: Mobile-optimized professional UI
- **Custom Targeting**: AI analysis of custom prospect profiles

## 🏗️ Architecture

```
growth-signals/
├── frontend/          # React.js dashboard
├── backend/           # FastAPI server
├── docs/             # Documentation
└── deployment/       # Deployment configs
```

## 🚀 Quick Deploy

### Option A: Vercel + Railway (5 minutes)

1. **Frontend (Vercel):**
   ```bash
   cd frontend
   npm install
   npm run build
   # Deploy build/ folder to Vercel
   ```

2. **Backend (Railway):**
   ```bash
   cd backend
   # Deploy to Railway with environment variables
   ```

### Option B: Your Domain (silverbirchgrowth.com)

1. **Frontend:**
   ```bash
   cd frontend && npm run build
   # Upload build/ to https://signals.silverbirchgrowth.com/
   ```

2. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8001
   ```

## ⚙️ Environment Variables

### Frontend (.env)
```
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=growth_signals
OPENAI_API_KEY=sk-proj-your-key
TWITTER_BEARER_TOKEN=your-twitter-token
```

## 📊 API Endpoints

- `GET /api/leads` - Get filtered leads
- `GET /api/live-tweets` - Real-time Twitter signals  
- `GET /api/cached-tweets` - Cached tweet data
- `GET /api/startup-news` - Curated news
- `GET /api/market-data` - Financial market data
- `GET /api/stats` - Dashboard statistics
- `POST /api/analyze-content` - AI content analysis

## 🛠️ Development

### Frontend
```bash
cd frontend
npm install
npm start
# Runs on http://localhost:3000
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
# Runs on http://localhost:8001
```

## 🎯 Integration Guide

### Adding New Intent Signals
Edit `backend/server.py`:
```python
INTENT_SIGNALS = [
    "Your New Signal",
    # ... existing signals
]
```

### Custom Lead Sources
Modify `FALLBACK_LEADS` in `backend/server.py` with your data.

### Branding Customization
Update logo and colors in `frontend/src/App.js` and `frontend/src/App.css`.

## 🔐 Security

- API keys stored in environment variables
- CORS configured for production domains
- Input validation on all endpoints
- Rate limiting on AI analysis endpoints

## 📈 Performance

- Progressive loading (critical data first)
- Cached tweet data for instant display
- Debounced search and filters
- Optimized API response sizes
- Loading states for all async operations

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd frontend && npm test
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Support

For questions or support:
- Email: hello@silverbirchgrowth.com
- Website: https://silverbirchgrowth.com
- Issues: Create GitHub issue

---

**Built with ❤️ by Silver Birch Growth**