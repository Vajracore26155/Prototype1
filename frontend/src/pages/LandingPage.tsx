import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Users, Lock, ArrowRight, CheckCircle, Zap, BarChart3, Mail } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* Navigation Bar */}
      <nav className="bg-white/40 backdrop-blur-xl border-b border-white/30 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Tatva</h1>
              <p className="text-xs text-gray-600 font-medium">Network Security Compliance Auditor</p>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-20">
          <h2 className="text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Welcome to <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Tatva</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Secure Network Security Compliance Platform for Device Configuration Auditing
          </p>
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-green-100/50 border border-green-300 rounded-lg">
            <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-green-800">System Active</span>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-20">
          {/* Vendor Section - PRIMARY */}
          <div className="order-1 lg:order-1">
            <div className="bg-white/60 backdrop-blur-xl border-2 border-indigo-200 rounded-2xl p-10 shadow-xl hover:shadow-2xl transition-all">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-3 bg-indigo-100 rounded-xl">
                  <Users className="w-6 h-6 text-indigo-600" />
                </div>
                <h3 className="text-3xl font-bold text-gray-900">Vendor Portal</h3>
              </div>

              <p className="text-gray-600 mb-8">
                Device vendors can securely register and upload network device configurations for security compliance auditing.
              </p>

              <div className="space-y-3 mb-8">
                <button
                  onClick={() => navigate('/vendor/register')}
                  className="w-full flex items-center justify-between px-6 py-4 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-xl hover:shadow-lg transition-all group"
                >
                  <span className="font-semibold">Vendor Registration</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>

                <button
                  onClick={() => navigate('/vendor/login')}
                  className="w-full flex items-center justify-between px-6 py-4 bg-indigo-50 border-2 border-indigo-200 text-indigo-900 rounded-xl hover:bg-indigo-100 transition-all group"
                >
                  <span className="font-semibold">Vendor Login</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>

              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 space-y-2">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-indigo-900">
                    <strong>Secure Registration</strong> - Complete vendor information and await approval
                  </span>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-indigo-900">
                    <strong>Flexible Authentication</strong> - Login with OTP or credentials
                  </span>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-indigo-900">
                    <strong>File Upload</strong> - Upload device configurations for audit
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Admin Section - SECONDARY */}
          <div className="order-2 lg:order-2">
            <div className="bg-white/40 backdrop-blur-xl border-2 border-gray-200 rounded-2xl p-10 shadow-lg hover:shadow-xl transition-all">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-3 bg-gray-100 rounded-xl">
                  <Lock className="w-6 h-6 text-gray-700" />
                </div>
                <h3 className="text-3xl font-bold text-gray-900">Admin Portal</h3>
              </div>

              <p className="text-gray-600 mb-8">
                System administrators manage vendor access, approve registrations, and monitor compliance across the platform.
              </p>

              <button
                onClick={() => navigate('/login')}
                className="w-full flex items-center justify-between px-6 py-4 bg-gray-800 text-white rounded-xl hover:bg-gray-900 transition-all group mb-6"
              >
                <span className="font-semibold">Admin Login</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-2">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-gray-700 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-gray-900">
                    <strong>Vendor Approvals</strong> - Review and approve vendor registrations
                  </span>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-gray-700 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-gray-900">
                    <strong>Activity Monitoring</strong> - Track vendor uploads and sessions
                  </span>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-gray-700 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-gray-900">
                    <strong>Access Management</strong> - Control vendor account status
                  </span>
                </div>
              </div>

              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-xs text-yellow-900">
                  <strong>Note:</strong> Only authorized system administrators can access this portal. Use your admin credentials to login.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-20">
          <h3 className="text-3xl font-bold text-gray-900 text-center mb-12">System Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Zap,
                title: "Fast Registration",
                description: "Complete vendor registration in minutes with secure approval workflow"
              },
              {
                icon: Lock,
                title: "Secure Authentication",
                description: "OTP-based and username/password authentication options"
              },
              {
                icon: BarChart3,
                title: "Compliance Auditing",
                description: "Comprehensive security compliance auditing for network devices"
              },
              {
                icon: Mail,
                title: "Email Notifications",
                description: "Real-time notifications for registrations, approvals, and OTP codes"
              },
              {
                icon: Users,
                title: "Vendor Management",
                description: "Complete vendor lifecycle management with role-based access"
              },
              {
                icon: Shield,
                title: "Enterprise Security",
                description: "Organization isolation and comprehensive audit logging"
              }
            ].map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div key={idx} className="bg-white/50 backdrop-blur-sm border border-white/50 rounded-xl p-6 hover:bg-white/70 transition-all">
                  <div className="p-3 bg-indigo-100 rounded-lg w-fit mb-4">
                    <Icon className="w-6 h-6 text-indigo-600" />
                  </div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h4>
                  <p className="text-gray-600 text-sm">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white/60 backdrop-blur-xl border border-white/50 rounded-2xl p-10 mb-20">
          <h3 className="text-3xl font-bold text-gray-900 text-center mb-12">How It Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                step: "1",
                title: "Register",
                description: "Vendor submits registration with company details"
              },
              {
                step: "2",
                title: "Approval",
                description: "Admin reviews and approves vendor request"
              },
              {
                step: "3",
                title: "Login",
                description: "Vendor logs in with OTP or credentials"
              },
              {
                step: "4",
                title: "Audit",
                description: "Upload configs for security compliance audit"
              }
            ].map((item, idx) => (
              <div key={idx} className="text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold text-lg">{item.step}</span>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">{item.title}</h4>
                <p className="text-sm text-gray-600">{item.description}</p>
                {idx < 3 && <div className="hidden md:block absolute left-1/2 top-1/3 w-6 h-0.5 bg-indigo-300 -translate-x-1/2"></div>}
              </div>
            ))}
          </div>
        </div>

        {/* Footer CTA */}
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Ready to Get Started?</h3>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button
              onClick={() => navigate('/vendor/register')}
              className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
            >
              Register as Vendor
            </button>
            <button
              onClick={() => navigate('/login')}
              className="px-8 py-3 bg-gray-900 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
            >
              Admin Login
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/30 bg-white/20 backdrop-blur-xl mt-20 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-gray-600 text-sm">
          <p>© 2026 Tatva - AI-Driven Multi-Vendor Network Security Compliance Auditor</p>
          <p className="mt-2">Enterprise Security | Vendor Management | Compliance Auditing</p>
        </div>
      </div>
    </div>
  );
}
