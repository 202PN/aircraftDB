# Deployment and Operations Guide (DOU) - HangarStack

This guide provides comprehensive instructions for deploying, operating, and maintaining the HangarStack aircraft database application in production environments.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Deployment Strategies](#deployment-strategies)
5. [Environment Setup](#environment-setup)
6. [Application Deployment](#application-deployment)
7. [Confluent Cloud Configuration](#confluent-cloud-configuration)
8. [Monitoring & Alerting](#monitoring--alerting)
9. [Operations Procedures](#operations-procedures)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)
12. [Security](#security)
13. [Backup & Recovery](#backup--recovery)
14. [Scaling](#scaling)

## 🎯 Overview

HangarStack is a Flask-based web application with real-time event streaming via Confluent Cloud. This guide covers production deployment and operational procedures.

### Key Components
- **Web Application**: Flask-based aircraft database
- **Event Streaming**: Confluent Cloud for real-time analytics
- **Static Assets**: Aircraft images and manufacturer logos
- **Data Storage**: JSON-based aircraft database

### Production Requirements
- **Availability**: 99.9% uptime
- **Performance**: Sub-100ms response times
- **Scalability**: Auto-scaling based on demand
- **Security**: Enterprise-grade security measures

## 🏗️ Architecture

### System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Servers    │    │  Confluent Cloud│
│   (Nginx/ALB)   │◄──►│   (Gunicorn)     │◄──►│   (Kafka)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Static Assets  │
                       │   (CDN/S3)       │
                       └──────────────────┘
```

### Component Responsibilities
- **Load Balancer**: Traffic distribution and SSL termination
- **Web Servers**: Application hosting and request processing
- **Confluent Cloud**: Event streaming and real-time analytics
- **Static Assets**: Image and CSS file delivery
- **Monitoring**: Health checks and performance metrics

## ✅ Prerequisites

### Infrastructure Requirements
- **Cloud Platform**: AWS, GCP, or Azure
- **Container Platform**: Docker and Kubernetes (optional)
- **Load Balancer**: Application Load Balancer or Nginx
- **SSL Certificate**: Valid SSL certificate for HTTPS
- **Domain Name**: Registered domain for the application

### Software Requirements
- **Python**: 3.8 or higher
- **WSGI Server**: Gunicorn or uWSGI
- **Web Server**: Nginx (for reverse proxy)
- **Process Manager**: Systemd or Supervisor
- **Monitoring**: Prometheus, Grafana, or cloud monitoring

### Confluent Cloud Requirements
- **Confluent Cloud Account**: Production-ready cluster
- **API Keys**: Properly configured with appropriate permissions
- **Topics**: All required topics created and configured
- **Monitoring**: Confluent Cloud monitoring enabled

## 🚀 Deployment Strategies

### Strategy 1: Traditional Server Deployment
**Best for**: Small to medium deployments
**Pros**: Simple setup, cost-effective
**Cons**: Limited scalability, manual scaling

### Strategy 2: Container Deployment (Docker)
**Best for**: Medium deployments, CI/CD integration
**Pros**: Consistent environments, easy scaling
**Cons**: Additional complexity

### Strategy 3: Kubernetes Deployment
**Best for**: Large-scale, high-availability deployments
**Pros**: Auto-scaling, high availability, advanced orchestration
**Cons**: Complex setup, requires expertise

### Strategy 4: Serverless Deployment
**Best for**: Variable load, cost optimization
**Pros**: Auto-scaling, pay-per-use
**Cons**: Cold starts, vendor lock-in

## 🔧 Environment Setup

### Production Environment Variables
```env
# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-super-secret-production-key
HOST=0.0.0.0
PORT=5000

# Confluent Cloud Configuration
KAFKA_BOOTSTRAP_SERVERS=your-production-cluster:9092
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_USERNAME=your-production-api-key
KAFKA_PASSWORD=your-production-api-secret

# Database Configuration (if using SQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# Monitoring Configuration
PROMETHEUS_ENDPOINT=http://prometheus:9090
GRAFANA_ENDPOINT=http://grafana:3000

# Security Configuration
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT=1000/hour
```

### System Requirements
```bash
# Minimum System Requirements
CPU: 2 cores
RAM: 4GB
Storage: 20GB SSD
Network: 100Mbps

# Recommended System Requirements
CPU: 4+ cores
RAM: 8GB+
Storage: 50GB+ SSD
Network: 1Gbps+
```

## 📦 Application Deployment

### Method 1: Traditional Server Deployment

#### Step 1: Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx supervisor -y

# Create application user
sudo useradd -m -s /bin/bash hangarstack
sudo usermod -aG sudo hangarstack
```

#### Step 2: Application Setup
```bash
# Switch to application user
sudo su - hangarstack

# Clone application
git clone https://github.com/your-repo/hangarstack.git
cd hangarstack

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements.txt
pip install gunicorn

# Set up environment variables
cp .env.example .env
# Edit .env with production values
```

#### Step 3: Gunicorn Configuration
```bash
# Create Gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
EOF
```

#### Step 4: Systemd Service
```bash
# Create systemd service file
sudo tee /etc/systemd/system/hangarstack.service << EOF
[Unit]
Description=HangarStack Aircraft Database
After=network.target

[Service]
Type=notify
User=hangarstack
Group=hangarstack
WorkingDirectory=/home/hangarstack/hangarstack
Environment=PATH=/home/hangarstack/hangarstack/venv/bin
ExecStart=/home/hangarstack/hangarstack/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable hangarstack
sudo systemctl start hangarstack
```

#### Step 5: Nginx Configuration
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/hangarstack << EOF
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    client_max_body_size 10M;
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /home/hangarstack/hangarstack/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/hangarstack /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Method 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 hangarstack && chown -R hangarstack:hangarstack /app
USER hangarstack

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  hangarstack:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS}
      - KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL}
      - KAFKA_USERNAME=${KAFKA_USERNAME}
      - KAFKA_PASSWORD=${KAFKA_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./static:/app/static
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - hangarstack
    restart: unless-stopped
```

## ☁️ Confluent Cloud Configuration

### Production Cluster Setup
```bash
# Create production environment
confluent environment create hangarstack-prod

# Create production cluster
confluent kafka cluster create hangarstack-prod-cluster \
  --cloud aws \
  --region us-east-1 \
  --type dedicated \
  --cku 1

# Create API keys with appropriate permissions
confluent api-key create --resource CLUSTER_ID --description "HangarStack Production"
```

### Topic Configuration
```bash
# Create topics with proper configuration
confluent kafka topic create hangarstack.aircraft.views \
  --cluster CLUSTER_ID \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete

confluent kafka topic create hangarstack.user.activity \
  --cluster CLUSTER_ID \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=2592000000 \
  --config cleanup.policy=delete

# Repeat for other topics...
```

### Schema Registry Setup
```bash
# Enable Schema Registry
confluent schema-registry cluster enable --cloud aws --region us-east-1

# Create schemas for events
confluent schema-registry schema create --subject hangarstack.aircraft.views-value \
  --schema aircraft_view_schema.json \
  --type JSON
```

## 📊 Monitoring & Alerting

### Application Monitoring

#### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check Confluent Cloud connection
        producer = HangarStackProducer()
        producer.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'confluent_cloud': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503
```

#### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
REQUEST_COUNT = Counter('hangarstack_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('hangarstack_request_duration_seconds', 'Request latency')
EVENT_COUNT = Counter('hangarstack_events_total', 'Total events', ['event_type'])

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Add metrics to application
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    REQUEST_LATENCY.observe(time.time() - request.start_time)
    return response
```

### Confluent Cloud Monitoring

#### Cluster Metrics
- **Broker Health**: Monitor broker status and performance
- **Topic Metrics**: Track message throughput and lag
- **Consumer Groups**: Monitor consumer health and performance
- **Network**: Track connection and bandwidth usage

#### Alerting Rules
```yaml
# Prometheus alerting rules
groups:
  - name: hangarstack
    rules:
      - alert: HighRequestLatency
        expr: histogram_quantile(0.95, hangarstack_request_duration_seconds) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency detected"
          
      - alert: ConfluentCloudDown
        expr: up{job="hangarstack"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "HangarStack application is down"
```

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('hangarstack.log', maxBytes=10000000, backupCount=5),
            logging.StreamHandler()
        ]
    )
```

## 🔄 Operations Procedures

### Deployment Procedures

#### Blue-Green Deployment
```bash
#!/bin/bash
# blue-green-deploy.sh

# Deploy to blue environment
echo "Deploying to blue environment..."
docker-compose -f docker-compose.blue.yml up -d

# Run health checks
echo "Running health checks..."
for i in {1..30}; do
    if curl -f http://blue.yourdomain.com/health; then
        echo "Blue environment healthy"
        break
    fi
    sleep 2
done

# Switch traffic to blue
echo "Switching traffic to blue..."
# Update load balancer configuration

# Deploy to green environment
echo "Deploying to green environment..."
docker-compose -f docker-compose.green.yml up -d

# Keep blue as backup
echo "Blue-green deployment completed"
```

#### Rolling Deployment
```bash
#!/bin/bash
# rolling-deploy.sh

# Update deployment with new image
kubectl set image deployment/hangarstack hangarstack=your-registry/hangarstack:latest

# Monitor rollout
kubectl rollout status deployment/hangarstack

# Verify deployment
kubectl get pods -l app=hangarstack
```

### Backup Procedures

#### Application Data Backup
```bash
#!/bin/bash
# backup.sh

# Create backup directory
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup application data
cp -r /app/data $BACKUP_DIR/
cp -r /app/static $BACKUP_DIR/

# Backup configuration
cp /app/.env $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR

# Upload to cloud storage
aws s3 cp $BACKUP_DIR.tar.gz s3://your-backup-bucket/

# Clean up local backup
rm -rf $BACKUP_DIR $BACKUP_DIR.tar.gz
```

#### Confluent Cloud Backup
```bash
# Export topic data
confluent kafka topic export hangarstack.aircraft.views \
  --cluster CLUSTER_ID \
  --output-file aircraft_views_backup.json

# Export schemas
confluent schema-registry schema export --subject hangarstack.aircraft.views-value
```

### Recovery Procedures

#### Application Recovery
```bash
#!/bin/bash
# recovery.sh

# Stop application
systemctl stop hangarstack

# Restore from backup
BACKUP_FILE="/backups/20240101_120000.tar.gz"
tar -xzf $BACKUP_FILE -C /tmp/

# Restore data
cp -r /tmp/backup/data/* /app/data/
cp -r /tmp/backup/static/* /app/static/
cp /tmp/backup/.env /app/

# Start application
systemctl start hangarstack

# Verify recovery
curl -f http://localhost:8000/health
```

## 🛠️ Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check service status
systemctl status hangarstack

# Check logs
journalctl -u hangarstack -f

# Check port availability
netstat -tlnp | grep :8000

# Check permissions
ls -la /home/hangarstack/hangarstack/
```

#### Confluent Cloud Connection Issues
```bash
# Test connection
python test_confluent.py

# Check credentials
cat .env | grep KAFKA

# Verify cluster status
confluent kafka cluster describe CLUSTER_ID

# Check API key permissions
confluent api-key list
```

#### High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Check Gunicorn workers
ps aux | grep gunicorn

# Restart application
systemctl restart hangarstack
```

#### Slow Response Times
```bash
# Check CPU usage
top
htop

# Check disk I/O
iostat -x 1

# Check network
iftop

# Check application logs
tail -f /var/log/hangarstack/application.log
```

### Diagnostic Commands
```bash
# System diagnostics
dmesg | tail
df -h
free -h
uptime

# Network diagnostics
ping -c 4 yourdomain.com
traceroute yourdomain.com
curl -I https://yourdomain.com

# Application diagnostics
curl -f http://localhost:8000/health
curl -f http://localhost:8000/metrics
```

## 🔧 Maintenance

### Regular Maintenance Tasks

#### Daily Tasks
```bash
# Check application health
curl -f http://yourdomain.com/health

# Check logs for errors
grep -i error /var/log/hangarstack/application.log | tail -20

# Check disk space
df -h

# Check memory usage
free -h
```

#### Weekly Tasks
```bash
# Run comprehensive tests
python test_confluent.py

# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean up old logs
find /var/log -name "*.log" -mtime +7 -delete

# Check backup status
ls -la /backups/
```

#### Monthly Tasks
```bash
# Review and rotate API keys
confluent api-key list
confluent api-key create --resource CLUSTER_ID

# Update application dependencies
pip install --upgrade -r requirements.txt

# Review monitoring metrics
# Check Grafana dashboards

# Security audit
# Review access logs and security events
```

### Performance Optimization

#### Application Optimization
```python
# Enable caching
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@app.route('/aircraft/<designation>')
@cache.cached(timeout=300)
def aircraft_detail(designation):
    # Aircraft detail logic
    pass
```

#### Database Optimization
```sql
-- If using SQL database
CREATE INDEX idx_aircraft_designation ON aircraft(designation);
CREATE INDEX idx_manufacturer_name ON manufacturers(name);
```

## 🔒 Security

### Security Best Practices

#### Network Security
```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Use VPN for admin access
# Configure VPC peering for Confluent Cloud
```

#### Application Security
```python
# Enable HTTPS only
@app.before_request
def before_request():
    if not request.is_secure and app.env != 'development':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/aircraft/<designation>/view')
@limiter.limit("100/hour")
def track_aircraft_view(designation):
    pass
```

#### API Key Management
```bash
# Rotate API keys regularly
confluent api-key create --resource CLUSTER_ID --description "New Production Key"

# Update application with new key
# Test with new key
python test_confluent.py

# Delete old key
confluent api-key delete OLD_KEY_ID
```

### Security Monitoring
```bash
# Monitor failed login attempts
grep "Failed password" /var/log/auth.log

# Monitor suspicious activity
tail -f /var/log/nginx/access.log | grep -E "(404|500|403)"

# Check for unauthorized access
grep -i "unauthorized" /var/log/hangarstack/application.log
```

## 📈 Scaling

### Horizontal Scaling

#### Load Balancer Configuration
```nginx
upstream hangarstack_backend {
    least_conn;
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
    server 10.0.1.13:8000;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://hangarstack_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Auto-scaling Configuration
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hangarstack-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hangarstack
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Scaling
```bash
# Increase server resources
# Update instance type in cloud provider
# Restart application with new configuration
systemctl restart hangarstack

# Monitor performance improvements
curl -f http://localhost:8000/metrics
```

## 📞 Support and Escalation

### Support Contacts
- **Primary Contact**: DevOps Team
- **Secondary Contact**: Development Team
- **Emergency Contact**: On-call Engineer
- **Confluent Support**: Enterprise Support (if applicable)

### Escalation Procedures
1. **Level 1**: Check logs and restart services
2. **Level 2**: Investigate root cause and apply fixes
3. **Level 3**: Engage development team for code issues
4. **Level 4**: Contact Confluent support for platform issues

### Incident Response
```bash
# Incident response checklist
1. Assess impact and scope
2. Implement immediate mitigation
3. Investigate root cause
4. Apply permanent fix
5. Document incident and lessons learned
6. Update monitoring and alerting
```

---

**HangarStack Operations** - Ensuring reliable, secure, and scalable aircraft database operations! 🛩️✨ 

## 📚 Where to Learn More

- [README (Project Tour & Learning Path)](README.md)
- [Confluent Cloud Setup Guide](CONFLUENT_SETUP_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Application Summary](APPLICATION_SUMMARY.md)
- [Cleanup Summary](CLEANUP_SUMMARY.md)

---

## 💡 Interview & Learning Tip

- For interviews, discuss Docker/K8s readiness and show the deployment scripts and diagrams.
- For learning, try deploying locally with Docker Compose, then explore cloud deployment options. 