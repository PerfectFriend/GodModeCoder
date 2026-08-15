@echo off
REM ACE-Step Gradio UI - DirectML Launcher
REM For Windows AMD iGPU (Radeon 780M) when ROCm fails

set PYTHONPATH=
set VIRTUAL_ENV=

REM ==================== DirectML Environment ====================
set ACESTEP_DEVICE=directml
set ACESTEP_LM_BACKEND=pt
set ACESTEP_CONFIG_PATH=acestep-v15-turbo
set ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
set ACESTEP_INIT_LLM=true
set ACESTEP_DOWNLOAD_SOURCE=auto
set ACESTEP_QUANTIZATION=none
set ACESTEP_OFFLOAD_TO_CPU=false
set ACESTEP_OFFLOAD_DIT_TO_CPU=false
set ACESTEP_USE_FLASH_ATTENTION=false

REM ==================== DirectML Specific ====================
set HSA_OVERRIDE_GFX_VERSION=
set PYTORCH_HIP_ALLOC_CONF=

REM ==================== Launch ====================
echo Starting ACE-Step Gradio UI with DirectML...
echo.
echo NOTE: DirectML uses system RAM. Limit batch size to 2.
echo.

cd /d C:\Users\tomas\ace-step\extracted\python_embeded
call Scripts\activate.bat
cd ..\..\extracted

REM Launch Gradio UI
python -u acestep\acestep_v15_pipeline.py --port 7860 --device directml

pause