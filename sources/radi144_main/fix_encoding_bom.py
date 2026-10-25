import os
import codecs

files_to_fix = [
    "generate_matrix.ps1",
    "focus_history.txt"
]

def add_bom(file_path):
    if not os.path.exists(file_path):
        print(f"Skipping {file_path} (not found)")
        return

    try:
        # Read content (assuming utf-8 or compatible)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Write back with utf-8-sig (adds BOM)
        with open(file_path, "w", encoding="utf-8-sig") as f:
            f.write(content)
        
        print(f"Added BOM to {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    for f in files_to_fix:
        add_bom(os.path.join(os.getcwd(), f))
