import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, Upload, FileText, Brain } from 'lucide-react';

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
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-500" />
              <div>
                <h1 className="text-xl font-bold">SIH26155</h1>
                <p className="text-xs text-gray-400">Network Security Auditor</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="px-3 py-1 bg-green-900/30 border border-green-800 rounded-lg text-green-400 text-sm">
                <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                System Active
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4">
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-3 border-b-2 transition-colors ${
                    isActive(item.path)
                      ? 'border-blue-500 text-blue-400 bg-gray-700/50'
                      : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-700/30'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <p>© 2026 SIH26155 - AI-Driven Multi-Vendor Network Security Compliance Auditor</p>
            <p>Prototype v1.0.0</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
