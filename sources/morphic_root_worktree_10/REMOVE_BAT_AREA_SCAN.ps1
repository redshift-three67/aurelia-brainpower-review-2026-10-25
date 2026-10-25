$lines = Get-Content apps/cli/main.py
$newLines = @()

for ($i = 0; $i -lt $lines.Count; $i++) {
    $skip = $false
    
    if ($i -ge 7747 -and $i -le 7984) {
        $skip = $true
    }
    
    if ($i -ge 7711 -and $i -le 7743) {
        $skip = $true
    }
    
    if (-not $skip) {
        $newLines += $lines[$i]
    }
}

$newLines | Set-Content apps/cli/main.py -Encoding UTF8 -Force
Write-Host 'Removed bat-area-scan and get_remedy_description from main.py'
(Get-Content apps/cli/main.py | Measure-Object -Line).Lines
