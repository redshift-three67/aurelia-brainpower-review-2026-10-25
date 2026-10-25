#!/usr/bin/env python3
"""Find exact boundaries of field_test() function"""

with open('apps/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_line = None
end_line = None
indent_level = None

for i, line in enumerate(lines):
    # Find start
    if 'def field_test(' in line:
        start_line = i + 1
        print(f'Start: Line {start_line}')
        indent_level = len(line) - len(line.lstrip())
        print(f'Indent level: {indent_level}')
    
    # Find end (next def at same indent level, or next decorator)
    if start_line and i > start_line:
        stripped = line.lstrip()
        if stripped and not line.startswith(' ' * (indent_level + 1)) and not stripped.startswith('#'):
            if stripped.startswith('@') or stripped.startswith('def '):
                end_line = i + 1
                print(f'End: Line {end_line} ({stripped[:50]}...)')
                break

# Also find the next function decorator before field_test
for i in range(len(lines)-1, -1, -1):
    if i < start_line - 10:
        break
    if '@' in lines[i] and 'log_command' in lines[i]:
        print(f'Decorator before: Line {i+1}')
        break

print(f'\nTotal lines in field_test: {end_line - start_line if end_line else "??"}')
