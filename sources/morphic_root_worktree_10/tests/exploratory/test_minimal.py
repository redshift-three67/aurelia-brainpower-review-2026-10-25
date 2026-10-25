#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

print("Testing minimal import...")

try:
    print("Step 1: Import typer")
    import typer
    
    print("Step 2: Import main module")
    import apps.cli.main as main_module
    
    print("Step 3: Check app")
    app = main_module.app
    print(f"App type: {type(app)}")
    
    print("Step 4: Check commands")
    commands = app.registered_commands
    print(f"Commands: {list(commands.keys())}")
    
    print("Step 5: Try to run help")
    try:
        # This will exit, so we catch it
        app(["--help"])
    except SystemExit as e:
        print(f"Help command exited with code: {e.code}")
    
    print("SUCCESS: All imports and basic functionality work")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
