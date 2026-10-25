import os

file_path = "focus_history.txt"
if os.path.exists(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
        print(f"File content (hex): {content.hex()}")
        try:
            print(f"Decoded (utf-8): {content.decode('utf-8')}")
        except:
            print("Decoded (utf-8): FAILED")
        try:
            print(f"Decoded (latin-1): {content.decode('latin-1')}")
        except:
            print("Decoded (latin-1): FAILED")
else:
    print("File not found")
