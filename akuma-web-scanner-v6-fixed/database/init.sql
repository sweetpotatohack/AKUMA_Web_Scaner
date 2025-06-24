-- AKUMA Web Scanner v6.0 Database Schema

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create scans table
CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    targets TEXT[] NOT NULL,
    scan_type VARCHAR(50) NOT NULL,
    scan_modules TEXT[],
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    results JSONB NULL
);

-- Create vulnerabilities table
CREATE TABLE IF NOT EXISTS vulnerabilities (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(50) REFERENCES scans(scan_id),
    vuln_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    cvss_score DECIMAL(3,1),
    description TEXT,
    url VARCHAR(500),
    tool VARCHAR(50),
    template VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create findings table
CREATE TABLE IF NOT EXISTS findings (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(50) REFERENCES scans(scan_id),
    finding_type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    tool VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_scans_scan_id ON scans(scan_id);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_scan_id ON vulnerabilities(scan_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON findings(scan_id);
CREATE INDEX IF NOT EXISTS idx_findings_type ON findings(finding_type);

-- Insert demo admin user (password: admin123)
INSERT INTO users (username, email, password_hash) 
VALUES ('admin', 'admin@akuma.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4SJrADJ.76')
ON CONFLICT (username) DO NOTHING;

-- Insert demo scan data
INSERT INTO scans (scan_id, name, targets, scan_type, scan_modules, status, progress) 
VALUES (
    'demo-001', 
    'Demo Scan - Example.com', 
    ARRAY['https://example.com'], 
    'ultimate', 
    ARRAY['nmap', 'nuclei', 'subdomain_enum'],
    'completed',
    100
) ON CONFLICT (scan_id) DO NOTHING;

-- Insert demo vulnerabilities
INSERT INTO vulnerabilities (scan_id, vuln_id, title, severity, cvss_score, description, tool) 
VALUES 
    ('demo-001', 'vuln-001', 'SSL Certificate Expired', 'medium', 5.3, 'SSL certificate has expired', 'testssl'),
    ('demo-001', 'vuln-002', 'Information Disclosure', 'low', 3.1, 'Server version disclosure in headers', 'nmap'),
    ('demo-001', 'vuln-003', 'Missing Security Headers', 'medium', 4.3, 'Missing X-Frame-Options header', 'nuclei')
ON CONFLICT DO NOTHING;

-- Create view for scan summary
CREATE OR REPLACE VIEW scan_summary AS
SELECT 
    s.scan_id,
    s.name,
    s.status,
    s.progress,
    s.created_at,
    COUNT(v.id) as vulnerability_count,
    COUNT(CASE WHEN v.severity = 'critical' THEN 1 END) as critical_count,
    COUNT(CASE WHEN v.severity = 'high' THEN 1 END) as high_count,
    COUNT(CASE WHEN v.severity = 'medium' THEN 1 END) as medium_count,
    COUNT(CASE WHEN v.severity = 'low' THEN 1 END) as low_count
FROM scans s
LEFT JOIN vulnerabilities v ON s.scan_id = v.scan_id
GROUP BY s.scan_id, s.name, s.status, s.progress, s.created_at;
