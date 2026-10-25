import sys
import os

log_file = "import_debug.log"

with open(log_file, "w") as f:
    f.write("Starting Import Check\n")
    
    try:
        import reportlab
        f.write(f"Reportlab: {reportlab.__version__}\n")
    except ImportError as e:
        f.write(f"Reportlab Failed: {e}\n")

    try:
        import openpyxl
        f.write(f"Openpyxl: {openpyxl.__version__}\n")
    except ImportError as e:
        f.write(f"Openpyxl Failed: {e}\n")

    try:
        import torch
        f.write(f"Torch: {torch.__version__}\n")
        f.write(f"CUDA: {torch.cuda.is_available()}\n")
    except ImportError as e:
        f.write(f"Torch Failed: {e}\n")

    try:
        from app.algorithms.resonance_engine import ResonanceMatrixEngine
        f.write("ResonanceEngine Import: OK\n")
        try:
            engine = ResonanceMatrixEngine(use_cuda=False)
            f.write("ResonanceEngine Init: OK\n")
        except Exception as e:
            f.write(f"ResonanceEngine Init Failed: {e}\n")
    except ImportError as e:
        f.write(f"ResonanceEngine Import Failed: {e}\n")
    except Exception as e:
        f.write(f"ResonanceEngine General Error: {e}\n")

print("Check done")
