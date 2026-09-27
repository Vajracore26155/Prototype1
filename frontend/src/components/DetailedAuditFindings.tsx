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
      // TODO: Replace with actual API call
      await simulateAuditFindingsLoad();
    } catch (error) {
      console.error('Failed to load audit findings:', error);
    } finally {
      setLoading(false);
    }
  };

  const simulateAuditFindingsLoad = async () => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Sample findings data
    const sampleFindings: DetailedFinding[] = [
      {
        finding_id: 'FND-001234',
        rule_id: 'NET-SSH-001',
        rule_name: 'SSH Weak Encryption Prevention',
        description: 'SSH service is configured with weak encryption algorithms that are vulnerable to cryptographic attacks.',
        severity: 'CRITICAL',
        status: 'FAIL',
        technical_details: {
          expected: 'aes256-ctr,aes192-ctr,aes128-ctr',
          actual: 'aes128-cbc,3des-cbc',
          field_path: 'remote_access.ssh.encryption_algorithms',
          risk_score: 8.7
        },
        evidence: {
          evidence_file: 'cisco_router_config.txt',
          evidence_line: 247,
          evidence_text: 'ip ssh version 2\nip ssh encryption aes128-cbc 3des-cbc',
          configuration_context: [
            'line 245: !',
            'line 246: ip ssh version 2',
            'line 247: ip ssh encryption aes128-cbc 3des-cbc',
            'line 248: ip ssh authentication-retries 3',
            'line 249: !'
          ]
        },
        remediation: {
          guidance: 'Configure SSH to use only strong encryption algorithms. Remove weak ciphers like 3DES and AES-CBC. Use AES-CTR or ChaCha20 family ciphers.',
          priority: 1,
          estimated_effort: 'Low (15-30 minutes)',
          business_impact: 'High - Prevents potential data interception during SSH sessions'
        },
        compliance_mapping: {
          frameworks: ['NIST', 'ISO 27001', 'PCI DSS'],
          standards: ['SC-8', 'SC-13', 'Req 4.1']
        },
        created_at: '2024-01-15T10:30:00Z'
      },
      // Add more sample findings...
    ];

    // Sample analysis data
    const sampleAnalysis: AuditAnalysis = {
      total_findings: 145,
      severity_breakdown: {
        critical: 8,
        high: 23,
        medium: 45,
        low: 69
      },
      status_breakdown: {
        pass: 1234,
        fail: 89,
        warning: 45,
        unknown: 12
      },
      compliance_frameworks: [
        { framework: 'NIST CSF', total_controls: 156, passed_controls: 134, failed_controls: 22, compliance_percentage: 85.9 },
        { framework: 'ISO 27001', total_controls: 89, passed_controls: 76, failed_controls: 13, compliance_percentage: 85.4 },
        { framework: 'PCI DSS', total_controls: 67, passed_controls: 54, failed_controls: 13, compliance_percentage: 80.6 }
      ],
      risk_categories: [
        { category: 'Network Security', total_findings: 45, critical_findings: 3, avg_risk_score: 6.8 },
        { category: 'Access Control', total_findings: 32, critical_findings: 2, avg_risk_score: 5.9 },
        { category: 'Data Protection', total_findings: 28, critical_findings: 2, avg_risk_score: 6.2 },
        { category: 'Authentication', total_findings: 23, critical_findings: 1, avg_risk_score: 5.5 },
        { category: 'Logging', total_findings: 17, critical_findings: 0, avg_risk_score: 4.3 }
      ]
    };

    setFindings(sampleFindings);
    setAnalysis(sampleAnalysis);
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
      case 'CRITICAL': return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LOW': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'HIGH': return <AlertCircle className="w-4 h-4 text-orange-600" />;
      case 'MEDIUM': return <Clock className="w-4 h-4 text-yellow-600" />;
      case 'LOW': return <CheckCircle className="w-4 h-4 text-green-600" />;
      default: return <XCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'FAIL': return 'bg-red-100 text-red-800';
      case 'PASS': return 'bg-green-100 text-green-800';
      case 'WARNING': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Analysis Summary */}
      {analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Severity Overview */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Shield className="w-5 h-5 mr-2" />
              Severity Breakdown
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span className="text-sm">Critical</span>
                </div>
                <span className="font-bold text-red-600">{analysis.severity_breakdown.critical}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 text-orange-600" />
                  <span className="text-sm">High</span>
                </div>
                <span className="font-bold text-orange-600">{analysis.severity_breakdown.high}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-yellow-600" />
                  <span className="text-sm">Medium</span>
                </div>
                <span className="font-bold text-yellow-600">{analysis.severity_breakdown.medium}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span className="text-sm">Low</span>
                </div>
                <span className="font-bold text-green-600">{analysis.severity_breakdown.low}</span>
              </div>
            </div>
          </div>

          {/* Compliance Frameworks */}
          <div className="bg-white rounded-lg border p-6">
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
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        framework.compliance_percentage >= 90 ? 'bg-green-500' :
                        framework.compliance_percentage >= 75 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
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
          <div className="bg-white rounded-lg border p-6">
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
      <div className="bg-white rounded-lg border p-6">
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
            <div key={finding.finding_id} className="bg-white rounded-lg border hover:shadow-lg transition-shadow">
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
                        <div className="text-lg font-bold text-red-600">{finding.technical_details.risk_score.toFixed(1)}</div>
                        <span className="text-sm text-gray-500">Field Path:</span>
                        <div className="font-mono text-xs">{finding.technical_details.field_path}</div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-500">Priority:</span>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            finding.remediation.priority <= 1 ? 'bg-red-500' :
                            finding.remediation.priority <= 2 ? 'bg-orange-500' :
                            finding.remediation.priority <= 3 ? 'bg-yellow-500' : 'bg-green-500'
                          }`} />
                          <span className="text-sm font-medium">Priority {finding.remediation.priority}</span>
                        </div>
                        <span className="text-sm text-gray-500">Effort:</span>
                        <div className="text-sm">{finding.remediation.estimated_effort}</div>
                      </div>
                    </div>

                    {/* Description */}
                    <div className="mb-4">
                      <p className="text-gray-700">{finding.description}</p>
                    </div>

                    {/* Compliance Frameworks */}
                    <div className="flex flex-wrap gap-2">
                      {finding.compliance_mapping.frameworks.map((framework, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {framework}
                        </span>
                      ))}
                      {finding.compliance_mapping.standards.map((standard, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
                          {standard}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col space-y-2 ml-6">
                    <button
                      onClick={() => toggleFindingExpansion(finding.finding_id)}
                      className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      <span>Details</span>
                    </button>
                    
                    <button
                      onClick={() => copyToClipboard(finding.finding_id)}
                      className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
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