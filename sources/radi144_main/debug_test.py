import os
import sys

print("Debug Test Starting...", flush=True)
print(f"CWD: {os.getcwd()}", flush=True)

try:
    with open("debug_output.txt", "w") as f:
        f.write("Debug write successful")
    print("File write successful", flush=True)
except Exception as e:
    print(f"File write failed: {e}", flush=True)
