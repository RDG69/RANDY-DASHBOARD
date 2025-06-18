# 🚀 Deployment Guide

## Quick Deploy Options

### Option A: Vercel + Railway (Recommended)

#### 1. Deploy Backend to Railway

1. Go to [railway.app](https://railway.app)
2. Click "Deploy from GitHub" 
3. Select this repository
4. Choose `/backend` as root directory
5. Add environment variables:
   ```
   MONGO_URL=mongodb://mongo:27017/growth_signals
   OPENAI_API_KEY=your-openai-key
   TWITTER_BEARER_TOKEN=your-twitter-token
   PORT=8001
   ```
6. Add MongoDB service: "Add Service" → "MongoDB"
7. Copy MongoDB connection URL to MONGO_URL

#### 2. Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import this GitHub repository
3. Set framework preset: "Create React App"
4. Set root directory: `frontend`
5. Add environment variable:
   ```
   REACT_APP_BACKEND_URL=https://your-railway-backend-url.railway.app
   ```
6. Deploy!

**Total time: ~5 minutes**

---

### Option B: Your Domain (silverbirchgrowth.com)

#### 1. Frontend Deployment

```bash
# Build the React app
cd frontend
npm install
npm run build

# Upload build/ contents to your web server
# Example: /var/www/signals.silverbirchgrowth.com/
```

#### 2. Backend Deployment

```bash
# On your server
cd backend
pip install -r requirements.txt

# Set environment variables
export MONGO_URL="mongodb://localhost:27017"
export DB_NAME="growth_signals"
export OPENAI_API_KEY="your-key"
export TWITTER_BEARER_TOKEN="your-token"

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8001
```

#### 3. Nginx Configuration

Use the nginx.conf file in `/deployment/nginx.conf`

```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/growth-signals
sudo ln -s /etc/nginx/sites-available/growth-signals /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

### Option C: Docker Deployment

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run with docker-compose
docker-compose -f deployment/docker-compose.yml up -d
```

## Environment Variables

### Required for Backend:
- `OPENAI_API_KEY` - Your OpenAI API key
- `TWITTER_BEARER_TOKEN` - Your Twitter API bearer token
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name (default: growth_signals)

### Required for Frontend:
- `REACT_APP_BACKEND_URL` - Backend API URL

## SSL Configuration

For production deployments on your domain:

1. **Get SSL Certificate:**
   ```bash
   sudo certbot --nginx -d signals.silverbirchgrowth.com
   ```

2. **Update Nginx Config:**
   The provided nginx.conf includes SSL configuration.

## Monitoring & Logs

### Railway/Vercel:
- Built-in logging and monitoring dashboards

### Self-hosted:
```bash
# Backend logs
tail -f /var/log/growth-signals/backend.log

# Nginx logs  
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Scaling

### Horizontal Scaling:
- Frontend: Vercel handles automatically
- Backend: Add more Railway instances or use load balancer

### Database Scaling:
- MongoDB Atlas for managed scaling
- Read replicas for high-traffic scenarios

## Troubleshooting

### Common Issues:

1. **CORS Errors:**
   - Check REACT_APP_BACKEND_URL is correct
   - Ensure backend CORS is configured for your domain

2. **API Key Errors:**
   - Verify environment variables are set
   - Check API key permissions and quotas

3. **Database Connection:**
   - Verify MONGO_URL format
   - Check network connectivity to MongoDB

### Health Checks:

```bash
# Backend health
curl https://your-backend-url.com/api/

# Frontend health  
curl https://your-frontend-url.com/
```

## Performance Optimization

1. **Frontend:**
   - Enable gzip compression
   - Use CDN for static assets
   - Implement caching headers

2. **Backend:**
   - Use Redis for caching
   - Implement rate limiting
   - Monitor API response times

3. **Database:**
   - Add indexes for query optimization
   - Use connection pooling
   - Regular backup strategy