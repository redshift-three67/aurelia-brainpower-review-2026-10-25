#!/usr/bin/env pwsh
cd d:/Radialgo2/Morphic_Engine_V1
git add apps/cli/main.py apps/cli/commands/scan.py CLAUDE.md PROJECT_MEMORY/
git commit -m "refactor: Migrate analyze function to scan.py with safe removal"
