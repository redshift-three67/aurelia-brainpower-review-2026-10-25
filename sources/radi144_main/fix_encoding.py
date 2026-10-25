import os

file_path = "focus_history.txt"
content = [
    "Kohaerente Harmonisierung Aura",
    "Auraschutz",
    "Auraheilung und Auraschutz",
    "Kohärenter Auraschutz",
    "Aurschutz"
]

# Write as UTF-8
with open(file_path, "w", encoding="utf-8") as f:
    for line in content:
        f.write(line + "\n")

print(f"Fixed {file_path} encoding to UTF-8")
