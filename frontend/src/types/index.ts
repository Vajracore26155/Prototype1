/**
 * TypeScript type definitions for SIH26155
 */

export interface Configuration {
  id: number;
  config_id: string;
  filename: string;
  file_type: string;
  status: 'UPLOADED' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'NEEDS_REVIEW';
  vendor?: string;
  vendor_confidence?: number;
  created_at: string;
}

export interface Audit {
  id: number;
  audit_id: string;
  configuration_id: number;
  configuration?: {
    config_id: string;
    filename: string;
    vendor: string;
  };
  status: 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'NEEDS_REVIEW';
  compliance_score?: number;
  risk_score?: number;
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  passed_count: number;
  failed_count: number;
  warning_count: number;
  started_at: string;
  completed_at?: string;
  // Human intervention metadata
  requires_human_review?: boolean;
  review_reason?: string;
  interpretation_confidence?: number;
  uninterpreted_lines?: number;
  total_lines?: number;
  pending_mappings?: number;
}

export interface Finding {
  id: number;
  finding_id: string;
  audit_id: number;
  rule_id: string;
  title: string;
  description?: string;
  status: 'PASS' | 'FAIL' | 'WARNING' | 'NOT_APPLICABLE' | 'UNKNOWN';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  expected?: string;
  actual?: string;
  field_path?: string;
  evidence_file?: string;
  evidence_line?: number;
  evidence_text?: string;
  evidence?: {
    file: string;
    line?: number;
    text: string;
  };
  risk_score?: number;
  remediation?: string;
  created_at: string;
}

export interface Evidence {
  file: string;
  line?: number;
  text: string;
}

export interface LearnedMapping {
  id: number;
  mapping_id: string;
  vendor: string;
  raw_pattern: string;
  normalized_field: string;
  value: string;
  suggested_meaning?: string;
  confidence: number;
  approved: boolean;
  created_at: string;
}

export interface DashboardSummary {
  total_configs: number;
  total_audits: number;
  compliance_score: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  passed_controls: number;
  vendor_distribution?: Record<string, number>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}
