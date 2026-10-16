# Product Requirement Document (PRD)
## Workplace Safety Sentinel (SentinelAI)
**Theme**: Building Physical AI Systems That See, Decide and Act  
**Track**: CraftifAI PipeGen Track A (Perception) + Closed-Loop Actuation  
**Author**: Team SentinelAI  
**Target Submission**: HackwithBangalore 4.0 Finale @ Microsoft Office, Bengaluru  

---

## 1. Problem Definition
Every year, over 2.8 million industrial workplace injuries occur globally due to:
1. Workers entering hazardous zones around automated industrial robotic arms or high-voltage machinery.
2. Failure to wear mandatory Personal Protective Equipment (PPE) such as hardhats and high-visibility vests.
3. Lack of real-time physical intervention before an impact occurs (human reaction times are 250-400ms; passive CCTV only logs footage for post-accident investigations).

## 2. Product Objectives
- **Zero-Accident Safety**: Build a sub-60ms edge vision pipeline running on NVIDIA TensorRT and DeepStream that detects personnel, validates PPE compliance, and geofences robotic danger zones.
- **Closed-Loop Physical Intervention**: When an intrusion occurs, immediately trigger physical actuators via an ESP32 microcontroller (tripping an emergency stop relay on the machinery and activating audio/visual alarms).
- **Enterprise-Grade Observability**: Expose real-time telemetry over MQTT and an interactive glassmorphic web operations console.

---

## 3. Functional Requirements (Categorized & Tagged)

### Category: Perception & Vision (`PERC`)
- **[REQ-01] Multi-Class Entity Detection (Explicit)**: The primary inference engine must detect human workers, mobile industrial equipment (forklifts), machinery, and hazard barrels at >=60 FPS on Jetson Orin Nano / RTX 4090 with confidence >= 0.50.
- **[REQ-02] Secondary PPE Verification (Explicit)**: The pipeline must evaluate crops of detected workers to classify Hardhat (Compliant / Non-Compliant) and High-Vis Safety Vest (Compliant / Non-Compliant) with >=92% accuracy.
- **[REQ-03] Multi-Object Tracking (Inferred)**: The system must maintain consistent tracking IDs across frames (`T-101`, `T-102`) to track path trajectories and dwell time.

### Category: Spatial Analytics & Geofencing (`GEOM`)
- **[REQ-04] Dynamic Polygon Geofencing (Explicit)**: Enforce arbitrary n-sided polygon danger zones (e.g. robotic cell perimeter) using ray-casting point-in-polygon math. Breaches must be flagged within one frame (<33ms).
- **[REQ-05] Interactive Zone Editing (Inferred)**: Allow facility safety managers to adjust polygon coordinates dynamically via web API without restarting the inference pipeline.

### Category: Telemetry & Actuation (`ACTU`)
- **[REQ-06] Actionable MQTT Stream (Explicit)**: Publish structured JSON violation events to `workplace/safety/alerts` within 50ms of breach onset.
- **[REQ-07] Hardware Closed-Loop Actuation (Bonus / Explicit)**: Bridge perception alerts to an ESP32 microcontroller driving GPIO pins for machine E-Stop relay, 2.4kHz industrial piezo siren, and visual beacon strobe.
- **[REQ-08] Operator HUD & Incident Logging (Explicit)**: Render an interactive web console showing live video stream with HUD bounding boxes, telemetry gauges, and downloadable JSON incident logs.

---

## 4. Acceptance Criteria & Verification Matrix

| Req ID | Target Metric | Verification Method | Acceptance Pass Threshold |
| :--- | :--- | :--- | :--- |
| **REQ-01** | Primary Detection Latency | TensorRT `trtexec` benchmark | Latency < 16.0 ms on Jetson Orin Nano |
| **REQ-02** | PPE Classification Accuracy | Secondary GIE evaluation | >= 92% accuracy on validation set |
| **REQ-03** | Track Continuity | NvDCF multi-object tracker | Zero ID switches during unobstructed transit |
| **REQ-04** | Zone Breach Detection Speed | Video injection test | Breach identified within 1 frame (<33ms) |
| **REQ-05** | Zone Update API | REST POST `/api/zones` | Polygon coordinates updated in runtime state |
| **REQ-06** | MQTT Latency | Network packet timestamping | Publish event delivered in < 50ms |
| **REQ-07** | Hardware Actuator Response | Oscilloscope / GPIO trigger test | Relay opens within 35ms of MQTT alert |
| **REQ-08** | Console FPS & HUD Display | Browser console test | Live stream rendered at >= 30 FPS with HUD |
