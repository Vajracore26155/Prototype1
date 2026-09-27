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

export default function VendorConfiguration() {
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
    setError('');
    
    try {
      const auditResponse = await runVendorAudit(configId);

      if (auditResponse.success) {
        setAudit(auditResponse.data);
        setCurrentStep(auditResponse.data.status === 'COMPLETED' ? 4 : 3);
      }
    } catch (err: any) {
      console.error('Failed to run audit:', err);
      setError(err.response?.data?.error?.message || 'Failed to run audit');
    } finally {
      setAuditLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!audit?.audit_id) return;
    
    try {
      const blob = await downloadVendorAuditReport(audit.audit_id);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit_report_${audit.audit_id}_${configuration?.filename || 'config'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('Failed to download report:', err);
      setError('Failed to download report. Please try again.');
    }
  };

  const viewAuditDetails = () => {
    if (audit?.audit_id) {
      navigate(`/vendor/audit/${audit.audit_id}`);
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-indigo-600" />
            <p className="text-gray-600">Loading configuration...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        
        {/* Header with Back Button */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/vendor/dashboard')}
                className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Dashboard</span>
              </button>
              <div className="w-px h-6 bg-gray-300"></div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Configuration Processing</h1>
                <p className="text-gray-600">{configuration?.filename || 'Loading...'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Progress Steps */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Processing Workflow</h2>
          
          <div className="flex items-center justify-between">
            {/* Step 1: Upload */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep >= 1 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
              }`}>
                <CheckCircle className="w-5 h-5" />
              </div>
              <div className="text-sm font-medium text-gray-900 mt-2">Upload</div>
              <div className="text-xs text-gray-500">File received</div>
            </div>

            {/* Connector */}
            <div className={`flex-1 h-px ${
              currentStep >= 2 ? 'bg-green-300' : 'bg-gray-200'
            }`}></div>

            {/* Step 2: Configuration */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep >= 2 ? 'bg-green-100 text-green-600' : 
                currentStep === 1 ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
              }`}>
                {currentStep === 1 ? <Loader className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
              </div>
              <div className="text-sm font-medium text-gray-900 mt-2">Configuration</div>
              <div className="text-xs text-gray-500">Processing & analysis</div>
            </div>

            {/* Connector */}
            <div className={`flex-1 h-px ${
              currentStep >= 3 ? 'bg-green-300' : 'bg-gray-200'
            }`}></div>
            {/* Step 3: Security Audit */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep >= 3 ? 'bg-green-100 text-green-600' : 
                currentStep === 2 ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
              }`}>
                {auditLoading ? <Loader className="w-5 h-5 animate-spin" /> : <Shield className="w-5 h-5" />}
              </div>
              <div className="text-sm font-medium text-gray-900 mt-2">Security Audit</div>
              <div className="text-xs text-gray-500">Compliance check</div>
            </div>

            {/* Connector */}
            <div className={`flex-1 h-px ${
              currentStep >= 4 ? 'bg-green-300' : 'bg-gray-200'
            }`}></div>

            {/* Step 4: Report */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep >= 4 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
              }`}>
                <Download className="w-5 h-5" />
              </div>
              <div className="text-sm font-medium text-gray-900 mt-2">Report</div>
              <div className="text-xs text-gray-500">Ready for download</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Configuration Details */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Configuration Details</h3>
            
            {configuration ? (
              <div className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
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
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  {currentStep === 2 && !audit && (
                    <button
                      onClick={runAudit}
                      disabled={auditLoading}
                      className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {auditLoading ? <Loader className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                      <span>{auditLoading ? 'Running Audit...' : 'Run Security Audit'}</span>
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>Loading configuration details...</p>
              </div>
            )}
          </div>
          {/* Audit Results */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Security Audit Results</h3>
            
            {audit ? (
              <div className="space-y-4">
                {/* Compliance Score */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-indigo-100">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-indigo-700">Compliance Score</span>
                    <span className="text-2xl font-bold text-indigo-900">{audit.compliance_score}%</span>
                  </div>
                  <div className="w-full bg-indigo-200 rounded-full h-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${audit.compliance_score}%` }}
                    ></div>
                  </div>
                </div>

                {/* Risk Level */}
                <div className={`rounded-lg p-4 border ${getRiskLevelColor(audit.risk_level)}`}>
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-5 h-5" />
                    <span className="font-medium">Risk Level: {audit.risk_level}</span>
                  </div>
                </div>

                {/* Audit Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-green-50 rounded-lg p-3 text-center">
                    <div className="text-lg font-bold text-green-900">{audit.passed_count}</div>
                    <div className="text-xs text-green-700">Passed</div>
                  </div>
                  <div className="bg-red-50 rounded-lg p-3 text-center">
                    <div className="text-lg font-bold text-red-900">{audit.failed_count}</div>
                    <div className="text-xs text-red-700">Failed</div>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-3 text-center">
                    <div className="text-lg font-bold text-yellow-900">{audit.warning_count}</div>
                    <div className="text-xs text-yellow-700">Warnings</div>
                  </div>
                </div>

                {/* Human Review Alert */}
                {audit.requires_human_review && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-amber-900">Human Review Required</div>
                        <div className="text-sm text-amber-700 mt-1">
                          This configuration requires manual review by security experts.
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={viewAuditDetails}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    <span>View Details</span>
                  </button>
                  
                  {audit.status === 'COMPLETED' && (
                    <button
                      onClick={downloadReport}
                      className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download Report</span>
                    </button>
                  )}
                  
                  <button
                    onClick={loadConfiguration}
                    className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Refresh</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Shield className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p className="mb-4">No audit results yet</p>
                {currentStep >= 2 && (
                  <button
                    onClick={runAudit}
                    disabled={auditLoading}
                    className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mx-auto"
                  >
                    {auditLoading ? <Loader className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                    <span>{auditLoading ? 'Running...' : 'Start Audit'}</span>
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}