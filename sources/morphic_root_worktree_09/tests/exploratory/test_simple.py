#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

print("Starting test...")

try:
    print("Importing main module...")
    import apps.cli.main as main_module
    print("Import successful!")
    
    print("Testing multiplex_scan function...")
    # Test the function directly
    result = main_module.multiplex_scan(
        name="Schneider",
        first_name="Joachim", 
        birth_date="22041959",
        birth_place="Thierhaupten",
        profile="pathogen",
        seed="test-seed",
        k_total=16,
        top_k=8,
        export=None
    )
    print("Function call completed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
