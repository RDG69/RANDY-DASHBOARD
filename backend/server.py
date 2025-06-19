from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
from datetime import datetime
import json
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI
app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI Setup
openai_api_key = os.environ.get('OPENAI_API_KEY')
openai_client = None

if openai_api_key:
    try:
        openai_client = openai.OpenAI(api_key=openai_api_key)
        logging.info("OpenAI API configured successfully")
    except Exception as e:
        logging.error(f"OpenAI setup failed: {e}")
        openai_client = None
else:
    logging.warning("OpenAI API key not found")

# Simple Data Models
class ContentAnalysisRequest(BaseModel):
    content: str
    company_context: Optional[str] = None

# SIMPLE RSS-STYLE DATA FEEDS
RSS_LEADS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Sarah Martinez", 
        "role": "CEO",
        "company": "ScaleUp AI",
        "geography": "San Francisco, CA",
        "social_content": "Looking to hire our first CRO after raising Series A. Need someone who can scale from $1M to $10M ARR.",
        "score": 7.2,
        "priority": "High",
        "keywords": ["cro", "series a", "scaling", "revenue"],
        "intent_signals": [{"signal": "CRO Hiring Urgency", "confidence": 0.9}],
        "linkedin_url": "https://linkedin.com/in/sarah-martinez-ceo",
        "company_website": "https://scaleup-ai.com"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Mike Chen",
        "role": "Founder", 
        "company": "GPU Dynamics",
        "geography": "Austin, TX",
        "social_content": "Raised $15M Series B to scale our GPU infrastructure. Building sales team from 2 to 20 people.",
        "score": 8.1,
        "priority": "High", 
        "keywords": ["gpu", "series b", "sales team", "scaling"],
        "intent_signals": [{"signal": "Sales Team Scaling", "confidence": 0.85}],
        "linkedin_url": "https://linkedin.com/in/mike-chen-founder",
        "company_website": "https://gpu-dynamics.com"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Alex Rivera",
        "role": "VP Engineering",
        "company": "DataFlow Inc", 
        "geography": "New York, NY",
        "social_content": "Our revenue hit a plateau at $5M. Board wants us to hire VP Sales to break through to next level.",
        "score": 6.8,
        "priority": "Medium",
        "keywords": ["vp sales", "revenue plateau", "hiring"],
        "intent_signals": [{"signal": "VP Sales Hiring", "confidence": 0.8}],
        "linkedin_url": "https://linkedin.com/in/alex-rivera-vp",
        "company_website": "https://dataflow-inc.com"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Jennifer Park",
        "role": "CEO",
        "company": "CloudTech Solutions",
        "geography": "Seattle, WA", 
        "social_content": "Just closed Series A funding round. Time to scale our GTM strategy and expand internationally.",
        "score": 7.5,
        "priority": "High",
        "keywords": ["series a", "gtm strategy", "international expansion"],
        "intent_signals": [{"signal": "International Expansion", "confidence": 0.75}],
        "linkedin_url": "https://linkedin.com/in/jennifer-park-ceo",
        "company_website": "https://cloudtech-solutions.com"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "David Thompson",
        "role": "Founder",
        "company": "SaaS Builder",
        "geography": "Boston, MA",
        "social_content": "Pipeline has been unpredictable. Looking for sales consultant to help us build repeatable process.",
        "score": 6.2,
        "priority": "Medium",
        "keywords": ["pipeline", "sales consultant", "process"],
        "intent_signals": [{"signal": "Pipeline Anxiety", "confidence": 0.7}],
        "linkedin_url": "https://linkedin.com/in/david-thompson-founder",
        "company_website": "https://saas-builder.com"
    }
]

RSS_NEWS = [
    {
        "title": "73% of Series A Companies Now Hiring Sales Consultants",
        "description": "New study shows growth-stage startups increasingly rely on external sales expertise",
        "content": "A comprehensive study reveals that Series A companies are turning to sales consultants at unprecedented rates. The trend reflects growing complexity in B2B sales processes.",
        "source": "SaaStr Weekly",
        "keywords": ["series a", "sales consultants", "growth"],
        "relevance_score": 8.5,
        "timestamp": "2025-01-15T10:00:00Z"
    },
    {
        "title": "CRO Hiring Boom: Why Early-Stage Companies Need Revenue Leadership", 
        "description": "Series A and B companies increasingly hiring Chief Revenue Officers",
        "content": "Chief Revenue Officer roles are becoming critical for scaling startups. Companies report 40% faster growth with dedicated CRO leadership.",
        "source": "TechCrunch",
        "keywords": ["cro", "revenue", "hiring", "leadership"],
        "relevance_score": 9.2,
        "timestamp": "2025-01-14T15:30:00Z"
    },
    {
        "title": "GPU Startups Raise Record $2.3B in Q4 2024",
        "description": "AI infrastructure companies dominate funding rounds",
        "content": "GPU and AI infrastructure startups raised record amounts in Q4, with average Series A rounds reaching $25M. Scaling challenges remain for hardware companies.",
        "source": "VentureBeat", 
        "keywords": ["gpu", "ai", "funding", "infrastructure"],
        "relevance_score": 7.8,
        "timestamp": "2025-01-13T09:15:00Z"
    },
    {
        "title": "Pipeline Anxiety: 68% of Growth-Stage CEOs Lose Sleep Over Sales",
        "description": "Survey reveals top concerns of Series A/B founders about revenue predictability",
        "content": "Revenue predictability remains the top concern for growth-stage CEOs. Many are investing in sales ops and process optimization.",
        "source": "First Round Review",
        "keywords": ["pipeline", "revenue", "sales", "predictability"],
        "relevance_score": 8.8,
        "timestamp": "2025-01-12T14:20:00Z"
    }
]

RSS_DEALS = [
    {
        "title": "SalesBoost Acquired by HubSpot for $150M",
        "description": "Sales acceleration platform focused on Series A/B companies",
        "content": "HubSpot acquires SalesBoost to expand services for growth-stage startups struggling with sales scaling.",
        "type": "M&A",
        "amount": "$150M",
        "company": "SalesBoost",
        "keywords": ["sales", "acceleration", "series a", "scaling"],
        "relevance_score": 9.1,
        "timestamp": "2025-01-15T11:00:00Z"
    },
    {
        "title": "GPU Infrastructure Startup TensorFlow Raises $40M Series B",
        "description": "Funding to accelerate sales team growth and international expansion", 
        "content": "TensorFlow's Series B will fund sales team expansion from 5 to 50 people and international market entry.",
        "type": "Financing",
        "amount": "$40M",
        "company": "TensorFlow",
        "keywords": ["gpu", "infrastructure", "sales team", "expansion"],
        "relevance_score": 8.7,
        "timestamp": "2025-01-14T16:45:00Z"
    },
    {
        "title": "Revenue Operations Platform RevOps Closes $25M Series A",
        "description": "Platform helps startups build predictable revenue processes",
        "content": "RevOps platform addresses pipeline anxiety by helping startups build repeatable sales processes and revenue predictability.",
        "type": "Financing", 
        "amount": "$25M",
        "company": "RevOps",
        "keywords": ["revenue", "operations", "pipeline", "process"],
        "relevance_score": 8.9,
        "timestamp": "2025-01-13T13:30:00Z"
    }
]

RSS_TWEETS = [
    {
        "id": str(uuid.uuid4()),
        "content": "Just hired our first CRO after 18 months of trying to scale sales ourselves. Should have done this at $2M ARR instead of waiting until $5M. Game changer.",
        "author_name": "Mark Stevens",
        "author_handle": "@markstevens_ceo",
        "keywords": ["cro", "scaling", "sales", "revenue"],
        "engagement_metrics": {"like_count": 45, "retweet_count": 12},
        "relevance_score": 8.2,
        "timestamp": "2025-01-15T14:30:00Z"
    },
    {
        "id": str(uuid.uuid4()),
        "content": "Series A complete! $12M to scale our GPU platform. Now the real work begins - building a sales machine that can take us to $50M ARR.",
        "author_name": "Lisa Chen", 
        "author_handle": "@lisachen_ai",
        "keywords": ["series a", "gpu", "sales", "scaling"],
        "engagement_metrics": {"like_count": 78, "retweet_count": 23},
        "relevance_score": 9.1,
        "timestamp": "2025-01-15T12:15:00Z"
    },
    {
        "id": str(uuid.uuid4()),
        "content": "Pipeline anxiety is real. Q4 was a rollercoaster. Investing heavily in sales ops and process this year. Any recommendations for fractional CROs?",
        "author_name": "Tony Martinez",
        "author_handle": "@tonymartinez_b2b", 
        "keywords": ["pipeline", "anxiety", "sales ops", "cro"],
        "engagement_metrics": {"like_count": 34, "retweet_count": 8},
        "relevance_score": 7.8,
        "timestamp": "2025-01-15T10:45:00Z"
    }
]

def simple_gpt_filter(data_items: List[Dict], search_context: str, data_type: str) -> List[Dict]:
    """Simple GPT filtering that actually works"""
    if not openai_client or not search_context:
        return data_items
    
    try:
        # Simple prompt that works
        prompt = f"""
        User is searching for: "{search_context}"
        
        Rank these {data_type} items by relevance (1-10 scale) for someone looking for prospects matching that criteria.
        
        Items: {json.dumps([{
            'keywords': item.get('keywords', []),
            'content': item.get('social_content', item.get('content', item.get('description', '')))[:100]
        } for item in data_items[:5]])}
        
        Return JSON array: [10, 8, 6, 9, 7] (scores for items in order)
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1,
            timeout=5
        )
        
        try:
            scores = json.loads(response.choices[0].message.content)
            if isinstance(scores, list) and len(scores) <= len(data_items):
                for i, score in enumerate(scores):
                    if i < len(data_items):
                        data_items[i]['relevance_score'] = min(float(score), 10)
                        data_items[i]['gpt_enhanced'] = True
        except:
            pass
            
    except Exception as e:
        logging.warning(f"GPT filtering failed: {e}")
    
    return sorted(data_items, key=lambda x: x.get('relevance_score', 0), reverse=True)

# SIMPLE API ENDPOINTS
@app.get("/api/")
async def root():
    return {"message": "Growth Signals API v1.0.0", "status": "operational"}

@app.get("/api/leads")
async def get_leads(context: Optional[str] = Query(None)):
    """Get leads with simple context filtering"""
    try:
        leads = RSS_LEADS.copy()
        
        if context:
            # Simple keyword matching + GPT enhancement
            context_lower = context.lower()
            
            # Boost scores for keyword matches
            for lead in leads:
                keyword_matches = sum(1 for keyword in lead.get('keywords', []) if keyword in context_lower)
                content_matches = sum(1 for word in context_lower.split() if word in lead.get('social_content', '').lower())
                
                if keyword_matches > 0 or content_matches > 0:
                    lead['score'] = min(lead['score'] + keyword_matches + content_matches * 0.5, 10)
                    lead['context_match'] = True
            
            # GPT enhancement
            leads = simple_gpt_filter(leads, context, "leads")
        
        # Sort by score
        leads.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return JSONResponse(content={"leads": leads, "total": len(leads)})
    except Exception as e:
        logging.error(f"Leads API failed: {e}")
        return JSONResponse(content={"leads": RSS_LEADS, "total": len(RSS_LEADS)})

@app.get("/api/startup-news")
async def get_news(context: Optional[str] = Query(None)):
    """Get news with simple context filtering"""
    try:
        news = RSS_NEWS.copy()
        
        if context:
            context_lower = context.lower()
            
            # Boost scores for keyword matches
            for item in news:
                keyword_matches = sum(1 for keyword in item.get('keywords', []) if keyword in context_lower)
                content_matches = sum(1 for word in context_lower.split() if word in item.get('content', '').lower())
                
                if keyword_matches > 0 or content_matches > 0:
                    item['relevance_score'] = min(item['relevance_score'] + keyword_matches + content_matches * 0.5, 10)
                    item['context_match'] = True
            
            # GPT enhancement
            news = simple_gpt_filter(news, context, "news")
        
        # Sort by relevance
        news.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return JSONResponse(content={"news": news, "total": len(news)})
    except Exception as e:
        logging.error(f"News API failed: {e}")
        return JSONResponse(content={"news": RSS_NEWS, "total": len(RSS_NEWS)})

@app.get("/api/deals")
async def get_deals(context: Optional[str] = Query(None)):
    """Get deals with simple context filtering"""
    try:
        deals = RSS_DEALS.copy()
        
        if context:
            context_lower = context.lower()
            
            # Boost scores for keyword matches
            for deal in deals:
                keyword_matches = sum(1 for keyword in deal.get('keywords', []) if keyword in context_lower)
                content_matches = sum(1 for word in context_lower.split() if word in deal.get('content', '').lower())
                
                if keyword_matches > 0 or content_matches > 0:
                    deal['relevance_score'] = min(deal['relevance_score'] + keyword_matches + content_matches * 0.5, 10)
                    deal['context_match'] = True
            
            # GPT enhancement
            deals = simple_gpt_filter(deals, context, "deals")
        
        # Sort by relevance
        deals.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return JSONResponse(content={"deals": deals, "total": len(deals)})
    except Exception as e:
        logging.error(f"Deals API failed: {e}")
        return JSONResponse(content={"deals": RSS_DEALS, "total": len(RSS_DEALS)})

@app.get("/api/cached-tweets")
async def get_cached_tweets(context: Optional[str] = Query(None)):
    """Get tweets with simple context filtering"""
    try:
        tweets = RSS_TWEETS.copy()
        
        if context:
            context_lower = context.lower()
            
            # Boost scores for keyword matches
            for tweet in tweets:
                keyword_matches = sum(1 for keyword in tweet.get('keywords', []) if keyword in context_lower)
                content_matches = sum(1 for word in context_lower.split() if word in tweet.get('content', '').lower())
                
                if keyword_matches > 0 or content_matches > 0:
                    tweet['relevance_score'] = min(tweet['relevance_score'] + keyword_matches + content_matches * 0.5, 10)
                    tweet['context_match'] = True
            
            # GPT enhancement
            tweets = simple_gpt_filter(tweets, context, "tweets")
        
        # Sort by relevance
        tweets.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return JSONResponse(content={"tweets": tweets, "total": len(tweets)})
    except Exception as e:
        logging.error(f"Tweets API failed: {e}")
        return JSONResponse(content={"tweets": RSS_TWEETS, "total": len(RSS_TWEETS)})

@app.get("/api/stats")
async def get_stats():
    """Get simple stats"""
    return JSONResponse(content={
        "total_leads": len(RSS_LEADS),
        "total_tweets": len(RSS_TWEETS), 
        "total_news": len(RSS_NEWS),
        "total_deals": len(RSS_DEALS),
        "last_updated": datetime.utcnow().isoformat()
    })

@app.post("/api/analyze-content")
async def analyze_content(request: ContentAnalysisRequest):
    """Simple content analysis"""
    try:
        content = request.content.lower()
        signals = []
        score = 0
        
        # Simple keyword detection
        if any(word in content for word in ["cro", "chief revenue"]):
            signals.append({"signal": "CRO Hiring Urgency", "confidence": 0.8})
            score += 3
        if any(word in content for word in ["vp sales", "sales director"]):
            signals.append({"signal": "VP Sales Hiring", "confidence": 0.75})
            score += 2
        if any(word in content for word in ["series a", "series b", "funding"]):
            signals.append({"signal": "Series A Follow-On Needed", "confidence": 0.7})
            score += 2
        if any(word in content for word in ["scaling", "scale", "growth"]):
            signals.append({"signal": "Sales Team Scaling", "confidence": 0.65})
            score += 1
        
        priority = "High" if score >= 5 else "Medium" if score >= 2 else "Low"
        
        return JSONResponse(content={
            "intent_signals": signals,
            "priority": priority,
            "score": min(score, 10),
            "relevance_score": min(score, 10)
        })
    except Exception as e:
        logging.error(f"Content analysis failed: {e}")
        return JSONResponse(content={
            "intent_signals": [],
            "priority": "Low", 
            "score": 0,
            "relevance_score": 0
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)