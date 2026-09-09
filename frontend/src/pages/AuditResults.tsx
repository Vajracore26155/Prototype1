import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Shield, AlertCircle, CheckCircle, ChevronDown, ChevronUp, ArrowLeft, AlertTriangle, Download } from 'lucide-react';
import { getAudit, getFindings, downloadAuditReport } from '../services/api';
import type { Audit, Finding } from '../types';

const AuditResults = () => {
  const { auditId } = useParams<{ auditId: string }>();
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
    try {
      await downloadAuditReport(auditId);
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('Failed to download report. Please try again.');
    } finally {
      setDownloadingReport(false);
    }
  };
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'text-red-400 bg-red-900/30 border-red-800';
      case 'HIGH': return 'text-orange-400 bg-orange-900/30 border-orange-800';
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-900/30 border-yellow-800';
      case 'LOW': return 'text-green-400 bg-green-900/30 border-green-800';
      default: return 'text-gray-400 bg-gray-700 border-gray-600';
    }
  };
  
  const getStatusIcon = (status: string) => {
    if (status === 'PASS') return <CheckCircle className="w-5 h-5 text-green-400" />;
    if (status === 'FAIL') return <AlertCircle className="w-5 h-5 text-red-400" />;
    return <Shield className="w-5 h-5 text-gray-400" />;
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  if (!audit) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Audit not found</p>
      </div>
    );
  }
  
  const failedFindings = findings.filter(f => f.status === 'FAIL');
  const passedFindings = findings.filter(f => f.status === 'PASS');
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/configurations" className="text-gray-400 hover:text-gray-200">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Audit Results</h1>
            <p className="text-gray-400">
              {audit.configuration?.filename} ({audit.configuration?.vendor})
            </p>
          </div>
        </div>
        
        {/* Download Report Button */}
        <button
          onClick={handleDownloadReport}
          disabled={downloadingReport}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
        >
          <Download className={`w-5 h-5 ${downloadingReport ? 'animate-bounce' : ''}`} />
          <span>{downloadingReport ? 'Generating...' : 'Download Report'}</span>
        </button>
      </div>

      {/* Human Intervention Alert */}
      {audit.requires_human_review && (
        <div className="card border-yellow-700 bg-yellow-900/20">
          <div className="flex items-start space-x-4">
            <AlertTriangle className="w-8 h-8 text-yellow-400 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="text-lg font-bold text-yellow-400 mb-2">
                Human Review Required
              </h3>
              <p className="text-gray-300 mb-3">
                {audit.review_reason || 'This configuration requires manual validation due to parsing uncertainties.'}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
                {audit.interpretation_confidence !== undefined && (
                  <div className="bg-gray-800/50 rounded p-3">
                    <p className="text-xs text-gray-400 mb-1">Interpretation Confidence</p>
                    <p className="text-xl font-bold text-yellow-300">
                      {(audit.interpretation_confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
                {audit.uninterpreted_lines !== undefined && audit.total_lines !== undefined && (
                  <div className="bg-gray-800/50 rounded p-3">
                    <p className="text-xs text-gray-400 mb-1">Uninterpreted Lines</p>
                    <p className="text-xl font-bold text-yellow-300">
                      {audit.uninterpreted_lines} / {audit.total_lines}
                    </p>
                  </div>
                )}
                {audit.pending_mappings !== undefined && audit.pending_mappings > 0 && (
                  <div className="bg-gray-800/50 rounded p-3">
                    <p className="text-xs text-gray-400 mb-1">Pending AI Mappings</p>
                    <p className="text-xl font-bold text-yellow-300">
                      {audit.pending_mappings}
                    </p>
                  </div>
                )}
                <div className="bg-gray-800/50 rounded p-3">
                  <p className="text-xs text-gray-400 mb-1">Action Required</p>
                  <Link 
                    to="/learning" 
                    className="text-sm font-semibold text-blue-400 hover:text-blue-300"
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
          <p className="text-gray-400 text-sm mb-1">Compliance Score</p>
          <p className="text-3xl font-bold text-blue-400">{audit.compliance_score?.toFixed(0)}%</p>
        </div>
        <div className="card">
          <p className="text-gray-400 text-sm mb-1">Risk Level</p>
          <p className={`text-2xl font-bold ${audit.risk_level === 'HIGH' || audit.risk_level === 'CRITICAL' ? 'text-red-400' : 'text-yellow-400'}`}>
            {audit.risk_level}
          </p>
        </div>
        <div className="card">
          <p className="text-gray-400 text-sm mb-1">Failed Controls</p>
          <p className="text-3xl font-bold text-red-400">{audit.failed_count}</p>
        </div>
        <div className="card">
          <p className="text-gray-400 text-sm mb-1">Passed Controls</p>
          <p className="text-3xl font-bold text-green-400">{audit.passed_count}</p>
        </div>
      </div>
      
      {/* Failed Findings */}
      {failedFindings.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4 flex items-center space-x-2">
            <AlertCircle className="w-6 h-6 text-red-400" />
            <span>Violations ({failedFindings.length})</span>
          </h2>
          
          <div className="space-y-3">
            {failedFindings.map((finding) => (
              <div key={finding.finding_id} className="border border-gray-700 rounded-lg">
                <div 
                  className="p-4 cursor-pointer hover:bg-gray-700/30"
                  onClick={() => setExpandedFinding(
                    expandedFinding === finding.finding_id ? null : finding.finding_id
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      {getStatusIcon(finding.status)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-semibold">{finding.title}</span>
                          <span className={`badge ${getSeverityColor(finding.severity)}`}>
                            {finding.severity}
                          </span>
                          <span className="badge bg-gray-700 text-gray-300 border border-gray-600">
                            {finding.rule_id}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400">
                          Expected: <span className="text-green-400">{finding.expected}</span>
                          {' | '}
                          Actual: <span className="text-red-400">{finding.actual}</span>
                        </p>
                      </div>
                    </div>
                    {expandedFinding === finding.finding_id ? 
                      <ChevronUp className="w-5 h-5 text-gray-400" /> :
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    }
                  </div>
                </div>
                
                {expandedFinding === finding.finding_id && (
                  <div className="border-t border-gray-700 p-4 bg-gray-800/50 space-y-4">
                    {/* Evidence */}
                    {finding.evidence && (
                      <div>
                        <p className="text-sm font-semibold text-gray-300 mb-2">Evidence:</p>
                        <div className="bg-gray-900 border border-gray-700 rounded p-3">
                          <p className="text-xs text-gray-500 mb-1">
                            {finding.evidence.file} • Line {finding.evidence.line}
                          </p>
                          <code className="text-sm text-blue-300">{finding.evidence.text}</code>
                        </div>
                      </div>
                    )}
                    
                    {/* Description */}
                    {finding.description && (
                      <div>
                        <p className="text-sm font-semibold text-gray-300 mb-2">Explanation:</p>
                        <p className="text-sm text-gray-400">{finding.description}</p>
                      </div>
                    )}
                    
                    {/* Remediation */}
                    {finding.remediation && (
                      <div>
                        <p className="text-sm font-semibold text-gray-300 mb-2">Recommended Fix:</p>
                        <div className="bg-gray-900 border border-green-800 rounded p-3">
                          <pre className="text-sm text-green-300 whitespace-pre-wrap font-mono">
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
        <div className="card border-green-800 bg-green-900/10">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-400" />
            <div>
              <h3 className="text-lg font-bold text-green-400">
                {passedFindings.length} Controls Passed
              </h3>
              <p className="text-sm text-gray-400">These security controls are properly configured</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditResults;
