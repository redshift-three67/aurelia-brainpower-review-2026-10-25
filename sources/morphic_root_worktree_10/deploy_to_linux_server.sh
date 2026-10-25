#!/bin/bash
set -e

echo "=========================================="
echo "MORPHIC ENGINE V1 - LINUX SERVER DEPLOYMENT"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Phase 0: Pre-deployment checks
echo "[PHASE 0] Pre-deployment Validation"
echo "--------------------------------------------"

if [ ! -f "apps/cli/main.py" ]; then
    echo -e "${RED}ERROR: apps/cli/main.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Repository structure OK"

MAIN_LINES=$(wc -l < apps/cli/main.py)
echo "  main.py: $MAIN_LINES lines"

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}ERROR: requirements.txt not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} requirements.txt present"

echo ""
echo "[PHASE 1] Python Environment Setup"
echo "--------------------------------------------"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version detected: $PYTHON_VERSION"

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
    echo -e "${RED}ERROR: Python 3.10+ required${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python version OK"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} venv created"
else
    echo -e "${YELLOW}⚠${NC} venv already exists"
fi

# Activate venv
source venv/bin/activate
echo -e "${GREEN}✓${NC} venv activated"

echo ""
echo "[PHASE 2] Dependencies Installation"
echo "--------------------------------------------"

echo "Upgrading pip..."
pip install --quiet --upgrade pip

echo "Installing requirements.txt..."
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓${NC} Base dependencies installed"

# Check for GPU support
echo ""
echo "Checking GPU support..."
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓${NC} nvidia-smi found"
    CUDA_VERSION=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -1)
    echo "  CUDA Compute Capability: $CUDA_VERSION"
    
    echo "Installing CuPy for GPU acceleration..."
    pip install --quiet cupy-cuda12x
    echo -e "${GREEN}✓${NC} CuPy installed"
else
    echo -e "${YELLOW}⚠${NC} No NVIDIA GPU detected"
    echo "  Performance will be degraded (CPU-only mode)"
fi

echo ""
echo "[PHASE 3] Code Validation"
echo "--------------------------------------------"

echo "Compiling Python files..."
python3 -m py_compile apps/cli/main.py
echo -e "${GREEN}✓${NC} main.py syntax OK"

for file in apps/cli/commands/*.py; do
    python3 -m py_compile "$file" 2>/dev/null && \
        echo -e "${GREEN}✓${NC} $(basename $file)" || \
        echo -e "${RED}✗${NC} $(basename $file)"
done

echo ""
echo "Testing imports..."
if python3 -c "from apps.cli.main import app; print('OK')" 2>&1 | grep -q "OK"; then
    echo -e "${GREEN}✓${NC} Main imports OK"
else
    echo -e "${RED}✗${NC} Import errors detected"
    exit 1
fi

echo ""
echo "[PHASE 4] Functionality Tests"
echo "--------------------------------------------"

echo "Testing CLI help..."
python3 -m apps.cli.main --help > /dev/null 2>&1 && \
    echo -e "${GREEN}✓${NC} CLI accessible" || \
    (echo -e "${RED}✗${NC} CLI error"; exit 1)

echo "Testing available commands..."
COMMANDS=$(python3 -m apps.cli.main --help 2>/dev/null | grep -E "^\s+[a-z]" | awk '{print $1}' | sort)
echo "  Available: $COMMANDS"

for cmd in scan field trend; do
    python3 -m apps.cli.main $cmd --help > /dev/null 2>&1 && \
        echo -e "${GREEN}✓${NC} $cmd command OK" || \
        echo -e "${YELLOW}⚠${NC} $cmd command not available"
done

echo ""
echo "[PHASE 5] System Configuration"
echo "--------------------------------------------"

# Create required directories
mkdir -p logs
mkdir -p data
mkdir -p exports
echo -e "${GREEN}✓${NC} Directories created"

# Check environment
echo "System info:"
echo "  OS: $(uname -s)"
echo "  Hostname: $(hostname)"
echo "  CPU cores: $(nproc)"
echo "  Total RAM: $(free -h | awk '/^Mem:/ {print $2}')"

echo ""
echo "[PHASE 6] Ollama Connectivity (Optional)"
echo "--------------------------------------------"

if command -v ollama &> /dev/null; then
    echo "Ollama found. Testing connection..."
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Ollama API accessible"
        curl -s http://localhost:11434/api/tags | python3 -m json.tool | head -20
    else
        echo -e "${YELLOW}⚠${NC} Ollama API not responding"
        echo "  Start with: ollama serve"
    fi
else
    echo -e "${YELLOW}⚠${NC} Ollama not installed"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}DEPLOYMENT COMPLETE${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start services:"
echo "   source venv/bin/activate"
echo "   ollama serve  # In separate terminal"
echo ""
echo "2. Run commands:"
echo "   python -m apps.cli.main scan --help"
echo "   python -m apps.cli.main field --help"
echo ""
echo "3. Monitor:"
echo "   nvidia-smi                          # GPU usage"
echo "   tail -f logs/radialgo.log          # Application logs"
echo ""
echo "Server deployment script finished successfully!"
