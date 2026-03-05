"""
Pydantic Schemas for Request/Response Validation
=================================================
Data validation and serialization schemas for API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


# ============================================================================
# CAMERA SCHEMAS
# ============================================================================

class CameraBase(BaseModel):
    """Base camera schema."""
    name: str = Field(..., description="Camera display name")
    location: Optional[str] = Field(None, description="Physical location")
    rtsp_url: Optional[str] = Field(None, description="RTSP stream URL")
    resolution: Optional[str] = Field("1920x1080", description="Video resolution")
    fps: Optional[int] = Field(30, description="Frames per second")


class CameraCreate(CameraBase):
    """Schema for creating a camera."""
    pass


class CameraSchema(CameraBase):
    """Schema for camera response."""
    id: int
    camera_id: str
    is_active: bool
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# THREAT ALERT SCHEMAS
# ============================================================================

class ThreatAlertBase(BaseModel):
    """Base threat alert schema."""
    camera_id: str = Field(..., description="Camera ID")
    threat_type: str = Field(..., description="Type of threat detected")
    threat_level: str = Field(..., description="Alert severity level")
    threat_score: Optional[int] = Field(None, description="Threat score 0-100")
    detector_name: Optional[str] = Field(None, description="Detector that triggered alert")
    threat_message: Optional[str] = Field(None, description="Human-readable message")
    pattern: Optional[str] = Field(None, description="Detection pattern")


class ThreatAlertCreate(ThreatAlertBase):
    """Schema for creating a threat alert."""
    pass


class ThreatAlertUpdate(BaseModel):
    """Schema for updating a threat alert."""
    responded: Optional[bool] = None
    response_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None


class ThreatAlertSchema(ThreatAlertBase):
    """Schema for threat alert response."""
    id: int
    responded: bool
    response_notes: Optional[str]
    timestamp: datetime
    resolved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# SYSTEM STATUS SCHEMAS
# ============================================================================

class DetectorStatus(BaseModel):
    """Status of a single detector."""
    name: str
    active: bool
    last_detection: Optional[datetime] = None
    total_detections: int = 0


class SystemStatusSchema(BaseModel):
    """Overall system status."""
    status: str = Field(..., description="System status: operational, degraded, error")
    timestamp: datetime
    active_cameras: int
    total_alerts_today: int
    critical_alerts: int
    system_uptime: str
    gpu_available: bool
    detectors: Dict[str, bool]


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class AlertStatsSchema(BaseModel):
    """Alert statistics."""
    total_alerts: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    alerts_by_type: Dict[str, int]
    alerts_by_detector: Dict[str, int]


class DetectorMetricsSchema(BaseModel):
    """Detector performance metrics."""
    detector_name: str
    average_latency_ms: float
    total_detections: int
    accuracy_percent: float
    false_positive_rate: float


class CameraMetricsSchema(BaseModel):
    """Camera performance metrics."""
    camera_id: str
    uptime_percent: float
    average_fps: float
    average_latency_ms: float
    total_frames_processed: int
    alert_count: int


# ============================================================================
# DETECTION RESULT SCHEMAS
# ============================================================================

class DetectionResultSchema(BaseModel):
    """Single detection result from a detector."""
    alert_triggered: bool
    threat_type: Optional[str] = None
    threat_score: Optional[int] = None
    detector_name: Optional[str] = None
    threat_message: Optional[str] = None
    pattern: Optional[str] = None
    confidence: Optional[float] = None


class FrameDetectionSchema(BaseModel):
    """Detection results for a frame."""
    camera_id: str
    timestamp: datetime
    frame_count: int
    people_detected: int
    objects_detected: int
    detections: List[DetectionResultSchema]
    alerts_triggered: List[str]


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class FrameDataSchema(BaseModel):
    """Frame data received from client."""
    camera_id: str
    frame_base64: str = Field(..., description="Base64 encoded frame")
    timestamp: int = Field(..., description="Unix timestamp")


class AlertResponseSchema(BaseModel):
    """Response to threat alert."""
    alert_id: int
    action: str = Field(..., description="Action taken: acknowledged, dismissed, escalated")
    notes: Optional[str] = Field(None, description="Response notes")
    responder_id: Optional[str] = Field(None, description="ID of responder")


class ConfigUpdateSchema(BaseModel):
    """Configuration update request."""
    detector_name: str
    parameter: str
    value: any


# ============================================================================
# LOGGING SCHEMAS
# ============================================================================

class SystemLogSchema(BaseModel):
    """System log entry."""
    id: int
    log_level: str
    message: str
    component: str
    camera_id: Optional[str]
    details: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ActivityLogSchema(BaseModel):
    """User activity log."""
    id: int
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[int]
    change_details: Optional[str]
    ip_address: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# HEALTH CHECK SCHEMAS
# ============================================================================

class HealthCheckSchema(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    ai_system: str
    detectors_active: int
    models_loaded: Dict[str, bool]


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorSchema(BaseModel):
    """Error response."""
    error: str
    status_code: int
    timestamp: datetime
    details: Optional[Dict] = None


class ValidationErrorSchema(BaseModel):
    """Validation error response."""
    error: str
    fields: Dict[str, List[str]]
    timestamp: datetime
