#!/usr/bin/env python3
"""Fix field.py - remove dangling @log_command"""

with open('apps/cli/commands/field.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original field.py: {len(lines)} lines")
print(f"Last 5 lines:")
for i, line in enumerate(lines[-5:], start=len(lines)-4):
    print(f"  {i}: {repr(line)}")

# Remove last line if it contains @log_command (dangling decorator)
if len(lines) > 0:
    if '@log_command' in lines[-1]:
        lines = lines[:-1]
        print()
        print("Removed last line (dangling @log_command)")
    # Also check second to last if it's empty
    if len(lines) > 0 and lines[-1].strip() == '':
        lines = lines[:-1]
        print("Removed trailing empty line")

print(f"Fixed field.py: {len(lines)} lines")

with open('apps/cli/commands/field.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("File saved.")
