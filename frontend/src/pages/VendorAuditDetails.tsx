import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Shield, AlertCircle, CheckCircle, XCircle, 
  AlertTriangle, Download, FileText, Clock, BarChart3,
  TrendingUp, Info
} from 'lucide-react';
import { 
  isVendorLoggedIn, 
  getVendorAudit,
  getVendorAuditFindings,
  downloadVendorAuditReport 
} from '../services/vendorApi';

interface AuditDetails {
  audit_id: string;
  configuration: {
    config_id: string;
    filename: string;
    vendor: string;
  };
  status: string;
  compliance_score: number;
  risk_score: number;
  risk_level: string;
  passed_count: number;
  failed_count: number;
  warning_count: number;
  started_at: string;
  completed_at?: string;
  requires_human_review: boolean;
  review_reason?: string;
  interpretation_confidence?: number;
  error_message?: string;
}

interface Finding {
  finding_id: string;
  rule_id: string;
  rule_name: string;
  severity: string;
  category: string;
  description: string;
  evidence: string;
  recommendation: string;
  status: string;
  confidence_score: number;
}

export default function VendorAuditDetails() {
  const { auditId } = useParams<{ auditId: string }>();
  const navigate = useNavigate();
  const [audit, setAudit] = useState<AuditDetails | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'evidence'>('overview');

  useEffect(() => {
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }
    
    if (!auditId) {
      navigate('/vendor/dashboard');
      return;
    }

    loadAuditDetails();
  }, [auditId, navigate]);

  const loadAuditDetails = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Get audit details using vendor API (includes normalized findings)
      const auditResponse = await getVendorAudit(auditId!);

      if (auditResponse.success) {
        setAudit(auditResponse.data);
        const embedded: any[] = Array.isArray((auditResponse.data as any)?.findings)
          ? (auditResponse.data as any).findings
          : [];
        if (embedded.length > 0) {
          setFindings(embedded);
        }
        
        // Load findings via vendor-scoped endpoint (no JWT required)
        try {
          const findingsResponse = await getVendorAuditFindings(auditId!);
          const list = (findingsResponse as any)?.data?.findings || (findingsResponse as any)?.data?.data?.findings || [];
          if (Array.isArray(list) && list.length > 0) {
            // normalize to UI shape if backend returns raw shape
            const norm = list.map((f: any) => ({
              finding_id: f.finding_id,
              rule_id: f.rule_id,
              rule_name: f.rule_name || f.title || f.rule_id,
              severity: f.severity || 'LOW',
              category: f.category || 'General',
              description: f.description || '',
              evidence: typeof f.evidence === 'string' ? f.evidence : (f.evidence_text || f.evidence?.evidence_text || ''),
              recommendation: f.recommendation || f.remediation || '',
              status: f.status || 'UNKNOWN',
              confidence_score: f.confidence_score ?? 0.95,
            }));
            setFindings(norm);
          } else if (embedded.length === 0) {
            // keep embedded (may be empty = truly no issues)
            setFindings(embedded);
          }
        } catch (err) {
          console.warn('Could not load findings, using embedded:', err);
          // fallback already set from embedded
        }
      } else {
        setError('Failed to load audit details');
      }
    } catch (err: any) {
      console.error('Failed to load audit:', err);
      setError(err.response?.data?.error?.message || 'Failed to load audit details');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!auditId) return;
    
    try {
      await downloadVendorAuditReport(auditId);
    } catch (err: any) {
      console.error('Failed to download report:', err);
      setError('Failed to download report. Please try again.');
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

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-ink-950 text-white';
      case 'high': return 'bg-ink-950 text-white';
      case 'medium': return 'bg-mist-200 text-ink-950';
      case 'low': return 'bg-white text-ink-900 border border-line';
      case 'info': return 'bg-mist-100 text-ink-900';
      default: return 'bg-mist-100 text-ink-500';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return <XCircle className="w-4 h-4" />;
      case 'high': return <AlertCircle className="w-4 h-4" />;
      case 'medium': return <AlertTriangle className="w-4 h-4" />;
      case 'low': return <Info className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-mist-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="tatva-card p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-line border-t-ink-950 rounded-full mx-auto mb-4"></div>
            <p className="font-bold text-ink-500">Loading audit details...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-mist-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">

        {/* Header with Back Button */}
        <div className="tatva-card p-6 mb-6">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center space-x-4 min-w-0">
              <button
                onClick={() => navigate(`/vendor/configuration/${audit?.configuration.config_id}`)}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-bold text-ink-500 hover:text-ink-950 hover:bg-mist-100 rounded-xl transition-colors shrink-0"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Configuration</span>
              </button>
              <div className="w-px h-6 bg-line"></div>
              <div className="min-w-0">
                <div className="text-[11px] font-bold tracking-[0.28em] text-ink-500">SECURITY AUDIT REPORT</div>
                <h1 className="text-3xl font-bold tracking-tight text-ink-900 truncate">Security Audit Report</h1>
                <p className="font-semibold text-ink-500">{audit?.configuration.filename || 'Loading...'}</p>
              </div>
            </div>
            <button
              onClick={downloadReport}
              className="btn-ink flex items-center space-x-2 px-8 py-3.5 rounded-xl text-sm shrink-0"
            >
              <Download className="w-4 h-4" />
              <span>Download PDF</span>
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-ink-950 text-white px-4 py-3 rounded-xl mb-6 font-bold text-sm">
            {error}
          </div>
        )}

        {audit && (
          <>
            {/* Audit Summary */}
            <div className="tatva-card p-6 sm:p-8 mb-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-5">

                {/* Compliance Score */}
                <div className="bg-ink-950 text-white rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold tracking-[0.2em] text-white/60">COMPLIANCE SCORE</span>
                    <BarChart3 className="w-5 h-5" />
                  </div>
                  <div className="text-4xl font-bold mb-2">{audit.compliance_score}%</div>
                  <div className="w-full bg-white/20 rounded-full h-2.5">
                    <div
                      className="bg-white h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${audit.compliance_score}%` }}
                    ></div>
                  </div>
                </div>

                {/* Risk Level */}
                <div className={`rounded-2xl p-5 border-2 font-bold ${getRiskLevelColor(audit.risk_level)}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold tracking-[0.2em]">RISK LEVEL</span>
                    <Shield className="w-5 h-5" />
                  </div>
                  <div className="text-3xl font-bold mb-1">{audit.risk_level}</div>
                  <div className="text-sm font-semibold opacity-75">Score: {audit.risk_score}/100</div>
                </div>

                {/* Test Results */}
                <div className="bg-mist-50 border border-line rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] font-bold tracking-[0.2em] text-ink-500">TEST RESULTS</span>
                    <TrendingUp className="w-5 h-5 text-ink-950" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm font-bold">
                      <span className="text-ink-500">Passed</span>
                      <span className="text-ink-950 text-lg">{audit.passed_count}</span>
                    </div>
                    <div className="flex justify-between text-sm font-bold">
                      <span className="text-ink-500">Failed</span>
                      <span className="text-ink-950 text-lg">{audit.failed_count}</span>
                    </div>
                    <div className="flex justify-between text-sm font-bold">
                      <span className="text-ink-500">Warnings</span>
                      <span className="text-ink-950 text-lg">{audit.warning_count}</span>
                    </div>
                  </div>
                </div>

                {/* Audit Info */}
                <div className="bg-white border border-line rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold tracking-[0.2em] text-ink-500">AUDIT STATUS</span>
                    <Clock className="w-5 h-5 text-ink-950" />
                  </div>
                  <div className="text-sm space-y-1 font-bold">
                    <div className="flex justify-between items-center">
                      <span className="text-ink-500">Status</span>
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                        audit.status === 'COMPLETED' ? 'bg-ink-950 text-white' : 'bg-mist-100 text-ink-500'
                      }`}>
                        {audit.status}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-ink-500 mt-2">
                      {audit.completed_at ? `Completed: ${new Date(audit.completed_at).toLocaleString()}` : 'In Progress'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Human Review Alert — prominent */}
              {audit.requires_human_review && (
                <div className="mt-6 bg-ink-950 text-white rounded-2xl p-6">
                  <div className="flex items-start space-x-3">
                    <span className="w-9 h-9 rounded-xl bg-white text-ink-950 flex items-center justify-center font-bold shrink-0">!</span>
                    <div>
                      <div className="font-bold text-lg tracking-tight">Human Evaluation Required</div>
                      <div className="text-sm text-amber-700 mt-1">
                        {audit.review_reason || 'This configuration requires manual review by security experts.'}
                      </div>
                      {audit.interpretation_confidence && (
                        <div className="text-xs text-amber-600 mt-2">
                          Interpretation Confidence: {(audit.interpretation_confidence * 100).toFixed(0)}%
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
            {/* Tab Navigation */}
            <div className="bg-white rounded-2xl shadow-xl mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'overview'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab('findings')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'findings'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Findings ({findings.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('evidence')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'evidence'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Evidence
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    
                    {/* Configuration Details */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuration Information</h3>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-gray-700">Configuration ID:</span>
                            <div className="text-gray-900 font-mono">{audit.configuration.config_id}</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Filename:</span>
                            <div className="text-gray-900">{audit.configuration.filename}</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Detected Vendor:</span>
                            <div className="text-gray-900">{audit.configuration.vendor}</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Audit ID:</span>
                            <div className="text-gray-900 font-mono">{audit.audit_id}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Executive Summary */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Executive Summary</h3>
                      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                        <p className="text-blue-900 leading-relaxed">
                          This security audit analyzed the configuration file <strong>{audit.configuration.filename}</strong> and 
                          found a compliance score of <strong>{audit.compliance_score}%</strong> with a 
                          <strong className="ml-1">{audit.risk_level.toLowerCase()}</strong> risk level. 
                          The audit identified <strong>{audit.failed_count}</strong> security issues that require attention, 
                          along with <strong>{audit.warning_count}</strong> recommendations for improvement.
                          {audit.requires_human_review && (
                            <span className="block mt-2 text-amber-800 bg-amber-100 rounded p-2 text-sm">
                              ⚠️ This configuration requires additional human expert review due to complex security patterns.
                            </span>
                          )}
                        </p>
                      </div>
                    </div>

                    {/* Risk Analysis */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Analysis</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        
                        {/* Critical/High Findings */}
                        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                          <div className="flex items-center space-x-2 mb-2">
                            <XCircle className="w-5 h-5 text-red-600" />
                            <span className="font-medium text-red-900">High Priority</span>
                          </div>
                          <div className="text-2xl font-bold text-red-900">
                            {findings.filter(f => ['critical', 'high'].includes(f.severity.toLowerCase())).length}
                          </div>
                          <div className="text-sm text-red-700">Critical/High severity issues requiring immediate attention</div>
                        </div>

                        {/* Medium Findings */}
                        <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                          <div className="flex items-center space-x-2 mb-2">
                            <AlertTriangle className="w-5 h-5 text-yellow-600" />
                            <span className="font-medium text-yellow-900">Medium Priority</span>
                          </div>
                          <div className="text-2xl font-bold text-yellow-900">
                            {findings.filter(f => f.severity.toLowerCase() === 'medium').length}
                          </div>
                          <div className="text-sm text-yellow-700">Medium severity issues for planned remediation</div>
                        </div>

                        {/* Low/Info Findings */}
                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                          <div className="flex items-center space-x-2 mb-2">
                            <Info className="w-5 h-5 text-blue-600" />
                            <span className="font-medium text-blue-900">Low Priority</span>
                          </div>
                          <div className="text-2xl font-bold text-blue-900">
                            {findings.filter(f => ['low', 'info'].includes(f.severity.toLowerCase())).length}
                          </div>
                          <div className="text-sm text-blue-700">Low priority recommendations and best practices</div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                {/* Findings Tab */}
                {activeTab === 'findings' && (
                  <div>
                    {findings.length > 0 ? (
                      <div className="space-y-4">
                        {findings.map((finding) => (
                          <div key={finding.finding_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                            
                            {/* Finding Header */}
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center space-x-3">
                                <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(finding.severity)}`}>
                                  {getSeverityIcon(finding.severity)}
                                  <span>{finding.severity}</span>
                                </div>
                                <div className="text-sm text-gray-500">
                                  {finding.category}
                                </div>
                              </div>
                              <div className="text-xs text-gray-400">
                                Confidence: {(((finding as any).confidence_score ?? 0.95) * 100).toFixed(0)}%
                              </div>
                            </div>

                            {/* Finding Title */}
                            <h4 className="font-semibold text-gray-900 mb-2">{finding.rule_name}</h4>
                            
                            {/* Description */}
                            <div className="text-sm text-gray-700 mb-3">
                              {finding.description}
                            </div>

                            {/* Evidence */}
                            {finding.evidence && (
                              <div className="mb-3">
                                <div className="text-xs font-medium text-gray-500 mb-1">Evidence:</div>
                                <div className="bg-gray-50 border rounded p-2 text-xs font-mono text-gray-800 overflow-x-auto">
                                  {finding.evidence}
                                </div>
                              </div>
                            )}

                            {/* Recommendation */}
                            {finding.recommendation && (
                              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                                <div className="text-xs font-medium text-blue-700 mb-1">Recommendation:</div>
                                <div className="text-sm text-blue-900">{finding.recommendation}</div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12 text-gray-500">
                        <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-400" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Security Issues Found</h3>
                        <p>This configuration passed all security checks.</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Evidence Tab */}
                {activeTab === 'evidence' && (
                  <div>
                    <div className="mb-4">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Configuration Evidence</h3>
                      <p className="text-gray-600 text-sm">
                        This section shows the evidence and configuration snippets analyzed during the security audit.
                      </p>
                    </div>
                    
                    {findings.filter(f => f.evidence).length > 0 ? (
                      <div className="space-y-6">
                        {findings.filter(f => f.evidence).map((finding) => (
                          <div key={finding.finding_id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-center space-x-2 mb-3">
                              <div className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(finding.severity)}`}>
                                {finding.severity}
                              </div>
                              <span className="font-medium text-gray-900">{finding.rule_name}</span>
                            </div>
                            
                            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                              <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
                                {finding.evidence}
                              </pre>
                            </div>
                            
                            {finding.recommendation && (
                              <div className="mt-3 text-sm text-gray-600">
                                <strong>Impact:</strong> {finding.description}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12 text-gray-500">
                        <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p>No configuration evidence available for this audit.</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}