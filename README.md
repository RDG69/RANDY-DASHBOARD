# 🚀 Growth Signals Dashboard

AI-powered B2B growth intelligence platform for identifying high-intent prospects through social media analysis.

[![Deploy Backend](https://railway.app/button.svg)](https://railway.app/template/F4jZcr)
[![Deploy Frontend](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/growth-signals)

## ✨ Features

- **AI-Powered Intent Analysis**: GPT-4 powered detection of 30+ B2B growth signals
- **Real-time Social Monitoring**: Live Twitter/X integration for GTM activities  
- **Smart Lead Scoring**: Automatic lead prioritization (0-10 scale)
- **Advanced Filtering**: Role, geography, priority, and score-based filtering
- **Market Intelligence**: Real-time financial market data
- **Responsive Design**: Mobile-optimized professional UI

## 🚀 Quick Deploy (5 minutes)

### Option A: One-Click Deploy
1. Click "Deploy Backend" → Add environment variables
2. Click "Deploy Frontend" → Add backend URL  
3. **LIVE!** 🎉

### Option B: Your Domain
```bash
# Frontend
cd frontend && npm install && npm run build
# Upload build/ to signals.silverbirchgrowth.com

# Backend  
cd backend && pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8001
```

## ⚙️ Environment Variables

### Backend
```
OPENAI_API_KEY=your-openai-key
TWITTER_BEARER_TOKEN=your-twitter-token  
MONGO_URL=mongodb://localhost:27017
```

### Frontend
```
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

## 📊 Live Demo

**Current Demo:** https://bcfadc05-47d4-4401-8547-56a7e2fbdcc1.preview.emergentagent.com

---

**Built with ❤️ by Silver Birch Growth**
