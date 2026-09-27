import { useState, useCallback } from 'react';
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadConfiguration } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../contexts/ToastContext';
import BackButton from '../components/BackButton';

const Upload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();
  
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
        showSuccess(
          'Configuration Uploaded!',
          `${file.name} has been successfully uploaded and is ready for analysis.`
        );
        setTimeout(() => {
          navigate('/configurations');
        }, 2000);
      } else {
        const errorMsg = response.error?.message || 'Upload failed';
        setError(errorMsg);
        showError('Upload Failed', errorMsg);
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      const errorMessage = err.response?.data?.detail?.error?.message 
        || err.response?.data?.error?.message 
        || err.message 
        || 'Upload failed. Please try again.';
      setError(errorMessage);
      showError('Upload Failed', errorMessage);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto space-y-8 page-enter">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <BackButton to="/dashboard" label="Dashboard" />
          </div>
          <h1 className="text-3xl font-bold mb-2 text-neutral-900">Upload Configuration</h1>
          <p className="text-neutral-600">Upload network device configurations for security analysis</p>
        </div>
      </div>
      
      {/* Upload Area - GLASS EFFECT */}
      <div className="card-glass">
        <div
          className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
            dragActive
              ? 'border-brand-500/60 bg-brand-50/80 backdrop-blur-xl'
              : 'border-neutral-300/60 hover:border-neutral-400/60 bg-surface-secondary/50 backdrop-blur-xl'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {!file ? (
            <>
              <div className="p-4 bg-white/80 backdrop-blur-sm rounded-3xl inline-block mb-4 border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
                <UploadIcon className="w-12 h-12 text-brand-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-neutral-900">Drop configuration file here</h3>
              <p className="text-neutral-600 mb-6">or click to browse</p>
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
              <p className="text-sm text-neutral-500 mt-6">
                Supported: .cfg, .conf, .txt, .json (Max 10MB)
              </p>
            </>
          ) : (
            <div className="space-y-4">
              <div className="p-4 bg-white/80 backdrop-blur-sm rounded-3xl inline-block border border-white/60" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
                <FileText className="w-12 h-12 text-brand-600" />
              </div>
              <div>
                <p className="text-lg font-semibold text-neutral-900">{file.name}</p>
                <p className="text-sm text-neutral-600 mt-1">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <div className="flex justify-center space-x-4 pt-4">
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
        
        {/* Success Message - GLASS */}
        {success && (
          <div className="mt-4 p-4 bg-status-success-bg/80 backdrop-blur-xl border-2 border-status-success-border/60 rounded-2xl flex items-center space-x-3" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
            <CheckCircle className="w-5 h-5 text-status-success-text flex-shrink-0" />
            <div>
              <p className="text-status-success-text font-semibold">Configuration uploaded successfully!</p>
              <p className="text-sm text-neutral-700 mt-0.5">Redirecting to configurations...</p>
            </div>
          </div>
        )}
        
        {/* Error Message - GLASS */}
        {error && (
          <div className="mt-4 p-4 bg-status-critical-bg/80 backdrop-blur-xl border-2 border-status-critical-border/60 rounded-2xl flex items-start space-x-3" style={{ boxShadow: '0 4px 16px 0 rgba(0, 0, 0, 0.06)' }}>
            <AlertCircle className="w-5 h-5 text-status-critical-text flex-shrink-0 mt-0.5" />
            <p className="text-status-critical-text font-medium">{error}</p>
          </div>
        )}
      </div>
      
      {/* Supported Vendors */}
      <div className="card">
        <h2 className="text-xl font-bold mb-6 text-neutral-900">Supported Vendors</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-5 bg-surface-secondary rounded-xl border border-neutral-200 hover:border-brand-300 hover:shadow-md transition-all duration-200 hover:translate-y-[-1px] stagger-item">
            <h3 className="font-semibold mb-2 text-neutral-900">Cisco IOS/IOS-XE</h3>
            <p className="text-sm text-neutral-600 leading-relaxed">
              Automatically detects and parses Cisco router and switch configurations
            </p>
          </div>
          <div className="p-5 bg-surface-secondary rounded-xl border border-neutral-200 hover:border-brand-300 hover:shadow-md transition-all duration-200 hover:translate-y-[-1px] stagger-item">
            <h3 className="font-semibold mb-2 text-neutral-900">Fortinet FortiGate</h3>
            <p className="text-sm text-neutral-600 leading-relaxed">
              Supports FortiGate firewall configuration files
            </p>
          </div>
          <div className="p-5 bg-surface-secondary rounded-xl border border-neutral-200 hover:border-brand-300 hover:shadow-md transition-all duration-200 hover:translate-y-[-1px] stagger-item">
            <h3 className="font-semibold mb-2 text-neutral-900">Unknown Vendors</h3>
            <p className="text-sm text-neutral-600 leading-relaxed">
              AI-assisted interpretation learns new configuration formats
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;
