import { useEffect, useState } from 'react';
import { FileText, Calendar, Shield, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { listConfigurations, runAudit } from '../services/api';
import type { Configuration } from '../types';

const Configurations = () => {
  const [configurations, setConfigurations] = useState<Configuration[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningAudit, setRunningAudit] = useState<string | null>(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    loadConfigurations();
  }, []);
  
  const loadConfigurations = async () => {
    try {
      const response = await listConfigurations();
      if (response.success && response.data) {
        setConfigurations(response.data.configurations);
      }
    } catch (error) {
      console.error('Failed to load configurations:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleRunAudit = async (configId: string) => {
    setRunningAudit(configId);
    try {
      const response = await runAudit(configId);
      if (response.success && response.data) {
        // Navigate to audit results
        navigate(`/audit/${response.data.audit_id}`);
      }
    } catch (error) {
      console.error('Failed to run audit:', error);
      alert('Failed to run audit. Please try again.');
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
        return 'bg-blue-900/30 text-blue-400 border border-blue-800';
      case 'NEEDS_REVIEW':
        return 'badge-medium';
      default:
        return 'bg-gray-700 text-gray-300 border border-gray-600';
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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Configurations</h1>
          <p className="text-gray-400">Uploaded network device configurations</p>
        </div>
        <a href="/upload" className="btn-primary">
          Upload New
        </a>
      </div>
      
      {configurations.length === 0 ? (
        <div className="card text-center py-12">
          <FileText className="w-16 h-16 mx-auto mb-4 text-gray-500" />
          <h3 className="text-xl font-semibold mb-2">No configurations yet</h3>
          <p className="text-gray-400 mb-4">Upload your first configuration to begin security analysis</p>
          <a href="/upload" className="btn-primary inline-block">
            Upload Configuration
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {configurations.map((config) => (
            <div key={config.id} className="card hover:border-gray-600 transition-colors cursor-pointer">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="text-4xl">{getVendorIcon(config.vendor)}</div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold">{config.filename}</h3>
                      <span className={`badge ${getStatusBadgeClass(config.status)}`}>
                        {config.status}
                      </span>
                      {config.vendor && (
                        <span className="badge bg-purple-900/30 text-purple-400 border border-purple-800">
                          {config.vendor}
                          {config.vendor_confidence && 
                            ` (${(config.vendor_confidence * 100).toFixed(0)}%)`
                          }
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <div className="flex items-center space-x-1">
                        <Shield className="w-4 h-4" />
                        <span>{config.config_id}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <FileText className="w-4 h-4" />
                        <span>{config.file_type}</span>
                      </div>
                      <div className="flex items-center space-x-1">
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
                    className="btn-primary flex items-center space-x-2"
                  >
                    {runningAudit === config.config_id ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Running...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
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
