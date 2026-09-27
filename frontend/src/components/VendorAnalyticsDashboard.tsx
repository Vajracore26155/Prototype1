import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import {
  TrendingUp, TrendingDown, Shield, AlertTriangle, CheckCircle, Clock,
  FileText, Activity, Zap, Target, Award, AlertCircle, Users, Database,
  Eye, Download, RefreshCw, Calendar, Filter, Upload, ChevronRight, ArrowUpRight
} from 'lucide-react';
import {
  getVendorAnalyticsOverview,
  getVendorComplianceTrends,
  getVendorRiskDistribution,
  getVendorFindingCategories
} from '../services/vendorApi';

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
  complianceChange: number;
  configurationsChange: number;
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

const PALETTE = {
  primary: '#1C1C1C',
  indigo: '#1C1C1C',
  emerald: '#1C1C1C',
  amber: '#6E6E6E',
  rose: '#1C1C1C',
  cyan: '#6E6E6E',
  slate: '#1C1C1C',
  cardBg: '#ffffff',
  critical: '#1C1C1C',
  high: '#555555',
  medium: '#9A9A9A',
  low: '#D8D8D8'
};

const VendorAnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [complianceTrend, setComplianceTrend] = useState<ComplianceTrend[]>([]);
  const [findingDistribution, setFindingDistribution] = useState<FindingDistribution[]>([]);
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange, selectedCategory]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // 1. Load Overview Metrics (real-time, no mocked defaults)
      const overviewResponse = await getVendorAnalyticsOverview(timeRange);
      if (overviewResponse.success && overviewResponse.data) {
        const raw = overviewResponse.data.metrics || overviewResponse.data;
        const pc = overviewResponse.data.period_comparison || {};
        setMetrics({
          totalConfigurations: raw.total_configurations ?? raw.totalConfigurations ?? 0,
          totalAudits: raw.total_audits ?? raw.totalAudits ?? 0,
          avgComplianceScore: Number(raw.avg_compliance_score ?? raw.avgComplianceScore ?? 0),
          criticalFindings: raw.critical_findings ?? raw.criticalFindings ?? 0,
          highFindings: raw.high_findings ?? raw.highFindings ?? 0,
          mediumFindings: raw.medium_findings ?? raw.mediumFindings ?? 0,
          lowFindings: raw.low_findings ?? raw.lowFindings ?? 0,
          passedControls: raw.passed_controls ?? raw.passedControls ?? 0,
          failedControls: raw.failed_controls ?? raw.failedControls ?? 0,
          warningControls: raw.warning_controls ?? raw.warningControls ?? 0,
          processingTime: {
            average: raw.processing_time?.average ?? 0,
            fastest: raw.processing_time?.fastest ?? 0,
            slowest: raw.processing_time?.slowest ?? 0,
          },
          riskTrend: raw.risk_trend || 'stable',
          complianceTrend: raw.compliance_trend || 'stable',
          complianceChange: Number(pc.compliance_change ?? 0),
          configurationsChange: Number(pc.configurations_change ?? 0),
        });
      } else {
        setMetrics({
          totalConfigurations: 0,
          totalAudits: 0,
          avgComplianceScore: 0,
          criticalFindings: 0,
          highFindings: 0,
          mediumFindings: 0,
          lowFindings: 0,
          passedControls: 0,
          failedControls: 0,
          warningControls: 0,
          processingTime: { average: 0, fastest: 0, slowest: 0 },
          riskTrend: 'stable',
          complianceTrend: 'stable',
          complianceChange: 0,
          configurationsChange: 0,
        });
      }

      // 2. Load Compliance Trends (real)
      const trendsResponse = await getVendorComplianceTrends(timeRange);
      if (trendsResponse.success && trendsResponse.data?.trend_data) {
        setComplianceTrend(trendsResponse.data.trend_data);
      } else {
        setComplianceTrend([]);
      }

      // 3. Load Risk Distribution (real)
      const riskResponse = await getVendorRiskDistribution();
      if (riskResponse.success && riskResponse.data?.risk_analysis) {
        setRiskAnalysis(riskResponse.data.risk_analysis);
      } else {
        setRiskAnalysis([]);
      }

      // 4. Load Finding Categories (real)
      const categoriesResponse = await getVendorFindingCategories();
      if (categoriesResponse.success && categoriesResponse.data?.finding_distribution) {
        setFindingDistribution(categoriesResponse.data.finding_distribution);
      } else {
        setFindingDistribution([]);
      }

    } catch (error) {
      console.error('Analytics load error:', error);
      setMetrics({
        totalConfigurations: 0,
        totalAudits: 0,
        avgComplianceScore: 0,
        criticalFindings: 0,
        highFindings: 0,
        mediumFindings: 0,
        lowFindings: 0,
        passedControls: 0,
        failedControls: 0,
        warningControls: 0,
        processingTime: { average: 0, fastest: 0, slowest: 0 },
        riskTrend: 'stable',
        complianceTrend: 'stable',
        complianceChange: 0,
        configurationsChange: 0,
      });
      setComplianceTrend([]);
      setRiskAnalysis([]);
      setFindingDistribution([]);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await loadAnalyticsData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-3xl p-12 border border-gray-200 text-center shadow-sm">
        <div className="animate-spin w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full mx-auto mb-4"></div>
        <p className="text-gray-500 font-semibold text-sm">Computing analytics & security compliance insights...</p>
      </div>
    );
  }

  const totalDecided = (metrics?.passedControls ?? 0) + (metrics?.failedControls ?? 0) + (metrics?.warningControls ?? 0);
  const passRate = totalDecided > 0 ? ((metrics?.passedControls ?? 0) / totalDecided) * 100 : 0;
  const lift = metrics?.complianceChange ?? 0;
  const liftText = `${lift >= 0 ? '+' : ''}${lift.toFixed(1)}% vs prior period`;
  const avgMin = metrics?.processingTime.average ?? 0;
  const slaText = avgMin < 1 ? `${Math.max(1, Math.round(avgMin * 60))}s` : `${avgMin.toFixed(1)}m`;
  const nonZeroTrend = complianceTrend.filter(p => (p.compliance ?? 0) > 0);
  const traj = nonZeroTrend.length >= 2
    ? (nonZeroTrend[nonZeroTrend.length - 1].compliance >= nonZeroTrend[0].compliance ? 'Positive Trajectory' : 'Needs Attention')
    : (metrics?.complianceTrend === 'improving' ? 'Positive Trajectory' : metrics?.complianceTrend === 'declining' ? 'Declining' : 'Stable');

  return (
    <div className="space-y-5">
      <div className="bg-ink-950 text-white rounded-2xl px-5 py-4 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2 text-white/60 font-mono text-[11px] uppercase tracking-wider mb-0.5">
            <Zap className="w-3.5 h-3.5" />
            <span>Tatva Intelligence Analytics Engine</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Security Compliance Intelligence</h2>
          <p className="text-white/60 text-xs mt-0.5 font-semibold">Real-time posture scores, threat distributions, and benchmark trends</p>
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <div className="flex items-center bg-white/10 border border-white/20 rounded-xl px-3 py-1.5 text-xs text-white">
            <Calendar className="w-4 h-4 mr-2" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-transparent text-white focus:outline-none cursor-pointer font-bold"
            >
              <option value="7d" className="bg-ink-950 text-white">Last 7 Days</option>
              <option value="30d" className="bg-ink-950 text-white">Last 30 Days</option>
              <option value="90d" className="bg-ink-950 text-white">Last 90 Days</option>
              <option value="1y" className="bg-ink-950 text-white">Last 1 Year</option>
            </select>
          </div>

          <button
            onClick={refreshData}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-white text-ink-950 text-xs font-bold rounded-xl disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid — compact monochrome */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
          {/* Average Compliance */}
          <div className="bg-white rounded-xl p-4 border border-line shadow-sm hover:border-ink-950 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">Avg Compliance</span>
              <Award className="w-4 h-4 text-ink-950" />
            </div>
            <div className="text-2xl font-bold text-ink-950 mt-1.5">
              {metrics.avgComplianceScore.toFixed(1)}%
            </div>
            <div className="flex items-center text-ink-500 text-[11px] font-bold mt-1">
              <TrendingUp className="w-3 h-3 mr-1" />
              <span>{liftText}</span>
            </div>
          </div>

          {/* Critical Findings */}
          <div className="bg-ink-950 rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-white/60 uppercase tracking-wide">Critical Risks</span>
              <AlertTriangle className="w-4 h-4 text-white" />
            </div>
            <div className="text-2xl font-bold text-white mt-1.5">
              {metrics.criticalFindings}
            </div>
            <div className="text-[11px] font-bold text-white/60 mt-1">
              Action Required
            </div>
          </div>

          {/* High Risks */}
          <div className="bg-white rounded-xl p-4 border border-line shadow-sm hover:border-ink-950 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">High Risks</span>
              <Shield className="w-4 h-4 text-ink-950" />
            </div>
            <div className="text-2xl font-bold text-ink-950 mt-1.5">
              {metrics.highFindings}
            </div>
            <div className="text-[11px] font-bold text-ink-500 mt-1">
              Review Needed
            </div>
          </div>

          {/* Passed Controls */}
          <div className="bg-white rounded-xl p-4 border border-line shadow-sm hover:border-ink-950 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">Passed Rules</span>
              <CheckCircle className="w-4 h-4 text-ink-950" />
            </div>
            <div className="text-2xl font-bold text-ink-950 mt-1.5">
              {metrics.passedControls.toLocaleString()}
            </div>
            <div className="text-[11px] font-bold text-ink-500 mt-1">
              {passRate.toFixed(1)}% Pass Rate
            </div>
          </div>

          {/* Total Configurations */}
          <div className="bg-white rounded-xl p-4 border border-line shadow-sm hover:border-ink-950 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">Total Configs</span>
              <Database className="w-4 h-4 text-ink-950" />
            </div>
            <div className="text-2xl font-bold text-ink-950 mt-1.5">
              {metrics.totalConfigurations}
            </div>
            <div className="text-[11px] font-bold text-ink-500 mt-1">
              Active Devices
            </div>
          </div>

          {/* Processing Latency */}
          <div className="bg-white rounded-xl p-4 border border-line shadow-sm hover:border-ink-950 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">Avg SLA Speed</span>
              <Zap className="w-4 h-4 text-ink-950" />
            </div>
            <div className="text-2xl font-bold text-ink-950 mt-1.5">
              {slaText}
            </div>
            <div className="text-[11px] font-bold text-ink-500 mt-1">
              {avgMin < 1 ? 'Sub-minute Audit' : 'Audit Duration'}
            </div>
          </div>
        </div>
      )}

      {/* Row 2: Charts (Compliance Trend + Risk Breakdown) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Compliance Trend Chart (Spans 2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-5 border border-line shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold tracking-tight text-ink-900">Historical Compliance Trend</h3>
              <p className="text-[11px] font-semibold text-ink-500">Track mean compliance percentage over time</p>
            </div>
            <span className="px-3 py-1 bg-mist-100 text-ink-900 font-bold text-xs rounded-full border border-line">
              {traj}
            </span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={complianceTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCompliance" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1C1C1C" stopOpacity={0.35}/>
                    <stop offset="95%" stopColor="#1C1C1C" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E2E2" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#6E6E6E' }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#6E6E6E' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1C1C1C', borderRadius: '12px', border: 'none', color: '#fff' }}
                  formatter={(val: number) => [`${val}%`, 'Compliance']}
                />
                <Area type="monotone" dataKey="compliance" stroke="#1C1C1C" strokeWidth={2.5} fillOpacity={1} fill="url(#colorCompliance)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution Breakdown */}
        <div className="bg-white rounded-2xl p-5 border border-line shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-base font-bold tracking-tight text-ink-900">Risk Severity Distribution</h3>
              <Shield className="w-5 h-5 text-ink-950" />
            </div>

            <div className="h-44 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskAnalysis}
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={74}
                    paddingAngle={3}
                    dataKey="count"
                    strokeWidth={0}
                  >
                    {riskAnalysis.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#1C1C1C', '#555555', '#9A9A9A', '#D8D8D8'][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1C1C1C', borderRadius: '10px', color: '#fff' }}
                    formatter={(val: number) => [val, 'Findings']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-1.5 mt-3">
            {riskAnalysis.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs font-bold p-2 bg-mist-50 rounded-xl border border-line">
                <div className="flex items-center space-x-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: ['#1C1C1C', '#555555', '#9A9A9A', '#D8D8D8'][idx % 4] }} />
                  <span className="text-ink-900">{item.riskLevel} Risk</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-ink-950">{item.count}</span>
                  <span className="text-ink-500 font-semibold">({item.percentage.toFixed(1)}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 3: Findings by Category Bar Chart */}
      <div className="bg-white rounded-3xl p-6 border border-gray-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900">Findings Breakdown by Security Domain</h3>
            <p className="text-xs text-gray-500">Vulnerabilities categorized across CIS/NIST security domains</p>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={findingDistribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis dataKey="category" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderRadius: '12px', color: '#fff' }} />
              <Bar dataKey="critical" name="Critical" fill={PALETTE.critical} radius={[4, 4, 0, 0]} />
              <Bar dataKey="high" name="High" fill={PALETTE.high} radius={[4, 4, 0, 0]} />
              <Bar dataKey="medium" name="Medium" fill={PALETTE.medium} radius={[4, 4, 0, 0]} />
              <Bar dataKey="low" name="Low" fill={PALETTE.low} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default VendorAnalyticsDashboard;