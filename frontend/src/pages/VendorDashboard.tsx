import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getVendorSession, getVendorUploadHistory, revokeVendorSession, isVendorLoggedIn } from '../services/vendorApi';
import { Building2, Mail, Clock, FileUp, LogOut, Upload as UploadIcon } from 'lucide-react';

interface SessionInfo {
  session_id: string;
  session_token: string;
  vendor_id: string;
  vendor_name: string;
  company_name: string;
  email: string;
  status: string;
  upload_count: number;
  created_at: string;
  expires_at: string;
}

interface UploadedFile {
  config_id: string;
  filename: string;
  detected_vendor: string;
  confidence: number;
  uploaded_at?: string;
}

export default function VendorDashboard() {
  const navigate = useNavigate();
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if vendor is logged in
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }

    loadDashboardData();
  }, [navigate]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      // Load session info
      const sessionResponse = await getVendorSession();
      if (sessionResponse.success) {
        setSessionInfo(sessionResponse.data);
      }

      // Load upload history
      const historyResponse = await getVendorUploadHistory();
      if (historyResponse.success) {
        setUploadedFiles(historyResponse.data.uploads || []);
      }
    } catch (err: any) {
      console.error('Failed to load dashboard:', err);
      setError(err.response?.data?.error?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await revokeVendorSession();
      navigate('/vendor/login');
    } catch (err) {
      // Force logout even if API fails
      localStorage.removeItem('vendor_session_token');
      localStorage.removeItem('vendor_info');
      navigate('/vendor/login');
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  const getTimeRemaining = (expiresAt: string) => {
    const expiry = new Date(expiresAt);
    const now = new Date();
    const diff = expiry.getTime() - now.getTime();

    if (diff < 0) return 'Expired';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) return `${hours}h ${minutes}m remaining`;
    return `${minutes}m remaining`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
          <p className="mt-4 text-gray-600">Loading your vendor dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Vendor Dashboard</h1>
              <p className="text-gray-600">Manage your uploads and configurations</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 bg-red-50 border border-red-200 text-red-700 rounded-lg hover:bg-red-100 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Session Info */}
          {sessionInfo && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Company Info */}
              <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <Building2 className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-1" />
                  <div>
                    <div className="text-xs text-indigo-600 font-medium">Company</div>
                    <div className="text-sm font-bold text-gray-900">{sessionInfo.company_name}</div>
                    <div className="text-xs text-gray-600 mt-1">ID: {sessionInfo.vendor_id}</div>
                  </div>
                </div>
              </div>

              {/* Email */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <Mail className="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" />
                  <div>
                    <div className="text-xs text-blue-600 font-medium">Email</div>
                    <div className="text-sm font-bold text-gray-900 break-all">{sessionInfo.email}</div>
                  </div>
                </div>
              </div>

              {/* Files Uploaded */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <FileUp className="w-5 h-5 text-green-600 flex-shrink-0 mt-1" />
                  <div>
                    <div className="text-xs text-green-600 font-medium">Files Uploaded</div>
                    <div className="text-2xl font-bold text-gray-900">{sessionInfo.upload_count}</div>
                  </div>
                </div>
              </div>

              {/* Session Expires */}
              <div className={`bg-gradient-to-br rounded-lg p-4 ${
                getTimeRemaining(sessionInfo.expires_at).includes('Expired')
                  ? 'from-red-50 to-red-100'
                  : 'from-purple-50 to-purple-100'
              }`}>
                <div className="flex items-start space-x-3">
                  <Clock className={`w-5 h-5 flex-shrink-0 mt-1 ${
                    getTimeRemaining(sessionInfo.expires_at).includes('Expired')
                      ? 'text-red-600'
                      : 'text-purple-600'
                  }`} />
                  <div>
                    <div className={`text-xs font-medium ${
                      getTimeRemaining(sessionInfo.expires_at).includes('Expired')
                        ? 'text-red-600'
                        : 'text-purple-600'
                    }`}>
                      Session Expires
                    </div>
                    <div className="text-sm font-bold text-gray-900">
                      {getTimeRemaining(sessionInfo.expires_at)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Section */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-indigo-100 rounded-lg">
                <UploadIcon className="w-6 h-6 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Upload Configurations</h2>
            </div>

            <div className="bg-indigo-50 border-2 border-dashed border-indigo-300 rounded-lg p-8 text-center">
              <svg className="w-12 h-12 text-indigo-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              <p className="text-gray-700 font-medium mb-2">Upload Device Configurations</p>
              <p className="text-sm text-gray-600 mb-4">
                Upload your network device configuration files for security compliance auditing
              </p>
              <button
                onClick={() => navigate('/vendor/upload')}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                Go to Upload Portal
              </button>
            </div>

            {/* Info */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="text-sm text-blue-900">
                <strong>Supported Formats:</strong> .txt, .cfg, .conf (Cisco, Fortinet, and other network devices)
              </div>
            </div>
          </div>

          {/* Recent Uploads */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Uploads</h2>

            {uploadedFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <FileUp className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-sm">No files uploaded yet</p>
                <p className="text-xs text-gray-400 mt-1">Start by uploading a configuration file</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {uploadedFiles.slice(0, 10).map((file, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 text-sm truncate">{file.filename}</div>
                        <div className="text-xs text-gray-600 mt-1">ID: {file.config_id}</div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-2">
                      <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs font-medium rounded">
                        {file.detected_vendor}
                      </span>
                      <span className="text-xs text-gray-500">
                        {(file.confidence * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Tips */}
        <div className="mt-6 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-2xl p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">📤 Upload Files</h4>
              <p className="text-sm text-gray-600">
                Go to the Upload Portal to submit your device configuration files for security auditing.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">⏱️ Session Duration</h4>
              <p className="text-sm text-gray-600">
                Your session is valid for 24 hours. Log in again to extend your session.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">🔒 Session Security</h4>
              <p className="text-sm text-gray-600">
                Your session token is securely stored. Always logout when done for security.
              </p>
            </div>
          </div>
        </div>

        {/* Session Details */}
        {sessionInfo && (
          <div className="mt-6 bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Session Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Session ID:</span>
                <div className="text-gray-600 font-mono text-xs break-all mt-1">{sessionInfo.session_id}</div>
              </div>
              <div>
                <span className="font-medium text-gray-700">Status:</span>
                <div className="text-gray-600 mt-1">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    sessionInfo.status === 'ACTIVE'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {sessionInfo.status}
                  </span>
                </div>
              </div>
              <div>
                <span className="font-medium text-gray-700">Created At:</span>
                <div className="text-gray-600 mt-1">{formatDate(sessionInfo.created_at)}</div>
              </div>
              <div>
                <span className="font-medium text-gray-700">Expires At:</span>
                <div className="text-gray-600 mt-1">{formatDate(sessionInfo.expires_at)}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
