import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { 
  Search, Filter, ExternalLink, Twitter, Linkedin, 
  TrendingUp, TrendingDown, DollarSign, Users,
  Building, MapPin, Star, Calendar, Activity,
  BarChart3, PieChart, ArrowUpRight
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
  const [filters, setFilters] = useState({
    role: "",
    geography: "",
    priority: "",
    minScore: ""
  });
  const [loading, setLoading] = useState(true);

  // Load data on component mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadLeads(),
        loadTweets(),
        loadNews(),
        loadMarketData(),
        loadStats()
      ]);
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
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
      const response = await axios.get(`${API}/live-tweets`);
      setTweets(response.data.tweets || []);
    } catch (error) {
      console.error("Error loading tweets:", error);
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
      const response = await axios.get(`${API}/market-data`);
      setMarketData(response.data.market_data || []);
    } catch (error) {
      console.error("Error loading market data:", error);
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

  // Apply filters
  useEffect(() => {
    loadLeads();
  }, [filters]);

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
              <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Silver Birch Growth</h1>
                <p className="text-xs text-gray-500">Growth Signals Dashboard</p>
              </div>
            </div>

            {/* Market Data Widget */}
            <div className="hidden md:flex items-center space-x-4">
              {marketData.map((market, index) => (
                <div key={index} className="text-center">
                  <p className="text-xs font-medium text-gray-500">{market.symbol}</p>
                  <p className="text-sm font-bold text-gray-900">${market.price?.toLocaleString()}</p>
                  <p className={`text-xs ${market.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {market.change_percent}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Search Bar */}
      <div className="bg-white border-b px-4 sm:px-6 lg:px-8 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="I am targeting..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-lg"
            />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-green-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Leads</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_leads || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Star className="w-8 h-8 text-red-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">High Priority</p>
                <p className="text-2xl font-bold text-gray-900">{stats.high_priority_leads || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Calendar className="w-8 h-8 text-blue-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">New Today</p>
                <p className="text-2xl font-bold text-gray-900">{stats.new_leads_today || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-purple-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Avg Score</p>
                <p className="text-2xl font-bold text-gray-900">{stats.avg_lead_score || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* News Section */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Startup & AI News</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {news.slice(0, 3).map((item, index) => (
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

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Leads Table (2/3 width) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">High-Intent Leads</h2>
                  <Filter className="w-5 h-5 text-gray-400" />
                </div>
                
                {/* Filters */}
                <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
                  <select
                    value={filters.role}
                    onChange={(e) => handleFilterChange("role", e.target.value)}
                    className="text-sm border border-gray-300 rounded px-3 py-2"
                  >
                    <option value="">All Roles</option>
                    <option value="CEO">CEO</option>
                    <option value="Founder">Founder</option>
                    <option value="COO">COO</option>
                    <option value="CMO">CMO</option>
                  </select>
                  
                  <select
                    value={filters.geography}
                    onChange={(e) => handleFilterChange("geography", e.target.value)}
                    className="text-sm border border-gray-300 rounded px-3 py-2"
                  >
                    <option value="">All Regions</option>
                    <option value="North America">North America</option>
                    <option value="Europe">Europe</option>
                    <option value="Asia">Asia</option>
                  </select>
                  
                  <select
                    value={filters.priority}
                    onChange={(e) => handleFilterChange("priority", e.target.value)}
                    className="text-sm border border-gray-300 rounded px-3 py-2"
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
                    className="text-sm border border-gray-300 rounded px-3 py-2"
                    min="0"
                    max="10"
                    step="0.1"
                  />
                </div>
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
                            {lead.twitter_handle && (
                              <a
                                href={`https://twitter.com/${lead.twitter_handle}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:text-blue-900"
                              >
                                <Twitter className="w-4 h-4" />
                              </a>
                            )}
                            {lead.linkedin_url && (
                              <a
                                href={lead.linkedin_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:text-blue-900"
                              >
                                <Linkedin className="w-4 h-4" />
                              </a>
                            )}
                            <button className="text-green-600 hover:text-green-900">
                              <ExternalLink className="w-4 h-4" />
                            </button>
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
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Live Signals</h2>
                <p className="text-sm text-gray-500">Real-time intent detection</p>
              </div>
              <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
                {tweets.map((tweet) => (
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
                    
                    {tweet.intent_analysis?.intent_signals && (
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
                        <span>❤️ {tweet.engagement_metrics?.likes || 0}</span>
                        <span>🔄 {tweet.engagement_metrics?.retweets || 0}</span>
                        <span>💬 {tweet.engagement_metrics?.replies || 0}</span>
                      </div>
                      <button className="text-blue-600 hover:text-blue-800">
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
            <Activity className="w-6 h-6 text-green-600 animate-spin" />
            <span className="text-gray-900 font-medium">Loading Growth Signals...</span>
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