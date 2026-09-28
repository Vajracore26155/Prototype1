import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { requestVendorOTP, verifyVendorOTP, vendorPasswordLogin } from '../services/vendorApi';
import VajraMark from '../components/VajraMark';

export default function VendorLogin() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Tab state
  const [loginMethod, setLoginMethod] = useState<'otp' | 'password'>('otp');
  
  // OTP login state
  const [otpStep, setOtpStep] = useState<'email' | 'otp'>('email');
  const [otpEmail, setOtpEmail] = useState(location.state?.email || '');
  const [otpCode, setOtpCode] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  
  // Password login state
  const [passwordEmail, setPasswordEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Common state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // OTP Login Handlers
  const handleRequestOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await requestVendorOTP({ vendor_email: otpEmail });
      
      if (response.success) {
        setOtpSent(true);
        setOtpStep('otp');
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || 'Failed to send OTP. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await verifyVendorOTP({
        vendor_email: otpEmail,
        otp_code: otpCode,
      });
      
      if (response.success) {
        navigate('/vendor/dashboard');
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || 'Invalid OTP code. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setOtpCode('');
    setError('');
    await handleRequestOTP(new Event('submit') as any);
  };

  // Password Login Handler
  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await vendorPasswordLogin({
        email: passwordEmail,
        password: password,
      });
      
      if (response.success) {
        navigate('/vendor/dashboard');
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || 'Login failed. Please check your credentials.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen tatva-hero-bg flex items-center justify-center px-4 py-10">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-white border border-line rounded-2xl mb-4 shadow-sm">
            <VajraMark className="w-10 h-10" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900 mb-1">Vendor Login</h1>
          <p className="text-xs font-bold tracking-[0.24em] text-ink-500">TATVA BY TEAM VAJRACORE</p>
        </div>

        <div className="tatva-card overflow-hidden">
          {/* Login Method Tabs */}
          <div className="flex border-b border-line">
            <button
              onClick={() => {
                setLoginMethod('otp');
                setError('');
              }}
              className={`flex-1 py-4 px-4 text-sm font-bold transition-colors ${
                loginMethod === 'otp'
                  ? 'bg-ink-950 text-white'
                  : 'text-ink-500 hover:text-ink-900'
              }`}
            >
              OTP Login
            </button>
            <button
              onClick={() => {
                setLoginMethod('password');
                setError('');
              }}
              className={`flex-1 py-4 px-4 text-sm font-bold transition-colors ${
                loginMethod === 'password'
                  ? 'bg-ink-950 text-white'
                  : 'text-ink-500 hover:text-ink-900'
              }`}
            >
              Password Login
            </button>
          </div>

          <div className="p-8">
            {/* OTP Login Form */}
            {loginMethod === 'otp' && (
              otpStep === 'email' ? (
                <form onSubmit={handleRequestOTP} className="space-y-6">
                  {error && (
                    <div className="bg-white border border-ink-900 text-ink-900 px-4 py-3 rounded-xl text-sm font-bold">
                      {error}
                    </div>
                  )}

                  <div>
                    <label htmlFor="email" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      required
                      value={otpEmail}
                      onChange={(e) => setOtpEmail(e.target.value)}
                      className="w-full px-4 py-3 border border-line rounded-xl font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900"
                      placeholder="vendor@company.com"
                      autoFocus
                    />
                  </div>

                  <div className="bg-mist-100 border border-line rounded-xl p-4">
                    <div className="flex items-start">
                      <div className="text-sm text-ink-900">
                        <p className="font-bold mb-1">Email-Based Authentication</p>
                        <p className="font-medium text-ink-500">We&apos;ll send a 6-digit OTP code to your email. The code expires in 10 minutes.</p>
                      </div>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-ink w-full py-3 px-4 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Sending OTP...' : 'Send OTP Code'}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOTP} className="space-y-6">
                  {error && (
                    <div className="bg-white border border-ink-900 text-ink-900 px-4 py-3 rounded-xl text-sm font-bold">
                      {error}
                    </div>
                  )}

                  {otpSent && (
                    <div className="bg-mist-100 border border-line text-ink-900 px-4 py-3 rounded-xl text-sm font-bold">
                      <strong>OTP Sent!</strong> Check your email for the 6-digit code.
                    </div>
                  )}

                  <div>
                    <label htmlFor="otp" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                      OTP Code
                    </label>
                    <input
                      type="text"
                      id="otp"
                      required
                      maxLength={6}
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                      className="w-full px-4 py-3 border border-line rounded-xl font-mono focus:outline-none focus:ring-2 focus:ring-ink-900 text-center text-2xl tracking-widest font-bold text-ink-900"
                      placeholder="000000"
                      autoFocus
                    />
                    <p className="mt-2 text-xs font-semibold text-ink-500 text-center">
                      Code sent to: <strong className="text-ink-900">{otpEmail}</strong>
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-sm font-bold">
                    <button
                      type="button"
                      onClick={() => setOtpStep('email')}
                      className="text-ink-500 hover:text-ink-900"
                    >
                      ← Change email
                    </button>
                    <button
                      type="button"
                      onClick={handleResendOTP}
                      disabled={loading}
                      className="text-ink-900 hover:underline disabled:opacity-50"
                    >
                      Resend OTP
                    </button>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || otpCode.length !== 6}
                    className="btn-ink w-full py-3 px-4 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Verifying...' : 'Verify & Login'}
                  </button>
                </form>
              )
            )}

            {/* Password Login Form */}
            {loginMethod === 'password' && (
              <form onSubmit={handlePasswordLogin} className="space-y-6">
                {error && (
                  <div className="bg-white border border-ink-900 text-ink-900 px-4 py-3 rounded-xl text-sm font-bold">
                    {error}
                  </div>
                )}

                <div>
                  <label htmlFor="password-email" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="password-email"
                    required
                    value={passwordEmail}
                    onChange={(e) => setPasswordEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-line rounded-xl font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900"
                    placeholder="vendor@company.com"
                    autoFocus
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    id="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-line rounded-xl font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-ink w-full py-3 px-4 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Logging in...' : 'Login'}
                </button>
              </form>
            )}

            <div className="mt-6 p-4 bg-mist-100 border border-line rounded-xl">
              <p className="text-xs font-bold uppercase tracking-wide text-ink-500 mb-2">
                Demo Credentials (Password Login)
              </p>
              <p className="text-sm font-semibold text-ink-900">
                Email: <span className="font-mono">designteam2345@gmail.com</span>
              </p>
              <p className="text-sm font-semibold text-ink-900">
                Password: <span className="font-mono">demo@123</span>
              </p>
              <button
                type="button"
                onClick={() => {
                  setLoginMethod('password');
                  setPasswordEmail('designteam2345@gmail.com');
                  setPassword('demo@123');
                  setError('');
                }}
                className="mt-3 w-full py-2 px-4 rounded-xl text-sm font-bold bg-white border border-line text-ink-900 hover:bg-mist-50"
              >
                Use demo credentials
              </button>
            </div>

            <div className="mt-6 text-center space-y-2 border-t border-line pt-6">
              <Link
                to="/vendor/register"
                className="block text-sm text-ink-900 hover:underline font-bold"
              >
                Don&apos;t have an account? Register here
              </Link>
              <Link
                to="/"
                className="block text-xs text-ink-500 hover:text-ink-950 font-bold"
              >
                ← Back to home
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-xs font-bold text-ink-500">
            TATVA by Team Vajracore
          </p>
        </div>
      </div>
    </div>
  );
}
