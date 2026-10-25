from __future__ import annotations

import sys
from typing import Any

from apps.web.contracts import Phase1ScanRequest


PS1_SCRIPT_PATH = "Run-MultiplexScan.ps1"
CLI_ENTRYPOINT = [sys.executable, "-m", "apps.cli.main", "scan", "top3-scan"]
PS1_REFERENCE_ENTRYPOINT = ".venv\\Scripts\\python.exe -m apps.cli.main scan top3-scan"
EXPORT_PATH = "C:\\Benutzer_Archive_Start"
HARDWARE_PROFILE = "windows"
K_TOTAL = 2048
TOP_K = 192
SYNERGY_COMBOS = 4
SYNERGY_THRESHOLD = 6.0
UNSUPPORTED_REQUEST_FIELDS: tuple[str, ...] = ()


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
        "--profile-template",
        request.profile_template,
        "--entropy-mode",
        request.entropy_mode,
    ]
    if request.image_path:
        command.extend(["--image", request.image_path])
    if request.adaptive_limits:
        command.append("--adaptive-limits")

    # Fokus und Hauptsymptom kombinieren, falls beide gesetzt sind.
    # Der CLI-Pfad kennt nur --focus; main_symptom wird daher in den
    # Fokus eingeflochten, damit es das Scan-Scoring beeinflusst.
    effective_focus = request.focus.strip()
    main_symptom = request.main_symptom.strip()
    if main_symptom:
        if effective_focus and main_symptom.lower() not in effective_focus.lower():
            effective_focus = f"{effective_focus} | {main_symptom}"
        elif not effective_focus:
            effective_focus = main_symptom
    if effective_focus:
        command.extend(["--focus", effective_focus])

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
        "`profile_template`, `entropy_mode`, `image_path` und `adaptive_limits` werden an den produktiven CLI-Pfad uebergeben.",
        f"Hauptsymptom: {main_symptom or 'nicht angegeben'}",
        f"Notizen: {request.notes.strip() or 'keine'}",
    ]
    return {
        "executes": executes,
        "command": command,
        "profile_level": request.profile_level,
        "top_n": request.top_n,
        "focus": effective_focus,
        "launcher": launcher,
        "notes": notes,
    }
