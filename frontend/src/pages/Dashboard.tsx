import { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Clock, FileText } from 'lucide-react';
import { getDashboardSummary } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import type { DashboardSummary } from '../types';

const Dashboard = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { showError } = useToast();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await getDashboardSummary();
      if (response.success && response.data) {
        setSummary(response.data);
      }
    } catch (error: any) {
      console.error('Failed to load dashboard:', error);
      showError('Failed to Load Dashboard', 'Could not retrieve dashboard data. Please try refreshing the page.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-10 w-10 rounded-full border-4 border-line border-t-ink-950"></div>
      </div>
    );
  }

  // Empty state for first-time users
  if (summary?.total_configs === 0) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-5">
          <div className="text-[11px] font-bold tracking-[0.28em] text-ink-500">SECURITY OVERVIEW</div>
          <h2 className="text-3xl font-bold tracking-tight text-ink-900 mt-1">
            Welcome, {user?.full_name || 'User'}
          </h2>
          <p className="text-sm font-semibold text-ink-500 mt-1">
            {user?.organization_name} • {user?.role.split('_').map(w => w.charAt(0) + w.slice(1).toLowerCase()).join(' ')}
          </p>
        </div>

        <div className="text-center py-12 tatva-card">
          <h1 className="text-3xl font-bold tracking-tight mb-3 text-ink-900">Welcome to Tatva Security Platform</h1>
          <p className="text-sm font-semibold text-ink-500 mb-6 max-w-2xl mx-auto leading-relaxed">
            Compliance status across your network infrastructure. Upload your first configuration file to begin.
          </p>
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
    <div className="space-y-5">
      {/* Page Header — New Audit removed (was blank page) */}
      <div>
        <div className="text-[11px] font-bold tracking-[0.28em] text-ink-500">SECURITY OVERVIEW</div>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-ink-900 mt-1">Security Overview</h1>
        <p className="text-sm font-semibold text-ink-500 mt-1">Compliance status across your network infrastructure</p>
      </div>

      {/* Hero KPI Section */}
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 tatva-card !bg-ink-950 !border-ink-950 text-white p-5">
          <div className="flex items-start justify-between mb-5">
            <div>
              <p className="text-[11px] font-bold text-white/60 uppercase tracking-widest mb-2">
                Overall Compliance
              </p>
              <div className="flex items-baseline space-x-2">
                <span className="text-6xl font-bold tracking-tight">
                  {summary?.compliance_score || 0}
                </span>
                <span className="text-3xl font-bold text-white/50">%</span>
              </div>
            </div>
            <div className="p-3 bg-white rounded-2xl">
              <CheckCircle className="w-8 h-8 text-ink-950" />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-5 border-t border-white/15">
            <div className="text-center">
              <p className="text-[11px] font-bold text-white/60 uppercase tracking-wide mb-1">Passed Controls</p>
              <p className="text-2xl font-bold">
                {summary?.passed_controls || 0}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[11px] font-bold text-white/60 uppercase tracking-wide mb-1">Total Findings</p>
              <p className="text-2xl font-bold">{totalFindings}</p>
            </div>
            <div className="text-center">
              <p className="text-[11px] font-bold text-white/60 uppercase tracking-wide mb-1">Risk Level</p>
              <p className="text-2xl font-bold">
                {riskLevel}
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="tatva-card p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">
                Configurations
              </p>
              <Shield className="w-4 h-4 text-ink-950" />
            </div>
            <p className="text-4xl font-bold tracking-tight text-ink-950 mb-0.5">
              {summary?.total_configs || 0}
            </p>
            <p className="text-xs font-bold text-ink-500">Active devices</p>
          </div>

          <div className="tatva-card p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">
                Audits Run
              </p>
              <Clock className="w-4 h-4 text-ink-950" />
            </div>
            <p className="text-4xl font-bold tracking-tight text-ink-950 mb-0.5">
              {summary?.total_audits || 0}
            </p>
            <p className="text-xs font-bold text-ink-500">Total scans</p>
          </div>
        </div>
      </div>

      {/* Critical Alert Banner */}
      {(summary?.critical_findings || 0) > 0 && (
        <div className="bg-ink-950 text-white rounded-2xl p-5">
          <div className="flex items-start space-x-4">
            <span className="w-10 h-10 rounded-xl bg-white text-ink-950 flex items-center justify-center font-bold shrink-0">!</span>
            <div className="flex-1">
              <h3 className="text-base font-bold mb-1">
                Critical Security Issues Detected
              </h3>
              <p className="text-sm font-semibold text-white/70 mb-3">
                {summary?.critical_findings} critical {summary?.critical_findings === 1 ? 'vulnerability' : 'vulnerabilities'} require immediate attention to maintain security compliance.
              </p>
              <a
                href="/configurations"
                className="inline-flex items-center space-x-2 text-sm font-bold text-white underline underline-offset-4"
              >
                <span>View Details</span>
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Risk Analysis Section */}
      <div className="tatva-card p-5">
        <div className="mb-4">
          <h2 className="text-xl font-bold tracking-tight text-ink-900">Security Findings</h2>
          <p className="text-xs font-semibold text-ink-500 mt-0.5">Breakdown by severity level</p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { k: 'Critical', v: summary?.critical_findings || 0, s: 'Immediate action required' },
            { k: 'High', v: summary?.high_findings || 0, s: 'Address promptly' },
            { k: 'Medium', v: summary?.medium_findings || 0, s: 'Plan remediation' },
            { k: 'Low', v: summary?.low_findings || 0, s: 'Monitor & track' },
          ].map((r) => (
            <div key={r.k} className="rounded-xl border border-line bg-mist-50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-ink-500 uppercase tracking-wider">{r.k}</span>
                <div className={`w-2 h-2 rounded-full ${r.v > 0 ? 'bg-ink-950' : 'bg-line'}`}></div>
              </div>
              <p className="text-4xl font-bold tracking-tight text-ink-950 mb-1">{r.v}</p>
              <p className="text-[11px] text-ink-500 font-bold">{r.s}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions Section */}
      <div className="grid md:grid-cols-2 gap-4">
        <a href="/configurations" className="tatva-card p-5 group cursor-pointer">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-base font-bold text-ink-900 mb-1">
                View All Configurations
              </h3>
              <p className="text-xs font-semibold text-ink-500 mb-3">
                Review and manage {summary?.total_configs || 0} uploaded network device configurations
              </p>
              <div className="flex items-center text-xs font-bold text-ink-950">
                <span>Go to configurations</span>
              </div>
            </div>
            <div className="p-2.5 bg-ink-950 rounded-xl">
              <FileText className="w-5 h-5 text-white" />
            </div>
          </div>
        </a>

        <a href="/admin/vendors" className="tatva-card p-5 group cursor-pointer">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-base font-bold text-ink-900 mb-1">
                Vendor Management
              </h3>
              <p className="text-xs font-semibold text-ink-500 mb-3">
                Review approvals, sessions and vendor activity
              </p>
              <div className="flex items-center text-xs font-bold text-ink-950">
                <span>Open vendor management</span>
              </div>
            </div>
            <div className="p-2.5 bg-ink-950 rounded-xl">
              <Shield className="w-5 h-5 text-white" />
            </div>
          </div>
        </a>
      </div>

      {!(summary?.critical_findings || summary?.high_findings) && (
        <div className="hidden">
          <AlertTriangle className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};

export default Dashboard;
