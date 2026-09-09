import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, Upload, FileText } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/upload', label: 'Upload', icon: Upload },
    { path: '/configurations', label: 'Configurations', icon: FileText },
  ];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-violet-100">
      {/* Header - Glass Effect */}
      <header className="header-glass sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/40 backdrop-blur-xl rounded-xl border border-white/30" style={{ boxShadow: '0 4px 16px -4px rgba(31, 38, 135, 0.15)' }}>
                <Shield className="w-7 h-7 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-neutral-900">Tatva</h1>
                <p className="text-xs text-neutral-700 font-medium">Network Security Compliance Auditor</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="px-3 py-1.5 bg-emerald-500/40 backdrop-blur-xl border border-emerald-600/30 rounded-lg flex items-center space-x-2" style={{ boxShadow: '0 4px 16px -4px rgba(31, 38, 135, 0.15)' }}>
                <span className="inline-block w-2 h-2 bg-emerald-600 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></span>
                <span className="text-sm font-semibold text-emerald-900">System Active</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="bg-white/40 backdrop-blur-2xl border-b border-white/30">
        <div className="container mx-auto px-6">
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-3 border-b-2 transition-all duration-200 ${
                    isActive(item.path)
                      ? 'border-indigo-600 text-indigo-900 bg-white/30 backdrop-blur-sm font-semibold'
                      : 'border-transparent text-neutral-700 hover:text-neutral-900 hover:bg-white/20 backdrop-blur-sm font-medium'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-white/40 backdrop-blur-2xl border-t border-white/30 mt-16">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-neutral-700">
            <p>© 2026 Tatva - AI-Driven Multi-Vendor Network Security Compliance Auditor</p>
            <p className="font-medium text-neutral-800">Version 1.0.0</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
