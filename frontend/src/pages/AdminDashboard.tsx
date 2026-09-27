import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Users, FileUp, CheckCircle, AlertCircle, TrendingUp, Clock } from 'lucide-react';
import api from '../services/api';

interface VendorStats {
  total_vendors: number;
  approved_vendors: number;
  pending_requests: number;
  rejected_vendors: number;
  suspended_vendors: number;
  active_sessions: number;
}

interface RecentActivity {
  vendor_id: string;
  company: string;
  action: string;
  timestamp: string;
}

interface TopVendors {
  vendor_id: string;
  company: string;
  uploads: number;
  last_activity: string;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<VendorStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [topVendors, setTopVendors] = useState<TopVendors[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      // Load vendor requests (pending count)
      const requestsRes = await api.get('/admin/vendor-requests?status=PENDING');
      const pendingCount = requestsRes.data.data?.total || 0;

      // Load all vendors
      const vendorsRes = await api.get('/admin/vendors');
      const vendors = vendorsRes.data.data?.vendors || [];

      // Load activity report
      const activityRes = await api.get('/admin/vendor-activity?days=30');
      const activityData = activityRes.data.data || {};

      // Load active sessions
      const sessionsRes = await api.get('/admin/vendor-sessions');
      const sessions = sessionsRes.data.data?.sessions || [];

      // Calculate stats
      const approvedCount = vendors.filter((v: any) => v.approval_status === 'APPROVED').length;
      const rejectedCount = vendors.filter((v: any) => v.approval_status === 'REJECTED').length;
      const suspendedCount = vendors.filter((v: any) => v.approval_status === 'SUSPENDED').length;

      setStats({
        total_vendors: vendors.length,
        approved_vendors: approvedCount,
        pending_requests: pendingCount,
        rejected_vendors: rejectedCount,
        suspended_vendors: suspendedCount,
        active_sessions: sessions.length,
      });

      // Format top vendors
      const sorted = (activityData.vendors || [])
        .sort((a: any, b: any) => b.total_uploads - a.total_uploads)
        .slice(0, 5)
        .map((v: any) => ({
          vendor_id: v.vendor_id,
          company: v.company,
          uploads: v.total_uploads,
          last_activity: v.last_activity,
        }));
      setTopVendors(sorted);

      // Format recent activity (mock - use actual activity from backend if available)
      const recentVendors = vendors.slice(0, 5).map((v: any) => ({
        vendor_id: v.vendor_id,
        company: v.company_name,
        action: v.approval_status === 'APPROVED' ? 'Approved' : 'Registered',
        timestamp: v.approved_at || v.created_at,
      }));
      setRecentActivity(recentVendors);
    } catch (err: any) {
      console.error('Failed to load admin dashboard:', err);
      setError(err.response?.data?.error?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-mist-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-line border-t-ink-950"></div>
          <p className="mt-4 text-sm font-bold text-ink-500">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-mist-50 py-6 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-5">
          <div className="text-[11px] font-bold tracking-[0.28em] text-ink-500">SYSTEM ADMINISTRATION</div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-ink-900 mt-1">Admin Dashboard</h1>
          <p className="text-sm font-semibold text-ink-500 mt-1">
            Welcome, <strong className="text-ink-900">{user?.full_name || user?.email}</strong> — System Administration Panel
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-ink-950 text-white px-4 py-3 rounded-xl mb-5 font-bold text-sm">
            {error}
          </div>
        )}

        {/* Key Metrics */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-5">
            {[
              { k: 'Total Vendors', v: stats.total_vendors },
              { k: 'Approved', v: stats.approved_vendors },
              { k: 'Pending', v: stats.pending_requests },
              { k: 'Rejected', v: stats.rejected_vendors },
              { k: 'Suspended', v: stats.suspended_vendors },
              { k: 'Active Sessions', v: stats.active_sessions },
            ].map((s, i) => (
              <div key={s.k} className={`rounded-xl p-4 border ${i === 0 ? 'bg-ink-950 text-white border-ink-950' : 'bg-white border-line'}`}>
                <p className={`text-[11px] font-bold uppercase tracking-wide ${i === 0 ? 'text-white/60' : 'text-ink-500'}`}>{s.k}</p>
                <p className={`text-3xl font-bold tracking-tight mt-1 ${i === 0 ? 'text-white' : 'text-ink-950'}`}>{s.v}</p>
              </div>
            ))}
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-5">
          {/* Top Vendors */}
          <div className="lg:col-span-2 tatva-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold tracking-tight text-ink-900 flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Top Vendors (by uploads)</span>
              </h2>
            </div>

            {topVendors.length === 0 ? (
              <div className="text-center py-8">
                <FileUp className="w-10 h-10 text-line mx-auto mb-3" />
                <p className="text-sm font-bold text-ink-500">No vendor activity yet</p>
              </div>
            ) : (
              <div className="space-y-2.5">
                {topVendors.map((vendor, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3.5 bg-mist-50 border border-line rounded-xl">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div className="flex items-center justify-center w-9 h-9 bg-ink-950 text-white rounded-full shrink-0">
                        <span className="font-bold text-xs">{idx + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-ink-900 text-sm truncate">{vendor.company}</p>
                        <p className="text-[11px] font-mono font-bold text-ink-500">{vendor.vendor_id}</p>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-xl font-bold text-ink-950">{vendor.uploads}</p>
                      <p className="text-[11px] font-bold text-ink-500">uploads</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* System Status */}
          <div className="tatva-card p-5">
            <h2 className="text-lg font-bold tracking-tight text-ink-900 mb-4">System Status</h2>

            <div className="space-y-2.5">
              <div className="p-3.5 bg-mist-50 border border-line rounded-xl">
                <div className="flex items-center space-x-2.5">
                  <div className="w-2.5 h-2.5 bg-ink-950 rounded-full animate-pulse"></div>
                  <div>
                    <p className="font-bold text-ink-900 text-sm">System Status</p>
                    <p className="text-xs font-semibold text-ink-500">All systems operational</p>
                  </div>
                </div>
              </div>

              <div className="p-3.5 bg-mist-50 border border-line rounded-xl">
                <p className="font-bold text-ink-900 text-sm">Vendor Management</p>
                <p className="text-xs font-semibold text-ink-500">
                  {stats?.pending_requests || 0} pending approvals
                  {stats && stats.pending_requests > 0 && (
                    <span className="ml-2 px-2 py-0.5 bg-ink-950 text-white text-[11px] font-bold rounded-full">Action needed</span>
                  )}
                </p>
              </div>

              <div className="p-3.5 bg-mist-50 border border-line rounded-xl">
                <p className="font-bold text-ink-900 text-sm">Active Sessions</p>
                <p className="text-xs font-semibold text-ink-500">
                  {stats?.active_sessions || 0} vendors online
                </p>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-line">
              <p className="text-xs font-bold uppercase tracking-wide text-ink-500 mb-2">Quick Actions</p>
              <div className="space-y-1">
                <button className="w-full text-left px-3 py-2 text-xs font-bold text-ink-900 hover:bg-mist-100 rounded-lg transition-colors">
                  → Review Pending Requests
                </button>
                <button className="w-full text-left px-3 py-2 text-xs font-bold text-ink-900 hover:bg-mist-100 rounded-lg transition-colors">
                  → View All Vendors
                </button>
                <button className="w-full text-left px-3 py-2 text-xs font-bold text-ink-900 hover:bg-mist-100 rounded-lg transition-colors">
                  → Monitor Sessions
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="tatva-card p-5">
          <h2 className="text-lg font-bold tracking-tight text-ink-900 mb-4">Recent Vendor Activity</h2>

          {recentActivity.length === 0 ? (
            <div className="text-center py-8 text-sm font-bold text-ink-500">
              <p>No recent activity</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-line">
                    <th className="text-left py-2.5 px-4 text-[11px] font-bold uppercase tracking-wide text-ink-500">Vendor ID</th>
                    <th className="text-left py-2.5 px-4 text-[11px] font-bold uppercase tracking-wide text-ink-500">Company</th>
                    <th className="text-left py-2.5 px-4 text-[11px] font-bold uppercase tracking-wide text-ink-500">Action</th>
                    <th className="text-left py-2.5 px-4 text-[11px] font-bold uppercase tracking-wide text-ink-500">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {recentActivity.map((activity, idx) => (
                    <tr key={idx} className="border-b border-line last:border-0 hover:bg-mist-50 transition-colors">
                      <td className="py-2.5 px-4 text-xs font-mono font-bold text-ink-500">{activity.vendor_id}</td>
                      <td className="py-2.5 px-4 text-sm font-bold text-ink-900">{activity.company}</td>
                      <td className="py-2.5 px-4 text-sm">
                        <span className="px-2 py-1 rounded-lg text-[11px] font-bold bg-ink-950 text-white">
                          {activity.action}
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-xs font-semibold text-ink-500">{formatDate(activity.timestamp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="mt-5 text-center text-xs font-bold text-ink-500">
          <p>Last updated: {new Date().toLocaleTimeString()}</p>
        </div>
      </div>
    </div>
  );
}
