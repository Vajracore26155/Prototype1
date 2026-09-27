import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, AreaChart, Area, RadialBarChart, RadialBar
} from 'recharts';
import {
  TrendingUp, TrendingDown, Shield, AlertTriangle, CheckCircle, Clock,
  FileText, Activity, Zap, Target, Award, AlertCircle, Users, Database,
  Eye, Download, RefreshCw, Calendar, Filter, Upload
} from 'lucide-react';
import {
  getVendorAnalyticsOverview,
  getVendorComplianceTrends,
  getVendorRiskDistribution,
  getVendorFindingCategories
} from '../services/vendorApi';

// Enhanced data interfaces for analytics
interface DashboardMetrics {
  totalConfigurations: number;
  totalAudits: number;
  avgComplianceScore: number;
  criticalFindings: number;
  highFindings: number;
  mediumFindings: number;
  lowFindings: number;
  passedControls: number;
  failedControls: number;
  warningControls: number;
  processingTime: {
    average: number;
    fastest: number;
    slowest: number;
  };
  riskTrend: 'improving' | 'declining' | 'stable';
  complianceTrend: 'improving' | 'declining' | 'stable';
}

interface ComplianceTrend {
  date: string;
  compliance: number;
  configurations: number;
  criticalFindings: number;
}

interface FindingDistribution {
  category: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
}

interface RiskAnalysis {
  riskLevel: string;
  count: number;
  percentage: number;
  color: string;
}

interface VendorPerformance {
  vendor: string;
  configurations: number;
  avgCompliance: number;
  riskScore: number;
  lastUpload: string;
}

interface ProcessingMetrics {
  stage: string;
  avgTime: number;
  successRate: number;
  errors: number;
}

const COLORS = {
  primary: '#4F46E5',
  success: '#10B981', 
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#06B6D4',
  gray: '#6B7280',
  critical: '#DC2626',
  high: '#F97316',
  medium: '#EAB308',
  low: '#22C55E'
};

const VendorAnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [complianceTrend, setComplianceTrend] = useState<ComplianceTrend[]>([]);
  const [findingDistribution, setFindingDistribution] = useState<FindingDistribution[]>([]);
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis[]>([]);
  const [vendorPerformance, setVendorPerformance] = useState<VendorPerformance[]>([]);
  const [processingMetrics, setProcessingMetrics] = useState<ProcessingMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange, selectedCategory]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Load analytics overview
      const overviewResponse = await getVendorAnalyticsOverview(timeRange);
      if (overviewResponse.success && overviewResponse.data) {
        setMetrics(overviewResponse.data.metrics);
      }

      // Load compliance trends
      const trendsResponse = await getVendorComplianceTrends(timeRange);
      if (trendsResponse.success && trendsResponse.data) {
        setComplianceTrend(trendsResponse.data.trend_data);
      }

      // Load risk distribution
      const riskResponse = await getVendorRiskDistribution();
      if (riskResponse.success && riskResponse.data) {
        setRiskAnalysis(riskResponse.data.risk_analysis);
      }

      // Load finding categories
      const categoriesResponse = await getVendorFindingCategories();
      if (categoriesResponse.success && categoriesResponse.data) {
        setFindingDistribution(categoriesResponse.data.finding_distribution);
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
      // Fallback to simulated data if API fails
      await simulateDataLoad();
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await loadAnalyticsData();
    setRefreshing(false);
  };

  // Simulate data loading - replace with real API calls
  const simulateDataLoad = async () => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Sample data - replace with real API data
    setMetrics({
      totalConfigurations: 145,
      totalAudits: 132,
      avgComplianceScore: 78.5,
      criticalFindings: 23,
      highFindings: 45,
      mediumFindings: 67,
      lowFindings: 89,
      passedControls: 1234,
      failedControls: 245,
      warningControls: 123,
      processingTime: {
        average: 4.2,
        fastest: 1.8,
        slowest: 12.5
      },
      riskTrend: 'improving',
      complianceTrend: 'improving'
    });

    // Sample trend data
    const trendData: ComplianceTrend[] = [];
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      trendData.push({
        date: date.toISOString().split('T')[0],
        compliance: Math.random() * 20 + 70,
        configurations: Math.floor(Math.random() * 10) + 5,
        criticalFindings: Math.floor(Math.random() * 5)
      });
    }
    setComplianceTrend(trendData);

    // Sample finding distribution
    setFindingDistribution([
      { category: 'Network Security', critical: 8, high: 15, medium: 22, low: 35, total: 80 },
      { category: 'Access Control', critical: 5, high: 12, medium: 18, low: 25, total: 60 },
      { category: 'Data Protection', critical: 3, high: 8, medium: 15, low: 20, total: 46 },
      { category: 'Authentication', critical: 4, high: 6, medium: 8, low: 12, total: 30 },
      { category: 'Logging & Monitoring', critical: 2, high: 4, medium: 6, low: 8, total: 20 }
    ]);

    // Sample risk analysis
    setRiskAnalysis([
      { riskLevel: 'Critical', count: 23, percentage: 10.2, color: COLORS.critical },
      { riskLevel: 'High', count: 45, percentage: 20.0, color: COLORS.high },
      { riskLevel: 'Medium', count: 67, percentage: 29.8, color: COLORS.medium },
      { riskLevel: 'Low', count: 89, percentage: 40.0, color: COLORS.low }
    ]);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between bg-white rounded-lg border p-4">
        <div className="flex items-center space-x-4 mb-4 lg:mb-0">
          <div className="flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-gray-400" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Categories</option>
              <option value="network">Network Security</option>
              <option value="access">Access Control</option>
              <option value="data">Data Protection</option>
              <option value="auth">Authentication</option>
            </select>
          </div>
        </div>

        <button
          onClick={refreshData}
          disabled={refreshing}
          className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Key Performance Indicators */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          {/* Total Configurations */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm font-medium">Configurations</p>
                <p className="text-3xl font-bold mt-2">{metrics.totalConfigurations}</p>
                <p className="text-blue-100 text-xs mt-1">+12 this month</p>
              </div>
              <Database className="w-8 h-8 text-blue-200" />
            </div>
          </div>

          {/* Average Compliance */}
          <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm font-medium">Avg Compliance</p>
                <p className="text-3xl font-bold mt-2">{metrics.avgComplianceScore.toFixed(1)}%</p>
                <div className="flex items-center mt-1">
                  {metrics.complianceTrend === 'improving' && <TrendingUp className="w-3 h-3 mr-1" />}
                  <p className="text-green-100 text-xs">
                    {metrics.complianceTrend === 'improving' ? '+2.3%' : '-1.2%'} vs last month
                  </p>
                </div>
              </div>
              <Award className="w-8 h-8 text-green-200" />
            </div>
          </div>

          {/* Critical Findings */}
          <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-100 text-sm font-medium">Critical Findings</p>
                <p className="text-3xl font-bold mt-2">{metrics.criticalFindings}</p>
                <div className="flex items-center mt-1">
                  {metrics.riskTrend === 'improving' && <TrendingDown className="w-3 h-3 mr-1" />}
                  <p className="text-red-100 text-xs">
                    {metrics.riskTrend === 'improving' ? '-5 resolved' : '+3 new'}
                  </p>
                </div>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-200" />
            </div>
          </div>
          {/* Processing Time */}
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm font-medium">Avg Processing</p>
                <p className="text-3xl font-bold mt-2">{metrics.processingTime.average.toFixed(1)}m</p>
                <p className="text-purple-100 text-xs mt-1">Range: {metrics.processingTime.fastest}m - {metrics.processingTime.slowest}m</p>
              </div>
              <Zap className="w-8 h-8 text-purple-200" />
            </div>
          </div>

          {/* Passed Controls */}
          <div className="bg-gradient-to-r from-teal-500 to-teal-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-teal-100 text-sm font-medium">Passed Controls</p>
                <p className="text-3xl font-bold mt-2">{metrics.passedControls.toLocaleString()}</p>
                <p className="text-teal-100 text-xs mt-1">vs {metrics.failedControls} failed</p>
              </div>
              <CheckCircle className="w-8 h-8 text-teal-200" />
            </div>
          </div>

          {/* Total Audits */}
          <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-indigo-100 text-sm font-medium">Total Audits</p>
                <p className="text-3xl font-bold mt-2">{metrics.totalAudits}</p>
                <p className="text-indigo-100 text-xs mt-1">{Math.round((metrics.totalAudits / metrics.totalConfigurations) * 100)}% coverage</p>
              </div>
              <Activity className="w-8 h-8 text-indigo-200" />
            </div>
          </div>
        </div>
      )}

      {/* Charts Row 1 - Compliance Trend and Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compliance Trend Chart */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Compliance Trend</h3>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <TrendingUp className="w-4 h-4" />
              <span>Improving trend</span>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={complianceTrend}>
              <defs>
                <linearGradient id="complianceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis domain={[0, 100]} />
              <Tooltip 
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Compliance Score']}
                labelFormatter={(value) => `Date: ${new Date(value).toLocaleDateString()}`}
              />
              <Area
                type="monotone"
                dataKey="compliance"
                stroke={COLORS.primary}
                fillOpacity={1}
                fill="url(#complianceGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Risk Distribution</h3>
            <div className="text-sm text-gray-500">
              {riskAnalysis.reduce((sum, item) => sum + item.count, 0)} total findings
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={riskAnalysis}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="count"
                >
                  {riskAnalysis.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number, name: string) => [value, 'Count']} />
              </PieChart>
            </ResponsiveContainer>

            <div className="space-y-3">
              {riskAnalysis.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm font-medium">{item.riskLevel}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{item.count}</div>
                    <div className="text-xs text-gray-500">{item.percentage.toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row 2 - Finding Categories and Processing Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Finding Distribution by Category */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Findings by Category</h3>
            <button className="text-sm text-indigo-600 hover:text-indigo-800">
              View Details
            </button>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={findingDistribution} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="category" 
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="critical" stackId="a" fill={COLORS.critical} name="Critical" />
              <Bar dataKey="high" stackId="a" fill={COLORS.high} name="High" />
              <Bar dataKey="medium" stackId="a" fill={COLORS.medium} name="Medium" />
              <Bar dataKey="low" stackId="a" fill={COLORS.low} name="Low" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Processing Performance Metrics */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Processing Performance</h3>
            <div className="text-sm text-gray-500">
              Last 30 days
            </div>
          </div>

          <div className="space-y-4">
            {/* Processing Speed Indicator */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 rounded-full">
                  <Zap className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <div className="text-sm font-medium">Average Processing Speed</div>
                  <div className="text-xs text-gray-500">Per configuration analysis</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-green-600">4.2 min</div>
                <div className="text-xs text-gray-500">+15% faster</div>
              </div>
            </div>

            {/* Success Rate */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-full">
                  <Target className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <div className="text-sm font-medium">Analysis Success Rate</div>
                  <div className="text-xs text-gray-500">Completed without errors</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-blue-600">97.3%</div>
                <div className="text-xs text-gray-500">132/136 configs</div>
              </div>
            </div>

            {/* Queue Status */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-100 rounded-full">
                  <Clock className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <div className="text-sm font-medium">Current Queue Status</div>
                  <div className="text-xs text-gray-500">Pending analysis</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-purple-600">0</div>
                <div className="text-xs text-gray-500">All caught up</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity and Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2 bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
            <button className="text-sm text-indigo-600 hover:text-indigo-800">
              View All
            </button>
          </div>

          <div className="space-y-4">
            {/* Sample activity items */}
            <div className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg">
              <div className="p-2 bg-green-100 rounded-full">
                <CheckCircle className="w-4 h-4 text-green-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900">
                  Configuration audit completed
                </div>
                <div className="text-sm text-gray-500">
                  cisco_router_config.txt - 78% compliance score
                </div>
                <div className="text-xs text-gray-400">2 minutes ago</div>
              </div>
            </div>

            <div className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg">
              <div className="p-2 bg-blue-100 rounded-full">
                <FileText className="w-4 h-4 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900">
                  New configuration uploaded
                </div>
                <div className="text-sm text-gray-500">
                  juniper_switch_config.txt - Processing started
                </div>
                <div className="text-xs text-gray-400">15 minutes ago</div>
              </div>
            </div>

            <div className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg">
              <div className="p-2 bg-orange-100 rounded-full">
                <AlertTriangle className="w-4 h-4 text-orange-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900">
                  Critical finding detected
                </div>
                <div className="text-sm text-gray-500">
                  SSH weak encryption in fortinet_fw.conf
                </div>
                <div className="text-xs text-gray-400">1 hour ago</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Quick Actions</h3>
          
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-3 bg-indigo-50 hover:bg-indigo-100 rounded-lg text-left transition-colors">
              <div className="flex items-center space-x-3">
                <Upload className="w-5 h-5 text-indigo-600" />
                <span className="font-medium">Upload Configuration</span>
              </div>
              <span className="text-indigo-600">→</span>
            </button>

            <button className="w-full flex items-center justify-between p-3 bg-green-50 hover:bg-green-100 rounded-lg text-left transition-colors">
              <div className="flex items-center space-x-3">
                <Download className="w-5 h-5 text-green-600" />
                <span className="font-medium">Download Report</span>
              </div>
              <span className="text-green-600">→</span>
            </button>

            <button className="w-full flex items-center justify-between p-3 bg-orange-50 hover:bg-orange-100 rounded-lg text-left transition-colors">
              <div className="flex items-center space-x-3">
                <Eye className="w-5 h-5 text-orange-600" />
                <span className="font-medium">View Findings</span>
              </div>
              <span className="text-orange-600">→</span>
            </button>

            <button className="w-full flex items-center justify-between p-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-left transition-colors">
              <div className="flex items-center space-x-3">
                <Users className="w-5 h-5 text-purple-600" />
                <span className="font-medium">Manage Settings</span>
              </div>
              <span className="text-purple-600">→</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorAnalyticsDashboard;