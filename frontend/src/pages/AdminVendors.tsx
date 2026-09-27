import { useState, useEffect } from 'react';
import {
  getVendorRequests,
  decideVendorRequest,
  getVendors,
  getVendorActivity,
  getVendorSessions,
  revokeVendorSessionAdmin,
  suspendVendor,
  type VendorRequest,
  type VendorActivityReport,
} from '../services/vendorApi';

export default function AdminVendors() {
  const [activeTab, setActiveTab] = useState<'requests' | 'vendors' | 'activity' | 'sessions'>('requests');
  const [pendingRequests, setPendingRequests] = useState<VendorRequest[]>([]);
  const [vendors, setVendors] = useState<any[]>([]);
  const [activity, setActivity] = useState<VendorActivityReport | null>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  // Auto-refresh pending requests every 15 seconds to prevent stale data
  useEffect(() => {
    if (activeTab === 'requests') {
      const interval = setInterval(() => {
        console.log('Auto-refreshing pending requests...');
        loadPendingRequests(false);
      }, 15000); // Refresh every 15 seconds
      
      return () => clearInterval(interval);
    }
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      switch (activeTab) {
        case 'requests':
          await loadPendingRequests();
          break;
        case 'vendors':
          await loadVendors();
          break;
        case 'activity':
          await loadActivity();
          break;
        case 'sessions':
          await loadSessions();
          break;
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadPendingRequests = async (force = false) => {
    console.log(`Loading pending requests (force: ${force})`);
    // Force fresh data with cache busting
    const timestamp = Date.now();
    const response = await getVendorRequests('PENDING');
    if (response.success) {
      const requests = response.data.requests || [];
      console.log(`Raw requests from API: ${requests.length}`);
      
      // Filter out any requests that might be stale or already processed
      const actuallyPending = requests.filter((req: any) => {
        const isPending = req.status === 'PENDING' || !req.status || req.status === undefined;
        if (!isPending) {
          console.log(`Filtering out non-pending request: ${req.company_name} (${req.status})`);
        }
        return isPending;
      });
      
      console.log(`Actually pending requests: ${actuallyPending.length}`);
      setPendingRequests(actuallyPending);
      
      if (force) {
        setSuccess(`Refreshed data - found ${actuallyPending.length} pending requests`);
        setTimeout(() => setSuccess(''), 3000);
      }
    }
  };

  const loadVendors = async () => {
    const response = await getVendors();
    if (response.success) {
      setVendors(response.data.vendors || []);
    }
  };

  const loadActivity = async () => {
    const response = await getVendorActivity(30);
    if (response.success) {
      setActivity(response.data);
    }
  };

  const loadSessions = async () => {
    const response = await getVendorSessions();
    if (response.success) {
      setSessions(response.data.sessions || []);
    }
  };

  const handleApprove = async (requestId: string) => {
    try {
      setLoading(true);  // Show loading during approval
      
      // Check if this request is actually still pending
      const currentRequests = await getVendorRequests('PENDING');
      const targetRequest = currentRequests.data.requests?.find((req: any) => req.request_id === requestId);
      
      if (!targetRequest) {
        setError('This vendor request is no longer pending. Refreshing list...');
        await loadPendingRequests();
        return;
      }
      
      const response = await decideVendorRequest(requestId, true, 'Approved by admin');
      if (response.success) {
        setSuccess('Vendor approved successfully!');
        // Immediate refresh without page reload
        await loadPendingRequests();
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err: any) {
      // Handle specific error cases
      if (err.response?.status === 400 && err.response?.data?.detail?.includes('not PENDING')) {
        setError('This vendor was already processed. Refreshing list...');
        await loadPendingRequests();
      } else {
        setError(err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to approve vendor');
      }
      console.error('Approval error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (requestId: string) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    try {
      setLoading(true);  // Show loading during rejection
      
      // Check if this request is actually still pending
      const currentRequests = await getVendorRequests('PENDING');
      const targetRequest = currentRequests.data.requests?.find((req: any) => req.request_id === requestId);
      
      if (!targetRequest) {
        setError('This vendor request is no longer pending. Refreshing list...');
        await loadPendingRequests();
        return;
      }
      
      const response = await decideVendorRequest(requestId, false, reason);
      if (response.success) {
        setSuccess('Vendor rejected');
        // Immediate refresh without page reload
        await loadPendingRequests();
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err: any) {
      // Handle specific error cases
      if (err.response?.status === 400 && err.response?.data?.detail?.includes('not PENDING')) {
        setError('This vendor was already processed. Refreshing list...');
        await loadPendingRequests();
      } else {
        setError(err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to reject vendor');
      }
      console.error('Rejection error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    if (!confirm('Revoke this vendor session?')) return;

    try {
      await revokeVendorSessionAdmin(sessionId);
      setSuccess('Session revoked');
      await loadSessions();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to revoke session');
    }
  };

  const handleSuspendVendor = async (vendorId: string) => {
    if (!confirm('Suspend this vendor? They will not be able to login.')) return;

    try {
      await suspendVendor(vendorId);
      setSuccess('Vendor suspended');
      await loadVendors();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to suspend vendor');
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  return (
    <div className="py-1">
      <div className="mb-5">
        <div className="text-[11px] font-bold tracking-[0.28em] text-ink-500">VENDOR MANAGEMENT</div>
        <h1 className="text-3xl font-bold tracking-tight text-ink-900 mt-1">Vendor Management</h1>
        <p className="text-sm font-semibold text-ink-500 mt-1">Manage vendor registrations, approvals, and activity</p>
      </div>

      {error && (
        <div className="bg-ink-950 text-white px-4 py-3 rounded-xl mb-5 font-bold text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-mist-100 border border-ink-950 text-ink-950 px-4 py-3 rounded-xl mb-5 font-bold text-sm">
          {success}
        </div>
      )}

      {/* Tabs */}
      <div className="tatva-card mb-5">
        <div className="border-b border-line">
          <nav className="flex -mb-px px-2">
            {[
              { id: 'requests', label: 'Pending Requests', count: pendingRequests.length },
              { id: 'vendors', label: 'All Vendors', count: vendors.length },
              { id: 'activity', label: 'Activity Report', count: null },
              { id: 'sessions', label: 'Active Sessions', count: sessions.length },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-5 py-3.5 text-sm font-bold border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-ink-950 text-ink-950'
                    : 'border-transparent text-ink-500 hover:text-ink-950'
                }`}
              >
                {tab.label}
                {tab.count !== null && (
                  <span className="ml-2 px-2 py-0.5 bg-mist-100 border border-line text-ink-900 rounded-full text-[11px]">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="tatva-card p-5">
        {loading ? (
          <div className="text-center py-10">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-line border-t-ink-950"></div>
            <p className="mt-4 text-sm font-bold text-ink-500">Loading...</p>
          </div>
        ) : (
          <>
            {/* Pending Requests Tab */}
            {activeTab === 'requests' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-bold tracking-tight text-ink-900">Pending Vendor Requests</h2>
                  <button
                    onClick={() => loadPendingRequests(true)}
                    className="btn-ink px-4 py-2 rounded-xl flex items-center gap-2 text-sm"
                    disabled={loading}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Refresh Data
                  </button>
                </div>
                {pendingRequests.length === 0 ? (
                  <div className="text-center py-10">
                    <svg className="w-14 h-14 mx-auto mb-4 text-line" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm font-bold text-ink-500">No pending vendor requests</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {pendingRequests.map((request) => (
                      <div key={request.request_id} className="border border-line rounded-2xl p-5">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <h3 className="text-base font-bold text-ink-900">{request.company_name}</h3>
                            <div className="mt-2 space-y-1 text-xs font-semibold text-ink-500">
                              <p><strong className="text-ink-900">Contact:</strong> {request.contact_name}</p>
                              <p><strong className="text-ink-900">Email:</strong> {request.vendor_email}</p>
                              {request.phone && <p><strong className="text-ink-900">Phone:</strong> {request.phone}</p>}
                              <p><strong className="text-ink-900">Request ID:</strong> {request.request_id}</p>
                              <p><strong className="text-ink-900">Vendor ID:</strong> {request.vendor_id}</p>
                              <p><strong className="text-ink-900">Requested:</strong> {formatDate(request.requested_at)}</p>
                            </div>
                          </div>
                          <div className="ml-4 flex gap-2 shrink-0">
                            <button
                              onClick={() => handleApprove(request.request_id)}
                              className="btn-ink px-4 py-2 rounded-xl text-sm"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleReject(request.request_id)}
                              className="btn-paper px-4 py-2 rounded-xl text-sm"
                            >
                              Reject
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* All Vendors Tab */}
            {activeTab === 'vendors' && (
              <div>
                {vendors.length === 0 ? (
                  <div className="text-center py-10 text-sm font-bold text-ink-500">
                    <p>No vendors registered yet</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto -mx-5 px-5">
                    <table className="min-w-full divide-y divide-line">
                      <thead>
                        <tr>
                          <th className="px-4 py-2.5 text-left text-[11px] font-bold text-ink-500 uppercase tracking-wide">Company</th>
                          <th className="px-4 py-2.5 text-left text-[11px] font-bold text-ink-500 uppercase tracking-wide">Email</th>
                          <th className="px-4 py-2.5 text-left text-[11px] font-bold text-ink-500 uppercase tracking-wide">Status</th>
                          <th className="px-4 py-2.5 text-left text-[11px] font-bold text-ink-500 uppercase tracking-wide">Sessions</th>
                          <th className="px-4 py-2.5 text-left text-[11px] font-bold text-ink-500 uppercase tracking-wide">Approved</th>
                          <th className="px-4 py-2.5 text-left text-[11px] font-bold text-ink-500 uppercase tracking-wide">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-line">
                        {vendors.map((vendor) => (
                          <tr key={vendor.vendor_id} className="hover:bg-mist-50">
                            <td className="px-4 py-3 whitespace-nowrap text-sm font-bold text-ink-900">
                              {vendor.company_name}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-xs font-semibold text-ink-500">
                              {vendor.email}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap">
                              <span className={`px-2 py-1 text-[11px] font-bold rounded-lg border ${
                                vendor.approval_status === 'APPROVED'
                                  ? 'bg-ink-950 text-white border-ink-950'
                                  : 'bg-mist-100 text-ink-900 border-line'
                              }`}>
                                {vendor.approval_status}
                              </span>
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-xs font-bold text-ink-900">
                              {vendor.upload_sessions || 0}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-xs font-semibold text-ink-500">
                              {vendor.approved_at ? formatDate(vendor.approved_at) : 'N/A'}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm">
                              {vendor.approval_status !== 'SUSPENDED' && (
                                <button
                                  onClick={() => handleSuspendVendor(vendor.vendor_id)}
                                  className="font-bold text-ink-900 hover:underline"
                                >
                                  Suspend
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Activity Report Tab */}
            {activeTab === 'activity' && activity && (
              <div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
                  <div className="bg-ink-950 text-white rounded-xl p-4">
                    <div className="text-[11px] font-bold uppercase tracking-wide text-white/60 mb-1">Total Uploads</div>
                    <div className="text-2xl font-bold">{activity.summary.total_uploads}</div>
                  </div>
                  <div className="bg-mist-50 border border-line rounded-xl p-4">
                    <div className="text-[11px] font-bold uppercase tracking-wide text-ink-500 mb-1">Active Vendors</div>
                    <div className="text-2xl font-bold text-ink-950">{activity.summary.active_vendors}</div>
                  </div>
                </div>

                <h3 className="text-base font-bold tracking-tight text-ink-900 mb-3">Vendor Activity (Last 30 Days)</h3>
                <div className="space-y-2.5">
                  {activity.vendors.map((vendor) => (
                    <div key={vendor.vendor_id} className="border border-line rounded-xl p-3.5">
                      <div className="flex items-center justify-between gap-3">
                        <div className="min-w-0">
                          <div className="font-bold text-ink-900 text-sm">{vendor.company}</div>
                          <div className="text-xs font-semibold text-ink-500 mt-0.5">
                            {vendor.total_uploads} uploads · {vendor.sessions_count} sessions · {vendor.active_sessions} active
                          </div>
                        </div>
                        <div className="text-xs font-semibold text-ink-500 shrink-0">
                          Last: {formatDate(vendor.last_activity)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Active Sessions Tab */}
            {activeTab === 'sessions' && (
              <div>
                {sessions.length === 0 ? (
                  <div className="text-center py-10 text-sm font-bold text-ink-500">
                    <p>No active vendor sessions</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {sessions.map((session) => (
                      <div key={session.session_id} className="border border-line rounded-2xl p-4">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-bold text-ink-900">
                              {session.vendor?.company || 'Unknown'}
                            </h3>
                            <div className="mt-2 space-y-1 text-xs font-semibold text-ink-500">
                              <p><strong className="text-ink-900">Session ID:</strong> {session.session_id}</p>
                              <p><strong className="text-ink-900">Vendor ID:</strong> {session.vendor?.vendor_id}</p>
                              <p><strong className="text-ink-900">Uploads:</strong> {session.upload_count || 0}</p>
                              <p><strong className="text-ink-900">Created:</strong> {formatDate(session.created_at)}</p>
                              <p><strong className="text-ink-900">Expires:</strong> {formatDate(session.expires_at)}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleRevokeSession(session.session_id)}
                            className="btn-ink ml-4 px-4 py-2 rounded-xl text-sm shrink-0"
                          >
                            Revoke
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
