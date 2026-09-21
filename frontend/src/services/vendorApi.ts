/**
 * Vendor API Service
 * Handles all vendor-related API calls
 */
import axios from 'axios';

const API_BASE_URL = '/api';

// Create a separate axios instance for vendor endpoints
const vendorApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Vendor authentication - uses session token instead of JWT
vendorApi.interceptors.request.use(
  (config) => {
    const vendorToken = localStorage.getItem('vendor_session_token');
    if (vendorToken && !config.url?.includes('/vendor/register') && !config.url?.includes('/vendor/request-otp') && !config.url?.includes('/vendor/verify-otp')) {
      config.headers['X-Vendor-Session-Token'] = vendorToken;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
vendorApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('vendor_session_token');
      localStorage.removeItem('vendor_info');
      if (window.location.pathname.includes('/vendor/')) {
        window.location.href = '/vendor/login';
      }
    }
    return Promise.reject(error);
  }
);

// Types
export interface VendorRegistration {
  email: string;
  company_name: string;
  contact_name: string;
  phone?: string;
  organization_id?: number;
}

export interface VendorOTPRequest {
  vendor_email: string;
}

export interface VendorOTPVerify {
  vendor_email: string;
  otp_code: string;
}

export interface VendorPasswordLogin {
  email: string;
  password: string;
}

export interface VendorSession {
  session_id: string;
  session_token: string;
  vendor_id: string;
  expires_at: string;
  valid_for_hours: number;
}

export interface VendorInfo {
  vendor_id: string;
  company: string;
  email: string;
  status: string;
}

export interface VendorUploadResponse {
  config_id: string;
  filename: string;
  detected_vendor: string;
  confidence: number;
  uploaded_by: {
    vendor_id: string;
    company: string;
  };
  session_info: {
    files_uploaded: number;
    expires_at: string;
  };
}

export interface VendorRequest {
  request_id: string;
  vendor_id: string;
  vendor_email: string;
  company_name: string;
  contact_name: string;
  phone?: string;
  status: string;
  requested_at: string;
  notes?: string;
}

export interface VendorActivityReport {
  vendors: {
    vendor_id: string;
    company: string;
    sessions_count: number;
    active_sessions: number;
    total_uploads: number;
    last_activity: string;
  }[];
  summary: {
    total_uploads: number;
    active_vendors: number;
  };
}

// ============================================================
// PUBLIC VENDOR ENDPOINTS
// ============================================================

/**
 * Register as a new vendor
 */
export const registerVendor = async (data: VendorRegistration) => {
  const response = await vendorApi.post('/vendor/register', data);
  return response.data;
};

/**
 * Request OTP code via email
 */
export const requestVendorOTP = async (data: VendorOTPRequest) => {
  const response = await vendorApi.post('/vendor/request-otp', data);
  return response.data;
};

/**
 * Verify OTP and get session token
 */
export const verifyVendorOTP = async (data: VendorOTPVerify) => {
  const response = await vendorApi.post('/vendor/verify-otp', data);
  
  if (response.data.success) {
    // Store session token
    localStorage.setItem('vendor_session_token', response.data.data.session_token);
    localStorage.setItem('vendor_info', JSON.stringify({
      vendor_id: response.data.data.vendor_id,
      expires_at: response.data.data.expires_at,
    }));
  }
  
  return response.data;
};

/**
 * Login with email and password
 */
export const vendorPasswordLogin = async (data: VendorPasswordLogin) => {
  const response = await vendorApi.post('/vendor/login', data);
  
  if (response.data.success) {
    // Store session token
    localStorage.setItem('vendor_session_token', response.data.data.session_token);
    localStorage.setItem('vendor_info', JSON.stringify({
      vendor_id: response.data.data.vendor_id,
      expires_at: response.data.data.expires_at,
    }));
  }
  
  return response.data;
};

// ============================================================
// AUTHENTICATED VENDOR ENDPOINTS
// ============================================================

/**
 * Upload configuration file
 */
export const uploadVendorConfiguration = async (file: File, deviceId?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  if (deviceId) {
    formData.append('device_id', deviceId);
  }
  
  const response = await vendorApi.post('/vendor/upload/configuration', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * Bulk upload configuration files
 */
export const uploadVendorBulk = async (files: File[]) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  
  const response = await vendorApi.post('/vendor/upload/bulk', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * Get current session info
 */
export const getVendorSession = async () => {
  const response = await vendorApi.get('/vendor/upload/session');
  return response.data;
};

/**
 * Get upload history
 */
export const getVendorUploadHistory = async () => {
  const response = await vendorApi.get('/vendor/upload/history');
  return response.data;
};

/**
 * Revoke current session (logout)
 */
export const revokeVendorSession = async () => {
  const response = await vendorApi.delete('/vendor/upload/session');
  
  // Clear local storage
  localStorage.removeItem('vendor_session_token');
  localStorage.removeItem('vendor_info');
  
  return response.data;
};

// ============================================================
// ADMIN VENDOR MANAGEMENT ENDPOINTS
// ============================================================

/**
 * Get pending vendor requests
 */
export const getVendorRequests = async (status = 'PENDING') => {
  const response = await axios.get(`${API_BASE_URL}/admin/vendor-requests`, {
    params: { status },
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
  });
  return response.data;
};

/**
 * Approve or reject vendor request
 */
export const decideVendorRequest = async (requestId: string, approved: boolean, notes?: string) => {
  const response = await axios.post(
    `${API_BASE_URL}/admin/vendor-requests/${requestId}/decide`,
    { approved, notes },
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    }
  );
  return response.data;
};

/**
 * Get all vendors
 */
export const getVendors = async (status?: string) => {
  const response = await axios.get(`${API_BASE_URL}/admin/vendors`, {
    params: status ? { status } : {},
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
  });
  return response.data;
};

/**
 * Get vendor activity report
 */
export const getVendorActivity = async (days = 30) => {
  const response = await axios.get(`${API_BASE_URL}/admin/vendor-activity`, {
    params: { days },
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
  });
  return response.data;
};

/**
 * Get active vendor sessions
 */
export const getVendorSessions = async () => {
  const response = await axios.get(`${API_BASE_URL}/admin/vendor-sessions`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
  });
  return response.data;
};

/**
 * Revoke vendor session (admin)
 */
export const revokeVendorSessionAdmin = async (sessionId: string) => {
  const response = await axios.post(
    `${API_BASE_URL}/admin/vendor-sessions/${sessionId}/revoke`,
    {},
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    }
  );
  return response.data;
};

/**
 * Suspend vendor
 */
export const suspendVendor = async (vendorId: string) => {
  const response = await axios.patch(
    `${API_BASE_URL}/admin/vendors/${vendorId}/suspend`,
    {},
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    }
  );
  return response.data;
};

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

/**
 * Check if vendor is logged in
 */
export const isVendorLoggedIn = (): boolean => {
  const token = localStorage.getItem('vendor_session_token');
  const info = localStorage.getItem('vendor_info');
  
  if (!token || !info) return false;
  
  try {
    const vendorInfo = JSON.parse(info);
    const expiresAt = new Date(vendorInfo.expires_at);
    return expiresAt > new Date();
  } catch {
    return false;
  }
};

/**
 * Get vendor info from storage
 */
export const getVendorInfo = (): VendorInfo | null => {
  try {
    const info = localStorage.getItem('vendor_info');
    return info ? JSON.parse(info) : null;
  } catch {
    return null;
  }
};

export default vendorApi;
