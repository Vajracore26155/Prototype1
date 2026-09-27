import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { isVendorLoggedIn, getVendorInfo } from '../services/vendorApi';
import { Settings, Lock, User, Mail, Phone } from 'lucide-react';
import BackButton from '../components/BackButton';

interface VendorProfile {
  vendor_id: string;
  email: string;
  username: string | null;
  company_name: string;
  contact_name: string;
  phone: string | null;
  email_verified: boolean;
  approval_status: string;
  has_password: boolean;
  created_at: string;
  updated_at: string;
}

export default function VendorSettings() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<VendorProfile | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');
  
  // Profile form
  const [contactName, setContactName] = useState('');
  const [phone, setPhone] = useState('');
  const [username, setUsername] = useState('');
  const [updatingProfile, setUpdatingProfile] = useState(false);
  
  // Password form
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);
  
  // Set Password form
  const [newUsername, setNewUsername] = useState('');
  const [newPasswordValue, setNewPasswordValue] = useState('');
  const [newPasswordFormError, setNewPasswordFormError] = useState('');
  const [settingPassword, setSettingPassword] = useState(false);

  useEffect(() => {
    if (!isVendorLoggedIn()) {
      navigate('/vendor/login');
      return;
    }

    loadProfile();
  }, [navigate]);

  const loadProfile = async () => {
    try {
      const vendorInfo = getVendorInfo();
      if (!vendorInfo) {
        throw new Error('Vendor info not found');
      }

      // Fetch profile data from backend
      const token = localStorage.getItem('vendor_session_token');
      const response = await fetch(`/api/vendor/profile/${vendorInfo.vendor_id}`, {
        headers: {
          'X-Vendor-Session-Token': token || '',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load profile');
      }

      const response_body = await response.json();
      const data = response_body.data || response_body;
      setProfile(data);
      setContactName(data.contact_name || '');
      setPhone(data.phone || '');
      setUsername(data.username || '');
    } catch (err: any) {
      setError(err.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setUpdatingProfile(true);

    try {
      const vendorInfo = getVendorInfo();
      if (!vendorInfo) throw new Error('Vendor info not found');

      const token = localStorage.getItem('vendor_session_token');
      const response = await fetch(`/api/vendor/profile/${vendorInfo.vendor_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-Vendor-Session-Token': token || '',
        },
        body: JSON.stringify({
          contact_name: contactName,
          phone: phone,
          username: username,
        }),
      });

      if (!response.ok) {
        const errorResponse = await response.json();
        const errorMsg = errorResponse.detail?.error?.message || errorResponse.detail || 'Failed to update profile';
        throw new Error(errorMsg);
      }

      await response.json();
      setSuccess('Profile updated successfully');
      await loadProfile();
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setUpdatingProfile(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setPasswordError('');
    setSuccess('');

    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('Passwords do not match');
      return;
    }

    setChangingPassword(true);

    try {
      const vendorInfo = getVendorInfo();
      if (!vendorInfo) throw new Error('Vendor info not found');

      const token = localStorage.getItem('vendor_session_token');
      const response = await fetch(`/api/vendor/change-password/${vendorInfo.vendor_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Vendor-Session-Token': token || '',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (!response.ok) {
        const errorResponse = await response.json();
        const errorMsg = errorResponse.detail?.error?.message || errorResponse.detail || 'Failed to change password';
        throw new Error(errorMsg);
      }

      setSuccess('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPasswordError(err.message || 'Failed to change password');
    } finally {
      setChangingPassword(false);
    }
  };

  const handleSetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setNewPasswordFormError('');
    setSuccess('');

    if (!newUsername) {
      setNewPasswordFormError('Username is required');
      return;
    }

    if (newPasswordValue.length < 8) {
      setNewPasswordFormError('Password must be at least 8 characters');
      return;
    }

    setSettingPassword(true);

    try {
      const vendorInfo = getVendorInfo();
      if (!vendorInfo) throw new Error('Vendor info not found');

      const token = localStorage.getItem('vendor_session_token');
      const response = await fetch(`/api/vendor/set-password/${vendorInfo.vendor_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Vendor-Session-Token': token || '',
        },
        body: JSON.stringify({
          username: newUsername,
          password: newPasswordValue,
        }),
      });

      if (!response.ok) {
        const errorResponse = await response.json();
        const errorMsg = errorResponse.detail?.error?.message || errorResponse.detail || 'Failed to set password';
        throw new Error(errorMsg);
      }

      setSuccess('Password set successfully! You can now login with username and password.');
      setNewUsername('');
      setNewPasswordValue('');
      await loadProfile();
    } catch (err: any) {
      setNewPasswordFormError(err.message || 'Failed to set password');
    } finally {
      setSettingPassword(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg- flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
          <p className="mt-4 text-gray-600">Loading your settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg- py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Back Button */}
        <BackButton />

        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center space-x-3 mb-2">
            <Settings className="w-8 h-8 text-ink-950" />
            <h1 className="text-3xl font-bold text-gray-900">Vendor Settings</h1>
          </div>
          <p className="text-gray-600 ml-11">Manage your profile and security settings</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Success Alert */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {success}
          </div>
        )}

        {/* Profile Info Card */}
        {profile && (
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Account Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-mist-100 rounded-lg p-4">
                <div className="text-xs text-ink-950 font-medium">Vendor ID</div>
                <div className="text-sm font-mono text-gray-900 mt-1">{profile.vendor_id}</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-xs text-blue-600 font-medium">Status</div>
                <div className="text-sm font-bold text-gray-900 mt-1">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    profile.approval_status === 'APPROVED'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {profile.approval_status}
                  </span>
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-xs text-purple-600 font-medium">Company</div>
                <div className="text-sm font-bold text-gray-900 mt-1">{profile.company_name}</div>
              </div>
              <div className="bg-pink-50 rounded-lg p-4">
                <div className="text-xs text-pink-600 font-medium">Email Verified</div>
                <div className="text-sm font-bold text-gray-900 mt-1">
                  {profile.email_verified ? (
                    <span className="text-green-600">✓ Verified</span>
                  ) : (
                    <span className="text-yellow-600">⏳ Pending</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('profile')}
            className={`pb-4 px-4 font-medium border-b-2 transition-colors ${
              activeTab === 'profile'
                ? 'border-indigo-600 text-ink-950'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2">
              <User className="w-4 h-4" />
              <span>Profile</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('password')}
            className={`pb-4 px-4 font-medium border-b-2 transition-colors ${
              activeTab === 'password'
                ? 'border-indigo-600 text-ink-950'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Lock className="w-4 h-4" />
              <span>Security</span>
            </div>
          </button>
        </div>

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Profile Information</h2>
            <form onSubmit={handleUpdateProfile} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                  <Mail className="w-4 h-4" />
                  <span>Email Address</span>
                </label>
                <input
                  type="email"
                  value={profile?.email || ''}
                  disabled
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
                <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Contact Name</label>
                <input
                  type="text"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ink-950 focus:border-indigo-500 transition-colors"
                  placeholder="Your name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                  <Phone className="w-4 h-4" />
                  <span>Phone Number</span>
                </label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ink-950 focus:border-indigo-500 transition-colors"
                  placeholder="+1-555-0100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ink-950 focus:border-indigo-500 transition-colors"
                  placeholder="For password-based login"
                />
                <p className="text-xs text-gray-500 mt-1">Optional: Used for password login</p>
              </div>

              <button
                type="submit"
                disabled={updatingProfile}
                className="w-full bg-ink-950 text-white py-3 px-4 rounded-lg font-medium hover:bg-black disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {updatingProfile ? 'Updating...' : 'Update Profile'}
              </button>
            </form>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'password' && (
          <div className="space-y-6">
            {/* Set Password Section */}
            {!profile?.has_password && (
              <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-yellow-500">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Set Up Password Login</h2>
                <p className="text-gray-600 mb-6">
                  You currently login using OTP codes sent to your email. Set up a password to also login with username and password.
                </p>

                <form onSubmit={handleSetPassword} className="space-y-4">
                  {newPasswordFormError && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                      {newPasswordFormError}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                    <input
                      type="text"
                      value={newUsername}
                      onChange={(e) => setNewUsername(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ink-950 focus:border-indigo-500 transition-colors"
                      placeholder="Choose a username"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                    <input
                      type="password"
                      value={newPasswordValue}
                      onChange={(e) => setNewPasswordValue(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ink-950 focus:border-indigo-500 transition-colors"
                      placeholder="At least 8 characters"
                    />
                    <p className="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
                  </div>

                  <button
                    type="submit"
                    disabled={settingPassword}
                    className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {settingPassword ? 'Setting Up...' : 'Set Password'}
                  </button>
                </form>
              </div>
            )}

            {/* Change Password Section */}
            {profile?.has_password && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Change Password</h2>

                <form onSubmit={handleChangePassword} className="space-y-4">
                  {passwordError && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                      {passwordError}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ink-950 focus:border-indigo-500 transition-colors"
                      placeholder="Enter your current password"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ink-950 focus:border-indigo-500 transition-colors"
                      placeholder="At least 8 characters"
                    />
                    <p className="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-ink-950 focus:border-indigo-500 transition-colors"
                      placeholder="Re-enter new password"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={changingPassword}
                    className="w-full bg-ink-950 text-white py-3 px-4 rounded-lg font-medium hover:bg-black disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {changingPassword ? 'Changing...' : 'Change Password'}
                  </button>
                </form>

                <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>💡 Tip:</strong> You can still use OTP login as a backup method for authentication.
                  </p>
                </div>
              </div>
            )}

            {/* Login Methods Info */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-line rounded-2xl p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Login Methods</h3>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    <div className="flex items-center justify-center h-6 w-6 rounded-full bg-ink-950 text-white text-sm font-bold">
                      1
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">OTP Login (Always Available)</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Request an OTP code via email and use it to login. This method is always available as a backup.
                    </p>
                  </div>
                </div>

                {profile?.has_password && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      <div className="flex items-center justify-center h-6 w-6 rounded-full bg-green-600 text-white text-sm font-bold">
                        2
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">Password Login</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        You have set up password login. Use your username and password to login quickly.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
