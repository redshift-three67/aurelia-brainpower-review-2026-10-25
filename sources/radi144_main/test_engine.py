import sys
import os
sys.path.append(os.getcwd())

try:
    from app.algorithms.resonance_engine import ResonanceMatrixEngine
    print("Import successful")
    
    engine = ResonanceMatrixEngine(use_cuda=False)
    print("Engine initialized")
    
    client_data = {
        "first_name": "Test",
        "last_names": ["User"],
        "birth_date": "1990-01-01",
        "birth_place": "Berlin",
        "planet": "Earth"
    }
    
    result = engine.calculate_resonance(client_data, "TestFocus")
    print("Calculation successful")
    print(f"Score: {result['resonance_score']}")
    print(f"Matrix shape: {len(result['matrix_12x12'])}x{len(result['matrix_12x12'][0])}")
    print(f"Colors generated: {len(result['matrix_colors'])} rows")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
