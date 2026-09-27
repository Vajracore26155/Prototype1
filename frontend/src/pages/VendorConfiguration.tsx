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
      await downloadVendorAuditReport(audit.audit_id);
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
      case 'critical': return 'bg-ink-950 text-white border-ink-950';
      case 'high': return 'bg-ink-950 text-white border-ink-950';
      case 'medium': return 'bg-mist-200 text-ink-950 border-line';
      case 'low': return 'bg-white text-ink-900 border-line';
      default: return 'bg-mist-100 text-ink-500 border-line';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'bg-ink-950 text-white';
      case 'processing':
      case 'running': return 'bg-mist-200 text-ink-950';
      case 'failed': return 'bg-ink-950 text-white';
      default: return 'bg-mist-100 text-ink-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-mist-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="tatva-card p-8 text-center">
            <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-ink-950" />
            <p className="font-bold text-ink-500">Loading configuration...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-mist-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">

        {/* Header with Back Button */}
        <div className="tatva-card p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/vendor/dashboard')}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-bold text-ink-500 hover:text-ink-950 hover:bg-mist-100 rounded-xl transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Dashboard</span>
              </button>
              <div className="w-px h-6 bg-line"></div>
              <div>
                <div className="text-[11px] font-bold tracking-[0.28em] text-ink-500">CONFIGURATION</div>
                <h1 className="text-3xl font-bold tracking-tight text-ink-900">Configuration Processing</h1>
                <p className="font-semibold text-ink-500">{configuration?.filename || 'Loading...'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-ink-950 text-white px-4 py-3 rounded-xl mb-6 font-bold text-sm">
            {error}
          </div>
        )}

        {/* Progress Steps */}
        <div className="tatva-card p-6 mb-6">
          <h2 className="text-2xl font-bold tracking-tight text-ink-900 mb-6">Processing Workflow</h2>
          
          <div className="flex items-center justify-between">
            {/* Step 1: Upload */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold ${
                currentStep >= 1 ? 'bg-ink-950 text-white' : 'bg-mist-100 text-ink-500'
              }`}>
                <CheckCircle className="w-5 h-5" />
              </div>
              <div className="text-sm font-bold text-ink-900 mt-2">Upload</div>
              <div className="text-xs font-semibold text-ink-500">File received</div>
            </div>

            {/* Connector */}
            <div className={`flex-1 h-0.5 rounded ${
              currentStep >= 2 ? 'bg-ink-950' : 'bg-line'
            }`}></div>

            {/* Step 2: Configuration */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold ${
                currentStep >= 2 ? 'bg-ink-950 text-white' :
                currentStep === 1 ? 'bg-mist-200 text-ink-950' : 'bg-mist-100 text-ink-500'
              }`}>
                {currentStep === 1 ? <Loader className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
              </div>
              <div className="text-sm font-bold text-ink-900 mt-2">Configuration</div>
              <div className="text-xs font-semibold text-ink-500">Processing & analysis</div>
            </div>

            {/* Connector */}
            <div className={`flex-1 h-0.5 rounded ${
              currentStep >= 3 ? 'bg-ink-950' : 'bg-line'
            }`}></div>
            {/* Step 3: Security Audit */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold ${
                currentStep >= 3 ? 'bg-ink-950 text-white' :
                currentStep === 2 ? 'bg-mist-200 text-ink-950' : 'bg-mist-100 text-ink-500'
              }`}>
                {auditLoading ? <Loader className="w-5 h-5 animate-spin" /> : <Shield className="w-5 h-5" />}
              </div>
              <div className="text-sm font-bold text-ink-900 mt-2">Security Audit</div>
              <div className="text-xs font-semibold text-ink-500">Compliance check</div>
            </div>

            {/* Connector */}
            <div className={`flex-1 h-0.5 rounded ${
              currentStep >= 4 ? 'bg-ink-950' : 'bg-line'
            }`}></div>

            {/* Step 4: Report */}
            <div className="flex flex-col items-center flex-1">
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold ${
                currentStep >= 4 ? 'bg-ink-950 text-white' : 'bg-mist-100 text-ink-500'
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
          <div className="tatva-card p-7">
            <div className="text-xs font-bold tracking-[0.24em] text-ink-500">CONFIGURATION</div>
            <h3 className="text-2xl font-bold tracking-tight text-ink-900 mt-1 mb-5">Configuration Details</h3>
            
            {configuration ? (
              <div className="space-y-4">
                <div className="bg-mist-50 border border-line rounded-xl p-5">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wide text-ink-500">Config ID</span>
                      <div className="text-ink-900 font-mono font-bold">{configuration.config_id}</div>
                    </div>
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wide text-ink-500">File Type</span>
                      <div className="font-bold text-ink-900">{configuration.file_type || 'N/A'}</div>
                    </div>
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wide text-ink-500">Detected Vendor</span>
                      <div className="font-bold text-ink-900">{configuration.vendor || 'Unknown'}</div>
                    </div>
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wide text-ink-500">Confidence</span>
                      <div className="font-bold text-ink-900">{(((configuration as any).vendor_confidence ?? 0) * 100).toFixed(0)}%</div>
                    </div>
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wide text-ink-500">Status</span>
                      <div>
                        <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${getStatusColor(configuration.status)}`}>
                          {configuration.status}
                        </span>
                      </div>
                    </div>
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wide text-ink-500">Uploaded</span>
                      <div className="font-bold text-ink-900 text-xs">
                        {configuration.created_at ? new Date(configuration.created_at).toLocaleString() : 'N/A'}
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
                      className="btn-ink flex items-center space-x-2 px-8 py-3.5 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {auditLoading ? <Loader className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                      <span>{auditLoading ? 'Running Audit...' : 'Run Security Audit'}</span>
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 font-bold text-ink-500">
                <FileText className="w-12 h-12 mx-auto mb-3 text-line" />
                <p>Loading configuration details...</p>
              </div>
            )}
          </div>
          {/* Audit Results */}
          <div className="tatva-card p-7">
            <div className="text-xs font-bold tracking-[0.24em] text-ink-500">AUDIT OUTCOME</div>
            <h3 className="text-2xl font-bold tracking-tight text-ink-900 mt-1 mb-5">Security Audit Results</h3>
            
            {audit ? (
              <div className="space-y-5">
                {/* Compliance Score */}
                <div className="bg-ink-950 text-white rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold tracking-[0.2em] text-white/60">COMPLIANCE SCORE</span>
                    <span className="text-3xl font-bold">{audit.compliance_score}%</span>
                  </div>
                  <div className="w-full bg-white/20 rounded-full h-2.5">
                    <div
                      className="bg-white h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${audit.compliance_score}%` }}
                    ></div>
                  </div>
                </div>

                {/* Risk Level */}
                <div className={`rounded-2xl p-5 border-2 font-bold ${getRiskLevelColor(audit.risk_level)}`}>
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-5 h-5" />
                    <span className="text-lg">Risk Level: {audit.risk_level}</span>
                  </div>
                </div>

                {/* Audit Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-mist-50 border border-line rounded-2xl p-4 text-center">
                    <div className="text-2xl font-bold text-ink-950">{audit.passed_count}</div>
                    <div className="text-xs font-bold tracking-wide text-ink-500">PASSED</div>
                  </div>
                  <div className="bg-ink-950 rounded-2xl p-4 text-center">
                    <div className="text-2xl font-bold text-white">{audit.failed_count}</div>
                    <div className="text-xs font-bold tracking-wide text-white/60">FAILED</div>
                  </div>
                  <div className="bg-mist-50 border border-line rounded-2xl p-4 text-center">
                    <div className="text-2xl font-bold text-ink-950">{audit.warning_count}</div>
                    <div className="text-xs font-bold tracking-wide text-ink-500">WARNINGS</div>
                  </div>
                </div>

                {/* Human Review Alert — prominent */}
                {audit.requires_human_review && (
                  <div className="bg-ink-950 text-white rounded-2xl p-6 border-2 border-ink-950">
                    <div className="flex items-start space-x-3">
                      <span className="w-9 h-9 rounded-xl bg-white text-ink-950 flex items-center justify-center font-bold shrink-0">!</span>
                      <div>
                        <div className="font-bold text-lg tracking-tight">Human Evaluation Required</div>
                        <div className="text-sm font-semibold text-white/75 mt-1">
                          This configuration requires manual review by security experts before sign-off.
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={viewAuditDetails}
                    className="btn-ink flex items-center space-x-2 px-6 py-3 rounded-xl text-sm"
                  >
                    <Eye className="w-4 h-4" />
                    <span>View Details</span>
                  </button>

                  {audit.status === 'COMPLETED' && (
                    <button
                      onClick={downloadReport}
                      className="btn-paper flex items-center space-x-2 px-6 py-3 rounded-xl text-sm"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download Report</span>
                    </button>
                  )}

                  <button
                    onClick={loadConfiguration}
                    className="flex items-center space-x-2 px-6 py-3 bg-mist-100 text-ink-900 rounded-xl hover:bg-mist-200 text-sm font-bold"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Refresh</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 font-bold text-ink-500">
                <Shield className="w-12 h-12 mx-auto mb-3 text-line" />
                <p className="mb-4">No audit results yet</p>
                {currentStep >= 2 && (
                  <button
                    onClick={runAudit}
                    disabled={auditLoading}
                    className="btn-ink flex items-center space-x-2 px-8 py-3.5 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed mx-auto"
                  >
                    {auditLoading ? <Loader className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                    <span>{auditLoading ? 'Running...' : 'Start Audit'}</span>
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Detailed Configuration (file preview, integrity, audits) */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mt-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Detailed Configuration</h3>
          {detailsLoading ? (
            <p className="text-gray-500 text-sm">Loading file details...</p>
          ) : configDetails ? (
            <div className="space-y-4 text-sm">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="font-medium text-gray-700">Vendor Detection</div>
                  <div className="text-gray-900">{configDetails.vendor_detection?.detected_vendor || 'Unknown'} ({(((configDetails.vendor_detection as any)?.confidence ?? 0) * 100).toFixed(1)}%)</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="font-medium text-gray-700">File Integrity</div>
                  <div className="text-gray-900 font-mono text-xs break-all">{configDetails.file_integrity?.sha256_hash || 'N/A'}</div>
                  <div className="text-gray-500 text-xs mt-1">{configDetails.file_content?.stats?.total_lines ?? 0} lines • {((configDetails.file_content?.stats?.file_size_bytes ?? 0) / 1024).toFixed(1)} KB</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="font-medium text-gray-700">Processing</div>
                  <div className="text-gray-900">Ingested: {configDetails.processing_status?.ingested ? 'Yes' : 'No'} • Audited: {configDetails.processing_status?.audited ? 'Yes' : 'No'}</div>
                  <div className="text-gray-500 text-xs mt-1">Audits: {(configDetails.audits || []).length}</div>
                </div>
              </div>
              <div>
                <div className="font-medium text-gray-700 mb-2">File Preview (sanitized, first 50 lines)</div>
                <pre className="bg-gray-900 text-green-300 rounded-lg p-4 overflow-x-auto text-xs whitespace-pre-wrap max-h-80 overflow-y-auto">{configDetails.file_content?.preview || 'No preview available'}</pre>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No detailed file information available.</p>
          )}
        </div>
      </div>
    </div>
  );
}