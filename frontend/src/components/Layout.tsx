import { ReactNode, useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Shield, LayoutDashboard, FileText, User, LogOut, Building, ChevronDown } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'SUPER_ADMIN':
        return 'bg-purple-500/40 text-purple-900 border-purple-600/30';
      case 'ADMIN':
        return 'bg-indigo-500/40 text-indigo-900 border-indigo-600/30';
      case 'SECURITY_ANALYST':
        return 'bg-blue-500/40 text-blue-900 border-blue-600/30';
      case 'AUDITOR':
        return 'bg-cyan-500/40 text-cyan-900 border-cyan-600/30';
      default:
        return 'bg-neutral-500/40 text-neutral-900 border-neutral-600/30';
    }
  };

  const formatRole = (role: string) => {
    return role.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
  };
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  ];
  
  // Add Admin Dashboard and Vendor Management for admins
  const adminNavItems = user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN' 
    ? [
        { path: '/admin/dashboard', label: 'Admin Dashboard', icon: LayoutDashboard },
        { path: '/admin/vendors', label: 'Vendor Management', icon: Building }
      ]
    : [];
  
  const allNavItems = [...navItems, ...adminNavItems];
  
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
            
            <div className="flex items-center space-x-4">
              <div className="px-3 py-1.5 bg-emerald-500/40 backdrop-blur-xl border border-emerald-600/30 rounded-lg flex items-center space-x-2" style={{ boxShadow: '0 4px 16px -4px rgba(31, 38, 135, 0.15)' }}>
                <span className="inline-block w-2 h-2 bg-emerald-600 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></span>
                <span className="text-sm font-semibold text-emerald-900">System Active</span>
              </div>

              {/* User Profile Dropdown */}
              {user && (
                <div className="relative" ref={profileRef}>
                  <button
                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                    className="flex items-center space-x-3 px-4 py-2 bg-white/40 backdrop-blur-xl border border-white/30 rounded-xl hover:bg-white/60 transition-all"
                    style={{ boxShadow: '0 4px 16px -4px rgba(31, 38, 135, 0.15)' }}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div className="text-left">
                        <p className="text-sm font-semibold text-neutral-900">{user.full_name}</p>
                        <p className="text-xs text-neutral-600">{user.organization_name}</p>
                      </div>
                    </div>
                    <ChevronDown className={`w-4 h-4 text-neutral-600 transition-transform ${isProfileOpen ? 'rotate-180' : ''}`} />
                  </button>

                  {/* Dropdown Menu */}
                  {isProfileOpen && (
                    <div 
                      className="absolute right-0 mt-2 w-72 bg-white/95 backdrop-blur-2xl border border-white/50 rounded-xl shadow-2xl overflow-hidden"
                      style={{ boxShadow: '0 10px 40px -10px rgba(31, 38, 135, 0.3)' }}
                    >
                      {/* User Info */}
                      <div className="p-4 border-b border-neutral-200">
                        <div className="flex items-center space-x-3 mb-3">
                          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                            <User className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1">
                            <p className="font-bold text-neutral-900">{user.full_name}</p>
                            <p className="text-sm text-neutral-600">{user.email}</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2 text-neutral-700">
                            <Building className="w-4 h-4" />
                            <span className="text-sm font-medium">{user.organization_name}</span>
                          </div>
                          <span className={`px-2 py-1 text-xs font-semibold rounded-lg border backdrop-blur-xl ${getRoleBadgeColor(user.role)}`}>
                            {formatRole(user.role)}
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="p-2">
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center space-x-3 px-4 py-3 text-left text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <LogOut className="w-5 h-5" />
                          <span className="font-semibold">Sign Out</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="bg-white/40 backdrop-blur-2xl border-b border-white/30">
        <div className="container mx-auto px-6">
          <div className="flex space-x-1">
            {allNavItems.map((item) => {
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
