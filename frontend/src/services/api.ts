/**
 * API service for communicating with backend
 */
import axios from 'axios';
import type { Configuration, Audit, Finding, DashboardSummary, LearnedMapping, ApiResponse } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add authentication token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle authentication errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear auth and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      
      // Only redirect if not already on login/register page
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Upload configuration file
export const uploadConfiguration = async (file: File): Promise<ApiResponse<Configuration>> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('Uploading file:', file.name, 'Size:', file.size);
    
    const response = await api.post('/config/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('Upload response:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Upload API error:', error);
    console.error('Error response:', error.response?.data);
    throw error;
  }
};

// List configurations
export const listConfigurations = async (): Promise<ApiResponse<{ configurations: Configuration[]; total: number }>> => {
  const response = await api.get('/configurations');
  return response.data;
};

// Get configuration details
export const getConfiguration = async (configId: string): Promise<ApiResponse<Configuration>> => {
  const response = await api.get(`/configurations/${configId}`);
  return response.data;
};

// Run audit
export const runAudit = async (configId: string): Promise<ApiResponse<Audit>> => {
  const response = await api.post(`/audits/${configId}/run`);
  return response.data;
};

// Get audit details
export const getAudit = async (auditId: string): Promise<ApiResponse<Audit>> => {
  const response = await api.get(`/audits/${auditId}`);
  return response.data;
};

// Get findings for audit
export const getFindings = async (auditId: string): Promise<ApiResponse<{ findings: Finding[] }>> => {
  const response = await api.get(`/audits/${auditId}/findings`);
  return response.data;
};

// Download audit report as PDF
export const downloadAuditReport = async (auditId: string): Promise<void> => {
  try {
    const response = await api.get(`/audits/${auditId}/report`, {
      responseType: 'blob', // Important: handle binary data
    });
    
    // Create blob from response
    const blob = new Blob([response.data], { type: 'application/pdf' });
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Extract filename from Content-Disposition header or use default
    const contentDisposition = response.headers['content-disposition'];
    let filename = `audit_report_${auditId}.pdf`;
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    console.error('Report download error:', error);
    throw error;
  }
};

// Get dashboard summary
export const getDashboardSummary = async (): Promise<ApiResponse<DashboardSummary>> => {
  const response = await api.get('/dashboard/summary');
  return response.data;
};

// Get pending AI mappings
export const getPendingMappings = async (): Promise<ApiResponse<{ pending_mappings: LearnedMapping[] }>> => {
  const response = await api.get('/learning/pending');
  return response.data;
};

// Accept AI mapping
export const acceptMapping = async (mappingData: any): Promise<ApiResponse<LearnedMapping>> => {
  const response = await api.post('/learning/mapping', mappingData);
  return response.data;
};

// Reject AI mapping
export const rejectMapping = async (mappingId: string): Promise<ApiResponse<void>> => {
  const response = await api.post(`/learning/mapping/${mappingId}/reject`);
  return response.data;
};

// Health check
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get('/health', { baseURL: '/' });
  return response.data;
};

export default api;
