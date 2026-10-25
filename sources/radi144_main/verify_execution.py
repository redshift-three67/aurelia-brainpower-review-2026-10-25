import subprocess
import sys
import os

print("Starting subprocess test...")
try:
    result = subprocess.run(
        [sys.executable, "dev_cli.py", "--name", "Test User", "--dob", "1990-01-01", "--focus", "Integration Test"],
        capture_output=True,
        text=True,
        check=True
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    # Check if files exist
    if os.path.exists("Analysen"):
        print("Analysen folder exists.")
        print("Files:", os.listdir("Analysen"))
    else:
        print("Analysen folder MISSING.")
        
except subprocess.CalledProcessError as e:
    print("Error running dev_cli.py")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
except Exception as e:
    print(f"General Error: {e}")
