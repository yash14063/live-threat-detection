# ThreatSense - Complete Setup Guide

## ✅ What's Been Created

Your complete production-ready threat detection system is now set up with:

### 📁 Backend (New/Enhanced)
- ✅ **main.py** - Production FastAPI application with WebSocket streaming
- ✅ **database.py** - SQLAlchemy ORM with 5 data models
- ✅ **schemas.py** - Pydantic validation schemas for all endpoints

### 🎨 Frontend (New/Enhanced)
- ✅ **static/index.html** - Modern, responsive dashboard with real-time updates

### 🤖 AI Detection System (Pre-built)
- ✅ 4 threat detectors (Shoplifting, Fall, Assault, Crowd)
- ✅ 3 AI/ML model wrappers (MediaPipe, YOLO, CNN)
- ✅ Utility functions and visualization tools
- ✅ Complete documentation

### 🚀 Deployment & Configuration
- ✅ **.env.example** - Environment configuration template
- ✅ **requirements.txt** - All Python dependencies listed
- ✅ **Dockerfile** - Multi-stage Docker build
- ✅ **docker-compose.yml** - Full container orchestration with Redis
- ✅ **run.sh** / **run.bat** - Startup scripts for Unix/Windows
- ✅ **Makefile** - Development commands

### 📚 Documentation
- ✅ **README.md** - Complete project documentation
- ✅ **ai_detectors/** - Comprehensive AI system docs

---

## 🚀 Getting Started (Choose One Method)

### Method 1: Quick Start (Recommended for Testing) ⚡

**Estimated time: 5-10 minutes**

```bash
# Navigate to project directory
cd live-threat-detection

# Windows: Run startup script
run.bat

# OR Linux/Mac:
chmod +x run.sh
./run.sh
```

Then open: **http://localhost:8000**

---

### Method 2: Manual Setup (Recommended for Development) 🔧

**Estimated time: 5-10 minutes**

```bash
# 1. Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment configuration
copy .env.example .env
# Edit .env if you need custom settings

# 4. Initialize database
python -c "from database import init_db; init_db()"

# 5. Start the server
uvicorn main:app --reload
```

Then open: **http://localhost:8000**

---

### Method 3: Docker (Recommended for Production) 🐳

**Estimated time: 3-5 minutes** (with Docker installed)

```bash
# 1. Build and start everything
docker-compose up -d

# 2. Check if it's running
docker-compose logs -f threatsense

# 3. Access the dashboard
# Open: http://localhost:8000

# 4. Stop when done
docker-compose down
```

---

## 📊 Testing the System

### 1. Dashboard Features

Open **http://localhost:8000** and you'll see:

- **Video Grid**: Two camera feeds (demo mode)
- **Real-time Stats**: Alert counters and metrics
- **Detector Status**: All 4 detectors showing online
- **Alert Panel**: Recent threats (click "Test Alert" button to simulate)
- **System Info**: Uptime, active cameras, critical alerts

### 2. Test Alert Functionality

1. Click **"Test Alert"** button under CAM_01
2. Random threat will be generated
3. Alert appears in the sidebar
4. Video card flashes red
5. Statistics update in real-time

### 3. Try the REST API

```bash
# Health check
curl http://localhost:8000/api/health

# Get statistics
curl http://localhost:8000/api/statistics

# Get recent alerts
curl http://localhost:8000/api/alerts

# List cameras
curl http://localhost:8000/api/cameras
```

---

## 🔌 API Quick Reference

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Dashboard (HTML) |
| `/api/health` | GET | System health check |
| `/api/statistics` | GET | Threat statistics |
| `/api/cameras` | GET | List cameras |
| `/api/alerts` | GET | List alerts |
| `/ws/{camera_id}` | WS | Real-time streaming |

### Example: Get Statistics

```bash
curl http://localhost:8000/api/statistics | python -m json.tool
```

Response:
```json
{
  "total_alerts": 5,
  "critical_alerts": 1,
  "high_alerts": 2,
  "medium_alerts": 1,
  "low_alerts": 1,
  "alerts_by_type": {
    "Fall/Medical Emergency": 1,
    "Retail Theft": 3,
    "Assault": 1
  }
}
```

---

## 📦 Project Files Overview

### Backend Files

```
main.py                 # FastAPI app with WebSocket, REST endpoints
database.py             # SQLAlchemy models (Camera, Alert, Log, etc)
schemas.py              # Pydantic validation schemas
```

### Frontend Files

```
static/index.html       # Modern responsive dashboard
                        # Includes CSS + JavaScript (all-in-one file)
```

### Configuration Files

```
.env.example            # Environment variables template
requirements.txt        # Python dependencies
```

### Deployment Files

```
Dockerfile              # Docker container definition
docker-compose.yml      # Multi-container orchestration
run.sh                  # Linux/Mac startup script
run.bat                 # Windows startup script
Makefile                # Development commands
```

### AI System Files (Pre-built)

```
ai_detectors/           # Complete AI detection system
├── base_detector.py    # Abstract base class
├── shoplifting_detector.py
├── fall_detector.py
├── assault_detector.py
├── crowd_analyzer.py
├── models/             # AI/ML wrappers
├── utils/              # Helper functions
└── config.py           # Configurable thresholds
```

---

## 🎯 Common Tasks

### Task 1: Adjust Detection Thresholds

Edit `ai_detectors/config.py`:

```python
# Make fall detection more sensitive (easier to trigger)
FALL_THRESHOLDS["aspect_ratio_threshold"] = 0.75  # was 0.8

# Reduce alert spam (longer cooldown)
SHOPLIFTING_THRESHOLDS["cooldown_ms"] = 5000     # was 3000

# Use faster model (less accurate but faster)
YOLO_CONFIG["model_name"] = "yolov8n.pt"         # nano model
```

Then restart the server.

### Task 2: Connect Real Camera

In a client application, send frames:

```javascript
// Example: Browser to backend
const ws = new WebSocket('ws://localhost:8000/ws/CAM_01');

// Send frame as base64
ws.send(JSON.stringify({
    type: 'frame',
    frame_base64: canvasElement.toDataURL().split(',')[1],
    timestamp: Date.now()
}));

// Receive results
ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('Threats:', result.alerts);
};
```

### Task 3: Access Database

Query threat alerts:

```python
from database import SessionLocal, ThreatAlert

db = SessionLocal()

# Get recent critical alerts
critical = db.query(ThreatAlert)\
    .filter(ThreatAlert.threat_level == 'CRITICAL')\
    .order_by(ThreatAlert.timestamp.desc())\
    .limit(10)\
    .all()

for alert in critical:
    print(f"{alert.threat_type}: {alert.threat_message}")

db.close()
```

### Task 4: Monitor Performance

The system logs to `logs/threatsense.log`:

```bash
# View recent logs (Linux/Mac)
tail -f logs/threatsense.log

# Or use the dashboard API
curl http://localhost:8000/api/health
```

---

## ⚙️ Configuration Options

### Environment Variables (.env)

```bash
# Application
APP_ENV=development        # or 'production'
DEBUG=True                 # Set to False in production

# Database
DATABASE_URL=sqlite:///./threats.db
# Production: postgresql://user:password@localhost/db

# AI Models
MEDIAPIPE_MODEL_COMPLEXITY=1  # 0=lite, 1=full, 2=heavy
YOLO_MODEL_NAME=yolov8m.pt    # Options: yolov8n, s, m, l, x
USE_GPU=True                   # Use GPU acceleration

# Learning more?
# See .env.example for all options
```

---

## 🐳 Docker Deployment Details

### What Docker-Compose Creates

```yaml
Services:
- threatsense     (FastAPI app on port 8000)
- redis           (Cache/queue on port 6379)
Network:
- threatsense-net (Internal communication)
Volumes:
- logs/           (Application logs)
- data/           (Database files)
- models/         (AI model cache)
- storage/        (Other data)
```

### Common Docker Commands

```bash
# Start containers
docker-compose up -d

# View logs
docker-compose logs -f threatsense

# Stop containers
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Remove all data (WARNING - deletes database)
docker-compose down -v
```

---

## 🔍 Debugging

### Check if Server is Running

```bash
# Test server
curl http://localhost:8000/api/health

# If error, server is not running
# Solution: Start it with one of the startup methods above
```

### Check Logs

```bash
# View application logs
tail -f logs/threatsense.log

# Or in Docker
docker-compose logs threatsense
```

### Port Already in Use

```bash
# Change port (example: use 8001 instead of 8000)
uvicorn main:app --port 8001

# Then access: http://localhost:8001
```

### Python Module Not Found

```bash
# Reinstall requirements
pip install -r requirements.txt

# Or in Docker
docker-compose up -d --build
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────┐
│           Frontend Dashboard (HTML5)                │
│          Real-Time Video + Alerts Display           │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket/REST API
                     │
┌─────────────────────▼────────────────────────────────┐
│          FastAPI Backend (Python)                   │
│  • WebSocket streaming handler                      │
│  • REST API endpoints (/api/*)                      │
│  • Request validation (Pydantic)                    │
└────────────────────┬────────────────────────────────┘
                     │ Calls
┌─────────────────────▼────────────────────────────────┐
│      AI Detection System (ai_detectors/)            │
│  • 4 Threat Detectors                               │
│  • 3 AI/ML Model Wrappers                           │
│  • Utility Functions                                │
└────────────────────┬────────────────────────────────┘
                     │ Reads/Writes
┌─────────────────────▼────────────────────────────────┐
│         Database (SQLite/PostgreSQL)                │
│  • Threat Alerts                                    │
│  • Camera Configuration                             │
│  • System Logs                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🎓 Next Steps

### Immediate (Today)
1. ✅ Start the system with one of the methods above
2. ✅ Open dashboard at http://localhost:8000
3. ✅ Test alert functionality with "Test Alert" button
4. ✅ Review the code in main.py and database.py

### Short-term (This Week)
1. Read [README.md](README.md) for complete documentation
2. Review AI system docs in [ai_detectors/README.md](ai_detectors/README.md)
3. Adjust thresholds in `ai_detectors/config.py`
4. Test with real video/camera if available

### Medium-term (This Month)
1. Deploy to production with Docker
2. Set up PostgreSQL database
3. Configure monitoring and logging
4. Integrate with your camera system

### Long-term (Ongoing)
1. Monitor detection accuracy
2. Fine-tune models with your data
3. Expand to additional threat types
4. Optimize performance

---

## 📚 Documentation Quick Links

| Document | Content |
|----------|---------|
| [README.md](README.md) | Project overview & features |
| [ai_detectors/README.md](ai_detectors/README.md) | AI system detailed documentation |
| [ai_detectors/QUICK_REFERENCE.md](ai_detectors/QUICK_REFERENCE.md) | Quick API reference |
| [ai_detectors/DEPLOYMENT.md](ai_detectors/DEPLOYMENT.md) | Production deployment guide |
| [.env.example](.env.example) | All configuration options |

---

## 💡 Tips & Best Practices

### Development
- Use `.env` for local configuration
- Enable `DEBUG=True` for development
- Use `--reload` flag for auto-restart
- Check logs to diagnose issues

### Production
- Set `DEBUG=False`
- Use PostgreSQL instead of SQLite
- Configure proper CORS origins
- Enable HTTPS/SSL
- Set up monitoring and backups
- Use strong SECRET_KEY

### Performance
- Use `yolov8n.pt` for speed, `yolov8x.pt` for accuracy
- Set `MEDIAPIPE_MODEL_COMPLEXITY=0` for lite mode
- Enable GPU with `USE_GPU=True`
- Monitor detection latency in logs

---

## ❓ FAQ

**Q: Can I use with existing cameras?**  
A: Yes! Send video frames to `/ws/{camera_id}` endpoint via WebSocket.

**Q: What database should I use?**  
A: SQLite for development/testing, PostgreSQL for production.

**Q: Can I train custom models?**  
A: Yes, see `ai_detectors/cnn_classifier.py` for transfer learning examples.

**Q: How do I scale to multiple servers?**  
A: Use load balancer + multiple Docker containers, see DEPLOYMENT.md

**Q: What about privacy/compliance?**  
A: Frames aren't stored by default, all alerts logged to database.

---

## 🆘 Getting Help

1. **Check Logs**: `logs/threatsense.log`
2. **Check Dashboard**: Health status at http://localhost:8000
3. **Read Docs**: Check documentation files above
4. **API Docs**: Visit http://localhost:8000/docs (FastAPI auto-docs)
5. **Review Code**: Study examples in `ai_detectors/example_integration.py`

---

## 🎉 You're All Set!

Your complete threat detection system is ready to run. Choose a startup method above and get started!

**Happy threat detecting! 🚨**

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**Status**: Production Ready ✅
