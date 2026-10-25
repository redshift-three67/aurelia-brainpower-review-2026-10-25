#!/usr/bin/env python3

with open("apps/cli/main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

to_remove = []

for func_name in ["nls-3d-export"]:
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if f'@app.command("{func_name}")' in line:
            start_idx = i - 1
            break
    
    if start_idx is not None:
        for i in range(start_idx + 1, len(lines)):
            if lines[i].startswith("@log_command") and i > start_idx + 10:
                end_idx = i
                break
        
        if end_idx is None:
            end_idx = len(lines)
        
        to_remove.append((start_idx, end_idx, func_name))

to_remove.sort(key=lambda x: x[0], reverse=True)

for start, end, name in to_remove:
    print(f"Found {name}: lines {start+1} to {end} ({end-start} lines)")
    lines = lines[:start] + lines[end:]

with open("apps/cli/main.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"OK: Removed {sum(r[1]-r[0] for r in to_remove)} lines total")
