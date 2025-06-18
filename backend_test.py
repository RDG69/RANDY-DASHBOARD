import requests
import json
import unittest
import sys
import os
from datetime import datetime

# Get the backend URL from the frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.strip().split('=')[1].strip('"\'')
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

# Base URL for API requests
BASE_URL = get_backend_url()
if not BASE_URL:
    print("Error: Could not determine backend URL")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Testing API at: {API_URL}")

class GrowthSignalsAPITest(unittest.TestCase):
    """Test suite for Growth Signals API backend"""

    def test_01_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n=== Testing Root API Endpoint ===")
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200, "Root endpoint should return 200 OK")
        
        data = response.json()
        self.assertIn("message", data, "Response should contain 'message' field")
        self.assertIn("status", data, "Response should contain 'status' field")
        
        print(f"Root API Response: {data}")
        print("✅ Root API endpoint test passed")

    def test_02_leads_endpoint_no_filters(self):
        """Test the leads endpoint without filters"""
        print("\n=== Testing Leads API Endpoint (No Filters) ===")
        response = requests.get(f"{API_URL}/leads")
        self.assertEqual(response.status_code, 200, "Leads endpoint should return 200 OK")
        
        data = response.json()
        self.assertIn("leads", data, "Response should contain 'leads' field")
        self.assertIn("total", data, "Response should contain 'total' field")
        self.assertGreater(len(data["leads"]), 0, "Should return at least one lead")
        
        # Verify lead structure
        lead = data["leads"][0]
        required_fields = ["id", "company", "name", "role", "geography", "priority", 
                          "score", "intent_signals", "social_content"]
        for field in required_fields:
            self.assertIn(field, lead, f"Lead should contain '{field}' field")
        
        print(f"Found {data['total']} leads")
        print("✅ Leads API endpoint (no filters) test passed")

    def test_03_leads_endpoint_with_filters(self):
        """Test the leads endpoint with various filters"""
        print("\n=== Testing Leads API Endpoint (With Filters) ===")
        
        # Test role filter
        response = requests.get(f"{API_URL}/leads?role=CEO")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["total"] > 0:
            for lead in data["leads"]:
                self.assertIn("CEO", lead["role"], "Filtered leads should contain 'CEO' in role")
        print("✅ Role filter test passed")
        
        # Test geography filter
        response = requests.get(f"{API_URL}/leads?geography=North America")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["total"] > 0:
            for lead in data["leads"]:
                self.assertEqual("North America", lead["geography"], 
                                "Filtered leads should have 'North America' geography")
        print("✅ Geography filter test passed")
        
        # Test priority filter
        response = requests.get(f"{API_URL}/leads?priority=High")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["total"] > 0:
            for lead in data["leads"]:
                self.assertEqual("High", lead["priority"], 
                                "Filtered leads should have 'High' priority")
        print("✅ Priority filter test passed")
        
        # Test min_score filter
        min_score = 8.0
        response = requests.get(f"{API_URL}/leads?min_score={min_score}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["total"] > 0:
            for lead in data["leads"]:
                self.assertGreaterEqual(lead["score"], min_score, 
                                      f"Filtered leads should have score >= {min_score}")
        print("✅ Min score filter test passed")
        
        # Test combined filters
        response = requests.get(f"{API_URL}/leads?priority=High&min_score=8.0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["total"] > 0:
            for lead in data["leads"]:
                self.assertEqual("High", lead["priority"])
                self.assertGreaterEqual(lead["score"], 8.0)
        print("✅ Combined filters test passed")

    def test_04_live_tweets_endpoint(self):
        """Test the live tweets endpoint"""
        print("\n=== Testing Live Tweets API Endpoint ===")
        response = requests.get(f"{API_URL}/live-tweets")
        self.assertEqual(response.status_code, 200, "Live tweets endpoint should return 200 OK")
        
        data = response.json()
        self.assertIn("tweets", data, "Response should contain 'tweets' field")
        self.assertIn("total", data, "Response should contain 'total' field")
        self.assertGreater(len(data["tweets"]), 0, "Should return at least one tweet")
        
        # Verify tweet structure
        tweet = data["tweets"][0]
        required_fields = ["id", "tweet_id", "content", "author_name", "author_handle", 
                          "engagement_metrics", "intent_analysis"]
        for field in required_fields:
            self.assertIn(field, tweet, f"Tweet should contain '{field}' field")
        
        # Verify intent analysis structure
        self.assertIn("intent_signals", tweet["intent_analysis"], 
                     "Intent analysis should contain 'intent_signals' field")
        
        print(f"Found {data['total']} live tweets with intent analysis")
        print("✅ Live tweets API endpoint test passed")

    def test_05_cached_tweets_endpoint(self):
        """Test the cached tweets endpoint"""
        print("\n=== Testing Cached Tweets API Endpoint ===")
        response = requests.get(f"{API_URL}/cached-tweets")
        self.assertEqual(response.status_code, 200, "Cached tweets endpoint should return 200 OK")
        
        data = response.json()
        self.assertIn("tweets", data, "Response should contain 'tweets' field")
        self.assertIn("total", data, "Response should contain 'total' field")
        self.assertGreater(len(data["tweets"]), 0, "Should return at least one tweet")
        
        # Verify tweet structure
        tweet = data["tweets"][0]
        required_fields = ["tweet_id", "content", "author_name", "author_handle", "engagement_metrics"]
        for field in required_fields:
            self.assertIn(field, tweet, f"Tweet should contain '{field}' field")
        
        print(f"Found {data['total']} cached tweets")
        print("✅ Cached tweets API endpoint test passed")

    def test_06_startup_news_endpoint(self):
        """Test the startup news endpoint"""
        print("\n=== Testing Startup News API Endpoint ===")
        response = requests.get(f"{API_URL}/startup-news")
        self.assertEqual(response.status_code, 200, "Startup news endpoint should return 200 OK")
        
        data = response.json()
        self.assertIn("news", data, "Response should contain 'news' field")
        self.assertIn("total", data, "Response should contain 'total' field")
        self.assertGreater(len(data["news"]), 0, "Should return at least one news item")
        
        # Verify news item structure
        news_item = data["news"][0]
        required_fields = ["title", "description", "url", "source", "category", "relevance_score"]
        for field in required_fields:
            self.assertIn(field, news_item, f"News item should contain '{field}' field")
        
        print(f"Found {data['total']} startup news items")
        print("✅ Startup news API endpoint test passed")

    def test_07_market_data_endpoint(self):
        """Test the market data endpoint"""
        print("\n=== Testing Market Data API Endpoint ===")
        response = requests.get(f"{API_URL}/market-data")
        self.assertEqual(response.status_code, 200, "Market data endpoint should return 200 OK")
        
        data = response.json()
        self.assertIn("market_data", data, "Response should contain 'market_data' field")
        self.assertGreater(len(data["market_data"]), 0, "Should return at least one market data item")
        
        # Verify market data structure
        market_item = data["market_data"][0]
        required_fields = ["symbol", "price", "change", "change_percent"]
        for field in required_fields:
            self.assertIn(field, market_item, f"Market data item should contain '{field}' field")
        
        print(f"Found {len(data['market_data'])} market data items")
        print("✅ Market data API endpoint test passed")

    def test_08_stats_endpoint(self):
        """Test the dashboard stats endpoint"""
        print("\n=== Testing Dashboard Stats API Endpoint ===")
        response = requests.get(f"{API_URL}/stats")
        self.assertEqual(response.status_code, 200, "Stats endpoint should return 200 OK")
        
        data = response.json()
        required_fields = ["total_leads", "high_priority_leads", "new_leads_today", 
                          "avg_lead_score", "total_signals_detected", "active_campaigns"]
        for field in required_fields:
            self.assertIn(field, data, f"Stats should contain '{field}' field")
        
        print("Dashboard stats data:", data)
        print("✅ Dashboard stats API endpoint test passed")

    def test_09_analyze_content_endpoint(self):
        """Test the content analysis endpoint"""
        print("\n=== Testing Content Analysis API Endpoint ===")
        
        test_content = {
            "content": "We're looking to upgrade our CRM system to better support our growing sales team. Need recommendations for enterprise solutions with strong analytics capabilities.",
            "company_context": "B2B SaaS company with 50+ sales reps, currently using basic CRM"
        }
        
        response = requests.post(f"{API_URL}/analyze-content", json=test_content)
        self.assertEqual(response.status_code, 200, "Content analysis endpoint should return 200 OK")
        
        data = response.json()
        self.assertIn("intent_signals", data, "Response should contain 'intent_signals' field")
        self.assertIn("priority", data, "Response should contain 'priority' field")
        self.assertIn("score", data, "Response should contain 'score' field")
        
        # Verify intent signals structure
        intent_signal = data["intent_signals"][0]
        required_fields = ["signal", "confidence", "reasoning"]
        for field in required_fields:
            self.assertIn(field, intent_signal, f"Intent signal should contain '{field}' field")
        
        print("Content analysis result:", data)
        print("✅ Content analysis API endpoint test passed")

    def test_10_fallback_data_system(self):
        """Test the fallback data system"""
        print("\n=== Testing Fallback Data System ===")
        
        # Test multiple endpoints to ensure they return fallback data
        endpoints = ["/leads", "/live-tweets", "/cached-tweets", "/startup-news", "/market-data", "/stats"]
        
        for endpoint in endpoints:
            response = requests.get(f"{API_URL}{endpoint}")
            self.assertEqual(response.status_code, 200, f"{endpoint} should return 200 OK with fallback data")
            
            # Verify response is not empty
            data = response.json()
            if endpoint == "/leads":
                self.assertGreater(len(data.get("leads", [])), 0, "Should return fallback leads")
            elif endpoint == "/live-tweets" or endpoint == "/cached-tweets":
                self.assertGreater(len(data.get("tweets", [])), 0, "Should return fallback tweets")
            elif endpoint == "/startup-news":
                self.assertGreater(len(data.get("news", [])), 0, "Should return fallback news")
            elif endpoint == "/market-data":
                self.assertGreater(len(data.get("market_data", [])), 0, "Should return fallback market data")
            elif endpoint == "/stats":
                self.assertGreater(len(data.keys()), 0, "Should return fallback stats")
        
        print("✅ Fallback data system test passed")

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)