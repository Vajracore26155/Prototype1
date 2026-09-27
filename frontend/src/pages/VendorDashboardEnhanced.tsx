import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LogOut, Upload, Menu, X, Key, Lock, CheckCircle, Save, ChevronRight, Building2, Download
} from 'lucide-react';
import { Search } from 'lucide-react';
import VajraMark from '../components/VajraMark';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import {
  getVendorSession,
  revokeVendorSession,
  isVendorLoggedIn,
  getVendorInfo
} from '../services/vendorApi';
import VendorAnalyticsDashboard from '../components/VendorAnalyticsDashboard';
import DetailedConfigurationManager from '../components/DetailedConfigurationManager';
import DetailedAuditFindings from '../components/DetailedAuditFindings';

interface SessionInfo {
  session_id: string;
  vendor: {
    vendor_id: string;
    company: string;
    contact: string;
    email: string;
  };
  status: string;
  upload_count: number;
  created_at: string;
  expires_at: string;
  last_activity: string;
  organization_id: number;
}

type DashboardView = 'overview' | 'analytics' | 'configurations' | 'findings' | 'reports' | 'settings';

export default function VendorDashboardEnhanced() {
  const navigate = useNavigate();
  const [currentView, setCurrentView] = useState<DashboardView>('overview');
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, type: 'success', message: 'Configuration audit completed', time: '2 min ago' },
    { id: 2, type: 'warning', message: 'Critical finding detected', time: '1 hour ago' },
    { id: 3, type: 'info', message: 'New compliance framework added', time: '3 hours ago' }
  ]);

  useEffect(() => {
    // Check if vendor is logged in
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }

    loadDashboardData();
  }, [navigate]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const sessionResponse = await getVendorSession();
      if (sessionResponse.success) {
        setSessionInfo(sessionResponse.data);
      } else {
        throw new Error(sessionResponse.data?.error?.message || 'Failed to load session');
      }
    } catch (err: any) {
      console.error('Failed to load dashboard:', err);
      setError(err.response?.data?.error?.message || err.message || 'Failed to load dashboard data');
      
      if (err.response?.status === 401) {
        localStorage.removeItem('vendor_session_token');
        localStorage.removeItem('vendor_info');
        setTimeout(() => navigate('/vendor/login'), 1000);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await revokeVendorSession();
      navigate('/vendor/login');
    } catch (err) {
      localStorage.removeItem('vendor_session_token');
      localStorage.removeItem('vendor_info');
      navigate('/vendor/login');
    }
  };

  const getTimeRemaining = (expiresAt: string) => {
    const expiry = new Date(expiresAt);
    const now = new Date();
    const diff = expiry.getTime() - now.getTime();

    if (diff < 0) return 'Expired';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const navTabs = [
    { id: 'overview', name: 'Dashboard' },
    { id: 'configurations', name: 'Configurations' },
    { id: 'findings', name: 'Security Audit' },
    { id: 'analytics', name: 'Reports' },
  ];

  const initials = (sessionInfo?.vendor?.contact || sessionInfo?.vendor?.company || 'V').charAt(0).toUpperCase()
    + ((sessionInfo?.vendor?.contact || '').split(' ')[1]?.charAt(0).toUpperCase() || '');

  return (
    <div className="min-h-screen bg-mist-50 text-ink-900">
      {/* Top nav — reference shell */}
      <header className="bg-white/90 backdrop-blur border-b border-line sticky top-0 z-40">
        <div className="max-w-[1400px] mx-auto px-5 sm:px-8">
          <div className="flex items-center justify-between h-16 gap-4">
            <button className="flex items-center gap-2.5 shrink-0" onClick={() => setCurrentView('overview')}>
              <VajraMark className="w-8 h-8" />
              <span className="text-left leading-none">
                <span className="block text-base font-bold tracking-tight">Vajracores</span>
                <span className="block text-[10px] font-bold tracking-[0.3em] text-ink-500">TATVA</span>
              </span>
            </button>
            <nav className="hidden lg:flex items-center gap-8">
              {navTabs.map((t) => {
                const active = currentView === t.id || (t.id === 'analytics' && currentView === 'reports');
                return (
                  <button
                    key={t.id}
                    onClick={() => setCurrentView(t.id as DashboardView)}
                    className={`relative py-5 text-sm font-bold ${active ? 'text-ink-950' : 'text-ink-500 hover:text-ink-950'}`}
                  >
                    {t.name}
                    {active && <span className="absolute left-1/2 -translate-x-1/2 -bottom-[1px] w-10 h-[3px] bg-ink-950 rounded-full" />}
                  </button>
                );
              })}
            </nav>
            <div className="flex items-center gap-3">
              <button onClick={() => setCurrentView('configurations')} title="Search configurations"
                className="hidden md:flex items-center gap-2 text-sm font-semibold text-ink-500 bg-mist-100 border border-line rounded-full pl-4 pr-3 py-2 hover:text-ink-950">
                <Search className="w-4 h-4" />
                <span className="hidden xl:inline">Search configurations…</span>
                <kbd className="text-[10px] font-bold bg-white border border-line rounded px-1.5 py-0.5">⌘K</kbd>
              </button>
              <button onClick={() => setCurrentView('settings')} title="Profile"
                className="w-10 h-10 rounded-full bg-ink-950 text-white text-xs font-bold flex items-center justify-center">
                {initials || 'MP'}
              </button>
              <button onClick={handleLogout} title="Logout"
                className="hidden sm:flex w-10 h-10 rounded-full border border-line items-center justify-center text-ink-500 hover:text-ink-950 hover:border-ink-950">
                <LogOut className="w-4 h-4" />
              </button>
              <button onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden p-2 text-ink-500 hover:text-ink-950" title="Menu">
                {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>
        {/* Collapsible panel (mobile + hideable nav) */}
        {sidebarOpen && (
          <div className="border-t border-line bg-white lg:hidden">
            <div className="px-5 py-3 grid gap-1">
              {[...navTabs, { id: 'reports', name: 'Downloads' }, { id: 'settings', name: 'Settings' }].map((t) => (
                <button key={t.id} onClick={() => { setCurrentView(t.id as DashboardView); setSidebarOpen(false); }}
                  className={`text-left px-3 py-2.5 rounded-xl text-sm font-bold ${currentView === t.id ? 'bg-ink-950 text-white' : 'text-ink-500 hover:bg-mist-100 hover:text-ink-950'}`}>
                  {t.name}
                </button>
              ))}
              <div className="flex items-center justify-between px-3 py-2 text-xs font-bold text-ink-500">
                <span>Session {getTimeRemaining(sessionInfo?.expires_at || '')} remaining</span>
                <button onClick={handleLogout} className="flex items-center gap-1 text-ink-900"><LogOut className="h-4 w-4" /> Logout</button>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <div className="max-w-[1400px] mx-auto px-5 sm:px-8 pb-16 flex flex-col min-h-[calc(100vh-64px)]">
        {/* Page hero */}
        <div className="pt-10 pb-8">
          <div className="text-[11px] font-bold tracking-[0.3em] text-ink-500">
            {currentView === 'overview' ? 'VENDOR OVERVIEW' :
             currentView === 'analytics' ? 'NETWORK SECURITY INTELLIGENCE' :
             currentView === 'configurations' ? 'CONFIGURATION MANAGEMENT' :
             currentView === 'findings' ? 'SECURITY FINDINGS' :
             currentView === 'reports' ? 'REPORTS & DOWNLOADS' : 'SETTINGS & PROFILE'}
          </div>
          <div className="mt-2 flex flex-col lg:flex-row lg:items-end justify-between gap-4">
            <h2 className="text-4xl sm:text-5xl font-bold tracking-tight">
              {currentView === 'overview' ? 'Good to see you.' :
               currentView === 'analytics' ? 'Analytics & Insights' :
               currentView === 'configurations' ? 'Configuration Management' :
               currentView === 'findings' ? 'Security Intelligence' :
               currentView === 'reports' ? 'Reports & Downloads' : 'Settings & Profile'}
            </h2>
            <div className="flex items-center gap-3">
              <button onClick={() => navigate('/vendor/upload')} className="btn-ink px-6 py-3 rounded-xl text-sm flex items-center gap-2">
                <Upload className="w-4 h-4" /> Quick Upload
              </button>
              {currentView !== 'overview' && (
                <button onClick={() => setCurrentView('overview')} className="btn-paper px-6 py-3 rounded-xl text-sm">Overview</button>
              )}
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1">
          {error && (
            <div className="mb-6 bg-white border border-ink-950 text-ink-950 px-4 py-3 rounded-xl font-bold text-sm">
              {error}
            </div>
          )}

          {/* Render Current View */}
          {currentView === 'overview' && (
            <VendorOverview sessionInfo={sessionInfo} />
          )}
          {currentView === 'analytics' && (
            <VendorAnalyticsDashboard />
          )}
          {currentView === 'configurations' && (
            <DetailedConfigurationManager />
          )}
          {currentView === 'findings' && (
            <DetailedAuditFindings auditId="" />
          )}
          {currentView === 'reports' && (
            <VendorReports />
          )}
          {currentView === 'settings' && (
            <VendorSettings sessionInfo={sessionInfo} />
          )}
        </div>
      </div>
    </div>
  );
}

// Overview Component — monochrome command center, real vendor data
const VendorOverview: React.FC<{ sessionInfo: SessionInfo | null }> = ({ sessionInfo }) => {
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { getVendorAnalyticsOverview, getVendorRiskDistribution, getVendorAudits, getVendorAuditEnhanced } =
          await import('../services/vendorApi');
        const [ov, risk, auditsResp] = await Promise.all([
          getVendorAnalyticsOverview('30d'),
          getVendorRiskDistribution(),
          getVendorAudits(),
        ]);
        const audits: any[] = auditsResp?.data?.audits || [];
        let topFails: any[] = [];
        for (const a of audits.slice(0, 6)) {
          try {
            const enh: any = await getVendorAuditEnhanced(a.audit_id);
            const fails = (enh?.data?.findings?.details || []).filter((f: any) => f.status === 'FAIL').slice(0, 3);
            topFails.push(...fails.map((f: any) => ({ ...f, audit_id: a.audit_id })));
          } catch { /* ignore single audit errors */ }
        }
        topFails = topFails.slice(0, 5);
        setData({
          metrics: ov?.data?.metrics || {},
          risk: risk?.data?.risk_analysis || [],
          audits: audits.slice(0, 4),
          topFails,
        });
      } catch {
        setData({ metrics: {}, risk: [], audits: [], topFails: [] });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const m = data?.metrics || {};
  const totalDecided = (m.passed_controls || 0) + (m.failed_controls || 0) + (m.warning_controls || 0);
  const passRate = totalDecided > 0 ? ((m.passed_controls || 0) / totalDecided) * 100 : 0;
  const initial = (sessionInfo?.vendor?.contact || sessionInfo?.vendor?.company || 'V').charAt(0).toUpperCase();
  const donut = [
    { name: 'Passed', value: m.passed_controls || 0, color: '#111418' },
    { name: 'Failed', value: m.failed_controls || 0, color: '#9AA3B2' },
    { name: 'Warning', value: m.warning_controls || 0, color: '#D9E1EC' },
  ];

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-line p-12 text-center">
        <div className="animate-spin w-10 h-10 border-4 border-line border-t-ink-950 rounded-full mx-auto mb-4" />
        <p className="font-bold text-ink-500 text-sm">Loading live posture…</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Command strip */}
      <div className="bg-ink-950 text-white rounded-2xl p-6 sm:p-8 flex flex-col xl:flex-row gap-8">
        <div className="flex items-start gap-5 min-w-0 flex-1">
          <div className="w-16 h-16 rounded-2xl bg-white text-ink-950 flex items-center justify-center font-bold text-3xl shrink-0">{initial}</div>
          <div className="min-w-0">
            <div className="text-[11px] font-bold tracking-[0.28em] text-white/60">VENDOR COMMAND CENTER</div>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight truncate">{sessionInfo?.vendor?.company || 'Vendor'}</h2>
            <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-sm font-semibold text-white/70">
              <span>Session <strong className="text-white font-mono">{sessionInfo?.session_id}</strong></span>
              <span>Uploads <strong className="text-white">{sessionInfo?.upload_count ?? 0}</strong></span>
              <span>Status <strong className="text-white">{sessionInfo?.status}</strong></span>
            </div>
            <div className="mt-5 flex flex-wrap gap-3">
              <button onClick={() => navigate('/vendor/upload')} className="bg-white text-ink-950 px-6 py-3 rounded-xl text-sm font-bold hover:bg-mist-100">Quick Upload</button>
              <button onClick={() => navigate('/vendor/configurations')} className="border border-white/40 text-white px-6 py-3 rounded-xl text-sm font-bold hover:bg-white/10">Configurations</button>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-6 xl:w-[420px] shrink-0 border-t xl:border-t-0 xl:border-l border-white/15 pt-6 xl:pt-0 xl:pl-8">
          <div>
            <div className="text-[11px] font-bold tracking-widest text-white/60">COMPLIANCE</div>
            <div className="text-4xl font-bold mt-1">{Number(m.avg_compliance_score || 0).toFixed(1)}%</div>
            <div className="text-xs font-bold text-white/60 mt-1">{passRate.toFixed(1)}% pass rate</div>
          </div>
          <div>
            <div className="text-[11px] font-bold tracking-widest text-white/60">OPEN FAILS</div>
            <div className="text-4xl font-bold mt-1">{m.failed_controls || 0}</div>
            <div className="text-xs font-bold text-white/60 mt-1">{m.critical_findings || 0} critical</div>
          </div>
          <div>
            <div className="text-[11px] font-bold tracking-widest text-white/60">AUDITS</div>
            <div className="text-4xl font-bold mt-1">{m.total_audits || 0}</div>
            <div className="text-xs font-bold text-white/60 mt-1">{m.total_configurations || 0} configs</div>
          </div>
        </div>
      </div>

      {/* Ledger + donut */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="tatva-card p-7">
          <div className="text-xs font-bold tracking-[0.24em] text-ink-500">RISK LEDGER</div>
          <h3 className="text-2xl font-bold tracking-tight text-ink-900 mt-1">What needs attention</h3>
          <div className="mt-5 space-y-3">
            {[
              { k: 'Critical', v: m.critical_findings || 0 },
              { k: 'High', v: m.high_findings || 0 },
              { k: 'Medium', v: m.medium_findings || 0 },
              { k: 'Low', v: m.low_findings || 0 },
            ].map((r) => (
              <div key={r.k} className="flex items-center justify-between border-b border-line pb-3 last:border-0 last:pb-0">
                <span className="font-bold text-ink-900">{r.k}</span>
                <span className="text-2xl font-bold text-ink-900">{r.v}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="tatva-card p-7">
          <div className="text-xs font-bold tracking-[0.24em] text-ink-500">OUTCOME MIX</div>
          <h3 className="text-2xl font-bold tracking-tight text-ink-900 mt-1">Pass vs fail vs warning</h3>
          <div className="h-44 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={donut} dataKey="value" nameKey="name" innerRadius={52} outerRadius={78} paddingAngle={3} strokeWidth={0}>
                  {donut.map((d, i) => (<Cell key={i} fill={d.color} />))}
                </Pie>
                <Tooltip contentStyle={{ background: '#111418', color: '#fff', borderRadius: 12, border: 'none' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-between text-xs font-bold text-ink-500 mt-2">
            <span>Passed {m.passed_controls || 0}</span><span>Failed {m.failed_controls || 0}</span><span>Warn {m.warning_controls || 0}</span>
          </div>
        </div>
        <div className="bg-ink-950 text-white rounded-2xl p-7 flex flex-col">
          <div className="text-xs font-bold tracking-[0.24em] text-white/60">ACTION QUEUE</div>
          <h3 className="text-2xl font-bold tracking-tight mt-1">Top failing controls</h3>
          <div className="mt-4 space-y-3 flex-1">
            {(data?.topFails || []).length === 0 && (
              <div className="text-sm font-bold text-white/60">No failing controls. Upload a configuration to begin.</div>
            )}
            {(data?.topFails || []).map((f: any) => (
              <button key={f.finding_id} onClick={() => navigate(`/vendor/audit/${f.audit_id}`)}
                className="w-full text-left bg-white/5 hover:bg-white/10 border border-white/15 rounded-xl p-3 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="font-bold text-sm truncate">{f.rule_name}</div>
                  <div className="text-xs font-mono text-white/60">{f.severity} &bull; {f.audit_id}</div>
                </div>
                <ChevronRight className="w-4 h-4 shrink-0" />
              </button>
            ))}
          </div>
          <button onClick={() => navigate('/vendor/upload')} className="mt-5 bg-white text-ink-950 rounded-xl py-3 text-sm font-bold">Upload New Configuration</button>
        </div>
      </div>

      {/* Latest audits ledger */}
      <div className="tatva-card p-7">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs font-bold tracking-[0.24em] text-ink-500">LATEST AUDITS</div>
            <h3 className="text-2xl font-bold tracking-tight text-ink-900 mt-1">Real results, newest first</h3>
          </div>
          <button onClick={() => navigate('/vendor/configurations')} className="btn-paper px-5 py-2.5 rounded-xl text-sm">All configurations</button>
        </div>
        <div className="mt-5 divide-y divide-line">
          {(data?.audits || []).length === 0 && (
            <div className="py-8 text-center font-bold text-ink-500 text-sm">No audits yet — upload your first configuration.</div>
          )}
          {(data?.audits || []).map((a: any) => (
            <button key={a.audit_id} onClick={() => navigate(`/vendor/audit/${a.audit_id}`)} className="w-full py-4 flex items-center justify-between gap-4 text-left hover:bg-mist-50 px-2 rounded-lg">
              <div className="min-w-0">
                <div className="font-bold text-ink-900 truncate">{a.audit_id} <span className="font-mono text-ink-500">· {a.configuration?.config_id}</span></div>
                <div className="text-xs font-semibold text-ink-500 truncate">{a.configuration?.filename} · {a.risk_level}</div>
              </div>
              <div className="text-right shrink-0">
                <div className="text-2xl font-bold text-ink-900">{Number(a.compliance_score || 0).toFixed(1)}%</div>
                <div className="text-[11px] font-bold text-ink-500">COMPLIANCE</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// Placeholder components for other views
const VendorReports: React.FC = () => (
  <div className="text-center py-12">
    <Download className="w-16 h-16 mx-auto text-gray-300 mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">Reports & Downloads</h3>
    <p className="text-gray-500">Comprehensive reporting functionality coming soon.</p>
  </div>
);

const VendorSettings: React.FC<{ sessionInfo: SessionInfo | null }> = ({ sessionInfo }) => {
  const [profile, setProfile] = useState<any>(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [profileError, setProfileError] = useState('');
  const [profileSaved, setProfileSaved] = useState(false);
  const [contact, setContact] = useState(sessionInfo?.vendor?.contact || '');
  const [phone, setPhone] = useState('');
  const [username, setUsername] = useState('');

  const [setUser, setSetUser] = useState('');
  const [setPass, setSetPass] = useState('');
  const [setMsg, setSetMsg] = useState('');
  const [setErr, setSetErr] = useState('');
  const [settingPw, setSettingPw] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState('');
  const [changingPw, setChangingPw] = useState(false);

  const vendorId = getVendorInfo()?.vendor_id || (sessionInfo as any)?.vendor?.vendor_id;
  const token = () => localStorage.getItem('vendor_session_token') || '';

  const loadProfile = async () => {
    if (!vendorId) { setLoadingProfile(false); return; }
    setLoadingProfile(true);
    setProfileError('');
    try {
      const res = await fetch(`/api/vendor/profile/${vendorId}`, { headers: { 'X-Vendor-Session-Token': token() } });
      const body = await res.json();
      if (!res.ok || !body.success) throw new Error(body?.detail?.error?.message || 'Failed to load profile');
      setProfile(body.data);
      setContact(body.data.contact_name || sessionInfo?.vendor?.contact || '');
      setPhone(body.data.phone || '');
      setUsername(body.data.username || '');
    } catch (e: any) {
      setProfileError(e.message || 'Failed to load profile');
    } finally {
      setLoadingProfile(false);
    }
  };

  useEffect(() => { loadProfile(); }, [vendorId]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileError('');
    setProfileSaved(false);
    try {
      const res = await fetch(`/api/vendor/profile/${vendorId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-Vendor-Session-Token': token() },
        body: JSON.stringify({ contact_name: contact, phone, username: username || undefined }),
      });
      const body = await res.json();
      if (!res.ok || !body.success) throw new Error(body?.detail?.error?.message || 'Failed to save profile');
      setProfileSaved(true);
      await loadProfile();
      setTimeout(() => setProfileSaved(false), 3000);
    } catch (e: any) {
      setProfileError(e.message || 'Failed to save profile');
    }
  };

  const handleSetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setSetErr(''); setSetMsg('');
    if (!setUser) { setSetErr('Username is required'); return; }
    if (setPass.length < 8) { setSetErr('Password must be at least 8 characters'); return; }
    setSettingPw(true);
    try {
      const res = await fetch(`/api/vendor/set-password/${vendorId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Vendor-Session-Token': token() },
        body: JSON.stringify({ username: setUser, password: setPass }),
      });
      const body = await res.json();
      if (!res.ok || !body.success) throw new Error(body?.detail?.error?.message || 'Failed to set password');
      setSetMsg('Username and password set! You can now login with OTP or email + password.');
      setSetUser(''); setSetPass('');
      await loadProfile();
    } catch (e: any) {
      setSetErr(e.message || 'Failed to set password');
    } finally {
      setSettingPw(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg('');
    if (newPassword !== confirmPassword) { setPasswordMsg('New passwords do not match'); return; }
    if (newPassword.length < 8) { setPasswordMsg('New password must be at least 8 characters'); return; }
    setChangingPw(true);
    try {
      const res = await fetch(`/api/vendor/change-password/${vendorId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Vendor-Session-Token': token() },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      const body = await res.json();
      if (!res.ok || !body.success) throw new Error(body?.detail?.error?.message || 'Failed to change password');
      setPasswordMsg('Password changed successfully! Use the new password next login.');
      setCurrentPassword(''); setNewPassword(''); setConfirmPassword('');
    } catch (e: any) {
      setPasswordMsg(e.message || 'Failed to change password');
    } finally {
      setChangingPw(false);
    }
  };

  const hasPassword = !!profile?.has_password;
  const displayCompany = sessionInfo?.vendor?.company || profile?.company_name || 'Vendor';
  const displayInitial = (contact || displayCompany || 'V').charAt(0).toUpperCase();

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header — reference black card */}
      <div className="bg-ink-950 text-white rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full border-2 border-white/40 flex items-center justify-center font-bold text-2xl shrink-0">
            {displayInitial}
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight">{displayCompany}</h2>
            <p className="text-white/60 text-xs font-bold mt-0.5">{profile?.email || sessionInfo?.vendor?.email || ''}</p>
            <div className="flex flex-wrap items-center gap-2 mt-2 text-[11px] font-bold">
              <span className="px-2.5 py-1 bg-white text-ink-950 rounded-full">Owner</span>
              <span className="px-2.5 py-1 border border-white/30 text-white rounded-full">Active</span>
              <span className={`px-2.5 py-1 border rounded-full ${hasPassword ? 'border-white/30 text-white' : 'border-white/30 text-white/60'}`}>
                {loadingProfile ? 'Checking login…' : hasPassword ? 'Password Enabled' : 'OTP Only'}
              </span>
            </div>
          </div>
        </div>
        <div className="text-[11px] font-mono font-bold text-white/50">Vendor ID: {profile?.vendor_id || vendorId || '—'}</div>
      </div>

      {profileError && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-800 rounded-xl text-xs font-bold">{profileError}</div>
      )}
      {profileSaved && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-bold flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          <span>Organization profile updated successfully!</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Profile */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-5">
            <div className="flex items-center space-x-3 border-b border-slate-100 pb-4">
              <Building2 className="w-6 h-6 text-ink-900" />
              <div>
                <h3 className="text-lg font-bold text-slate-900">Organization & Profile Information</h3>
                <p className="text-xs font-semibold text-slate-500">Contact and username used for password login</p>
              </div>
            </div>
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Contact Person</label>
                  <input type="text" value={contact} onChange={(e) => setContact(e.target.value)}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Phone</label>
                  <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91-…"
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Username (for password login)</label>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="choose-a-username"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="flex justify-end">
                <button type="submit" className="flex items-center space-x-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold text-sm">
                  <Save className="w-4 h-4" /><span>Save Profile</span>
                </button>
              </div>
            </form>
          </div>

          {/* First-time: set username + password */}
          {!hasPassword && !loadingProfile && (
            <div className="bg-white rounded-2xl p-6 border border-amber-200 shadow-sm space-y-4">
              <div className="flex items-center space-x-3 border-b border-slate-100 pb-4">
                <Key className="w-6 h-6 text-amber-600" />
                <div>
                  <h3 className="text-lg font-bold text-slate-900">Set Username & Password (first OTP login)</h3>
                  <p className="text-xs font-semibold text-slate-500">After this you can login with OTP or email + password</p>
                </div>
              </div>
              {setErr && <div className="p-3 bg-red-50 border border-red-200 text-red-800 rounded-xl text-xs font-bold">{setErr}</div>}
              {setMsg && <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-bold">{setMsg}</div>}
              <form onSubmit={handleSetPassword} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Username</label>
                  <input type="text" value={setUser} onChange={(e) => setSetUser(e.target.value)}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-bold text-slate-900" required />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Password (min 8 chars)</label>
                  <input type="password" value={setPass} onChange={(e) => setSetPass(e.target.value)}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-bold text-slate-900" required />
                </div>
                <div className="flex justify-end">
                  <button type="submit" disabled={settingPw} className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-sm disabled:opacity-50">
                    {settingPw ? 'Saving…' : 'Set Username & Password'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Change password */}
          {hasPassword && (
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
              <div className="flex items-center space-x-3 border-b border-slate-100 pb-4">
                <Lock className="w-6 h-6 text-indigo-700" />
                <div>
                  <h3 className="text-lg font-bold text-slate-900">Change Current Password</h3>
                  <p className="text-xs font-semibold text-slate-500">Use this interface to rotate your login password</p>
                </div>
              </div>
              {passwordMsg && (
                <div className={`p-3 rounded-xl text-xs font-bold ${passwordMsg.includes('successfully') ? 'bg-emerald-50 border border-emerald-200 text-emerald-800' : 'bg-red-50 border border-red-200 text-red-800'}`}>{passwordMsg}</div>
              )}
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Current Password</label>
                  <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-bold text-slate-900" required />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">New Password</label>
                    <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-bold text-slate-900" required />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Confirm New Password</label>
                    <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm font-bold text-slate-900" required />
                  </div>
                </div>
                <div className="flex justify-end">
                  <button type="submit" disabled={changingPw} className="flex items-center space-x-2 px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-sm disabled:opacity-50">
                    <Key className="w-4 h-4" /><span>{changingPw ? 'Updating…' : 'Update Password'}</span>
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* Login methods (real state) */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
            <h3 className="text-base font-bold text-slate-900">Login Methods</h3>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
              <div className="font-bold text-slate-900">1. OTP login</div>
              <div className="font-semibold text-slate-500">Email code — always available</div>
            </div>
            <div className={`p-3 rounded-xl border text-xs ${hasPassword ? 'bg-emerald-50 border-emerald-200' : 'bg-amber-50 border-amber-200'}`}>
              <div className="font-bold text-slate-900">2. Password login {hasPassword ? '— active' : '— not set'}</div>
              <div className="font-semibold text-slate-500">{hasPassword ? `Username: ${profile?.username || username || 'set'} — use email + password on login page` : 'Set username + password on first OTP login to enable it'}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};