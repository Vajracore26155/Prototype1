import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Configurations from './pages/Configurations';
import AuditResults from './pages/AuditResults';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/configurations" element={<Configurations />} />
          <Route path="/audit/:auditId" element={<AuditResults />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
