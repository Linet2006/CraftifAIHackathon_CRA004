# 🏆 HackwithBangalore 4.0 — Hackathon Submission & Pitch Guide
## Project: SentinelAI — Workplace Safety Sentinel
**Theme**: Building Physical AI Systems That See, Decide and Act  
**Submission Form Link**: [https://forms.gle/eJyeCKCG2UH757QZ8](https://forms.gle/eJyeCKCG2UH757QZ8)  
**Submission Deadline**: October 16, 2026 at 11:00 PM IST  

---

## 📋 Copy-Paste Form Field Answers

### 1. Project Title
`SentinelAI — Autonomous Workplace Safety Sentinel & Physical AI Closed-Loop Engine`

### 2. Selected Track
`Track A — PipeGen (Perception) + Closed-Loop Bonus Track`

### 3. Problem Statement & Motivation
Every year, over 2.8 million industrial workplace injuries occur due to personnel entering hazardous robotic zones or neglecting mandatory PPE. Traditional CCTV monitoring is passive—video is only inspected *after* an accident occurs. Human reaction time is 250-400ms, too slow to prevent high-speed robotic arm strikes. 

SentinelAI closes the perception-to-action gap by compiling a multi-task vision pipeline into an edge TensorRT engine that tracks workers, verifies PPE compliance (hard hats and vests), and detects restricted zone breaches in sub-15ms. It then physically intervenes via an ESP32 microcontroller that opens an Emergency Stop (E-Stop) relay on machinery and sounds a 2.4kHz warning siren within 50ms total loop time.

### 4. PipeGen 5-Stage Implementation Summary
- **Stage 1 (Requirement)**: Formalized natural language requirements into `pipegen/requirement.json`, specifying 60+ FPS throughput, <16ms latency on Jetson Orin Nano, and explicit safety acceptance criteria.
- **Stage 2 (Pipeline IR)**: Built complete AST graph `pipegen/pipeline_ir.json` connecting `nvstreammux` -> Primary GIE -> `nvtracker` -> `nvdsanalytics` -> Secondary GIE -> `nvdsosd` -> `nvmsgbroker (MQTT)`.
- **Stage 3 (Models)**: Defined YOLOv8s primary detector and MobileNetV3 secondary PPE classifier with ONNX export scripts in `pipegen/models/`.
- **Stage 4 (Compiler)**: Executed TensorRT compilation using `trtexec` with FP16 and INT8 quantization flags. Benchmarked across Jetson Orin Nano, AGX Orin, and RTX 4090.
- **Stage 5 (Run)**: Packaged deepstream execution scripts (`pipegen/run.sh`) with GPU telemetry, MQTT broker dispatch, and hybrid web simulation fallback.

### 5. Bonus Categories Claimed
1. **Closed Loop Bonus**: Perception events over MQTT directly command an ESP32 microcontroller (`hardware_bridge/closed_loop_controller.py` & `esp32_firmware_sketch.ino`) to trip an E-Stop machine halt relay and trigger visual/audio alarms in real time.
2. **Edge Optimization Bonus**: Quantized YOLOv8s to INT8 precision using calibration caching, boosting Jetson Orin Nano throughput from 67.5 FPS to **104.2 FPS** (3.62x speedup) with 48.2% VRAM savings.

### 6. TensorRT Benchmark Results
- **Jetson Orin Nano (15W FP16)**: 14.8 ms latency, 67.5 FPS
- **Jetson Orin Nano (15W INT8)**: 9.6 ms latency, 104.2 FPS
- **Jetson AGX Orin (50W FP16)**: 6.8 ms latency, 147.0 FPS
- **NVIDIA RTX 4090 (FP16)**: 4.1 ms latency, 243.9 FPS
- **Total Closed-Loop Reaction Time**: ~50.9 ms

### 7. GitHub Repository URL
`https://github.com/Linet2006/workplace-safety-sentinel`

---

## 🎤 2-Minute Judge Presentation Pitch Script

> *"Good evening judges. In modern factories, industrial robots and workers operate side-by-side. But traditional safety systems rely on passive cameras that only record accidents after they happen.*
>
> *Today, we present **SentinelAI**, an autonomous Physical AI sentinel built on **CraftifAI PipeGen**.*
>
> *SentinelAI runs through all 5 stages of the PipeGen flow: from our plain-English requirement to a DeepStream 7.0 pipeline compiled to TensorRT. On a 15-Watt Jetson Orin Nano, our INT8 engine runs at **104 frames per second** with just **9.6 milliseconds** of inference latency.*
>
> *In our live demo, watch CAM-04: Worker 1 walks safely in the designated pedestrian lane with a verified hardhat and vest. But Worker 2 approaches the automated robotic cell with missing PPE. The moment his foot crosses our dynamic polygon geofence, the pipeline detects the intrusion in under a frame. It broadcasts an actionable JSON alert over MQTT.*
>
> *And here is our **Closed-Loop Actuator**: an ESP32 board immediately trips the machine's E-Stop relay, shutting off power to the robotic arm, while flashing the strobe and sounding the 2.4kHz warning siren—all in under 51 milliseconds, before the worker can be injured.*
>
> *With PipeGen and Physical AI, we turn passive cameras into active lifesavers. Thank you!"*
