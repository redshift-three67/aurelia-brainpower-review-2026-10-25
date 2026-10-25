
import sys
import os
import platform

# Mock torch for faster verification if needed, but we rely on installed torch
sys.path.append(os.getcwd())

try:
    from app.algorithms.resonance_engine import ResonanceMatrixEngine
    print("Import successful.")
    
    # Test Windows/CPU instantiation
    engine = ResonanceMatrixEngine(use_cuda=False)
    print(f"Candidates (Windows/CPU): {engine.candidate_count}")
    print(f"HW Info: {engine.hw_info}")
    print(f"D-Wave Enabled: {engine.dwave_enabled}")
    
    # Check if logic exists in source (static analysis since we are on Windows)
    import inspect
    source = inspect.getsource(ResonanceMatrixEngine.__init__)
    if 'self.candidate_count = 500000' in source:
        print("Linux scaling logic verified in source code.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
