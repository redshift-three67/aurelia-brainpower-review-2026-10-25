#!/usr/bin/env python3
import sys
print("Testing imports...")

try:
    from apps.cli.main import app
    print("[OK] Main app imports")
except Exception as e:
    print(f"[FAIL] Main import error: {e}")
    sys.exit(1)

try:
    from apps.cli.commands.field import field_app
    print("[OK] field_app imports")
except Exception as e:
    print(f"[FAIL] field_app import error: {e}")
    sys.exit(1)

try:
    # Test all command apps
    from apps.cli.commands.scan import scan_app
    from apps.cli.commands.trend import trend_app
    from apps.cli.commands.harmonize import harmonize_app
    from apps.cli.commands.descriptions import descriptions_app
    from apps.cli.commands.synergy import synergy_app
    print("[OK] All command apps import")
except Exception as e:
    print(f"[FAIL] Command app import error: {e}")
    sys.exit(1)

print("")
print("ALL IMPORTS SUCCESSFUL - Server-ready!")
