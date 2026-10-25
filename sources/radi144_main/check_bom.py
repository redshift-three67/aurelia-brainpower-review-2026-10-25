import os

files = ["generate_matrix.ps1", "focus_history.txt"]

for f in files:
    if os.path.exists(f):
        with open(f, "rb") as fp:
            header = fp.read(4)
            print(f"{f}: {header}")
    else:
        print(f"{f}: NOT FOUND")
