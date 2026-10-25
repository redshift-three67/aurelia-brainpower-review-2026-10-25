
import sys
import os
sys.path.append(os.getcwd())

from app.algorithms.client_signature import ClientSignatureGenerator
from datetime import datetime

print("Testing ClientSignatureGenerator fix...")

try:
    gen = ClientSignatureGenerator()
    client_data = {
        "first_name": "Max",
        "last_names": ["Mustermann"],
        "birth_date": "1990-01-01"
    }
    
    # This caused the crash before
    sig = gen.generate_signature(client_data)
    
    print("Signature generated successfully.")
    print(f"Components: {sig['components']}")
    print(f"Frequency: {sig['frequency']}")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
