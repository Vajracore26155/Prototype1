import React, { useState, useEffect } from 'react';
import {
  FileText, Eye, Download, Search, Filter, Grid, List, MoreVertical,
  Clock, Shield, AlertTriangle, CheckCircle, XCircle, Upload,
  ChevronDown, ChevronRight, Hash, Activity, Zap, Target,
  Calendar, User, Database, Lock, Unlock
} from 'lucide-react';

interface DetailedConfiguration {
  config_id: string;
  filename: string;
  file_type: string;
  status: string;
  vendor: string;
  vendor_confidence: number;
  created_at: string;
  file_size?: number;
  file_integrity: {
    sha256_hash: string;
    storage_path: string | null;
    sanitized_path: string | null;
  };
  processing_status: {
    ingested: boolean;
    vendor_detected: boolean;
    audited: boolean;
    latest_audit: any;
  };
  file_stats: {
    total_lines: number;
    preview_lines: number;
    file_size_bytes: number;
  };
  upload_metadata: {
    uploaded_by: string;
    uploaded_at: string;
    organization_id: number;
  };
  audit_summary?: {
    compliance_score: number;
    risk_level: string;
    critical_findings: number;
    high_findings: number;
    medium_findings: number;
    low_findings: number;
    processing_time?: number;
  };
}

const DetailedConfigurationManager: React.FC = () => {
  const [configurations, setConfigurations] = useState<DetailedConfiguration[]>([]);
  const [filteredConfigs, setFilteredConfigs] = useState<DetailedConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [vendorFilter, setVendorFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'detailed'>('detailed');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [expandedConfigs, setExpandedConfigs] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadConfigurations();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [configurations, searchTerm, statusFilter, vendorFilter, riskFilter, sortBy, sortOrder]);

  const loadConfigurations = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call to get detailed configurations
      await simulateConfigurationLoad();
    } catch (error) {
      console.error('Failed to load configurations:', error);
    } finally {
      setLoading(false);
    }
  };

  // Simulate loading detailed configuration data
  const simulateConfigurationLoad = async () => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const sampleConfigs: DetailedConfiguration[] = [
      {
        config_id: 'CFG-001234',
        filename: 'cisco_router_main.txt',
        file_type: 'text/plain',
        status: 'COMPLETED',
        vendor: 'Cisco',
        vendor_confidence: 0.95,
        created_at: '2024-01-15T10:30:00Z',
        file_size: 45678,
        file_integrity: {
          sha256_hash: 'abc123def456...',
          storage_path: '/uploads/cisco_router_main.txt',
          sanitized_path: '/sanitized/cisco_router_main_clean.txt'
        },
        processing_status: {
          ingested: true,
          vendor_detected: true,
          audited: true,
          latest_audit: { audit_id: 'AUD-001234' }
        },
        file_stats: {
          total_lines: 1247,
          preview_lines: 50,
          file_size_bytes: 45678
        },
        upload_metadata: {
          uploaded_by: 'VND-000123',
          uploaded_at: '2024-01-15T10:30:00Z',
          organization_id: 1
        },
        audit_summary: {
          compliance_score: 78.5,
          risk_level: 'MEDIUM',
          critical_findings: 2,
          high_findings: 5,
          medium_findings: 12,
          low_findings: 23,
          processing_time: 4.2
        }
      },
      // Add more sample configurations...
    ];

    setConfigurations(sampleConfigs);
  };

  const applyFilters = () => {
    let filtered = [...configurations];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(config =>
        config.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        config.config_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        config.vendor.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(config => config.status.toLowerCase() === statusFilter.toLowerCase());
    }

    // Apply vendor filter
    if (vendorFilter !== 'all') {
      filtered = filtered.filter(config => config.vendor.toLowerCase() === vendorFilter.toLowerCase());
    }

    // Apply risk filter
    if (riskFilter !== 'all') {
      filtered = filtered.filter(config => 
        config.audit_summary?.risk_level.toLowerCase() === riskFilter.toLowerCase()
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aVal, bVal;
      
      switch (sortBy) {
        case 'filename':
          aVal = a.filename;
          bVal = b.filename;
          break;
        case 'compliance_score':
          aVal = a.audit_summary?.compliance_score || 0;
          bVal = b.audit_summary?.compliance_score || 0;
          break;
        case 'risk_level':
          const riskOrder = { 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4 };
          aVal = riskOrder[a.audit_summary?.risk_level as keyof typeof riskOrder] || 0;
          bVal = riskOrder[b.audit_summary?.risk_level as keyof typeof riskOrder] || 0;
          break;
        default:
          aVal = new Date(a.created_at).getTime();
          bVal = new Date(b.created_at).getTime();
      }

      if (sortOrder === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
      }
    });

    setFilteredConfigs(filtered);
  };

  const toggleConfigExpansion = (configId: string) => {
    const newExpanded = new Set(expandedConfigs);
    if (newExpanded.has(configId)) {
      newExpanded.delete(configId);
    } else {
      newExpanded.add(configId);
    }
    setExpandedConfigs(newExpanded);
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing': return <Clock className="w-4 h-4 text-blue-500" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />;
      default: return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-yellow-100 text-yellow-800';
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters and Controls */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Search and Filters */}
          <div className="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search configurations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent w-full lg:w-64"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>

            {/* Vendor Filter */}
            <select
              value={vendorFilter}
              onChange={(e) => setVendorFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Vendors</option>
              <option value="cisco">Cisco</option>
              <option value="juniper">Juniper</option>
              <option value="fortinet">Fortinet</option>
            </select>

            {/* Risk Filter */}
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Risk Levels</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          {/* View Controls */}
          <div className="flex items-center space-x-4">
            {/* Sort Controls */}
            <div className="flex items-center space-x-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
              >
                <option value="created_at">Date</option>
                <option value="filename">Name</option>
                <option value="compliance_score">Compliance</option>
                <option value="risk_level">Risk Level</option>
              </select>
              
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-1 border border-gray-300 rounded-lg">
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-l-lg ${viewMode === 'list' ? 'bg-indigo-100 text-indigo-600' : 'hover:bg-gray-50'}`}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-indigo-100 text-indigo-600' : 'hover:bg-gray-50'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('detailed')}
                className={`p-2 rounded-r-lg ${viewMode === 'detailed' ? 'bg-indigo-100 text-indigo-600' : 'hover:bg-gray-50'}`}
              >
                <Eye className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
      {/* Results Summary */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {filteredConfigs.length} of {configurations.length} configurations
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <span>Completed: {filteredConfigs.filter(c => c.status === 'COMPLETED').length}</span>
            <span>Processing: {filteredConfigs.filter(c => c.status === 'PROCESSING').length}</span>
            <span>Failed: {filteredConfigs.filter(c => c.status === 'FAILED').length}</span>
          </div>
        </div>
      </div>

      {/* Configuration List/Grid */}
      <div className="space-y-4">
        {filteredConfigs.length === 0 ? (
          <div className="bg-white rounded-lg border p-12 text-center">
            <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Configurations Found</h3>
            <p className="text-gray-500 mb-6">
              {searchTerm || statusFilter !== 'all' || vendorFilter !== 'all' || riskFilter !== 'all'
                ? 'Try adjusting your search criteria or filters'
                : 'Upload your first configuration to get started'
              }
            </p>
            <button className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
              <Upload className="w-4 h-4 inline mr-2" />
              Upload Configuration
            </button>
          </div>
        ) : (
          filteredConfigs.map((config) => (
            <div key={config.config_id} className="bg-white rounded-lg border hover:shadow-lg transition-shadow">
              {/* Main Configuration Row */}
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {/* Header */}
                    <div className="flex items-center space-x-3 mb-4">
                      <button
                        onClick={() => toggleConfigExpansion(config.config_id)}
                        className="flex items-center space-x-2 text-left"
                      >
                        {expandedConfigs.has(config.config_id) 
                          ? <ChevronDown className="w-4 h-4 text-gray-400" />
                          : <ChevronRight className="w-4 h-4 text-gray-400" />
                        }
                        <FileText className="w-5 h-5 text-indigo-600" />
                        <h3 className="text-lg font-semibold text-gray-900 truncate">
                          {config.filename}
                        </h3>
                      </button>
                      
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(config.status)}
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(config.status)}`}>
                          {config.status}
                        </span>
                      </div>
                    </div>

                    {/* Configuration ID and Basic Info */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                      <div>
                        <span className="text-gray-500">Config ID:</span>
                        <div className="font-mono text-indigo-600">{config.config_id}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Vendor:</span>
                        <div className="font-medium">{config.vendor}</div>
                        <div className="text-xs text-gray-400">
                          {(config.vendor_confidence * 100).toFixed(1)}% confidence
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-500">File Size:</span>
                        <div>{(config.file_stats.file_size_bytes / 1024).toFixed(1)} KB</div>
                        <div className="text-xs text-gray-400">
                          {config.file_stats.total_lines.toLocaleString()} lines
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-500">Uploaded:</span>
                        <div>{new Date(config.created_at).toLocaleDateString()}</div>
                        <div className="text-xs text-gray-400">
                          {new Date(config.created_at).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>

                    {/* Audit Summary */}
                    {config.audit_summary && (
                      <div className="bg-gray-50 rounded-lg p-4 mb-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium text-gray-900">Security Audit Results</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium border ${getRiskLevelColor(config.audit_summary.risk_level)}`}>
                            {config.audit_summary.risk_level} RISK
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {config.audit_summary.compliance_score.toFixed(1)}%
                            </div>
                            <div className="text-gray-500">Compliance</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-red-600">
                              {config.audit_summary.critical_findings}
                            </div>
                            <div className="text-gray-500">Critical</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-orange-600">
                              {config.audit_summary.high_findings}
                            </div>
                            <div className="text-gray-500">High</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-yellow-600">
                              {config.audit_summary.medium_findings}
                            </div>
                            <div className="text-gray-500">Medium</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-green-600">
                              {config.audit_summary.low_findings}
                            </div>
                            <div className="text-gray-500">Low</div>
                          </div>
                        </div>

                        {config.audit_summary.processing_time && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <div className="flex items-center text-sm text-gray-500">
                              <Clock className="w-4 h-4 mr-2" />
                              Processing completed in {config.audit_summary.processing_time.toFixed(1)} minutes
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col space-y-2 ml-6">
                    <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      <Eye className="w-4 h-4" />
                      <span>View Details</span>
                    </button>
                    
                    {config.audit_summary && (
                      <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                        <Download className="w-4 h-4" />
                        <span>Download Report</span>
                      </button>
                    )}

                    <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedConfigs.has(config.config_id) && (
                <div className="border-t border-gray-200 bg-gray-50 p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* File Information */}
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Database className="w-4 h-4 mr-2" />
                        File Information
                      </h5>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-500">File Type:</span>
                          <span className="font-mono">{config.file_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">SHA256 Hash:</span>
                          <span className="font-mono text-xs">{config.file_integrity.sha256_hash.substring(0, 16)}...</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Storage Status:</span>
                          <div className="flex items-center space-x-2">
                            {config.processing_status.ingested 
                              ? <Lock className="w-3 h-3 text-green-500" />
                              : <Unlock className="w-3 h-3 text-red-500" />
                            }
                            <span>{config.processing_status.ingested ? 'Secured' : 'Pending'}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Processing Status */}
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Activity className="w-4 h-4 mr-2" />
                        Processing Pipeline
                      </h5>
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${config.processing_status.ingested ? 'bg-green-500' : 'bg-gray-300'}`} />
                          <span className="text-sm">File Ingested & Sanitized</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${config.processing_status.vendor_detected ? 'bg-green-500' : 'bg-gray-300'}`} />
                          <span className="text-sm">Vendor Detection Completed</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${config.processing_status.audited ? 'bg-green-500' : 'bg-gray-300'}`} />
                          <span className="text-sm">Security Audit Completed</span>
                        </div>
                      </div>
                    </div>

                    {/* Upload Metadata */}
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <User className="w-4 h-4 mr-2" />
                        Upload Metadata
                      </h5>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Uploaded By:</span>
                          <span className="font-mono">{config.upload_metadata.uploaded_by}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Organization:</span>
                          <span>ID: {config.upload_metadata.organization_id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Upload Time:</span>
                          <span>{new Date(config.upload_metadata.uploaded_at).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Zap className="w-4 h-4 mr-2" />
                        Quick Actions
                      </h5>
                      <div className="space-y-2">
                        <button className="w-full flex items-center justify-between p-2 text-left bg-white rounded border hover:bg-gray-50">
                          <span className="text-sm">View File Content Preview</span>
                          <ChevronRight className="w-4 h-4" />
                        </button>
                        <button className="w-full flex items-center justify-between p-2 text-left bg-white rounded border hover:bg-gray-50">
                          <span className="text-sm">Compare with Previous Version</span>
                          <ChevronRight className="w-4 h-4" />
                        </button>
                        <button className="w-full flex items-center justify-between p-2 text-left bg-white rounded border hover:bg-gray-50">
                          <span className="text-sm">Schedule Re-audit</span>
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Pagination would go here if needed */}
    </div>
  );
};

export default DetailedConfigurationManager;