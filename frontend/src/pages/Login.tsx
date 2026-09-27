import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, AlertCircle, LogIn } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import VajraMark from '../components/VajraMark';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { showSuccess, showError } = useToast();

  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(formData.email, formData.password);
      showSuccess('Welcome back!', 'You have successfully logged in.');
      navigate('/dashboard');
    } catch (err: any) {
      const errorMessage = err.message || 'Login failed. Please try again.';
      setError(errorMessage);
      showError('Login Failed', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen tatva-hero-bg flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-white border border-line rounded-2xl mb-4 shadow-sm">
            <VajraMark className="w-12 h-12" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900 mb-1">TATVA</h1>
          <p className="text-[11px] font-bold tracking-[0.3em] text-ink-500">WHERE NETWORKS MEET SECURITY</p>
          <p className="text-xs font-bold text-ink-500 mt-2">Admin Login &bull; Team Vajracore</p>
        </div>

        <div className="tatva-card p-8">
          <h2 className="text-2xl font-bold tracking-tight text-ink-900 mb-6">Sign In</h2>

          {error && (
            <div className="mb-6 p-4 bg-white border border-ink-900 rounded-xl flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-ink-900 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-bold text-ink-900">{error}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail className="w-5 h-5 text-ink-500" />
                </div>
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 border border-line rounded-xl bg-white text-ink-900 placeholder:text-ink-500/60 font-semibold pl-12 focus:outline-none focus:ring-2 focus:ring-ink-900"
                  placeholder="you@example.com"
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-ink-500" />
                </div>
                <input
                  type="password"
                  id="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-3 border border-line rounded-xl bg-white text-ink-900 placeholder:text-ink-500/60 font-semibold pl-12 focus:outline-none focus:ring-2 focus:ring-ink-900"
                  placeholder="••••••••"
                  required
                  autoComplete="current-password"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-ink w-full flex items-center justify-center space-x-2 rounded-xl py-3.5 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>Sign In</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center border-t border-line pt-6">
            <Link
              to="/vendor/login"
              className="block text-ink-900 hover:underline font-bold text-sm"
            >
              Vendor Login (OTP)
            </Link>
            <Link
              to="/"
              className="block text-ink-500 hover:text-ink-950 font-bold text-xs mt-2"
            >
              ← Back to home
            </Link>
          </div>
        </div>

        <div className="mt-6 text-center text-xs font-bold text-ink-500">
          <p>TATVA by Team Vajracore</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
