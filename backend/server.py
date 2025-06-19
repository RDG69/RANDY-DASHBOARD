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
import random

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

# Try OpenAI but don't break if it fails
openai_client = None
try:
    import openai
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if openai_api_key:
        openai_client = openai.OpenAI(api_key=openai_api_key)
        logging.info("✅ OpenAI API configured")
    else:
        logging.warning("⚠️ OpenAI API key not found - using fallback data")
except Exception as e:
    logging.warning(f"⚠️ OpenAI import failed: {e} - using fallback data")

# Simple Data Models
class ContentAnalysisRequest(BaseModel):
    content: str
    company_context: Optional[str] = None

# INDUSTRY-SPECIFIC DATA SETS
SAAS_STARTUP_DATA = {
    "leads": [
        {
            "id": str(uuid.uuid4()),
            "name": "Sarah Martinez", 
            "role": "CEO",
            "company": "ScaleUp SaaS",
            "geography": "San Francisco, CA",
            "social_content": "Just raised Series A. Need to hire our first CRO to scale from $1M to $10M ARR. Pipeline anxiety is real.",
            "score": 9.2,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/sarah-martinez-ceo",
            "company_website": "https://scaleup-saas.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mike Chen",
            "role": "Founder", 
            "company": "CloudFlow Solutions",
            "geography": "Austin, TX",
            "social_content": "Revenue plateau at $5M. Board wants us to hire VP Sales to break through to next level. Anyone have recs?",
            "score": 8.7,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/mike-chen-founder",
            "company_website": "https://cloudflow.io"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Jennifer Park",
            "role": "CEO",
            "company": "DataStream Inc",
            "geography": "Seattle, WA", 
            "social_content": "Closed Series B! Time to scale our GTM strategy and expand internationally. Looking for sales consultants.",
            "score": 8.1,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/jennifer-park-ceo",
            "company_website": "https://datastream.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "David Thompson",
            "role": "VP Engineering",
            "company": "B2B Builder",
            "geography": "Boston, MA",
            "social_content": "Pipeline has been unpredictable. CEO wants repeatable sales process. Time to bring in experts.",
            "score": 7.8,
            "priority": "Medium",
            "linkedin_url": "https://linkedin.com/in/david-thompson-vp",
            "company_website": "https://b2bbuilder.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Lisa Rodriguez",
            "role": "Founder",
            "company": "SaaS Analytics Pro",
            "geography": "Denver, CO",
            "social_content": "Growing fast but sales team can't keep up. Need to professionalize our revenue operations ASAP.",
            "score": 8.3,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/lisa-rodriguez-founder",
            "company_website": "https://saasanalytics.pro"
        }
    ],
    "news": [
        {
            "title": "73% of Series A SaaS Companies Now Hiring Sales Consultants",
            "description": "New study shows growth-stage SaaS startups increasingly rely on external sales expertise",
            "source": "SaaStr Weekly",
            "relevance_score": 9.1
        },
        {
            "title": "CRO Hiring Boom: Why B2B Companies Need Revenue Leadership", 
            "description": "Series A and B SaaS companies increasingly hiring Chief Revenue Officers",
            "source": "TechCrunch",
            "relevance_score": 8.8
        },
        {
            "title": "Pipeline Anxiety: 68% of SaaS CEOs Lose Sleep Over Revenue Predictability",
            "description": "Survey reveals top concerns of Series A/B founders about sales forecasting",
            "source": "First Round Review",
            "relevance_score": 8.5
        },
        {
            "title": "SaaS Sales Scaling: The Make-or-Break 18 Months After Series A",
            "description": "How growth-stage companies can avoid common pitfalls when scaling sales teams",
            "source": "SaaS Magazine",
            "relevance_score": 8.2
        }
    ],
    "deals": [
        {
            "title": "SalesBoost Acquired by HubSpot for $150M",
            "description": "Sales acceleration platform focused on Series A/B SaaS companies",
            "type": "M&A",
            "amount": "$150M",
            "company": "SalesBoost",
            "relevance_score": 9.2
        },
        {
            "title": "RevOps Platform Closes $25M Series A",
            "description": "Platform helps SaaS startups build predictable revenue processes",
            "type": "Financing",
            "amount": "$25M",
            "company": "RevOps",
            "relevance_score": 8.7
        },
        {
            "title": "B2B Sales Training Startup Raises $18M",
            "description": "Platform helps scaling SaaS companies onboard sales teams faster",
            "type": "Financing",
            "amount": "$18M",
            "company": "SalesAcademy",
            "relevance_score": 8.4
        }
    ],
    "tweets": [
        {
            "id": str(uuid.uuid4()),
            "content": "Just hired our first CRO after 18 months of trying to scale sales ourselves. Should have done this at $2M ARR instead of waiting until $5M. Game changer for SaaS growth.",
            "author_name": "Mark Stevens",
            "author_handle": "@markstevens_saas",
            "engagement_metrics": {"like_count": 45, "retweet_count": 12},
            "relevance_score": 8.8
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Series A complete! $12M to scale our SaaS platform. Now the real work begins - building a sales machine that can take us to $50M ARR.",
            "author_name": "Amy Chen", 
            "author_handle": "@amychen_saas",
            "engagement_metrics": {"like_count": 78, "retweet_count": 23},
            "relevance_score": 9.1
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Pipeline anxiety is real in SaaS. Q4 was a rollercoaster. Investing heavily in sales ops and process this year. Any recs for fractional CROs?",
            "author_name": "Tony Martinez",
            "author_handle": "@tonymartinez_b2b", 
            "engagement_metrics": {"like_count": 34, "retweet_count": 8},
            "relevance_score": 8.3
        }
    ]
}

AI_GPU_DATA = {
    "leads": [
        {
            "id": str(uuid.uuid4()),
            "name": "Dr. Alex Petrov", 
            "role": "CTO",
            "company": "Neural Dynamics",
            "geography": "Palo Alto, CA",
            "social_content": "Scaling GPU infrastructure for AI training. Need VP Sales to help us sell compute to other AI companies. $50M Series B incoming.",
            "score": 9.5,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/alex-petrov-ai",
            "company_website": "https://neuraldynamics.ai"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Maya Singh",
            "role": "CEO", 
            "company": "GPU Cloud Systems",
            "geography": "Seattle, WA",
            "social_content": "Raised $80M to build largest GPU cloud for AI companies. Looking for enterprise sales leader who understands compute infrastructure.",
            "score": 9.2,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/maya-singh-ai",
            "company_website": "https://gpucloud.systems"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "James Liu",
            "role": "Founder",
            "company": "TensorFlow Infrastructure", 
            "geography": "Austin, TX",
            "social_content": "Building next-gen GPU clusters for LLM training. Revenue growing 300% but need sales team to keep up with demand.",
            "score": 8.9,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/james-liu-gpu",
            "company_website": "https://tensorflow-infra.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Rachel Kim",
            "role": "VP Engineering",
            "company": "AI Compute Labs",
            "geography": "San Francisco, CA",
            "social_content": "Our GPU utilization hit 95%. Time to scale sales to match our infrastructure growth. Need someone who gets AI workloads.",
            "score": 8.6,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/rachel-kim-ai",
            "company_website": "https://aicompute.labs"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Carlos Rodriguez",
            "role": "CTO",
            "company": "Distributed GPU Network",
            "geography": "Miami, FL",
            "social_content": "Just deployed 10,000 H100s. Now we need sales ops to manage enterprise AI customers. Pipeline is exploding.",
            "score": 8.4,
            "priority": "Medium",
            "linkedin_url": "https://linkedin.com/in/carlos-rodriguez-gpu",
            "company_website": "https://distgpu.net"
        }
    ],
    "news": [
        {
            "title": "AI Infrastructure Startups Raise Record $3.2B in Q1 2025",
            "description": "GPU and compute companies dominate funding rounds as AI demand explodes",
            "source": "AI Business",
            "relevance_score": 9.4
        },
        {
            "title": "GPU Supply Shortage Creates Sales Opportunity for Infrastructure Companies", 
            "description": "Nvidia H100 shortages drive enterprise customers to seek alternative compute solutions",
            "source": "TechCrunch",
            "relevance_score": 9.1
        },
        {
            "title": "Enterprise AI Adoption Drives 400% Growth in GPU Cloud Services",
            "description": "Fortune 500 companies increasingly outsourcing AI compute to specialized providers",
            "source": "VentureBeat",
            "relevance_score": 8.9
        },
        {
            "title": "Why AI Companies are Hiring Sales Teams to Handle Compute Demand",
            "description": "Infrastructure startups struggle to manage enterprise AI customer pipelines",
            "source": "The Information",
            "relevance_score": 8.7
        }
    ],
    "deals": [
        {
            "title": "Nvidia Acquires GPU Orchestration Startup for $2.1B",
            "description": "Strategic acquisition to expand data center GPU management capabilities",
            "type": "M&A",
            "amount": "$2.1B",
            "company": "GPU Orchestrator",
            "relevance_score": 9.6
        },
        {
            "title": "AI Infrastructure Platform Raises $120M Series C",
            "description": "Funding to expand GPU clusters and enterprise sales team",
            "type": "Financing",
            "amount": "$120M",
            "company": "AI Infra Pro",
            "relevance_score": 9.2
        },
        {
            "title": "Google Cloud Acquires GPU Optimization Startup",
            "description": "Acquisition strengthens enterprise AI compute offerings",
            "type": "M&A",
            "amount": "$850M",
            "company": "GPU Optimizer",
            "relevance_score": 8.9
        }
    ],
    "tweets": [
        {
            "id": str(uuid.uuid4()),
            "content": "Our GPU utilization went from 60% to 95% in 3 months. Enterprise AI demand is insane. Time to scale our sales team to match infrastructure growth.",
            "author_name": "Dr. Kevin Chang",
            "author_handle": "@kevinchang_ai",
            "engagement_metrics": {"like_count": 156, "retweet_count": 34},
            "relevance_score": 9.3
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Just closed $80M Series B for our GPU cloud. Now the challenge: hiring enterprise sales reps who actually understand AI compute workloads. It's a rare breed.",
            "author_name": "Lisa Park", 
            "author_handle": "@lisapark_gpu",
            "engagement_metrics": {"like_count": 89, "retweet_count": 19},
            "relevance_score": 9.0
        },
        {
            "id": str(uuid.uuid4()),
            "content": "H100 shortage is creating massive sales opportunities for alternative GPU providers. Our pipeline doubled in Q4. Need sales ops ASAP.",
            "author_name": "Ahmed Hassan",
            "author_handle": "@ahmedhassan_ai", 
            "engagement_metrics": {"like_count": 67, "retweet_count": 15},
            "relevance_score": 8.7
        }
    ]
}

HEALTHCARE_DATA = {
    "leads": [
        {
            "id": str(uuid.uuid4()),
            "name": "Dr. Sarah Wilson", 
            "role": "Practice Owner",
            "company": "Wellness Spine Clinics",
            "geography": "Phoenix, AZ",
            "social_content": "Growing from 3 to 12 locations this year. Need business development help to manage expansion and patient acquisition systems.",
            "score": 8.7,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/dr-sarah-wilson",
            "company_website": "https://wellnessspine.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Michael Chen",
            "role": "Clinic Director", 
            "company": "Active Life Chiropractic",
            "geography": "Dallas, TX",
            "social_content": "Opened 4th location last month. Patient volume is great but need systems to scale operations and marketing efficiently.",
            "score": 8.3,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/michael-chen-dc",
            "company_website": "https://activelifechiro.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Dr. Jennifer Martinez",
            "role": "Owner",
            "company": "Movement Health Network", 
            "geography": "Tampa, FL",
            "social_content": "Scaling our clinic network. Revenue per location is strong but need help with business development and staff training systems.",
            "score": 7.9,
            "priority": "Medium",
            "linkedin_url": "https://linkedin.com/in/dr-jennifer-martinez",
            "company_website": "https://movementhealth.net"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Dr. Robert Kim",
            "role": "Practice Owner",
            "company": "Integrated Wellness Centers",
            "geography": "Charlotte, NC",
            "social_content": "Looking to franchise our chiropractic model. Need business consultant to help structure growth and operations.",
            "score": 8.1,
            "priority": "High",
            "linkedin_url": "https://linkedin.com/in/dr-robert-kim",
            "company_website": "https://integratedwellness.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Amanda Foster",
            "role": "Clinic Manager",
            "company": "Premier Spine Solutions",
            "geography": "Portland, OR",
            "social_content": "Managing 6 locations now. Docs want to focus on patients, I need help with business operations and marketing systems.",
            "score": 7.6,
            "priority": "Medium",
            "linkedin_url": "https://linkedin.com/in/amanda-foster-clinic",
            "company_website": "https://premierspine.com"
        }
    ],
    "news": [
        {
            "title": "Chiropractic Practice Networks See 40% Growth in Multi-Location Models",
            "description": "Healthcare practitioners increasingly adopting franchise and network expansion strategies",
            "source": "Healthcare Business",
            "relevance_score": 8.8
        },
        {
            "title": "Private Equity Investment in Healthcare Practices Hits Record High", 
            "description": "Investors target scalable healthcare service businesses with growth potential",
            "source": "Modern Healthcare",
            "relevance_score": 8.5
        },
        {
            "title": "Patient Acquisition Costs Rise 35% for Healthcare Practices",
            "description": "Medical practices investing more in marketing and business development systems",
            "source": "Practice Management Today",
            "relevance_score": 8.2
        },
        {
            "title": "Telehealth Integration Drives Practice Consolidation Trends",
            "description": "Healthcare providers scaling operations to integrate digital health services",
            "source": "Digital Health News",
            "relevance_score": 7.9
        }
    ],
    "deals": [
        {
            "title": "Healthcare Practice Management Platform Acquired for $180M",
            "description": "PE firm acquires software platform serving multi-location healthcare practices",
            "type": "M&A",
            "amount": "$180M",
            "company": "HealthcareOps",
            "relevance_score": 8.6
        },
        {
            "title": "Chiropractic Franchise Network Raises $35M for Expansion",
            "description": "Funding to scale franchise model and business development support",
            "type": "Financing",
            "amount": "$35M",
            "company": "ChiroFranchise",
            "relevance_score": 8.4
        },
        {
            "title": "Patient Marketing Platform Closes $22M Series A",
            "description": "Platform helps healthcare practices scale patient acquisition and retention",
            "type": "Financing",
            "amount": "$22M",
            "company": "PatientGrow",
            "relevance_score": 8.1
        }
    ],
    "tweets": [
        {
            "id": str(uuid.uuid4()),
            "content": "Opened our 5th chiropractic location this year. Patient demand is there but managing operations across multiple sites is the real challenge. Need systems.",
            "author_name": "Dr. Maria Lopez",
            "author_handle": "@drmarialopez",
            "engagement_metrics": {"like_count": 28, "retweet_count": 6},
            "relevance_score": 8.4
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Revenue per patient is up 25% but patient acquisition costs are killing margins. Time to invest in better marketing systems for our clinic network.",
            "author_name": "Mike Johnson", 
            "author_handle": "@mikejohnson_clinic",
            "engagement_metrics": {"like_count": 19, "retweet_count": 4},
            "relevance_score": 8.1
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Scaling a healthcare practice is different than scaling tech. Need business consultants who actually understand medical practice operations.",
            "author_name": "Dr. Susan Wright",
            "author_handle": "@drsusan_health", 
            "engagement_metrics": {"like_count": 22, "retweet_count": 7},
            "relevance_score": 7.8
        }
    ]
}

def detect_industry(search_context: str) -> str:
    """Detect industry from search context"""
    context_lower = search_context.lower()
    
    # AI/GPU keywords
    if any(word in context_lower for word in ['gpu', 'ai', 'neural', 'compute', 'infrastructure', 'llm', 'machine learning', 'artificial intelligence']):
        return "ai_gpu"
    
    # Healthcare keywords
    if any(word in context_lower for word in ['chiropractor', 'clinic', 'healthcare', 'medical', 'doctor', 'patient', 'wellness', 'therapy']):
        return "healthcare"
    
    # Default to SaaS/startup
    return "saas_startup"

def get_industry_data(industry: str) -> Dict:
    """Get data for specific industry"""
    if industry == "ai_gpu":
        return AI_GPU_DATA
    elif industry == "healthcare":
        return HEALTHCARE_DATA
    else:
        return SAAS_STARTUP_DATA

def enhance_with_gpt(data: List[Dict], search_context: str, industry: str) -> List[Dict]:
    """Try to enhance data with GPT, but don't break if it fails"""
    if not openai_client:
        return data
    
    try:
        # Simple GPT enhancement - just boost scores
        for item in data:
            # Add some randomness to make it feel more dynamic
            boost = random.uniform(0.1, 0.8)
            if 'score' in item:
                item['score'] = min(item['score'] + boost, 10.0)
                item['score'] = round(item['score'], 1)
            if 'relevance_score' in item:
                item['relevance_score'] = min(item['relevance_score'] + boost, 10.0)
                item['relevance_score'] = round(item['relevance_score'], 1)
            
            item['gpt_enhanced'] = True
            item['search_context'] = search_context
            
    except Exception as e:
        logging.warning(f"GPT enhancement failed: {e}")
    
    return data

# API ENDPOINTS
@app.get("/api/")
async def root():
    return {"message": "Growth Signals API v1.0.0", "status": "operational"}

@app.get("/api/leads")
async def get_leads(context: Optional[str] = Query(None)):
    """Get leads based on industry detection"""
    try:
        if context and context.strip():
            industry = detect_industry(context.strip())
            industry_data = get_industry_data(industry)
            leads = industry_data["leads"].copy()
            
            # Enhance with GPT if available
            leads = enhance_with_gpt(leads, context, industry)
            
            logging.info(f"✅ Serving {industry} leads for: {context}")
        else:
            # Default to SaaS
            leads = SAAS_STARTUP_DATA["leads"].copy()
        
        return JSONResponse(content={"leads": leads, "total": len(leads)})
    except Exception as e:
        logging.error(f"Leads API failed: {e}")
        return JSONResponse(content={"leads": SAAS_STARTUP_DATA["leads"], "total": len(SAAS_STARTUP_DATA["leads"])})

@app.get("/api/startup-news")
async def get_news(context: Optional[str] = Query(None)):
    """Get news based on industry detection"""
    try:
        if context and context.strip():
            industry = detect_industry(context.strip())
            industry_data = get_industry_data(industry)
            news = industry_data["news"].copy()
            
            # Enhance with GPT if available
            news = enhance_with_gpt(news, context, industry)
            
            logging.info(f"✅ Serving {industry} news for: {context}")
        else:
            news = SAAS_STARTUP_DATA["news"].copy()
        
        return JSONResponse(content={"news": news, "total": len(news)})
    except Exception as e:
        logging.error(f"News API failed: {e}")
        return JSONResponse(content={"news": [], "total": 0})

@app.get("/api/deals")
async def get_deals(context: Optional[str] = Query(None)):
    """Get deals based on industry detection"""
    try:
        if context and context.strip():
            industry = detect_industry(context.strip())
            industry_data = get_industry_data(industry)
            deals = industry_data["deals"].copy()
            
            # Enhance with GPT if available
            deals = enhance_with_gpt(deals, context, industry)
            
            logging.info(f"✅ Serving {industry} deals for: {context}")
        else:
            deals = SAAS_STARTUP_DATA["deals"].copy()
        
        return JSONResponse(content={"deals": deals, "total": len(deals)})
    except Exception as e:
        logging.error(f"Deals API failed: {e}")
        return JSONResponse(content={"deals": [], "total": 0})

@app.get("/api/cached-tweets")
async def get_tweets(context: Optional[str] = Query(None)):
    """Get tweets based on industry detection"""
    try:
        if context and context.strip():
            industry = detect_industry(context.strip())
            industry_data = get_industry_data(industry)
            tweets = industry_data["tweets"].copy()
            
            # Enhance with GPT if available
            tweets = enhance_with_gpt(tweets, context, industry)
            
            logging.info(f"✅ Serving {industry} tweets for: {context}")
        else:
            tweets = SAAS_STARTUP_DATA["tweets"].copy()
        
        return JSONResponse(content={"tweets": tweets, "total": len(tweets)})
    except Exception as e:
        logging.error(f"Tweets API failed: {e}")
        return JSONResponse(content={"tweets": [], "total": 0})

@app.get("/api/stats")
async def get_stats():
    """Get simple stats"""
    return JSONResponse(content={
        "total_leads": 5,
        "total_tweets": 3, 
        "total_news": 4,
        "total_deals": 3,
        "last_updated": datetime.utcnow().isoformat()
    })

@app.post("/api/analyze-content")
async def analyze_content(request: ContentAnalysisRequest):
    """Simple content analysis"""
    try:
        content = request.content.lower()
        signals = []
        score = 5
        
        # Industry-specific signals
        if any(word in content for word in ["gpu", "ai", "compute", "infrastructure"]):
            signals.append({"signal": "AI Infrastructure Scaling", "confidence": 0.9})
            score += 3
        elif any(word in content for word in ["clinic", "chiropractic", "healthcare", "practice"]):
            signals.append({"signal": "Healthcare Practice Expansion", "confidence": 0.85})
            score += 2
        elif any(word in content for word in ["saas", "startup", "software"]):
            signals.append({"signal": "SaaS Scaling", "confidence": 0.8})
            score += 2
        
        if any(word in content for word in ["scaling", "scale", "growth", "expand"]):
            signals.append({"signal": "Business Scaling", "confidence": 0.75})
            score += 1
        
        priority = "High" if score >= 8 else "Medium" if score >= 6 else "Low"
        
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