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
      <div className="min-h-screen bg-mist-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="tatva-card p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-line border-t-ink-950 rounded-full mx-auto mb-4"></div>
            <p className="font-bold text-ink-500">Loading configurations...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-mist-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="tatva-card p-5 mb-5">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center space-x-4 min-w-0">
              <button
                onClick={() => navigate('/vendor/dashboard')}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-bold text-ink-500 hover:text-ink-950 hover:bg-mist-100 rounded-xl transition-colors shrink-0"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Dashboard</span>
              </button>
              <div className="w-px h-6 bg-line"></div>
              <div className="min-w-0">
                <div className="text-[11px] font-bold tracking-[0.28em] text-ink-500">CONFIGURATION MANAGEMENT</div>
                <h1 className="text-3xl font-bold tracking-tight text-ink-900 truncate">Configuration Management</h1>
                <p className="text-sm font-semibold text-ink-500">{configurations.length} configuration{configurations.length !== 1 ? 's' : ''} found</p>
              </div>
            </div>

            <div className="flex items-center space-x-2 shrink-0">
              <button
                onClick={loadConfigurations}
                className="flex items-center space-x-2 px-4 py-2.5 text-sm font-bold text-ink-500 hover:text-ink-950 hover:bg-mist-100 rounded-xl transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>

              <button
                onClick={() => navigate('/vendor/upload')}
                className="btn-ink flex items-center space-x-2 px-6 py-3 rounded-xl text-sm"
              >
                <Upload className="w-4 h-4" />
                <span>Upload New</span>
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-ink-950 text-white px-4 py-3 rounded-xl mb-5 font-bold text-sm">
            {error}
          </div>
        )}

        {/* Search and Filters */}
        <div className="tatva-card p-4 mb-5">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div className="flex flex-col md:flex-row md:items-center gap-3 flex-1">
              {/* Search */}
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-ink-500 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search configurations..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2.5 border border-line rounded-xl font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-950 w-full md:w-64"
                />
              </div>

              {/* Status Filter */}
              <div className="relative">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="pl-3 pr-8 py-2.5 border border-line rounded-xl font-bold text-ink-900 focus:outline-none appearance-none bg-white text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="uploaded">Uploaded</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
                <Filter className="absolute right-3 top-1/2 transform -translate-y-1/2 text-ink-500 w-4 h-4 pointer-events-none" />
              </div>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-1 bg-mist-50 border border-line rounded-xl p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'list' ? 'bg-ink-950 text-white' : 'text-ink-500 hover:text-ink-950'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'grid' ? 'bg-ink-950 text-white' : 'text-ink-500 hover:text-ink-950'
                }`}
              >
                <Grid className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        {/* Configurations List/Grid */}
        <div className="tatva-card p-5">
          {filteredConfigurations.length === 0 ? (
            <div className="text-center py-10">
              <FileText className="w-14 h-14 mx-auto mb-4 text-line" />
              <h3 className="text-lg font-bold tracking-tight text-ink-900 mb-2">
                {searchTerm || filterStatus !== 'all' ? 'No Matching Configurations' : 'No Configurations Yet'}
              </h3>
              <p className="mb-4 text-sm font-semibold text-ink-500">
                {searchTerm || filterStatus !== 'all' ?
                  'Try adjusting your search or filter criteria' :
                  'Upload your first configuration file to get started'
                }
              </p>
              {!searchTerm && filterStatus === 'all' && (
                <button
                  onClick={() => navigate('/vendor/upload')}
                  className="btn-ink px-6 py-3 rounded-xl text-sm font-bold"
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
                  <div key={config.config_id} className="border border-line rounded-2xl p-5 hover:border-ink-950 hover:shadow-md transition-all bg-white">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-ink-900 truncate mb-1">{config.filename}</h3>
                        <p className="text-xs font-mono font-bold text-ink-500">{config.config_id}</p>
                      </div>
                      <div className="relative">
                        <button className="p-1 text-ink-500 hover:text-ink-950">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wide text-ink-500">Status</span>
                        <div className={`flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-bold ${getStatusColor(config.status)}`}>
                          {getStatusIcon(config.status)}
                          <span>{config.status}</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wide text-ink-500">Vendor</span>
                        <span className="text-sm font-bold text-ink-900">{config.vendor}</span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wide text-ink-500">Confidence</span>
                        <span className="text-sm font-bold text-ink-900">{(((config as any).vendor_confidence ?? 0) * 100).toFixed(0)}%</span>
                      </div>

                      {associatedAudit && (
                        <div className="bg-mist-50 border border-line rounded-xl p-3 mt-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[11px] font-bold uppercase tracking-wide text-ink-500">Latest Audit</span>
                            <span className={`px-2 py-1 rounded-lg text-[11px] font-bold border ${getRiskLevelColor(associatedAudit.risk_level)}`}>
                              {associatedAudit.risk_level}
                            </span>
                          </div>
                          <div className="text-xs font-semibold text-ink-500">
                            Compliance: <span className="font-bold text-ink-950">{associatedAudit.compliance_score}%</span>
                          </div>
                        </div>
                      )}

                      <div className="flex space-x-2 pt-4 border-t border-line">
                        <button
                          onClick={() => navigate(`/vendor/configuration/${config.config_id}`)}
                          className="btn-ink flex-1 flex items-center justify-center space-x-1 px-3 py-2.5 text-sm rounded-xl"
                        >
                          <Eye className="w-3 h-3" />
                          <span>View</span>
                        </button>

                        {associatedAudit && associatedAudit.status === 'COMPLETED' && (
                          <button
                            onClick={() => navigate(`/vendor/audit/${associatedAudit.audit_id}`)}
                            className="btn-paper flex-1 flex items-center justify-center space-x-1 px-3 py-2.5 text-sm rounded-xl"
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
                  <div key={config.config_id} className="border border-line rounded-2xl p-4 hover:border-ink-950 hover:shadow-md transition-all bg-white">
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2 flex-wrap">
                          <h3 className="font-bold text-ink-900 truncate">{config.filename}</h3>
                          <span className={`flex items-center space-x-1 px-2.5 py-1 rounded-lg text-[11px] font-bold ${getStatusColor(config.status)}`}>
                            {getStatusIcon(config.status)}
                            <span>{config.status}</span>
                          </span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                          <div>
                            <span className="text-[11px] font-bold uppercase tracking-wide text-ink-500">Config ID</span>
                            <div className="font-mono text-xs font-bold text-ink-900">{config.config_id}</div>
                          </div>
                          <div>
                            <span className="text-[11px] font-bold uppercase tracking-wide text-ink-500">Vendor</span>
                            <div className="font-bold text-ink-900">{config.vendor}</div>
                          </div>
                          <div>
                            <span className="text-[11px] font-bold uppercase tracking-wide text-ink-500">Confidence</span>
                            <div className="font-bold text-ink-900">{(((config as any).vendor_confidence ?? 0) * 100).toFixed(0)}%</div>
                          </div>
                          <div>
                            <span className="text-[11px] font-bold uppercase tracking-wide text-ink-500">Uploaded</span>
                            <div className="text-xs font-bold text-ink-900">{config.created_at ? new Date(config.created_at).toLocaleDateString() : 'N/A'}</div>
                          </div>
                          <div>
                            {associatedAudit ? (
                              <div>
                                <span className="text-[11px] font-bold uppercase tracking-wide text-ink-500">Audit</span>
                                <div className="flex items-center space-x-1.5">
                                  <span className="text-xs font-bold text-ink-900">{associatedAudit.compliance_score}%</span>
                                  <span className={`px-2 py-0.5 rounded-lg text-[11px] font-bold border ${getRiskLevelColor(associatedAudit.risk_level)}`}>
                                    {associatedAudit.risk_level}
                                  </span>
                                </div>
                              </div>
                            ) : (
                              <div className="text-xs font-bold text-ink-500">No audit yet</div>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 ml-4 shrink-0">
                        <button
                          onClick={() => navigate(`/vendor/configuration/${config.config_id}`)}
                          className="btn-ink flex items-center space-x-1 px-4 py-2 text-sm rounded-xl"
                        >
                          <Eye className="w-3 h-3" />
                          <span>View</span>
                        </button>

                        {associatedAudit && associatedAudit.status === 'COMPLETED' && (
                          <button
                            onClick={() => navigate(`/vendor/audit/${associatedAudit.audit_id}`)}
                            className="btn-paper flex items-center space-x-1 px-4 py-2 text-sm rounded-xl"
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
          <div className="mt-5 tatva-card p-5">
            <h3 className="text-xl font-bold tracking-tight text-ink-900 mb-4">Summary Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-ink-950 text-white rounded-xl p-4">
                <div className="text-2xl font-bold">{configurations.length}</div>
                <div className="text-[11px] font-bold text-white/60 uppercase tracking-wide">Total Configurations</div>
              </div>
              <div className="bg-mist-50 border border-line rounded-xl p-4">
                <div className="text-2xl font-bold text-ink-950">
                  {audits.filter(a => a.status === 'COMPLETED').length}
                </div>
                <div className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">Completed Audits</div>
              </div>
              <div className="bg-mist-50 border border-line rounded-xl p-4">
                <div className="text-2xl font-bold text-ink-950">
                  {audits.filter(a => a.requires_human_review).length}
                </div>
                <div className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">Need Review</div>
              </div>
              <div className="bg-mist-50 border border-line rounded-xl p-4">
                <div className="text-2xl font-bold text-ink-950">
                  {audits.length > 0 ?
                    Math.round(audits.filter(a => a.status === 'COMPLETED')
                      .reduce((sum, a) => sum + a.compliance_score, 0) /
                      audits.filter(a => a.status === 'COMPLETED').length || 0
                    ) : 0
                  }%
                </div>
                <div className="text-[11px] font-bold text-ink-500 uppercase tracking-wide">Avg Compliance</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}