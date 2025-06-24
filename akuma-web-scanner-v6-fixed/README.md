# 🚀 AKUMA Web Scanner v6.0 - Ultimate Security Arsenal

**Advanced Vulnerability Scanner with Comprehensive Security Testing**

## 🌟 Features

### 🎯 Scanning Capabilities
- **Network Scanning**: Comprehensive port scanning with Nmap
- **Vulnerability Detection**: Advanced vulnerability scanning with Nuclei
- **Subdomain Enumeration**: Discover subdomains with Subfinder
- **Directory Fuzzing**: Find hidden directories and files
- **Technology Detection**: Identify web technologies and frameworks
- **SSL/TLS Analysis**: Certificate and configuration testing

### 🔧 Integrated Tools
- **Nmap**: Network discovery and port scanning
- **Nuclei**: Fast vulnerability scanner with templates
- **Subfinder**: Subdomain discovery tool
- **TestSSL**: SSL/TLS testing
- **Custom modules**: Directory fuzzing, tech detection

### 📊 Visualization & Monitoring
- **React Web Interface**: Modern, responsive cyberpunk-themed UI
- **Grafana Dashboard**: Visual analytics for scan results
- **Prometheus Metrics**: Performance monitoring
- **Real-time Progress**: Live scan progress updates
- **Comprehensive Reports**: Detailed vulnerability reports

### 🏗️ Architecture
- **Microservices**: Scalable, containerized architecture
- **PostgreSQL**: Robust database for scan data
- **Redis**: Fast caching and task queuing
- **Nginx**: High-performance reverse proxy
- **Docker**: Easy deployment and scaling

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM recommended
- Linux/macOS/Windows with WSL2

### Installation

1. **Clone/Download the scanner**:
```bash
cd /root/AKUMA_Web_Scaner/akuma-web-scanner-v6-fixed
```

2. **Start the scanner**:
```bash
./start.sh
```

3. **Access the web interface**:
- Open http://localhost:3001 in your browser
- Create your first scan
- Monitor results in real-time

### Manual Setup
```bash
# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🌐 Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| **Web Interface** | http://localhost:3001 | Main scanner interface |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Grafana Dashboard** | http://localhost:3000 | Visualization (admin/cyberpunk2077) |
| **Prometheus Metrics** | http://localhost:9090 | Monitoring metrics |
| **Scanner API** | http://localhost:5000 | Internal scanner service |

## 📖 Usage Guide

### Creating Scans

#### Method 1: Web Interface
1. Navigate to http://localhost:3001
2. Click "Create Scan" tab
3. Enter scan name and targets
4. Select scan type (Ultimate/Quick/Deep/Web)
5. Click "Launch Scan"

#### Method 2: File Upload
1. Prepare a text file with targets (one per line)
2. Use the file upload section
3. Select your file and click "Upload & Scan"

#### Method 3: API
```bash
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Security Scan",
    "targets": ["https://example.com", "192.168.1.1"],
    "scan_type": "ultimate",
    "scan_modules": ["nmap", "nuclei", "subdomain_enum"]
  }'
```

### Scan Types

| Type | Description | Tools Used |
|------|-------------|------------|
| **Ultimate** | Complete security assessment | All tools |
| **Quick** | Fast basic scan | Nmap, basic checks |
| **Deep** | Thorough vulnerability scan | Nuclei, advanced tests |
| **Web** | Web application focused | HTTP-specific tools |

### Monitoring Results

#### Real-time Progress
- View live progress in the web interface
- Progress updates every 5 seconds
- Status indicators (Pending/Running/Completed/Failed)

#### Vulnerability Analysis
- Severity-based categorization (Critical/High/Medium/Low/Info)
- CVSS scoring
- Tool attribution
- Detailed descriptions

#### Advanced Visualization
- Grafana dashboards for Nmap data
- Network topology visualization
- Historical scan comparison
- Export capabilities

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://akuma:cyberpunk2077@postgres:5432/akuma_scanner

# Redis
REDIS_URL=redis://:cyberpunk2077@redis:6379/0

# Security
SECRET_KEY=your-secret-key-here

# Scanner
REDIS_HOST=redis
BACKEND_URL=http://backend:8000
```

### Customizing Scans
Edit `scanner/scanner.py` to:
- Add new scanning modules
- Modify scan parameters
- Integrate additional tools
- Customize result parsing

### Adding Tools
To add new security tools:

1. **Update scanner Dockerfile**:
```dockerfile
RUN apt-get install -y your-tool
```

2. **Create module in scanner.py**:
```python
def run_your_tool(self, target):
    # Tool implementation
    pass
```

3. **Add to scan modules**:
```python
elif module == 'your_tool':
    self.run_your_tool(target)
```

## 📊 API Reference

### Scan Management
```bash
# Create scan
POST /api/scans
{
  "name": "Scan Name",
  "targets": ["target1", "target2"],
  "scan_type": "ultimate"
}

# List scans
GET /api/scans

# Get scan details
GET /api/scans/{scan_id}

# Delete scan
DELETE /api/scans/{scan_id}

# Get vulnerabilities
GET /api/scans/{scan_id}/vulnerabilities

# Generate report
GET /api/scans/{scan_id}/report
```

### Upload Scans
```bash
# Upload target file
POST /api/scans/upload
Content-Type: multipart/form-data
- name: "Scan Name"
- scan_type: "ultimate"
- file: targets.txt
```

### Dashboard
```bash
# Get statistics
GET /api/dashboard/stats
```

## 🛠️ Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker status
docker info

# Restart services
docker-compose restart

# Check logs
docker-compose logs [service-name]
```

#### Frontend Not Loading
```bash
# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose restart frontend

# Check frontend logs
docker-compose logs frontend
```

#### Scan Failures
```bash
# Check scanner logs
docker-compose logs scanner

# Verify scanner health
curl http://localhost:5000/health

# Check Redis connection
docker-compose exec redis redis-cli ping
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats

# Increase Docker memory limit
# Reduce concurrent scans
# Optimize scan parameters
```

### Log Locations
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs [backend|frontend|scanner|postgres|redis]

# Follow logs
docker-compose logs -f --tail=100
```

## 🔒 Security Considerations

### Production Deployment
- Change default passwords
- Use strong SSL certificates
- Configure firewall rules
- Enable authentication
- Regular security updates

### Network Security
- Isolate scanner network
- Use VPN for remote access
- Monitor scan targets
- Respect rate limits

### Data Protection
- Encrypt sensitive data
- Regular database backups
- Access logging
- Data retention policies

## 🚀 Performance Optimization

### Scaling
```bash
# Scale scanner instances
docker-compose up --scale scanner=3

# Use external database
# Configure Redis cluster
# Load balancer setup
```

### Tuning
- Adjust scan timeouts
- Optimize database queries
- Configure Redis memory
- Network bandwidth management

## 📈 Monitoring & Metrics

### Grafana Dashboards
- Scan performance metrics
- Vulnerability trends
- System resource usage
- Network topology maps

### Prometheus Metrics
- Service health indicators
- Response times
- Error rates
- Custom business metrics

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone [repository-url]

# Development with hot reload
docker-compose -f docker-compose.dev.yml up

# Run tests
docker-compose exec backend python -m pytest
docker-compose exec frontend npm test
```

### Adding Features
1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📋 Changelog

### v6.0.0 (Current)
- ✅ Complete system rebuild
- ✅ Modern React frontend
- ✅ Advanced scanner engine
- ✅ Comprehensive API
- ✅ Docker containerization
- ✅ Grafana integration
- ✅ File upload support
- ✅ Real-time progress
- ✅ Multiple scan types

### Previous Versions
- v5.0: Enhanced scanning modules
- v4.0: Grafana integration
- v3.0: Web interface addition
- v2.0: Database integration
- v1.0: Initial release

## 📞 Support

### Documentation
- API Documentation: http://localhost:8000/docs
- Interactive API: http://localhost:8000/redoc

### Issues
- Check logs first
- Verify system requirements
- Search existing issues
- Report with full details

### Community
- Share scan configurations
- Contribute modules
- Report vulnerabilities
- Suggest improvements

---

**🚀 AKUMA Web Scanner v6.0 - Where Security Meets Excellence**

*Built with ❤️ for the cybersecurity community*
