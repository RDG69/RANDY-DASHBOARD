import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { 
  Search, Filter, ExternalLink, Twitter, Linkedin, 
  TrendingUp, TrendingDown, DollarSign, Users,
  Building, MapPin, Star, Calendar, Activity,
  BarChart3, PieChart, ArrowUpRight, Phone, Mail,
  Globe, Target
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Dashboard Component
const Dashboard = () => {
  const [leads, setLeads] = useState([]);
  const [tweets, setTweets] = useState([]);
  const [news, setNews] = useState([]);
  const [marketData, setMarketData] = useState([]);
  const [stats, setStats] = useState({});
  const [searchTerm, setSearchTerm] = useState("");
  const [customTarget, setCustomTarget] = useState("");
  const [filters, setFilters] = useState({
    role: "",
    geography: "",
    priority: "",
    minScore: ""
  });
  const [loading, setLoading] = useState(true);
  const [tweetsLoading, setTweetsLoading] = useState(true);
  const [marketLoading, setMarketLoading] = useState(true);

  // Load data on component mount with progressive loading
  useEffect(() => {
    loadCriticalDataFirst();
  }, []);

  const loadCriticalDataFirst = async () => {
    // Load most important data first (leads, stats, news)
    try {
      await Promise.all([
        loadLeads(),
        loadStats(),
        loadNews()
      ]);
      setLoading(false); // Allow user to interact with main content
      
      // Load secondary data in background
      setTimeout(() => {
        loadMarketData();
        loadTweets();
      }, 100);
    } catch (error) {
      console.error("Error loading critical data:", error);
      setLoading(false);
    }
  };

  const loadLeads = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.role) params.append("role", filters.role);
      if (filters.geography) params.append("geography", filters.geography);
      if (filters.priority) params.append("priority", filters.priority);
      if (filters.minScore) params.append("min_score", filters.minScore);

      const response = await axios.get(`${API}/leads?${params.toString()}`);
      setLeads(response.data.leads || []);
    } catch (error) {
      console.error("Error loading leads:", error);
    }
  };

  const loadTweets = async () => {
    try {
      setTweetsLoading(true);
      
      // First load cached tweets for instant display
      try {
        const cachedResponse = await axios.get(`${API}/cached-tweets`);
        setTweets(cachedResponse.data.tweets || []);
        setTweetsLoading(false); // Show cached data immediately
      } catch (error) {
        console.error("Failed to load cached tweets:", error);
      }
      
      // Then load live tweets in background
      setTimeout(async () => {
        try {
          const liveResponse = await axios.get(`${API}/live-tweets`);
          if (liveResponse.data.tweets && liveResponse.data.tweets.length > 0) {
            setTweets(liveResponse.data.tweets);
          }
        } catch (error) {
          console.error("Failed to load live tweets:", error);
        }
      }, 2000); // Wait 2 seconds before loading live data
      
    } catch (error) {
      console.error("Error loading tweets:", error);
      setTweetsLoading(false);
    }
  };

  const loadNews = async () => {
    try {
      const response = await axios.get(`${API}/startup-news`);
      setNews(response.data.news || []);
    } catch (error) {
      console.error("Error loading news:", error);
    }
  };

  const loadMarketData = async () => {
    try {
      setMarketLoading(true);
      const response = await axios.get(`${API}/market-data`);
      setMarketData(response.data.market_data || []);
    } catch (error) {
      console.error("Error loading market data:", error);
    } finally {
      setMarketLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data || {});
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  };

  // Filter leads based on search term
  const filteredLeads = leads.filter(lead => 
    lead.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Apply filters with debouncing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      loadLeads();
    }, 300); // 300ms delay

    return () => clearTimeout(timeoutId);
  }, [filters]);

  // Handle custom target analysis
  const handleCustomTargetAnalysis = async () => {
    if (!customTarget.trim()) return;
    
    try {
      setLoading(true);
      // Trigger re-analysis with custom target
      const response = await axios.post(`${API}/analyze-content`, {
        content: `Targeting ${customTarget}`,
        company_context: "Custom target analysis"
      });
      
      // Reload leads with new analysis
      await loadLeads();
      await loadTweets();
    } catch (error) {
      console.error("Error analyzing custom target:", error);
    } finally {
      setLoading(false);
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

  const getScoreColor = (score) => {
    if (score >= 8) return "text-green-600";
    if (score >= 6) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <img src="/sbg-logo.svg" alt="Silver Birch Growth" className="w-16 h-8" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Growth Signals</h1>
                <p className="text-xs text-gray-500">Compliments of SilverBirchGrowth.com</p>
                <a 
                  href="https://9kct1c25.drwbrdg.com/sbginsiders" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-xs text-green-600 hover:text-green-700 font-medium"
                >
                  📧 Join our Mailer to win a trip
                </a>
              </div>
            </div>

            {/* Stats - Moved to Header */}
            <div className="hidden md:flex items-center space-x-6">
              <div className="text-center">
                <p className="text-xs font-medium text-gray-500">Total Leads</p>
                <p className="text-lg font-bold text-gray-900">{stats.total_leads || 0}</p>
              </div>
              <div className="text-center">
                <p className="text-xs font-medium text-gray-500">High Priority</p>
                <p className="text-lg font-bold text-red-600">{stats.high_priority_leads || 0}</p>
              </div>
              <div className="text-center">
                <p className="text-xs font-medium text-gray-500">New Today</p>
                <p className="text-lg font-bold text-blue-600">{stats.new_leads_today || 0}</p>
              </div>
              <div className="text-center">
                <p className="text-xs font-medium text-gray-500">Avg Score</p>
                <p className="text-lg font-bold text-green-600">{stats.avg_lead_score || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Purple CTA Ribbon */}
        <div className="absolute top-0 right-0 bg-gradient-to-r from-purple-600 to-purple-700 text-white px-6 py-2 rounded-bl-lg shadow-lg transform hover:scale-105 transition-transform">
          <a
            href="https://silverbirchgrowth.com/contact"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 text-sm font-semibold"
          >
            <span>🚀 Ready to Scale Sales?</span>
            <ArrowUpRight className="w-4 h-4" />
          </a>
        </div>
      </header>

      {/* Inspirational Quote */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="text-center">
            <p className="text-sm italic text-gray-600">
              "The best time to plant a tree was 20 years ago. The second best time is now. The same applies to scaling your sales." 
              <span className="font-medium"> - Growth Proverb</span>
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* News Section - Full Width, 5 Headlines */}
        <div className="bg-white rounded-lg shadow mb-4">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Startup & AI News</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {news.slice(0, 5).map((item, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {item.category}
                    </span>
                    <span className="text-xs text-gray-500">{item.relevance_score}/10</span>
                  </div>
                  <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">{item.title}</h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{item.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">{item.source}</span>
                    <a 
                      href={item.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-green-600 hover:text-green-700"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Search and Target Section */}
        <div className="bg-white rounded-lg shadow mb-6 p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">I am targeting</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Enter search terms..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Custom Target</label>
              <div className="flex space-x-2">
                <div className="relative flex-1">
                  <Target className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="e.g., CTOs at fintech startups..."
                    value={customTarget}
                    onChange={(e) => setCustomTarget(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>
                <button
                  onClick={handleCustomTargetAnalysis}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                >
                  Analyze
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
            <Filter className="w-5 h-5 text-gray-400" />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="Role (CEO, CRO, VP Sales, Founder...)"
              value={filters.role}
              onChange={(e) => handleFilterChange("role", e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2"
            />
            
            <input
              type="text"
              placeholder="Location (city, state, country, postal code...)"
              value={filters.geography}
              onChange={(e) => handleFilterChange("geography", e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2"
            />
            
            <select
              value={filters.priority}
              onChange={(e) => handleFilterChange("priority", e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2"
            >
              <option value="">All Priorities</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
            
            <input
              type="number"
              placeholder="Min Score"
              value={filters.minScore}
              onChange={(e) => handleFilterChange("minScore", e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2"
              min="0"
              max="10"
              step="0.1"
            />
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Leads Table (2/3 width) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">High-Intent Leads ({filteredLeads.length})</h2>
              </div>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Lead
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Intent Signals
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Score
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredLeads.map((lead) => (
                      <tr key={lead.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10">
                              <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                                <Building className="w-5 h-5 text-green-600" />
                              </div>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                              <div className="text-sm text-gray-500">{lead.role} at {lead.company}</div>
                              <div className="flex items-center text-xs text-gray-400 mt-1">
                                <MapPin className="w-3 h-3 mr-1" />
                                {lead.geography}
                                <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getPriorityColor(lead.priority)}`}>
                                  {lead.priority}
                                </span>
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="space-y-1">
                            {lead.intent_signals?.slice(0, 2).map((signal, idx) => (
                              <div key={idx} className="text-xs">
                                <span className="inline-flex items-center px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                                  {signal.signal}
                                </span>
                                <span className="ml-1 text-gray-500">
                                  ({Math.round(signal.confidence * 100)}%)
                                </span>
                              </div>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className={`text-sm font-medium ${getScoreColor(lead.score)}`}>
                            {lead.score}/10
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            {lead.twitter_handle ? (
                              <a
                                href={`https://twitter.com/${lead.twitter_handle.replace('@', '')}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:text-blue-900"
                                title="View Twitter Profile"
                              >
                                <Twitter className="w-4 h-4" />
                              </a>
                            ) : (
                              <span className="text-gray-300" title="Twitter not available">
                                <Twitter className="w-4 h-4" />
                              </span>
                            )}
                            {lead.linkedin_url ? (
                              <a
                                href={lead.linkedin_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:text-blue-900"
                                title="View LinkedIn Profile"
                              >
                                <Linkedin className="w-4 h-4" />
                              </a>
                            ) : (
                              <span className="text-gray-300" title="LinkedIn not available">
                                <Linkedin className="w-4 h-4" />
                              </span>
                            )}
                            {lead.company_website && (
                              <a
                                href={lead.company_website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-green-600 hover:text-green-700"
                                title="Company Website"
                              >
                                <Globe className="w-4 h-4" />
                              </a>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Live Tweets (1/3 width) */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow h-full">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Live GTM Signals</h2>
                <p className="text-sm text-gray-500">Sales, hiring & growth activity</p>
              </div>
              <div className="p-6 space-y-4 overflow-y-auto" style={{height: "calc(100% - 100px)"}}>
                {tweetsLoading ? (
                  <div className="space-y-4">
                    {[1,2,3,4,5,6].map((i) => (
                      <div key={i} className="border border-gray-200 rounded-lg p-4 animate-pulse">
                        <div className="flex items-start space-x-3 mb-3">
                          <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                          <div>
                            <div className="h-4 w-24 bg-gray-200 rounded mb-1"></div>
                            <div className="h-3 w-16 bg-gray-200 rounded"></div>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="h-3 w-full bg-gray-200 rounded"></div>
                          <div className="h-3 w-3/4 bg-gray-200 rounded"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : tweets.filter(tweet => tweet.relevance_score > 3).map((tweet) => (
                  <div key={tweet.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Twitter className="w-4 h-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{tweet.author_name}</p>
                          <p className="text-xs text-gray-500">{tweet.author_handle}</p>
                        </div>
                      </div>
                      <span className="text-xs text-green-600 font-medium">
                        {tweet.relevance_score}/10
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-3">{tweet.content}</p>
                    
                    {tweet.intent_analysis?.intent_signals && tweet.intent_analysis.intent_signals.length > 0 && (
                      <div className="space-y-1 mb-3">
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
                        <span>💬 {tweet.engagement_metrics?.reply_count || 0}</span>
                      </div>
                      <a
                        href={`https://twitter.com/${tweet.author_handle.replace('@', '')}/status/${tweet.tweet_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <ArrowUpRight className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-8 bg-gradient-to-r from-green-600 to-green-700 rounded-lg shadow-lg">
          <div className="px-6 py-8 text-center">
            <h3 className="text-2xl font-bold text-white mb-2">Ready to Accelerate Your Growth?</h3>
            <p className="text-green-100 mb-6">Get strategic sales and GTM consultation from our experts</p>
            <div className="flex flex-col sm:flex-row justify-center space-y-3 sm:space-y-0 sm:space-x-4">
              <a
                href="https://silverbirchgrowth.com/contact"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-6 py-3 bg-white text-green-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Phone className="w-5 h-5 mr-2" />
                Schedule Consultation
              </a>
              <a
                href="mailto:hello@silverbirchgrowth.com"
                className="inline-flex items-center px-6 py-3 bg-green-800 text-white font-semibold rounded-lg hover:bg-green-900 transition-colors"
              >
                <Mail className="w-5 h-5 mr-2" />
                Send Feedback
              </a>
            </div>
          </div>
        </div>
      </div>

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
            <Activity className="w-6 h-6 text-green-600 animate-spin" />
            <span className="text-gray-900 font-medium">Analyzing Growth Signals...</span>
          </div>
        </div>
      )}
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;