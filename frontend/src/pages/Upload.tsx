import { useState, useCallback } from 'react';
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadConfiguration } from '../services/api';
import { useNavigate } from 'react-router-dom';

const Upload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();
  
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  }, []);
  
  const handleFileSelection = (selectedFile: File) => {
    setError(null);
    setSuccess(false);
    
    // Validate file extension
    const allowedExtensions = ['.cfg', '.conf', '.txt', '.json'];
    const fileExtension = '.' + selectedFile.name.split('.').pop()?.toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
      setError(`Unsupported file type. Allowed: ${allowedExtensions.join(', ')}`);
      return;
    }
    
    // Validate file size (10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit');
      return;
    }
    
    setFile(selectedFile);
  };
  
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setError(null);
    
    try {
      const response = await uploadConfiguration(file);
      
      if (response.success) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/configurations');
        }, 2000);
      } else {
        setError(response.error?.message || 'Upload failed');
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      const errorMessage = err.response?.data?.detail?.error?.message 
        || err.response?.data?.error?.message 
        || err.message 
        || 'Upload failed. Please check console for details.';
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Upload Configuration</h1>
        <p className="text-gray-400">Upload network device configurations for security analysis</p>
      </div>
      
      {/* Upload Area */}
      <div className="card">
        <div
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-900/20'
              : 'border-gray-600 hover:border-gray-500'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {!file ? (
            <>
              <UploadIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-semibold mb-2">Drop configuration file here</h3>
              <p className="text-gray-400 mb-4">or click to browse</p>
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".cfg,.conf,.txt,.json"
                onChange={handleFileInput}
              />
              <label
                htmlFor="file-upload"
                className="btn-primary cursor-pointer inline-block"
              >
                Select File
              </label>
              <p className="text-sm text-gray-500 mt-4">
                Supported: .cfg, .conf, .txt, .json (Max 10MB)
              </p>
            </>
          ) : (
            <div className="space-y-4">
              <FileText className="w-16 h-16 mx-auto text-blue-400" />
              <div>
                <p className="text-lg font-semibold">{file.name}</p>
                <p className="text-sm text-gray-400">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <div className="flex justify-center space-x-4">
                <button
                  onClick={handleUpload}
                  disabled={uploading || success}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Uploading...' : success ? 'Uploaded!' : 'Upload'}
                </button>
                <button
                  onClick={() => {
                    setFile(null);
                    setError(null);
                    setSuccess(false);
                  }}
                  disabled={uploading}
                  className="btn-secondary disabled:opacity-50"
                >
                  Clear
                </button>
              </div>
            </div>
          )}
        </div>
        
        {/* Success Message */}
        {success && (
          <div className="mt-4 p-4 bg-green-900/30 border border-green-800 rounded-lg flex items-center space-x-3">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <div>
              <p className="text-green-400 font-medium">Configuration uploaded successfully!</p>
              <p className="text-sm text-gray-300">Redirecting to configurations...</p>
            </div>
          </div>
        )}
        
        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-red-900/30 border border-red-800 rounded-lg flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <p className="text-red-400">{error}</p>
          </div>
        )}
      </div>
      
      {/* Supported Vendors */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Supported Vendors</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-700/50 rounded-lg border border-gray-600">
            <h3 className="font-semibold mb-2">Cisco IOS/IOS-XE</h3>
            <p className="text-sm text-gray-400">
              Automatically detects and parses Cisco router and switch configurations
            </p>
          </div>
          <div className="p-4 bg-gray-700/50 rounded-lg border border-gray-600">
            <h3 className="font-semibold mb-2">Fortinet FortiGate</h3>
            <p className="text-sm text-gray-400">
              Supports FortiGate firewall configuration files
            </p>
          </div>
          <div className="p-4 bg-gray-700/50 rounded-lg border border-gray-600">
            <h3 className="font-semibold mb-2">Unknown Vendors</h3>
            <p className="text-sm text-gray-400">
              AI-assisted interpretation learns new configuration formats
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;
