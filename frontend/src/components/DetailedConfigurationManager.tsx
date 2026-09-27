import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, Eye, Download, Search,
  CheckCircle, Upload, ChevronDown, ChevronRight,
  Database, Activity, X, ArrowRight, RefreshCw
} from 'lucide-react';
import {
  getVendorConfigurations,
  getVendorAudits,
  getVendorAuditEnhanced,
  downloadVendorAuditReport,
  getVendorConfigurationDetails
} from '../services/vendorApi';

interface DetailedConfiguration {
  config_id: string;
  filename: string;
  file_type: string;
  status: string;
  vendor: string;
  vendor_confidence: number;
  created_at: string;
  file_size?: number;
  audit_summary?: {
    audit_id?: string;
    compliance_score: number;
    risk_level: string;
    critical_findings: number;
    high_findings: number;
    medium_findings: number;
    low_findings: number;
  };
}

const DetailedConfigurationManager: React.FC = () => {
  const navigate = useNavigate();
  const [configurations, setConfigurations] = useState<DetailedConfiguration[]>([]);
  const [filteredConfigs, setFilteredConfigs] = useState<DetailedConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [vendorFilter, setVendorFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');
  const [expandedConfigs, setExpandedConfigs] = useState<Set<string>>(new Set());

  const [selectedConfig, setSelectedConfig] = useState<DetailedConfiguration | null>(null);
  const [detailTab, setDetailTab] = useState<'findings' | 'overview' | 'metadata'>('findings');
  const [detailFindings, setDetailFindings] = useState<any[]>([]);
  const [detailMeta, setDetailMeta] = useState<any>(null);
  const [downloadingAuditId, setDownloadingAuditId] = useState<string | null>(null);
  const [downloadStatusMsg, setDownloadStatusMsg] = useState<string | null>(null);

  useEffect(() => { loadConfigurations(); }, []);

  useEffect(() => { applyFilters(); }, [configurations, searchTerm, statusFilter, vendorFilter, riskFilter]);

  const loadConfigurations = async () => {
    setLoading(true);
    try {
      const [configRes, auditRes] = await Promise.all([getVendorConfigurations(), getVendorAudits()]);
      const auditsList: any[] = auditRes.success ? (auditRes.data?.audits || []) : [];
      const list: DetailedConfiguration[] = [];

      if (configRes.success && configRes.data?.configurations) {
        for (const c of configRes.data.configurations as any[]) {
          const matched = auditsList.find((a: any) => a.configuration?.config_id === c.config_id);
          let sev = { critical: 0, high: 0, medium: 0, low: 0 };
          let compliance = matched?.compliance_score ?? 0;
          let risk = matched?.risk_level || 'UNKNOWN';
          if (matched?.audit_id) {
            try {
              const enh: any = await getVendorAuditEnhanced(matched.audit_id);
              const s = enh?.data?.findings?.summary?.by_severity || {};
              sev = {
                critical: Number(s.critical || 0),
                high: Number(s.high || 0),
                medium: Number(s.medium || 0),
                low: Number(s.low || 0),
              };
              compliance = enh?.data?.audit_summary?.compliance_score ?? compliance;
              risk = enh?.data?.audit_summary?.risk_level || risk;
            } catch { /* keep list-level values */ }
          }
          list.push({
            config_id: c.config_id,
            filename: c.filename || 'device_configuration.conf',
            file_type: c.file_type || '',
            status: c.status || 'UPLOADED',
            vendor: c.vendor || 'Unknown',
            vendor_confidence: c.vendor_confidence ?? 0,
            created_at: c.created_at || new Date().toISOString(),
            file_size: c.file_size ?? undefined,
            audit_summary: matched ? {
              audit_id: matched.audit_id,
              compliance_score: Number(compliance || 0),
              risk_level: risk,
              critical_findings: sev.critical,
              high_findings: sev.high,
              medium_findings: sev.medium,
              low_findings: sev.low,
            } : undefined,
          });
        }
      }
      setConfigurations(list);
    } catch (error) {
      console.error('Failed to load configurations:', error);
      setConfigurations([]);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...configurations];
    if (searchTerm) {
      filtered = filtered.filter(config =>
        config.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        config.config_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        config.vendor.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (statusFilter !== 'all') filtered = filtered.filter(config => config.status.toLowerCase() === statusFilter.toLowerCase());
    if (vendorFilter !== 'all') filtered = filtered.filter(config => config.vendor.toLowerCase() === vendorFilter.toLowerCase());
    if (riskFilter !== 'all') filtered = filtered.filter(config => config.audit_summary?.risk_level.toLowerCase() === riskFilter.toLowerCase());
    setFilteredConfigs(filtered);
  };

  const toggleExpand = (configId: string) => {
    setExpandedConfigs(prev => {
      const next = new Set(prev);
      if (next.has(configId)) next.delete(configId);
      else next.add(configId);
      return next;
    });
  };

  const handleViewDetails = async (config: DetailedConfiguration) => {
    setSelectedConfig(config);
    setDetailTab('findings');
    setDetailFindings([]);
    setDetailMeta(null);
    try {
      const [det, enh] = await Promise.all([
        getVendorConfigurationDetails(config.config_id).catch(() => null),
        config.audit_summary?.audit_id ? getVendorAuditEnhanced(config.audit_summary.audit_id).catch(() => null) : Promise.resolve(null),
      ]);
      if (det?.success) setDetailMeta(det.data);
      const details = (enh as any)?.data?.findings?.details || [];
      setDetailFindings(details);
    } catch { /* modal still shows header */ }
  };

  const handleDownloadReport = async (auditId: string) => {
    if (!auditId) return;
    setDownloadingAuditId(auditId);
    setDownloadStatusMsg('Generating compliance report…');
    try {
      await downloadVendorAuditReport(auditId);
      setDownloadStatusMsg('Report downloaded successfully!');
      setTimeout(() => setDownloadStatusMsg(null), 3000);
    } catch (err: any) {
      setDownloadStatusMsg(err?.message || 'Failed to download report. Please try again.');
      setTimeout(() => setDownloadStatusMsg(null), 4000);
    } finally {
      setDownloadingAuditId(null);
    }
  };

  const sevBar = (v: number, max: number) => (
    <div className="h-1.5 bg-mist-200 rounded-full mt-2 overflow-hidden">
      <div className="h-full bg-ink-950 rounded-full" style={{ width: `${max > 0 ? Math.min(100, (v / max) * 100) : 0}%` }} />
    </div>
  );

  return (
    <div className="space-y-6">
      {downloadStatusMsg && (
        <div className="fixed bottom-6 right-6 z-50 bg-ink-950 text-white px-5 py-3 rounded-xl shadow-2xl flex items-center space-x-3">
          <CheckCircle className="w-5 h-5" />
          <span className="text-sm font-bold">{downloadStatusMsg}</span>
        </div>
      )}

      {/* Filter toolbar — reference style */}
      <div className="tatva-card p-4 sm:p-5">
        <div className="flex flex-col xl:flex-row gap-3">
          <button onClick={() => navigate('/vendor/upload')} className="btn-ink px-6 py-3 rounded-xl text-sm font-bold flex items-center gap-2 shrink-0">
            <Upload className="w-4 h-4" /> Upload New
          </button>
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-500" />
            <input type="text" placeholder="Search configurations..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-3 border border-line rounded-xl text-sm font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-950" />
          </div>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-3 border border-line rounded-xl text-sm font-bold bg-white text-ink-900 focus:outline-none">
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="uploaded">Uploaded</option>
            <option value="processing">Processing</option>
          </select>
          <select value={vendorFilter} onChange={(e) => setVendorFilter(e.target.value)}
            className="px-4 py-3 border border-line rounded-xl text-sm font-bold bg-white text-ink-900 focus:outline-none">
            <option value="all">All Vendors</option>
            <option value="cisco">Cisco</option>
            <option value="fortinet">Fortinet</option>
            <option value="unknown">Unknown</option>
          </select>
          <select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}
            className="px-4 py-3 border border-line rounded-xl text-sm font-bold bg-white text-ink-900 focus:outline-none">
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <button onClick={loadConfigurations} className="p-3 text-ink-500 hover:text-ink-950 border border-line rounded-xl hover:bg-mist-50" title="Refresh List">
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Configurations List — reference rows */}
      {loading ? (
        <div className="tatva-card p-12 text-center">
          <div className="animate-spin w-10 h-10 border-4 border-line border-t-ink-950 rounded-full mx-auto mb-4"></div>
          <p className="font-bold text-ink-500">Loading configurations and security audits…</p>
        </div>
      ) : filteredConfigs.length === 0 ? (
        <div className="tatva-card p-12 text-center">
          <FileText className="w-16 h-16 text-line mx-auto mb-4" />
          <h3 className="text-xl font-bold tracking-tight text-ink-900 mb-1">No configurations found</h3>
          <p className="text-sm font-semibold text-ink-500 mb-6">Try clearing your filters or upload a new configuration file.</p>
          <button onClick={() => navigate('/vendor/upload')} className="btn-ink px-6 py-3 rounded-xl text-sm font-bold">Upload Configuration</button>
        </div>
      ) : (
        <div className="space-y-5">
          {filteredConfigs.map((config) => {
            const isExpanded = expandedConfigs.has(config.config_id);
            const auditId = config.audit_summary?.audit_id || '';
            const maxSev = Math.max(1, config.audit_summary?.critical_findings || 0, config.audit_summary?.high_findings || 0, config.audit_summary?.medium_findings || 0, config.audit_summary?.low_findings || 0);
            return (
              <div key={config.config_id} className="tatva-card overflow-hidden">
                <div className="p-6">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                    <button onClick={() => toggleExpand(config.config_id)} className="flex items-center gap-4 min-w-0 flex-1 text-left">
                      <span className="w-14 h-14 rounded-2xl bg-ink-950 text-white flex items-center justify-center shrink-0">
                        <FileText className="w-6 h-6" />
                      </span>
                      <span className="min-w-0">
                        <span className="flex items-center gap-3 flex-wrap">
                          <span className="text-xl font-bold tracking-tight text-ink-900">{config.filename}</span>
                          <span className="px-2.5 py-1 bg-mist-100 border border-line text-ink-900 text-[11px] font-bold rounded-full flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 bg-ink-950 rounded-full" />{config.status}
                          </span>
                        </span>
                        <span className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs font-semibold text-ink-500 mt-1.5">
                          <span className="font-mono font-bold text-ink-900">{config.config_id}</span>
                          <span>{config.vendor}</span>
                          {config.file_type && <span>{config.file_type}</span>}
                          {config.file_size ? <span>{(config.file_size / 1024).toFixed(0)} KB</span> : null}
                          <span>Uploaded {new Date(config.created_at).toLocaleString()}</span>
                        </span>
                      </span>
                    </button>
                    <div className="flex items-center gap-8 shrink-0">
                      <span className="text-right">
                        <span className="block text-[11px] font-bold tracking-widest text-ink-500">RISK LEVEL</span>
                        <span className="block text-2xl font-bold tracking-tight text-ink-900">{config.audit_summary?.risk_level || '—'}</span>
                      </span>
                      <span className="text-right">
                        <span className="block text-[11px] font-bold tracking-widest text-ink-500">COMPLIANCE</span>
                        <span className="block text-2xl font-bold tracking-tight text-ink-900">
                          {config.audit_summary ? `${Number(config.audit_summary.compliance_score).toFixed(1)}%` : '—'}
                        </span>
                      </span>
                      <button onClick={() => toggleExpand(config.config_id)} className="w-10 h-10 rounded-full border border-line flex items-center justify-center text-ink-900 hover:bg-mist-50">
                        {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  {config.audit_summary && (
                    <div className="mt-5 bg-mist-50 border border-line rounded-2xl p-5">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        {[
                          { k: 'Critical', v: config.audit_summary.critical_findings },
                          { k: 'High', v: config.audit_summary.high_findings },
                          { k: 'Medium', v: config.audit_summary.medium_findings },
                          { k: 'Low', v: config.audit_summary.low_findings },
                        ].map((s) => (
                          <div key={s.k}>
                            <div className="text-xs font-bold text-ink-500">{s.k}</div>
                            <div className="text-2xl font-bold text-ink-900">{s.v}</div>
                            {sevBar(s.v, maxSev)}
                          </div>
                        ))}
                      </div>
                      <div className="mt-5 flex flex-col sm:flex-row gap-3 sm:justify-end">
                        <button onClick={() => navigate(`/vendor/configuration/${config.config_id}`)}
                          className="btn-ink px-6 py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2">
                          View Details <ArrowRight className="w-4 h-4" />
                        </button>
                        {auditId && (
                          <button onClick={() => handleDownloadReport(auditId)} disabled={downloadingAuditId === auditId}
                            className="btn-paper px-6 py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 disabled:opacity-50">
                            <Download className="w-4 h-4" />
                            <span>{downloadingAuditId === auditId ? 'Downloading…' : 'Download Report'}</span>
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {isExpanded && (
                  <div className="border-t border-line bg-mist-50/60 px-6 py-5">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                      <div>
                        <h5 className="font-bold text-ink-900 mb-2 flex items-center gap-1.5">
                          <Database className="w-4 h-4" /><span>File Integrity</span>
                        </h5>
                        <div className="space-y-1 text-xs font-semibold text-ink-500">
                          <div>Format: <span className="font-mono font-bold text-ink-900">{config.file_type || '—'}</span></div>
                          <div>Vendor: <span className="font-bold text-ink-900">{config.vendor} ({Math.round((config.vendor_confidence || 0) * 100)}%)</span></div>
                        </div>
                      </div>
                      <div>
                        <h5 className="font-bold text-ink-900 mb-2 flex items-center gap-1.5">
                          <Activity className="w-4 h-4" /><span>Pipeline</span>
                        </h5>
                        <div className="space-y-1 text-xs font-semibold text-ink-500">
                          <div className="flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 text-ink-950" /><span>File sanitized & stored</span></div>
                          <div className="flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 text-ink-950" /><span>{config.audit_summary ? 'Audit completed' : 'Awaiting audit'}</span></div>
                        </div>
                      </div>
                      <div>
                        <h5 className="font-bold text-ink-900 mb-2">Quick Actions</h5>
                        <button onClick={() => navigate(`/vendor/configuration/${config.config_id}`)}
                          className="text-xs font-bold text-ink-950 hover:underline flex items-center gap-1">
                          <span>Inspect complete audit findings</span><ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Details modal — real findings */}
      {selectedConfig && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink-950/60 animate-fade-in">
          <div className="bg-white rounded-3xl border border-line shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
            <div className="p-6 border-b border-line bg-mist-50 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold tracking-tight text-ink-900">{selectedConfig.filename}</h3>
                <p className="text-xs font-semibold text-ink-500 mt-0.5">
                  Config ID: <strong className="font-mono text-ink-900">{selectedConfig.config_id}</strong> · Vendor: <strong className="text-ink-900">{selectedConfig.vendor}</strong>
                </p>
              </div>
              <button onClick={() => setSelectedConfig(null)} className="p-2 text-ink-500 hover:text-ink-950 rounded-full hover:bg-mist-100">
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex border-b border-line bg-white px-6 gap-6 text-sm font-bold">
              {(['findings', 'overview', 'metadata'] as const).map((t) => (
                <button key={t} onClick={() => setDetailTab(t)}
                  className={`py-3.5 border-b-2 ${detailTab === t ? 'border-ink-950 text-ink-950' : 'border-transparent text-ink-500 hover:text-ink-900'}`}>
                  {t === 'findings' ? 'Audit Findings' : t === 'overview' ? 'Scorecard' : 'File Preview'}
                </button>
              ))}
            </div>
            <div className="p-6 overflow-y-auto flex-1 space-y-4">
              {detailTab === 'findings' && (
                detailFindings.length === 0 ? (
                  <p className="text-sm font-bold text-ink-500">No detailed findings loaded for this configuration.</p>
                ) : detailFindings.slice(0, 12).map((f: any) => (
                  <div key={f.finding_id} className="p-4 rounded-2xl border border-line bg-white space-y-1.5">
                    <div className="flex items-center justify-between gap-3">
                      <span className="px-2.5 py-0.5 bg-ink-950 text-white rounded-md text-xs font-bold">{f.severity}</span>
                      <span className="text-xs text-ink-500 font-mono">{f.rule_id}</span>
                    </div>
                    <h5 className="font-bold text-ink-900 text-sm">{f.rule_name}</h5>
                    <p className="text-xs font-medium text-ink-500">{f.description}</p>
                    {f.remediation?.guidance && (
                      <div className="bg-mist-50 p-2.5 rounded-xl border border-line text-xs font-semibold text-ink-900">
                        Remediation: {f.remediation.guidance}
                      </div>
                    )}
                  </div>
                ))
              )}
              {detailTab === 'overview' && selectedConfig.audit_summary && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                  <div className="p-4 bg-ink-950 text-white rounded-2xl">
                    <div className="text-3xl font-bold">{Number(selectedConfig.audit_summary.compliance_score).toFixed(1)}%</div>
                    <div className="text-xs font-bold text-white/60 mt-1">COMPLIANCE</div>
                  </div>
                  {[
                    { k: 'Critical', v: selectedConfig.audit_summary.critical_findings },
                    { k: 'High', v: selectedConfig.audit_summary.high_findings },
                    { k: 'Medium', v: selectedConfig.audit_summary.medium_findings },
                  ].map((s) => (
                    <div key={s.k} className="p-4 bg-mist-50 border border-line rounded-2xl">
                      <div className="text-3xl font-bold text-ink-950">{s.v}</div>
                      <div className="text-xs font-bold text-ink-500 mt-1">{s.k.toUpperCase()}</div>
                    </div>
                  ))}
                </div>
              )}
              {detailTab === 'metadata' && (
                <pre className="bg-ink-950 text-white/90 p-5 rounded-2xl font-mono text-xs overflow-x-auto leading-relaxed whitespace-pre-wrap">
                  {(detailMeta?.file_content?.preview || 'Configuration preview not available for this file.')}
                </pre>
              )}
            </div>
            <div className="p-6 border-t border-line bg-mist-50 flex items-center justify-between">
              <span className="text-xs font-bold text-ink-500">TATVA by Team Vajracore</span>
              <div className="flex items-center gap-3">
                <button onClick={() => setSelectedConfig(null)} className="px-4 py-2 bg-mist-200 text-ink-900 font-bold rounded-xl hover:bg-mist-100 text-sm">Close</button>
                {selectedConfig.audit_summary?.audit_id && (
                  <button onClick={() => handleDownloadReport(selectedConfig.audit_summary!.audit_id!)} disabled={downloadingAuditId !== null}
                    className="btn-ink flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-bold">
                    <Download className="w-4 h-4" /><span>Download Report PDF</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DetailedConfigurationManager;
