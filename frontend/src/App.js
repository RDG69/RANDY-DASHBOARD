import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { 
  Search, ExternalLink, Twitter, Linkedin, 
  TrendingUp, Users, Calendar, Star, Activity, ArrowUpRight
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [leads, setLeads] = useState([]);
  const [tweets, setTweets] = useState([]);
  const [news, setNews] = useState([]);
  const [deals, setDeals] = useState([]);
  const [stats, setStats] = useState({});
  const [targetingInput, setTargetingInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [tweetsLoading, setTweetsLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [showPdfPrompt, setShowPdfPrompt] = useState(false);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setTweetsLoading(true);
      
      // Load all data in parallel
      const [leadsRes, tweetsRes, newsRes, dealsRes, statsRes] = await Promise.all([
        axios.get(`${API}/leads`),
        axios.get(`${API}/cached-tweets`),
        axios.get(`${API}/startup-news`),
        axios.get(`${API}/deals`),
        axios.get(`${API}/stats`)
      ]);

      setLeads(leadsRes.data.leads || []);
      setTweets(tweetsRes.data.tweets || []);
      setNews(newsRes.data.news || []);
      setDeals(dealsRes.data.deals || []);
      setStats(statsRes.data);
      
    } catch (error) {
      console.error("Error loading initial data:", error);
    } finally {
      setLoading(false);
      setTweetsLoading(false);
    }
  };

  const handleSmartAnalysis = async () => {
    if (!targetingInput.trim()) return;
    
    try {
      setAnalyzing(true);
      
      // Step 1: Use GPT to analyze the input and generate search strategy
      const analysisResponse = await axios.post(`${API}/analyze-content`, {
        content: `User is targeting: "${targetingInput}". Generate relevant search keywords for Twitter API, relevant intent signals to look for, and industry context for news filtering.`,
        company_context: "Smart targeting analysis for B2B prospecting"
      });
      
      // Step 2: Update leads based on analysis
      const leadsResponse = await axios.get(`${API}/leads`, {
        params: {
          context: targetingInput,
          ai_enhanced: true
        }
      });
      
      // Step 3: Get relevant tweets with updated search terms
      const twitterResponse = await axios.get(`${API}/live-tweets`, {
        params: {
          search_context: targetingInput,
          ai_keywords: true
        }
      });
      
      // Step 4: Get relevant news
      const newsResponse = await axios.get(`${API}/startup-news`, {
        params: {
          context: targetingInput,
          ai_filtered: true
        }
      });
      
      // Update all data
      setLeads(leadsResponse.data.leads || []);
      setTweets(twitterResponse.data.tweets || []);
      setNews(newsResponse.data.news || []);
      
      // Update stats
      const statsResponse = await axios.get(`${API}/stats`);
      setStats(statsResponse.data);
      
    } catch (error) {
      console.error("Error in smart analysis:", error);
      // Fallback to basic search if AI fails
      try {
        const leadsResponse = await axios.get(`${API}/leads`, {
          params: { role: targetingInput }
        });
        setLeads(leadsResponse.data.leads || []);
      } catch (fallbackError) {
        console.error("Fallback search also failed:", fallbackError);
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "High": return "text-red-600 bg-red-50";
      case "Medium": return "text-yellow-600 bg-yellow-50";
      case "Low": return "text-green-600 bg-green-50";
      default: return "text-gray-600 bg-gray-50";
    }
  };

  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/" element={
            <div className="min-h-screen bg-gray-50">
              {/* Header */}
              <div className="bg-white shadow-sm border-b border-gray-200 print-header">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <img
                        className="h-8 w-8 mr-3"
                        src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4"
                        alt="Silver Birch Growth"
                      />
                      <div>
                        <h1 className="text-2xl font-bold text-gray-900">Prospecting for Intent</h1>
                        <p className="text-sm text-gray-600">Silver Birch Growth • B2B Intelligence Platform</p>
                      </div>
                    </div>
                    
                    {/* Purple CTA Ribbon - Hidden in print */}
                    <div className="hidden md:block no-print">
                      <a
                        href="https://9kct1c25.drwbrdg.com/sbginsiders"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white text-sm font-medium rounded-lg shadow-md hover:from-purple-700 hover:to-purple-800 transform hover:scale-105 transition-all duration-200"
                      >
                        🎁 Join our Mailer to win a trip
                        <ArrowUpRight className="ml-2 w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              {/* Smart Targeting Section */}
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="text-center mb-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">🎯 Smart AI Targeting</h3>
                    <p className="text-gray-600">Describe who you're looking for and AI will find matching prospects and signals</p>
                  </div>
                  
                  <div className="max-w-3xl mx-auto">
                    <div className="flex flex-col space-y-4">
                      <div>
                        <div className="relative">
                          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                          <input
                            type="text"
                            placeholder="e.g., Founders of startups scaling GPUs based in NA, CTOs at fintech companies raising Series A..."
                            value={targetingInput}
                            onChange={(e) => setTargetingInput(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-lg"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                handleSmartAnalysis();
                              }
                            }}
                          />
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <button
                          onClick={handleSmartAnalysis}
                          disabled={!targetingInput.trim() || analyzing}
                          className="inline-flex items-center px-8 py-3 bg-green-600 text-white font-bold text-lg rounded-lg shadow-lg hover:bg-green-700 transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                        >
                          {analyzing ? (
                            <>
                              <Activity className="w-5 h-5 mr-3 animate-spin" />
                              Analyzing & Finding Matches...
                            </>
                          ) : (
                            <>
                              🚀 GO
                            </>
                          )}
                        </button>
                        <p className="text-sm text-gray-500 mt-2">
                          {analyzing 
                            ? "AI is analyzing your targeting criteria and finding relevant prospects and signals..."
                            : "AI will find prospects, tweets, and news matching your targeting criteria"
                          }
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Main Content Grid - Leads and Tweets */}
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Leads Section (2/3 width) */}
                  <div className="lg:col-span-2">
                    <div className="bg-white rounded-lg shadow">
                      <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">High-Intent Prospects</h2>
                        <p className="text-sm text-gray-500">Companies showing growth signals {targetingInput && `for "${targetingInput}"`}</p>
                      </div>
                      <div className="overflow-x-auto">
                        {loading ? (
                          <div className="p-6">
                            <div className="space-y-4">
                              {[1,2,3,4,5].map((i) => (
                                <div key={i} className="border border-gray-200 rounded-lg p-4 animate-pulse">
                                  <div className="flex justify-between items-start mb-3">
                                    <div>
                                      <div className="h-5 w-32 bg-gray-200 rounded mb-2"></div>
                                      <div className="h-4 w-48 bg-gray-200 rounded"></div>
                                    </div>
                                    <div className="h-6 w-16 bg-gray-200 rounded"></div>
                                  </div>
                                  <div className="flex space-x-2 mb-3">
                                    <div className="h-6 w-20 bg-gray-200 rounded"></div>
                                    <div className="h-6 w-24 bg-gray-200 rounded"></div>
                                  </div>
                                  <div className="flex space-x-2">
                                    <div className="h-8 w-20 bg-gray-200 rounded"></div>
                                    <div className="h-8 w-20 bg-gray-200 rounded"></div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="p-6 space-y-4">
                            {leads.slice(0, 8).map((lead) => (
                              <div key={lead.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                <div className="flex justify-between items-start mb-3">
                                  <div>
                                    <h3 className="text-lg font-medium text-gray-900">{lead.name}</h3>
                                    <p className="text-sm text-gray-600">{lead.role} at {lead.company}</p>
                                    <p className="text-xs text-gray-500">{lead.geography}</p>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(lead.priority)}`}>
                                      {lead.priority}
                                    </span>
                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                                      {lead.score}/10
                                    </span>
                                  </div>
                                </div>
                                
                                {/* Intent Signals */}
                                <div className="flex flex-wrap gap-2 mb-3">
                                  {lead.intent_signals?.slice(0, 2).map((signal, idx) => (
                                    <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                                      {signal.signal} ({Math.round(signal.confidence * 100)}%)
                                    </span>
                                  ))}
                                </div>
                                
                                {/* Social Links */}
                                <div className="flex space-x-3">
                                  {lead.linkedin_url && (
                                    <a
                                      href={lead.linkedin_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors"
                                    >
                                      <Linkedin className="w-3 h-3 mr-1" />
                                      LinkedIn
                                    </a>
                                  )}
                                  {lead.company_website && (
                                    <a
                                      href={lead.company_website}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center px-3 py-1 bg-gray-600 text-white text-xs rounded-lg hover:bg-gray-700 transition-colors"
                                    >
                                      <ExternalLink className="w-3 h-3 mr-1" />
                                      Website
                                    </a>
                                  )}
                                  {lead.twitter_handle && (
                                    <a
                                      href={`https://twitter.com/${lead.twitter_handle.replace('@', '')}`}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center px-3 py-1 bg-blue-400 text-white text-xs rounded-lg hover:bg-blue-500 transition-colors"
                                    >
                                      <Twitter className="w-3 h-3 mr-1" />
                                      Twitter
                                    </a>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Live Tweets (1/3 width, flush and scrollable) */}
                  <div className="lg:col-span-1">
                    <div className="bg-white rounded-lg shadow h-full">
                      <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">Live GTM Signals</h2>
                        <p className="text-sm text-gray-500">Latest relevant activity {targetingInput && `for "${targetingInput.slice(0, 30)}..."`}</p>
                      </div>
                      <div className="h-96 overflow-y-auto p-4 space-y-3">
                        {tweetsLoading ? (
                          <div className="space-y-3">
                            {[1,2,3,4,5,6].map((i) => (
                              <div key={i} className="border border-gray-200 rounded-lg p-3 animate-pulse">
                                <div className="flex items-start space-x-2 mb-2">
                                  <div className="w-6 h-6 bg-gray-200 rounded-full"></div>
                                  <div>
                                    <div className="h-3 w-20 bg-gray-200 rounded mb-1"></div>
                                    <div className="h-2 w-16 bg-gray-200 rounded"></div>
                                  </div>
                                </div>
                                <div className="space-y-1">
                                  <div className="h-2 w-full bg-gray-200 rounded"></div>
                                  <div className="h-2 w-3/4 bg-gray-200 rounded"></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : tweets.filter(tweet => tweet.relevance_score > 4).slice(0, 10).map((tweet) => (
                          <div key={tweet.id} className="border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                                  <Twitter className="w-3 h-3 text-blue-600" />
                                </div>
                                <div>
                                  <p className="text-xs font-medium text-gray-900">{tweet.author_name}</p>
                                  <p className="text-xs text-gray-500">{tweet.author_handle}</p>
                                </div>
                              </div>
                              <span className="text-xs text-green-600 font-medium">
                                {tweet.relevance_score}/10
                              </span>
                            </div>
                            <p className="text-xs text-gray-600 mb-2 line-clamp-3">{tweet.content}</p>
                            
                            {tweet.intent_analysis?.intent_signals && tweet.intent_analysis.intent_signals.length > 0 && (
                              <div className="mb-2">
                                {tweet.intent_analysis.intent_signals.slice(0, 1).map((signal, idx) => (
                                  <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                                    {signal.signal}
                                  </span>
                                ))}
                              </div>
                            )}
                            
                            <div className="flex items-center justify-between text-xs text-gray-500">
                              <div className="flex space-x-3">
                                <span>❤️ {tweet.engagement_metrics?.like_count || 0}</span>
                                <span>🔄 {tweet.engagement_metrics?.retweet_count || 0}</span>
                              </div>
                              <span className="text-gray-400">2h</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* News Section */}
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900">Growth Stage News</h2>
                    <p className="text-sm text-gray-500">Latest startup and business intelligence {targetingInput && `related to "${targetingInput}"`}</p>
                  </div>
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {news.slice(0, 6).map((item, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                          <h3 className="text-sm font-medium text-gray-900 mb-2">{item.title}</h3>
                          <p className="text-xs text-gray-600 mb-2">{item.description}</p>
                          <div className="flex justify-between items-center text-xs text-gray-500">
                            <span>{item.source}</span>
                            <span>{item.relevance_score}/10</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;