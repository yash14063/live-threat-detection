"""
Database Models and Configuration
==================================
SQLAlchemy ORM models for threat logging and camera management.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./threats.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# ============================================================================
# DATABASE MODELS
# ============================================================================

class Camera(Base):
    """Camera endpoint configuration."""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(50), unique=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    rtsp_url = Column(String(500))
    resolution = Column(String(20), default="1920x1080")
    fps = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Camera(camera_id={self.camera_id}, name={self.name})>"


class ThreatAlert(Base):
    """Threat detection alerts and incidents."""
    __tablename__ = "threat_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(50), index=True)
    threat_type = Column(String(100), nullable=False)  # e.g., "Shoplifting", "Fall", "Assault"
    threat_level = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    threat_score = Column(Integer)  # 0-100
    detector_name = Column(String(100))  # e.g., "ShopliftingDetector"
    threat_message = Column(Text)  # Human-readable message
    pattern = Column(String(255))  # Detection pattern (e.g., "rack-to-pocket")
    image_data = Column(LargeBinary)  # Optional: frame image as binary
    responded = Column(Boolean, default=False)
    response_notes = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ThreatAlert(threat_type={self.threat_type}, level={self.threat_level})>"


class SystemLog(Base):
    """System operation logs."""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(String(20))  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text)
    component = Column(String(100))  # e.g., "detector", "camera", "api"
    camera_id = Column(String(50), nullable=True)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SystemLog(level={self.log_level}, component={self.component})>"


class DetectionMetric(Base):
    """Performance metrics and statistics."""
    __tablename__ = "detection_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(50), index=True)
    detector_name = Column(String(100))
    detection_latency_ms = Column(Float)  # Milliseconds
    people_detected = Column(Integer)
    objects_detected = Column(Integer)
    alert_triggered = Column(Boolean)
    gpu_memory_mb = Column(Float)
    cpu_percent = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<DetectionMetric(camera={self.camera_id}, latency={self.detection_latency_ms}ms)>"


class UserAction(Base):
    """Track user actions for audit trail."""
    __tablename__ = "user_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=True)
    action = Column(String(100))  # e.g., "respond_alert", "configure_camera"
    resource_type = Column(String(50))  # e.g., "alert", "camera"
    resource_id = Column(Integer, nullable=True)
    change_details = Column(Text)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<UserAction(action={self.action}, resource={self.resource_type})>"


# ============================================================================
# CREATE TABLES
# ============================================================================

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
