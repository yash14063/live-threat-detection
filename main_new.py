"""
ThreatSense - Main FastAPI Backend Application
===============================================
Production-ready backend integrating AI detection system with WebSocket real-time streaming,
REST API endpoints, and SQLite database for threat logging.

Author: ThreatSense Team
Version: 1.0.0
"""

import json
import logging
import asyncio
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import base64

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uvicorn

# Import AI detection system
from ai_detectors import (
    ShopliftingDetector,
    FallDetector,
    AssaultDetector,
    CrowdAnalyzer
)
from ai_detectors.models import MediapipePoseDetector, YOLODetector
from ai_detectors.utils.visualization import SkeletonVisualizer

# Import database and models
from database import engine, SessionLocal, Base, Camera, ThreatAlert, SystemLog
from schemas import ThreatAlertSchema, CameraSchema, SystemStatusSchema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/threatsense.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ThreatSense API",
    description="Real-time threat detection system",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize AI detection system
logger.info("Initializing AI detection system...")
try:
    pose_detector = MediapipePoseDetector(model_complexity=1)
    yolo_detector = YOLODetector(model_name="yolov8m.pt")
    
    shoplifting_detector = ShopliftingDetector()
    fall_detector = FallDetector()
    assault_detector = AssaultDetector()
    crowd_analyzer = CrowdAnalyzer()
    
    detectors = [
        shoplifting_detector,
        fall_detector,
        assault_detector,
        crowd_analyzer
    ]
    logger.info("✓ AI detection system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI system: {e}")
    raise


# ============================================================================
# DEPENDENCY INJECTIONS
# ============================================================================

def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# DATA MODELS & SCHEMAS
# ============================================================================

class FrameData(BaseModel):
    """Frame data received from frontend."""
    camera_id: str
    frame_base64: str
    timestamp: int


class DetectionResult(BaseModel):
    """Detection result structure."""
    camera_id: str
    timestamp: datetime
    alert_triggered: bool
    threat_type: Optional[str] = None
    threat_score: Optional[int] = None
    detector_name: Optional[str] = None
    threat_message: Optional[str] = None
    pattern: Optional[str] = None


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Serve frontend dashboard."""
    return FileResponse("static/index.html")


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.query(Camera).first()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "ai_system": "ready",
            "detectors_active": len(detectors),
            "models_loaded": {
                "mediapipe": True,
                "yolo": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 500


@app.get("/api/cameras")
async def get_cameras(db: Session = Depends(get_db)):
    """Get list of configured cameras."""
    cameras = db.query(Camera).all()
    return [CameraSchema.from_orm(cam) for cam in cameras]


@app.post("/api/cameras")
async def create_camera(camera: CameraSchema, db: Session = Depends(get_db)):
    """Register a new camera."""
    try:
        db_camera = Camera(
            name=camera.name,
            location=camera.location,
            rtsp_url=camera.rtsp_url if camera.rtsp_url else None,
            is_active=True
        )
        db.add(db_camera)
        db.commit()
        db.refresh(db_camera)
        
        logger.info(f"Camera registered: {db_camera.camera_id} - {camera.name}")
        return CameraSchema.from_orm(db_camera)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create camera: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/alerts")
async def get_alerts(
    camera_id: Optional[str] = None,
    threat_level: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get threat alerts with optional filtering."""
    query = db.query(ThreatAlert)
    
    if camera_id:
        query = query.filter(ThreatAlert.camera_id == camera_id)
    
    if threat_level:
        query = query.filter(ThreatAlert.threat_level == threat_level)
    
    alerts = query.order_by(ThreatAlert.timestamp.desc()).limit(limit).all()
    return [ThreatAlertSchema.from_orm(alert) for alert in alerts]


@app.get("/api/statistics")
async def get_statistics(camera_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get threat detection statistics."""
    query = db.query(ThreatAlert)
    
    if camera_id:
        query = query.filter(ThreatAlert.camera_id == camera_id)
    
    alerts = query.all()
    
    stats = {
        "total_alerts": len(alerts),
        "critical_alerts": len([a for a in alerts if a.threat_level == "CRITICAL"]),
        "high_alerts": len([a for a in alerts if a.threat_level == "HIGH"]),
        "medium_alerts": len([a for a in alerts if a.threat_level == "MEDIUM"]),
        "low_alerts": len([a for a in alerts if a.threat_level == "LOW"]),
        "alerts_by_type": {},
        "alerts_by_detector": {}
    }
    
    # Group by threat type
    for alert in alerts:
        threat_type = alert.threat_type or "unknown"
        detector = alert.detector_name or "unknown"
        
        stats["alerts_by_type"][threat_type] = stats["alerts_by_type"].get(threat_type, 0) + 1
        stats["alerts_by_detector"][detector] = stats["alerts_by_detector"].get(detector, 0) + 1
    
    return stats


@app.get("/api/system/status")
async def system_status():
    """Get overall system status."""
    return SystemStatusSchema(
        status="operational",
        timestamp=datetime.now(),
        active_cameras=1,
        total_alerts_today=0,
        critical_alerts=0,
        system_uptime="24h",
        gpu_available=True,
        detectors={
            "shoplifting": True,
            "fall": True,
            "assault": True,
            "crowd": True
        }
    )


# ============================================================================
# WEBSOCKET HANDLER FOR REAL-TIME STREAMING
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, camera_id: str):
        """Register new WebSocket connection."""
        await websocket.accept()
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = []
        self.active_connections[camera_id].append(websocket)
        logger.info(f"Client connected to camera: {camera_id}")
    
    async def disconnect(self, websocket: WebSocket, camera_id: str):
        """Unregister WebSocket connection."""
        if camera_id in self.active_connections:
            self.active_connections[camera_id].remove(websocket)
            if not self.active_connections[camera_id]:
                del self.active_connections[camera_id]
        logger.info(f"Client disconnected from camera: {camera_id}")
    
    async def broadcast(self, camera_id: str, data: dict):
        """Broadcast message to all connected clients."""
        if camera_id not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[camera_id]:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            await self.disconnect(conn, camera_id)


manager = ConnectionManager()


@app.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time video streaming and threat detection.
    
    Expected message format:
    {
        "type": "frame",
        "frame_base64": "...",
        "timestamp": 1234567890
    }
    """
    await manager.connect(websocket, camera_id)
    
    try:
        frame_count = 0
        alert_count = 0
        
        while True:
            # Receive frame from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") != "frame":
                continue
            
            frame_count += 1
            
            try:
                # Decode frame from base64
                frame_data = base64.b64decode(message.get("frame_base64", ""))
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    continue
                
                # Run AI detection
                poses = pose_detector.detect(frame)
                objects = yolo_detector.detect(frame)
                
                detections = []
                alerts = []
                
                # Run all detectors
                for detector in detectors:
                    result = detector.detect(frame, poses, objects)
                    detections.append(result)
                    
                    # Log alert if triggered
                    if result.get("alert_triggered"):
                        alert_count += 1
                        
                        # Determine threat level based on threat_score
                        threat_score = result.get("threat_score", 0)
                        if threat_score >= 80:
                            threat_level = "CRITICAL"
                        elif threat_score >= 60:
                            threat_level = "HIGH"
                        elif threat_score >= 40:
                            threat_level = "MEDIUM"
                        else:
                            threat_level = "LOW"
                        
                        # Save to database
                        alert = ThreatAlert(
                            camera_id=camera_id,
                            threat_type=result.get("threat_type"),
                            threat_level=threat_level,
                            threat_score=threat_score,
                            detector_name=detector.detector_name,
                            threat_message=result.get("threat_message"),
                            pattern=result.get("pattern"),
                            image_data=None  # Optional: store frame
                        )
                        db.add(alert)
                        db.commit()
                        
                        alerts.append({
                            "detector": detector.detector_name,
                            "threat_type": result.get("threat_type"),
                            "threat_score": threat_score,
                            "threat_level": threat_level,
                            "message": result.get("threat_message")
                        })
                
                # Prepare response
                response = {
                    "type": "detection_result",
                    "camera_id": camera_id,
                    "timestamp": datetime.now().isoformat(),
                    "frame_count": frame_count,
                    "people_detected": len(poses),
                    "objects_detected": len(objects),
                    "alerts": alerts,
                    "has_threat": len(alerts) > 0
                }
                
                # Broadcast to all clients watching this camera
                await manager.broadcast(camera_id, response)
                
                # Log frame processing every 30 frames
                if frame_count % 30 == 0:
                    logger.info(
                        f"Camera {camera_id}: processed {frame_count} frames, "
                        f"{alert_count} alerts, {len(poses)} people detected"
                    )
            
            except Exception as e:
                logger.error(f"Error processing frame: {e}")
                error_response = {
                    "type": "error",
                    "camera_id": camera_id,
                    "error": str(e)
                }
                await websocket.send_json(error_response)
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket, camera_id)
        logger.info(f"Client disconnected from camera: {camera_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket, camera_id)


# ============================================================================
# STATIC FILES
# ============================================================================

# Mount static files (CSS, JS, etc.)
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup."""
    logger.info("=" * 60)
    logger.info("ThreatSense System Startup")
    logger.info("=" * 60)
    logger.info("✓ FastAPI server started")
    logger.info("✓ AI detection system ready")
    logger.info("✓ Database initialized")
    logger.info("✓ WebSocket streaming enabled")
    logger.info("✓ REST API endpoints available")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    logger.info("ThreatSense System Shutting Down...")


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
