import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import VendorRegister from './pages/VendorRegister';
import VendorLogin from './pages/VendorLogin';
import VendorDashboard from './pages/VendorDashboard';
import VendorDashboardEnhanced from './pages/VendorDashboardEnhanced';
import VendorUpload from './pages/VendorUpload';
import VendorUploadEnhanced from './pages/VendorUploadEnhanced';
import VendorConfiguration from './pages/VendorConfiguration';
import VendorAuditDetails from './pages/VendorAuditDetails';
import VendorSettings from './pages/VendorSettings';
import VendorConfigurations from './pages/VendorConfigurations';
import VendorConfigurationEnhanced from './pages/VendorConfigurationEnhanced';
import AdminVendors from './pages/AdminVendors';

function App() {
  return (
    <Router>
      <ToastProvider>
        <AuthProvider>
          <Routes>
            {/* Landing Page - First page users see */}
            <Route path="/" element={<LandingPage />} />
            
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            {/* Admin registration disabled on website — single fixed admin.
                New admins are created via terminal only. */}
            
            {/* Vendor public routes */}
            <Route path="/vendor/register" element={<VendorRegister />} />
            <Route path="/vendor/login" element={<VendorLogin />} />
            
            {/* Vendor protected routes */}
            <Route path="/vendor/dashboard" element={<VendorDashboardEnhanced />} />
            <Route path="/vendor/dashboard/legacy" element={<VendorDashboard />} />
            <Route path="/vendor/configurations" element={<VendorConfigurations />} />
            <Route path="/vendor/upload" element={<VendorUploadEnhanced />} />
            <Route path="/vendor/upload/legacy" element={<VendorUpload />} />
            <Route path="/vendor/configuration/:configId" element={<VendorConfiguration />} />
            <Route path="/vendor/audit/:auditId" element={<VendorAuditDetails />} />
            <Route path="/vendor/settings" element={<VendorSettings />} />
            
            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <AdminDashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/vendors"
              element={
                <ProtectedRoute>
                  <Layout>
                    <AdminVendors />
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </Router>
  );
}

export default App;
