#!/bin/bash
# ============================================================
# 12x12 Resonance Matrix Engine v1.5.0
# Linux Debian Root Server Setup Script
# Target: GPU Server M G1 (RTX 4000 SFF Ada, 128GB DDR5)
# ============================================================

set -e

echo "=========================================="
echo " 12x12 Resonance Engine - Server Setup"
echo " v1.5.0 (EMF Compensation Edition)"
echo "=========================================="

# --- 1. System Dependencies ---
echo "[1/7] Installing system dependencies..."
apt-get update
apt-get install -y python3.11 python3.11-venv python3.11-dev \
    git curl wget build-essential \
    nvidia-driver-535 nvidia-cuda-toolkit

# --- 2. Create User & Directories ---
echo "[2/7] Creating service user and directories..."
useradd -r -s /bin/false resonance 2>/dev/null || true
mkdir -p /opt/resonance-engine
mkdir -p /opt/resonance-engine/data
mkdir -p /opt/resonance-engine/exports
mkdir -p /var/log/resonance-engine
chown -R resonance:resonance /opt/resonance-engine
chown -R resonance:resonance /var/log/resonance-engine

# --- 3. Deploy Application ---
echo "[3/7] Deploying application..."
# Copy project files (run from project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

rsync -av --exclude='RestorePoints' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='.git' \
          --exclude='output_*' \
          --exclude='venv' \
          --exclude='node_modules' \
          "$PROJECT_DIR/" /opt/resonance-engine/

# --- 4. Python Virtual Environment ---
echo "[4/7] Setting up Python virtual environment..."
cd /opt/resonance-engine
python3.11 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA 12.x support (RTX 4000 Ada = SM89)
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# --- 5. CUDA Verification ---
echo "[5/7] Verifying CUDA setup..."
python3 -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'VRAM: {torch.cuda.get_device_properties(0).total_mem / (1024**3):.1f} GB')
    print(f'Compute Capability: {torch.cuda.get_device_capability(0)}')
"

# --- 6. Install systemd Service ---
echo "[6/7] Installing systemd service..."
cp deploy/resonance-engine.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable resonance-engine

# --- 7. EMF Compensator Validation ---
echo "[7/7] Validating EMF Compensator..."
python3 -c "
from app.algorithms.emf_compensator import EMFCompensator
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
comp = EMFCompensator(device=device)
profile = comp.profile_environment()
print(f'EMF Index: {profile[\"composite_emf_index\"]:.4f}')
print(f'Entropy Score: {profile[\"entropy_score\"]:.4f}')
rec = comp.get_timing_recommendation()
print(f'Recommendation: {rec[\"recommendation\"]} ({rec[\"confidence\"]*100:.0f}%)')
print('EMF Compensator: OK')
"

echo ""
echo "=========================================="
echo " Setup Complete!"
echo "=========================================="
echo ""
echo " Start:   systemctl start resonance-engine"
echo " Status:  systemctl status resonance-engine"
echo " Logs:    journalctl -u resonance-engine -f"
echo " Monitor: http://SERVER_IP:8000/api/v1/emf/monitor"
echo " API:     http://SERVER_IP:8000/docs"
echo ""
