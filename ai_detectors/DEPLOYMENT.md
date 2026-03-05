"""
DEPLOYMENT.md - Production Deployment Guide
============================================

Guide for deploying ThreatSense AI Detection System to production environments.
"""

# ThreatSense AI Detection - Production Deployment Guide

## 🚀 Pre-Deployment Checklist

- [ ] All tests passing: `python test_detectors.py`
- [ ] Dependencies locked: `pip freeze > requirements.lock`
- [ ] Configuration reviewed: Thresholds set for your environment
- [ ] GPU availability checked: `nvidia-smi` (if using NVIDIA)
- [ ] Model weights downloaded and cached
- [ ] Logging configured with proper levels
- [ ] Database migrations applied
- [ ] SSL certificates ready (if using HTTPS)
- [ ] Resource limits estimated (CPU, memory, disk)
- [ ] Monitoring and alerting configured

---

## 💻 Hardware Requirements

### Minimum Configuration (Single Camera, 10 FPS)
```
CPU:       Intel Core i5 or equivalent (4 cores)
RAM:       8 GB
Storage:   100 GB (for models and logs)
Network:   1 Gbps (for video streaming)
GPU:       Not required (optional for acceleration)
```

### Recommended Configuration (4 Cameras, 30 FPS)
```
CPU:       Intel Core i7 or Intel Xeon (8+ cores)
RAM:       16-32 GB
Storage:   500 GB (for models, logs, video cache)
Network:   10 Gbps or dual 1 Gbps NICs
GPU:       NVIDIA RTX 2080+ or A100 (10-40x faster)
```

### Enterprise Configuration (16+ Cameras, Multi-Site)
```
CPU:       Dual Xeon processors (32+ cores)
RAM:       64-128 GB
Storage:   2+ TB NAS with 10 Gbps SAN connection
Network:   Redundant 10 Gbps connections
GPU:       8x A100 (80 GB) GPUs for parallel processing
```

---

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from ai_detectors import FallDetector; print('OK')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  threatsense:
    build: .
    container_name: threatsense-detection
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./threats.db
      - LOG_LEVEL=INFO
      - GPU_ENABLED=true
    volumes:
      - ./ai_detectors:/app/ai_detectors
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
        reservations:
          cpus: '4'
          memory: 8G

  database:
    image: sqlite
    container_name: threatsense-db
    volumes:
      - ./data:/data
    restart: unless-stopped

  redis:
    image: redis:latest
    container_name: threatsense-cache
    ports:
      - "6379:6379"
    restart: unless-stopped
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

### Launch with Docker

```bash
# Build image
docker build -t threatsense:latest .

# Run container
docker run -d \
  --name threatsense \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --gpus all \
  threatsense:latest

# Or use docker-compose
docker-compose up -d
```

---

## 🎮 GPU Acceleration Setup

### NVIDIA GPU Configuration

```bash
# Install NVIDIA Container Runtime
# See: https://github.com/NVIDIA/nvidia-docker

# Check GPU availability
nvidia-smi

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU detection
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"
```

### Enable GPU in Code

```python
# main.py or example_integration.py
import torch
from ai_detectors.config import YOLO_CONFIG

# Check GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Configure for GPU
YOLO_CONFIG["device"] = 0  # GPU 0
YOLO_CONFIG["amp"] = True  # Enable automatic mixed precision

# Allocate models to GPU
processor.yolo_detector.model.to(device)
```

### Multi-GPU Setup

```python
# Distribute detectors across multiple GPUs
from torch.nn import DataParallel

yolo_detector.model = DataParallel(
    yolo_detector.model,
    device_ids=[0, 1, 2, 3]  # Use GPUs 0-3
)
```

---

## 🌐 Load Balancing & Scaling

### Horizontal Scaling (Multiple Servers)

```python
# main.py with load balancing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aioredis

app = FastAPI()

# Initialize shared Redis for coordination
redis = aioredis.create_redis_pool('redis://localhost')

# Endpoint for health checks (used by load balancer)
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gpu_utilization": get_gpu_usage(),
        "cpu_utilization": get_cpu_usage(),
        "queue_depth": await redis.llen("detection_queue")
    }

# WebSocket with queue management
@app.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: str):
    await websocket.accept()
    
    while True:
        frame = await websocket.receive_bytes()
        
        # Queue for processing
        job_id = str(uuid.uuid4())
        await redis.lpush("detection_queue", json.dumps({
            "job_id": job_id,
            "camera_id": camera_id,
            "frame": base64.b64encode(frame).decode()
        }))
        
        # Can wait or return immediately
        results = await process_queue_job(job_id)
        await websocket.send_json(results)
```

### Load Balancer Configuration (Nginx)

```nginx
upstream threatsense_backend {
    least_conn;  # Route to server with fewest connections
    
    server threatsense-1.internal:8000 weight=1;
    server threatsense-2.internal:8000 weight=1;
    server threatsense-3.internal:8000 weight=1;
}

server {
    listen 443 ssl;
    server_name threat.company.com;
    
    ssl_certificate /etc/ssl/certs/threat.crt;
    ssl_certificate_key /etc/ssl/private/threat.key;
    
    # WebSocket support
    location /ws {
        proxy_pass http://threatsense_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
    
    # REST API
    location / {
        proxy_pass http://threatsense_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://threatsense_backend;
    }
}
```

---

## 📊 Monitoring & Logging

### Configure Logging

```python
# main.py
import logging
from logging.handlers import RotatingFileHandler

# Create logger
logger = logging.getLogger("threatsense")
logger.setLevel(logging.DEBUG)

# File handler
handler = RotatingFileHandler(
    "logs/threatsense.log",
    maxBytes=100_000_000,  # 100 MB
    backupCount=10
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log detection metrics
logger.info(f"Detection: {detector_name}, Score: {threat_score}, Pattern: {pattern}")
```

### Prometheus Metrics

```python
# Export metrics for Prometheus monitoring
from prometheus_client import Counter, Histogram, Gauge

threats_detected = Counter(
    'threatsense_threats_detected_total',
    'Total threats detected',
    ['detector_type', 'threat_level']
)

detection_latency = Histogram(
    'threatsense_detection_latency_seconds',
    'Detection pipeline latency'
)

active_connections = Gauge(
    'threatsense_active_connections',
    'Number of active WebSocket connections'
)

# Use in code
@app.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket):
    active_connections.inc()
    try:
        # ... detection logic ...
        threats_detected.labels(detector_type="fall", threat_level="critical").inc()
    finally:
        active_connections.dec()
```

### Grafana Dashboard

Create custom dashboard queries:

```
# Threats per minute
rate(threatsense_threats_detected_total[5m])

# Average latency (p95)
histogram_quantile(0.95, threatsense_detection_latency_seconds)

# Active connections
threatsense_active_connections
```

---

## 🔒 Security Hardening

### Environment Variables (Not in Code)

```bash
# .env file (DO NOT COMMIT)
DATABASE_URL=sqlite:///./threats.db
API_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret
LOG_LEVEL=INFO
DEBUG=False
ALLOWED_ORIGINS=https://threat.company.com
```

### API Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

@app.websocket("/ws/{camera_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    camera_id: str,
    token: HTTPAuthCredentials = Depends(security)
):
    # Verify JWT token
    if not verify_token(token.credentials):
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    # ... proceed with WebSocket ...
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/frame")
@limiter.limit("100/minute")
async def process_frame(request: Request, frame: bytes):
    # Process frame
    pass
```

---

## 🚨 Backup & Disaster Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/threatsense"

# Backup database
sqlite3 threats.db ".backup $BACKUP_DIR/threats_$DATE.db"

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Upload to cloud (e.g., S3)
aws s3 cp $BACKUP_DIR/threats_$DATE.db s3://backup-bucket/threatsense/

# Keep last 30 days
find $BACKUP_DIR -name "threats_*" -mtime +30 -delete
find $BACKUP_DIR -name "logs_*" -mtime +30 -delete
```

### Automated Backups (Cron)

```bash
# /etc/cron.d/threatsense-backup
0 2 * * * root /home/threatsense/backup.sh >> /var/log/threatsense-backup.log 2>&1
```

---

## 📈 Performance Optimization

### Model Caching

```python
# Cache models to avoid reloading
from functools import lru_cache

@lru_cache(maxsize=1)
def get_pose_detector():
    return MediapipePoseDetector(model_complexity=1)

@lru_cache(maxsize=1)
def get_yolo_detector():
    return YOLODetector(model_name="yolov8m.pt")
```

### Frame Preprocessing Optimization

```python
import cv2

# Resize frames to improve speed
def preprocess_frame(frame, target_width=640):
    height, width = frame.shape[:2]
    if width > target_width:
        scale = target_width / width
        new_height = int(height * scale)
        frame = cv2.resize(frame, (target_width, new_height))
    return frame
```

### Batch Processing

```python
# Process multiple frames in parallel
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def process_multiple_cameras():
    futures = []
    for camera_id in camera_list:
        frame = await get_latest_frame(camera_id)
        future = executor.submit(processor.process_frame, frame)
        futures.append((camera_id, future))
    
    results = {}
    for camera_id, future in futures:
        results[camera_id] = future.result()
    
    return results
```

---

## 🧪 Pre-Production Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, websocket_task, between
import base64
import cv2

class ThreatSenseLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    @websocket_task
    def websocket_stream(self):
        frame = cv2.imread("test_frame.jpg")
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = base64.b64encode(buffer).tobytes()
        
        with self.client.websocket_connect("/ws/CAM_01") as ws:
            ws.send(frame_bytes)
            data = ws.receive_text()
            
            if not data:
                self.client.request_meta.failure_count += 1
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000 --users=50 --spawn-rate=5
```

---

## 📋 Rollback Procedures

### Version Control

```bash
# Tag production releases
git tag -a v1.0.0 -m "Production Release 1.0.0"
git push origin v1.0.0

# Rollback to previous version
git checkout v0.9.9
docker build -t threatsense:v0.9.9 .
docker-compose up -d
```

---

## ✅ Post-Deployment Checklist

- [ ] Verify all detectors are active
- [ ] Test alerts with sample threats
- [ ] Confirm logging is working
- [ ] Monitor GPU/CPU usage
- [ ] Test failover mechanisms
- [ ] Verify backup procedures
- [ ] Train operations team
- [ ] Document recovery procedures
- [ ] Schedule maintenance windows
- [ ] Set up escalation procedures

---

## 📞 Support & Maintenance

**Production Support**: 24/7 monitoring and alerting  
**Scheduled Maintenance**: Weekends 2-4 AM UTC  
**Model Updates**: Monthly (new threat patterns)  
**Security Patches**: As needed, within 48 hours  

---

**Last Updated**: 2024  
**Version**: 1.0.0
