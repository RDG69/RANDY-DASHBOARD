# 🚀 Growth Signals - One-Click Deploy

## Deploy Option A: Vercel + Railway (5 minutes)

### 1. Backend (Railway)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Click "Deploy on Railway" 
2. Select this repo → `/backend` folder
3. Add these environment variables:
   ```
   OPENAI_API_KEY=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
   TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAADOR2QEAAAAA6W506IomOHuS50m2topvTT2o5QQ%3DwkFVv6RKndJEsYI8Fh8Wqjfk1IR14zN7wzzEpC4KWa3UAqJHOL
   MONGO_URL=mongodb://mongo:27017/growth_signals
   ```
4. Add MongoDB service
5. Copy your Railway URL

### 2. Frontend (Vercel)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/git/external?repository-url=https://github.com/yourusername/growth-signals&project-name=growth-signals&repository-name=growth-signals)

1. Click "Deploy with Vercel"
2. Import this repo
3. Set root directory: `frontend`
4. Add environment variable:
   ```
   REACT_APP_BACKEND_URL=https://your-railway-url.railway.app
   ```
5. Deploy!

**Live in 5 minutes! 🎉**

---

## Deploy Option C: Your Domain (silverbirchgrowth.com)

### Quick Commands:
```bash
# 1. Build frontend
cd frontend && npm install && npm run build

# 2. Upload build/ to signals.silverbirchgrowth.com

# 3. Run backend on your server
cd backend
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8001

# 4. Configure nginx (see deployment/nginx.conf)
```

### Full Documentation:
See `/docs/DEPLOYMENT.md` for complete instructions.

---

**Ready to deploy! Your Growth Signals dashboard will be live in minutes.** 🚀