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
    <div className="min-h-screen bg-mist-50">
      {/* Header */}
      <div className="bg-white border-b border-line">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left side */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/vendor/dashboard')}
                title="Back to Dashboard"
                className="p-2 text-ink-500 hover:text-ink-950 hover:bg-mist-100 rounded-xl"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>

              <div className="flex items-center space-x-3">
                <Building2 className="h-8 w-8 text-ink-950" />
                <div>
                  <h1 className="text-lg font-bold tracking-tight text-ink-900">
                    {sessionInfo?.vendor?.company || 'Loading...'}
                  </h1>
                  <p className="text-xs font-bold text-ink-500">Enhanced Upload Portal</p>
                </div>
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-3">
              {sessionInfo && (
                <div className="text-sm font-bold text-ink-900 hidden sm:block">
                  {sessionInfo.vendor.contact}
                </div>
              )}
              <button
                onClick={handleLogout}
                title="Logout"
                className="p-2 text-ink-500 hover:text-ink-950 border border-line rounded-xl hover:bg-mist-50"
              >
                <LogOut className="h-5 w-5" />
              </button>

              {/* Menu */}
              <div className="relative">
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="p-2 text-ink-500 hover:text-ink-950 rounded-xl hover:bg-mist-50"
                >
                  <Settings className="h-5 w-5" />
                </button>

                {menuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-2xl shadow-xl border border-line">
                    <div className="py-1">
                      <button
                        onClick={() => navigate('/vendor/dashboard')}
                        className="flex items-center w-full px-4 py-2 text-sm font-bold text-ink-900 hover:bg-mist-50"
                      >
                        <TrendingUp className="h-4 w-4 mr-3" />
                        Dashboard
                      </button>
                      <button
                        onClick={() => navigate('/vendor/settings')}
                        className="flex items-center w-full px-4 py-2 text-sm font-bold text-ink-900 hover:bg-mist-50"
                      >
                        <Settings className="h-4 w-4 mr-3" />
                        Settings
                      </button>
                      <hr className="my-1 border-line" />
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm font-bold text-ink-950 hover:bg-mist-50"
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {error && (
          <div className="mb-5 bg-ink-950 text-white rounded-xl p-4">
            <div className="text-sm font-bold">{error}</div>
          </div>
        )}

        {/* Session Info Banner */}
        {sessionInfo && (
          <div className="mb-5 bg-ink-950 text-white rounded-2xl p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold tracking-tight mb-2">
                  Welcome, {sessionInfo.vendor.company}!
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-white/60 text-[11px] font-bold uppercase tracking-wide">Session ID</span>
                    <div className="text-white font-mono font-bold">{sessionInfo.session_id}</div>
                  </div>
                  <div>
                    <span className="text-white/60 text-[11px] font-bold uppercase tracking-wide">Status</span>
                    <div className="text-white capitalize font-bold">{sessionInfo.status}</div>
                  </div>
                  <div>
                    <span className="text-white/60 text-[11px] font-bold uppercase tracking-wide">Files Uploaded</span>
                    <div className="font-bold">{sessionInfo.upload_count}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Upload Component */}
        <EnhancedVendorUpload />

        {/* Usage Guidelines */}
        <div className="mt-5 tatva-card p-5">
          <h3 className="text-base font-bold tracking-tight text-ink-900 mb-3">Upload Guidelines</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wide text-ink-500 mb-1.5">Supported File Types</h4>
              <ul className="text-sm font-semibold text-ink-900 space-y-1">
                <li>• Configuration files (.cfg, .conf, .txt)</li>
                <li>• JSON configuration (.json)</li>
                <li>• XML configuration (.xml)</li>
                <li>• YAML configuration (.yaml, .yml)</li>
              </ul>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wide text-ink-500 mb-1.5">File Requirements</h4>
              <ul className="text-sm font-semibold text-ink-900 space-y-1">
                <li>• Maximum file size: 10MB</li>
                <li>• Files must be text-readable</li>
                <li>• No executable files allowed</li>
                <li>• Files are scanned for security</li>
              </ul>
            </div>
          </div>

          <div className="mt-5 p-4 bg-mist-50 border border-line rounded-xl">
            <h4 className="text-xs font-bold uppercase tracking-wide text-ink-900 mb-1.5">Bulk Upload Behavior</h4>
            <p className="text-sm font-semibold text-ink-500">
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