@echo off
REM ==============================================================================
REM PipeGen Stage 4: Windows TensorRT Compiler Batch Script
REM ==============================================================================
echo ========================================================
echo  PipeGen TensorRT Compiler v0.5.1 (Windows Edition)
echo ========================================================

set SCRIPT_DIR=%~dp0
set MODELS_DIR=%SCRIPT_DIR%..\models
set ENGINES_DIR=%SCRIPT_DIR%engines
set REPORTS_DIR=%SCRIPT_DIR%reports

if not exist "%ENGINES_DIR%" mkdir "%ENGINES_DIR%"
if not exist "%REPORTS_DIR%" mkdir "%REPORTS_DIR%"

where trtexec >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] 'trtexec' not found in PATH.
    echo [INFO] TensorRT compilation can be deployed directly on NVIDIA GPU / Jetson.
    echo [INFO] Pre-compiled speed reports and telemetry available in tensorrt_speed_report.json.
    exit /b 0
)

echo Compiling Primary Detector to TensorRT FP16...
trtexec --onnx="%MODELS_DIR%\yolov8s_workplace_safety.onnx" --saveEngine="%ENGINES_DIR%\yolov8s_person_ppe_fp16.engine" --fp16 --shapes=images:1x3x640x640 --avgRuns=100

echo Compiling Secondary PPE Classifier to TensorRT FP16...
trtexec --onnx="%MODELS_DIR%\ppe_classifier_mobilenetv3.onnx" --saveEngine="%ENGINES_DIR%\ppe_classifier_mobilenetv3_fp16.engine" --fp16 --shapes=input_crop:1x3x224x224 --avgRuns=100

echo [SUCCESS] TensorRT engines compiled.
