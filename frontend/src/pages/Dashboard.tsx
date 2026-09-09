import { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Clock, TrendingUp, ArrowUpRight, FileText } from 'lucide-react';
import { getDashboardSummary } from '../services/api';
import type { DashboardSummary } from '../types';

const Dashboard = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadDashboard();
  }, []);
  
  const loadDashboard = async () => {
    try {
      const response = await getDashboardSummary();
      if (response.success && response.data) {
        setSummary(response.data);
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner h-12 w-12"></div>
      </div>
    );
  }

  // Empty state for first-time users
  if (summary?.total_configs === 0) {
    return (
      <div className="max-w-4xl mx-auto page-enter">
        <div className="text-center py-16">
          <div className="inline-flex p-6 bg-brand-50 rounded-3xl mb-6 animate-[scaleIn_500ms_var(--ease-out)]">
            <Shield className="w-20 h-20 text-brand-600" />
          </div>
          <h1 className="text-4xl font-bold mb-4 text-neutral-900">Welcome to Network Security Auditor</h1>
          <p className="text-lg text-neutral-600 mb-8 max-w-2xl mx-auto leading-relaxed">
            AI-powered compliance auditing for multi-vendor network configurations. 
            Get started by uploading your first configuration file.
          </p>
          <a href="/upload" className="btn-primary text-lg px-8 py-3 group inline-flex items-center space-x-2">
            <span>Upload Configuration</span>
            <ArrowUpRight className="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-200" />
          </a>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mt-16">
          <div className="card text-center stagger-item">
            <div className="inline-flex p-3 bg-brand-50 rounded-xl mb-4">
              <Shield className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="font-semibold text-neutral-900 mb-2">Multi-Vendor Support</h3>
            <p className="text-sm text-neutral-600">
              Cisco, Fortinet, and AI-assisted learning for unknown vendors
            </p>
          </div>
          <div className="card text-center stagger-item">
            <div className="inline-flex p-3 bg-status-success-bg rounded-xl mb-4">
              <CheckCircle className="w-6 h-6 text-status-success-text" />
            </div>
            <h3 className="font-semibold text-neutral-900 mb-2">Automated Compliance</h3>
            <p className="text-sm text-neutral-600">
              Real-time security compliance checking against industry standards
            </p>
          </div>
          <div className="card text-center stagger-item">
            <div className="inline-flex p-3 bg-status-info-bg rounded-xl mb-4">
              <TrendingUp className="w-6 h-6 text-status-info-text" />
            </div>
            <h3 className="font-semibold text-neutral-900 mb-2">Actionable Insights</h3>
            <p className="text-sm text-neutral-600">
              Detailed findings with remediation steps and risk scoring
            </p>
          </div>
        </div>
      </div>
    );
  }

  const totalFindings = (summary?.critical_findings || 0) + 
                       (summary?.high_findings || 0) + 
                       (summary?.medium_findings || 0) + 
                       (summary?.low_findings || 0);
  
  const riskLevel = (summary?.critical_findings || 0) > 0 ? 'CRITICAL' : 
                    (summary?.high_findings || 0) > 0 ? 'HIGH' : 
                    (summary?.medium_findings || 0) > 0 ? 'MEDIUM' : 'LOW';
  
  return (
    <div className="space-y-8 page-enter">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-4xl font-bold text-neutral-900 mb-2">Security Overview</h1>
          <p className="text-neutral-600">Compliance status across your network infrastructure</p>
        </div>
        <a 
          href="/upload" 
          className="btn-primary flex items-center space-x-2 group"
        >
          <span>New Audit</span>
          <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-200" />
        </a>
      </div>

      {/* Hero KPI Section - Compliance Score takes center stage */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Primary KPI - Compliance Score (Larger, more prominent) - GLASS EFFECT */}
        <div className="lg:col-span-2 card-glass bg-gradient-to-br from-white/90 to-brand-50/80 border-white/60">
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-sm font-semibold text-neutral-600 uppercase tracking-wide mb-2">
                Overall Compliance
              </p>
              <div className="flex items-baseline space-x-3">
                <span className="text-7xl font-bold text-neutral-900">
                  {summary?.compliance_score || 0}
                </span>
                <span className="text-4xl font-bold text-neutral-500">%</span>
              </div>
            </div>
            <div className="p-4 bg-white/90 backdrop-blur-sm rounded-2xl border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
              <CheckCircle className="w-10 h-10 text-brand-600" />
            </div>
          </div>
          
          <div className="flex items-center justify-between pt-6 border-t border-white/40">
            <div>
              <p className="text-sm text-neutral-600 mb-1">Passed Controls</p>
              <p className="text-2xl font-bold text-status-success-text">
                {summary?.passed_controls || 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-neutral-600 mb-1">Total Findings</p>
              <p className="text-2xl font-bold text-neutral-900">{totalFindings}</p>
            </div>
            <div>
              <p className="text-sm text-neutral-600 mb-1">Risk Level</p>
              <p className={`text-2xl font-bold ${
                riskLevel === 'CRITICAL' ? 'text-status-critical-text' :
                riskLevel === 'HIGH' ? 'text-status-high-text' :
                riskLevel === 'MEDIUM' ? 'text-status-medium-text' :
                'text-status-success-text'
              }`}>
                {riskLevel}
              </p>
            </div>
          </div>
        </div>

        {/* Secondary KPIs - SUBTLE GLASS */}
        <div className="space-y-6">
          <div className="card-glass">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                Configurations
              </p>
              <Shield className="w-5 h-5 text-neutral-400" />
            </div>
            <p className="text-5xl font-bold text-neutral-900 mb-1">
              {summary?.total_configs || 0}
            </p>
            <p className="text-sm text-neutral-600">Active devices</p>
          </div>

          <div className="card-glass">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                Audits Run
              </p>
              <Clock className="w-5 h-5 text-neutral-400" />
            </div>
            <p className="text-5xl font-bold text-neutral-900 mb-1">
              {summary?.total_audits || 0}
            </p>
            <p className="text-sm text-neutral-600">Total scans</p>
          </div>
        </div>
      </div>

      {/* Critical Alert Banner - Only show if critical findings exist - ELEVATED GLASS */}
      {(summary?.critical_findings || 0) > 0 && (
        <div className="elevated-glass border-2 border-status-critical-border/60 bg-status-critical-bg/70 p-6">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-white/90 backdrop-blur-sm rounded-xl border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
              <AlertTriangle className="w-7 h-7 text-status-critical-text" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-status-critical-text mb-1">
                Critical Security Issues Detected
              </h3>
              <p className="text-neutral-800 mb-4">
                {summary?.critical_findings} critical {summary?.critical_findings === 1 ? 'vulnerability' : 'vulnerabilities'} require immediate attention to maintain security compliance.
              </p>
              <a 
                href="/configurations" 
                className="inline-flex items-center space-x-2 text-sm font-semibold text-status-critical-text hover:text-status-critical-text/80"
              >
                <span>View Details</span>
                <ArrowUpRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Risk Analysis Section - GLASS CARDS */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900">Security Findings</h2>
            <p className="text-sm text-neutral-600 mt-1">Breakdown by severity level</p>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Critical - GLASS EFFECT */}
          <div 
            className="group relative overflow-hidden rounded-2xl border-2 border-status-critical-border/60 bg-gradient-to-br from-status-critical-bg/80 to-white/90 backdrop-blur-xl p-6 transition-all duration-300 hover:translate-y-[-4px]"
            style={{ boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.08)' }}
            onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 16px 48px 0 rgba(0, 0, 0, 0.10)'}
            onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 8px 32px 0 rgba(0, 0, 0, 0.08)'}
          >
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-status-critical-text uppercase tracking-wider">
                  Critical
                </span>
                <div className="w-2 h-2 rounded-full bg-status-critical-text" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}></div>
              </div>
              <p className="text-5xl font-bold text-status-critical-text mb-2">
                {summary?.critical_findings || 0}
              </p>
              <p className="text-xs text-neutral-700 font-medium">
                Immediate action required
              </p>
            </div>
          </div>

          {/* High - GLASS EFFECT */}
          <div 
            className="group relative overflow-hidden rounded-2xl border-2 border-status-high-border/60 bg-gradient-to-br from-status-high-bg/80 to-white/90 backdrop-blur-xl p-6 transition-all duration-300 hover:translate-y-[-4px]"
            style={{ boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.08)' }}
            onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 16px 48px 0 rgba(0, 0, 0, 0.10)'}
            onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 8px 32px 0 rgba(0, 0, 0, 0.08)'}
          >
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-status-high-text uppercase tracking-wider">
                  High
                </span>
                <div className="w-2 h-2 rounded-full bg-status-high-text" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}></div>
              </div>
              <p className="text-5xl font-bold text-status-high-text mb-2">
                {summary?.high_findings || 0}
              </p>
              <p className="text-xs text-neutral-700 font-medium">
                Address promptly
              </p>
            </div>
          </div>

          {/* Medium - GLASS EFFECT */}
          <div 
            className="group relative overflow-hidden rounded-2xl border-2 border-status-medium-border/60 bg-gradient-to-br from-status-medium-bg/80 to-white/90 backdrop-blur-xl p-6 transition-all duration-300 hover:translate-y-[-4px]"
            style={{ boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.08)' }}
            onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 16px 48px 0 rgba(0, 0, 0, 0.10)'}
            onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 8px 32px 0 rgba(0, 0, 0, 0.08)'}
          >
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-status-medium-text uppercase tracking-wider">
                  Medium
                </span>
                <div className="w-2 h-2 rounded-full bg-status-medium-text" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}></div>
              </div>
              <p className="text-5xl font-bold text-status-medium-text mb-2">
                {summary?.medium_findings || 0}
              </p>
              <p className="text-xs text-neutral-700 font-medium">
                Plan remediation
              </p>
            </div>
          </div>

          {/* Low - GLASS EFFECT */}
          <div 
            className="group relative overflow-hidden rounded-2xl border-2 border-status-low-border/60 bg-gradient-to-br from-status-low-bg/80 to-white/90 backdrop-blur-xl p-6 transition-all duration-300 hover:translate-y-[-4px]"
            style={{ boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.08)' }}
            onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 16px 48px 0 rgba(0, 0, 0, 0.10)'}
            onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 8px 32px 0 rgba(0, 0, 0, 0.08)'}
          >
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-status-low-text uppercase tracking-wider">
                  Low
                </span>
                <div className="w-2 h-2 rounded-full bg-status-low-text" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}></div>
              </div>
              <p className="text-5xl font-bold text-status-low-text mb-2">
                {summary?.low_findings || 0}
              </p>
              <p className="text-xs text-neutral-700 font-medium">
                Monitor & track
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions Section */}
      <div className="grid md:grid-cols-2 gap-6">
        <a href="/configurations" className="card group hover:border-brand-300 transition-all duration-200 cursor-pointer hover:shadow-lg hover:translate-y-[-2px]">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-bold text-neutral-900 mb-2 group-hover:text-brand-600 transition-colors duration-200">
                View All Configurations
              </h3>
              <p className="text-sm text-neutral-600 mb-4">
                Review and manage {summary?.total_configs || 0} uploaded network device configurations
              </p>
              <div className="flex items-center text-sm font-semibold text-brand-600">
                <span>Go to configurations</span>
                <ArrowUpRight className="w-4 h-4 ml-1 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform duration-200" />
              </div>
            </div>
            <div className="p-3 bg-brand-50 rounded-xl group-hover:bg-brand-100 transition-colors duration-200">
              <FileText className="w-6 h-6 text-brand-600" />
            </div>
          </div>
        </a>

        <a href="/upload" className="card group hover:border-brand-300 transition-all duration-200 cursor-pointer hover:shadow-lg hover:translate-y-[-2px]">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-bold text-neutral-900 mb-2 group-hover:text-brand-600 transition-colors duration-200">
                Upload New Configuration
              </h3>
              <p className="text-sm text-neutral-600 mb-4">
                Add another network device configuration for security analysis
              </p>
              <div className="flex items-center text-sm font-semibold text-brand-600">
                <span>Start new audit</span>
                <ArrowUpRight className="w-4 h-4 ml-1 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform duration-200" />
              </div>
            </div>
            <div className="p-3 bg-brand-50 rounded-xl group-hover:bg-brand-100 transition-colors duration-200">
              <Shield className="w-6 h-6 text-brand-600" />
            </div>
          </div>
        </a>
      </div>
    </div>
  );
};

export default Dashboard;
