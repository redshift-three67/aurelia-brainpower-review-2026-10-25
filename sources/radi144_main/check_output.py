import os

print("Checking Analysen folder...")
target = os.path.join(os.getcwd(), "Analysen")

if os.path.exists(target):
    print(f"Folder exists: {target}")
    files = os.listdir(target)
    print(f"Files found: {len(files)}")
    for f in files:
        print(f" - {f}")
else:
    print("Folder 'Analysen' does NOT exist.")
