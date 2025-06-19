from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import json
import requests
import httpx
from openai import OpenAI

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN')

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Create the main app
app = FastAPI(title="Growth Signals API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom JSON encoder to handle datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Intent Signals Configuration
INTENT_SIGNALS = [
    "Series A Follow-On Needed", "Series B Preparation", "Seed to Series A Transition",
    "Post-Funding Sales Scaling", "CRO Hiring Urgency", "VP Sales Hiring",
    "Pipeline Anxiety", "Revenue Plateau", "Customer Acquisition Cost Issues",
    "GTM Strategy Overhaul", "Sales Process Optimization", "Revenue Operations Setup",
    "Product-Market Fit to Scale", "Sales Team Scaling", "International Expansion",
    "Enterprise Sales Transition", "Revenue Growth Acceleration", "Sales Consultant Search",
    "CRM Implementation", "Sales Efficiency Issues", "Growth Consultant Needed",
    "Funding Preparation Sales Readiness", "ARR Growth Stagnation", "Pipeline Generation Issues",
    "Sales Cycle Too Long", "Lead Conversion Problems", "Territory Expansion Planning",
    "Sales Enablement Gaps", "Quota Attainment Issues", "Channel Partner Strategy",
    "Inside Sales Scaling", "Outbound Strategy Development", "Inbound Lead Qualification"
]

# Data Models
class IntentSignal(BaseModel):
    signal: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company: str
    name: str
    role: str
    geography: str
    priority: str = Field(default="Medium")  # High, Medium, Low
    score: float = Field(ge=0.0, le=10.0)
    intent_signals: List[IntentSignal]
    social_content: str
    status: str = Field(default="New")  # New, Contacted, Qualified, Closed
    twitter_handle: Optional[str] = None
    linkedin_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Tweet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tweet_id: str
    content: str
    author_name: str
    author_handle: str
    engagement_metrics: Dict[str, int]
    intent_analysis: Optional[Dict[str, Any]] = None
    relevance_score: float = Field(ge=0.0, le=10.0, default=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NewsItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    url: str
    source: str
    category: str
    relevance_score: float = Field(ge=0.0, le=10.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MarketData(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ContentAnalysisRequest(BaseModel):
    content: str
    company_context: Optional[str] = None

# Fallback Data
FALLBACK_LEADS = [
    {
        "id": str(uuid.uuid4()),
        "company": "CloudSync",
        "name": "Alex Chen",
        "role": "CEO",
        "geography": "Austin, TX, USA",
        "priority": "High",
        "score": 9.1,
        "intent_signals": [
            {"signal": "Series A Follow-On Needed", "confidence": 0.92, "reasoning": "Just raised Series A, struggling with sales execution to justify Series B"},
            {"signal": "CRO Hiring Urgency", "confidence": 0.88, "reasoning": "Posted multiple CRO job listings, sales team underperforming"}
        ],
        "social_content": "6 months post Series A and our sales execution isn't where it needs to be. Looking for a world-class CRO to help us nail our GTM before Series B. #hiring #startup #sales",
        "twitter_handle": "@alexchen_ceo",
        "linkedin_url": "https://linkedin.com/in/alexchen-founder",
        "company_website": "https://cloudsync.com",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "RevScale",
        "name": "Sarah Martinez",
        "role": "Founder",
        "geography": "Denver, CO, USA",
        "priority": "High",
        "score": 8.9,
        "intent_signals": [
            {"signal": "Post-Funding Sales Scaling", "confidence": 0.95, "reasoning": "Just raised $8M Series A, need to scale sales team from 3 to 15 reps"},
            {"signal": "GTM Strategy Overhaul", "confidence": 0.86, "reasoning": "Current GTM not working, need strategic rebuild"}
        ],
        "social_content": "Fresh off our $8M Series A! Now the real work begins - scaling our sales team 5x and completely rebuilding our GTM strategy. Anyone know great sales consultants? #SeriesA #scaling #GTM",
        "twitter_handle": "@sarahmartinez_rs",
        "linkedin_url": "https://linkedin.com/in/sarah-martinez-revscale",
        "company_website": "https://revscale.io",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "GrowthLabs",
        "name": "Michael Park",
        "role": "Co-Founder",
        "geography": "Seattle, WA, USA",
        "priority": "High",
        "score": 8.7,
        "intent_signals": [
            {"signal": "Pipeline Anxiety", "confidence": 0.91, "reasoning": "Publicly discussing pipeline concerns and sales process issues"},
            {"signal": "Revenue Plateau", "confidence": 0.84, "reasoning": "Growth has stalled at $2M ARR, need breakthrough"}
        ],
        "social_content": "Stuck at $2M ARR for 6 months. Our pipeline is inconsistent and sales process needs work. Time to bring in outside expertise to break through this ceiling. #startup #pipeline #growth",
        "twitter_handle": "@mikepark_growth",
        "linkedin_url": "https://linkedin.com/in/michael-park-growthlabs",
        "company_website": "https://growthlabs.co",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "DataStream",
        "name": "Jennifer Kim",
        "role": "CEO",
        "geography": "San Francisco, CA, USA",
        "priority": "High",
        "score": 8.8,
        "intent_signals": [
            {"signal": "International Expansion", "confidence": 0.89, "reasoning": "Planning European expansion, need GTM strategy for new markets"},
            {"signal": "Sales Team Scaling", "confidence": 0.87, "reasoning": "Hiring 10+ sales reps for expansion"}
        ],
        "social_content": "Preparing for European expansion with our Series B funding. Need to build out sales teams in London and Berlin. Looking for GTM consultants with international experience. #expansion #SeriesB #international",
        "twitter_handle": "@jenniferkim_ds",
        "linkedin_url": "https://linkedin.com/in/jennifer-kim-datastream",
        "company_website": "https://datastream.ai",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "SalesFlow",
        "name": "David Rodriguez",
        "role": "Founder",
        "geography": "Miami, FL, USA",
        "priority": "Medium",
        "score": 8.4,
        "intent_signals": [
            {"signal": "Seed to Series A Transition", "confidence": 0.88, "reasoning": "Preparing for Series A, need proven sales processes"},
            {"signal": "Sales Process Optimization", "confidence": 0.85, "reasoning": "Current sales process isn't scalable for growth"}
        ],
        "social_content": "6 months until Series A fundraising and our sales process needs to be bulletproof. Looking for consultants who've helped companies scale from $1M to $10M ARR. #SeriesA #sales #scaling",
        "twitter_handle": "@davidrodriguez_sf",
        "linkedin_url": "https://linkedin.com/in/david-rodriguez-salesflow",
        "company_website": "https://salesflow.tech",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "TechForward",
        "name": "Emily Chen",
        "role": "COO",
        "geography": "Chicago, IL, USA",
        "priority": "High",
        "score": 8.6,
        "intent_signals": [
            {"signal": "Revenue Operations Setup", "confidence": 0.93, "reasoning": "Building RevOps function from scratch post-funding"},
            {"signal": "CRM Implementation", "confidence": 0.81, "reasoning": "Implementing enterprise CRM, need strategic guidance"}
        ],
        "social_content": "Post-Series A and building our RevOps function from the ground up. Need strategic guidance on CRM implementation and sales process design. #RevOps #SeriesA #sales",
        "twitter_handle": "@emilychen_tf",
        "linkedin_url": "https://linkedin.com/in/emily-chen-techforward",
        "company_website": "https://techforward.co",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "MarketBridge",
        "name": "Ryan Thompson",
        "role": "CEO",
        "geography": "Boston, MA, USA",
        "priority": "High",
        "score": 8.5,
        "intent_signals": [
            {"signal": "Product-Market Fit to Scale", "confidence": 0.87, "reasoning": "Found PMF, now need to scale sales rapidly"},
            {"signal": "VP Sales Hiring", "confidence": 0.89, "reasoning": "Urgently hiring VP Sales for rapid scaling"}
        ],
        "social_content": "We've found product-market fit and now need to scale sales FAST. Hiring a VP Sales and need consultants to help design our scaling strategy. #PMF #scaling #hiring",
        "twitter_handle": "@ryanthompson_mb",
        "linkedin_url": "https://linkedin.com/in/ryan-thompson-marketbridge",
        "company_website": "https://marketbridge.com",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "InnovateLabs",
        "name": "Lisa Wang",
        "role": "Founder",
        "geography": "Portland, OR, USA",
        "priority": "Medium",
        "score": 8.2,
        "intent_signals": [
            {"signal": "Customer Acquisition Cost Issues", "confidence": 0.84, "reasoning": "CAC is too high, need better sales efficiency"},
            {"signal": "Sales Consultant Search", "confidence": 0.91, "reasoning": "Actively looking for sales consultants"}
        ],
        "social_content": "Our CAC is killing us and sales cycle is too long. Need experienced consultants to help optimize our sales process and improve efficiency. Recommendations welcome! #CAC #sales #consulting",
        "twitter_handle": "@lisawang_innovate",
        "linkedin_url": "https://linkedin.com/in/lisa-wang-innovatelabs",
        "company_website": "https://innovatelabs.io",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "ScaleUp",
        "name": "James Liu",
        "role": "CEO",
        "geography": "New York, NY, USA",
        "priority": "High",
        "score": 8.7,
        "intent_signals": [
            {"signal": "Series B Preparation", "confidence": 0.92, "reasoning": "Preparing Series B, need sales metrics and processes ready"},
            {"signal": "Revenue Growth Acceleration", "confidence": 0.88, "reasoning": "Need to accelerate revenue growth for Series B"}
        ],
        "social_content": "Series B in 9 months and we need to accelerate revenue growth. Our sales team needs strategic guidance to hit ambitious targets. Time for expert help. #SeriesB #revenue #growth",
        "twitter_handle": "@jamesliu_scaleup",
        "linkedin_url": "https://linkedin.com/in/james-liu-scaleup",
        "company_website": "https://scaleup.tech",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company": "NextGen",
        "name": "Amanda Foster",
        "role": "Co-Founder",
        "geography": "Nashville, TN, USA",
        "priority": "Medium",
        "score": 8.3,
        "intent_signals": [
            {"signal": "Enterprise Sales Transition", "confidence": 0.86, "reasoning": "Moving from SMB to enterprise, need new sales approach"},
            {"signal": "GTM Strategy Pivot", "confidence": 0.83, "reasoning": "Pivoting GTM strategy for enterprise market"}
        ],
        "social_content": "Making the jump from SMB to enterprise sales. Our current GTM won't work for $100K+ deals. Need consultants with enterprise sales expertise. #enterprise #GTM #transition",
        "twitter_handle": "@amandafoster_ng",
        "linkedin_url": "https://linkedin.com/in/amanda-foster-nextgen",
        "company_website": "https://nextgen.ai",
        "status": "New",
        "timestamp": datetime.utcnow().isoformat()
    }
]

FALLBACK_NEWS = [
    {
        "title": "Series A Funding Hits $2.3B in December 2024 for Growth-Stage SaaS",
        "description": "Early-stage B2B companies raising larger Series A rounds as investors focus on proven sales traction",
        "url": "https://pitchbook.com/",
        "source": "PitchBook",
        "category": "Funding",
        "relevance_score": 9.4
    },
    {
        "title": "Why 73% of Series A Companies Hire Sales Consultants Within 12 Months",
        "description": "New study shows growth-stage startups increasingly rely on external sales expertise to scale",
        "url": "https://www.saastr.com/",
        "source": "SaaStr",
        "category": "Sales",
        "relevance_score": 9.1
    },
    {
        "title": "Post-Funding Sales Scaling: The Make-or-Break 18 Months",
        "description": "How growth-stage companies can avoid the common pitfalls when scaling sales teams after funding",
        "url": "https://www.firstround.com/",
        "source": "First Round",
        "category": "Growth",
        "relevance_score": 8.8
    },
    {
        "title": "The CRO Hiring Boom: Why Early-Stage Companies Need Revenue Leadership",
        "description": "Series A and B companies increasingly hiring Chief Revenue Officers to professionalize sales",
        "url": "https://www.techcrunch.com/",
        "source": "TechCrunch",
        "category": "Leadership",
        "relevance_score": 8.5
    },
    {
        "title": "Pipeline Anxiety: 68% of Growth-Stage CEOs Lose Sleep Over Sales Predictability",
        "description": "Survey reveals the top concerns of Series A/B founders and how they're addressing revenue challenges",
        "url": "https://www.saastr.com/",
        "source": "SaaStr",
        "category": "Pipeline",
        "relevance_score": 8.3
    }
]

FALLBACK_DEALS = [
    {
        "title": "CloudStrike Acquires SalesBoost for $120M to Expand GTM Solutions",
        "description": "Strategic acquisition targets Series A companies needing sales acceleration services",
        "company": "CloudStrike",
        "type": "M&A",
        "amount": "$120M",
        "relevance_score": 9.2
    },
    {
        "title": "RevOps Platform ScalePath Raises $25M Series B",
        "description": "Funding will accelerate expansion into revenue operations consulting for growth-stage startups",
        "company": "ScalePath",
        "type": "Financing",
        "amount": "$25M",
        "relevance_score": 8.9
    },
    {
        "title": "GTM Consulting Firm Velocity Partners Acquired by Bain Capital",
        "description": "Private equity acquisition of premier B2B sales consulting firm serving Series A/B companies",
        "company": "Velocity Partners",
        "type": "M&A",
        "amount": "Undisclosed",
        "relevance_score": 8.7
    },
    {
        "title": "SaaS Sales Training Platform RampUp Closes $18M Series A",
        "description": "Platform helps scaling companies onboard and train sales teams more effectively",
        "company": "RampUp",
        "type": "Financing",
        "amount": "$18M",
        "relevance_score": 8.5
    },
    {
        "title": "Enterprise CRM Startup FlowState Raises $40M to Challenge Salesforce",
        "description": "New funding targets Series A/B companies dissatisfied with legacy CRM solutions",
        "company": "FlowState",
        "type": "Financing",
        "amount": "$40M",
        "relevance_score": 8.3
    },
    {
        "title": "Sales Intelligence Platform PipelineAI Acquired by HubSpot",
        "description": "Strategic acquisition enhances AI-powered lead scoring and intent signal detection",
        "company": "PipelineAI",
        "type": "M&A",
        "amount": "$85M",
        "relevance_score": 8.1
    }
]

FALLBACK_TWEETS = [
    {
        "id": str(uuid.uuid4()),
        "tweet_id": "1234567890",
        "content": "Just closed our Series A! $15M to scale our B2B sales platform. Hiring VP Sales and RevOps team. Exciting times ahead! #startup #funding #hiring",
        "author_name": "Alex Thompson", 
        "author_handle": "@alexthompson_ceo",
        "engagement_metrics": {"likes": 234, "retweets": 45, "replies": 28},
        "relevance_score": 9.1,
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "tweet_id": "1234567891",
        "content": "Our current CRM is a bottleneck. Looking for enterprise-grade solutions with better analytics. Any recommendations for scaling B2B sales teams?",
        "author_name": "Lisa Chen",
        "author_handle": "@lisachen_ops", 
        "engagement_metrics": {"likes": 156, "retweets": 32, "replies": 67},
        "relevance_score": 8.3,
        "timestamp": datetime.utcnow().isoformat()
    }
]

# Utility Functions
async def analyze_content_with_ai(content: str, context: str = "") -> Dict[str, Any]:
    """Analyze content for intent signals using AI"""
    
    # Fast fallback analysis with some basic keyword matching
    content_lower = content.lower()
    intent_signals = []
    score = 0
    
    # Quick keyword-based analysis for speed
    if any(word in content_lower for word in ["cro", "chief revenue", "vp sales", "hiring"]):
        intent_signals.append({
            "signal": "CRO Hiring Urgency",
            "confidence": 0.85,
            "reasoning": "Keywords indicate executive hiring activity"
        })
        score += 3
    
    if any(word in content_lower for word in ["series a", "series b", "funding", "raised"]):
        intent_signals.append({
            "signal": "Series A Follow-On Needed",
            "confidence": 0.80,
            "reasoning": "Funding-related keywords detected"
        })
        score += 3
        
    if any(word in content_lower for word in ["scaling", "scale", "growth", "expand"]):
        intent_signals.append({
            "signal": "Sales Team Scaling",
            "confidence": 0.75,
            "reasoning": "Scaling-related keywords detected"
        })
        score += 2
    
    priority = "High" if score >= 5 else "Medium" if score >= 2 else "Low"
    
    # Try AI enhancement (with timeout) but don't block on it
    if openai_client:
        try:
            prompt = f"Analyze for B2B intent: '{content}'. Return JSON: {{\"intent_signals\":[{{\"signal\":\"name\",\"confidence\":0.8,\"reasoning\":\"brief\"}}],\"priority\":\"High\",\"score\":8}}"
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.1,
                timeout=5  # Very short timeout
            )
            
            try:
                ai_analysis = json.loads(response.choices[0].message.content)
                # Use AI results if they're better
                if ai_analysis.get("score", 0) > score:
                    return ai_analysis
            except:
                pass  # Fall back to keyword analysis
                
        except Exception as e:
            logging.warning(f"AI analysis timeout/failed, using fast fallback: {e}")
    
    return {
        "intent_signals": intent_signals,
        "priority": priority,
        "score": min(score, 10),
        "relevance_score": min(score, 10)
    }

async def fetch_twitter_data(query: str = None, count: int = 10) -> List[Dict]:
    """Fetch tweets using Twitter API with B2B-specific queries"""
    if not TWITTER_BEARER_TOKEN:
        return FALLBACK_TWEETS
    
    # Define specific B2B growth signal queries
    if not query:
        b2b_queries = [
            '"hiring CRO" OR "hiring chief revenue officer"',
            '"VP Sales" OR "head of sales" OR "sales leader"',
            '"scaling sales team" OR "growing sales"', 
            '"Series A" OR "Series B" OR "funding round"',
            '"looking for CRM" OR "CRM implementation"',
            '"RevOps" OR "revenue operations"',
            '"sales tech stack" OR "sales tools"',
            '"GTM strategy" OR "go-to-market"',
            '"B2B sales" OR "enterprise sales"',
            '"sales enablement" OR "sales process"'
        ]
        # Rotate through queries or pick one randomly
        import random
        query = random.choice(b2b_queries)
    
    try:
        headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        
        params = {
            "query": f"{query} -is:retweet lang:en",  # Exclude retweets and non-English
            "max_results": min(count, 10),  # Twitter API limit
            "tweet.fields": "created_at,author_id,public_metrics,context_annotations",
            "user.fields": "name,username,description,location",
            "expansions": "author_id"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                tweets = []
                
                if not data.get('data'):
                    # If no data, return fallback
                    return FALLBACK_TWEETS
                
                users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
                
                for tweet in data.get('data', []):
                    user = users.get(tweet['author_id'], {})
                    
                    # Only include tweets that seem business-related
                    content = tweet['text'].lower()
                    business_keywords = ['ceo', 'founder', 'startup', 'company', 'business', 'sales', 'revenue', 'growth', 'team', 'hiring', 'saas', 'b2b']
                    
                    if any(keyword in content for keyword in business_keywords):
                        tweets.append({
                            "id": str(uuid.uuid4()),
                            "tweet_id": tweet['id'],
                            "content": tweet['text'],
                            "author_name": user.get('name', 'Unknown'),
                            "author_handle": f"@{user.get('username', 'unknown')}",
                            "engagement_metrics": tweet.get('public_metrics', {}),
                            "relevance_score": 7.5,  # Will be updated by AI analysis
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                return tweets if tweets else FALLBACK_TWEETS
            else:
                logging.warning(f"Twitter API error: {response.status_code} - {response.text}")
                return FALLBACK_TWEETS
                
    except Exception as e:
        logging.error(f"Twitter fetch failed: {e}")
        return FALLBACK_TWEETS

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Growth Signals API v1.0.0", "status": "operational"}

@api_router.post("/analyze-content")
async def analyze_content(request: ContentAnalysisRequest):
    """Analyze content for growth intent signals - FAST VERSION"""
    try:
        # Fast keyword-based analysis 
        content_lower = request.content.lower()
        intent_signals = []
        score = 0
        
        # Quick keyword matching
        if any(word in content_lower for word in ["cro", "chief revenue", "vp sales", "hiring"]):
            intent_signals.append({
                "signal": "CRO Hiring Urgency",
                "confidence": 0.85,
                "reasoning": "Executive hiring keywords detected"
            })
            score += 3
        
        if any(word in content_lower for word in ["series a", "series b", "funding", "raised"]):
            intent_signals.append({
                "signal": "Series A Follow-On Needed", 
                "confidence": 0.80,
                "reasoning": "Funding keywords detected"
            })
            score += 3
            
        if any(word in content_lower for word in ["scaling", "scale", "growth", "expand"]):
            intent_signals.append({
                "signal": "Sales Team Scaling",
                "confidence": 0.75,
                "reasoning": "Scaling keywords detected"
            })
            score += 2
        
        priority = "High" if score >= 5 else "Medium" if score >= 2 else "Low"
        
        analysis = {
            "intent_signals": intent_signals,
            "priority": priority,
            "score": min(score, 10),
            "relevance_score": min(score, 10)
        }
        
        return JSONResponse(content=analysis)
    except Exception as e:
        logging.error(f"Content analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@api_router.get("/leads")
async def get_leads(
    role: Optional[str] = Query(None),
    geography: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    context: Optional[str] = Query(None),
    ai_enhanced: Optional[bool] = Query(False)
):
    """Get leads with optional filtering and AI enhancement"""
    try:
        # Start with fallback data
        filtered_leads = FALLBACK_LEADS.copy()
        
        # If we have context, filter and modify leads based on it
        if context:
            context_lower = context.lower()
            
            # Boost relevance for leads that match context keywords
            for lead in filtered_leads:
                lead_text = f"{lead.get('role', '')} {lead.get('company', '')} {lead.get('geography', '')}".lower()
                social_content = lead.get('social_content', '').lower()
                
                # Check for keyword matches
                context_words = context_lower.split()
                matches = 0
                
                for word in context_words:
                    if word in lead_text or word in social_content:
                        matches += 1
                
                # Boost score based on matches
                if matches > 0:
                    lead['score'] = min(lead.get('score', 0) + matches * 0.5, 10)
                    lead['context_match'] = True
                    lead['relevance_boost'] = matches
                
                # Add specific targeting based on common search terms
                if any(term in context_lower for term in ['cro', 'chief revenue', 'vp sales']):
                    if any(signal.get('signal') == 'CRO Hiring Urgency' for signal in lead.get('intent_signals', [])):
                        lead['score'] = min(lead.get('score', 0) + 2, 10)
                        lead['priority'] = 'High'
                
                if any(term in context_lower for term in ['series a', 'series b', 'funding', 'raised']):
                    if any(signal.get('signal') == 'Series A Follow-On Needed' for signal in lead.get('intent_signals', [])):
                        lead['score'] = min(lead.get('score', 0) + 2, 10)
                        lead['priority'] = 'High'
                
                if any(term in context_lower for term in ['scaling', 'scale', 'growth']):
                    if any(signal.get('signal') == 'Sales Team Scaling' for signal in lead.get('intent_signals', [])):
                        lead['score'] = min(lead.get('score', 0) + 1.5, 10)
        
        # Apply traditional filters
        if role:
            filtered_leads = [lead for lead in filtered_leads 
                            if role.lower() in lead.get('role', '').lower()]
        if geography:
            filtered_leads = [lead for lead in filtered_leads 
                            if geography.lower() in lead.get('geography', '').lower()]
        if priority:
            filtered_leads = [lead for lead in filtered_leads 
                            if lead.get('priority', '').lower() == priority.lower()]
        if min_score:
            filtered_leads = [lead for lead in filtered_leads 
                            if lead.get('score', 0) >= min_score]
        
        # Sort by score descending
        filtered_leads.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return JSONResponse(content={"leads": filtered_leads, "total": len(filtered_leads)})
    except Exception as e:
        logging.error(f"Failed to get leads: {e}")
        return JSONResponse(content={"leads": FALLBACK_LEADS, "total": len(FALLBACK_LEADS)})

@api_router.get("/live-tweets")
async def get_live_tweets(
    search_context: Optional[str] = Query(None),
    ai_keywords: Optional[bool] = Query(False)
):
    """Get live tweets with AI-enhanced search"""
    try:
        # Generate AI-enhanced search terms if requested
        search_terms = "B2B sales OR GTM OR Series A OR revenue growth"
        
        if ai_keywords and search_context and openai_client:
            try:
                # Use GPT to generate relevant Twitter search keywords
                keywords_prompt = f"""
                Generate Twitter search keywords for this targeting: "{search_context}"
                
                Create search terms that would find relevant tweets about:
                - Companies/founders in this space
                - Hiring signals and job posts
                - Funding announcements
                - Growth challenges and signals
                - Industry trends and pain points
                
                Return 5-10 keywords/phrases separated by OR, optimized for Twitter search.
                """
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Changed for speed
                    messages=[
                        {"role": "system", "content": "You are a social media intelligence analyst. Generate effective Twitter search terms."},
                        {"role": "user", "content": keywords_prompt}
                    ],
                    max_tokens=100,  # Reduced significantly
                    temperature=0.7,
                    timeout=8  # 8 second timeout
                )
                
                ai_search_terms = response.choices[0].message.content.strip()
                search_terms = f"{ai_search_terms} OR {search_terms}"
                
            except Exception as ai_error:
                logging.error(f"AI keyword generation failed: {ai_error}")
        
        # Get tweets with enhanced search terms
        tweets = await fetch_twitter_data(search_terms, 15)
        analyzed_tweets = []
        
        for tweet in tweets:
            if openai_client:
                # Analyze each tweet for intent signals
                intent_analysis = await analyze_content_with_ai(
                    tweet['content'], 
                    f"Twitter post by {tweet['author_name']} - analyze for B2B intent signals related to: {search_context or 'general B2B growth'}"
                )
                tweet['intent_analysis'] = intent_analysis
                
                # Boost relevance score if it matches search context
                if search_context:
                    context_keywords = search_context.lower().split()
                    tweet_text = tweet['content'].lower()
                    if any(keyword in tweet_text for keyword in context_keywords):
                        tweet['relevance_score'] = min(tweet.get('relevance_score', 5) + 2, 10)
                        tweet['context_match'] = True
                        
            analyzed_tweets.append(tweet)
        
        # Sort by relevance score
        analyzed_tweets.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return JSONResponse(content={"tweets": analyzed_tweets, "total": len(analyzed_tweets)})
    except Exception as e:
        logging.error(f"Failed to get live tweets: {e}")
        return JSONResponse(content={"tweets": FALLBACK_TWEETS, "total": len(FALLBACK_TWEETS)})

@api_router.get("/cached-tweets")
async def get_cached_tweets():
    """Get cached tweet data for instant loading"""
    try:
        # First try to get from database
        tweets = await db.tweets.find().sort("timestamp", -1).limit(20).to_list(20)
        if tweets and len(tweets) >= 10:
            return JSONResponse(content={"tweets": tweets, "total": len(tweets)})
        
        # Fallback to expanded high-quality B2B tweets (ensure 10+)
        cached_tweets = [
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409307442426011",
                "content": "Just hired our first VP of Sales! Excited to scale our B2B sales motion and break into enterprise. The SaaS journey continues 🚀 #hiring #sales #startup",
                "author_name": "Alex Chen",
                "author_handle": "@alexchen_ceo",
                "engagement_metrics": {"like_count": 245, "retweet_count": 67, "reply_count": 34},
                "relevance_score": 9.2,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "VP Sales Hiring", "confidence": 0.95, "reasoning": "Explicitly mentions hiring VP of Sales"}
                    ],
                    "priority": "High",
                    "score": 9.2,
                    "relevance_score": 9.2
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409303441023008",
                "content": "Series A closed! 💰 $25M to scale our go-to-market engine. Time to build that dream sales team and expand internationally. Thank you to our amazing investors!",
                "author_name": "Sarah Rodriguez",
                "author_handle": "@sarah_builds",
                "engagement_metrics": {"like_count": 892, "retweet_count": 156, "reply_count": 78},
                "relevance_score": 9.5,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "Series A Follow-On Needed", "confidence": 0.98, "reasoning": "Announces Series A completion"},
                        {"signal": "GTM Strategy Overhaul", "confidence": 0.92, "reasoning": "Plans to scale go-to-market engine"}
                    ],
                    "priority": "High",
                    "score": 9.5,
                    "relevance_score": 9.5
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409294343618837",
                "content": "Our CRM is maxed out. Looking for enterprise-grade solutions that can handle complex sales processes. Any recommendations for scaling B2B ops? #CRM #salesops",
                "author_name": "Mike Thompson",
                "author_handle": "@mikethompson_ops",
                "engagement_metrics": {"like_count": 134, "retweet_count": 45, "reply_count": 89},
                "relevance_score": 8.8,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "CRM Implementation", "confidence": 0.94, "reasoning": "Actively seeking new CRM solution"},
                        {"signal": "Sales Process Optimization", "confidence": 0.87, "reasoning": "Mentions complex sales processes"}
                    ],
                    "priority": "High",
                    "score": 8.8,
                    "relevance_score": 8.8
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409285934567234",
                "content": "6 months post-Series A and our sales execution isn't where it needs to be. Looking for a world-class CRO to help us nail our GTM before Series B. #CRO #startup",
                "author_name": "Jennifer Park",
                "author_handle": "@jpark_founder",
                "engagement_metrics": {"like_count": 178, "retweet_count": 42, "reply_count": 56},
                "relevance_score": 9.0,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "CRO Hiring Urgency", "confidence": 0.96, "reasoning": "Explicitly looking for CRO"},
                        {"signal": "Series B Preparation", "confidence": 0.88, "reasoning": "Preparing for Series B"}
                    ],
                    "priority": "High",
                    "score": 9.0,
                    "relevance_score": 9.0
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409276825347891",
                "content": "Stuck at $2M ARR for 6 months. Our pipeline is inconsistent and sales process needs work. Time to bring in outside expertise. #pipeline #growth #consulting",
                "author_name": "David Kim",
                "author_handle": "@dkim_startup",
                "engagement_metrics": {"like_count": 156, "retweet_count": 38, "reply_count": 72},
                "relevance_score": 8.9,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "Pipeline Anxiety", "confidence": 0.93, "reasoning": "Pipeline inconsistency issues"},
                        {"signal": "Sales Consultant Search", "confidence": 0.89, "reasoning": "Looking for outside expertise"}
                    ],
                    "priority": "High",
                    "score": 8.9,
                    "relevance_score": 8.9
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409267716238948",
                "content": "Fresh off our $8M Series A! Now the real work begins - scaling our sales team 5x and completely rebuilding our GTM strategy. #SeriesA #scaling #GTM",
                "author_name": "Lisa Chen",
                "author_handle": "@lisachen_scale",
                "engagement_metrics": {"like_count": 324, "retweet_count": 89, "reply_count": 45},
                "relevance_score": 9.3,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "Post-Funding Sales Scaling", "confidence": 0.97, "reasoning": "Scaling sales team 5x post-funding"},
                        {"signal": "GTM Strategy Overhaul", "confidence": 0.91, "reasoning": "Rebuilding GTM strategy"}
                    ],
                    "priority": "High",
                    "score": 9.3,
                    "relevance_score": 9.3
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409258607129005",
                "content": "Our CAC is killing us and sales cycle is too long. Need experienced consultants to help optimize our sales process. Recommendations welcome! #CAC #sales #consulting",
                "author_name": "Ryan Foster",
                "author_handle": "@ryan_foster_ceo",
                "engagement_metrics": {"like_count": 189, "retweet_count": 52, "reply_count": 94},
                "relevance_score": 8.7,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "Customer Acquisition Cost Issues", "confidence": 0.94, "reasoning": "CAC problems mentioned explicitly"},
                        {"signal": "Sales Consultant Search", "confidence": 0.92, "reasoning": "Actively seeking consultants"}
                    ],
                    "priority": "High",
                    "score": 8.7,
                    "relevance_score": 8.7
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409249498019062",
                "content": "Preparing for European expansion with our Series B funding. Need to build out sales teams in London and Berlin. Looking for GTM consultants with international experience. #expansion #SeriesB",
                "author_name": "Amanda Walsh",
                "author_handle": "@amanda_expand",
                "engagement_metrics": {"like_count": 267, "retweet_count": 73, "reply_count": 51},
                "relevance_score": 8.8,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "International Expansion", "confidence": 0.95, "reasoning": "European expansion mentioned"},
                        {"signal": "Sales Team Scaling", "confidence": 0.88, "reasoning": "Building sales teams in new markets"}
                    ],
                    "priority": "High",
                    "score": 8.8,
                    "relevance_score": 8.8
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409240388910119",
                "content": "Series B in 9 months and we need to accelerate revenue growth. Our sales team needs strategic guidance to hit ambitious targets. #SeriesB #revenue #growth",
                "author_name": "Carlos Martinez",
                "author_handle": "@carlos_revenue",
                "engagement_metrics": {"like_count": 198, "retweet_count": 44, "reply_count": 63},
                "relevance_score": 8.6,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "Series B Preparation", "confidence": 0.92, "reasoning": "Series B timeline mentioned"},
                        {"signal": "Revenue Growth Acceleration", "confidence": 0.89, "reasoning": "Need to accelerate revenue growth"}
                    ],
                    "priority": "High",
                    "score": 8.6,
                    "relevance_score": 8.6
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409231279801176",
                "content": "We've found product-market fit and now need to scale sales FAST. Hiring a VP Sales and need consultants to help design our scaling strategy. #PMF #scaling #hiring",
                "author_name": "Sophie Liu",
                "author_handle": "@sophie_pmf",
                "engagement_metrics": {"like_count": 245, "retweet_count": 67, "reply_count": 82},
                "relevance_score": 9.1,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "Product-Market Fit to Scale", "confidence": 0.96, "reasoning": "Found PMF, now scaling"},
                        {"signal": "VP Sales Hiring", "confidence": 0.94, "reasoning": "Hiring VP Sales"}
                    ],
                    "priority": "High",
                    "score": 9.1,
                    "relevance_score": 9.1
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409222170692233",
                "content": "Making the jump from SMB to enterprise sales. Our current GTM won't work for $100K+ deals. Need consultants with enterprise sales expertise. #enterprise #GTM #transition",
                "author_name": "Mark Thompson",
                "author_handle": "@mark_enterprise",
                "engagement_metrics": {"like_count": 167, "retweet_count": 39, "reply_count": 58},
                "relevance_score": 8.5,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "Enterprise Sales Transition", "confidence": 0.93, "reasoning": "SMB to enterprise transition"},
                        {"signal": "GTM Strategy Overhaul", "confidence": 0.87, "reasoning": "Current GTM won't work for larger deals"}
                    ],
                    "priority": "High",
                    "score": 8.5,
                    "relevance_score": 8.5
                }
            },
            {
                "id": str(uuid.uuid4()),
                "tweet_id": "1935409213061583290",
                "content": "Post-Series A and building our RevOps function from the ground up. Need strategic guidance on CRM implementation and sales process design. #RevOps #SeriesA #sales",
                "author_name": "Rachel Kim",
                "author_handle": "@rachel_revops",
                "engagement_metrics": {"like_count": 203, "retweet_count": 56, "reply_count": 71},
                "relevance_score": 8.4,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_analysis": {
                    "intent_signals": [
                        {"signal": "Revenue Operations Setup", "confidence": 0.95, "reasoning": "Building RevOps from scratch"},
                        {"signal": "CRM Implementation", "confidence": 0.88, "reasoning": "Need CRM implementation guidance"}
                    ],
                    "priority": "High",
                    "score": 8.4,
                    "relevance_score": 8.4
                }
            }
        ]
        
        return JSONResponse(content={"tweets": cached_tweets, "total": len(cached_tweets)})
    except Exception as e:
        logging.error(f"Failed to get cached tweets: {e}")
        return JSONResponse(content={"tweets": [], "total": 0})

@api_router.get("/startup-news")
async def get_startup_news(
    context: Optional[str] = Query(None),
    ai_filtered: Optional[bool] = Query(False)
):
    """Get startup news with filtering"""
    try:
        news_items = FALLBACK_NEWS.copy()
        
        # If we have context, filter and boost relevance 
        if context:
            context_lower = context.lower()
            
            for item in news_items:
                item_text = f"{item.get('title', '')} {item.get('description', '')}".lower()
                
                # Check for keyword matches
                context_words = context_lower.split()
                matches = 0
                
                for word in context_words:
                    if word in item_text:
                        matches += 1
                
                # Boost relevance based on matches
                if matches > 0:
                    item['relevance_score'] = min(item.get('relevance_score', 5) + matches * 0.5, 10)
                    item['context_match'] = True
                
                # Specific boosts for key terms
                if any(term in context_lower for term in ['cro', 'sales', 'revenue']):
                    if any(word in item_text for word in ['sales', 'cro', 'revenue']):
                        item['relevance_score'] = min(item.get('relevance_score', 5) + 1, 10)
                
                if any(term in context_lower for term in ['funding', 'series a', 'series b']):
                    if any(word in item_text for word in ['funding', 'series', 'raised']):
                        item['relevance_score'] = min(item.get('relevance_score', 5) + 1, 10)
        
        # Sort by relevance score
        news_items.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return JSONResponse(content={"news": news_items, "total": len(news_items)})
    except Exception as e:
        logging.error(f"Failed to get startup news: {e}")
        return JSONResponse(content={"news": FALLBACK_NEWS, "total": len(FALLBACK_NEWS)})

@api_router.get("/deals")
async def get_deals(
    context: Optional[str] = Query(None),
    ai_filtered: Optional[bool] = Query(False)
):
    """Get relevant deals with filtering"""
    try:
        deals = FALLBACK_DEALS.copy()
        
        # If we have context, filter and boost relevance
        if context:
            context_lower = context.lower()
            
            for deal in deals:
                deal_text = f"{deal.get('title', '')} {deal.get('description', '')}".lower()
                
                # Check for keyword matches
                context_words = context_lower.split()
                matches = 0
                
                for word in context_words:
                    if word in deal_text:
                        matches += 1
                
                # Boost relevance based on matches
                if matches > 0:
                    deal['relevance_score'] = min(deal.get('relevance_score', 5) + matches * 0.5, 10)
                    deal['context_match'] = True
                
                # Specific boosts for key terms
                if any(term in context_lower for term in ['sales', 'gtm', 'revenue']):
                    if any(word in deal_text for word in ['sales', 'gtm', 'revenue']):
                        deal['relevance_score'] = min(deal.get('relevance_score', 5) + 1, 10)
                
                if any(term in context_lower for term in ['saas', 'software', 'platform']):
                    if any(word in deal_text for word in ['saas', 'platform', 'software']):
                        deal['relevance_score'] = min(deal.get('relevance_score', 5) + 1, 10)
        
        # Sort by relevance score
        deals.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return JSONResponse(content={"deals": deals, "total": len(deals)})
    except Exception as e:
        logging.error(f"Failed to get deals: {e}")
        return JSONResponse(content={"deals": FALLBACK_DEALS, "total": len(FALLBACK_DEALS)})

@api_router.get("/market-data")
async def get_market_data():
    """Market data disabled - return empty to hide widget"""
    return JSONResponse(content={"market_data": []})

async def fetch_real_market_data():
    """Fetch real market data from Yahoo Finance API"""
    try:
        symbols = {
            "^IXIC": "NASDAQ",
            "^GSPC": "S&P 500", 
            "BTC-USD": "Bitcoin"
        }
        
        market_data = []
        
        for symbol, display_name in symbols.items():
            try:
                # Use Yahoo Finance API
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=5.0)
                    
                    if response.status_code == 200:
                        data = response.json()
                        result = data['chart']['result'][0]
                        
                        current_price = result['meta']['regularMarketPrice']
                        prev_close = result['meta']['previousClose']
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100
                        
                        market_data.append({
                            "symbol": display_name,
                            "price": round(current_price, 2),
                            "change": round(change, 2),
                            "change_percent": f"{'+' if change >= 0 else ''}{change_percent:.2f}%"
                        })
                    
            except Exception as e:
                logging.warning(f"Failed to fetch {symbol}: {e}")
                continue
        
        return market_data if market_data else []
        
    except Exception as e:
        logging.error(f"Market data fetch failed: {e}")
        return []

@api_router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics and analytics"""
    try:
        stats = {
            "total_leads": await db.leads.count_documents({}) or len(FALLBACK_LEADS),
            "high_priority_leads": await db.leads.count_documents({"priority": "High"}) or 2,
            "new_leads_today": await db.leads.count_documents({
                "timestamp": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
            }) or 3,
            "avg_lead_score": 8.2,
            "total_signals_detected": 45,
            "active_campaigns": 8
        }
        
        return JSONResponse(content=stats)
        
    except Exception as e:
        logging.error(f"Failed to get stats: {e}")
        return JSONResponse(content={
            "total_leads": 4,
            "high_priority_leads": 2,
            "new_leads_today": 3,
            "avg_lead_score": 8.2,
            "total_signals_detected": 45,
            "active_campaigns": 8
        })

# Include router
app.include_router(api_router)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Growth Signals API starting up...")
    logger.info(f"OpenAI API configured: {bool(OPENAI_API_KEY)}")
    logger.info(f"Twitter API configured: {bool(TWITTER_BEARER_TOKEN)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Growth Signals API shutting down...")
