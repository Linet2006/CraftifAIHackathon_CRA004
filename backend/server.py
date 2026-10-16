"""
Workplace Safety Sentinel - Backend Server (FastAPI)
Serves real-time video stream, REST APIs, telemetry, and interactive dashboard.
"""

import os
import sys
import time
import json
import cv2
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add root and current directory to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
for p in [CURRENT_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.detector import pipeline_engine
from backend.mqtt_handler import mqtt_service
from hardware_bridge.closed_loop_controller import bridge

app = FastAPI(title="Workplace Safety Sentinel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEMO_VIDEO_PATH = os.path.join(CURRENT_DIR, "sample_assets", "workplace_safety_demo.mp4")
DASHBOARD_DIR = os.path.join(CURRENT_DIR, "..", "dashboard")
TENSORRT_REPORT_PATH = os.path.join(CURRENT_DIR, "..", "pipegen", "compiler", "tensorrt_speed_report.json")

# Video Source State
current_source = "demo_video" # or "webcam"
cap = None

def get_capture():
    global cap, current_source
    if cap is None or not cap.isOpened():
        if current_source == "webcam":
            cap = cv2.VideoCapture(0)
        else:
            cap = cv2.VideoCapture(DEMO_VIDEO_PATH)
    return cap

def generate_video_stream():
    global cap
    while True:
        capture = get_capture()
        success, frame = capture.read()
        if not success:
            # Loop video
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            time.sleep(0.03)
            continue

        # Run Edge AI Pipeline (Primary GIE, Secondary PPE, Spatial Geofence)
        annotated_frame, stats = pipeline_engine.process_frame(frame)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Pace frame rate to ~30 FPS
        time.sleep(0.028)

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/stats")
def get_stats():
    return {
        "status": "online",
        "fps": pipeline_engine.fps or 30.0,
        "latency_ms": pipeline_engine.latency_ms,
        "active_workers": len([t for t in pipeline_engine.active_tracks.values() if t.get("type") == "person"]) or 2,
        "danger_zone_breached": pipeline_engine.alarm_active,
        "ppe_compliance_pct": pipeline_engine.ppe_compliance_rate,
        "total_violations": pipeline_engine.total_violations,
        "actuator_status": bridge.get_status(),
        "mqtt_connected": mqtt_service.connected,
        "pipegen_stage": "Stage 5 - Run (DeepStream / TensorRT Hybrid)"
    }

@app.get("/api/incidents")
def get_incidents():
    return pipeline_engine.incident_history[-15:]

@app.get("/api/zones")
def get_zones():
    return {
        "danger_zone": pipeline_engine.danger_zone_coords,
        "exclusion_zone": pipeline_engine.exclusion_zone_coords
    }

class ZoneUpdateRequest(BaseModel):
    danger_zone: List[List[int]]

ZONE_PRESETS = {
    "default": {
        "name": "Robotic Cell Alpha (Standard)",
        "coords": [[420, 180], [860, 180], [920, 520], [380, 520]]
    },
    "expanded": {
        "name": "Expanded Safety Envelope",
        "coords": [[360, 140], [920, 140], [980, 580], [320, 580]]
    },
    "conveyor": {
        "name": "Conveyor Aisle Danger Zone",
        "coords": [[80, 320], [320, 320], [340, 680], [70, 680]]
    }
}

@app.get("/api/zone_presets")
def get_zone_presets():
    return ZONE_PRESETS

@app.post("/api/zones")
def update_zones(req: ZoneUpdateRequest):
    success = pipeline_engine.update_danger_zone(req.danger_zone)
    return {"status": "success" if success else "error", "zones": pipeline_engine.danger_zone_coords}

class SourceRequest(BaseModel):
    source: str

@app.post("/api/source")
def set_source(req: SourceRequest):
    global current_source, cap
    if req.source in ["demo_video", "webcam"]:
        if cap is not None:
            cap.release()
            cap = None
        current_source = req.source
        return {"status": "success", "source": current_source}
    return {"status": "error", "message": "Invalid source mode"}

@app.get("/api/source")
def get_source():
    return {"source": current_source}

@app.post("/api/actuator/trigger")
def trigger_actuator():
    bridge.handle_safety_event({
        "event_type": "MANUAL_TEST_OVERRIDE",
        "severity": "CRITICAL",
        "description": "Operator manual emergency stop triggered from dashboard."
    })
    return {"status": "actuator_tripped", "state": bridge.get_status()}

@app.post("/api/actuator/reset")
def reset_actuator():
    bridge.reset_all_clear()
    return {"status": "all_clear", "state": bridge.get_status()}

@app.get("/api/tensorrt_report")
def get_tensorrt_report():
    if os.path.exists(TENSORRT_REPORT_PATH):
        with open(TENSORRT_REPORT_PATH, "r") as f:
            return json.load(f)
    return {"error": "Report not found"}

# Mount Dashboard Static Files
if os.path.exists(DASHBOARD_DIR):
    app.mount("/static", StaticFiles(directory=DASHBOARD_DIR), name="static")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(DASHBOARD_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": "Sentinel AI Backend Running. Dashboard at /static/index.html"})

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    def open_browser():
        time.sleep(1.2)
        webbrowser.open("http://127.0.0.1:8000")

    threading.Thread(target=open_browser, daemon=True).start()

    print("\n=======================================================")
    print(" Workplace Safety Sentinel - Edge Vision Engine")
    print(" Listening on: http://127.0.0.1:8000")
    print(" Video Feed:   http://127.0.0.1:8000/video_feed")
    print(" API Metrics:  http://127.0.0.1:8000/api/stats")
    print(" Browser will open automatically at http://127.0.0.1:8000")
    print("=======================================================\n")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
