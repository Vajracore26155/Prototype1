import { useNavigate } from 'react-router-dom';
import { Users, Lock, ArrowRight, CheckCircle, Zap, BarChart3, Mail, UserPlus, Shield } from 'lucide-react';
import VajraMark from '../components/VajraMark';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-mist-50 text-ink-900">
      {/* Top bar */}
      <nav className="bg-white/85 backdrop-blur border-b border-line sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <VajraMark className="w-9 h-9" />
            <div>
              <div className="text-lg font-bold tracking-tight text-ink-900 leading-none">TATVA</div>
              <div className="text-[11px] font-bold tracking-[0.22em] text-ink-500">VAJRACORES</div>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-3">
            <button onClick={() => navigate('/vendor/login')} className="text-sm font-bold text-ink-900 hover:underline">Vendor Login</button>
            <button onClick={() => navigate('/login')} className="btn-ink text-sm px-5 py-2.5 rounded-xl">Admin Login</button>
          </div>
        </div>
      </nav>

      {/* HERO — reference Image 1 + background Image 2 */}
      <header className="tatva-hero-bg relative overflow-hidden border-b border-line">
        <div className="tatva-grid absolute inset-0" aria-hidden="true" />
        {/* cyber shield glow, right side */}
        <svg viewBox="0 0 520 520" className="absolute -right-24 top-1/2 -translate-y-1/2 w-[560px] h-[560px] opacity-70 pointer-events-none" aria-hidden="true">
          <defs>
            <radialGradient id="tatvaGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#7FB6EC" stopOpacity="0.55" />
              <stop offset="55%" stopColor="#7FB6EC" stopOpacity="0.18" />
              <stop offset="100%" stopColor="#7FB6EC" stopOpacity="0" />
            </radialGradient>
          </defs>
          <circle cx="260" cy="260" r="240" fill="url(#tatvaGlow)" />
          <circle cx="260" cy="260" r="150" fill="none" stroke="#2F6DB3" strokeOpacity="0.35" strokeWidth="1.5" />
          <circle cx="260" cy="260" r="118" fill="none" stroke="#2F6DB3" strokeOpacity="0.5" strokeWidth="1.5" />
          <circle cx="260" cy="260" r="88" fill="#FFFFFF" stroke="#2F6DB3" strokeOpacity="0.55" strokeWidth="2" />
          <path d="M260 210 L296 224 V258 C296 284 280 302 260 312 C240 302 224 284 224 258 V224 Z" fill="#E7F1FB" stroke="#1F4E86" strokeWidth="3" />
          <rect x="250" y="252" width="20" height="16" rx="2" fill="#1F4E86" />
          <path d="M253 252 v-5 a7 7 0 0 1 14 0 v5" fill="none" stroke="#1F4E86" strokeWidth="3" />
        </svg>

        <div className="relative max-w-7xl mx-auto px-6 pt-14 pb-16 text-center">
          <div className="flex items-center justify-center gap-2 mb-8">
            <VajraMark className="w-5 h-5" />
            <span className="tatva-eyebrow">VAJRACORES</span>
          </div>
          <div className="inline-block tatva-box px-10 sm:px-16 py-5 sm:py-7">
            <h1 className="tatva-display text-7xl sm:text-8xl md:text-9xl">TATVA</h1>
          </div>
          <p className="tatva-tagline mt-6">WHERE NETWORKS MEET SECURITY</p>
          <p className="mt-4 text-sm font-bold text-ink-500 tracking-wide">Team Vajracore &bull; SIH 2026 &bull; AI-Driven Multi-Vendor Compliance Auditor</p>
          <div className="mt-8 flex flex-col sm:flex-row justify-center gap-3">
            <button onClick={() => navigate('/vendor/register')} className="btn-ink px-8 py-3.5 rounded-xl text-sm">Start as Vendor <ArrowRight className="inline w-4 h-4 ml-1" /></button>
            <button onClick={() => navigate('/login')} className="btn-paper px-8 py-3.5 rounded-xl text-sm">Admin Login</button>
          </div>
          <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-white border border-line rounded-full">
            <span className="w-2 h-2 bg-emerald-600 rounded-full animate-pulse" />
            <span className="text-xs font-bold text-ink-900">System Active</span>
          </div>
        </div>
      </header>

      {/* PORTALS — same routes, premium cards */}
      <main className="max-w-7xl mx-auto px-6 py-16">
        <div className="flex items-end justify-between mb-8">
          <div>
            <div className="text-xs font-bold tracking-[0.28em] text-ink-500">ACCESS PORTALS</div>
            <h2 className="text-4xl sm:text-5xl font-bold tracking-tight text-ink-900 mt-2">Choose your workspace</h2>
          </div>
          <div className="hidden md:block text-sm font-semibold text-ink-500">Black &bull; White &bull; Gray</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <PortalCard
            eyebrow="VENDORS"
            title="Vendor Login"
            desc="OTP or email + password. Upload configs, track audits, download designer PDF reports."
            points={['OTP + password login', 'Upload & auto-audit', 'Findings with evidence']}
            cta="Open Vendor Login"
            dark
            onClick={() => navigate('/vendor/login')}
            icon={<Users className="w-6 h-6" />}
          />
          <PortalCard
            eyebrow="VENDORS"
            title="Vendor Registration"
            desc="Register your company once. Admin approves, then first OTP login sets your username + password."
            points={['Company + contact profile', 'Admin approval workflow', 'Set credentials on first login']}
            cta="Register as Vendor"
            onClick={() => navigate('/vendor/register')}
            icon={<UserPlus className="w-6 h-6" />}
          />
          <PortalCard
            eyebrow="ADMINISTRATORS"
            title="Admin Login"
            desc="Single authorized admin. Approve vendors, monitor sessions, review audits and platform compliance."
            points={['Vendor approvals', 'Sessions & activity', 'Platform oversight']}
            cta="Open Admin Login"
            dark
            onClick={() => navigate('/login')}
            icon={<Lock className="w-6 h-6" />}
          />
        </div>

        {/* Features */}
        <div className="mt-20">
          <h3 className="text-3xl sm:text-4xl font-bold tracking-tight text-ink-900 text-center">Engineered like a product, not a prototype</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
            {[
              { icon: Zap, title: 'Vendor lifecycle, complete', desc: 'Registration, approval, OTP, username + password, profile, sessions — one continuous flow.' },
              { icon: BarChart3, title: 'Real-time analytics', desc: 'Live compliance, risk distribution and domain breakdowns computed per vendor.' },
              { icon: Shield, title: 'Evidence-grade audits', desc: 'Findings carry rule, severity, evidence line, remediation and framework mapping.' },
              { icon: Mail, title: 'Operational email', desc: 'OTP, approval and notification flows backed by the email service.' },
              { icon: Users, title: 'Isolated multi-tenancy', desc: 'Vendors only ever see their own configurations and audits.' },
              { icon: CheckCircle, title: 'Designer reports', desc: 'Confidential-styled PDFs with cover, executive summary and appendices.' },
            ].map((f, i) => (
              <div key={i} className="tatva-card p-7">
                <div className="w-11 h-11 rounded-xl bg-ink-950 text-white flex items-center justify-center mb-5"><f.icon className="w-5 h-5" /></div>
                <h4 className="text-lg font-bold text-ink-900">{f.title}</h4>
                <p className="text-sm font-medium text-ink-500 mt-2 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* How it works */}
        <div className="tatva-card p-10 mt-16">
          <h3 className="text-3xl font-bold tracking-tight text-ink-900 text-center">How it works</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mt-10">
            {[
              { n: '01', t: 'Register', d: 'Vendor submits company details.' },
              { n: '02', t: 'Approve', d: 'Admin reviews and approves.' },
              { n: '03', t: 'Login', d: 'OTP first, then OTP or password.' },
              { n: '04', t: 'Audit', d: 'Upload configs, get findings + PDF.' },
            ].map((s) => (
              <div key={s.n} className="text-center">
                <div className="text-5xl font-bold tracking-tight text-ink-900">{s.n}</div>
                <div className="mt-2 text-base font-bold text-ink-900">{s.t}</div>
                <div className="mt-1 text-sm font-medium text-ink-500">{s.d}</div>
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer className="border-t border-line bg-white mt-4">
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <VajraMark className="w-6 h-6" />
            <span className="text-sm font-bold text-ink-900">TATVA by Team Vajracore</span>
          </div>
          <div className="text-xs font-semibold text-ink-500">Enterprise Security | Vendor Management | Compliance Auditing</div>
        </div>
      </footer>
    </div>
  );
}

function PortalCard({ eyebrow, title, desc, points, cta, dark, onClick, icon }: {
  eyebrow: string; title: string; desc: string; points: string[]; cta: string; dark?: boolean; onClick: () => void; icon: React.ReactNode;
}) {
  return (
    <div className={`tatva-card p-8 flex flex-col ${dark ? '!bg-ink-950 !border-ink-950 text-white' : ''}`}>
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-5 ${dark ? 'bg-white text-ink-950' : 'bg-ink-950 text-white'}`}>{icon}</div>
      <div className={`text-[11px] font-bold tracking-[0.28em] ${dark ? 'text-white/60' : 'text-ink-500'}`}>{eyebrow}</div>
      <h3 className={`text-2xl font-bold tracking-tight mt-2 ${dark ? 'text-white' : 'text-ink-900'}`}>{title}</h3>
      <p className={`text-sm font-medium mt-3 leading-relaxed ${dark ? 'text-white/70' : 'text-ink-500'}`}>{desc}</p>
      <ul className="mt-5 space-y-2">
        {points.map((p) => (
          <li key={p} className={`flex items-start gap-2 text-sm font-semibold ${dark ? 'text-white/85' : 'text-ink-900'}`}>
            <CheckCircle className={`w-4 h-4 mt-0.5 ${dark ? 'text-white' : 'text-ink-900'}`} /><span>{p}</span>
          </li>
        ))}
      </ul>
      <button onClick={onClick} className={`mt-7 w-full flex items-center justify-between px-5 py-3.5 rounded-xl text-sm ${dark ? 'bg-white text-ink-950 hover:bg-mist-100' : 'btn-ink rounded-xl'}`}>
        <span>{cta}</span><ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
}
