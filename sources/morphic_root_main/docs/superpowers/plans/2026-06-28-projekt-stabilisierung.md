# Projekt-Stabilisierung Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Das Projekt wird wieder reproduzierbar startfaehig, testbar und fuer den Top-5-/Multiplex-Workflow stabil benutzbar.

**Architecture:** Die Stabilisierung erfolgt in Gates: zuerst Umgebung und Importpfade, dann CLI-Vertrag, dann Workflow-Funktionalitaet, dann Reports/Archiv, danach Datenbanken und UX. Jede Phase muss mit einem kleinen, nachweisbaren Test abschliessen, damit Importfehler nicht durch den naechsten Workaround verdeckt werden.

**Tech Stack:** Python 3.12, Typer, pytest, PowerShell, SQLite, Three.js-Viewer, lokale Datenbanken unter `data/`.

---

## Ausgangslage

| Bereich | Befund | Prioritaet | Konsequenz |
|---|---|---:|---|
| Backup | Shadow Copy erstellt unter `C:\Morphic_v1\_backups\Shadow_Copy_20260628_091517`; `_backups` wurde bewusst ausgeschlossen. | P0 | Wiederherstellung der aktuellen Arbeitslage ist moeglich, ohne rekursive Backup-Kopien. |
| Python | `python` zeigt auf `C:\Users\Hubert111\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`. | P0 | `typer`, `numpy`, `pytest` fehlen; Module koennen aus fremden Umgebungen aufgeloest werden. |
| Projekt-venv | `venv\pyvenv.cfg` verweist auf Linux-Pfade wie `/usr/bin`. | P0 | Lokale Windows-Ausfuehrung ist nicht reproduzierbar. |
| CLI | `apps/cli/main.py` hat doppelte `app = typer.Typer(...)`-Definitionen und fruehe `app()`-Ausfuehrung. | P1 | Commands werden unvollstaendig oder gar nicht registriert. |
| Legacy-Module | Tracked Module wie `cli`, `tools`, `providers`, `infra` sind geloescht oder fehlen lokal. | P1 | Nach Installation von `typer` folgen weitere `ModuleNotFoundError`. |
| Commands | PowerShell ruft Root-Commands `top3-scan` und `multiplex-scan` auf; der aktuelle Code liegt teilweise unter Subapps wie `field`. | P1 | Der Top-5-Workflow startet nicht stabil. |
| Helper | Mehrere Helper-Dateien unter `apps/cli/commands/helpers/` exportieren erwartete Namen, enthalten aber keine Implementierungen. | P1 | Spalte Import-/Runtime-Fehler nach CLI-Reparatur. |
| Tests | pytest-Collection bricht mit fehlenden Imports ab. | P1 | Keine belastbare Regressionserkennung. |
| Datenbanken | `remedies.db` und `descriptions.db` sind nutzbar, aber Beschreibungslogik ist auf mehrere Systeme verteilt; `resonance.db` ist leer. | P2 | Reporting und Interpretation sind schwer validierbar. |
| UI/UX | Bedienung ist ueber lange PowerShell-Dialoge organisiert; Preflight fehlt. | P2 | Anwender sieht Fehler erst nach mehreren Eingaben. |

## Priorisierte Zielreihenfolge

| Rang | Ziel | Muss erreicht sein, bevor weitergearbeitet wird |
|---:|---|---|
| 1 | Reproduzierbare Python-Umgebung | `python -m apps.cli.main --help` nutzt Projekt-Python und findet `typer`. |
| 2 | Saubere Import-Grenzen | pytest kann Tests sammeln, ohne an fehlenden `cli`/`tools`/`providers`-Packages zu scheitern. |
| 3 | Eindeutiger CLI-Vertrag | Genau ein Typer-App-Einstiegspunkt; `top3-scan` und `multiplex-scan` sind dokumentiert und getestet. |
| 4 | Top-5-/Multiplex-Workflow | Beispielkommando mit Fokus `Bronchien` erzeugt kontrolliert JSON/HTML/TXT-Output. |
| 5 | Reporting und Archiv | Exportstruktur ist konsistent; Trend-, Synergie-, Remedy- und PDF-Stufen lesen dieselben Schemas. |
| 6 | Datenbankpflege | DB-Zugriffe sind gekapselt, Migrationen/Healthchecks pruefen Tabellen und Mindestdaten. |
| 7 | UX-Stabilisierung | PowerShell-Launcher hat Preflight, klare Fehlermeldungen und verhindert bekannte Fehlstarts. |
| 8 | Qualitaetsgate | Smoke-, CLI-, Workflow- und DB-Tests laufen in einer festen Reihenfolge reproduzierbar. |

## Datei- und Verantwortungsplan

| Datei / Bereich | Rolle nach Stabilisierung |
|---|---|
| `pyproject.toml` | Kanonische Projektmetadaten und Abhaengigkeiten. |
| `requirements.txt` | Windows-kompatible Runtime-/Dev-Installationsliste, sofern kein Lockfile eingefuehrt wird. |
| `.venv/` | Neue lokale Windows-venv; nicht mit `venv/` Linux-Artefakt vermischen. |
| `apps/cli/main.py` | Einziger Typer-Root-Einstieg, Registrierung der Subapps und Kompatibilitaetsaliases. |
| `apps/cli/commands/scan.py` | Top-5-Orchestrierung und Scan-nahe Commands. |
| `apps/cli/commands/field.py` | Multiplex-/Field-Scan-Engine oder delegierter Adapter zu einem neuen Service. |
| `apps/cli/commands/helpers/*.py` | Tatsaechliche Helper-Implementierungen statt leerer Re-Export-Stubs. |
| `core/profile_sync/__init__.py` | Zentrale Wahrheit fuer die 35 Hauptprofile. |
| `core/subgroups/procedural_groups.py` | Kanonische dynamische Gruppen, inkl. Remedy-Multiplexe. |
| `core/remedy_group_registry.py` | Remedy-Gruppen-Erkennung und Anzeigenamen. |
| `core/trend_analysis.py` | Trend-Leser fuer aktuelle Exportstruktur. |
| `services/harmonization_worker.py` | Harmonisierung mit nachvollziehbarem Job-Status und Stop-Verhalten. |
| `Run-MultiplexScan.ps1` | Benutzerfuehrung, Preflight, Python-Aufloesung, Aufruf der CLI. |
| `tests/` | Regressionsschutz fuer Umgebung, CLI, Workflow, DB und Reporting. |
| `docs/PROJEKT_TIEFENANALYSE_20260628.md` | Befundbasis fuer diese Planung. |

---

## Phase 0: Sicherung und Arbeitsisolation

**Ziel:** Keine Reparatur beginnt ohne nachvollziehbare Ausgangslage.

**Files:**
- Read: `docs/PROJEKT_TIEFENANALYSE_20260628.md`
- Read: `git status --short`
- Optional Create: neue Git-Branch oder Worktree ausserhalb der Shadow Copy

- [ ] **Step 0.1: Shadow Copy bestaetigen**

Run:

```powershell
Test-Path -LiteralPath 'C:\Morphic_v1\_backups\Shadow_Copy_20260628_091517'
Get-ChildItem -LiteralPath 'C:\Morphic_v1\_backups\Shadow_Copy_20260628_091517' -Force | Measure-Object
```

Expected:

```text
True
Count groesser 0
```

- [ ] **Step 0.2: Dirty State festhalten**

Run:

```powershell
git status --short > docs\git-status-before-stabilization-20260628.txt
```

Expected:

```text
Datei docs\git-status-before-stabilization-20260628.txt existiert und enthaelt alle vorhandenen Aenderungen.
```

- [ ] **Step 0.3: Keine geloeschten Nutzerdateien zuruecksetzen**

Rule:

```text
Kein git reset --hard.
Kein git checkout -- <path>.
Kein Restore geloeschter Tracked-Dateien ohne vorherige Entscheidung, ob Legacy-Pfade oder neue Modulpfade kanonisch werden.
```

Gate:

```powershell
git status --short
```

Expected:

```text
Status ist bekannt; keine unerklaerten automatischen Reverts.
```

---

## Phase 1: Python-Umgebung reparieren

**Ziel:** Das Projekt startet mit einer lokalen, reproduzierbaren Windows-Python-Umgebung und nicht mit der Hermes-Agent-venv.

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`
- Modify: `Run-MultiplexScan.ps1`
- Keep: altes `venv/` nur als Artefakt, bis entschieden ist, ob es geloescht oder archiviert wird

- [ ] **Step 1.1: Lokale Windows-venv erstellen**

Run:

```powershell
& 'C:\Users\Hubert111\AppData\Local\Programs\Python\Python312\python.exe' -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Expected:

```text
.\.venv\Scripts\python.exe existiert.
pip install endet ohne Fehler.
```

- [ ] **Step 1.2: Projekt-Python verifizieren**

Run:

```powershell
.\.venv\Scripts\python.exe -c "import sys, typer, numpy, pytest; print(sys.executable); print(typer.__version__)"
```

Expected:

```text
C:\Morphic_v1\.venv\Scripts\python.exe
Typer-Version wird ausgegeben.
```

- [ ] **Step 1.3: Launcher-Python in `Run-MultiplexScan.ps1` zentralisieren**

Modify `Run-MultiplexScan.ps1` near the current `$pythonExe = 'python'` assignment:

```powershell
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$preferredPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $preferredPython) {
    $pythonExe = $preferredPython
} else {
    $pythonExe = "python"
}
```

Acceptance:

```powershell
Select-String -Path .\Run-MultiplexScan.ps1 -Pattern '\.venv\\Scripts\\python\.exe'
```

Expected:

```text
Die zentrale Python-Aufloesung ist vorhanden.
```

- [ ] **Step 1.4: Preflight-Funktion im Launcher einfuehren**

Add to `Run-MultiplexScan.ps1` before interactive questions:

```powershell
function Test-MorphicEnvironment {
    param([string]$PythonExe)

    $probe = @"
import sys
missing = []
for name in ["typer", "numpy"]:
    try:
        __import__(name)
    except Exception:
        missing.append(name)
print(sys.executable)
if missing:
    raise SystemExit("Missing Python modules: " + ", ".join(missing))
"@

    & $PythonExe -c $probe
    if ($LASTEXITCODE -ne 0) {
        throw "Python-Preflight fehlgeschlagen. Bitte .venv installieren: .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    }
}

Test-MorphicEnvironment -PythonExe $pythonExe
```

Gate:

```powershell
.\Run-MultiplexScan.ps1
```

Expected:

```text
Bei fehlender .venv endet der Launcher vor Benutzerfragen mit einer klaren Meldung.
Bei vorhandener .venv startet das Menue.
```

---

## Phase 2: Import-Grenzen und Modulpakete klaeren

**Ziel:** Fehlende Legacy-Imports werden nicht zufaellig aus Fremdumgebungen geladen. Entweder werden kompatible Adapter erstellt oder die Imports werden auf neue kanonische Module umgestellt.

**Files:**
- Modify: `apps/cli/main.py`
- Modify: `apps/cli/commands/scan.py`
- Modify: `apps/cli/commands/field.py`
- Modify/Create: `apps/cli/commands/helpers/*.py`
- Decide: `cli/`, `tools/`, `providers/`, `infra/`
- Test: `tests/test_import_contracts.py`

- [ ] **Step 2.1: Import-Contract-Test schreiben**

Create `tests/test_import_contracts.py`:

```python
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_project_python_does_not_resolve_legacy_modules_from_foreign_site_packages():
    for name in ("cli", "tools", "providers"):
        spec = importlib.util.find_spec(name)
        if spec is None or spec.origin is None:
            continue
        origin = Path(spec.origin).resolve()
        assert ROOT in origin.parents or origin == ROOT, f"{name} resolves outside project: {origin}"
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_import_contracts.py -q
```

Expected:

```text
Test failt, wenn Legacy-Module aus Hermes oder anderen Fremdumgebungen kommen.
```

- [ ] **Step 2.2: Entscheidungsmatrix fuer Legacy-Pakete treffen**

Use this rule:

| Legacy-Paket | Wenn noch fachlich benoetigt | Wenn nicht mehr benoetigt |
|---|---|---|
| `cli.utils.backup` | Adapter unter `apps/cli/utils/backup.py` oder Paket `cli/` bewusst wiederherstellen | Import entfernen und Logging lokal ersetzen |
| `tools.synergy_consolidator` | Service nach `services/` oder `core/` migrieren und Import anpassen | Aufruf aus Scan-Orchestrierung entfernen |
| `tools.remedy_reporter` | Reporting-Service in `services/reporting/` erstellen | Remedy-Report-Stufe deaktivieren mit klarer CLI-Meldung |
| `providers.hardware.entropy_sources` | Provider unter `providers/` wiederherstellen oder `core/hardware/` als neue Quelle nutzen | Hardware-Entropy im CLI deaktivierbar machen |

Gate:

```powershell
rg -n "from cli|import cli|from tools|import tools|from providers|import providers|from infra|import infra" apps core services tests
```

Expected:

```text
Alle Treffer sind bewusst klassifiziert: Adapter, Migration oder Entfernung.
```

- [ ] **Step 2.3: Helper-Stubs fuellen oder Imports entfernen**

Target files:

```text
apps/cli/commands/helpers/database_helpers.py
apps/cli/commands/helpers/utility_helpers.py
apps/cli/commands/helpers/potency_helpers.py
apps/cli/commands/helpers/interpretation_helpers.py
apps/cli/commands/helpers/influence_helpers.py
apps/cli/commands/helpers/harmonization_helpers.py
```

Required exported names from `apps/cli/commands/helpers/__init__.py` must be implemented or removed from the export list.

Run:

```powershell
.\.venv\Scripts\python.exe -c "from apps.cli.commands import helpers; print('helpers import ok')"
```

Expected:

```text
helpers import ok
```

---

## Phase 3: CLI-Einstiegspunkt vereinheitlichen

**Ziel:** Es gibt genau eine Typer-Root-App, und alle Commands sind vor `app()` registriert.

**Files:**
- Modify: `apps/cli/main.py`
- Modify: `apps/cli/commands/scan.py`
- Modify: `apps/cli/commands/field.py`
- Test: `tests/test_cli_contract.py`

- [x] **Step 3.1: CLI-Contract-Test schreiben**

Create `tests/test_cli_contract.py`:

```python
from typer.testing import CliRunner

from apps.cli.main import app


runner = CliRunner()


def test_root_help_loads():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.output
    assert "scan" in result.output
    assert "field" in result.output


def test_top3_scan_command_is_discoverable():
    result = runner.invoke(app, ["scan", "top3-scan", "--help"])
    assert result.exit_code == 0, result.output
    assert "--focus" in result.output


def test_multiplex_scan_command_is_discoverable():
    result = runner.invoke(app, ["field", "multiplex-scan", "--help"])
    assert result.exit_code == 0, result.output
    assert "--profile" in result.output or "--group" in result.output
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_cli_contract.py -q
```

Expected:

```text
Anfangs rot, weil CLI-Registrierung aktuell gebrochen ist.
```

- [x] **Step 3.2: `apps/cli/main.py` auf eine Root-App reduzieren**

Required final structure:

```python
import typer

from apps.cli.commands.scan import scan_app
from apps.cli.commands.field import field_app

app = typer.Typer(help="Morphic Engine V1 CLI")
app.add_typer(scan_app, name="scan")
app.add_typer(field_app, name="field")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
```

Migration rule:

```text
Kein zweites app = typer.Typer(...) in derselben Datei.
Kein if __name__ == "__main__": app() vor vollstaendiger Command-Registrierung.
Legacy-Code unterhalb des ersten app()-Blocks muss entweder in Commands migriert oder entfernt werden.
```

Run:

```powershell
rg -n "app = typer\.Typer|if __name__ == .__main__." apps\cli\main.py
.\.venv\Scripts\python.exe -m apps.cli.main --help
```

Expected:

```text
Eine Root-App-Definition.
Help-Ausgabe ohne Importfehler.
```

Status 2026-06-28:

```text
Erledigt: `apps/cli/main.py` enthaelt nur noch eine `app = typer.Typer(...)`-Definition und einen Main-Guard am Dateiende.
Abgedeckt durch `tests/test_cli_main_structure.py`.
Verbleibend: fachliche Legacy-Helper liegen weiterhin in `apps/cli/main.py`, weil `apps/cli/commands/field.py` sie aktuell importiert.
```

- [x] **Step 3.2a: Command-Module von `apps.cli.main` als Helper-Quelle entkoppeln**

Status 2026-06-28:

```text
Erledigt: `apps/cli/commands/field.py` und `apps/cli/commands/scan.py` importieren Report-, Export-,
Interpretations- und Influence-Helper direkt aus `apps.cli.commands.helpers`.
Abgedeckt durch `tests/test_cli_import_boundaries.py`.
```

- [x] **Step 3.2b: Legacy-Helper-Kopien in `apps/cli/main.py` entfernen oder delegieren**

Rule:

```text
Vor dem Entfernen pruefen, ob Root-Alias `analyze`, Subapps oder externe Legacy-Adapter noch direkte Symbolimporte benoetigen.
Wenn Kompatibilitaet noetig ist, sollen alte Namen auf `apps.cli.commands.helpers` delegieren statt eigene Kopien zu halten.
```

Status 2026-06-28:

```text
Erledigt: `apps/cli/main.py` ist ein duennes Root-CLI-Modul. Lokale Helper-Kopien wurden entfernt.
Legacy-Helper-Namen werden aus `apps.cli.commands.helpers` delegiert, damit alte Imports nicht sofort brechen.
Abgedeckt durch `tests/test_cli_main_helper_delegation.py`.
```

- [x] **Step 3.2c: Legacy-Adapter `cli/main.py` bewusst entscheiden**

Rule:

```text
`cli/main.py` bleibt aktuell als Kompatibilitaetsadapter auf `apps.cli.commands.helpers` erhalten.
Naechster Schritt: dokumentieren, ob dieser Adapter langfristig unterstuetzt wird oder mit Migrationshinweis abgekündigt wird.
```

Status 2026-06-28:

```text
Entscheidung: `cli/main.py` bleibt als unterstuetzter Kompatibilitaetsadapter erhalten.
Der Adapter exportiert `COMPATIBILITY_STATUS = "supported"` und `ADAPTER_TARGET = "apps.cli.commands.helpers"`.
Alle Helper-Namen werden direkt aus `apps.cli.commands.helpers` delegiert.
Abgedeckt durch `tests/test_cli_legacy_adapter.py`.
```

- [ ] **Step 3.3: Kompatibilitaetsaliases bewusst entscheiden**

Option A, empfohlen fuer kurze Stabilisierung:

```text
Root-Aliases top3-scan und multiplex-scan bleiben voruebergehend erhalten und delegieren intern auf scan top3-scan bzw. field multiplex-scan.
```

Option B, sauberer CLI-Vertrag:

```text
PowerShell-Launcher wird direkt auf scan top3-scan und field multiplex-scan umgestellt; Root-Aliases werden nicht mehr angeboten.
```

Acceptance:

```powershell
.\.venv\Scripts\python.exe -m apps.cli.main --help
.\.venv\Scripts\python.exe -m apps.cli.main scan top3-scan --help
.\.venv\Scripts\python.exe -m apps.cli.main field multiplex-scan --help
```

Expected:

```text
Alle Help-Aufrufe enden mit Exit-Code 0.
```

---

## Phase 4: Top-5-/Multiplex-Workflow stabilisieren

**Ziel:** Der konkrete Anwenderworkflow laeuft mit Fokus-Keyword, 35 Hauptprofilen und Top-5-Auswertung wieder reproduzierbar.

**Files:**
- Modify: `Run-MultiplexScan.ps1`
- Modify: `apps/cli/commands/scan.py`
- Modify: `apps/cli/commands/field.py`
- Modify: `core/profile_sync/__init__.py`
- Test: `tests/test_top5_workflow_smoke.py`

- [ ] **Step 4.1: PowerShell-Aufrufe auf kanonische Commands setzen**

Replace Top-5 invocation in `Run-MultiplexScan.ps1`:

```powershell
$args = @(
    "-m", "apps.cli.main",
    "scan", "top3-scan",
    $firstName,
    $lastName,
    "--birth-date", $birthDate,
    "--birth-place", $birthPlace,
    "--export", $exportRoot,
    "--hardware-profile", $hardwareProfile,
    "--k-total", "4096",
    "--top-k", "384",
    "--synergy",
    "--synergy-combos", "4",
    "--synergy-threshold", "6.0",
    "--top-n", "5"
)
if ($focusKeyword) {
    $args += @("--focus", $focusKeyword)
}
& $pythonExe @args
```

Run:

```powershell
Select-String -Path .\Run-MultiplexScan.ps1 -Pattern '"scan", "top3-scan"'
```

Expected:

```text
Top-5-Aufruf nutzt scan top3-scan.
```

- [ ] **Step 4.2: Interne Subprocess-Aufrufe in `scan.py` korrigieren**

Rule:

```text
Jeder interne Aufruf von python -m apps.cli.main multiplex-scan wird ersetzt durch python -m apps.cli.main field multiplex-scan.
```

Run:

```powershell
rg -n "apps\.cli\.main.*multiplex-scan|multiplex-scan" apps\cli\commands\scan.py
```

Expected:

```text
Keine Root-Subprocess-Aufrufe auf multiplex-scan bleiben uebrig.
```

- [ ] **Step 4.3: Profilquelle vereinheitlichen**

Use `core.profile_sync.MASTER_PROFILES` as the only source for automatic main profiles.

Acceptance command:

```powershell
.\.venv\Scripts\python.exe -c "from core.profile_sync import get_profile_stats; print(get_profile_stats())"
```

Expected:

```text
total_profiles: 35
```

Rule:

```text
Run-MultiplexScan.ps1 darf keine abweichende fachliche Hauptprofil-Wahrheit enthalten. Anzeigeoptionen koennen vorhanden sein, muessen aber aus der zentralen Quelle generiert oder dokumentiert synchronisiert werden.
```

- [x] **Step 4.4: Smoke-Test fuer Top-5 schreiben**

Create `tests/test_top5_workflow_smoke.py`:

```python
from typer.testing import CliRunner

from apps.cli.main import app


runner = CliRunner()


def test_top5_scan_accepts_focus_and_export_options(tmp_path):
    result = runner.invoke(
        app,
        [
            "scan",
            "top3-scan",
            "Deisenhofer",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--export",
            str(tmp_path),
            "--hardware-profile",
            "windows",
            "--k-total",
            "64",
            "--top-k",
            "16",
            "--top-n",
            "2",
            "--focus",
            "Bronchien",
        ],
    )
    assert result.exit_code == 0, result.output
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_top5_workflow_smoke.py -q
```

Expected:

```text
Test laeuft mit kleiner Scan-Groesse und schreibt nur in tmp_path.
```

---

## Phase 5: Reporting, Archiv und Export-Schema vereinheitlichen

**Ziel:** Alle Folgeprozesse lesen dieselbe Exportstruktur.

**Files:**
- Modify: `apps/cli/commands/field.py`
- Modify: `apps/cli/commands/scan.py`
- Modify: `core/trend_analysis.py`
- Modify/Create: `services/reporting/*.py`
- Test: `tests/test_export_schema.py`

- [ ] **Step 5.1: Export-Schema dokumentieren**

Create `docs/EXPORT_SCHEMA_V1.md`:

```markdown
# Export Schema V1

Required top-level fields:
- `schema_version`: string, value `morphic.scan.v1`
- `client`: object with `first_name`, `last_name`, `birth_date`, `birth_place`
- `scan`: object with `profile`, `focus`, `hardware_profile`, `k_total`, `top_k`
- `results`: object with `top_items`
- `reports`: object with relative paths to generated `json`, `html`, `txt`, `pdf`

Required `results.top_items[]` fields:
- `rank`: integer
- `name`: string
- `score`: number
- `group`: string
- `profile`: string
```

Acceptance:

```powershell
Test-Path docs\EXPORT_SCHEMA_V1.md
```

Expected:

```text
True
```

- [ ] **Step 5.2: Schema-Test schreiben**

Create `tests/test_export_schema.py`:

```python
import json


def assert_export_schema(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "morphic.scan.v1"
    assert "client" in payload
    assert "scan" in payload
    assert "results" in payload
    assert isinstance(payload["results"]["top_items"], list)


def test_export_schema_fixture(tmp_path):
    export = tmp_path / "sample_multiplex_scan.json"
    export.write_text(
        json.dumps(
            {
                "schema_version": "morphic.scan.v1",
                "client": {
                    "first_name": "Klaus",
                    "last_name": "Deisenhofer",
                    "birth_date": "09041966",
                    "birth_place": "Augsburg",
                },
                "scan": {
                    "profile": "atmung_lunge_detailliert",
                    "focus": "Bronchien",
                    "hardware_profile": "windows",
                    "k_total": 64,
                    "top_k": 16,
                },
                "results": {
                    "top_items": [
                        {
                            "rank": 1,
                            "name": "Beispiel",
                            "score": 1.0,
                            "group": "test",
                            "profile": "atmung_lunge_detailliert",
                        }
                    ]
                },
                "reports": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    assert_export_schema(export)
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_export_schema.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5.3: Trend-Reader rekursiv und schemafaehig machen**

Modify `core/trend_analysis.py`:

```text
glob(os.path.join(folder, "**", "*_multiplex_scan.json"), recursive=True)
```

and accept both legacy `top_items` and V1 `results.top_items`.

Gate:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -k "trend or export_schema" -q
```

Expected:

```text
Trend-/Schema-Tests laufen ohne Importfehler.
```

---

## Phase 6: Datenbankverwaltung und Healthchecks

**Ziel:** Datenbanken werden vor Scans geprueft; leere oder inkonsistente DBs erzeugen klare Fehler.

**Files:**
- Modify/Create: `core/db/health.py`
- Modify: `monitoring/health.py`
- Modify: `apps/cli/main.py`
- Test: `tests/test_database_health.py`

- [x] **Step 6.1: DB-Healthcheck definieren**

Create `core/db/health.py`:

```python
import sqlite3
from pathlib import Path


def table_count(db_path: Path, table: str) -> int:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f"select count(*) from {table}")
        return int(cursor.fetchone()[0])


def assert_core_databases_ready(data_dir: Path) -> None:
    remedies = data_dir / "remedies.db"
    descriptions = data_dir / "descriptions.db"
    if not remedies.exists() or remedies.stat().st_size == 0:
        raise RuntimeError(f"Missing or empty remedies database: {remedies}")
    if not descriptions.exists() or descriptions.stat().st_size == 0:
        raise RuntimeError(f"Missing or empty descriptions database: {descriptions}")
    if table_count(remedies, "remedies") < 1000:
        raise RuntimeError("remedies.db contains too few remedies")
    if table_count(descriptions, "items") < 1000:
        raise RuntimeError("descriptions.db contains too few items")
```

Run:

```powershell
.\.venv\Scripts\python.exe -c "from core.db.health import assert_core_databases_ready; from pathlib import Path; assert_core_databases_ready(Path('data')); print('db health ok')"
```

Expected:

```text
db health ok
```

- [x] **Step 6.2: CLI-Health-Command anbieten**

Add Typer command:

```text
python -m apps.cli.main health
```

Required checks:

```text
Python executable
Installed modules: typer, numpy
Database counts: remedies, remedy_keywords, items
Export roots from config.yaml
Profile count from core.profile_sync
```

Gate:

```powershell
.\.venv\Scripts\python.exe -m apps.cli.main health
```

Expected:

```text
Exit-Code 0 bei gesunder Umgebung.
Exit-Code ungleich 0 mit klarer Meldung bei fehlender DB oder fehlendem Modul.
```

---

## Phase 7: UI/UX des PowerShell-Launchers verbessern

**Ziel:** Nutzer erhalten vor der Eingabe eine Systempruefung, klare Menuefuehrung und belastbare Fehlertexte.

**Files:**
- Modify: `Run-MultiplexScan.ps1`
- Modify: `docs/README.md` or `README.md`

- [x] **Step 7.1: Preflight vor Menue setzen**

Required visible checks:

```text
[OK] Python: C:\Morphic_v1\.venv\Scripts\python.exe
[OK] Typer/Numpy importierbar
[OK] remedies.db: 4079 remedies
[OK] descriptions.db: 8228 items
[OK] Profile: 35
```

Failure example:

```text
[FEHLER] Python zeigt auf Hermes-Agent-venv. Erwartet: C:\Morphic_v1\.venv\Scripts\python.exe
Behebung: .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Gate:

```powershell
.\Run-MultiplexScan.ps1
```

Expected:

```text
Der erste sichtbare Block ist der Preflight.
```

- [x] **Step 7.2: Fokus-Keyword transparent anzeigen**

Before launching Top-5 scan, print:

```text
Fokus: Bronchien
Gewichtung: Top-Fokus +25%, Sekundaer +15%, Kontext +10%
Profile: 35 Hauptprofile aus core.profile_sync
```

Gate:

```powershell
Select-String -Path .\Run-MultiplexScan.ps1 -Pattern 'Gewichtung|35 Hauptprofile|core.profile_sync'
```

Expected:

```text
Benutzer sieht die fachliche Scan-Konfiguration vor dem Start.
```

---

## Phase 8: Test- und Release-Gates

**Ziel:** Stabilitaet wird ueber feste Kommandos nachgewiesen.

**Files:**
- Modify: `README.md`
- Modify/Create: `docs/STABILIZATION_TEST_MATRIX.md`
- Test: `tests/`

- [x] **Step 8.1: Testmatrix dokumentieren**

Create `docs/STABILIZATION_TEST_MATRIX.md`:

```markdown
# Stabilization Test Matrix

1. Environment:
   `.\.venv\Scripts\python.exe -c "import typer, numpy, pytest; print('env ok')"`

2. CLI:
   `.\.venv\Scripts\python.exe -m apps.cli.main --help`

3. Import contracts:
   `.\.venv\Scripts\python.exe -m pytest tests\test_import_contracts.py -q`

4. CLI contracts:
   `.\.venv\Scripts\python.exe -m pytest tests\test_cli_contract.py -q`

5. DB health:
   `.\.venv\Scripts\python.exe -m apps.cli.main health`

6. Top-5 smoke:
   `.\.venv\Scripts\python.exe -m pytest tests\test_top5_workflow_smoke.py -q`

7. Full current tests:
   `.\.venv\Scripts\python.exe -m pytest -q`
```

Acceptance:

```powershell
Test-Path docs\STABILIZATION_TEST_MATRIX.md
```

Expected:

```text
True
```

- [ ] **Step 8.2: Abschluss-Gate fuer "lauffaehig" definieren**

The project may be called "stabil lauffaehig" only when:

```text
1. .\.venv\Scripts\python.exe -m apps.cli.main --help exits 0.
2. .\.venv\Scripts\python.exe -m apps.cli.main health exits 0.
3. .\.venv\Scripts\python.exe -m pytest tests\test_import_contracts.py tests\test_cli_contract.py tests\test_top5_workflow_smoke.py -q exits 0.
4. Ein Top-5-Scan mit kleinen Parametern schreibt JSON in ein Temp-Exportverzeichnis.
5. Run-MultiplexScan.ps1 nutzt nicht mehr die Hermes-Agent-venv.
```

Final verification command:

```powershell
.\.venv\Scripts\python.exe -m apps.cli.main --help
.\.venv\Scripts\python.exe -m apps.cli.main health
.\.venv\Scripts\python.exe -m pytest tests\test_import_contracts.py tests\test_cli_contract.py tests\test_top5_workflow_smoke.py -q
```

Expected:

```text
Alle drei Kommandos enden mit Exit-Code 0.
```

---

## Empfohlene Umsetzungsreihenfolge

| Reihenfolge | Phase | Warum zuerst / danach |
|---:|---|---|
| 1 | Phase 0 | Sichert die aktuelle Lage und verhindert unkontrolliertes Zuruecksetzen. |
| 2 | Phase 1 | Ohne lokale venv sind alle weiteren Fehlerbilder unzuverlaessig. |
| 3 | Phase 2 | Fehlende Imports muessen vor CLI- und Workflowtests geloest werden. |
| 4 | Phase 3 | Ein eindeutiger CLI-Vertrag ist Voraussetzung fuer PowerShell und Tests. |
| 5 | Phase 4 | Der konkret gemeldete Top-5-Workflow wird hier repariert. |
| 6 | Phase 5 | Reports und Trends koennen erst nach stabilem Export-Schema sinnvoll repariert werden. |
| 7 | Phase 6 | DB-Health verhindert spaet auftretende Datenfehler. |
| 8 | Phase 7 | UX lohnt sich nach stabiler technischer Basis. |
| 9 | Phase 8 | Testmatrix macht den Zustand reproduzierbar und releasefaehig. |

## Nicht empfohlene Schnellfixes

| Schnellfix | Warum vermeiden |
|---|---|
| `pip install typer` in die Hermes-venv | Verdeckt nur den ersten Fehler und laesst Fremdmodule im Suchpfad. |
| Root-Command `top3-scan` ad hoc in `apps/cli/main.py` duplizieren | Erhoeht die bestehende CLI-Dopplung. |
| Fehlende Module per `git checkout -- cli tools providers` blind wiederherstellen | Kann aktuelle Migrationen oder Nutzerloeschungen ueberschreiben. |
| Tests ignorieren, bis der komplette Workflow laeuft | Fuehrt zu spaeten Mehrfachfehlern in Reporting, DB und CLI. |
| PowerShell weiter auf `python` lassen | Reproduziert die falsche Interpreter-Auswahl. |

## Erster konkreter Reparatur-Sprint

| Tag / Block | Inhalt | Ergebnis |
|---|---|---|
| Block 1 | `.venv` erstellen, Dependencies installieren, Launcher-Python zentralisieren. | `typer`-Fehler ist an der Quelle behoben. |
| Block 2 | Import-Contract-Test schreiben, Legacy-Imports klassifizieren. | Keine Fremdmodule aus Hermes werden mehr genutzt. |
| Block 3 | `apps/cli/main.py` auf eine Root-App reduzieren. | `python -m apps.cli.main --help` funktioniert. |
| Block 4 | `scan top3-scan` und `field multiplex-scan` vertraglich fixieren. | PowerShell kann die richtigen Commands aufrufen. |
| Block 5 | Minimalen Top-5-Smoke mit kleinem `k_total` ausfuehren. | Der gemeldete Workflow ist technisch nachweisbar lauffaehig. |

## Abschlussdefinition

Das Projekt gilt nach diesem Plan nicht schon als stabil, wenn der urspruengliche `ModuleNotFoundError: No module named 'typer'` verschwindet. Stabil ist es erst, wenn die Umgebung reproduzierbar ist, die CLI-Commands eindeutig registriert sind, die fehlenden Importgrenzen bereinigt sind, ein kleiner Top-5-Scan erfolgreich exportiert und die Kern-Tests ohne Collection-Abbruch laufen.
