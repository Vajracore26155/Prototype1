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

  const loadPendingRequests = async () => {
    const response = await getVendorRequests('PENDING');
    if (response.success) {
      setPendingRequests(response.data.requests || []);
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
      const response = await decideVendorRequest(requestId, true, 'Approved by admin');
      if (response.success) {
        setSuccess('Vendor approved successfully!');
        await loadPendingRequests();
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to approve vendor');
    }
  };

  const handleReject = async (requestId: string) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    try {
      const response = await decideVendorRequest(requestId, false, reason);
      if (response.success) {
        setSuccess('Vendor rejected');
        await loadPendingRequests();
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to reject vendor');
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
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Vendor Management</h1>
        <p className="text-gray-600">Manage vendor registrations, approvals, and activity</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
          {success}
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            {[
              { id: 'requests', label: 'Pending Requests', count: pendingRequests.length },
              { id: 'vendors', label: 'All Vendors', count: vendors.length },
              { id: 'activity', label: 'Activity Report', count: null },
              { id: 'sessions', label: 'Active Sessions', count: sessions.length },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
                {tab.count !== null && (
                  <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        ) : (
          <>
            {/* Pending Requests Tab */}
            {activeTab === 'requests' && (
              <div>
                {pendingRequests.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p>No pending vendor requests</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {pendingRequests.map((request) => (
                      <div key={request.request_id} className="border border-gray-200 rounded-lg p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900">{request.company_name}</h3>
                            <div className="mt-2 space-y-1 text-sm text-gray-600">
                              <p><strong>Contact:</strong> {request.contact_name}</p>
                              <p><strong>Email:</strong> {request.vendor_email}</p>
                              {request.phone && <p><strong>Phone:</strong> {request.phone}</p>}
                              <p><strong>Request ID:</strong> {request.request_id}</p>
                              <p><strong>Vendor ID:</strong> {request.vendor_id}</p>
                              <p><strong>Requested:</strong> {formatDate(request.requested_at)}</p>
                            </div>
                          </div>
                          <div className="ml-6 flex gap-2">
                            <button
                              onClick={() => handleApprove(request.request_id)}
                              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleReject(request.request_id)}
                              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
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
                  <div className="text-center py-12 text-gray-500">
                    <p>No vendors registered yet</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead>
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sessions</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Approved</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {vendors.map((vendor) => (
                          <tr key={vendor.vendor_id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {vendor.company_name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {vendor.email}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs font-medium rounded ${
                                vendor.approval_status === 'APPROVED'
                                  ? 'bg-green-100 text-green-800'
                                  : vendor.approval_status === 'SUSPENDED'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {vendor.approval_status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {vendor.upload_sessions || 0}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {vendor.approved_at ? formatDate(vendor.approved_at) : 'N/A'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              {vendor.approval_status !== 'SUSPENDED' && (
                                <button
                                  onClick={() => handleSuspendVendor(vendor.vendor_id)}
                                  className="text-red-600 hover:text-red-800 font-medium"
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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-blue-50 rounded-lg p-6">
                    <div className="text-sm text-blue-600 font-medium mb-1">Total Uploads</div>
                    <div className="text-3xl font-bold text-blue-900">{activity.summary.total_uploads}</div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-6">
                    <div className="text-sm text-green-600 font-medium mb-1">Active Vendors</div>
                    <div className="text-3xl font-bold text-green-900">{activity.summary.active_vendors}</div>
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-4">Vendor Activity (Last 30 Days)</h3>
                <div className="space-y-3">
                  {activity.vendors.map((vendor) => (
                    <div key={vendor.vendor_id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">{vendor.company}</div>
                          <div className="text-sm text-gray-600 mt-1">
                            {vendor.total_uploads} uploads · {vendor.sessions_count} sessions · {vendor.active_sessions} active
                          </div>
                        </div>
                        <div className="text-sm text-gray-500">
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
                  <div className="text-center py-12 text-gray-500">
                    <p>No active vendor sessions</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {sessions.map((session) => (
                      <div key={session.session_id} className="border border-gray-200 rounded-lg p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {session.vendor?.company || 'Unknown'}
                            </h3>
                            <div className="mt-2 space-y-1 text-sm text-gray-600">
                              <p><strong>Session ID:</strong> {session.session_id}</p>
                              <p><strong>Vendor ID:</strong> {session.vendor?.vendor_id}</p>
                              <p><strong>Uploads:</strong> {session.upload_count || 0}</p>
                              <p><strong>Created:</strong> {formatDate(session.created_at)}</p>
                              <p><strong>Expires:</strong> {formatDate(session.expires_at)}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleRevokeSession(session.session_id)}
                            className="ml-6 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
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
