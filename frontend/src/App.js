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
    console.log("GO button clicked! Input:", targetingInput);
    if (!targetingInput.trim()) {
      console.log("No input provided, returning early");
      return;
    }
    
    try {
      console.log("Starting analysis...");
      setAnalyzing(true);
      
      console.log("Making API calls...");
      // Load all data sections immediately without AI delays
      const [leadsResponse, tweetsResponse, newsResponse, dealsResponse, statsResponse] = await Promise.all([
        // Basic leads filtering (fast)
        axios.get(`${API}/leads`, {
          params: { context: targetingInput }
        }),
        // Use cached tweets for speed
        axios.get(`${API}/cached-tweets`),
        // Basic news filtering
        axios.get(`${API}/startup-news`, {
          params: { context: targetingInput }
        }),
        // Basic deals filtering  
        axios.get(`${API}/deals`, {
          params: { context: targetingInput }
        }),
        // Stats
        axios.get(`${API}/stats`)
      ]);
      
      console.log("API calls completed, updating data...");
      // Update all data immediately
      setLeads(leadsResponse.data.leads || []);
      setTweets(tweetsResponse.data.tweets || []);
      setNews(newsResponse.data.news || []);
      setDeals(dealsResponse.data.deals || []);
      setStats(statsResponse.data);
      
      console.log("Data updated successfully!");
      
    } catch (error) {
      console.error("Error in smart analysis:", error);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGetMore = () => {
    setShowPdfPrompt(true);
  };

  const handlePdfPromptResponse = (downloadPdf) => {
    setShowPdfPrompt(false);
    
    if (downloadPdf) {
      // Show PDF instruction
      alert("Press Ctrl+P (Cmd+P on Mac) to save current results as PDF. The page is optimized for single-page printing.");
      setTimeout(() => {
        window.print();
      }, 1000);
    }
    
    // Refresh data after PDF handling
    setTimeout(() => {
      handleSmartAnalysis();
    }, downloadPdf ? 3000 : 0);
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

              {/* Hot Deals & News - MOVED TO TOP */}
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Hot Deals Section */}
                  <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-lg shadow border-l-4 border-red-500">
                    <div className="px-6 py-4 bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-t-lg">
                      <h2 className="text-lg font-bold flex items-center">
                        🔥 Hot Deals & M&A Activity
                        <span className="ml-2 px-2 py-1 bg-white bg-opacity-20 rounded-full text-xs">LIVE</span>
                      </h2>
                      <p className="text-sm opacity-90">Latest funding & acquisition activity {targetingInput && `for "${targetingInput.slice(0, 30)}..."`}</p>
                    </div>
                    <div className="p-4 max-h-96 overflow-y-auto">
                      <div className="space-y-3">
                        {deals.slice(0, 4).map((deal, index) => (
                          <div key={index} className="bg-white rounded-lg p-3 shadow-sm border hover:shadow-md transition-shadow">
                            <div className="flex items-start justify-between mb-2">
                              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                                deal.type === 'M&A' ? 'bg-red-100 text-red-800' :
                                deal.type === 'Financing' ? 'bg-green-100 text-green-800' :
                                'bg-blue-100 text-blue-800'
                              }`}>
                                {deal.type}
                              </div>
                              <span className="text-xs font-bold text-green-600">{deal.amount}</span>
                            </div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-1">{deal.title}</h4>
                            <p className="text-xs text-gray-600 mb-2 line-clamp-2">{deal.description}</p>
                            <div className="flex justify-between items-center text-xs text-gray-500">
                              <span className="font-medium">{deal.company}</span>
                              <span className="text-orange-600 font-bold">{deal.relevance_score}/10</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Growth Intelligence News */}
                  <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg shadow border-l-4 border-purple-500">
                    <div className="px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-t-lg">
                      <h2 className="text-lg font-bold flex items-center">
                        📈 Growth Intelligence
                        <span className="ml-2 px-2 py-1 bg-white bg-opacity-20 rounded-full text-xs">TRENDING</span>
                      </h2>
                      <p className="text-sm opacity-90">Latest startup & business intel {targetingInput && `for "${targetingInput.slice(0, 30)}..."`}</p>
                    </div>
                    <div className="p-4 max-h-96 overflow-y-auto">
                      <div className="space-y-3">
                        {news.slice(0, 4).map((item, index) => (
                          <div key={index} className="bg-white rounded-lg p-3 shadow-sm border hover:shadow-md transition-shadow">
                            <h4 className="text-sm font-semibold text-gray-900 mb-1 line-clamp-2">{item.title}</h4>
                            <p className="text-xs text-gray-600 mb-2 line-clamp-2">{item.description}</p>
                            <div className="flex justify-between items-center text-xs text-gray-500">
                              <span className="font-medium">{item.source}</span>
                              <span className="text-purple-600 font-bold">{item.relevance_score}/10</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Main Content Grid - Leads and GTM Signals - COMPACT & FLUSH */}
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 items-start">
                  
                  {/* High-Intent Prospects (3/5 width) - COMPACT */}
                  <div className="lg:col-span-3">
                    <div className="bg-white rounded-lg shadow">
                      <div className="px-6 py-3 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
                        <h2 className="text-lg font-bold text-gray-900 flex items-center">
                          🎯 High-Intent Prospects
                          <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">{leads.length}</span>
                        </h2>
                        <p className="text-sm text-gray-600">Companies showing growth signals {targetingInput && `for "${targetingInput.slice(0, 40)}..."`}</p>
                      </div>
                      <div className="max-h-[500px] overflow-y-auto">
                        {loading ? (
                          <div className="p-4">
                            <div className="space-y-3">
                              {[1,2,3,4].map((i) => (
                                <div key={i} className="border border-gray-200 rounded-lg p-3 animate-pulse">
                                  <div className="flex justify-between items-start mb-2">
                                    <div>
                                      <div className="h-4 w-32 bg-gray-200 rounded mb-1"></div>
                                      <div className="h-3 w-48 bg-gray-200 rounded"></div>
                                    </div>
                                    <div className="h-5 w-12 bg-gray-200 rounded"></div>
                                  </div>
                                  <div className="flex space-x-2">
                                    <div className="h-5 w-16 bg-gray-200 rounded"></div>
                                    <div className="h-5 w-20 bg-gray-200 rounded"></div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="p-4 space-y-3">
                            {leads.slice(0, 8).map((lead) => (
                              <div key={lead.id} className="border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow hover:bg-gray-50">
                                <div className="flex justify-between items-start mb-2">
                                  <div className="flex-1">
                                    <h3 className="text-base font-semibold text-gray-900">{lead.name}</h3>
                                    <p className="text-sm text-gray-600">{lead.role} at <span className="font-medium">{lead.company}</span></p>
                                    <p className="text-xs text-gray-500">{lead.geography}</p>
                                  </div>
                                  <div className="flex items-center space-x-2 ml-4">
                                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${getPriorityColor(lead.priority)}`}>
                                      {lead.priority}
                                    </span>
                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold">
                                      {lead.score}/10
                                    </span>
                                  </div>
                                </div>
                                
                                {/* Intent Signals - COMPACT */}
                                <div className="flex flex-wrap gap-1 mb-2">
                                  {lead.intent_signals?.slice(0, 2).map((signal, idx) => (
                                    <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800 font-medium">
                                      {signal.signal}
                                    </span>
                                  ))}
                                </div>
                                
                                {/* Social Links - COMPACT */}
                                <div className="flex space-x-2">
                                  {lead.linkedin_url && (
                                    <a
                                      href={lead.linkedin_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
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
                                      className="inline-flex items-center px-2 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700 transition-colors"
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
                                      className="inline-flex items-center px-2 py-1 bg-blue-400 text-white text-xs rounded hover:bg-blue-500 transition-colors"
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

                  {/* Live GTM Signals (2/5 width) - FLUSH & COMPACT */}
                  <div className="lg:col-span-2">
                    <div className="bg-white rounded-lg shadow">
                      <div className="px-6 py-3 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-cyan-50">
                        <h2 className="text-lg font-bold text-gray-900 flex items-center">
                          📡 Live GTM Signals
                          <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">LIVE</span>
                        </h2>
                        <p className="text-sm text-gray-600">Real-time activity {targetingInput && `for "${targetingInput.slice(0, 25)}..."`}</p>
                      </div>
                      <div className="max-h-[500px] overflow-y-auto p-3 space-y-2">
                        {tweetsLoading ? (
                          <div className="space-y-2">
                            {[1,2,3,4,5].map((i) => (
                              <div key={i} className="border border-gray-200 rounded-lg p-2 animate-pulse">
                                <div className="flex items-start space-x-2 mb-2">
                                  <div className="w-5 h-5 bg-gray-200 rounded-full"></div>
                                  <div>
                                    <div className="h-3 w-16 bg-gray-200 rounded mb-1"></div>
                                    <div className="h-2 w-12 bg-gray-200 rounded"></div>
                                  </div>
                                </div>
                                <div className="space-y-1">
                                  <div className="h-2 w-full bg-gray-200 rounded"></div>
                                  <div className="h-2 w-3/4 bg-gray-200 rounded"></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : tweets.filter(tweet => tweet.relevance_score > 4).slice(0, 12).map((tweet) => (
                          <div key={tweet.id} className="border border-gray-200 rounded-lg p-2 hover:shadow-sm transition-shadow hover:bg-gray-50">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center space-x-2 flex-1">
                                <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                  <Twitter className="w-3 h-3 text-blue-600" />
                                </div>
                                <div className="min-w-0 flex-1">
                                  <p className="text-xs font-semibold text-gray-900 truncate">{tweet.author_name}</p>
                                  <p className="text-xs text-gray-500 truncate">{tweet.author_handle}</p>
                                </div>
                              </div>
                              <span className="text-xs text-green-600 font-bold flex-shrink-0">
                                {tweet.relevance_score}/10
                              </span>
                            </div>
                            <p className="text-xs text-gray-600 mb-2 line-clamp-3">{tweet.content}</p>
                            
                            {tweet.intent_analysis?.intent_signals && tweet.intent_analysis.intent_signals.length > 0 && (
                              <div className="mb-2">
                                {tweet.intent_analysis.intent_signals.slice(0, 1).map((signal, idx) => (
                                  <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800 font-medium">
                                    {signal.signal}
                                  </span>
                                ))}
                              </div>
                            )}
                            
                            <div className="flex items-center justify-between text-xs text-gray-500">
                              <div className="flex space-x-2">
                                <span>❤️ {tweet.engagement_metrics?.like_count || 0}</span>
                                <span>🔄 {tweet.engagement_metrics?.retweet_count || 0}</span>
                              </div>
                              <span className="text-gray-400">Live</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Get More Button */}
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
                <div className="text-center">
                  <button
                    onClick={handleGetMore}
                    disabled={analyzing}
                    className="inline-flex items-center px-8 py-3 bg-purple-600 text-white font-bold text-lg rounded-lg shadow-lg hover:bg-purple-700 transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                  >
                    {analyzing ? (
                      <>
                        <Activity className="w-5 h-5 mr-3 animate-spin" />
                        Finding More...
                      </>
                    ) : (
                      <>
                        🔄 Get More Results
                      </>
                    )}
                  </button>
                  <p className="text-sm text-gray-500 mt-2">
                    Refresh with new prospects and signals matching your criteria
                  </p>
                </div>
              </div>
              {/* PDF Prompt Modal */}
              {showPdfPrompt && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                  <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">💾 Save Current Results?</h3>
                    <p className="text-gray-600 mb-6">
                      Would you like to save your current prospect results as a PDF before getting new data?
                    </p>
                    <div className="flex space-x-4">
                      <button
                        onClick={() => handlePdfPromptResponse(true)}
                        className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700"
                      >
                        📄 Yes, Save PDF First
                      </button>
                      <button
                        onClick={() => handlePdfPromptResponse(false)}
                        className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-50"
                      >
                        🔄 Just Refresh
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-3 text-center">
                      PDF will be optimized for single-page printing
                    </p>
                  </div>
                </div>
              )}
            </div>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;