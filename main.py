from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from datetime import datetime

app = FastAPI(title="ThreatSense OS Backend")

# Allow your Vercel frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
def init_db():
    conn = sqlite3.connect("threatsense.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT,
            alert_type TEXT,
            threat_level TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# WebSocket Manager for Real-Time Event Streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive alert payload from the frontend AI
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # Save the alert to the database
            conn = sqlite3.connect("threatsense.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO security_alerts (camera_id, alert_type, threat_level, timestamp) VALUES (?, ?, ?, ?)",
                (payload.get("camera_id"), payload.get("alert_type"), payload.get("threat_level"), datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            
            print(f"[ALERT RECEIVED] {payload['camera_id']} - {payload['alert_type']}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# REST API to fetch logs
@app.get("/api/logs")
async def get_logs():
    conn = sqlite3.connect("threatsense.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM security_alerts ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    
    logs = [{"id": r[0], "camera_id": r[1], "alert_type": r[2], "threat_level": r[3], "timestamp": r[4]} for r in rows]
    return {"status": "success", "data": logs}
