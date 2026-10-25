
import sys
import os
sys.path.append(os.getcwd())

try:
    from app.algorithms.client_signature import ClientSignatureGenerator
    print("Import successful")
    
    gen = ClientSignatureGenerator()
    client_data = {
        "first_name": "Max",
        "last_names": ["Mustermann"],
        "birth_date": "1990-01-01"
    }
    
    print("Generating signature...")
    sig = gen.generate_signature(client_data)
    
    print("Signature generated successfully.")
    print(f"Components keys: {list(sig['components'].keys())}")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
