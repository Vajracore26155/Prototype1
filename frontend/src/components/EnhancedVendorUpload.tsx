import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle, X, Play, Pause } from 'lucide-react';

interface UploadFile {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  error?: string;
  result?: any;
}

const EnhancedVendorUpload: React.FC = () => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadType, setUploadType] = useState<'single' | 'bulk'>('single');
  
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
    
    try {
      if (uploadType === 'single') {
        for (const fileItem of files) {
          await uploadSingleFile(fileItem);
        }
      } else {
        await uploadBulkFiles(files);
      }
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
          'Authorization': `Bearer ${localStorage.getItem('token')}`
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
          'Authorization': `Bearer ${localStorage.getItem('token')}`
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
      {/* Upload Type Selection */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold mb-4">Upload Configuration Files</h3>
        
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setUploadType('single')}
            className={`px-4 py-2 rounded-md ${
              uploadType === 'single'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Single File Upload
          </button>
          <button
            onClick={() => setUploadType('bulk')}
            className={`px-4 py-2 rounded-md ${
              uploadType === 'bulk'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Bulk Upload
          </button>
        </div>

        {/* Drop Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          {isDragActive ? (
            <p className="text-blue-600 font-medium">Drop files here...</p>
          ) : (
            <div>
              <p className="text-gray-600 mb-2">
                Drag and drop configuration files here, or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supports: .txt, .cfg, .conf, .json, .xml, .yaml, .yml (max 10MB)
              </p>
            </div>
          )}
        </div>
      </div>
      {/* File List */}
      {files.length > 0 && (
        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b bg-gray-50">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">
                Selected Files ({files.length})
              </h4>
              <button
                onClick={() => setFiles([])}
                className="text-gray-500 hover:text-gray-700"
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
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-2">
                Ready to upload {files.length} file(s)
              </p>
              {uploadType === 'bulk' && files.length > 5 && (
                <p className="text-sm text-amber-600">
                  ⚠️ Bulk upload with 5+ files will generate an overall configuration
                </p>
              )}
            </div>
            
            <button
              onClick={handleUpload}
              disabled={isUploading || files.length === 0}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
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
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'uploading':
      case 'processing':
        return <div className="h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <FileText className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (fileItem.status) {
      case 'completed':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'uploading':
      case 'processing':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <div>
            <p className="font-medium text-gray-900">{fileItem.file.name}</p>
            <p className="text-sm text-gray-500">
              {(fileItem.file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {fileItem.status.charAt(0).toUpperCase() + fileItem.status.slice(1)}
          </span>
          {!disabled && fileItem.status === 'pending' && (
            <button
              onClick={onRemove}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {fileItem.status === 'uploading' || fileItem.status === 'processing' ? (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${fileItem.progress}%` }}
          />
        </div>
      ) : null}

      {/* Error Message */}
      {fileItem.error && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-700">{fileItem.error}</p>
        </div>
      )}

      {/* Success Result */}
      {fileItem.result && fileItem.status === 'completed' && (
        <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-700">
            ✅ Upload successful - Configuration created: {fileItem.result.configuration_id}
          </p>
          {fileItem.result.audit_id && (
            <p className="text-sm text-green-600 mt-1">
              🔍 Security audit initiated: {fileItem.result.audit_id}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default EnhancedVendorUpload;