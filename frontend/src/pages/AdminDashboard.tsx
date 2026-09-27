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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
          <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">
            Welcome, <strong>{user?.full_name || user?.email}</strong> - System Administration Panel
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Key Metrics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
            {/* Total Vendors */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Total Vendors</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_vendors}</p>
                </div>
                <Users className="w-10 h-10 text-blue-500 opacity-20" />
              </div>
            </div>

            {/* Approved Vendors */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Approved</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.approved_vendors}</p>
                </div>
                <CheckCircle className="w-10 h-10 text-green-500 opacity-20" />
              </div>
            </div>

            {/* Pending Requests */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Pending</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.pending_requests}</p>
                </div>
                <AlertCircle className="w-10 h-10 text-yellow-500 opacity-20" />
              </div>
            </div>

            {/* Rejected */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Rejected</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.rejected_vendors}</p>
                </div>
                <AlertCircle className="w-10 h-10 text-red-500 opacity-20" />
              </div>
            </div>

            {/* Suspended */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Suspended</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.suspended_vendors}</p>
                </div>
                <AlertCircle className="w-10 h-10 text-purple-500 opacity-20" />
              </div>
            </div>

            {/* Active Sessions */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-indigo-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Active Sessions</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.active_sessions}</p>
                </div>
                <Clock className="w-10 h-10 text-indigo-500 opacity-20" />
              </div>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Top Vendors */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                <TrendingUp className="w-6 h-6 text-indigo-600" />
                <span>Top Vendors (by uploads)</span>
              </h2>
            </div>

            {topVendors.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <FileUp className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p>No vendor activity yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {topVendors.map((vendor, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="flex items-center justify-center w-10 h-10 bg-indigo-200 rounded-full">
                        <span className="text-indigo-900 font-bold text-sm">{idx + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900">{vendor.company}</p>
                        <p className="text-xs text-gray-600 mt-1">{vendor.vendor_id}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">{vendor.uploads}</p>
                      <p className="text-xs text-gray-600 mt-1">uploads</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* System Status */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">System Status</h2>

            <div className="space-y-4">
              {/* Overall Health */}
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-600 rounded-full animate-pulse"></div>
                  <div>
                    <p className="font-medium text-gray-900">System Status</p>
                    <p className="text-sm text-green-700">All systems operational</p>
                  </div>
                </div>
              </div>

              {/* Vendor Management */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Vendor Management</p>
                    <p className="text-sm text-blue-700">
                      {stats?.pending_requests || 0} pending approvals
                    </p>
                  </div>
                  {stats && stats.pending_requests > 0 && (
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded">
                      Action needed
                    </span>
                  )}
                </div>
              </div>

              {/* Activity Level */}
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Active Sessions</p>
                    <p className="text-sm text-purple-700">
                      {stats?.active_sessions || 0} vendors online
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm font-semibold text-gray-900 mb-3">Quick Actions</p>
              <div className="space-y-2">
                <button className="w-full text-left px-4 py-2 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                  → Review Pending Requests
                </button>
                <button className="w-full text-left px-4 py-2 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                  → View All Vendors
                </button>
                <button className="w-full text-left px-4 py-2 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                  → Monitor Sessions
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Vendor Activity</h2>

          {recentActivity.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No recent activity</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Vendor ID</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Company</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Action</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {recentActivity.map((activity, idx) => (
                    <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4 text-sm text-gray-600 font-mono">{activity.vendor_id}</td>
                      <td className="py-3 px-4 text-sm text-gray-900 font-medium">{activity.company}</td>
                      <td className="py-3 px-4 text-sm">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          activity.action === 'Approved'
                            ? 'bg-green-100 text-green-800'
                            : activity.action === 'Registered'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {activity.action}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{formatDate(activity.timestamp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>Last updated: {new Date().toLocaleTimeString()}</p>
        </div>
      </div>
    </div>
  );
}
