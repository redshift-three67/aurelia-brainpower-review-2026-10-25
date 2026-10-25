#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

try:
    print("Importing apps.cli.main...")
    import apps.cli.main as main_module
    print("Import successful!")
    
    print("Available commands:")
    if hasattr(main_module, 'app'):
        print("app object found")
        # Try to run help
        try:
            main_module.app(["--help"])
        except SystemExit:
            pass
    else:
        print("No app object found")
        
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
