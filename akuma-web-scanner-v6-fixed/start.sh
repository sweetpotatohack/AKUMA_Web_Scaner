#!/bin/bash

echo "🚀 Starting AKUMA Web Scanner v6.0 - Ultimate Security Arsenal"
echo "=================================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Create SSL directory for Nginx
mkdir -p nginx/ssl

# Generate self-signed SSL certificates if they don't exist
if [ ! -f nginx/ssl/nginx.crt ]; then
    echo "🔐 Generating self-signed SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/nginx.key \
        -out nginx/ssl/nginx.crt \
        -subj "/C=US/ST=Cyber/L=Space/O=AKUMA/OU=Security/CN=localhost"
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Clean up old volumes if requested
if [ "$1" = "--clean" ]; then
    echo "🧹 Cleaning up old data..."
    docker-compose down -v
    docker system prune -f
fi

# Build and start all services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Check health
echo ""
echo "🏥 Health Checks:"
echo "Backend API: $(curl -s http://localhost:8000/api/health | jq -r '.status // "unreachable"')"
echo "Frontend: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001)"
echo "Scanner: $(curl -s http://localhost:5000/health | jq -r '.status // "unreachable"')"

echo ""
echo "✅ AKUMA Web Scanner v6.0 is ready!"
echo "=================================================================="
echo "🌐 Web Interface: http://localhost:3001"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📊 Grafana Dashboard: http://localhost:3000 (admin/cyberpunk2077)"
echo "📈 Prometheus Metrics: http://localhost:9090"
echo "🔍 Scanner API: http://localhost:5000"
echo ""
echo "🎯 Quick Start:"
echo "1. Open http://localhost:3001 in your browser"
echo "2. Go to 'Create Scan' tab"
echo "3. Enter target URLs and start scanning"
echo "4. Monitor results in 'View Scans' tab"
echo "5. View advanced metrics in Grafana"
echo ""
echo "📝 Logs: docker-compose logs -f [service-name]"
echo "🛑 Stop: docker-compose down"
echo "=================================================================="
