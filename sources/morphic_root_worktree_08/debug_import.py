#!/usr/bin/env python3

import sys
import os
import traceback

print("=== DEBUG IMPORT TEST ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")

sys.path.insert(0, '.')

print("\n1. Testing basic imports...")
try:
    import typer
    print("✓ typer imported successfully")
except Exception as e:
    print(f"✗ typer import failed: {e}")

try:
    import numpy as np
    print("✓ numpy imported successfully")
except Exception as e:
    print(f"✗ numpy import failed: {e}")

print("\n2. Testing local module imports...")
try:
    from core.profiles.profile import ClientProfile
    print("✓ ClientProfile imported successfully")
except Exception as e:
    print(f"✗ ClientProfile import failed: {e}")
    traceback.print_exc()

try:
    from services.analysis_service import AnalysisService
    print("✓ AnalysisService imported successfully")
except Exception as e:
    print(f"✗ AnalysisService import failed: {e}")
    traceback.print_exc()

print("\n3. Testing main module import...")
try:
    import apps.cli.main as main_module
    print("✓ apps.cli.main imported successfully")
    print(f"✓ Module has app attribute: {hasattr(main_module, 'app')}")
    if hasattr(main_module, 'app'):
        print(f"✓ App type: {type(main_module.app)}")
except Exception as e:
    print(f"✗ apps.cli.main import failed: {e}")
    traceback.print_exc()

print("\n4. Testing typer app functionality...")
try:
    import apps.cli.main as main_module
    if hasattr(main_module, 'app'):
        # Try to get the commands
        commands = main_module.app.registered_commands
        print(f"✓ Registered commands: {list(commands.keys())}")
        
        # Check if multiplex-scan is there
        if 'multiplex-scan' in commands:
            print("✓ multiplex-scan command found")
        else:
            print("✗ multiplex-scan command NOT found")
            
except Exception as e:
    print(f"✗ Typer app test failed: {e}")
    traceback.print_exc()

print("\n=== DEBUG COMPLETE ===")
