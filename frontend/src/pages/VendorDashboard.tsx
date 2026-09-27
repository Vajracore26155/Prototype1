import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  getVendorSession, 
  getVendorUploadHistory, 
  isVendorLoggedIn,
  getVendorConfigurations,
  getVendorAudits,
  revokeVendorSession 
} from '../services/vendorApi';
import { 
  Building2, Mail, Clock, FileUp, Upload as UploadIcon,
  CheckCircle, TrendingUp, FileText, Shield, MoreVertical,
  Settings, LogOut, Eye, Download
} from 'lucide-react';

interface SessionInfo {
  session_id: string;
  vendor: {
    vendor_id: string;
    company: string;
    contact: string;
    email: string;
  };
  status: string;
  upload_count: number;
  created_at: string;
  expires_at: string;
  last_activity: string;
  organization_id: number;
  files_uploaded: UploadedFile[];
}

interface UploadedFile {
  config_id: string;
  filename: string;
  detected_vendor: string;
  confidence: number;
  uploaded_at?: string;
}

interface VendorConfiguration {
  config_id: string;
  filename: string;
  file_type: string;
  status: string;
  vendor: string;
  vendor_confidence: number;
  created_at: string;
  file_size?: number;
}

interface VendorAudit {
  audit_id: string;
  configuration: {
    config_id: string;
    filename: string;
    vendor: string;
  };
  status: string;
  compliance_score: number;
  risk_level: string;
  risk_score: number;
  started_at: string;
  completed_at?: string;
  requires_human_review: boolean;
  passed_count: number;
  failed_count: number;
  warning_count: number;
}

interface VendorStats {
  total_configurations: number;
  total_audits: number;
  avg_compliance_score: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  passed_controls: number;
}

export default function VendorDashboard() {
  const navigate = useNavigate();
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [configurations, setConfigurations] = useState<VendorConfiguration[]>([]);
  const [audits, setAudits] = useState<VendorAudit[]>([]);
  const [stats, setStats] = useState<VendorStats | null>(null);
  const [error, setError] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    // Check if vendor is logged in
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }

    loadDashboardData();
  }, [navigate]);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuOpen && !(event.target as Element)?.closest('.relative')) {
        setMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuOpen]);

  // Trigger stats calculation when configurations or audits change
  useEffect(() => {
    if (configurations.length > 0 || audits.length > 0) {
      calculateStats();
    }
  }, [configurations, audits]);

  const loadDashboardData = async () => {
    setError('');
    try {
      // Load session info
      const sessionResponse = await getVendorSession();
      if (sessionResponse.success) {
        setSessionInfo(sessionResponse.data);
      } else {
        throw new Error(sessionResponse.data?.error?.message || 'Failed to load session');
      }

      // Load upload history
      const historyResponse = await getVendorUploadHistory();
      if (historyResponse.success) {
        setUploadedFiles(historyResponse.data.uploads || []);
      }

      // Load configurations
      try {
        const configsResponse = await getVendorConfigurations();
        if (configsResponse.success) {
          setConfigurations(configsResponse.data.configurations || []);
        }
      } catch (err: any) {
        console.warn('Failed to load configurations:', err);
      }

      // Load audits
      try {
        const auditsResponse = await getVendorAudits();
        if (auditsResponse.success) {
          setAudits(auditsResponse.data.audits || []);
        }
      } catch (err: any) {
        console.warn('Failed to load audits:', err);
      }

      // Calculate stats from loaded data (will be updated when data loads)
      // The useEffect will handle this when configurations and audits are set
    } catch (err: any) {
      console.error('Failed to load dashboard:', err);
      const errorMessage = err.response?.data?.error?.message || err.message || 'Failed to load dashboard data';
      setError(errorMessage);
      
      // If unauthorized, redirect to login
      if (err.response?.status === 401) {
        localStorage.removeItem('vendor_session_token');
        localStorage.removeItem('vendor_info');
        setTimeout(() => navigate('/vendor/login'), 1000);
      }
    }
  };

  const calculateStats = () => {
    const totalConfigs = configurations.length;
    const totalAudits = audits.length;
    const completedAudits = audits.filter(a => a.status === 'COMPLETED');
    const avgCompliance = completedAudits.length > 0 
      ? completedAudits.reduce((sum, audit) => sum + (audit.compliance_score || 0), 0) / completedAudits.length
      : 0;

    setStats({
      total_configurations: totalConfigs,
      total_audits: totalAudits,
      avg_compliance_score: avgCompliance,
      critical_findings: 0, // These would need additional API calls to get detailed findings
      high_findings: 0,
      medium_findings: 0,
      low_findings: 0,
      passed_controls: completedAudits.reduce((sum, audit) => sum + (audit.passed_count || 0), 0)
    });
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

  const viewConfiguration = (configId: string) => {
    navigate(`/vendor/configuration/${configId}`);
  };

  const viewAuditDetails = (auditId: string) => {
    navigate(`/vendor/audit/${auditId}`);
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': 
      case 'running': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Vendor Dashboard</h1>
              <p className="text-gray-600">
                Welcome, <strong>{sessionInfo?.vendor.company}</strong> - Configuration Management & Security Auditing
              </p>
            </div>
            
            {/* Settings Menu */}
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <MoreVertical className="w-5 h-5 text-gray-600" />
              </button>
              
              {menuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="py-1">
                    <button
                      onClick={() => {
                        setMenuOpen(false);
                        navigate('/vendor/settings');
                      }}
                      className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                    >
                      <Settings className="w-4 h-4" />
                      <span>Account Settings</span>
                    </button>
                    <div className="border-t border-gray-100"></div>
                    <button
                      onClick={() => {
                        setMenuOpen(false);
                        handleLogout();
                      }}
                      className="flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 w-full text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Key Metrics */}
        {stats && sessionInfo && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
            {/* Total Configurations */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Configurations</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_configurations}</p>
                </div>
                <FileText className="w-10 h-10 text-blue-500 opacity-20" />
              </div>
            </div>

            {/* Total Audits */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-indigo-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Audits</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_audits}</p>
                </div>
                <Shield className="w-10 h-10 text-indigo-500 opacity-20" />
              </div>
            </div>

            {/* Compliance Score */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Avg Compliance</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.avg_compliance_score.toFixed(0)}%</p>
                </div>
                <CheckCircle className="w-10 h-10 text-green-500 opacity-20" />
              </div>
            </div>

            {/* Session Status */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Session</p>
                  <p className="text-sm font-bold text-gray-900 mt-2">{getTimeRemaining(sessionInfo.expires_at)}</p>
                </div>
                <Clock className="w-10 h-10 text-purple-500 opacity-20" />
              </div>
            </div>

            {/* Files Uploaded This Session */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Session Uploads</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{sessionInfo.upload_count}</p>
                </div>
                <FileUp className="w-10 h-10 text-orange-500 opacity-20" />
              </div>
            </div>

            {/* Passed Controls */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-teal-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Passed Controls</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.passed_controls}</p>
                </div>
                <TrendingUp className="w-10 h-10 text-teal-500 opacity-20" />
              </div>
            </div>
          </div>
        )}

        {/* Session Info Cards */}
        {sessionInfo && !stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {/* Company Info */}
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Building2 className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-1" />
                <div>
                  <div className="text-xs text-indigo-600 font-medium">Company</div>
                  <div className="text-sm font-bold text-gray-900">{sessionInfo.vendor.company}</div>
                  <div className="text-xs text-gray-600 mt-1">ID: {sessionInfo.vendor.vendor_id}</div>
                </div>
              </div>
            </div>

            {/* Email */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Mail className="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" />
                <div>
                  <div className="text-xs text-blue-600 font-medium">Email</div>
                  <div className="text-sm font-bold text-gray-900 break-all">{sessionInfo.vendor.email}</div>
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

        {/* Configurations Management */}
        <div className="mt-6 bg-white rounded-2xl shadow-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Configuration Management</h2>
            <div className="text-sm text-gray-500">
              {configurations.length} configuration{configurations.length !== 1 ? 's' : ''}
            </div>
          </div>

          {configurations.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Configurations Yet</h3>
              <p className="mb-4">Upload your first configuration file to get started</p>
              <button
                onClick={() => navigate('/vendor/upload')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Upload Configuration
              </button>
            </div>
          ) : (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {configurations.map((config) => {
                // Find associated audit
                const associatedAudit = audits.find(a => a.configuration.config_id === config.config_id);
                
                return (
                  <div key={config.config_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2">
                          <h4 className="font-medium text-gray-900 truncate">{config.filename}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(config.status)}`}>
                            {config.status}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-3">
                          <div>
                            <span className="font-medium">Config ID:</span>
                            <div className="font-mono text-xs">{config.config_id}</div>
                          </div>
                          <div>
                            <span className="font-medium">Vendor:</span>
                            <div>{config.vendor}</div>
                          </div>
                          <div>
                            <span className="font-medium">Confidence:</span>
                            <div>{(((config as any).vendor_confidence ?? 0) * 100).toFixed(0)}%</div>
                          </div>
                          <div>
                            <span className="font-medium">Uploaded:</span>
                            <div className="text-xs">{new Date(config.created_at).toLocaleDateString()}</div>
                          </div>
                        </div>

                        {/* Audit Status */}
                        {associatedAudit && (
                          <div className="bg-gray-50 rounded-lg p-3 mb-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-700">Latest Audit Results</span>
                              <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskLevelColor(associatedAudit.risk_level)}`}>
                                {associatedAudit.risk_level}
                              </span>
                            </div>
                            <div className="flex items-center space-x-4 text-sm">
                              <div>
                                <span className="text-gray-600">Compliance:</span>
                                <span className="font-medium ml-1">{associatedAudit.compliance_score}%</span>
                              </div>
                              <div>
                                <span className="text-gray-600">Status:</span>
                                <span className={`ml-1 px-2 py-0.5 rounded text-xs ${getStatusColor(associatedAudit.status)}`}>
                                  {associatedAudit.status}
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex flex-col space-y-2 ml-4">
                        <button
                          onClick={() => viewConfiguration(config.config_id)}
                          className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                        >
                          <Eye className="w-3 h-3" />
                          <span>View</span>
                        </button>
                        
                        {associatedAudit && associatedAudit.status === 'COMPLETED' && (
                          <button
                            onClick={() => viewAuditDetails(associatedAudit.audit_id)}
                            className="flex items-center space-x-1 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                          >
                            <Download className="w-3 h-3" />
                            <span>Report</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
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
