import { useEffect, useState } from 'react';
import { FileText, Calendar, Shield, Play, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { listConfigurations, runAudit } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import type { Configuration } from '../types';
import BackButton from '../components/BackButton';

const Configurations = () => {
  const [configurations, setConfigurations] = useState<Configuration[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningAudit, setRunningAudit] = useState<string | null>(null);
  const navigate = useNavigate();
  const { showSuccess, showError, showInfo } = useToast();
  
  useEffect(() => {
    loadConfigurations();
  }, []);
  
  const loadConfigurations = async () => {
    try {
      const response = await listConfigurations();
      if (response.success && response.data) {
        setConfigurations(response.data.configurations);
      }
    } catch (error: any) {
      console.error('Failed to load configurations:', error);
      showError('Failed to Load Configurations', 'Could not retrieve configuration list. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleRunAudit = async (configId: string) => {
    setRunningAudit(configId);
    showInfo('Starting Audit', 'Running security compliance audit...');
    
    console.log(`[DEBUG] Starting audit for config: ${configId}`);
    
    try {
      console.log(`[DEBUG] Calling runAudit API...`);
      const response = await runAudit(configId);
      console.log(`[DEBUG] API Response:`, response);
      
      if (response.success && response.data) {
        showSuccess('Audit Complete!', 'Security audit completed successfully.');
        // Navigate to audit results
        navigate(`/audit/${response.data.audit_id}`);
      } else {
        console.error('[DEBUG] API returned success=false:', response);
        showError('Audit Failed', response.error?.message || 'Unknown error occurred');
      }
    } catch (error: any) {
      console.error('[DEBUG] Exception caught:', error);
      console.error('[DEBUG] Error response:', error.response);
      console.error('[DEBUG] Error data:', error.response?.data);
      console.error('[DEBUG] Error status:', error.response?.status);
      
      const errorMessage = error.response?.data?.detail?.error?.message 
        || error.response?.data?.detail 
        || error.message 
        || 'Could not run security audit. Please try again.';
      
      showError('Audit Failed', errorMessage);
    } finally {
      setRunningAudit(null);
    }
  };
  
  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'badge-pass';
      case 'FAILED':
        return 'badge-fail';
      case 'PROCESSING':
        return 'badge-info';
      case 'NEEDS_REVIEW':
        return 'badge-medium';
      default:
        return 'bg-neutral-100 text-neutral-700 border-neutral-300';
    }
  };
  
  const getVendorIcon = (vendor?: string) => {
    if (!vendor) return '❓';
    switch (vendor.toLowerCase()) {
      case 'cisco':
        return '🔷';
      case 'fortinet':
        return '🔶';
      default:
        return '❓';
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner h-12 w-12"></div>
      </div>
    );
  }
  
  return (
    <div className="space-y-8 page-enter">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <BackButton to="/dashboard" label="Dashboard" />
          </div>
          <h1 className="text-3xl font-bold mb-2 text-neutral-900">Configurations</h1>
          <p className="text-neutral-600">Uploaded network device configurations</p>
        </div>
        <a href="/upload" className="btn-primary group flex items-center space-x-2">
          <span>Upload New</span>
          <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-200" />
        </a>
      </div>
      
      {configurations.length === 0 ? (
        <div className="card text-center py-12">
          <div className="p-4 bg-neutral-100 rounded-2xl inline-block mb-4">
            <FileText className="w-16 h-16 text-neutral-500" />
          </div>
          <h3 className="text-xl font-semibold mb-2 text-neutral-900">No configurations yet</h3>
          <p className="text-neutral-600 mb-6">Upload your first configuration to begin security analysis</p>
          <a href="/upload" className="btn-primary inline-block">
            Upload Configuration
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {configurations.map((config, index) => (
            <div 
              key={config.id} 
              className="card hover:border-neutral-300 hover:shadow-md transition-all duration-200 cursor-pointer hover:translate-y-[-1px] stagger-item"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="text-4xl">{getVendorIcon(config.vendor)}</div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2 flex-wrap gap-y-2">
                      <h3 className="text-lg font-semibold text-neutral-900">{config.filename}</h3>
                      <span className={`badge ${getStatusBadgeClass(config.status)} transition-all duration-150`}>
                        {config.status}
                      </span>
                      {config.vendor && (
                        <span className="badge bg-purple-50 text-purple-700 border-purple-200 transition-all duration-150">
                          {config.vendor}
                          {config.vendor_confidence && 
                            ` (${(config.vendor_confidence * 100).toFixed(0)}%)`
                          }
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-neutral-600">
                      <div className="flex items-center space-x-1.5">
                        <Shield className="w-4 h-4" />
                        <span className="font-medium">{config.config_id}</span>
                      </div>
                      <div className="flex items-center space-x-1.5">
                        <FileText className="w-4 h-4" />
                        <span>{config.file_type}</span>
                      </div>
                      <div className="flex items-center space-x-1.5">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(config.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {config.status === 'UPLOADED' && (
                  <button 
                    onClick={() => handleRunAudit(config.config_id)}
                    disabled={runningAudit === config.config_id}
                    className="btn-primary flex items-center space-x-2 group"
                  >
                    {runningAudit === config.config_id ? (
                      <>
                        <div className="spinner h-4 w-4 border-white"></div>
                        <span>Running...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                        <span>Run Audit</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Configurations;
