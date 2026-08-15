#!/bin/bash
# setup-wsl2-rocm.sh
# One-shot setup for ACE-Step GPU inference on WSL2 Ubuntu 24.04 + ROCm 6.3
# Target: Radeon 780M (RDNA3, GFX1102) with 16 GB UMA
# Run inside WSL2: wsl -d Ubuntu-24.04 -- bash setup-wsl2-rocm.sh

set -euo pipefail

echo "=== ACE-Step WSL2 ROCm 6.3 Setup ==="
echo "Target: Radeon 780M (RDNA3, GFX1102) 16GB UMA"
echo ""

# 1. System update
echo "[1/7] Updating system..."
sudo apt update && sudo apt upgrade -y

# 2. Install prerequisites
echo "[2/7] Installing prerequisites..."
sudo apt install -y \
    python3.12 python3.12-venv python3.12-dev \
    wget gnupg2 software-properties-common \
    build-essential cmake git \
    rocm-smi

# 3. Add ROCm 6.3 repository
echo "[3/7] Adding ROCm 6.3 repository..."
wget -qO - https://repo.radeon.com/rocm/rocm.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/rocm.gpg
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.3/ noble main' | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update

# 4. Install minimal ROCm runtime
echo "[4/7] Installing ROCm 6.3 runtime..."
sudo apt install -y \
    hip-runtime-amd \
    hsa-rocr6.3.0 \
    hipblas6.3.0 \
    hipsparse6.3.0 \
    hipfft6.3.0 \
    rccl6.3.0 \
    rocm-smi6.3.0 \
    rocm-core6.3.0

# 5. Verify ROCm installation
echo "[5/7] Verifying ROCm..."
echo "--- rocm-smi output ---"
rocm-smi
echo "--- rocminfo (GPU details) ---"
rocminfo 2>/dev/null | grep -A5 "Name:" | head -20

# Check GFX version
echo "--- Checking GFX version for 780M ---"
rocminfo 2>/dev/null | grep -i "gfx" | head -5

# 6. Setup Python environment
echo "[6/7] Setting up Python 3.12 venv..."
ACE_STEP_DIR="${ACE_STEP_DIR:-/mnt/c/Users/tomas/ace-step/extracted}"
cd "$ACE_STEP_DIR"

if [ ! -d ".venv-rocm" ]; then
    python3.12 -m venv .venv-rocm
fi

source .venv-rocm/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install ROCm PyTorch
echo "Installing PyTorch for ROCm 6.0..."
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0

# Verify torch sees ROCm
python -c "
import torch
print('Torch version:', torch.__version__)
print('ROCm available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('Device count:', torch.cuda.device_count())
    print('Device name:', torch.cuda.get_device_name(0))
    print('VRAM (GB):', torch.cuda.get_device_properties(0).total_memory / 1e9)
"

# Install ACE-Step requirements
if [ -f "requirements-rocm.txt" ]; then
    echo "Installing ACE-Step ROCm requirements..."
    pip install -r requirements-rocm.txt
else
    echo "Installing ACE-Step in editable mode..."
    pip install -e .
fi

# 7. Create environment activation script
echo "[7/7] Creating activation script..."
cat > activate_rocm.sh << 'EOF'
#!/bin/bash
# Source this to activate ACE-Step ROCm environment
# Usage: source activate_rocm.sh

export ACE_STEP_DIR="${ACE_STEP_DIR:-/mnt/c/Users/tomas/ace-step/extracted}"
cd "$ACE_STEP_DIR"

source .venv-rocm/bin/activate

# ACE-Step environment variables (Tier 6a: 16-20 GB VRAM)
export ACESTEP_DEVICE=auto
export ACESTEP_LM_BACKEND=vllm
export ACESTEP_INIT_LLM=true
export ACESTEP_CONFIG_PATH=acestep-v15-turbo
export ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B

# Radeon 780M = RDNA3 = GFX1102
export HSA_OVERRIDE_GFX_VERSION=11.0.1
export MIOPEN_FIND_MODE=FAST
export PYTORCH_HIP_ALLOC_CONF=garbage_collection_threshold:0.6,max_split_size_mb:128

# vllm optimization for 16GB
export VLLM_WORKER_MULTIPROC_METHOD=spawn

echo "✅ ACE-Step ROCm environment activated"
echo "   ACE_STEP_DIR: $ACE_STEP_DIR"
echo "   Python: $(which python)"
echo "   Torch ROCm: $(python -c 'import torch; print(torch.version.hip if torch.cuda.is_available() else \"NOT AVAILABLE\")')"
EOF

chmod +x activate_rocm.sh

# Create API server startup script
cat > start_api_server.sh << 'EOF'
#!/bin/bash
# Start ACE-Step API server on WSL2 (accessible from Windows via localhost:8001)

source activate_rocm.sh

echo "Starting ACE-Step API server on 0.0.0.0:8001..."
echo "Accessible from Windows at: http://localhost:8001"
echo ""

python -m acestep.api_server --port 8001 --host 0.0.0.0
EOF

chmod +x start_api_server.sh

# Create Gradio UI startup script
cat > start_gradio.sh << 'EOF'
#!/bin/bash
# Start ACE-Step Gradio UI on WSL2

source activate_rocm.sh

echo "Starting ACE-Step Gradio UI on 0.0.0.0:7860..."
echo "Accessible from Windows at: http://localhost:7860"
echo ""

python -m acestep.acestep_v15_pipeline --port 7860 --server-name 0.0.0.0
EOF

chmod +x start_gradio.sh

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Restart WSL2 to load kernel modules:"
echo "   wsl --shutdown"
echo "   (then reopen terminal)"
echo ""
echo "2. Activate environment:"
echo "   cd $ACE_STEP_DIR"
echo "   source activate_rocm.sh"
echo ""
echo "3. Test GPU access:"
echo "   python -c \"import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NOT FOUND')\""
echo ""
echo "4. Start API server (for Windows gen_music.py integration):"
echo "   ./start_api_server.sh"
echo ""
echo "5. Or start Gradio UI:"
echo "   ./start_gradio.sh"
echo ""
echo "Windows integration:"
echo "  - API endpoint: http://localhost:8001"
echo "  - gen_music.py should use ACESTEP_API_URL=http://localhost:8001"
echo "  - WSL2 port forwarding works automatically"