import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Building2, Settings, LogOut, TrendingUp } from 'lucide-react';
import { 
  getVendorSession, 
  revokeVendorSession, 
  isVendorLoggedIn 
} from '../services/vendorApi';
import EnhancedVendorUpload from '../components/EnhancedVendorUpload';

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

export default function VendorUploadEnhanced() {
  const navigate = useNavigate();
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [error, setError] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    // Check if vendor is logged in
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }

    loadSessionInfo();
  }, [navigate]);

  const loadSessionInfo = async () => {
    try {
      const response = await getVendorSession();
      if (response.success) {
        setSessionInfo(response.data);
      } else {
        setError('Failed to load session info');
      }
    } catch (err: any) {
      console.error('Failed to load session:', err);
      if (err.response?.status === 401) {
        navigate('/vendor/login');
      } else {
        setError('Failed to load session info');
      }
    }
  };

  const handleLogout = async () => {
    try {
      await revokeVendorSession();
      navigate('/vendor/login');
    } catch (err) {
      console.error('Logout failed:', err);
      // Navigate anyway on logout
      navigate('/vendor/login');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left side */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/vendor/dashboard')}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-md"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              
              <div className="flex items-center space-x-3">
                <Building2 className="h-8 w-8 text-indigo-600" />
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">
                    {sessionInfo?.vendor?.company || 'Loading...'}
                  </h1>
                  <p className="text-sm text-gray-500">Enhanced Upload Portal</p>
                </div>
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              {sessionInfo && (
                <div className="text-sm text-gray-600">
                  {sessionInfo.vendor.contact}
                </div>
              )}
              
              {/* Menu */}
              <div className="relative">
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-md"
                >
                  <Settings className="h-5 w-5" />
                </button>
                
                {menuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5">
                    <div className="py-1">
                      <button
                        onClick={() => navigate('/vendor/dashboard')}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <TrendingUp className="h-4 w-4 mr-3" />
                        Dashboard
                      </button>
                      <button
                        onClick={() => navigate('/vendor/settings')}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <Settings className="h-4 w-4 mr-3" />
                        Settings
                      </button>
                      <hr className="my-1" />
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <LogOut className="h-4 w-4 mr-3" />
                        Logout
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="text-red-700">{error}</div>
          </div>
        )}

        {/* Session Info Banner */}
        {sessionInfo && (
          <div className="mb-6 bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-indigo-900 mb-2">
                  Welcome, {sessionInfo.vendor.company}!
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-indigo-600 font-medium">Session ID:</span>
                    <div className="text-indigo-800 font-mono">{sessionInfo.session_id}</div>
                  </div>
                  <div>
                    <span className="text-indigo-600 font-medium">Status:</span>
                    <div className="text-indigo-800 capitalize">{sessionInfo.status}</div>
                  </div>
                  <div>
                    <span className="text-indigo-600 font-medium">Files Uploaded:</span>
                    <div className="text-indigo-800 font-semibold">{sessionInfo.upload_count}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Upload Component */}
        <EnhancedVendorUpload />

        {/* Usage Guidelines */}
        <div className="mt-8 bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">Upload Guidelines</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Supported File Types</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Configuration files (.cfg, .conf, .txt)</li>
                <li>• JSON configuration (.json)</li>
                <li>• XML configuration (.xml)</li>
                <li>• YAML configuration (.yaml, .yml)</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">File Requirements</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Maximum file size: 10MB</li>
                <li>• Files must be text-readable</li>
                <li>• No executable files allowed</li>
                <li>• Files are scanned for security</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 rounded-md">
            <h4 className="font-medium text-blue-900 mb-2">Bulk Upload Behavior</h4>
            <p className="text-sm text-blue-800">
              • 1-4 files: Individual configurations created<br />
              • 5+ files: Overall configuration with aggregated analysis<br />
              • Each file is processed with AI-driven security analysis<br />
              • Professional PDF reports available after processing
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}