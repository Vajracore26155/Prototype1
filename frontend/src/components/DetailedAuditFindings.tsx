import React, { useState, useEffect } from 'react';
import {
  Shield, AlertTriangle, AlertCircle, CheckCircle, XCircle, Clock,
  Eye, Code, BookOpen, TrendingUp, Target, Zap, Filter,
  ChevronDown, ChevronRight, ExternalLink, Copy, Search
} from 'lucide-react';

interface DetailedFinding {
  finding_id: string;
  rule_id: string;
  rule_name: string;
  description: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'FAIL' | 'PASS' | 'WARNING' | 'UNKNOWN';
  technical_details: {
    expected: string;
    actual: string;
    field_path: string;
    risk_score: number;
  };
  evidence: {
    evidence_file: string;
    evidence_line: number;
    evidence_text: string;
    configuration_context: string[];
  };
  remediation: {
    guidance: string;
    priority: number;
    estimated_effort: string;
    business_impact: string;
  };
  compliance_mapping: {
    frameworks: string[];
    standards: string[];
  };
  created_at: string;
}

interface AuditAnalysis {
  total_findings: number;
  severity_breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  status_breakdown: {
    pass: number;
    fail: number;
    warning: number;
    unknown: number;
  };
  compliance_frameworks: Array<{
    framework: string;
    total_controls: number;
    passed_controls: number;
    failed_controls: number;
    compliance_percentage: number;
  }>;
  risk_categories: Array<{
    category: string;
    total_findings: number;
    critical_findings: number;
    avg_risk_score: number;
  }>;
}

const DetailedAuditFindings: React.FC<{ auditId: string }> = ({ auditId }) => {
  const [findings, setFindings] = useState<DetailedFinding[]>([]);
  const [analysis, setAnalysis] = useState<AuditAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [frameworkFilter, setFrameworkFilter] = useState('all');
  const [expandedFindings, setExpandedFindings] = useState<Set<string>>(new Set());
  const [showRemediationOnly, setShowRemediationOnly] = useState(false);

  useEffect(() => {
    loadAuditFindings();
  }, [auditId]);

  const loadAuditFindings = async () => {
    setLoading(true);
    try {
      const { getVendorAudits, getVendorAuditEnhanced } = await import('../services/vendorApi');
      const auditsResp: any = await getVendorAudits();
      const audits: any[] = auditsResp?.data?.audits || [];
      if (!audits || audits.length === 0) {
        setFindings([]);
        setAnalysis({
          total_findings: 0,
          severity_breakdown: { critical: 0, high: 0, medium: 0, low: 0 },
          status_breakdown: { pass: 0, fail: 0, warning: 0, unknown: 0 },
          compliance_frameworks: [],
          risk_categories: [],
        });
        return;
      }
      // If a specific (non-dummy) auditId is given, prioritize it; otherwise aggregate across recent audits
      const isDummy = !auditId || auditId === 'AUD-001234';
      const targetAudits = isDummy ? audits.slice(0, 6) : audits.filter((a: any) => a.audit_id === auditId);
      const listToLoad = targetAudits.length > 0 ? targetAudits : audits.slice(0, 6);

      const allDetails: DetailedFinding[] = [];
      for (const a of listToLoad) {
        try {
          const enh: any = await getVendorAuditEnhanced(a.audit_id);
          const details: any[] = enh?.data?.findings?.details || [];
          for (const f of details) {
            allDetails.push({
              finding_id: f.finding_id,
              rule_id: f.rule_id,
              rule_name: f.rule_name || 'Finding',
              description: f.description || '',
              severity: (f.severity || 'LOW') as DetailedFinding['severity'],
              status: (f.status || 'UNKNOWN') as DetailedFinding['status'],
              technical_details: {
                expected: String(f.technical_details?.expected ?? ''),
                actual: String(f.technical_details?.actual ?? ''),
                field_path: String(f.technical_details?.field_path ?? ''),
                risk_score: Number(f.technical_details?.risk_score ?? 0),
              },
              evidence: {
                evidence_file: String(f.evidence?.evidence_file ?? ''),
                evidence_line: Number(f.evidence?.evidence_line ?? 0),
                evidence_text: String(f.evidence?.evidence_text ?? ''),
                configuration_context: Array.isArray(f.evidence?.configuration_context) ? f.evidence.configuration_context.map(String) : [],
              },
              remediation: {
                guidance: String(f.remediation?.guidance ?? ''),
                priority: Number(f.remediation?.priority ?? 3),
                estimated_effort: String(f.remediation?.estimated_effort ?? ''),
                business_impact: String(f.remediation?.business_impact ?? ''),
              },
              compliance_mapping: {
                frameworks: Array.isArray(f.compliance_mapping?.frameworks) ? f.compliance_mapping.frameworks.map(String) : [],
                standards: Array.isArray(f.compliance_mapping?.standards) ? f.compliance_mapping.standards.map(String) : [],
              },
              created_at: String(f.created_at || new Date().toISOString()),
            });
          }
        } catch (e) {
          console.warn('Failed to load audit', a.audit_id, e);
        }
      }

      // Build real analysis from aggregated findings
      const bySev = { critical: 0, high: 0, medium: 0, low: 0 };
      const byStatus = { pass: 0, fail: 0, warning: 0, unknown: 0 };
      const fwMap = new Map<string, { total: number; pass: number; fail: number }>();
      const catMap = new Map<string, { total: number; critical: number; riskSum: number; riskN: number }>();
      const catFor = (ruleId: string) => {
        const r = (ruleId || '').toUpperCase();
        if (r.includes('SSH') || r.includes('TELNET') || r.startsWith('NET-')) return 'Network Security';
        if (r.includes('AUTH') || r.includes('USER') || r.includes('ACCESS')) return 'Access Control';
        if (r.includes('ENCRYPT') || r.includes('CRYPTO')) return 'Data Protection';
        if (r.includes('LOG') || r.includes('AUDIT')) return 'Logging';
        if (r.includes('PASS') || r.includes('PWD')) return 'Authentication';
        return 'Other';
      };
      for (const f of allDetails) {
        const s = (f.severity || '').toLowerCase();
        if (s === 'critical') bySev.critical++;
        else if (s === 'high') bySev.high++;
        else if (s === 'medium') bySev.medium++;
        else bySev.low++;
        const st = (f.status || '').toLowerCase();
        if (st === 'pass') byStatus.pass++;
        else if (st === 'fail') byStatus.fail++;
        else if (st === 'warning') byStatus.warning++;
        else byStatus.unknown++;
        const fws = f.compliance_mapping.frameworks.length > 0 ? f.compliance_mapping.frameworks : ['General'];
        for (const fw of fws) {
          const e = fwMap.get(fw) || { total: 0, pass: 0, fail: 0 };
          e.total++;
          if (f.status === 'PASS') e.pass++;
          if (f.status === 'FAIL') e.fail++;
          fwMap.set(fw, e);
        }
        const cat = catFor(f.rule_id);
        const c = catMap.get(cat) || { total: 0, critical: 0, riskSum: 0, riskN: 0 };
        c.total++;
        if (f.severity === 'CRITICAL' && f.status === 'FAIL') c.critical++;
        if (f.technical_details.risk_score) { c.riskSum += f.technical_details.risk_score; c.riskN++; }
        catMap.set(cat, c);
      }
      setFindings(allDetails);
      setAnalysis({
        total_findings: allDetails.length,
        severity_breakdown: bySev,
        status_breakdown: byStatus,
        compliance_frameworks: Array.from(fwMap.entries()).slice(0, 6).map(([framework, v]) => ({
          framework,
          total_controls: v.total,
          passed_controls: v.pass,
          failed_controls: v.fail,
          compliance_percentage: v.total > 0 ? (v.pass / v.total) * 100 : 0,
        })),
        risk_categories: Array.from(catMap.entries()).map(([category, v]) => ({
          category,
          total_findings: v.total,
          critical_findings: v.critical,
          avg_risk_score: v.riskN > 0 ? v.riskSum / v.riskN : 0,
        })),
      });
    } catch (error) {
      console.error('Failed to load audit findings:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredFindings = findings.filter(finding => {
    const matchesSearch = 
      finding.rule_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      finding.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      finding.finding_id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSeverity = severityFilter === 'all' || finding.severity.toLowerCase() === severityFilter.toLowerCase();
    const matchesStatus = statusFilter === 'all' || finding.status.toLowerCase() === statusFilter.toLowerCase();
    const matchesFramework = frameworkFilter === 'all' || finding.compliance_mapping.frameworks.some(f => f.toLowerCase().includes(frameworkFilter.toLowerCase()));
    const matchesRemediation = !showRemediationOnly || finding.status === 'FAIL';

    return matchesSearch && matchesSeverity && matchesStatus && matchesFramework && matchesRemediation;
  });

  const toggleFindingExpansion = (findingId: string) => {
    const newExpanded = new Set(expandedFindings);
    if (newExpanded.has(findingId)) {
      newExpanded.delete(findingId);
    } else {
      newExpanded.add(findingId);
    }
    setExpandedFindings(newExpanded);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'bg-ink-950 text-white border-ink-950';
      case 'HIGH': return 'bg-ink-950 text-white border-ink-950';
      case 'MEDIUM': return 'bg-mist-200 text-ink-950 border-line';
      case 'LOW': return 'bg-white text-ink-900 border-line';
      default: return 'bg-mist-100 text-ink-500 border-line';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <AlertTriangle className="w-4 h-4 text-ink-950" />;
      case 'HIGH': return <AlertCircle className="w-4 h-4 text-ink-950" />;
      case 'MEDIUM': return <Clock className="w-4 h-4 text-ink-500" />;
      case 'LOW': return <CheckCircle className="w-4 h-4 text-ink-950" />;
      default: return <XCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'FAIL': return 'bg-ink-950 text-white';
      case 'PASS': return 'bg-mist-200 text-ink-950';
      case 'WARNING': return 'bg-white text-ink-900 border border-line';
      default: return 'bg-mist-100 text-ink-500';
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ink-950"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Analysis Summary */}
      {analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Severity Overview */}
          <div className="tatva-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Shield className="w-5 h-5 mr-2" />
              Severity Breakdown
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-ink-950" />
                  <span className="text-sm">Critical</span>
                </div>
                <span className="font-bold text-ink-950">{analysis.severity_breakdown.critical}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 text-ink-950" />
                  <span className="text-sm">High</span>
                </div>
                <span className="font-bold text-ink-950">{analysis.severity_breakdown.high}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-ink-500" />
                  <span className="text-sm">Medium</span>
                </div>
                <span className="font-bold text-ink-500">{analysis.severity_breakdown.medium}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-ink-950" />
                  <span className="text-sm">Low</span>
                </div>
                <span className="font-bold text-ink-950">{analysis.severity_breakdown.low}</span>
              </div>
            </div>
          </div>

          {/* Compliance Frameworks */}
          <div className="tatva-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2" />
              Compliance Status
            </h3>
            <div className="space-y-4">
              {analysis.compliance_frameworks.map((framework, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">{framework.framework}</span>
                    <span className="text-sm font-bold">{framework.compliance_percentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-mist-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-ink-950"
                      style={{ width: `${framework.compliance_percentage}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>{framework.passed_controls} passed</span>
                    <span>{framework.failed_controls} failed</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Categories */}
          <div className="tatva-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Risk Categories
            </h3>
            <div className="space-y-3">
              {analysis.risk_categories.map((category, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div>
                    <div className="text-sm font-medium">{category.category}</div>
                    <div className="text-xs text-gray-500">
                      {category.critical_findings} critical of {category.total_findings} total
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">
                      {category.avg_risk_score.toFixed(1)}
                    </div>
                    <div className="text-xs text-gray-500">Risk Score</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Filters and Controls */}
      <div className="tatva-card p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search findings..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 w-full lg:w-64"
              />
            </div>

            {/* Filters */}
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Severity</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Status</option>
              <option value="fail">Failed</option>
              <option value="pass">Passed</option>
              <option value="warning">Warning</option>
            </select>

            <select
              value={frameworkFilter}
              onChange={(e) => setFrameworkFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Frameworks</option>
              <option value="nist">NIST</option>
              <option value="iso">ISO 27001</option>
              <option value="pci">PCI DSS</option>
            </select>
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={showRemediationOnly}
                onChange={(e) => setShowRemediationOnly(e.target.checked)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm">Show only items needing remediation</span>
            </label>
            
            <div className="text-sm text-gray-500">
              {filteredFindings.length} of {findings.length} findings
            </div>
          </div>
        </div>
      </div>
      {/* Findings List */}
      <div className="space-y-4">
        {filteredFindings.length === 0 ? (
          <div className="bg-white rounded-lg border p-12 text-center">
            <Shield className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Findings Found</h3>
            <p className="text-gray-500">
              {searchTerm || severityFilter !== 'all' || statusFilter !== 'all' || frameworkFilter !== 'all'
                ? 'Try adjusting your search criteria or filters'
                : 'No security findings to display'
              }
            </p>
          </div>
        ) : (
          filteredFindings.map((finding) => (
            <div key={finding.finding_id} className="tatva-card">
              {/* Main Finding Row */}
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {/* Header */}
                    <div className="flex items-center space-x-3 mb-4">
                      <button
                        onClick={() => toggleFindingExpansion(finding.finding_id)}
                        className="flex items-center space-x-2 text-left"
                      >
                        {expandedFindings.has(finding.finding_id) 
                          ? <ChevronDown className="w-4 h-4 text-gray-400" />
                          : <ChevronRight className="w-4 h-4 text-gray-400" />
                        }
                        {getSeverityIcon(finding.severity)}
                        <h3 className="text-lg font-semibold text-gray-900">
                          {finding.rule_name}
                        </h3>
                      </button>
                      
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(finding.severity)}`}>
                          {finding.severity}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(finding.status)}`}>
                          {finding.status}
                        </span>
                      </div>
                    </div>

                    {/* Finding Details */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
                      <div>
                        <span className="text-sm text-gray-500">Finding ID:</span>
                        <div className="font-mono text-sm">{finding.finding_id}</div>
                        <span className="text-sm text-gray-500">Rule ID:</span>
                        <div className="font-mono text-sm">{finding.rule_id}</div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-500">Risk Score:</span>
                        <div className="text-lg font-bold text-ink-950">{finding.technical_details.risk_score.toFixed(1)}</div>
                        <span className="text-sm text-gray-500">Field Path:</span>
                        <div className="font-mono text-xs">{finding.technical_details.field_path}</div>
                      </div>
                      <div>
                        <span className="text-sm font-bold text-ink-500">Priority:</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 rounded-full bg-ink-950" />
                          <span className="text-sm font-bold text-ink-900">Priority {finding.remediation.priority}</span>
                        </div>
                        <span className="text-sm font-bold text-ink-500">Effort:</span>
                        <div className="text-sm font-bold text-ink-900">{finding.remediation.estimated_effort}</div>
                      </div>
                    </div>

                    {/* Description */}
                    <div className="mb-4">
                      <p className="font-medium text-ink-900">{finding.description}</p>
                    </div>

                    {/* Compliance Frameworks */}
                    <div className="flex flex-wrap gap-2">
                      {finding.compliance_mapping.frameworks.map((framework, index) => (
                        <span key={index} className="px-2 py-1 bg-mist-100 border border-line text-ink-900 text-xs rounded font-bold">
                          {framework}
                        </span>
                      ))}
                      {finding.compliance_mapping.standards.map((standard, index) => (
                        <span key={index} className="px-2 py-1 bg-white border border-line text-ink-500 text-xs rounded font-bold">
                          {standard}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col space-y-2 ml-6">
                    <button
                      onClick={() => toggleFindingExpansion(finding.finding_id)}
                      className="flex items-center space-x-2 px-4 py-2 bg-ink-950 text-white rounded-xl hover:bg-black transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      <span>Details</span>
                    </button>
                    
                    <button
                      onClick={() => copyToClipboard(finding.finding_id)}
                      className="flex items-center space-x-2 px-4 py-2 bg-mist-200 text-ink-950 rounded-xl hover:bg-mist-100 transition-colors"
                    >
                      <Copy className="w-4 h-4" />
                      <span>Copy ID</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedFindings.has(finding.finding_id) && (
                <div className="border-t border-gray-200 bg-gray-50 p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Technical Details */}
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Code className="w-4 h-4 mr-2" />
                        Technical Details
                      </h5>
                      <div className="space-y-4">
                        <div>
                          <span className="text-sm text-gray-500">Expected Value:</span>
                          <div className="font-mono text-sm bg-green-50 border border-green-200 rounded p-2 mt-1">
                            {finding.technical_details.expected}
                          </div>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">Actual Value:</span>
                          <div className="font-mono text-sm bg-red-50 border border-red-200 rounded p-2 mt-1">
                            {finding.technical_details.actual}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Evidence */}
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <BookOpen className="w-4 h-4 mr-2" />
                        Evidence & Context
                      </h5>
                      <div className="space-y-3">
                        <div>
                          <span className="text-sm text-gray-500">Source File:</span>
                          <div className="font-mono text-sm">{finding.evidence.evidence_file}</div>
                          <span className="text-sm text-gray-500">Line {finding.evidence.evidence_line}</span>
                        </div>
                        
                        <div>
                          <span className="text-sm text-gray-500">Configuration Context:</span>
                          <div className="font-mono text-xs bg-gray-100 border rounded p-3 mt-1 overflow-x-auto">
                            {finding.evidence.configuration_context.map((line, index) => (
                              <div key={index} className={
                                line.includes(`line ${finding.evidence.evidence_line}:`) 
                                  ? 'bg-yellow-200 text-yellow-900 px-1 rounded' 
                                  : ''
                              }>
                                {line}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Remediation Guidance */}
                    <div className="lg:col-span-2">
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Zap className="w-4 h-4 mr-2" />
                        Remediation Guidance
                      </h5>
                      <div className="space-y-4">
                        <div className="bg-white rounded-lg border p-4">
                          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
                            <div>
                              <span className="text-sm text-gray-500">Remediation Priority:</span>
                              <div className="flex items-center space-x-2 mt-1">
                                <div className={`w-3 h-3 rounded-full ${
                                  finding.remediation.priority <= 1 ? 'bg-red-500' :
                                  finding.remediation.priority <= 2 ? 'bg-orange-500' :
                                  finding.remediation.priority <= 3 ? 'bg-yellow-500' : 'bg-green-500'
                                }`} />
                                <span className="font-medium">Priority {finding.remediation.priority}</span>
                              </div>
                            </div>
                            <div>
                              <span className="text-sm text-gray-500">Estimated Effort:</span>
                              <div className="font-medium mt-1">{finding.remediation.estimated_effort}</div>
                            </div>
                            <div>
                              <span className="text-sm text-gray-500">Business Impact:</span>
                              <div className="text-sm mt-1">{finding.remediation.business_impact}</div>
                            </div>
                          </div>
                          
                          <div>
                            <span className="text-sm text-gray-500">Remediation Steps:</span>
                            <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded">
                              <p className="text-sm text-blue-900">{finding.remediation.guidance}</p>
                            </div>
                          </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="flex flex-wrap gap-2">
                          <button className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                            <ExternalLink className="w-3 h-3" />
                            <span>View Documentation</span>
                          </button>
                          <button className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                            <Target className="w-3 h-3" />
                            <span>Mark as Remediated</span>
                          </button>
                          <button className="flex items-center space-x-2 px-3 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700">
                            <Copy className="w-3 h-3" />
                            <span>Copy Config Command</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DetailedAuditFindings;