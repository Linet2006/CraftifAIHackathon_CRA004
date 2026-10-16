#!/bin/bash
# ==============================================================================
# PipeGen Stage 5: DeepStream Production Pipeline Runner
# Workplace Safety Sentinel - Autonomous Hazard Detection & Telemetry Engine
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${SCRIPT_DIR}/config"
COMPILER_DIR="${SCRIPT_DIR}/compiler"

echo "==================================================================="
echo "  CraftifAI PipeGen v0.5.1 - Stage 5 Execution Runner"
echo "  Project: Workplace Safety Sentinel (SentinelAI)"
echo "==================================================================="

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "[GPU] Active Hardware Detected:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
    echo "[INFO] No native NVIDIA GPU driver in this container/host environment."
    echo "[INFO] Switching to PipeGen Hybrid CPU/Web Simulator Runner..."
    cd "${SCRIPT_DIR}/../backend"
    python server.py
    exit 0
fi

# Ensure TensorRT engines exist
if [ ! -f "${COMPILER_DIR}/engines/yolov8s_person_ppe_fp16.engine" ]; then
    echo "[BUILD] TensorRT engine not found. Running PipeGen Stage 4 Compiler..."
    bash "${COMPILER_DIR}/build_tensorrt_engine.sh"
fi

# Check DeepStream installation
if command -v deepstream-app &> /dev/null; then
    echo "[RUN] Launching DeepStream Application with PipeGen Config..."
    deepstream-app -c "${CONFIG_DIR}/deepstream_app_config.txt"
else
    echo "[WARNING] 'deepstream-app' binary not found. Launching Python GStreamer DeepStream pipeline..."
    cd "${SCRIPT_DIR}/../backend"
    python server.py
fi
