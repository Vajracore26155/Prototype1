import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, FileText, Shield, Eye, AlertCircle, 
  CheckCircle, XCircle, Clock, Upload, RefreshCw, Search,
  Filter, Grid, List, MoreVertical
} from 'lucide-react';
import { 
  isVendorLoggedIn,
  getVendorConfigurations,
  getVendorAudits
} from '../services/vendorApi';

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

export default function VendorConfigurations() {
  const navigate = useNavigate();
  const [configurations, setConfigurations] = useState<VendorConfiguration[]>([]);
  const [audits, setAudits] = useState<VendorAudit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');

  useEffect(() => {
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }

    loadConfigurations();
  }, [navigate]);

  const loadConfigurations = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Load configurations
      const configsResponse = await getVendorConfigurations();
      if (configsResponse.success) {
        setConfigurations(configsResponse.data.configurations || []);
      }

      // Load audits
      const auditsResponse = await getVendorAudits();
      if (auditsResponse.success) {
        setAudits(auditsResponse.data.audits || []);
      }
    } catch (err: any) {
      console.error('Failed to load configurations:', err);
      setError(err.response?.data?.error?.message || 'Failed to load configurations');
    } finally {
      setLoading(false);
    }
  };

  const getAuditForConfig = (configId: string) => {
    return audits.find(a => a.configuration.config_id === configId);
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

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'processing':
      case 'running': return <Clock className="w-4 h-4" />;
      case 'failed': return <XCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const filteredConfigurations = configurations.filter(config => {
    const matchesSearch = config.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.config_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.vendor.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || config.status.toLowerCase() === filterStatus.toLowerCase();
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600">Loading configurations...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
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
                <h1 className="text-2xl font-bold text-gray-900">Configuration Management</h1>
                <p className="text-gray-600">{configurations.length} configuration{configurations.length !== 1 ? 's' : ''} found</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={loadConfigurations}
                className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
              
              <button
                onClick={() => navigate('/vendor/upload')}
                className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <Upload className="w-4 h-4" />
                <span>Upload New</span>
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search configurations..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent w-full md:w-64"
                />
              </div>

              {/* Status Filter */}
              <div className="relative">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="pl-3 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent appearance-none bg-white"
                >
                  <option value="all">All Status</option>
                  <option value="uploaded">Uploaded</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
                <Filter className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
              </div>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'list' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'grid' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <Grid className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        {/* Configurations List/Grid */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          {filteredConfigurations.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchTerm || filterStatus !== 'all' ? 'No Matching Configurations' : 'No Configurations Yet'}
              </h3>
              <p className="mb-4">
                {searchTerm || filterStatus !== 'all' ? 
                  'Try adjusting your search or filter criteria' : 
                  'Upload your first configuration file to get started'
                }
              </p>
              {!searchTerm && filterStatus === 'all' && (
                <button
                  onClick={() => navigate('/vendor/upload')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Upload Configuration
                </button>
              )}
            </div>
          ) : (
            <div className={viewMode === 'grid' ? 
              'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 
              'space-y-4'
            }>
              {filteredConfigurations.map((config) => {
                const associatedAudit = getAuditForConfig(config.config_id);
                
                return viewMode === 'grid' ? (
                  /* Grid Card View */
                  <div key={config.config_id} className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 truncate mb-1">{config.filename}</h3>
                        <p className="text-sm text-gray-500 font-mono">{config.config_id}</p>
                      </div>
                      <div className="relative">
                        <button className="p-1 text-gray-400 hover:text-gray-600">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Status:</span>
                        <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs font-medium ${getStatusColor(config.status)}`}>
                          {getStatusIcon(config.status)}
                          <span>{config.status}</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Vendor:</span>
                        <span className="text-sm font-medium">{config.vendor}</span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Confidence:</span>
                        <span className="text-sm font-medium">{(config.vendor_confidence * 100).toFixed(0)}%</span>
                      </div>

                      {associatedAudit && (
                        <div className="bg-gray-50 rounded-lg p-3 mt-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-gray-700">Latest Audit</span>
                            <span className={`px-2 py-1 rounded text-xs font-medium border ${getRiskLevelColor(associatedAudit.risk_level)}`}>
                              {associatedAudit.risk_level}
                            </span>
                          </div>
                          <div className="text-xs text-gray-600">
                            Compliance: <span className="font-medium">{associatedAudit.compliance_score}%</span>
                          </div>
                        </div>
                      )}

                      <div className="flex space-x-2 pt-4 border-t border-gray-100">
                        <button
                          onClick={() => navigate(`/vendor/configuration/${config.config_id}`)}
                          className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                        >
                          <Eye className="w-3 h-3" />
                          <span>View</span>
                        </button>
                        
                        {associatedAudit && associatedAudit.status === 'COMPLETED' && (
                          <button
                            onClick={() => navigate(`/vendor/audit/${associatedAudit.audit_id}`)}
                            className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                          >
                            <Shield className="w-3 h-3" />
                            <span>Audit</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  /* List Row View */
                  <div key={config.config_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-medium text-gray-900 truncate">{config.filename}</h3>
                          <span className={`flex items-center space-x-1 px-2 py-1 rounded text-xs font-medium ${getStatusColor(config.status)}`}>
                            {getStatusIcon(config.status)}
                            <span>{config.status}</span>
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm text-gray-600">
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
                            <div>{(config.vendor_confidence * 100).toFixed(0)}%</div>
                          </div>
                          <div>
                            <span className="font-medium">Uploaded:</span>
                            <div className="text-xs">{new Date(config.created_at).toLocaleDateString()}</div>
                          </div>
                          <div>
                            {associatedAudit ? (
                              <div>
                                <span className="font-medium">Audit:</span>
                                <div className="flex items-center space-x-1">
                                  <span className="text-xs">{associatedAudit.compliance_score}%</span>
                                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getRiskLevelColor(associatedAudit.risk_level)}`}>
                                    {associatedAudit.risk_level}
                                  </span>
                                </div>
                              </div>
                            ) : (
                              <div className="text-xs text-gray-400">No audit yet</div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2 ml-4">
                        <button
                          onClick={() => navigate(`/vendor/configuration/${config.config_id}`)}
                          className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                        >
                          <Eye className="w-3 h-3" />
                          <span>View</span>
                        </button>
                        
                        {associatedAudit && associatedAudit.status === 'COMPLETED' && (
                          <button
                            onClick={() => navigate(`/vendor/audit/${associatedAudit.audit_id}`)}
                            className="flex items-center space-x-1 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                          >
                            <Shield className="w-3 h-3" />
                            <span>Audit</span>
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

        {/* Summary Stats */}
        {filteredConfigurations.length > 0 && (
          <div className="mt-6 bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Summary Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-900">{configurations.length}</div>
                <div className="text-sm text-blue-700">Total Configurations</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-900">
                  {audits.filter(a => a.status === 'COMPLETED').length}
                </div>
                <div className="text-sm text-green-700">Completed Audits</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-yellow-900">
                  {audits.filter(a => a.requires_human_review).length}
                </div>
                <div className="text-sm text-yellow-700">Need Review</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-900">
                  {audits.length > 0 ? 
                    Math.round(audits.filter(a => a.status === 'COMPLETED')
                      .reduce((sum, a) => sum + a.compliance_score, 0) / 
                      audits.filter(a => a.status === 'COMPLETED').length || 0
                    ) : 0
                  }%
                </div>
                <div className="text-sm text-purple-700">Avg Compliance</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}