import sys
import os

print("Diagnostic Start", flush=True)

try:
    import torch
    print(f"Torch Version: {torch.__version__}", flush=True)
    print(f"CUDA Available: {torch.cuda.is_available()}", flush=True)
except ImportError as e:
    print(f"Torch Import Error: {e}", flush=True)

try:
    import reportlab
    print(f"Reportlab Version: {reportlab.Version}", flush=True)
except ImportError as e:
    print(f"Reportlab Import Error: {e}", flush=True)

try:
    import openpyxl
    print(f"Openpyxl Version: {openpyxl.__version__}", flush=True)
except ImportError as e:
    print(f"Openpyxl Import Error: {e}", flush=True)

try:
    from app.algorithms.resonance_engine import ResonanceMatrixEngine
    print("Engine Import Successful", flush=True)
except ImportError as e:
    print(f"Engine Import Error: {e}", flush=True)
except Exception as e:
    print(f"Engine Load Error: {e}", flush=True)
