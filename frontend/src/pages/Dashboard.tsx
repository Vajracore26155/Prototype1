import { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { getDashboardSummary } from '../services/api';
import type { DashboardSummary } from '../types';

const Dashboard = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadDashboard();
  }, []);
  
  const loadDashboard = async () => {
    try {
      const response = await getDashboardSummary();
      if (response.success && response.data) {
        setSummary(response.data);
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
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
      <div>
        <h1 className="text-3xl font-bold mb-2">Security Compliance Dashboard</h1>
        <p className="text-gray-400">Multi-vendor network configuration security analysis</p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Configurations</p>
              <p className="text-3xl font-bold">{summary?.total_configs || 0}</p>
            </div>
            <Shield className="w-12 h-12 text-blue-500 opacity-50" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Compliance Score</p>
              <p className="text-3xl font-bold">{summary?.compliance_score || 0}%</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-500 opacity-50" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Critical Findings</p>
              <p className="text-3xl font-bold text-red-400">{summary?.critical_findings || 0}</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-500 opacity-50" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Total Audits</p>
              <p className="text-3xl font-bold">{summary?.total_audits || 0}</p>
            </div>
            <Clock className="w-12 h-12 text-blue-500 opacity-50" />
          </div>
        </div>
      </div>
      
      {/* Findings Summary */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Findings by Severity</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-red-900/20 border border-red-800 rounded-lg">
            <p className="text-3xl font-bold text-red-400">{summary?.critical_findings || 0}</p>
            <p className="text-sm text-gray-400 mt-1">Critical</p>
          </div>
          <div className="text-center p-4 bg-orange-900/20 border border-orange-800 rounded-lg">
            <p className="text-3xl font-bold text-orange-400">{summary?.high_findings || 0}</p>
            <p className="text-sm text-gray-400 mt-1">High</p>
          </div>
          <div className="text-center p-4 bg-yellow-900/20 border border-yellow-800 rounded-lg">
            <p className="text-3xl font-bold text-yellow-400">{summary?.medium_findings || 0}</p>
            <p className="text-sm text-gray-400 mt-1">Medium</p>
          </div>
          <div className="text-center p-4 bg-green-900/20 border border-green-800 rounded-lg">
            <p className="text-3xl font-bold text-green-400">{summary?.low_findings || 0}</p>
            <p className="text-sm text-gray-400 mt-1">Low</p>
          </div>
        </div>
      </div>
      
      {/* Getting Started */}
      {summary?.total_configs === 0 && (
        <div className="card border-blue-800 bg-blue-900/20">
          <div className="flex items-start space-x-4">
            <Shield className="w-8 h-8 text-blue-400 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-bold mb-2">Welcome to SIH26155!</h3>
              <p className="text-gray-300 mb-4">
                Get started by uploading your first network configuration file. 
                We support Cisco, Fortinet, and can learn to understand new vendor formats using AI.
              </p>
              <a 
                href="/upload" 
                className="btn-primary inline-block"
              >
                Upload Configuration
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
