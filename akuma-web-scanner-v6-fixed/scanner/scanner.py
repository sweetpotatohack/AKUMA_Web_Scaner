#!/usr/bin/env python3
"""
AKUMA Web Scanner v6.0 - Advanced Scanner Engine
Integrated security testing with multiple tools
"""

import os
import json
import time
import uuid
import asyncio
import subprocess
import requests
import redis
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')
SCAN_OUTPUT_DIR = '/app/scan_results'
NMAP_DATA_DIR = '/root/nmap-did-what/data'

# Create directories
Path(SCAN_OUTPUT_DIR).mkdir(exist_ok=True)
Path(NMAP_DATA_DIR).mkdir(parents=True, exist_ok=True)

# Redis connection
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    redis_client.ping()
    print("✅ Scanner Redis connected")
except Exception as e:
    print(f"❌ Scanner Redis connection failed: {e}")
    redis_client = None

class AKUMAScanner:
    def __init__(self, scan_id, targets, modules):
        self.scan_id = scan_id
        self.targets = targets
        self.modules = modules
        self.results = {
            'vulnerabilities': [],
            'open_ports': [],
            'directories': [],
            'subdomains': [],
            'technologies': []
        }
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] SCAN-{self.scan_id}: {message}")
        
    def update_progress(self, progress, status="running"):
        """Update scan progress via Redis"""
        try:
            if redis_client:
                scan_data = {
                    'progress': progress,
                    'status': status,
                    'last_updated': datetime.now().isoformat()
                }
                redis_client.setex(f"scan:{self.scan_id}", 3600, json.dumps(scan_data))
        except Exception as e:
            self.log(f"Failed to update progress: {e}")
    
    def run_nmap_scan(self, target):
        """Run Nmap scan with comprehensive options"""
        self.log(f"🔍 Running Nmap scan on {target}")
        
        try:
            # Create output files
            output_file = f"{SCAN_OUTPUT_DIR}/nmap_{self.scan_id}_{target.replace('://', '_').replace('/', '_')}"
            nmap_data_file = f"{NMAP_DATA_DIR}/nmap-result"
            
            # Comprehensive Nmap command
            cmd = [
                'nmap',
                '-sV',  # Version detection
                '-sC',  # Default scripts
                '-Pn',  # Skip ping
                '-p-',  # Scan all ports
                '--open',  # Only show open ports
                '--min-rate=5000',  # Fast scanning
                '--script=http-title,ssl-cert,http-server-header,http-methods',
                '-oA', output_file,  # Output all formats
                '-oX', f"{nmap_data_file}.xml",  # XML for nmap-did-what
                target
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.log(f"✅ Nmap scan completed for {target}")
                
                # Parse results
                self._parse_nmap_results(f"{output_file}.xml")
                
                # Process with nmap-to-sqlite for Grafana
                self._process_nmap_to_grafana(f"{nmap_data_file}.xml")
                
            else:
                self.log(f"❌ Nmap scan failed for {target}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Nmap scan timed out for {target}")
        except Exception as e:
            self.log(f"💥 Nmap scan error for {target}: {e}")
    
    def _parse_nmap_results(self, xml_file):
        """Parse Nmap XML results"""
        try:
            if not os.path.exists(xml_file):
                return
                
            # Simple XML parsing for open ports
            with open(xml_file, 'r') as f:
                content = f.read()
                
            # Extract open ports (basic parsing)
            import re
            port_pattern = r'<port protocol="(\w+)" portid="(\d+)">.*?<state state="open"'
            ports = re.findall(port_pattern, content, re.DOTALL)
            
            for protocol, port in ports:
                self.results['open_ports'].append({
                    'port': int(port),
                    'protocol': protocol,
                    'service': 'unknown',
                    'tool': 'nmap'
                })
                
            self.log(f"📊 Found {len(ports)} open ports")
            
        except Exception as e:
            self.log(f"❌ Failed to parse Nmap results: {e}")
    
    def _process_nmap_to_grafana(self, xml_file):
        """Process Nmap XML with nmap-to-sqlite for Grafana visualization"""
        try:
            if not os.path.exists(xml_file):
                self.log(f"⚠️ Nmap XML file not found: {xml_file}")
                return
                
            # Check if nmap-to-sqlite script exists
            nmap_script = "/root/nmap-did-what/nmap-to-sqlite.py"
            if not os.path.exists(nmap_script):
                self.log("⚠️ nmap-to-sqlite.py not found, skipping Grafana integration")
                return
                
            # Run nmap-to-sqlite
            cmd = [
                'python3', nmap_script,
                '--xml', xml_file,
                '--db', f"{NMAP_DATA_DIR}/nmap_results.db"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("✅ Nmap results processed for Grafana")
            else:
                self.log(f"⚠️ nmap-to-sqlite failed: {result.stderr}")
                
        except Exception as e:
            self.log(f"❌ Failed to process Nmap for Grafana: {e}")
    
    def run_nuclei_scan(self, target):
        """Run Nuclei vulnerability scanner"""
        self.log(f"🧬 Running Nuclei scan on {target}")
        
        try:
            output_file = f"{SCAN_OUTPUT_DIR}/nuclei_{self.scan_id}_{target.replace('://', '_').replace('/', '_')}.json"
            
            cmd = [
                'nuclei',
                '-u', target,
                '-j',  # JSON output
                '-o', output_file,
                '-silent',
                '-timeout', '30',
                '-retries', '2'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_file):
                self._parse_nuclei_results(output_file)
                self.log(f"✅ Nuclei scan completed for {target}")
            else:
                self.log(f"⚠️ Nuclei scan completed with no results for {target}")
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Nuclei scan timed out for {target}")
        except Exception as e:
            self.log(f"💥 Nuclei scan error for {target}: {e}")
    
    def _parse_nuclei_results(self, json_file):
        """Parse Nuclei JSON results"""
        try:
            with open(json_file, 'r') as f:
                for line in f:
                    if line.strip():
                        result = json.loads(line.strip())
                        
                        severity = result.get('info', {}).get('severity', 'info')
                        
                        vulnerability = {
                            'id': str(uuid.uuid4())[:8],
                            'title': result.get('info', {}).get('name', 'Unknown Vulnerability'),
                            'severity': severity,
                            'cvss': self._severity_to_cvss(severity),
                            'description': result.get('info', {}).get('description', ''),
                            'url': result.get('matched-at', ''),
                            'tool': 'nuclei',
                            'template': result.get('template-id', ''),
                            'found_at': datetime.now().isoformat()
                        }
                        
                        self.results['vulnerabilities'].append(vulnerability)
                        
        except Exception as e:
            self.log(f"❌ Failed to parse Nuclei results: {e}")
    
    def run_subdomain_enum(self, target):
        """Run subdomain enumeration"""
        self.log(f"🌐 Running subdomain enumeration for {target}")
        
        try:
            # Extract domain from URL
            import tldextract
            extracted = tldextract.extract(target)
            domain = f"{extracted.domain}.{extracted.suffix}"
            
            # Run subfinder if available
            output_file = f"{SCAN_OUTPUT_DIR}/subdomains_{self.scan_id}_{domain}.txt"
            
            cmd = ['subfinder', '-d', domain, '-o', output_file, '-silent']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    subdomains = [line.strip() for line in f if line.strip()]
                    
                for subdomain in subdomains[:10]:  # Limit to first 10
                    self.results['subdomains'].append({
                        'subdomain': subdomain,
                        'tool': 'subfinder'
                    })
                    
                self.log(f"✅ Found {len(subdomains)} subdomains")
            else:
                self.log(f"⚠️ Subfinder not available or no subdomains found")
                
        except Exception as e:
            self.log(f"💥 Subdomain enumeration error: {e}")
    
    def run_directory_fuzzing(self, target):
        """Run directory fuzzing"""
        self.log(f"📁 Running directory fuzzing on {target}")
        
        try:
            output_file = f"{SCAN_OUTPUT_DIR}/dirs_{self.scan_id}_{target.replace('://', '_').replace('/', '_')}.txt"
            
            # Common directories to check
            common_dirs = [
                'admin', 'login', 'wp-admin', 'phpmyadmin', 'backup',
                'config', 'test', 'dev', 'api', 'uploads', 'files'
            ]
            
            found_dirs = []
            
            for directory in common_dirs:
                try:
                    test_url = f"{target.rstrip('/')}/{directory}"
                    response = requests.get(test_url, timeout=10, allow_redirects=False)
                    
                    if response.status_code in [200, 301, 302, 403]:
                        found_dirs.append({
                            'path': f"/{directory}",
                            'status_code': response.status_code,
                            'tool': 'directory_fuzzer'
                        })
                        
                except:
                    continue
            
            self.results['directories'] = found_dirs
            self.log(f"✅ Found {len(found_dirs)} directories")
            
        except Exception as e:
            self.log(f"💥 Directory fuzzing error: {e}")
    
    def run_technology_detection(self, target):
        """Detect web technologies"""
        self.log(f"🔧 Detecting technologies for {target}")
        
        try:
            response = requests.get(target, timeout=10)
            headers = response.headers
            content = response.text[:1000]  # First 1KB
            
            technologies = []
            
            # Check server header
            if 'server' in headers:
                technologies.append({
                    'name': headers['server'],
                    'type': 'Web Server',
                    'tool': 'headers'
                })
            
            # Check for common frameworks
            if 'x-powered-by' in headers:
                technologies.append({
                    'name': headers['x-powered-by'],
                    'type': 'Framework',
                    'tool': 'headers'
                })
            
            # Simple content-based detection
            if 'wordpress' in content.lower():
                technologies.append({
                    'name': 'WordPress',
                    'type': 'CMS',
                    'tool': 'content_analysis'
                })
            
            if 'drupal' in content.lower():
                technologies.append({
                    'name': 'Drupal',
                    'type': 'CMS',
                    'tool': 'content_analysis'
                })
            
            self.results['technologies'] = technologies
            self.log(f"✅ Detected {len(technologies)} technologies")
            
        except Exception as e:
            self.log(f"💥 Technology detection error: {e}")
    
    def _severity_to_cvss(self, severity):
        """Convert severity to CVSS score"""
        severity_map = {
            'critical': 9.5,
            'high': 7.5,
            'medium': 5.5,
            'low': 3.5,
            'info': 1.0
        }
        return severity_map.get(severity.lower(), 1.0)
    
    def run_scan(self):
        """Main scan execution"""
        self.log("🚀 Starting AKUMA scan")
        self.update_progress(0, "running")
        
        total_targets = len(self.targets)
        modules_per_target = len(self.modules)
        total_tasks = total_targets * modules_per_target
        completed_tasks = 0
        
        for target in self.targets:
            self.log(f"🎯 Scanning target: {target}")
            
            for module in self.modules:
                try:
                    if module == 'nmap':
                        self.run_nmap_scan(target)
                    elif module == 'nuclei':
                        self.run_nuclei_scan(target)
                    elif module == 'subdomain_enum':
                        self.run_subdomain_enum(target)
                    elif module == 'directory_fuzzing':
                        self.run_directory_fuzzing(target)
                    elif module == 'tech_detection':
                        self.run_technology_detection(target)
                    
                    completed_tasks += 1
                    progress = int((completed_tasks / total_tasks) * 100)
                    self.update_progress(progress)
                    
                except Exception as e:
                    self.log(f"💥 Module {module} failed for {target}: {e}")
                    completed_tasks += 1
        
        self.update_progress(100, "completed")
        self.log("✅ Scan completed successfully")
        
        # Save final results
        self._save_results()
        
        return self.results
    
    def _save_results(self):
        """Save scan results to file and update backend"""
        try:
            # Save to file
            results_file = f"{SCAN_OUTPUT_DIR}/scan_{self.scan_id}_results.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            self.log(f"💾 Results saved to {results_file}")
            
            # Try to update backend via API
            try:
                payload = {
                    'scan_id': self.scan_id,
                    'results': self.results,
                    'status': 'completed'
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/api/scanner/update",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.log("✅ Backend updated successfully")
                else:
                    self.log(f"⚠️ Backend update failed: {response.status_code}")
                    
            except Exception as e:
                self.log(f"⚠️ Failed to update backend: {e}")
                
        except Exception as e:
            self.log(f"❌ Failed to save results: {e}")

# Flask API for scanner control
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'scanner': 'AKUMA v6.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/scan', methods=['POST'])
def start_scan():
    try:
        data = request.get_json()
        scan_id = data.get('scan_id')
        targets = data.get('targets', [])
        modules = data.get('modules', ['nmap', 'nuclei'])
        
        if not scan_id or not targets:
            return jsonify({'error': 'Missing scan_id or targets'}), 400
        
        # Start scan in background thread
        scanner = AKUMAScanner(scan_id, targets, modules)
        thread = threading.Thread(target=scanner.run_scan)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Scan started successfully',
            'scan_id': scan_id,
            'targets': targets,
            'modules': modules
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scan/<scan_id>/status')
def get_scan_status(scan_id):
    try:
        if redis_client:
            data = redis_client.get(f"scan:{scan_id}")
            if data:
                return jsonify(json.loads(data))
        
        return jsonify({'error': 'Scan not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 AKUMA Scanner v6.0 starting...")
    print(f"📁 Scan output directory: {SCAN_OUTPUT_DIR}")
    print(f"📊 Nmap data directory: {NMAP_DATA_DIR}")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
