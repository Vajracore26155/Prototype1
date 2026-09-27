import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle, X, Play, Pause, ArrowRight, Check } from 'lucide-react';

interface UploadFile {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  error?: string;
  result?: any;
}

interface EnhancedVendorUploadProps {
  onUploadComplete?: () => void;
}

const EnhancedVendorUpload: React.FC<EnhancedVendorUploadProps> = ({ onUploadComplete }) => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadType, setUploadType] = useState<'single' | 'bulk'>('single');
  const [redirectNotice, setRedirectNotice] = useState<string | null>(null);
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending' as const,
      progress: 0
    }));
    
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt', '.cfg', '.conf'],
      'application/json': ['.json'],
      'text/xml': ['.xml'],
      'text/yaml': ['.yaml', '.yml']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const handleUpload = async () => {
    setIsUploading(true);
    setRedirectNotice(null);
    
    try {
      if (uploadType === 'single') {
        for (const fileItem of files) {
          await uploadSingleFile(fileItem);
        }
      } else {
        await uploadBulkFiles(files);
      }
      
      setRedirectNotice('Configuration uploaded successfully! Redirecting to Configurations...');
      setTimeout(() => {
        if (onUploadComplete) {
          onUploadComplete();
        } else {
          navigate('/vendor/configurations');
        }
      }, 1200);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const uploadSingleFile = async (fileItem: UploadFile) => {
    const formData = new FormData();
    formData.append('file', fileItem.file);
    
    try {
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      ));

      const response = await fetch('/api/vendor/enhanced-upload', {
        method: 'POST',
        headers: {
          'X-Vendor-Session-Token': `${localStorage.getItem('vendor_session_token') || ''}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      const result = await response.json();
      
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'completed', progress: 100, result }
          : f
      ));

    } catch (error) {
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'error', error: (error as Error).message }
          : f
      ));
    }
  };
  const uploadBulkFiles = async (fileItems: UploadFile[]) => {
    const formData = new FormData();
    fileItems.forEach(item => {
      formData.append('files', item.file);
    });

    try {
      setFiles(prev => prev.map(f => 
        ({ ...f, status: 'uploading', progress: 0 })
      ));

      const response = await fetch('/api/vendor/enhanced-bulk-upload', {
        method: 'POST',
        headers: {
          'X-Vendor-Session-Token': `${localStorage.getItem('vendor_session_token') || ''}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Bulk upload failed');
      }

      const result = await response.json();
      
      setFiles(prev => prev.map(f => 
        ({ ...f, status: 'completed', progress: 100, result })
      ));

    } catch (error) {
      setFiles(prev => prev.map(f => 
        ({ ...f, status: 'error', error: (error as Error).message })
      ));
    }
  };

  return (
    <div className="space-y-6">
      {redirectNotice && (
        <div className="bg-ink-950 text-white px-5 py-4 rounded-2xl shadow-sm flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-5 h-5" />
            <span className="font-bold text-sm">{redirectNotice}</span>
          </div>
          <ArrowRight className="w-5 h-5 animate-pulse" />
        </div>
      )}
      {/* Upload Type Selection */}
      <div className="tatva-card p-7">
        <div className="text-xs font-bold tracking-[0.24em] text-ink-500">UPLOAD MODE</div>
        <h3 className="text-2xl font-bold tracking-tight text-ink-900 mt-1">Upload Configuration Files</h3>

        <div className="flex gap-3 mt-5 mb-6">
          <button
            onClick={() => setUploadType('single')}
            className={`px-5 py-2.5 rounded-xl text-sm font-bold ${
              uploadType === 'single'
                ? 'bg-ink-950 text-white'
                : 'bg-mist-100 text-ink-500 hover:text-ink-950'
            }`}
          >
            Single File Upload
          </button>
          <button
            onClick={() => setUploadType('bulk')}
            className={`px-5 py-2.5 rounded-xl text-sm font-bold ${
              uploadType === 'bulk'
                ? 'bg-ink-950 text-white'
                : 'bg-mist-100 text-ink-500 hover:text-ink-950'
            }`}
          >
            Bulk Upload
          </button>
        </div>

        {/* Drop Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-ink-950 bg-mist-100'
              : 'border-line hover:border-ink-950'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-ink-950 mb-4" />
          {isDragActive ? (
            <p className="text-ink-950 font-bold">Drop files here...</p>
          ) : (
            <div>
              <p className="font-bold text-ink-900 mb-2 text-lg">
                Drag and drop configuration files here, or click to browse
              </p>
              <p className="text-sm font-semibold text-ink-500">
                Supports: .txt, .cfg, .conf, .json, .xml, .yaml, .yml (max 10MB)
              </p>
            </div>
          )}
        </div>
      </div>
      {/* File List */}
      {files.length > 0 && (
        <div className="tatva-card">
          <div className="p-5 border-b border-line bg-mist-50 rounded-t-2xl">
            <div className="flex items-center justify-between">
              <h4 className="font-bold text-ink-900">
                Selected Files ({files.length})
              </h4>
              <button
                onClick={() => setFiles([])}
                className="text-ink-500 hover:text-ink-950 font-bold text-sm"
                disabled={isUploading}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
          
          <div className="divide-y">
            {files.map(fileItem => (
              <FileUploadItem
                key={fileItem.id}
                fileItem={fileItem}
                onRemove={() => {
                  setFiles(prev => prev.filter(f => f.id !== fileItem.id));
                }}
                disabled={isUploading}
              />
            ))}
          </div>
        </div>
      )}

      {/* Upload Controls */}
      {files.length > 0 && (
        <div className="tatva-card p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-bold text-ink-900 mb-1">
                Ready to upload {files.length} file(s)
              </p>
              {uploadType === 'bulk' && files.length > 5 && (
                <p className="text-sm font-bold text-ink-900">
                  Bulk upload with 5+ files will generate an overall configuration
                </p>
              )}
            </div>

            <button
              onClick={handleUpload}
              disabled={isUploading || files.length === 0}
              className="btn-ink px-8 py-3.5 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isUploading ? (
                <>
                  <Pause className="h-4 w-4 animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  <span>Start Upload</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
// File Upload Item Component
interface FileUploadItemProps {
  fileItem: UploadFile;
  onRemove: () => void;
  disabled: boolean;
}

const FileUploadItem: React.FC<FileUploadItemProps> = ({ fileItem, onRemove, disabled }) => {
  const getStatusIcon = () => {
    switch (fileItem.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-ink-950" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-ink-950" />;
      case 'uploading':
      case 'processing':
        return <div className="h-5 w-5 border-2 border-ink-950 border-t-transparent rounded-full animate-spin" />;
      default:
        return <FileText className="h-5 w-5 text-ink-500" />;
    }
  };

  const getStatusColor = () => {
    switch (fileItem.status) {
      case 'completed':
        return 'text-ink-950';
      case 'error':
        return 'text-ink-950';
      case 'uploading':
      case 'processing':
        return 'text-ink-900';
      default:
        return 'text-ink-500';
    }
  };

  return (
    <div className="p-5">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <div>
            <p className="font-bold text-ink-900">{fileItem.file.name}</p>
            <p className="text-sm font-semibold text-ink-500">
              {(fileItem.file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <span className={`text-sm font-bold ${getStatusColor()}`}>
            {fileItem.status.charAt(0).toUpperCase() + fileItem.status.slice(1)}
          </span>
          {!disabled && fileItem.status === 'pending' && (
            <button
              onClick={onRemove}
              className="text-ink-500 hover:text-ink-950"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {fileItem.status === 'uploading' || fileItem.status === 'processing' ? (
        <div className="w-full bg-mist-200 rounded-full h-2">
          <div
            className="bg-ink-950 h-2 rounded-full transition-all duration-300"
            style={{ width: `${fileItem.progress}%` }}
          />
        </div>
      ) : null}

      {/* Error Message */}
      {fileItem.error && (
        <div className="mt-2 p-3 bg-mist-100 border border-ink-950 rounded-xl">
          <p className="text-sm font-bold text-ink-950">{fileItem.error}</p>
        </div>
      )}

      {/* Success Result */}
      {fileItem.result && fileItem.status === 'completed' && (
        <div className="mt-2 p-3 bg-ink-950 text-white rounded-xl">
          <p className="text-sm font-bold">
            Upload successful — Configuration created: {fileItem.result.configuration_id}
          </p>
          {fileItem.result.audit_id && (
            <p className="text-sm font-semibold text-white/70 mt-1">
              Security audit initiated: {fileItem.result.audit_id}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default EnhancedVendorUpload;