import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Shield, AlertCircle, CheckCircle, ChevronDown, AlertTriangle, Download } from 'lucide-react';
import { getAudit, getFindings, downloadAuditReport } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import type { Audit, Finding } from '../types';
import BackButton from '../components/BackButton';

const AuditResults = () => {
  const { auditId } = useParams<{ auditId: string }>();
  const { showSuccess, showError, showInfo } = useToast();
  const [audit, setAudit] = useState<Audit | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedFinding, setExpandedFinding] = useState<string | null>(null);
  const [downloadingReport, setDownloadingReport] = useState(false);
  
  useEffect(() => {
    if (auditId) {
      loadAuditData(auditId);
    }
  }, [auditId]);
  
  const loadAuditData = async (id: string) => {
    try {
      const [auditRes, findingsRes] = await Promise.all([
        getAudit(id),
        getFindings(id)
      ]);
      
      if (auditRes.success && auditRes.data) {
        setAudit(auditRes.data);
      }
      
      if (findingsRes.success && findingsRes.data) {
        setFindings(findingsRes.data.findings);
      }
    } catch (error) {
      console.error('Failed to load audit:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDownloadReport = async () => {
    if (!auditId) return;
    
    setDownloadingReport(true);
    showInfo('Generating Report', 'Creating PDF report...');
    
    console.log('[DEBUG] Starting report download for audit:', auditId);
    
    try {
      await downloadAuditReport(auditId);
      showSuccess('Report Downloaded', 'Audit report has been downloaded successfully.');
      console.log('[DEBUG] Report downloaded successfully');
    } catch (error: any) {
      console.error('[DEBUG] Failed to download report:', error);
      console.error('[DEBUG] Error response:', error.response);
      console.error('[DEBUG] Error status:', error.response?.status);
      console.error('[DEBUG] Error data:', error.response?.data);
      
      const errorMessage = error.response?.data?.detail?.message 
        || error.response?.data?.detail 
        || error.message 
        || 'Failed to download report. Please try again.';
      
      showError('Download Failed', errorMessage);
    } finally {
      setDownloadingReport(false);
    }
  };
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'text-status-critical-text bg-status-critical-bg border-status-critical-border';
      case 'HIGH': return 'text-status-high-text bg-status-high-bg border-status-high-border';
      case 'MEDIUM': return 'text-status-medium-text bg-status-medium-bg border-status-medium-border';
      case 'LOW': return 'text-status-low-text bg-status-low-bg border-status-low-border';
      default: return 'text-neutral-700 bg-neutral-100 border-neutral-300';
    }
  };
  
  const getStatusIcon = (status: string) => {
    if (status === 'PASS') return <CheckCircle className="w-5 h-5 text-status-success-text" />;
    if (status === 'FAIL') return <AlertCircle className="w-5 h-5 text-status-critical-text" />;
    return <Shield className="w-5 h-5 text-neutral-500" />;
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner h-12 w-12"></div>
      </div>
    );
  }
  
  if (!audit) {
    return (
      <div className="text-center py-12">
        <p className="text-neutral-600">Audit not found</p>
      </div>
    );
  }
  
  const failedFindings = findings.filter(f => f.status === 'FAIL');
  const passedFindings = findings.filter(f => f.status === 'PASS');
  
  return (
    <div className="space-y-6 page-enter">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <BackButton to="/configurations" label="Configurations" />
          </div>
          <h1 className="text-3xl font-bold text-neutral-900 mb-1">Audit Results</h1>
          <p className="text-neutral-600">
            {audit.configuration?.filename} ({audit.configuration?.vendor})
          </p>
        </div>
        
        {/* Download Report Button */}
        <button
          onClick={handleDownloadReport}
          disabled={downloadingReport}
          className="flex items-center space-x-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-700 disabled:bg-neutral-300 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-all duration-200 shadow-sm hover:shadow-md group"
        >
          <Download className={`w-5 h-5 ${downloadingReport ? 'animate-bounce' : 'group-hover:translate-y-0.5 transition-transform duration-200'}`} />
          <span>{downloadingReport ? 'Generating...' : 'Download Report'}</span>
        </button>
      </div>

      {/* Human Intervention Alert - GLASS EFFECT */}
      {audit.requires_human_review && (
        <div className="elevated-glass border-2 border-status-medium-border/60 bg-status-medium-bg/70 p-6">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-white/90 backdrop-blur-sm rounded-xl border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
              <AlertTriangle className="w-8 h-8 text-status-medium-text flex-shrink-0" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-status-medium-text mb-2">
                Human Review Required
              </h3>
              <p className="text-neutral-800 mb-4 leading-relaxed">
                {audit.review_reason || 'This configuration requires manual validation due to parsing uncertainties.'}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {audit.interpretation_confidence !== undefined && (
                  <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
                    <p className="text-xs text-neutral-600 mb-1 font-medium">Interpretation Confidence</p>
                    <p className="text-2xl font-bold text-status-medium-text">
                      {(audit.interpretation_confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
                {audit.uninterpreted_lines !== undefined && audit.total_lines !== undefined && (
                  <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
                    <p className="text-xs text-neutral-600 mb-1 font-medium">Uninterpreted Lines</p>
                    <p className="text-2xl font-bold text-status-medium-text">
                      {audit.uninterpreted_lines} / {audit.total_lines}
                    </p>
                  </div>
                )}
                {audit.pending_mappings !== undefined && audit.pending_mappings > 0 && (
                  <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
                    <p className="text-xs text-neutral-600 mb-1 font-medium">Pending AI Mappings</p>
                    <p className="text-2xl font-bold text-status-medium-text">
                      {audit.pending_mappings}
                    </p>
                  </div>
                )}
                <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
                  <p className="text-xs text-neutral-600 mb-1 font-medium">Action Required</p>
                  <Link 
                    to="/learning" 
                    className="text-sm font-semibold text-brand-600 hover:text-brand-700"
                  >
                    Review Mappings →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <p className="text-neutral-600 text-sm font-medium mb-1">Compliance Score</p>
          <p className="text-4xl font-bold text-brand-600">{audit.compliance_score?.toFixed(0)}%</p>
        </div>
        <div className="card">
          <p className="text-neutral-600 text-sm font-medium mb-1">Risk Level</p>
          <p className={`text-3xl font-bold ${
            audit.risk_level === 'HIGH' || audit.risk_level === 'CRITICAL' 
              ? 'text-status-critical-text' 
              : 'text-status-medium-text'
          }`}>
            {audit.risk_level}
          </p>
        </div>
        <div className="card">
          <p className="text-neutral-600 text-sm font-medium mb-1">Failed Controls</p>
          <p className="text-4xl font-bold text-status-critical-text">{audit.failed_count}</p>
        </div>
        <div className="card">
          <p className="text-neutral-600 text-sm font-medium mb-1">Passed Controls</p>
          <p className="text-4xl font-bold text-status-success-text">{audit.passed_count}</p>
        </div>
      </div>
      
      {/* Failed Findings */}
      {failedFindings.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-6 flex items-center space-x-2 text-neutral-900">
            <AlertCircle className="w-6 h-6 text-status-critical-text" />
            <span>Violations ({failedFindings.length})</span>
          </h2>
          
          <div className="space-y-3">
            {failedFindings.map((finding, index) => (
              <div 
                key={finding.finding_id} 
                className="border-2 border-neutral-200 rounded-xl overflow-hidden hover:border-neutral-300 transition-all duration-200 stagger-item"
                style={{ animationDelay: `${index * 30}ms` }}
              >
                <div 
                  className="p-4 cursor-pointer hover:bg-surface-secondary transition-colors duration-200"
                  onClick={() => setExpandedFinding(
                    expandedFinding === finding.finding_id ? null : finding.finding_id
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      {getStatusIcon(finding.status)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2 flex-wrap gap-y-1">
                          <span className="font-semibold text-neutral-900">{finding.title}</span>
                          <span className={`badge ${getSeverityColor(finding.severity)} transition-all duration-150`}>
                            {finding.severity}
                          </span>
                          <span className="badge bg-neutral-100 text-neutral-700 border-neutral-300 transition-all duration-150">
                            {finding.rule_id}
                          </span>
                        </div>
                        <p className="text-sm text-neutral-700">
                          Expected: <span className="font-semibold text-status-success-text">{finding.expected}</span>
                          {' | '}
                          Actual: <span className="font-semibold text-status-critical-text">{finding.actual}</span>
                        </p>
                      </div>
                    </div>
                    <div className={`transition-transform duration-200 ${expandedFinding === finding.finding_id ? 'rotate-180' : ''}`}>
                      <ChevronDown className="w-5 h-5 text-neutral-500 flex-shrink-0" />
                    </div>
                  </div>
                </div>
                
                {expandedFinding === finding.finding_id && (
                  <div className="border-t-2 border-neutral-200 p-5 bg-surface-secondary space-y-4 animate-[fadeIn_200ms_var(--ease-out)]">
                    {/* Evidence */}
                    {finding.evidence && (
                      <div>
                        <p className="text-sm font-semibold text-neutral-900 mb-2">Evidence:</p>
                        <div className="bg-white border-2 border-neutral-200 rounded-lg p-4">
                          <p className="text-xs text-neutral-600 mb-2 font-medium">
                            {finding.evidence.file} • Line {finding.evidence.line}
                          </p>
                          <code className="text-sm text-brand-700 font-mono">{finding.evidence.text}</code>
                        </div>
                      </div>
                    )}
                    
                    {/* Description */}
                    {finding.description && (
                      <div>
                        <p className="text-sm font-semibold text-neutral-900 mb-2">Explanation:</p>
                        <p className="text-sm text-neutral-700 leading-relaxed">{finding.description}</p>
                      </div>
                    )}
                    
                    {/* Remediation */}
                    {finding.remediation && (
                      <div>
                        <p className="text-sm font-semibold text-neutral-900 mb-2">Recommended Fix:</p>
                        <div className="bg-status-success-bg border-2 border-status-success-border rounded-lg p-4">
                          <pre className="text-sm text-status-success-text whitespace-pre-wrap font-mono">
                            {finding.remediation}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Passed Findings Summary */}
      {passedFindings.length > 0 && (
        <div className="card border-2 border-status-success-border bg-status-success-bg">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-status-success-text" />
            <div>
              <h3 className="text-lg font-bold text-status-success-text">
                {passedFindings.length} Controls Passed
              </h3>
              <p className="text-sm text-neutral-700 mt-0.5">These security controls are properly configured</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditResults;
