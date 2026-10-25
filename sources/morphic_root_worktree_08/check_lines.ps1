$lines = (Get-Content "apps/cli/main.py" | Measure-Object -Line).Lines
Write-Host "main.py: $lines lines"
