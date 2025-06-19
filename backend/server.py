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

# FALLBACK DATA (for when GPT fails)
FALLBACK_LEADS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Alex Johnson", 
        "role": "Business Owner",
        "company": "Growth Solutions",
        "geography": "Denver, CO",
        "social_content": "Looking to scale our operations and improve our processes.",
        "score": 7.0,
        "priority": "Medium",
        "linkedin_url": "https://linkedin.com/in/alex-johnson",
        "company_website": "https://growth-solutions.com"
    }
]

def generate_contextual_content(search_context: str, content_type: str) -> List[Dict]:
    """Generate new content based on search context using GPT"""
    if not openai_client:
        return FALLBACK_LEADS if content_type == "leads" else []
    
    try:
        if content_type == "leads":
            prompt = f"""
            Generate 5 realistic business prospects for: "{search_context}"
            
            Return ONLY valid JSON array:
            [{{
                "id": "{str(uuid.uuid4())}",
                "name": "First Last",
                "role": "Job Title", 
                "company": "Company Name",
                "geography": "City, State",
                "social_content": "Brief post about their business challenges or growth needs",
                "score": 8.2,
                "priority": "High",
                "linkedin_url": "https://linkedin.com/in/firstname-lastname",
                "company_website": "https://companyname.com"
            }}]
            
            Make it specific to "{search_context}" industry and needs.
            """
        
        elif content_type == "news":
            prompt = f"""
            Generate 4 realistic industry news articles for: "{search_context}"
            
            Return ONLY valid JSON array:
            [{{
                "title": "Industry News Title",
                "description": "Brief description of the news",
                "source": "Industry Source",
                "relevance_score": 8.5
            }}]
            
            Make it relevant to "{search_context}" industry.
            """
        
        elif content_type == "deals":
            prompt = f"""
            Generate 3 realistic business deals/acquisitions for: "{search_context}"
            
            Return ONLY valid JSON array:
            [{{
                "title": "Deal/Acquisition Title",
                "description": "Brief description of the deal",
                "type": "M&A",
                "amount": "$5M",
                "company": "Company Name",
                "relevance_score": 8.0
            }}]
            
            Make it relevant to "{search_context}" industry.
            """
        
        elif content_type == "tweets":
            prompt = f"""
            Generate 4 realistic social media posts for: "{search_context}"
            
            Return ONLY valid JSON array:
            [{{
                "id": "{str(uuid.uuid4())}",
                "content": "Social media post content about business challenges",
                "author_name": "Author Name",
                "author_handle": "@authorname",
                "engagement_metrics": {{"like_count": 25, "retweet_count": 8}},
                "relevance_score": 7.5
            }}]
            
            Make it relevant to "{search_context}" industry and business needs.
            """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7,
            timeout=15
        )
        
        try:
            content = response.choices[0].message.content.strip()
            # Clean up any markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            new_content = json.loads(content)
            if isinstance(new_content, list) and len(new_content) > 0:
                logging.info(f"Generated {len(new_content)} {content_type} items for '{search_context}'")
                return new_content
        except json.JSONDecodeError as e:
            logging.warning(f"GPT returned invalid JSON for {content_type}: {e}")
            logging.warning(f"Raw response: {response.choices[0].message.content}")
            
    except Exception as e:
        logging.error(f"{content_type} generation failed: {e}")
    
    # Return fallback
    if content_type == "leads":
        return FALLBACK_LEADS
    return []

# SIMPLE API ENDPOINTS
@app.get("/api/")
async def root():
    return {"message": "Growth Signals API v1.0.0", "status": "operational"}

@app.get("/api/leads")
async def get_leads(context: Optional[str] = Query(None)):
    """Get leads - generate new ones if context provided"""
    try:
        if context and context.strip():
            # Generate new leads based on context
            leads = generate_contextual_content(context.strip(), "leads")
        else:
            # Return fallback
            leads = FALLBACK_LEADS
        
        return JSONResponse(content={"leads": leads, "total": len(leads)})
    except Exception as e:
        logging.error(f"Leads API failed: {e}")
        return JSONResponse(content={"leads": FALLBACK_LEADS, "total": len(FALLBACK_LEADS)})

@app.get("/api/startup-news")
async def get_news(context: Optional[str] = Query(None)):
    """Get news - generate new ones if context provided"""
    try:
        if context and context.strip():
            news = generate_contextual_content(context.strip(), "news")
        else:
            news = []
        
        return JSONResponse(content={"news": news, "total": len(news)})
    except Exception as e:
        logging.error(f"News API failed: {e}")
        return JSONResponse(content={"news": [], "total": 0})

@app.get("/api/deals")
async def get_deals(context: Optional[str] = Query(None)):
    """Get deals - generate new ones if context provided"""
    try:
        if context and context.strip():
            deals = generate_contextual_content(context.strip(), "deals")
        else:
            deals = []
        
        return JSONResponse(content={"deals": deals, "total": len(deals)})
    except Exception as e:
        logging.error(f"Deals API failed: {e}")
        return JSONResponse(content={"deals": [], "total": 0})

@app.get("/api/cached-tweets")
async def get_tweets(context: Optional[str] = Query(None)):
    """Get tweets - generate new ones if context provided"""
    try:
        if context and context.strip():
            tweets = generate_contextual_content(context.strip(), "tweets")
        else:
            tweets = []
        
        return JSONResponse(content={"tweets": tweets, "total": len(tweets)})
    except Exception as e:
        logging.error(f"Tweets API failed: {e}")
        return JSONResponse(content={"tweets": [], "total": 0})

@app.get("/api/stats")
async def get_stats():
    """Get simple stats"""
    return JSONResponse(content={
        "total_leads": 5,
        "total_tweets": 4, 
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
        score = 5  # Default score
        
        # Simple keyword detection
        if any(word in content for word in ["cro", "chief revenue", "vp sales", "sales director"]):
            signals.append({"signal": "Sales Leadership Hiring", "confidence": 0.8})
            score += 2
        if any(word in content for word in ["scaling", "scale", "growth", "expand"]):
            signals.append({"signal": "Business Scaling", "confidence": 0.7})
            score += 2
        if any(word in content for word in ["hiring", "recruiting", "staff"]):
            signals.append({"signal": "Team Expansion", "confidence": 0.75})
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