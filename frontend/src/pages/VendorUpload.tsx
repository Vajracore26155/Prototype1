import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  uploadVendorConfiguration,
  uploadVendorBulk,
  getVendorSession,
  getVendorUploadHistory,
  revokeVendorSession,
  isVendorLoggedIn,
} from '../services/vendorApi';

interface UploadedFile {
  config_id: string;
  filename: string;
  detected_vendor: string;
  confidence: number;
  uploaded_at?: string;
}

export default function VendorUpload() {
  const navigate = useNavigate();
  const [sessionInfo, setSessionInfo] = useState<any>(null);
  const [uploadHistory, setUploadHistory] = useState<UploadedFile[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: string }>({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [redirecting, setRedirecting] = useState(false);
  const [redirectCountdown, setRedirectCountdown] = useState(0);

  useEffect(() => {
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }
    loadSessionInfo();
    loadUploadHistory();
  }, [navigate]);

  const loadSessionInfo = async () => {
    try {
      const response = await getVendorSession();
      if (response.success) {
        setSessionInfo(response.data);
      }
    } catch (err: any) {
      console.error('Failed to load session:', err);
    }
  };

  const loadUploadHistory = async () => {
    try {
      const response = await getVendorUploadHistory();
      if (response.success) {
        setUploadHistory(response.data.uploads || []);
      }
    } catch (err: any) {
      console.error('Failed to load history:', err);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
      setError('');
      setSuccess('');
    }
  };

  const handleSingleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const file = selectedFiles[0];
      setUploadProgress({ [file.name]: 'Uploading...' });

      const response = await uploadVendorConfiguration(file);

      if (response.success) {
        setUploadProgress({ [file.name]: 'Success!' });
        setSuccess(`File "${file.name}" uploaded successfully!`);
        
        // Get config_id from response for navigation
        const configId = response.data.config_id;
        
        // Clear file input
        const fileInput = document.getElementById('file-input') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
        
        // Start redirect countdown
        setRedirecting(true);
        setRedirectCountdown(3);
        
        const countdownInterval = setInterval(() => {
          setRedirectCountdown(prev => {
            if (prev <= 1) {
              clearInterval(countdownInterval);
              navigate(`/vendor/configuration/${configId}`);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || 'Upload failed';
      setError(errorMsg);
      setUploadProgress({});
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress({}), 3000);
    }
  };

  const handleBulkUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setError('');
    setSuccess('');

    const progress: { [key: string]: string } = {};
    selectedFiles.forEach(file => {
      progress[file.name] = 'Uploading...';
    });
    setUploadProgress(progress);

    try {
      const response = await uploadVendorBulk(selectedFiles);

      if (response.success) {
        const uploaded = response.data.uploaded || [];
        const failed = response.data.failed || [];

        uploaded.forEach((item: any) => {
          progress[item.filename] = 'Success!';
        });

        failed.forEach((item: any) => {
          progress[item.filename] = `Failed: ${item.error}`;
        });

        setUploadProgress(progress);
        setSuccess(`Uploaded ${uploaded.length} of ${selectedFiles.length} files successfully`);
        
        // Clear file input
        const fileInput = document.getElementById('file-input') as HTMLInputElement;
        if (fileInput) fileInput.value = '';

        // If we have successful uploads, navigate to the first one after delay
        if (uploaded.length > 0) {
          const firstConfigId = uploaded[0].config_id;
          setRedirecting(true);
          setRedirectCountdown(5);
          
          const countdownInterval = setInterval(() => {
            setRedirectCountdown(prev => {
              if (prev <= 1) {
                clearInterval(countdownInterval);
                navigate(`/vendor/configuration/${firstConfigId}`);
                return 0;
              }
              return prev - 1;
            });
          }, 1000);
        }
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || 'Bulk upload failed';
      setError(errorMsg);
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress({}), 5000);
    }
  };

  const handleLogout = async () => {
    try {
      await revokeVendorSession();
      navigate('/vendor/login');
    } catch (err) {
      // Force logout even if API fails
      localStorage.removeItem('vendor_session_token');
      localStorage.removeItem('vendor_info');
      navigate('/vendor/login');
    }
  };

  const formatExpiryTime = (expiresAt: string) => {
    const expiry = new Date(expiresAt);
    const now = new Date();
    const diff = expiry.getTime() - now.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diff < 0) return 'Expired';
    if (hours > 0) return `${hours}h ${minutes}m remaining`;
    return `${minutes}m remaining`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-1">Vendor Upload Portal</h1>
              <p className="text-gray-600">
                {sessionInfo?.vendor?.company || 'Loading...'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Logout
            </button>
          </div>

          {/* Session Info */}
          {sessionInfo && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-sm text-blue-600 font-medium mb-1">Session Status</div>
                <div className="text-lg font-bold text-blue-900">{sessionInfo.status}</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-green-600 font-medium mb-1">Files Uploaded</div>
                <div className="text-lg font-bold text-green-900">{sessionInfo.upload_count || 0}</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-sm text-purple-600 font-medium mb-1">Session Expires</div>
                <div className="text-lg font-bold text-purple-900">
                  {formatExpiryTime(sessionInfo.expires_at)}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Configurations</h2>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4 text-sm">
                {success}
              </div>
            )}

            {redirecting && redirectCountdown > 0 && (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mb-4 text-sm">
                <div className="flex items-center space-x-2">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>
                    Redirecting to configuration processing in {redirectCountdown} second{redirectCountdown !== 1 ? 's' : ''}...
                  </span>
                </div>
              </div>
            )}

            <div className="space-y-4">
              {/* File Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Configuration Files
                </label>
                <input
                  id="file-input"
                  type="file"
                  multiple
                  onChange={handleFileSelect}
                  className="w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none transition-colors cursor-pointer hover:border-indigo-400"
                  accept=".txt,.cfg,.conf"
                />
                <p className="mt-2 text-xs text-gray-500">
                  Supported formats: .txt, .cfg, .conf (Cisco, Fortinet configurations)
                </p>
              </div>

              {/* Selected Files */}
              {selectedFiles.length > 0 && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-700 mb-2">
                    Selected Files ({selectedFiles.length})
                  </div>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {selectedFiles.map((file, idx) => (
                      <div key={idx} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 truncate flex-1">{file.name}</span>
                        <span className="text-gray-400 ml-2">
                          {(file.size / 1024).toFixed(1)} KB
                        </span>
                        {uploadProgress[file.name] && (
                          <span className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${
                            uploadProgress[file.name].includes('Success')
                              ? 'bg-green-100 text-green-800'
                              : uploadProgress[file.name].includes('Failed')
                              ? 'bg-red-100 text-red-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {uploadProgress[file.name]}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Upload Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={handleSingleUpload}
                  disabled={uploading || selectedFiles.length === 0}
                  className="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {uploading ? 'Uploading...' : 'Upload Single'}
                </button>
                <button
                  onClick={handleBulkUpload}
                  disabled={uploading || selectedFiles.length < 2}
                  className="flex-1 bg-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {uploading ? 'Uploading...' : `Bulk Upload (${selectedFiles.length})`}
                </button>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-1">Upload Tips</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Use "Upload Single" for one file at a time</li>
                      <li>Use "Bulk Upload" for multiple files (faster)</li>
                      <li>Files are automatically scanned for security issues</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Upload History */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload History</h2>

            {uploadHistory.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>No files uploaded yet</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {uploadHistory.map((file, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 truncate">{file.filename}</div>
                        <div className="text-sm text-gray-500 mt-1">
                          ID: {file.config_id}
                        </div>
                      </div>
                      <div className="ml-4 flex-shrink-0">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                          {file.detected_vendor}
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center text-xs text-gray-500">
                      <span>Confidence: {(file.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
