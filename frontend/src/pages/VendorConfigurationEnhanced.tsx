import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, CheckCircle, AlertCircle, FileText, Shield, 
  Download, Eye, Loader, RefreshCw, Hash, Clock, Database,
  Activity, BarChart3, FileCheck, AlertTriangle, XCircle
} from 'lucide-react';
import { 
  isVendorLoggedIn, 
  getVendorConfigurations, 
  getVendorAudits, 
  runVendorAudit,
  downloadVendorAuditReport,
  getVendorConfigurationDetails,
  type ConfigurationDetails
} from '../services/vendorApi';

interface Configuration {
  config_id: string;
  filename: string;
  file_type: string;
  status: string;
  vendor: string;
  vendor_confidence: number;
  created_at: string;
  file_size?: number;
}

interface Audit {
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

export default function VendorConfigurationEnhanced() {
  const { configId } = useParams<{ configId: string }>();
  const navigate = useNavigate();
  const [configuration, setConfiguration] = useState<Configuration | null>(null);
  const [configDetails, setConfigDetails] = useState<ConfigurationDetails | null>(null);
  const [audit, setAudit] = useState<Audit | null>(null);
  const [loading, setLoading] = useState(true);
  const [auditLoading, setAuditLoading] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState(1);
  const [activeTab, setActiveTab] = useState<'overview' | 'technical' | 'content' | 'audit'>('overview');

  useEffect(() => {
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }
    
    if (!configId) {
      navigate('/vendor/dashboard');
      return;
    }

    loadConfiguration();
    loadConfigurationDetails();
  }, [configId, navigate]);

  const loadConfiguration = async () => {
    setLoading(true);
    setError('');
    
    try {
      const configResponse = await getVendorConfigurations();

      if (configResponse.success) {
        const configs = configResponse.data.configurations || [];
        const config = configs.find((c: Configuration) => c.config_id === configId);
        
        if (!config) {
          setError('Configuration not found');
          return;
        }
        
        setConfiguration(config);
        setCurrentStep(2);
        
        // Check if audit exists
        const auditResponse = await getVendorAudits();
        
        if (auditResponse.success) {
          const audits = auditResponse.data.audits || [];
          const configAudit = audits.find((a: Audit) => a.configuration?.config_id === configId);
          
          if (configAudit) {
            setAudit(configAudit);
            setCurrentStep(3);
          }
        }
      } else {
        setError('Failed to load configuration');
      }
    } catch (err) {
      setError('Error loading configuration');
    } finally {
      setLoading(false);
    }
  };

  const loadConfigurationDetails = async () => {
    if (!configId) return;
    
    setDetailsLoading(true);
    try {
      const response = await getVendorConfigurationDetails(configId);
      if (response.success && response.data) {
        setConfigDetails(response.data);
      }
    } catch (err) {
      console.error('Error loading configuration details:', err);
    } finally {
      setDetailsLoading(false);
    }
  };

  const runAudit = async () => {
    if (!configId) return;
    
    setAuditLoading(true);
    try {
      const response = await runVendorAudit(configId);
      if (response.success) {
        // Reload configuration to get updated audit info
        setTimeout(loadConfiguration, 2000);
      }
    } catch (err) {
      console.error('Error running audit:', err);
    } finally {
      setAuditLoading(false);
    }
  };

  // Helper functions
  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'COMPLETED': return 'bg-green-100 text-green-800';
      case 'UPLOADED': return 'bg-blue-100 text-blue-800';
      case 'PROCESSING': return 'bg-yellow-100 text-yellow-800';
      case 'FAILED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'LOW': return 'text-green-600';
      case 'MEDIUM': return 'text-yellow-600';
      case 'HIGH': return 'text-orange-600';
      case 'CRITICAL': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            {/* Basic Configuration Info */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuration Overview</h3>
              
              {configuration && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Config ID:</span>
                    <div className="text-gray-900 font-mono">{configuration.config_id}</div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">File Type:</span>
                    <div className="text-gray-900">{configuration.file_type || 'N/A'}</div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Detected Vendor:</span>
                    <div className="text-gray-900">{configuration.vendor}</div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Confidence:</span>
                    <div className="text-gray-900">{(configuration.vendor_confidence * 100).toFixed(0)}%</div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Status:</span>
                    <div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(configuration.status)}`}>
                        {configuration.status}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Uploaded:</span>
                    <div className="text-gray-900 text-xs">
                      {new Date(configuration.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Processing Status */}
            {configDetails && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Status</h3>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${configDetails.processing_status.ingested ? 'bg-green-100' : 'bg-gray-100'}`}>
                      {configDetails.processing_status.ingested ? <CheckCircle className="w-5 h-5 text-green-600" /> : <XCircle className="w-5 h-5 text-gray-400" />}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Ingested</div>
                      <div className="text-sm text-gray-500">File processed</div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${configDetails.processing_status.vendor_detected ? 'bg-green-100' : 'bg-gray-100'}`}>
                      {configDetails.processing_status.vendor_detected ? <CheckCircle className="w-5 h-5 text-green-600" /> : <XCircle className="w-5 h-5 text-gray-400" />}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Vendor Detected</div>
                      <div className="text-sm text-gray-500">Device identified</div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${configDetails.processing_status.audited ? 'bg-green-100' : 'bg-gray-100'}`}>
                      {configDetails.processing_status.audited ? <CheckCircle className="w-5 h-5 text-green-600" /> : <XCircle className="w-5 h-5 text-gray-400" />}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Audited</div>
                      <div className="text-sm text-gray-500">Security scanned</div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-full bg-blue-100">
                      <Shield className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Ready</div>
                      <div className="text-sm text-gray-500">Analysis complete</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        );

      case 'technical':
        return (
          <div className="space-y-6">
            {configDetails ? (
              <>
                {/* File Integrity & Metadata */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                    <Hash className="w-5 h-5" />
                    <span>File Integrity & Metadata</span>
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">SHA-256 Hash:</span>
                        <div className="text-gray-900 font-mono text-xs break-all mt-1">
                          {configDetails.file_integrity.sha256_hash}
                        </div>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Internal Filename:</span>
                        <div className="text-gray-900 font-mono">{configDetails.internal_filename}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">File Size:</span>
                        <div className="text-gray-900">{formatFileSize(configDetails.file_content.stats.file_size_bytes)}</div>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Total Lines:</span>
                        <div className="text-gray-900">{configDetails.file_content.stats.total_lines}</div>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Preview Lines:</span>
                        <div className="text-gray-900">{configDetails.file_content.stats.preview_lines}</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Vendor Detection Details */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                    <Activity className="w-5 h-5" />
                    <span>Vendor Detection Analysis</span>
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-2">Detected Vendor</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {configDetails.vendor_detection.detected_vendor}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-2">Confidence Score</div>
                      <div className="flex items-center space-x-3">
                        <div className="text-lg font-semibold text-gray-900">
                          {(configDetails.vendor_detection.confidence * 100).toFixed(1)}%
                        </div>
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${configDetails.vendor_detection.confidence * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Upload Metadata */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                    <Clock className="w-5 h-5" />
                    <span>Upload Information</span>
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Uploaded By:</span>
                      <div className="text-gray-900 font-mono">{configDetails.upload_metadata.uploaded_by}</div>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Upload Date:</span>
                      <div className="text-gray-900">
                        {new Date(configDetails.upload_metadata.uploaded_at).toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Organization ID:</span>
                      <div className="text-gray-900">{configDetails.upload_metadata.organization_id}</div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center justify-center py-8">
                  {detailsLoading ? (
                    <Loader className="w-6 h-6 animate-spin text-gray-400" />
                  ) : (
                    <div className="text-center text-gray-500">
                      <Database className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                      <p>Technical details not available</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        );

      case 'content':
        return (
          <div className="space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <FileText className="w-5 h-5" />
                <span>Configuration File Preview</span>
              </h3>
              
              {configDetails?.file_content.preview ? (
                <div className="space-y-4">
                  <div className="text-sm text-gray-600 mb-3">
                    Showing first {configDetails.file_content.stats.preview_lines} lines of {configDetails.file_content.stats.total_lines} total lines.
                    Sensitive information has been sanitized.
                  </div>
                  
                  <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
                      {configDetails.file_content.preview}
                    </pre>
                  </div>
                  
                  {configDetails.file_content.stats.total_lines > configDetails.file_content.stats.preview_lines && (
                    <div className="text-sm text-gray-500 text-center py-2">
                      ... {configDetails.file_content.stats.total_lines - configDetails.file_content.stats.preview_lines} more lines (truncated for preview)
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p>Configuration content not available</p>
                </div>
              )}
            </div>
          </div>
        );

      case 'audit':
        return (
          <div className="space-y-6">
            {audit ? (
              <>
                {/* Compliance Score */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-indigo-100">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-indigo-900">Security Compliance</h3>
                    <span className="text-3xl font-bold text-indigo-900">{audit.compliance_score}%</span>
                  </div>
                  <div className="w-full bg-indigo-200 rounded-full h-3 mb-2">
                    <div 
                      className="bg-indigo-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${audit.compliance_score}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-sm text-indigo-700">
                    <span>Risk Level: <span className={`font-semibold ${getRiskColor(audit.risk_level)}`}>{audit.risk_level}</span></span>
                    <span>Score: {audit.risk_score}/10</span>
                  </div>
                </div>

                {/* Findings Summary */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Findings Overview</h3>
                  
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-green-600">{audit.passed_count}</div>
                      <div className="text-sm font-medium text-green-700">Passed</div>
                    </div>
                    <div className="bg-red-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-red-600">{audit.failed_count}</div>
                      <div className="text-sm font-medium text-red-700">Failed</div>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-yellow-600">{audit.warning_count}</div>
                      <div className="text-sm font-medium text-yellow-700">Warnings</div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={() => navigate(`/vendor/audit/${audit.audit_id}`)}
                    className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    <span>View Detailed Results</span>
                  </button>

                  <button
                    onClick={() => downloadVendorAuditReport(audit.audit_id)}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download Report</span>
                  </button>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="text-center py-8">
                  {currentStep === 2 && !auditLoading && (
                    <>
                      <Shield className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Security Audit Available</h3>
                      <p className="text-gray-500 mb-6">Run a security audit to analyze this configuration for compliance issues.</p>
                      <button
                        onClick={runAudit}
                        disabled={auditLoading}
                        className="flex items-center space-x-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mx-auto"
                      >
                        {auditLoading ? <Loader className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                        <span>{auditLoading ? 'Running Audit...' : 'Run Security Audit'}</span>
                      </button>
                    </>
                  )}
                  
                  {auditLoading && (
                    <div className="text-center">
                      <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-indigo-600" />
                      <p className="text-gray-600">Running security audit...</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center py-12">
          <Loader className="w-8 h-8 animate-spin text-indigo-600" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-6 h-6 text-red-600" />
            <div>
              <h3 className="text-lg font-medium text-red-900">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/vendor/dashboard')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </button>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={loadConfigurationDetails}
            disabled={detailsLoading}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${detailsLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Configuration Title */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {configuration?.filename || 'Configuration Details'}
        </h1>
        <p className="text-gray-600 mt-1">
          Comprehensive configuration analysis and security assessment
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'overview', label: 'Overview', icon: FileCheck },
            { key: 'technical', label: 'Technical Details', icon: BarChart3 },
            { key: 'content', label: 'File Content', icon: FileText },
            { key: 'audit', label: 'Security Audit', icon: Shield }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key as any)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === key
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mb-8">
        {renderTabContent()}
      </div>
    </div>
  );
}