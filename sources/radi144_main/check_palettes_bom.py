import os

base_dir = r"c:\Users\Hubert111\CascadeProjects\12x12"
files = ["palettes.json"]

for f in files:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        with open(path, "rb") as fp:
            header = fp.read(3)
            # UTF-8 BOM is ef bb bf
            has_bom = header == b'\xef\xbb\xbf'
            print(f"{f}: BOM={has_bom} (Header: {header})")
    else:
        print(f"{f}: NOT FOUND")
