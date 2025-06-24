import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [scans, setScans] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Form states
  const [scanForm, setScanForm] = useState({
    name: '',
    targets: '',
    scan_type: 'ultimate'
  });
  const [uploadFile, setUploadFile] = useState(null);

  // Fetch data on component mount
  useEffect(() => {
    fetchScans();
    fetchStats();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(() => {
      if (activeTab === 'dashboard') {
        fetchStats();
      }
      fetchScans();
    }, 5000);
    
    return () => clearInterval(interval);
  }, [activeTab]);

  const fetchScans = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/scans`);
      setScans(response.data);
    } catch (error) {
      console.error('Error fetching scans:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const handleCreateScan = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const targets = scanForm.targets.split('\n').filter(t => t.trim());
      const payload = {
        name: scanForm.name,
        targets: targets,
        scan_type: scanForm.scan_type,
        scan_modules: ['nmap', 'nuclei', 'subdomain_enum', 'directory_fuzzing']
      };

      const response = await axios.post(`${API_BASE}/api/scans`, payload);
      showMessage('success', `Scan "${response.data.name}" created successfully!`);
      setScanForm({ name: '', targets: '', scan_type: 'ultimate' });
      fetchScans();
      setActiveTab('scans');
    } catch (error) {
      showMessage('error', `Error creating scan: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      showMessage('error', 'Please select a file');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('name', `File Upload - ${uploadFile.name}`);
    formData.append('scan_type', 'ultimate');

    try {
      const response = await axios.post(`${API_BASE}/api/scans/upload`, formData);
      showMessage('success', `Scan created from file "${uploadFile.name}"!`);
      setUploadFile(null);
      fetchScans();
      setActiveTab('scans');
    } catch (error) {
      showMessage('error', `Error uploading file: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteScan = async (scanId) => {
    if (!window.confirm('Are you sure you want to delete this scan?')) return;

    try {
      await axios.delete(`${API_BASE}/api/scans/${scanId}`);
      showMessage('success', 'Scan deleted successfully!');
      fetchScans();
      fetchStats();
    } catch (error) {
      showMessage('error', `Error deleting scan: ${error.response?.data?.detail || error.message}`);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'running': return 'status-running';
      case 'completed': return 'status-completed';
      case 'pending': return 'status-pending';
      case 'failed': return 'status-failed';
      default: return '';
    }
  };

  const renderDashboard = () => (
    <div className="section">
      <h2>🚀 AKUMA Dashboard</h2>
      <div className="dashboard-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.total_scans || 0}</div>
          <div className="stat-label">Total Scans</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.running_scans || 0}</div>
          <div className="stat-label">Running Scans</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.completed_scans || 0}</div>
          <div className="stat-label">Completed Scans</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.total_vulnerabilities || 0}</div>
          <div className="stat-label">Vulnerabilities</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.critical_vulnerabilities || 0}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.high_vulnerabilities || 0}</div>
          <div className="stat-label">High Risk</div>
        </div>
      </div>
      
      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <a 
          href="http://localhost:3000" 
          target="_blank" 
          rel="noopener noreferrer"
          className="btn btn-secondary"
          style={{ marginRight: '1rem' }}
        >
          📊 Open Grafana
        </a>
        <a 
          href={`${API_BASE}/docs`} 
          target="_blank" 
          rel="noopener noreferrer"
          className="btn btn-secondary"
        >
          📚 API Documentation
        </a>
      </div>
    </div>
  );

  const renderCreateScan = () => (
    <div className="section">
      <h2>🎯 Create New Scan</h2>
      
      <div className="tabs">
        <button className="tab active">Manual Target Entry</button>
        <button className="tab" onClick={() => document.getElementById('file-upload-section').scrollIntoView()}>
          File Upload
        </button>
      </div>

      <form onSubmit={handleCreateScan}>
        <div className="form-group">
          <label>Scan Name</label>
          <input
            type="text"
            className="form-input"
            value={scanForm.name}
            onChange={(e) => setScanForm({...scanForm, name: e.target.value})}
            placeholder="Enter scan name"
            required
          />
        </div>

        <div className="form-group">
          <label>Targets (one per line)</label>
          <textarea
            className="form-input"
            rows="6"
            value={scanForm.targets}
            onChange={(e) => setScanForm({...scanForm, targets: e.target.value})}
            placeholder="https://example.com&#10;192.168.1.1&#10;subdomain.example.com"
            required
          />
        </div>

        <div className="form-group">
          <label>Scan Type</label>
          <select
            className="form-input"
            value={scanForm.scan_type}
            onChange={(e) => setScanForm({...scanForm, scan_type: e.target.value})}
          >
            <option value="ultimate">🚀 Ultimate Scan (All Modules)</option>
            <option value="quick">⚡ Quick Scan</option>
            <option value="deep">🔍 Deep Scan</option>
            <option value="web">🌐 Web Application Scan</option>
          </select>
        </div>

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Creating Scan...' : '🚀 Launch Scan'}
        </button>
      </form>

      <div id="file-upload-section" style={{ marginTop: '3rem' }}>
        <h3>📁 Upload Target File</h3>
        <form onSubmit={handleFileUpload}>
          <div className="file-upload" onClick={() => document.getElementById('file-input').click()}>
            <input
              id="file-input"
              type="file"
              accept=".txt,.csv,.json"
              onChange={(e) => setUploadFile(e.target.files[0])}
              style={{ display: 'none' }}
            />
            <p>
              {uploadFile ? `Selected: ${uploadFile.name}` : 'Click to select target file (.txt, .csv, .json)'}
            </p>
          </div>
          {uploadFile && (
            <button type="submit" className="btn" disabled={loading} style={{ marginTop: '1rem' }}>
              {loading ? 'Uploading...' : '📤 Upload & Scan'}
            </button>
          )}
        </form>
      </div>
    </div>
  );

  const renderScans = () => (
    <div className="section">
      <h2>📊 Scan Results</h2>
      
      {scans.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No scans found. Create your first scan!
        </div>
      ) : (
        <div className="scans-grid">
          {scans.map((scan) => (
            <div key={scan.id} className="scan-card">
              <div className="scan-header">
                <div className="scan-name">{scan.name}</div>
                <div className={`scan-status ${getStatusClass(scan.status)}`}>
                  {scan.status}
                </div>
              </div>
              
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${scan.progress}%` }}
                ></div>
              </div>
              
              <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#ccc' }}>
                <div>📅 Created: {formatDate(scan.created_at)}</div>
                <div>🎯 Targets: {scan.targets.join(', ')}</div>
                <div>📈 Progress: {scan.progress}%</div>
                <div>🔍 Type: {scan.scan_type}</div>
              </div>

              {scan.vulnerabilities && scan.vulnerabilities.length > 0 && (
                <div className="vuln-list">
                  <h4>🚨 Vulnerabilities Found: {scan.vulnerabilities.length}</h4>
                  {scan.vulnerabilities.slice(0, 3).map((vuln, idx) => (
                    <div key={idx} className={`vuln-item vuln-${vuln.severity}`}>
                      <div className="vuln-title">{vuln.title}</div>
                      <div className="vuln-meta">
                        <span>Severity: {vuln.severity.toUpperCase()}</span>
                        <span>CVSS: {vuln.cvss}</span>
                        <span>Tool: {vuln.tool}</span>
                      </div>
                    </div>
                  ))}
                  {scan.vulnerabilities.length > 3 && (
                    <div style={{ textAlign: 'center', color: '#666', marginTop: '0.5rem' }}>
                      ... and {scan.vulnerabilities.length - 3} more
                    </div>
                  )}
                </div>
              )}

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <a
                  href={`${API_BASE}/api/scans/${scan.id}/report`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                  style={{ flex: 1, textAlign: 'center', textDecoration: 'none' }}
                >
                  📄 View Report
                </a>
                <button
                  onClick={() => handleDeleteScan(scan.id)}
                  className="btn btn-danger"
                  style={{ flex: 1 }}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="app">
      <header className="header">
        <h1>🚀 AKUMA Web Scanner v6.0</h1>
        <div className="subtitle">Ultimate Security Arsenal - Advanced Vulnerability Scanner</div>
      </header>

      <nav className="nav">
        <button 
          className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={`nav-button ${activeTab === 'create' ? 'active' : ''}`}
          onClick={() => setActiveTab('create')}
        >
          🎯 Create Scan
        </button>
        <button 
          className={`nav-button ${activeTab === 'scans' ? 'active' : ''}`}
          onClick={() => setActiveTab('scans')}
        >
          📋 View Scans
        </button>
      </nav>

      <div className="container">
        {message.text && (
          <div className={`alert alert-${message.type}`}>
            {message.text}
          </div>
        )}

        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'create' && renderCreateScan()}
        {activeTab === 'scans' && renderScans()}
      </div>
    </div>
  );
}

export default App;
