import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2, Settings, LogOut, TrendingUp, Upload, Users, Calendar,
  BarChart3, FileText, Shield, Activity, Bell, Download, RefreshCw,
  ChevronRight, ExternalLink, ArrowLeft, Menu, X
} from 'lucide-react';
import { 
  getVendorSession, 
  revokeVendorSession, 
  isVendorLoggedIn 
} from '../services/vendorApi';
import VendorAnalyticsDashboard from '../components/VendorAnalyticsDashboard';
import DetailedConfigurationManager from '../components/DetailedConfigurationManager';
import DetailedAuditFindings from '../components/DetailedAuditFindings';

interface SessionInfo {
  session_id: string;
  vendor: {
    vendor_id: string;
    company: string;
    contact: string;
    email: string;
  };
  status: string;
  upload_count: number;
  created_at: string;
  expires_at: string;
  last_activity: string;
  organization_id: number;
}

type DashboardView = 'overview' | 'analytics' | 'configurations' | 'findings' | 'reports' | 'settings';

export default function VendorDashboardEnhanced() {
  const navigate = useNavigate();
  const [currentView, setCurrentView] = useState<DashboardView>('overview');
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, type: 'success', message: 'Configuration audit completed', time: '2 min ago' },
    { id: 2, type: 'warning', message: 'Critical finding detected', time: '1 hour ago' },
    { id: 3, type: 'info', message: 'New compliance framework added', time: '3 hours ago' }
  ]);

  useEffect(() => {
    // Check if vendor is logged in
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }

    loadDashboardData();
  }, [navigate]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const sessionResponse = await getVendorSession();
      if (sessionResponse.success) {
        setSessionInfo(sessionResponse.data);
      } else {
        throw new Error(sessionResponse.data?.error?.message || 'Failed to load session');
      }
    } catch (err: any) {
      console.error('Failed to load dashboard:', err);
      setError(err.response?.data?.error?.message || err.message || 'Failed to load dashboard data');
      
      if (err.response?.status === 401) {
        localStorage.removeItem('vendor_session_token');
        localStorage.removeItem('vendor_info');
        setTimeout(() => navigate('/vendor/login'), 1000);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await revokeVendorSession();
      navigate('/vendor/login');
    } catch (err) {
      localStorage.removeItem('vendor_session_token');
      localStorage.removeItem('vendor_info');
      navigate('/vendor/login');
    }
  };

  const sidebarItems = [
    { id: 'overview', name: 'Overview', icon: TrendingUp },
    { id: 'analytics', name: 'Analytics', icon: BarChart3 },
    { id: 'configurations', name: 'Configurations', icon: FileText },
    { id: 'findings', name: 'Security Findings', icon: Shield },
    { id: 'reports', name: 'Reports', icon: Download },
    { id: 'settings', name: 'Settings', icon: Settings }
  ];

  const getTimeRemaining = (expiresAt: string) => {
    const expiry = new Date(expiresAt);
    const now = new Date();
    const diff = expiry.getTime() - now.getTime();

    if (diff < 0) return 'Expired';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0 lg:static lg:inset-0`}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 bg-indigo-600 text-white">
          <div className="flex items-center space-x-3">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-lg font-semibold truncate">
                {sessionInfo?.vendor?.company || 'Vendor Portal'}
              </h1>
              <p className="text-indigo-100 text-xs">Professional Dashboard</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 text-indigo-200 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentView(item.id as DashboardView);
                  setSidebarOpen(false);
                }}
                className={`w-full flex items-center px-3 py-3 text-sm font-medium rounded-lg mb-1 transition-colors ${
                  currentView === item.id
                    ? 'bg-indigo-100 text-indigo-700 border-l-4 border-indigo-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.name}
                {currentView === item.id && (
                  <ChevronRight className="ml-auto h-4 w-4" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Session Info */}
        {sessionInfo && (
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
            <div className="text-xs text-gray-500 mb-2">Session Status</div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-900">
                  {getTimeRemaining(sessionInfo.expires_at)}
                </div>
                <div className="text-xs text-gray-500">remaining</div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-gray-600 rounded"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="lg:pl-64 flex flex-col min-h-screen">
        {/* Top Header */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Mobile Menu Button */}
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 text-gray-400 hover:text-gray-600"
              >
                <Menu className="h-6 w-6" />
              </button>

              {/* Page Title */}
              <div className="flex items-center space-x-4">
                <h2 className="text-2xl font-bold text-gray-900 capitalize">
                  {currentView === 'overview' ? 'Dashboard Overview' : 
                   currentView === 'analytics' ? 'Analytics & Insights' :
                   currentView === 'configurations' ? 'Configuration Management' :
                   currentView === 'findings' ? 'Security Findings' :
                   currentView === 'reports' ? 'Reports & Downloads' :
                   'Settings & Profile'}
                </h2>
              </div>

              {/* Header Actions */}
              <div className="flex items-center space-x-4">
                {/* Notifications */}
                <div className="relative">
                  <button className="p-2 text-gray-400 hover:text-gray-600 relative">
                    <Bell className="h-5 w-5" />
                    {notifications.length > 0 && (
                      <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {notifications.length}
                      </span>
                    )}
                  </button>
                </div>

                {/* Quick Upload */}
                <button
                  onClick={() => navigate('/vendor/upload')}
                  className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Upload className="h-4 w-4" />
                  <span className="hidden sm:inline">Quick Upload</span>
                </button>

                {/* Refresh */}
                <button
                  onClick={loadDashboardData}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                  title="Refresh Data"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 p-4 sm:p-6 lg:p-8">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Render Current View */}
          {currentView === 'overview' && (
            <VendorOverview sessionInfo={sessionInfo} />
          )}
          {currentView === 'analytics' && (
            <VendorAnalyticsDashboard />
          )}
          {currentView === 'configurations' && (
            <DetailedConfigurationManager />
          )}
          {currentView === 'findings' && (
            <DetailedAuditFindings auditId="AUD-001234" />
          )}
          {currentView === 'reports' && (
            <VendorReports />
          )}
          {currentView === 'settings' && (
            <VendorSettings sessionInfo={sessionInfo} />
          )}
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}

// Overview Component
const VendorOverview: React.FC<{ sessionInfo: SessionInfo | null }> = ({ sessionInfo }) => {
  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      {sessionInfo && (
        <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold mb-2">
                Welcome back, {sessionInfo.vendor.company}!
              </h2>
              <p className="text-indigo-100 mb-4">
                Here's your security compliance overview for today
              </p>
              <div className="flex items-center space-x-6 text-sm">
                <div>
                  <span className="text-indigo-200">Session ID:</span>
                  <span className="ml-2 font-mono">{sessionInfo.session_id}</span>
                </div>
                <div>
                  <span className="text-indigo-200">Files Uploaded:</span>
                  <span className="ml-2 font-bold">{sessionInfo.upload_count}</span>
                </div>
                <div>
                  <span className="text-indigo-200">Status:</span>
                  <span className="ml-2 capitalize font-medium">{sessionInfo.status}</span>
                </div>
              </div>
            </div>
            <div className="hidden lg:block">
              <div className="text-right">
                <div className="text-4xl font-bold">78.5%</div>
                <div className="text-indigo-200">Avg Compliance</div>
                <div className="flex items-center justify-end mt-2">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  <span className="text-sm">+2.3% this month</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Configurations</p>
              <p className="text-2xl font-bold text-gray-900">145</p>
              <p className="text-sm text-green-600">+12 this week</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <Shield className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Security Audits</p>
              <p className="text-2xl font-bold text-gray-900">132</p>
              <p className="text-sm text-green-600">97.3% success rate</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-red-100 rounded-lg">
              <Activity className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Critical Findings</p>
              <p className="text-2xl font-bold text-gray-900">23</p>
              <p className="text-sm text-red-600">Need attention</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Calendar className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Processing</p>
              <p className="text-2xl font-bold text-gray-900">4.2m</p>
              <p className="text-sm text-green-600">15% faster</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity and Next Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {/* Sample activities */}
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-green-100 rounded-full">
                <Shield className="w-4 h-4 text-green-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">Security audit completed</p>
                <p className="text-sm text-gray-500">cisco_router_config.txt - 78% compliance</p>
                <p className="text-xs text-gray-400">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-orange-100 rounded-full">
                <Activity className="w-4 h-4 text-orange-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">Critical finding detected</p>
                <p className="text-sm text-gray-500">SSH weak encryption in fortinet_fw.conf</p>
                <p className="text-xs text-gray-400">1 hour ago</p>
              </div>
            </div>
          </div>
        </div>

        {/* Next Actions */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Actions</h3>
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-3 bg-red-50 hover:bg-red-100 rounded-lg text-left">
              <div>
                <p className="font-medium text-red-900">Review Critical Findings</p>
                <p className="text-sm text-red-700">23 items need immediate attention</p>
              </div>
              <ChevronRight className="w-5 h-5 text-red-600" />
            </button>
            <button className="w-full flex items-center justify-between p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-left">
              <div>
                <p className="font-medium text-blue-900">Upload New Configuration</p>
                <p className="text-sm text-blue-700">Continue your compliance assessment</p>
              </div>
              <ChevronRight className="w-5 h-5 text-blue-600" />
            </button>
            <button className="w-full flex items-center justify-between p-3 bg-green-50 hover:bg-green-100 rounded-lg text-left">
              <div>
                <p className="font-medium text-green-900">Download Reports</p>
                <p className="text-sm text-green-700">Generate compliance documentation</p>
              </div>
              <ChevronRight className="w-5 h-5 text-green-600" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Placeholder components for other views
const VendorReports: React.FC = () => (
  <div className="text-center py-12">
    <Download className="w-16 h-16 mx-auto text-gray-300 mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">Reports & Downloads</h3>
    <p className="text-gray-500">Comprehensive reporting functionality coming soon.</p>
  </div>
);

const VendorSettings: React.FC<{ sessionInfo: SessionInfo | null }> = ({ sessionInfo }) => (
  <div className="text-center py-12">
    <Settings className="w-16 h-16 mx-auto text-gray-300 mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">Settings & Profile</h3>
    <p className="text-gray-500">User settings and profile management coming soon.</p>
    {sessionInfo && (
      <div className="mt-4 text-sm text-gray-600">
        <p>Current session: {sessionInfo.session_id}</p>
        <p>Company: {sessionInfo.vendor.company}</p>
      </div>
    )}
  </div>
);