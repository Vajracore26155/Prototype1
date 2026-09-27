import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerVendor, type VendorRegistration } from '../services/vendorApi';
import VajraMark from '../components/VajraMark';

export default function VendorRegister() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<VendorRegistration>({
    email: '',
    company_name: '',
    contact_name: '',
    phone: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await registerVendor(formData);
      
      if (response.success) {
        setSuccess(true);
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/vendor/login', { state: { email: formData.email } });
        }, 3000);
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  if (success) {
    return (
      <div className="min-h-screen tatva-hero-bg flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <div className="tatva-card p-8 text-center">
            <div className="w-16 h-16 bg-ink-950 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-ink-900 mb-2">Registration Submitted!</h2>
            <p className="text-sm font-semibold text-ink-500 mb-4">
              Your vendor registration has been submitted for approval.
            </p>
            <div className="bg-mist-100 border border-line rounded-xl p-4 mb-6">
              <p className="text-sm font-semibold text-ink-900">
                <strong>What&apos;s Next?</strong><br />
                1. Admin will review your request<br />
                2. You&apos;ll receive an email notification<br />
                3. Once approved, you can login and upload configurations
              </p>
            </div>
            <p className="text-sm font-semibold text-ink-500">
              Redirecting to login page...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen tatva-hero-bg flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-white border border-line rounded-2xl mb-4 shadow-sm">
            <VajraMark className="w-10 h-10" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900 mb-1">Vendor Registration</h1>
          <p className="text-xs font-bold tracking-[0.24em] text-ink-500">TATVA BY TEAM VAJRACORE</p>
        </div>

        <div className="tatva-card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-white border border-ink-900 text-ink-900 px-4 py-3 rounded-xl text-sm font-bold">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="company_name" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                Company Name *
              </label>
              <input
                type="text"
                id="company_name"
                name="company_name"
                required
                value={formData.company_name}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-line rounded-xl font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900"
                placeholder="ACME Corporation"
              />
            </div>

            <div>
              <label htmlFor="contact_name" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                Contact Name *
              </label>
              <input
                type="text"
                id="contact_name"
                name="contact_name"
                required
                value={formData.contact_name}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-line rounded-xl font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                Email Address *
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-line rounded-xl font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900"
                placeholder="vendor@company.com"
              />
              <p className="mt-1 text-xs font-semibold text-ink-500">You&apos;ll receive OTP codes at this email</p>
            </div>

            <div>
              <label htmlFor="phone" className="block text-xs font-bold uppercase tracking-wide text-ink-900 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-line rounded-xl font-semibold text-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900"
                placeholder="+1-555-0100"
              />
            </div>

            <div className="bg-mist-100 border border-line rounded-xl p-4">
              <div className="text-sm font-semibold text-ink-900">
                <p className="font-bold mb-1">Approval Process</p>
                <p className="text-ink-500">Your registration will be reviewed by the admin. You&apos;ll receive an email once your account is approved.</p>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-ink w-full py-3 px-4 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Submitting...' : 'Submit Registration'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link
              to="/vendor/login"
              className="block text-sm text-ink-900 hover:underline font-bold"
            >
              Already registered? Login with OTP
            </Link>
            <Link
              to="/"
              className="block text-xs text-ink-500 hover:text-ink-950 font-bold mt-2"
            >
              ← Back to home
            </Link>
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
