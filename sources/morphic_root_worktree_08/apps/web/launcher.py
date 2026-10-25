from __future__ import annotations

import sys
from typing import Any

from apps.web.contracts import Phase1ScanRequest


PS1_SCRIPT_PATH = "Run-MultiplexScan.ps1"
CLI_ENTRYPOINT = [sys.executable, "-m", "apps.cli.main", "scan", "top3-scan"]
PS1_REFERENCE_ENTRYPOINT = ".venv\\Scripts\\python.exe -m apps.cli.main scan top3-scan"
EXPORT_PATH = "C:\\Benutzer_Archive_Start"
HARDWARE_PROFILE = "windows"
K_TOTAL = 4096
TOP_K = 384
SYNERGY_COMBOS = 4
SYNERGY_THRESHOLD = 6.0
UNSUPPORTED_REQUEST_FIELDS = (
    "profile_template",
    "entropy_mode",
    "image_path",
    "adaptive_limits",
)


def build_phase1_scan_launcher(
    request: Phase1ScanRequest, *, executes: bool
) -> dict[str, Any]:
    command = [
        *CLI_ENTRYPOINT,
        request.last_name,
        request.first_name,
        "--birth-date",
        request.birth_date,
        "--birth-place",
        request.birth_place,
        "--level",
        str(request.profile_level),
        "--export",
        EXPORT_PATH,
        "--hardware-profile",
        HARDWARE_PROFILE,
        "--k-total",
        str(K_TOTAL),
        "--top-k",
        str(TOP_K),
        "--synergy",
        "--synergy-combos",
        str(SYNERGY_COMBOS),
        "--synergy-threshold",
        f"{SYNERGY_THRESHOLD:.1f}",
        "--top-n",
        str(request.top_n),
    ]
    if request.focus:
        command.extend(["--focus", request.focus])

    launcher = {
        "mode": "top_n_auto_scan",
        "script_path": PS1_SCRIPT_PATH,
        "ps1_reference_entrypoint": PS1_REFERENCE_ENTRYPOINT,
        "cli_entrypoint": " ".join(CLI_ENTRYPOINT),
        "unsupported_request_fields": list(UNSUPPORTED_REQUEST_FIELDS),
    }
    notes = [
        "Der Web-Launcher uebernimmt die produktiven Top-N-Flags aus Run-MultiplexScan.ps1.",
        "Die Web-Ausfuehrung nutzt denselben aktuell produktiven CLI-Pfad wie der PowerShell-Launcher.",
        "`profile_template`, `entropy_mode`, `image_path` und `adaptive_limits` werden derzeit im CLI-Pfad noch nicht umgesetzt.",
    ]
    return {
        "executes": executes,
        "command": command,
        "profile_level": request.profile_level,
        "top_n": request.top_n,
        "focus": request.focus,
        "launcher": launcher,
        "notes": notes,
    }
