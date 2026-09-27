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
      // Set the session token header properly
      (config.headers as any)['X-Vendor-Session-Token'] = vendorToken;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
vendorApi.interceptors.response.use(
  (response) => {
    // Any write invalidates the GET cache so later reads stay fresh
    const m = (response.config?.method || 'get').toLowerCase();
    if (m !== 'get') clearVendorCache();
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('vendor_session_token');
      localStorage.removeItem('vendor_info');
      if (window.location.pathname.includes('/vendor/')) {
        window.location.href = '/vendor/login';
      }
    }
    // Don't hammer a rate-limited backend: surface a friendly message
    if (error.response?.status === 429) {
      error.message = 'Too many requests — please wait a few seconds and try again.';
    }
    return Promise.reject(error);
  }
);

// Short-lived GET cache (30s) to absorb tab remounts + parallel fans
const __getCache = new Map<string, { t: number; data: any }>();
const CACHE_TTL_MS = 30_000;
export function clearVendorCache() {
  __getCache.clear();
}
async function cachedGet<T = any>(key: string, fetcher: () => Promise<{ data: T }>): Promise<{ data: T }> {
  const hit = __getCache.get(key);
  if (hit && Date.now() - hit.t < CACHE_TTL_MS) {
    return { data: hit.data as T };
  }
  const res = await fetcher();
  __getCache.set(key, { t: Date.now(), data: res.data });
  return { data: res.data };
}

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
  const response = await cachedGet<any>('GET:/vendor/upload/session', () => vendorApi.get('/vendor/upload/session'));
  return response.data;
};

/**
 * Get upload history
 */
export const getVendorUploadHistory = async () => {
  const response = await cachedGet<any>('GET:/vendor/upload/history', () => vendorApi.get('/vendor/upload/history'));
  return response.data;
};

/**
 * Get vendor configurations
 */
export const getVendorConfigurations = async () => {
  const response = await cachedGet<any>('GET:/vendor/configurations', () => vendorApi.get('/vendor/configurations'));
  return response.data;
};

/**
 * Get vendor audits
 */
export const getVendorAudits = async () => {
  const response = await cachedGet<any>('GET:/vendor/audits', () => vendorApi.get('/vendor/audits'));
  return response.data;
};

/**
 * Run audit on configuration
 */
export const runVendorAudit = async (configId: string) => {
  const response = await vendorApi.post(`/vendor/audit/${configId}`);
  return response.data;
};

/**
 * Get audit details (legacy function, now redirects to enhanced version)
 */
export const getVendorAudit = async (auditId: string): Promise<{ success: boolean; data?: any; error?: string }> => {
  // Use enhanced version but return simplified format for backward compatibility
  try {
    const enhanced = await getVendorAuditEnhanced(auditId);
    if (!enhanced.success || !enhanced.data) {
      return enhanced;
    }

    // Convert enhanced format to legacy format safely
    const dataAny = enhanced.data as any;
    const summary = dataAny.audit_summary || {};
    const parsing = dataAny.parsing_analysis || {};
    const findingsObj = dataAny.findings || {};
    const rawFindings: any[] = findingsObj.details || (Array.isArray(dataAny.findings) ? dataAny.findings : []);

    // Normalize findings to UI shape (rule_name/title, severity, category, evidence string, recommendation)
    const normalized = (rawFindings || []).map((f: any) => {
      const ev = f.evidence;
      const evStr = typeof ev === 'string' ? ev : (ev?.evidence_text || f.evidence_text || '');
      const rec = f.recommendation || f.remediation?.guidance || (typeof f.remediation === 'string' ? f.remediation : '') || '';
      return {
        finding_id: f.finding_id || `${f.rule_id || 'FND'}-${Math.random().toString(36).slice(2, 8)}`,
        rule_id: f.rule_id || 'N/A',
        rule_name: f.rule_name || f.title || f.rule_id || 'Finding',
        title: f.title || f.rule_name || f.rule_id || 'Finding',
        severity: (f.severity || 'LOW').toString(),
        category: f.category || (f.rule_id && f.rule_id.includes('-') ? f.rule_id.split('-')[0] : 'General'),
        description: f.description || '',
        evidence: evStr,
        evidence_file: ev?.evidence_file || f.evidence_file || '',
        evidence_line: ev?.evidence_line || f.evidence_line || null,
        evidence_text: evStr,
        recommendation: rec,
        remediation: rec,
        status: f.status || 'UNKNOWN',
        confidence_score: f.confidence_score ?? 0.95,
      };
    });

    const passed = summary.passed_count ?? dataAny.passed_count ?? findingsObj.summary?.by_status?.pass ?? normalized.filter(x => x.status === 'PASS').length;
    const failed = summary.failed_count ?? dataAny.failed_count ?? findingsObj.summary?.by_status?.fail ?? normalized.filter(x => x.status === 'FAIL').length;
    const warnings = summary.warning_count ?? dataAny.warning_count ?? findingsObj.summary?.by_status?.warning ?? normalized.filter(x => x.status === 'WARNING').length;

    const legacyData = {
      audit_id: dataAny.audit_id || auditId,
      configuration: dataAny.configuration || {},
      status: summary.status || dataAny.status || 'COMPLETED',
      compliance_score: summary.compliance_score ?? dataAny.compliance_score ?? 0,
      risk_score: summary.risk_score ?? dataAny.risk_score ?? 0,
      risk_level: summary.risk_level || dataAny.risk_level || 'MEDIUM',
      passed_count: passed,
      failed_count: failed,
      warning_count: warnings,
      started_at: summary.started_at || dataAny.started_at || new Date().toISOString(),
      completed_at: summary.completed_at || dataAny.completed_at,
      requires_human_review: parsing.requires_human_review ?? dataAny.requires_human_review ?? false,
      review_reason: parsing.review_reason || dataAny.review_reason || '',
      interpretation_confidence: parsing.interpretation_confidence ?? dataAny.interpretation_confidence ?? 0.95,
      findings: normalized,
      findings_summary: findingsObj.summary || dataAny.findings_summary || {}
    };

    return {
      success: true,
      data: legacyData
    };
  } catch (error) {
    console.error('Error in legacy getVendorAudit:', error);
    return {
      success: false,
      error: 'Failed to fetch audit details'
    };
  }
};

/**
 * Get findings for vendor audit (vendor-scoped, uses session token)
 */
export const getVendorAuditFindings = async (auditId: string): Promise<{ success: boolean; data?: any; error?: string }> => {
  try {
    const response = await cachedGet(`GET:/vendor/audit/${auditId}/findings`, () => vendorApi.get(`/vendor/audit/${auditId}/findings`));
    return response.data;
  } catch (error) {
    console.error('Error fetching vendor audit findings:', error);
    return { success: false, error: 'Failed to fetch findings' };
  }
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
    params: { 
      status,
      _t: Date.now()  // Cache busting parameter
    },
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache'
    },
  });
  return response.data;
};

/**
 * Approve or reject vendor request
 */
export const decideVendorRequest = async (requestId: string, approved: boolean, notes?: string) => {
  const endpoint = approved ? 'approve' : 'reject';
  const response = await axios.post(
    `${API_BASE_URL}/admin/vendor-requests/${requestId}/${endpoint}`,
    { notes },
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
// Enhanced configuration detail interface
export interface ConfigurationDetails {
  config_id: string;
  filename: string;
  internal_filename: string;
  file_type: string;
  status: string;
  vendor_detection: {
    detected_vendor: string;
    confidence: number;
  };
  file_integrity: {
    sha256_hash: string;
    storage_path: string | null;
    sanitized_path: string | null;
  };
  file_content: {
    preview: string;
    stats: {
      total_lines: number;
      preview_lines: number;
      file_size_bytes: number;
    };
  };
  upload_metadata: {
    uploaded_by: string;
    uploaded_at: string;
    organization_id: number;
  };
  audits: AuditSummary[];
  processing_status: {
    ingested: boolean;
    vendor_detected: boolean;
    audited: boolean;
    latest_audit: AuditSummary | null;
  };
}

// Enhanced audit detail interface
export interface EnhancedAuditDetails {
  audit_id: string;
  configuration: {
    config_id: string;
    filename: string;
    vendor: string;
    vendor_confidence: number;
    file_hash: string;
  };
  audit_summary: {
    status: string;
    compliance_score: number;
    risk_score: number;
    risk_level: string;
    started_at: string;
    completed_at?: string;
    duration_seconds?: number;
    error_message?: string;
  };
  parsing_analysis: {
    interpretation_confidence: number;
    total_config_lines: number;
    successfully_interpreted: number;
    uninterpreted_lines: number;
    interpretation_rate: number;
    pending_ai_mappings: number;
    requires_human_review: boolean;
    review_reason?: string;
    normalized_data_available: boolean;
  };
  risk_assessment: {
    overall_risk_score: number;
    risk_level: string;
    risk_breakdown: {
      security_posture: number;
      compliance_gap: string;
      configuration_complexity: string;
    };
    business_risk_factors: string[];
  };
  device_assessment: {
    security_posture: string;
    configuration_quality: string;
    vendor_best_practices: string;
    maintenance_recommendations: string[];
  };
  findings: {
    total_count: number;
    summary: {
      by_severity: {
        critical: number;
        high: number;
        medium: number;
        low: number;
      };
      by_status: {
        pass: number;
        fail: number;
        warning: number;
        unknown: number;
      };
    };
    details: EnhancedFinding[];
  };
  evidence_and_provenance: {
    evidence_files_analyzed: number;
    configuration_lines_referenced: number;
    total_evidence_entries: number;
  };
  remediation_guidance: {
    priority_1_critical: EnhancedFinding[];
    priority_2_important: EnhancedFinding[];
    priority_3_maintenance: EnhancedFinding[];
    estimated_total_effort: string;
  };
}

export interface EnhancedFinding {
  finding_id: string;
  rule_id: string;
  rule_name: string;
  description: string;
  severity: string;
  status: string;
  technical_details: {
    expected: string;
    actual: string;
    field_path: string;
    risk_score: number;
  };
  evidence: {
    evidence_file: string;
    evidence_line: number;
    evidence_text: string;
    configuration_context: string[];
  };
  remediation: {
    guidance: string;
    priority: number;
    estimated_effort: string;
    business_impact: string;
  };
  compliance_mapping: {
    frameworks: string[];
    standards: string[];
  };
  created_at: string;
}

export interface AuditSummary {
  audit_id: string;
  status: string;
  compliance_score: number;
  risk_score: number;
  risk_level: string;
  started_at: string;
  completed_at?: string;
  requires_human_review: boolean;
  interpretation_confidence: number;
  parsing_stats: {
    total_lines: number;
    uninterpreted_lines: number;
    interpretation_rate: number;
    pending_mappings: number;
  };
  review_reason?: string;
  findings_count: {
    total: number;
    passed: number;
    failed: number;
    warnings: number;
  };
}

// Enhanced API functions
export const getVendorConfigurationDetails = async (configId: string): Promise<{ success: boolean; data?: ConfigurationDetails; error?: string }> => {
  try {
    const response = await cachedGet(`GET:/vendor/configuration/${configId}`, () => vendorApi.get(`/vendor/configuration/${configId}`));
    return response.data;
  } catch (error) {
    console.error('Error fetching configuration details:', error);
    return {
      success: false,
      error: 'Failed to fetch configuration details'
    };
  }
};

export const getVendorAuditEnhanced = async (auditId: string): Promise<{ success: boolean; data?: EnhancedAuditDetails; error?: string }> => {
  try {
    const response = await cachedGet(`GET:/vendor/audit/${auditId}`, () => vendorApi.get(`/vendor/audit/${auditId}`));
    return response.data;
  } catch (error) {
    console.error('Error fetching enhanced audit details:', error);
    return {
      success: false,
      error: 'Failed to fetch enhanced audit details'
    };
  }
};

export const downloadVendorAuditReportEnhanced = async (auditId: string): Promise<void> => {
  try {
    const token = localStorage.getItem('vendor_session_token');
    const response = await vendorApi.get(`/vendor/audit/${auditId}/report`, {
      headers: {
        'X-Vendor-Session-Token': token
      },
      responseType: 'blob'
    });

    const contentType = (response.headers['content-type'] || '') as string;
    // Backend returns JSON on error even with blob responseType -> detect and throw readable error
    if (contentType.includes('application/json')) {
      const text = await (response.data as Blob).text();
      try {
        const j = JSON.parse(text);
        throw new Error(j?.detail?.error?.message || j?.message || 'Failed to generate PDF report');
      } catch (e: any) {
        if (e?.message && !e.message.includes('Unexpected')) throw e;
        throw new Error('Failed to generate PDF report');
      }
    }
    if ((response.data as Blob)?.size === 0) {
      throw new Error('Empty PDF received from server');
    }
    
    // Create blob and download
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    
    // Extract filename from response headers if available
    const contentDisposition = response.headers['content-disposition'];
    let filename = `audit_report_${auditId}.pdf`;
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error downloading enhanced audit report:', error);
    throw error;
  }
};

// Legacy function for backward compatibility
export const downloadVendorAuditReport = downloadVendorAuditReportEnhanced;

// Enhanced Analytics API functions
export const getVendorAnalyticsOverview = async (timeframe: string = '30d'): Promise<{ success: boolean; data?: any; error?: string }> => {
  try {
    const response = await cachedGet(`GET:/vendor/analytics/overview?timeframe=${timeframe}`, () => vendorApi.get(`/vendor/analytics/overview?timeframe=${timeframe}`));
    return response.data;
  } catch (error) {
    console.error('Error fetching analytics overview:', error);
    return {
      success: false,
      error: 'Failed to fetch analytics overview'
    };
  }
};

export const getVendorComplianceTrends = async (timeframe: string = '30d'): Promise<{ success: boolean; data?: any; error?: string }> => {
  try {
    const response = await cachedGet(`GET:/vendor/analytics/trends?timeframe=${timeframe}`, () => vendorApi.get(`/vendor/analytics/trends?timeframe=${timeframe}`));
    return response.data;
  } catch (error) {
    console.error('Error fetching compliance trends:', error);
    return {
      success: false,
      error: 'Failed to fetch compliance trends'
    };
  }
};

export const getVendorRiskDistribution = async (): Promise<{ success: boolean; data?: any; error?: string }> => {
  try {
    const response = await cachedGet<any>('GET:/vendor/analytics/risk-distribution', () => vendorApi.get('/vendor/analytics/risk-distribution'));
    return response.data;
  } catch (error) {
    console.error('Error fetching risk distribution:', error);
    return {
      success: false,
      error: 'Failed to fetch risk distribution'
    };
  }
};

export const getVendorFindingCategories = async (): Promise<{ success: boolean; data?: any; error?: string }> => {
  try {
    const response = await cachedGet<any>('GET:/vendor/analytics/categories', () => vendorApi.get('/vendor/analytics/categories'));
    return response.data;
  } catch (error) {
    console.error('Error fetching finding categories:', error);
    return {
      success: false,
      error: 'Failed to fetch finding categories'
    };
  }
};