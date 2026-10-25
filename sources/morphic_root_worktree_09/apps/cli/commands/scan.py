import hmac
import json
import math
import os
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Mapping
from uuid import uuid4

import typer

from apps.cli.commands.helpers.utility_helpers import _topn_session_folder_id
from cli.utils.backup import log_command
from services.subgroup_service import SubgroupService
from services.analysis_service import AnalysisService
from tools.group_manager import GroupManager
from providers.hardware.hardware_entropy import sample_hid_level
from providers.hardware.entropy_sources import select_entropy_source
from core.compliance.group_activation_runtime import (
    consume_group_activation_from_environment,
    issue_child_group_activation_environment,
)
from core.compliance.operator_context import OperatorContext, resolve_operator_context
from core.profile_sync import (
    MULTIPLEX_EXPORT_RECORD_PREFIX,
    ProfileAuthorityError,
    SCAN_PROFILE_POOL_FINGERPRINT_ENV,
    SCAN_PROCESS_GATE_NONCE_ENV,
    SCAN_PROCESS_GATE_PROOF_ENV,
    SCREENING_RESULT_RECORD_PREFIX,
    build_scan_process_gate_proof,
    build_scan_profile_pool_fingerprint,
    get_top_n_analysis_profiles_by_level,
)
from core.profiles.group_vector import GroupAnalysisOptIn
from core.profiles.profile import ClientProfile


TOP3_PHASE2_TIMEOUT_SECONDS = 600
_MAX_STRUCTURED_RECORD_PAYLOAD_CHARS = 64 * 1024


def _fail_top3_scan(message: str) -> None:
    typer.echo(message, err=True)
    raise typer.Exit(code=1) from None


def _parse_single_structured_record(stdout: str, prefix: str) -> dict[str, object]:
    records = [
        line[len(prefix) :]
        for line in stdout.splitlines()
        if line.startswith(prefix)
    ]
    if len(records) != 1:
        raise ValueError("invalid structured record count")
    if len(records[0]) > _MAX_STRUCTURED_RECORD_PAYLOAD_CHARS:
        raise ValueError("invalid structured record")
    try:
        payload = json.loads(records[0])
    except (json.JSONDecodeError, RecursionError, TypeError) as exc:
        raise ValueError("invalid structured record") from exc
    if type(payload) is not dict:
        raise ValueError("invalid structured record")
    return payload


def _parse_screening_result_record(
    stdout: str,
    *,
    expected_profile: str,
    expected_score_count: int,
) -> list[float]:
    if (
        type(expected_score_count) is not int
        or not 1 <= expected_score_count <= 5
    ):
        raise ValueError("invalid expected screening score count")
    payload = _parse_single_structured_record(stdout, SCREENING_RESULT_RECORD_PREFIX)
    if (
        set(payload) != {"version", "profile", "scores"}
        or type(payload["version"]) is not int
        or payload["version"] != 1
        or type(payload["profile"]) is not str
        or payload["profile"] != expected_profile
        or type(payload["scores"]) is not list
        or len(payload["scores"]) != expected_score_count
    ):
        raise ValueError("invalid screening result")
    scores = payload["scores"]
    converted_scores: list[float] = []
    try:
        for score in scores:
            if type(score) not in {int, float}:
                raise ValueError("invalid screening result")
            converted = float(score)
            if not math.isfinite(converted):
                raise ValueError("invalid screening result")
            converted_scores.append(converted)
    except (OverflowError, TypeError, ValueError):
        raise ValueError("invalid screening result") from None
    return converted_scores


def _parse_multiplex_export_record(
    stdout: str,
    *,
    expected_profile: str,
    expected_session_id: str,
    export_root: Path,
    used_paths: set[Path],
) -> tuple[Path, Path]:
    payload = _parse_single_structured_record(stdout, MULTIPLEX_EXPORT_RECORD_PREFIX)
    if (
        set(payload)
        != {"version", "profile", "session_id", "json_path", "html_path"}
        or type(payload["version"]) is not int
        or payload["version"] != 1
        or type(payload["profile"]) is not str
        or payload["profile"] != expected_profile
        or type(payload["session_id"]) is not str
        or payload["session_id"] != expected_session_id
        or type(payload["json_path"]) is not str
        or not payload["json_path"]
        or type(payload["html_path"]) is not str
        or not payload["html_path"]
    ):
        raise ValueError("invalid export result")

    try:
        raw_json_path = Path(payload["json_path"])
        raw_html_path = Path(payload["html_path"])
        if not raw_json_path.is_absolute() or not raw_html_path.is_absolute():
            raise ValueError("invalid export result")
        root = export_root.resolve(strict=True)
        json_path = raw_json_path.resolve(strict=True)
        html_path = raw_html_path.resolve(strict=True)
        json_path.relative_to(root)
        html_path.relative_to(root)
        root_stat = root.stat()
        json_stat = json_path.stat()
        html_stat = html_path.stat()
        if (
            not stat.S_ISDIR(root_stat.st_mode)
            or not stat.S_ISREG(json_stat.st_mode)
            or json_stat.st_size <= 0
            or json_path.suffix.lower() != ".json"
            or not stat.S_ISREG(html_stat.st_mode)
            or html_stat.st_size <= 0
            or html_path.suffix.lower() not in {".html", ".htm"}
            or json_path == html_path
            or json_path in used_paths
            or html_path in used_paths
        ):
            raise ValueError("invalid export result")
    except (OSError, OverflowError, RuntimeError, ValueError):
        raise ValueError("invalid export result") from None
    return json_path, html_path


def _new_top3_session_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    return f"{timestamp}{uuid4().hex[:12]}"


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def resolve_topn_group_opt_in(
    *,
    environment: Mapping[str, str] | None = None,
    context: OperatorContext | None = None,
    now: datetime | None = None,
) -> GroupAnalysisOptIn | None:
    """Consume the private root activation once in the Top-N orchestrator."""

    return consume_group_activation_from_environment(
        os.environ if environment is None else environment,
        context=context or resolve_operator_context(),
        now=now or datetime.now().astimezone(),
    )


def build_topn_child_process_environment(
    *,
    base_environment: Mapping[str, str],
    parent_environment: Mapping[str, str],
    group_opt_in: GroupAnalysisOptIn | None,
    context: OperatorContext,
    now: datetime,
) -> dict[str, str]:
    """Build one child environment; never place activation data in the command."""

    child_environment = dict(base_environment)
    if group_opt_in is None:
        return child_environment
    child_environment.update(
        issue_child_group_activation_environment(
            group_opt_in,
            parent_environment=parent_environment,
            context=context,
            now=now,
        )
    )
    return child_environment


FOCUS_PROFILE_MAP: Dict[str, List[str]] = {
    "leber": [
        "leber_detailliert",
        "verdauung_detailliert",
        "detox",
        "toxin",
        "vergiftung_komplett",
    ],
    "galle": ["leber_detailliert", "verdauung_detailliert"],
    "niere": ["niere_detailliert", "detox", "vergiftung_komplett"],
    "darm": ["verdauung_detailliert", "pathogen", "immune"],
    "magen": ["verdauung_detailliert", "pathogen"],
    "herz": ["herz_kreislauf_fein", "regulation"],
    "lunge": ["atmung_lunge_detailliert", "pathogen"],
    "gehirn": [
        "gehirn_detailliert",
        "nervensystem_detailliert",
        "schwindel_detailliert",
    ],
    "haut": ["haut_detailliert", "allergie_detailliert", "detox"],
    "lymph": ["lymphsystem_detailliert", "immune", "detox"],
    "immun": [
        "immune",
        "immunsystem_detailliert",
        "pathogen",
        "lymphsystem_detailliert",
    ],
    "hormon": ["endokrin_detailliert", "regulation"],
    "nerv": ["nervensystem_detailliert", "gehirn_detailliert", "schmerz_detailliert"],
    "verdauung": ["verdauung_detailliert", "leber_detailliert", "pathogen"],
    "schmerz": [
        "schmerz_detailliert",
        "nervensystem_detailliert",
        "wirbelsaeule_detailliert",
    ],
    "kopfschmerz": [
        "gehirn_detailliert",
        "nervensystem_detailliert",
        "schmerz_detailliert",
        "zahn_detailliert",
    ],
    "migrän": ["gehirn_detailliert", "nervensystem_detailliert", "leber_detailliert"],
    "schwindel": [
        "schwindel_detailliert",
        "nervensystem_detailliert",
        "herz_kreislauf_fein",
    ],
    "müdig": ["endokrin_detailliert", "regulation", "immune", "vergiftung_komplett"],
    "schlaf": ["schmerz_detailliert", "nervensystem_detailliert", "psyche_detailliert"],
    "allergie": [
        "allergie_detailliert",
        "immune",
        "haut_detailliert",
        "verdauung_detailliert",
    ],
    "zahn": ["zahn_detailliert", "tote_zaehne_detailliert", "stoerfelder_toxisch"],
    "zähn": ["zahn_detailliert", "tote_zaehne_detailliert", "stoerfelder_toxisch"],
    "wirbel": [
        "wirbelsaeule_detailliert",
        "schmerz_detailliert",
        "nervensystem_detailliert",
    ],
    "rücken": ["wirbelsaeule_detailliert", "schmerz_detailliert"],
    "gelenk": ["knochen_detailliert", "schmerz_detailliert", "immune"],
    "knochen": ["knochen_detailliert", "schmerz_detailliert"],
    "entgift": ["detox", "leber_detailliert", "vergiftung_komplett", "schwermetalle"],
    "detox": ["detox", "leber_detailliert", "vergiftung_komplett", "schwermetalle"],
    "gift": ["vergiftung_komplett", "toxin", "schwermetalle", "detox"],
    "vergift": ["vergiftung_komplett", "toxin", "schwermetalle", "detox"],
    "schwermetall": [
        "schwermetalle",
        "vergiftung_komplett",
        "detox",
        "nervensystem_detailliert",
    ],
    "quecksilber": ["schwermetalle", "vergiftung_komplett", "nervensystem_detailliert"],
    "amalgam": ["schwermetalle", "zahn_detailliert", "vergiftung_komplett"],
    "strahl": ["strahlung_detailliert", "vergiftung_komplett", "immune"],
    "emf": ["strahlung_detailliert", "nervensystem_detailliert"],
    "elektro": ["strahlung_detailliert", "nervensystem_detailliert"],
    "pestizid": ["vergiftung_komplett", "toxin", "detox"],
    "herbizid": ["vergiftung_komplett", "toxin", "detox"],
    "chemie": ["vergiftung_komplett", "toxin", "allergie_detailliert"],
    "angst": ["psyche_detailliert", "nervensystem_detailliert"],
    "depression": [
        "psyche_detailliert",
        "nervensystem_detailliert",
        "endokrin_detailliert",
    ],
    "stress": ["psyche_detailliert", "endokrin_detailliert", "regulation"],
    "trauma": ["psyche_detailliert", "miasma_detailliert"],
    "psyche": ["psyche_detailliert", "nervensystem_detailliert"],
    "virus": ["pathogen", "immune", "immunsystem_detailliert"],
    "bakter": ["pathogen", "immune"],
    "pilz": ["pathogen", "immune", "verdauung_detailliert"],
    "candida": ["pathogen", "verdauung_detailliert", "immune"],
    "parasit": ["pathogen", "verdauung_detailliert", "immune"],
    "borrel": ["pathogen", "immune", "nervensystem_detailliert"],
    "infekt": ["pathogen", "immune", "immunsystem_detailliert"],
    "chakr": ["chakren_meridiane", "regulation", "psyche_detailliert"],
    "meridian": ["chakren_meridiane", "regulation"],
    "energie": [
        "regulation",
        "chakren_meridiane",
        "endokrin_detailliert",
        "mitochondrien_dysfunktion",
    ],
    "miasm": ["miasma_detailliert", "pathogen"],
    "glyphosat": [
        "pestizide_herbizide",
        "vergiftung_komplett",
        "nervensystem_detailliert",
    ],
    "medikament": [
        "medikamenten_toxizitaet",
        "vergiftung_komplett",
        "leber_detailliert",
    ],
    "nebenwirkung": ["medikamenten_toxizitaet", "vergiftung_komplett"],
    "histamin": [
        "nahrungsmittel_intoleranzen",
        "allergie_detailliert",
        "verdauung_detailliert",
    ],
    "gluten": ["nahrungsmittel_intoleranzen", "verdauung_detailliert", "immune"],
    "laktose": ["nahrungsmittel_intoleranzen", "verdauung_detailliert"],
    "intoleranz": [
        "nahrungsmittel_intoleranzen",
        "allergie_detailliert",
        "verdauung_detailliert",
    ],
    "unverträglich": ["nahrungsmittel_intoleranzen", "allergie_detailliert"],
    "mitochondr": ["mitochondrien_dysfunktion", "regulation", "vergiftung_komplett"],
    "erschöpf": ["mitochondrien_dysfunktion", "endokrin_detailliert", "regulation"],
    "fatigue": ["mitochondrien_dysfunktion", "immune", "endokrin_detailliert"],
    "chronic fatigue": ["mitochondrien_dysfunktion", "immune", "pathogen"],
    "bindegewebe": ["bindegewebe_faszien", "knochen_detailliert", "immune"],
    "faszien": [
        "bindegewebe_faszien",
        "schmerz_detailliert",
        "wirbelsaeule_detailliert",
    ],
    "kollagen": ["bindegewebe_faszien", "haut_detailliert"],
    "matrix": ["bindegewebe_faszien", "detox", "lymphsystem_detailliert"],
    "bandscheibe": [
        "wirbelsaeule_detailliert",
        "knochen_detailliert",
        "schmerz_detailliert",
        "nervensystem_detailliert",
    ],
    "bandscheiben": [
        "wirbelsaeule_detailliert",
        "knochen_detailliert",
        "schmerz_detailliert",
        "nervensystem_detailliert",
    ],
    "gedächtnis": [
        "gehirn_detailliert",
        "nervensystem_detailliert",
        "psyche_detailliert",
    ],
    "gedaechtnis": [
        "gehirn_detailliert",
        "nervensystem_detailliert",
        "psyche_detailliert",
    ],
    "konzentration": [
        "gehirn_detailliert",
        "nervensystem_detailliert",
        "endokrin_detailliert",
    ],
    "fühlen": ["psyche_detailliert", "nervensystem_detailliert", "gehirn_detailliert"],
    "fuehlen": ["psyche_detailliert", "nervensystem_detailliert", "gehirn_detailliert"],
    "gefühl": ["psyche_detailliert", "nervensystem_detailliert"],
    "emotion": [
        "psyche_detailliert",
        "nervensystem_detailliert",
        "endokrin_detailliert",
    ],
    "blut": [
        "herz_kreislauf_fein",
        "immune",
        "leber_detailliert",
        "lymphsystem_detailliert",
    ],
    "blutdruck": ["herz_kreislauf_fein", "niere_detailliert", "endokrin_detailliert"],
    "kreislauf": ["herz_kreislauf_fein", "regulation"],
    "durchblutung": ["herz_kreislauf_fein", "nervensystem_detailliert"],
    "ischias": [
        "wirbelsaeule_detailliert",
        "nervensystem_detailliert",
        "schmerz_detailliert",
    ],
    "hexenschuss": ["wirbelsaeule_detailliert", "schmerz_detailliert"],
    "lendenwirbel": [
        "wirbelsaeule_detailliert",
        "schmerz_detailliert",
        "nervensystem_detailliert",
    ],
    "halswirbel": [
        "wirbelsaeule_detailliert",
        "schmerz_detailliert",
        "nervensystem_detailliert",
    ],
    "brustwirbel": ["wirbelsaeule_detailliert", "schmerz_detailliert"],
    "skoliose": [
        "wirbelsaeule_detailliert",
        "knochen_detailliert",
        "schmerz_detailliert",
    ],
    "arthrose": ["knochen_detailliert", "schmerz_detailliert", "immune"],
    "arthritis": ["knochen_detailliert", "immune", "schmerz_detailliert"],
    "rheuma": [
        "immune",
        "knochen_detailliert",
        "schmerz_detailliert",
        "verdauung_detailliert",
    ],
    "osteoporose": ["knochen_detailliert", "endokrin_detailliert"],
    "demenz": ["gehirn_detailliert", "nervensystem_detailliert", "vergiftung_komplett"],
    "alzheimer": [
        "gehirn_detailliert",
        "nervensystem_detailliert",
        "vergiftung_komplett",
    ],
    "parkinson": [
        "gehirn_detailliert",
        "nervensystem_detailliert",
        "vergiftung_komplett",
    ],
    "multiple sklerose": ["nervensystem_detailliert", "immune", "gehirn_detailliert"],
    "ms": ["nervensystem_detailliert", "immune", "gehirn_detailliert"],
    "tinnitus": [
        "nervensystem_detailliert",
        "gehirn_detailliert",
        "zahn_detailliert",
        "schwindel_detailliert",
    ],
    "hörsturz": ["nervensystem_detailliert", "herz_kreislauf_fein"],
    "auge": ["nervensystem_detailliert", "gehirn_detailliert", "leber_detailliert"],
    "sehen": ["nervensystem_detailliert", "gehirn_detailliert", "leber_detailliert"],
    "diabetes": [
        "endokrin_detailliert",
        "verdauung_detailliert",
        "herz_kreislauf_fein",
    ],
    "schilddrüse": ["endokrin_detailliert", "immune", "regulation"],
    "schilddruese": ["endokrin_detailliert", "immune", "regulation"],
    "nebenniere": ["endokrin_detailliert", "regulation", "psyche_detailliert"],
    "burnout": [
        "endokrin_detailliert",
        "psyche_detailliert",
        "mitochondrien_dysfunktion",
    ],
    "erschöpfung": ["mitochondrien_dysfunktion", "endokrin_detailliert", "regulation"],
    "chronisch": ["mitochondrien_dysfunktion", "immune", "pathogen"],
    "autoimmun": ["immune", "immunsystem_detailliert", "verdauung_detailliert"],
    "entzündung": ["immune", "pathogen", "verdauung_detailliert"],
    "entzuendung": ["immune", "pathogen", "verdauung_detailliert"],
}


def _compute_focus_profile_bonus(focus: str, profile_name: str) -> float:
    if not focus:
        return 0.0

    focus_lower = (
        focus.lower()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    profile_lower = profile_name.lower()

    for keyword in focus_lower.split():
        if len(keyword) >= 3 and keyword in profile_lower:
            return 0.25

    for focus_key, profiles in FOCUS_PROFILE_MAP.items():
        focus_key_norm = (
            focus_key.replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
        )
        if focus_key_norm in focus_lower or focus_key in focus.lower():
            if profile_name in profiles:
                idx = profiles.index(profile_name)
                if idx == 0:
                    return 0.25
                elif idx <= 2:
                    return 0.15
                else:
                    return 0.10

    return 0.0


def _collect_current_session_scan_files(
    base_dir: Path, session_timestamp: str
) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    patterns = (
        f"**/{session_timestamp}_*_multiplex_scan.json",
        f"**/{session_timestamp}_*_field_test.json",
    )

    for pattern in patterns:
        for path in sorted(base_dir.glob(pattern)):
            resolved = path.resolve()
            if resolved in seen:
                continue
            files.append(path)
            seen.add(resolved)

    return files


def _run_topn_report_tool(label: str, cmd: list[str], env: dict[str, str]) -> bool:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        typer.echo(f"  [WARNUNG] {label} konnte nicht erstellt werden: Timeout")
        return False
    except Exception as exc:
        typer.echo(f"  [WARNUNG] {label} konnte nicht erstellt werden: {exc}")
        return False

    if result.returncode == 0:
        typer.echo(f"  [OK] {label} erstellt")
        return True

    output = (result.stdout or "") + (result.stderr or "")
    last_line = next(
        (line for line in reversed(output.splitlines()) if line.strip()), ""
    )
    detail = f": {last_line[:160]}" if last_line else ""
    typer.echo(f"  [WARNUNG] {label} konnte nicht erstellt werden{detail}")
    return False


def _phase1_template_values(profile_template: str) -> dict[str, float]:
    template = (profile_template or "phase1-default").strip().lower()
    templates = {
        "phase1-default": {
            "emotion": 0.5,
            "physisch": 0.5,
            "mental": 0.5,
            "astral": 0.5,
        },
        "personal-balanced": {
            "emotion": 0.6,
            "physisch": 0.6,
            "mental": 0.6,
            "astral": 0.6,
        },
        "personal-focused": {
            "emotion": 0.55,
            "physisch": 0.75,
            "mental": 0.65,
            "astral": 0.45,
        },
    }
    if template not in templates:
        raise typer.BadParameter(
            "profile-template must be one of phase1-default, personal-balanced or personal-focused"
        )
    return templates[template]


def _effective_adaptive_top_k(
    top_k: int, *, top_n: int, adaptive_limits: bool
) -> int:
    if not adaptive_limits:
        return top_k
    return min(top_k, max(32, top_n * 16))


def _build_interpretation_report_command(
    *,
    name: str,
    first_name: str,
    birth_date: str,
    birth_place: str,
    top_n: int,
    focus: str,
    base_dir: Path,
    local_ai: bool,
) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "tools.interpretation_generator",
        name,
        first_name,
        "--birth-date",
        birth_date,
        "--birth-place",
        birth_place,
        "--scans",
        str(top_n),
        "--focus",
        focus,
    ]
    if local_ai:
        command.append("--llm")
    command.extend(
        ["--archive-root", str(base_dir), "--output-root", str(base_dir)]
    )
    return command


def _build_phase1_cli_option_args(
    *, profile_template: str, entropy_mode: str, image_path: str, planet_type: str = ""
) -> tuple[list[str], dict[str, str]]:
    profile_values = _phase1_template_values(profile_template)
    mode = (entropy_mode or "legacy").strip().lower()
    if mode not in {"legacy", "enhanced", "hybrid"}:
        raise typer.BadParameter("entropy-mode must be one of legacy, enhanced or hybrid")

    args = [
        "--p-emotion",
        f"{profile_values['emotion']:.2f}".rstrip("0").rstrip("."),
        "--p-physisch",
        f"{profile_values['physisch']:.2f}".rstrip("0").rstrip("."),
        "--p-mental",
        f"{profile_values['mental']:.2f}".rstrip("0").rstrip("."),
        "--p-astral",
        f"{profile_values['astral']:.2f}".rstrip("0").rstrip("."),
    ]
    if mode == "hybrid":
        args.append("--hybrid-entropy")

    cleaned_image_path = (image_path or "").strip()
    if cleaned_image_path:
        args.extend(["--image", cleaned_image_path])

    cleaned_planet_type = (planet_type or "").strip()
    if cleaned_planet_type:
        args.extend(["--planet-type", cleaned_planet_type])

    return args, {"ME_ENTROPY_MODE": mode}


# Sub‑Typer für Scan‑bezogene Befehle
scan_app = typer.Typer(help="Scan‑ und Analyse‑Befehle")


# ---------------------------------------------------------------------
# groups_overview (bereits dekoriert)
# ---------------------------------------------------------------------
@log_command
@scan_app.command("groups-overview")
def groups_overview(
    json_out: bool = typer.Option(False, "--json", help="Ausgabe als JSON"),
) -> None:
    """Zeigt eine Übersicht aller verfügbaren Gruppen/Multiplexe und vergleicht sie mit dem FULL-Profil.

    - System-Gruppen: prozedural verfügbare Gruppen (SubgroupService / procedural_groups)
    - Custom-Gruppen & Multiplexe: aus tools/group_manager
    - FULL-Profil: Gruppenliste aus multiplex_scan (Profil 'full'/'therapy')
    """

    subgroup_svc = SubgroupService()
    system_groups = set(subgroup_svc.list_groups())

    manager = GroupManager()
    custom_groups = set(manager.list_custom_groups())
    custom_multiplexes = manager.list_custom_multiplexes()

    full_profile_groups = {
        "kreislauf",
        "chakren",
        "chakren_full",
        "chakren_erweitert",
        "nebenchakren",
        "meridiane",
        "tcm_punkte",
        "tcm_punkte_extended",
        "tcm_full",
        "extra_meridiane",
        "bakterien",
        "bakterien_fein",
        "viren",
        "viren_fein",
        "parasiten",
        "parasiten_fein",
        "pilze",
        "pilze_fein",
        "schwermetalle",
        "schwermetalle_tox",
        "pestizide_tox",
        "chemikalien_tox",
        "strahlung_tox",
        "emf_fein",
        "geopathie",
        "endokrin",
        "detox",
        "mikrozirkulation",
        "mitochondrien",
        "entzuendung",
        "allergene",
        "mikronaehrstoffe",
        "wirbelsaeule",
        "zahnorgane",
        "odontone",
        "schlaf",
        "homoeopathie_klassisch",
        "homoeopathie_klassisch_potenzen",
        "tcm_rezepturen",
        "tcm_rezepturen_potenzen",
        "spagyrik",
        "farbtherapie",
        "edelsteine",
        "laser_protokolle",
        "rife_cafl_proc",
        "baklayan_proc",
    }

    missing_in_system = sorted(g for g in full_profile_groups if g not in system_groups)
    extra_system = sorted(g for g in system_groups if g not in full_profile_groups)

    summary: Dict[str, object] = {
        "system_groups": sorted(system_groups),
        "full_profile_groups": sorted(full_profile_groups),
        "missing_in_system": missing_in_system,
        "extra_system_groups": extra_system,
        "custom_groups": sorted(custom_groups),
        "custom_multiplexes": sorted(custom_multiplexes),
    }

    if json_out:
        typer.echo(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    typer.echo("Morphic Engine V1 – Gruppen-/Profil-Übersicht")
    typer.echo("")

    typer.echo(f"System-Gruppen (prozedural): {len(system_groups)}")
    for g in sorted(system_groups):
        typer.echo(f"  - {g}")

    typer.echo("")
    typer.echo(f"FULL-Profil-Gruppen: {len(full_profile_groups)}")
    typer.echo(
        f"  Davon physisch vorhanden: {len(full_profile_groups - set(missing_in_system))}"
    )
    typer.echo(f"  Davon fehlend: {len(missing_in_system)}")
    if missing_in_system:
        typer.echo("  Fehlende FULL-Gruppen:")
        for g in missing_in_system:
            typer.echo(f"    - {g}")

    if extra_system:
        typer.echo("")
        typer.echo(f"System-Gruppen außerhalb des FULL-Profils: {len(extra_system)}")
        for g in extra_system:
            typer.echo(f"  - {g}")

    typer.echo("")
    typer.echo(f"Benutzerdefinierte Gruppen: {len(custom_groups)}")
    for g in sorted(custom_groups):
        typer.echo(f"  - {g}")

    typer.echo("")
    typer.echo(f"Benutzerdefinierte Multiplexe: {len(custom_multiplexes)}")
    for m in sorted(custom_multiplexes):
        typer.echo(f"  - {m}")


# ---------------------------------------------------------------------
# hw_diagnostics
# ---------------------------------------------------------------------
@log_command
@scan_app.command("hw-diagnostics")
def hw_diagnostics(
    duration_s: float = typer.Option(
        2.0, "--duration", help="Messdauer je Quelle in Sekunden"
    ),
    export: Path | None = typer.Option(
        None,
        "--export",
        help="Exportiert Ergebnisse der Hardware-Diagnose als JSON-Datei",
    ),
) -> None:
    """Diagnose der verfügbaren Hardware-Entropiequellen.

    Zeigt an, welche Quellen (cpu_timer, hid_sensor, qrng) verfügbar sind und
    welche h-Level-Werte sie liefern. Zusätzlich wird ausgegeben, welche Quelle
    `select_entropy_source` aktuell auswählen würde.
    """

    typer.echo("Morphic Engine V1 – Hardware-Diagnose")
    typer.echo(f"Messdauer: {duration_s:.2f}s")
    typer.echo("")

    result: Dict[str, object] = {"duration_s": float(duration_s), "sources": {}}
    sources: Dict[str, Dict[str, object]] = {}
    result["sources"] = sources

    cpu_src = select_entropy_source(preferred=["cpu_timer"])
    cpu_h = _clamp(cpu_src.sample_h_level(duration_s=duration_s))
    typer.echo(f"cpu_timer: verfügbar, h_level={cpu_h:.3f}")
    sources["cpu_timer"] = {"available": True, "h_level": float(cpu_h)}

    hid_src = select_entropy_source(preferred=["hid_sensor", "cpu_timer"])
    hid_h = None
    if hid_src.name() == "hid_sensor":
        try:
            hid_stats = sample_hid_level(duration_s=duration_s)
        except Exception:
            hid_stats = {"ok": False, "h_level": 0.0}
        hid_h = _clamp(float(hid_stats.get("h_level", 0.0)))
        typer.echo(f"hid_sensor: verfügbar, h_level={hid_h:.3f}")
        sources["hid_sensor"] = {
            "available": True,
            "h_level": float(hid_h),
            "ok": bool(hid_stats.get("ok")),
            "count": hid_stats.get("count"),
            "std_norm": hid_stats.get("std_norm"),
            "var_norm": hid_stats.get("var_norm"),
            "entropy": hid_stats.get("entropy"),
            "reason": hid_stats.get("reason"),
        }

        ok = bool(hid_stats.get("ok"))
        if ok:
            count = hid_stats.get("count")
            std_norm = hid_stats.get("std_norm")
            var_norm = hid_stats.get("var_norm")
            entropy = hid_stats.get("entropy")

            detail_parts = []
            if count is not None:
                try:
                    detail_parts.append(f"count={int(count)}")
                except Exception:
                    pass
            if std_norm is not None:
                try:
                    detail_parts.append(f"std_norm={float(std_norm):.3f}")
                except Exception:
                    pass
            if var_norm is not None:
                try:
                    detail_parts.append(f"var_norm={float(var_norm):.3f}")
                except Exception:
                    pass
            if entropy is not None:
                try:
                    detail_parts.append(f"entropy={float(entropy):.3f}")
                except Exception:
                    pass
            if detail_parts:
                typer.echo("  HID-Details: " + ", ".join(detail_parts))
        else:
            reason = hid_stats.get("reason")
            count = hid_stats.get("count")
            msg = "  HID-Fehler"
            if reason:
                msg += f": {reason}"
            if count is not None:
                try:
                    msg += f" (count={int(count)})"
                except Exception:
                    pass
            typer.echo(msg)
    else:
        typer.echo("hid_sensor: nicht verfügbar oder kein Gerät gefunden")
        sources["hid_sensor"] = {"available": False}

    qrng_src = select_entropy_source(preferred=["qrng", "cpu_timer"])
    qrng_h = None
    if qrng_src.name() == "qrng":
        try:
            qrng_h_val = qrng_src.sample_h_level(duration_s=duration_s)
        except Exception:
            qrng_h_val = 0.0
        qrng_h = _clamp(float(qrng_h_val))
        typer.echo(f"qrng: verfügbar, h_level={qrng_h:.3f}")
        sources["qrng"] = {"available": True, "h_level": float(qrng_h)}
    else:
        typer.echo("qrng: nicht verfügbar")
        sources["qrng"] = {"available": False}

    gpu_src = select_entropy_source(preferred=["gpu", "cpu_timer"])
    gpu_h = None
    if gpu_src.name() == "gpu":
        try:
            gpu_h_val = gpu_src.sample_h_level(duration_s=duration_s)
        except Exception:
            gpu_h_val = 0.0
        gpu_h = _clamp(float(gpu_h_val))
        typer.echo(f"gpu: verfügbar, h_level={gpu_h:.3f}")
        sources["gpu"] = {"available": True, "h_level": float(gpu_h)}
    else:
        typer.echo("gpu: nicht verfügbar")
        sources["gpu"] = {"available": False}

    network_src = select_entropy_source(preferred=["network", "cpu_timer"])
    network_h = None
    if network_src.name() == "network":
        try:
            network_h_val = network_src.sample_h_level(duration_s=duration_s)
        except Exception:
            network_h_val = 0.0
        network_h = _clamp(float(network_h_val))
        typer.echo(f"network: verfügbar, h_level={network_h:.3f}")
        sources["network"] = {"available": True, "h_level": float(network_h)}
    else:
        typer.echo("network: nicht verfügbar")
        sources["network"] = {"available": False}

    typer.echo("")
    typer.echo(
        "Adaptive Auswahl (Bevorzugung: qrng > gpu > network > hid_sensor > cpu_timer):"
    )

    selected_name = "cpu_timer"
    selected_h = cpu_h

    if qrng_src.name() == "qrng" and qrng_h is not None and qrng_h > 0.0:
        selected_name = "qrng"
        selected_h = qrng_h
    elif gpu_src.name() == "gpu" and gpu_h is not None and gpu_h > 0.0:
        selected_name = "gpu"
        selected_h = gpu_h
    elif network_src.name() == "network" and network_h is not None and network_h > 0.0:
        selected_name = "network"
        selected_h = network_h
    elif hid_src.name() == "hid_sensor" and hid_h is not None and hid_h > 0.0:
        selected_name = "hid_sensor"
        selected_h = hid_h

    typer.echo(f"  ausgewählte Quelle: {selected_name}, h_level={selected_h:.3f}")
    sources["selected"] = {"name": selected_name, "h_level": float(selected_h)}

    if export is not None:
        try:
            export.parent.mkdir(parents=True, exist_ok=True)
            export.write_text(
                json.dumps(result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            typer.echo(f"Export gespeichert: {export}")
        except Exception as exc:
            typer.echo(f"Export fehlgeschlagen: {exc}")


# ---------------------------------------------------------------------
# multiplex_scan
# ---------------------------------------------------------------------
@log_command
@scan_app.command("multiplex-scan")
def multiplex_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(
        ..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"
    ),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    profile: str = typer.Option(
        "pathogen",
        "--profile",
        "-P",
        help="Multiplex-Profil: 'pathogen', 'toxin', 'regulation', 'full' (Alias: 'therapy')",
    ),
    seed: str = typer.Option(
        "multiplex-seed", "--seed", help="Seed für prozedurale Multiplex-Kandidaten"
    ),
    p_emotion: float = typer.Option(
        0.5, "--p-emotion", min=0.0, max=1.0, help="Einstufung emotionale Ebene [0,1]"
    ),
    p_physisch: float = typer.Option(
        0.5, "--p-physisch", min=0.0, max=1.0, help="Einstufung physische Ebene [0,1]"
    ),
    p_mental: float = typer.Option(
        0.5, "--p-mental", min=0.0, max=1.0, help="Einstufung mentale Ebene [0,1]"
    ),
    p_astral: float = typer.Option(
        0.5, "--p-astral", min=0.0, max=1.0, help="Einstufung astrale Ebene [0,1]"
    ),
    hardware_profile: str = typer.Option(
        "windows",
        "--hardware-profile",
        help="Hardware-Profil: z.B. 'legacy', 'windows' oder 'debian_server'",
    ),
    focus: str = typer.Option(
        "",
        "--focus",
        help="Optionaler Fokus / Symptom (z.B. 'Narbenstörung')",
    ),
    k_total: int = typer.Option(
        512, "--k-total", min=16, help="Anzahl der Multiplex-Kandidaten"
    ),
    top_k: int = typer.Option(
        32, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"
    ),
    export: Path | None = typer.Option(
        None,
        "--export",
        help="Exportiert Ergebnisse des Multiplex-Scans als JSON+HTML",
    ),
    synergy: bool = typer.Option(
        True,
        "--synergy/--no-synergy",
        help="Aktiviert Quantum-Synergy Analyse für synergistische Kombinationen",
    ),
    synergy_combos: int = typer.Option(
        4,
        "--synergy-combos",
        min=2,
        max=5,
        help="Anzahl Items pro synergistischer Kombination (2-5)",
    ),
    synergy_threshold: float = typer.Option(
        6.0,
        "--synergy-threshold",
        min=0.0,
        max=10.0,
        help="Mindest-Score für Synergy-Kombinationen (0-10, Standard: 6.0 wie früher)",
    ),
    tcm_type: str = typer.Option(
        "",
        "--tcm-type",
        help=(
            "Optionaler TCM-Grundtyp, z.B. 'Holz-Leber', 'Feuer-Herz', "
            "'Erde-Milz', 'Metall-Lunge', 'Wasser-Niere'."
        ),
    ),
    planet_type: str = typer.Option(
        "",
        "--planet-type",
        help=(
            "Optionaler Planetentyp, z.B. 'Mars', 'Venus', 'Sonne', 'Saturn', 'Neptun'."
        ),
    ),
    debug_groups: bool = typer.Option(
        False,
        "--debug-groups",
        help="Zeigt Verteilung der Multiplex-Kandidaten pro Gruppe an",
    ),
    influence_compare: bool = typer.Option(
        False,
        "--influence-compare",
        help=(
            "Berechnet zusätzliche Influence-Scores (TCM+Organuhr) im JSON-Export "
            "zur Gegenüberstellung von Basis- und beeinflusstem Scoring."
        ),
    ),
    db_analysis_mode: bool = typer.Option(
        False,
        "--db-analysis",
        help=(
            "Aktiviert experimentelle Bruce-Copen-DB-Analyse im JSON-Export "
            "(zusätzlicher Block 'db_analysis')."
        ),
    ),
    morphic_field: bool = typer.Option(
        True,
        "--morphic-field/--no-morphic-field",
        help=(
            "Aktiviert morphische Feld-Analyse im JSON-Export "
            "(zusätzlicher Block 'morphic_field'). Standard: aktiviert."
        ),
    ),
    mf_geometry: str = typer.Option(
        "",
        "--mf-geometry",
        help=(
            "Optionale geometrische Form fuer die morphische Feld-Analyse "
            "(z.B. 'flower_of_life', 'merkaba', 'torus')."
        ),
    ),
    mf_intention: str = typer.Option(
        "",
        "--mf-intention",
        help=(
            "Optionale Intention fuer die morphische Feld-Analyse "
            "(z.B. 'healing', 'detox', 'protection', 'harmonization')."
        ),
    ),
    mf_use_hardware: bool = typer.Option(
        True,
        "--mf-use-hardware/--no-mf-use-hardware",
        help=(
            "Verwendet Hardware-Modulation (h_level) in der morphischen Feld-Analyse. "
            "Standard: aktiviert (Kozyrev-inspiriert)."
        ),
    ),
    focus_weighting: bool = typer.Option(
        True,
        "--focus-weighting/--no-focus-weighting",
        help=(
            "Steuert, ob der gesetzte Fokus das Scoring sanft gewichten darf "
            "(Multiplikator bis ca. +5%)."
        ),
    ),
    export_3d: bool = typer.Option(
        False,
        "--export-3d",
        help="Generiert eine 3D-JSON-Datei für den Morphic Viewer.",
    ),
    show_progress: bool = typer.Option(
        True,
        "--progress/--no-progress",
        help="Zeigt Fortschritts-Updates während des Scans.",
    ),
    use_hybrid_entropy: bool = typer.Option(
        False,
        "--hybrid-entropy",
        help="Verwendet Hybrid-Entropie (mehrere Quellen kombiniert).",
    ),
    show_confidence: bool = typer.Option(
        True,
        "--confidence/--no-confidence",
        help="Zeigt Konfidenz-Bewertung im Report.",
    ),
    intention: str = typer.Option(
        "",
        "--intention",
        "-I",
        help=(
            "Aktive Intention für Score-Gewichtung: "
            "'healing' (Heilung), 'clearing' (Klärung), 'protection' (Schutz), "
            "'transformation', 'harmonization', 'connection', 'activation'. "
            "Leer = keine Gewichtung."
        ),
    ),
    filename_suffix: str = typer.Option(
        "",
        "--filename-suffix",
        help="Optionaler Suffix für den Dateinamen (z.B. Profilname bei Top-3 Scan)",
    ),
    scan_type: str = typer.Option(
        "SINGLE",
        "--scan-type",
        help="Scan-Typ für Ordner-Label: 'SINGLE', 'top5_session', etc.",
    ),
    session_id: str = typer.Option(
        "",
        "--session-id",
        help="Session-ID für Top-5 Gruppierung (alle Profile derselben Session)",
    ),
    client_gender: str = typer.Option(
        "",
        "--gender",
        "-G",
        help="Geschlecht des Klienten: 'm' (männlich), 'f' (weiblich), 'd' (divers). Leer = neutral.",
    ),
    client_weight: float = typer.Option(
        0.0,
        "--weight",
        "-W",
        help="Gewicht in kg (z.B. 75.5). 0 = nicht angegeben.",
    ),
    client_height: int = typer.Option(
        0,
        "--height",
        "-H",
        help="Größe in cm (z.B. 178). 0 = nicht angegeben.",
    ),
    client_stress: int = typer.Option(
        0,
        "--stress-level",
        help="Stress-Level 1-10 (1=niedrig, 10=sehr hoch). 0 = nicht angegeben.",
    ),
    client_sleep: float = typer.Option(
        0.0,
        "--sleep-hours",
        help="Durchschnittliche Schlafstunden pro Nacht. 0 = nicht angegeben.",
    ),
    client_emf: str = typer.Option(
        "",
        "--emf-exposure",
        help="EMF-Belastung: 'niedrig', 'mittel', 'hoch'. Leer = nicht angegeben.",
    ),
    image_path: str = typer.Option(
        "",
        "--image",
        help="Optionaler Pfad zu einem Klienten-Bild (JPG/PNG) fuer Bild-Vektor-Signatur.",
    ),
) -> None:
    """Führt einen erweiterten Multiplex-Scan über vordefinierte Gruppenprofile durch.

    Diese Implementierung delegiert direkt an den bestehenden field multiplex-scan
    Command, sodass der Kompatibilitaetsalias dieselbe bewaehrte Logik nutzt.
    """
    from apps.cli.commands.field import multiplex_scan as field_multiplex_scan

    return field_multiplex_scan(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        profile=profile,
        seed=seed,
        p_emotion=p_emotion,
        p_physisch=p_physisch,
        p_mental=p_mental,
        p_astral=p_astral,
        hardware_profile=hardware_profile,
        focus=focus,
        k_total=k_total,
        top_k=top_k,
        export=export,
        synergy=synergy,
        synergy_combos=synergy_combos,
        synergy_threshold=synergy_threshold,
        tcm_type=tcm_type,
        planet_type=planet_type,
        debug_groups=debug_groups,
        influence_compare=influence_compare,
        db_analysis_mode=db_analysis_mode,
        morphic_field=morphic_field,
        mf_geometry=mf_geometry,
        mf_intention=mf_intention,
        mf_use_hardware=mf_use_hardware,
        focus_weighting=focus_weighting,
        export_3d=export_3d,
        show_progress=show_progress,
        use_hybrid_entropy=use_hybrid_entropy,
        show_confidence=show_confidence,
        intention=intention,
        filename_suffix=filename_suffix,
        scan_type=scan_type,
        session_id=session_id,
        client_gender=client_gender,
        client_weight=client_weight,
        client_height=client_height,
        client_stress=client_stress,
        client_sleep=client_sleep,
        client_emf=client_emf,
        image_path=image_path,
    )


# ---------------------------------------------------------------------
# top3_scan
# ---------------------------------------------------------------------
@log_command
@scan_app.command("top3-scan")
def top3_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(
        ..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"
    ),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    export_path: str = typer.Option(
        "C:\\Benutzer_Archive_Start", "--export", "-e", help="Export-Verzeichnis"
    ),
    focus: str = typer.Option(
        "", "--focus", "-f", help="Optionaler Fokus/Symptom des Klienten"
    ),
    k_total: int = typer.Option(
        4096, "--k-total", min=16, help="Anzahl der Multiplex-Kandidaten pro Profil"
    ),
    top_k: int = typer.Option(
        192, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"
    ),
    hardware_profile: str = typer.Option(
        "windows", "--hardware-profile", help="Hardware-Profil"
    ),
    quick_scan: bool = typer.Option(
        True, "--quick/--full", help="Schnell-Scan (weniger Kandidaten) oder Voll-Scan"
    ),
    synergy: bool = typer.Option(
        True, "--synergy/--no-synergy", help="Quantum-Synergy Analyse aktivieren"
    ),
    synergy_combos: int = typer.Option(
        4, "--synergy-combos", help="Anzahl Synergy-Kombinationen"
    ),
    synergy_threshold: float = typer.Option(
        6.0,
        "--synergy-threshold",
        help="Synergy-Schwellenwert (Standard: 6.0 wie früher)",
    ),
    top_n: int = typer.Option(
        5,
        "--top-n",
        "-n",
        min=3,
        max=10,
        help="Anzahl der Top-Profile (Standard: 5, früher 3)",
    ),
    profile_level: int = typer.Option(
        3,
        "--level",
        "-l",
        min=1,
        max=5,
        help="Profil-Level: 1=Basis(5), 2=Standard(35), 3=Erweitert(55), 4=Komplett(153+), 5=VersionL(361+)",
    ),
    profile_template: str = typer.Option(
        "phase1-default",
        "--profile-template",
        help="Phase-1 Personalprofil: phase1-default, personal-balanced oder personal-focused",
    ),
    entropy_mode: str = typer.Option(
        "legacy",
        "--entropy-mode",
        help="Entropie-Modus: legacy, enhanced oder hybrid",
    ),
    image_path: str = typer.Option(
        "",
        "--image",
        help="Optionaler Pfad zu einem Klienten-Bild (JPG/PNG) fuer Bild-Vektor-Signatur.",
    ),
    planet_type: str = typer.Option("", "--planet-type", help="Optionaler Planetentyp."),
    adaptive_limits: bool = typer.Option(
        False,
        "--adaptive-limits/--fixed-limits",
        help="Reduziert Detail-Report-Groessen adaptiv anhand Top-N.",
    ),
    local_ai: bool = typer.Option(
        False,
        "--local-ai/--no-local-ai",
        help="Fordert explizit eine lokale Ollama-Interpretation an.",
    ),
) -> None:
    """Ermittelt automatisch die Top-N relevantesten Profile und führt vollständige Analysen durch.

    Dieser Befehl führt zunächst einen schnellen Screening-Scan über alle Haupt-Profile durch,
    ermittelt die N Profile mit den höchsten Resonanzen (Standard: 5) und führt dann vollständige
    Analysen für diese Profile durch. Bei gesetztem Fokus werden fokus-relevante Profile priorisiert.

    Beispiel:
        python -m apps.cli.main scan top3-scan "Mustermann" "Max" -d 01011990 -p Berlin
        python -m apps.cli.main scan top3-scan "Mustermann" "Max" -d 01011990 -p Berlin --top-n 3 --focus "Bandscheiben"
        python -m apps.cli.main scan top3-scan "Mustermann" "Max" -d 01011990 -p Berlin --level 4
    """
    expected_fingerprint = os.environ.pop(
        SCAN_PROFILE_POOL_FINGERPRINT_ENV,
        None,
    )
    gate_nonce = os.environ.pop(SCAN_PROCESS_GATE_NONCE_ENV, None)
    gate_proof = os.environ.pop(SCAN_PROCESS_GATE_PROOF_ENV, None)
    gate_bound = gate_nonce is not None or gate_proof is not None
    if gate_bound:
        valid_shape = (
            type(gate_nonce) is str
            and re.fullmatch(r"[0-9a-f]{64}", gate_nonce) is not None
            and type(gate_proof) is str
            and re.fullmatch(r"[0-9a-f]{64}", gate_proof) is not None
            and type(expected_fingerprint) is str
            and re.fullmatch(r"[0-9a-f]{64}", expected_fingerprint) is not None
        )
        if not valid_shape:
            _fail_top3_scan(
                "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein."
            )
        expected_proof = build_scan_process_gate_proof(
            gate_nonce,
            expected_fingerprint,
        )
        if not hmac.compare_digest(gate_proof, expected_proof):
            _fail_top3_scan(
                "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein."
            )
    typer.echo("=" * 70)
    typer.echo(f"TOP-{top_n} PROFIL-ANALYSE (Level {profile_level})")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo(f"Geburtsdatum: {birth_date}")
    typer.echo(f"Geburtsort: {birth_place}")
    typer.echo("=" * 70)
    typer.echo("")

    phase1_args, phase1_env = _build_phase1_cli_option_args(
        profile_template=profile_template,
        entropy_mode=entropy_mode,
        image_path=image_path,
        planet_type=planet_type,
    )
    effective_top_k = _effective_adaptive_top_k(
        top_k, top_n=top_n, adaptive_limits=adaptive_limits
    )

    typer.echo("📊 PHASE 1: Screening aller Haupt-Profile...")
    typer.echo("-" * 50)

    # k_total=24 can yield four deduplicated scores; full screening yields five.
    screening_k = 24 if quick_scan else 48
    screening_top_k = 4 if quick_scan else 5
    profile_scores = []

    # Profile nach Level laden (Level 1-5)
    try:
        screening_profiles = get_top_n_analysis_profiles_by_level(profile_level)
    except ProfileAuthorityError:
        _fail_top3_scan("Scanprofil-Pool nicht verfügbar.")
    except Exception:
        _fail_top3_scan("Scanprofil-Pool nicht verfügbar.")

    if expected_fingerprint is not None:
        if (
            len(expected_fingerprint) != 64
            or any(character not in "0123456789abcdef" for character in expected_fingerprint)
        ):
            _fail_top3_scan(
                "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein."
            )
        try:
            actual_fingerprint = build_scan_profile_pool_fingerprint(
                profile_level,
                screening_profiles,
            )
        except Exception:
            _fail_top3_scan(
                "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein."
            )
        if not hmac.compare_digest(expected_fingerprint, actual_fingerprint):
            _fail_top3_scan(
                "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein."
            )

    if top_n > len(screening_profiles):
        _fail_top3_scan("Top-N überschreitet den bestätigten Scanprofil-Pool.")

    try:
        base_dir = Path(export_path).expanduser().resolve()
        base_dir.mkdir(parents=True, exist_ok=True)
        if not base_dir.is_dir():
            raise NotADirectoryError(base_dir)
    except Exception:
        _fail_top3_scan("Export-Verzeichnis nicht verfügbar.")

    try:
        group_context = resolve_operator_context()
        group_opt_in = resolve_topn_group_opt_in(context=group_context)
    except Exception:
        _fail_top3_scan("Scan-Aktivierung nicht verfügbar.")

    typer.echo(f"  Profil-Level: {profile_level} ({len(screening_profiles)} Profile)")

    for i, (profile_name, profile_desc) in enumerate(screening_profiles, 1):
        typer.echo(
            f"  [{i}/{len(screening_profiles)}] Screening: {profile_name}...",
            nl=False,
        )

        cmd = [
            sys.executable,
            "-m",
            "apps.cli.main",
            "field",
            "multiplex-scan",
            name,
            first_name,
            "-d",
            birth_date,
            "-p",
            birth_place,
            "--profile",
            profile_name,
            "--k-total",
            str(screening_k),
            "--top-k",
            str(screening_top_k),
            "--hardware-profile",
            hardware_profile,
            "--no-progress",
        ]
        cmd.extend(phase1_args)

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        env.update(phase1_env)
        try:
            env = build_topn_child_process_environment(
                base_environment=env,
                parent_environment=os.environ,
                group_opt_in=group_opt_in,
                context=group_context,
                now=datetime.now().astimezone(),
            )
        except Exception:
            _fail_top3_scan("Scan-Aktivierung nicht verfügbar.")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            _fail_top3_scan("Screening fehlgeschlagen.")
        except Exception:
            _fail_top3_scan("Screening fehlgeschlagen.")

        if result.returncode != 0:
            _fail_top3_scan("Screening fehlgeschlagen.")

        try:
            scores = _parse_screening_result_record(
                result.stdout or "",
                expected_profile=profile_name,
                expected_score_count=screening_top_k,
            )
        except ValueError:
            _fail_top3_scan("Screening fehlgeschlagen.")
        try:
            avg_score = math.fsum(scores) / len(scores)
        except (OverflowError, ValueError):
            _fail_top3_scan("Screening fehlgeschlagen.")
        if not math.isfinite(avg_score):
            _fail_top3_scan("Screening fehlgeschlagen.")

        profile_scores.append(
            {
                "profile": profile_name,
                "description": profile_desc,
                "avg_score": avg_score,
                "high_count": len(scores),
            }
        )
        typer.echo(f" [OK] (avg={avg_score:.5f}, n={len(scores)})")

    typer.echo("")

    if len(profile_scores) != len(screening_profiles):
        _fail_top3_scan("Screening fehlgeschlagen.")

    for p in profile_scores:
        focus_bonus = _compute_focus_profile_bonus(focus, p["profile"])
        p["focus_bonus"] = focus_bonus
        p["raw_score"] = p["avg_score"]
        p["final_score"] = p["avg_score"] * (1 + focus_bonus)

    profile_scores.sort(key=lambda x: x["final_score"], reverse=True)

    if focus:
        best_focus_profile = None
        for p in profile_scores:
            if p["focus_bonus"] > 0:
                best_focus_profile = p
                break

        if best_focus_profile:
            best_focus_raw = best_focus_profile["raw_score"]
            for p in profile_scores:
                if p["focus_bonus"] == 0 and p["raw_score"] > best_focus_raw * 1.25:
                    p["significant_override"] = True
                    typer.echo(
                        f"  [WARNUNG] {p['profile']} hat signifikant hohere Resonanz ({p['raw_score']:.5f} vs {best_focus_raw:.5f})"
                    )

    top_profiles = profile_scores[:top_n]

    if len(top_profiles) != top_n:
        _fail_top3_scan("Screening fehlgeschlagen.")

    typer.echo("=" * 70)
    typer.echo(f"[OK] TOP-{top_n} RELEVANTE PROFILE:")
    if focus:
        typer.echo(f"   (Fokus: {focus} - Gewichtung: 25%/15%/10%)")
    typer.echo("=" * 70)
    for i, p in enumerate(top_profiles, 1):
        bonus_str = (
            f" [+{p['focus_bonus'] * 100:.0f}% Fokus]"
            if p.get("focus_bonus", 0) > 0
            else ""
        )
        override_str = (
            " [WARNUNG - SIGNIFIKANT]" if p.get("significant_override") else ""
        )
        typer.echo(
            f"  {i}. {p['profile']} ({p['description']}){bonus_str}{override_str}"
        )
        typer.echo(
            f"     Resonanz: {p['raw_score']:.5f} -> Final: {p['final_score']:.5f}"
        )
    typer.echo("")

    typer.echo("=" * 70)
    typer.echo(f"[2/2] PHASE 2: Vollstaendige Analyse der Top-{top_n} Profile...")
    typer.echo("=" * 70)
    typer.echo("")

    session_timestamp = _new_top3_session_id()
    session_file_timestamp = "_".join(session_timestamp.split("_")[:2])
    catalog_session_id = _topn_session_folder_id(session_timestamp, top_n)

    results = []
    validated_json_files: list[Path] = []
    validated_profiles: set[str] = set()
    used_artifact_paths: set[Path] = set()

    for i, p in enumerate(top_profiles, 1):
        profile_name = p["profile"]
        typer.echo(f"[{i}/{top_n}] Vollstaendige Analyse: {profile_name}")
        typer.echo("-" * 50)

        profile_number = str(i).zfill(2)
        filename_suffix = (
            f"{session_file_timestamp}_{profile_number}_{profile_name}_top{top_n}"
        )

        effective_focus = focus.strip() if focus.strip() else p["description"]

        cmd = [
            sys.executable,
            "-m",
            "apps.cli.main",
            "field",
            "multiplex-scan",
            name,
            first_name,
            "-d",
            birth_date,
            "-p",
            birth_place,
            "--profile",
            profile_name,
            "--export",
            str(base_dir),
            "--k-total",
            str(k_total),
            "--top-k",
            str(effective_top_k),
            "--hardware-profile",
            hardware_profile,
            "--filename-suffix",
            filename_suffix,
            "--focus",
            effective_focus,
            "--scan-type",
            f"top{top_n}_session",
            "--session-id",
            session_timestamp,
        ]
        cmd.extend(phase1_args)

        if synergy:
            cmd.extend(
                [
                    "--synergy",
                    "--synergy-combos",
                    str(synergy_combos),
                    "--synergy-threshold",
                    str(synergy_threshold),
                ]
            )

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        env.update(phase1_env)
        try:
            env = build_topn_child_process_environment(
                base_environment=env,
                parent_environment=os.environ,
                group_opt_in=group_opt_in,
                context=group_context,
                now=datetime.now().astimezone(),
            )
        except Exception:
            _fail_top3_scan("Scan-Aktivierung nicht verfügbar.")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=TOP3_PHASE2_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            _fail_top3_scan("Vollständige Profilanalyse fehlgeschlagen.")
        except Exception:
            _fail_top3_scan("Vollständige Profilanalyse fehlgeschlagen.")

        if result.returncode != 0:
            _fail_top3_scan("Vollständige Profilanalyse fehlgeschlagen.")

        try:
            json_path, html_path = _parse_multiplex_export_record(
                result.stdout or "",
                expected_profile=profile_name,
                expected_session_id=session_timestamp,
                export_root=base_dir,
                used_paths=used_artifact_paths,
            )
        except ValueError:
            _fail_top3_scan("Vollständige Profilanalyse fehlgeschlagen.")
        if profile_name in validated_profiles:
            _fail_top3_scan("Vollständige Profilanalyse fehlgeschlagen.")
        used_artifact_paths.update({json_path, html_path})
        validated_profiles.add(profile_name)
        validated_json_files.append(json_path)

        typer.echo(f"Export gespeichert: {json_path}")
        typer.echo(f"HTML-Report gespeichert: {html_path}")
        typer.echo(
            MULTIPLEX_EXPORT_RECORD_PREFIX
            + json.dumps(
                {
                    "version": 1,
                    "profile": profile_name,
                    "session_id": catalog_session_id,
                    "json_path": str(json_path),
                    "html_path": str(html_path),
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )

        results.append({"profile": profile_name, "status": "OK"})
        typer.echo(f"  [OK] Profil {profile_name} abgeschlossen")

        typer.echo("")

    if (
        len(results) != top_n
        or any(result["status"] != "OK" for result in results)
        or len(validated_json_files) != top_n
        or validated_profiles != {profile["profile"] for profile in top_profiles}
    ):
        _fail_top3_scan("Vollständige Profilanalyse fehlgeschlagen.")

    typer.echo("=" * 70)
    typer.echo(f"TOP-{top_n} ANALYSE ZUSAMMENFASSUNG")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    if focus:
        typer.echo(f"Fokus: {focus}")
    typer.echo(f"Analysierte Profile ({top_n}):")
    for i, p in enumerate(top_profiles, 1):
        status = next(
            (r["status"] for r in results if r["profile"] == p["profile"]), "?"
        )
        status_icon = "[OK]" if status == "OK" else "[FEHLER]"
        bonus_str = (
            f" [+{p.get('focus_bonus', 0) * 100:.0f}%]"
            if p.get("focus_bonus", 0) > 0
            else ""
        )
        typer.echo(
            f"  {i}. {status_icon} {p['profile']} (Score: {p['final_score']:.5f}){bonus_str}"
        )
    typer.echo("")
    typer.echo(f"Die HTML-Berichte wurden unter {base_dir} gespeichert.")

    try:
        from tools.synergy_consolidator import consolidate_synergies
        from tools.remedy_reporter import consolidate_remedy_synergies
        from tools.reporting_common import client_report_dir, register_report_artifact

        typer.echo("")
        typer.echo("=" * 70)
        typer.echo("ERSTELLE KONSOLIDIERTE BERICHTE...")
        typer.echo("=" * 70)

        json_files = list(validated_json_files)

        if json_files:
            typer.echo(f"[OK] {len(json_files)} JSON-Dateien gefunden")

            typer.echo("  -> Erstelle Quantum-Synergy Report...")
            synergy_dir = (
                client_report_dir(
                    base_dir,
                    name,
                    first_name,
                    "Synergy",
                    birth_date,
                    birth_place,
                )
                / f"{session_timestamp}_synergy_report"
            )
            synergy_success = consolidate_synergies(
                json_files,
                synergy_dir,
                client={
                    "name": name,
                    "first_name": first_name,
                    "birth_date": birth_date,
                    "birth_place": birth_place,
                },
                focus=focus,
                session_id=session_timestamp,
            )
            if synergy_success:
                register_report_artifact(
                    synergy_dir / "synergy_gesamt.json",
                    {
                        "name": name,
                        "first_name": first_name,
                        "birth_date": birth_date,
                        "birth_place": birth_place,
                    },
                    "synergy_json",
                    label="Synergy Gesamt JSON",
                    session_id=session_timestamp,
                    focus=focus,
                    config={"command": "top3-scan", "top_n": top_n},
                )
                register_report_artifact(
                    synergy_dir / "synergy_gesamt.html",
                    {
                        "name": name,
                        "first_name": first_name,
                        "birth_date": birth_date,
                        "birth_place": birth_place,
                    },
                    "synergy_html",
                    label="Synergy Gesamt HTML",
                    session_id=session_timestamp,
                    focus=focus,
                    config={"command": "top3-scan", "top_n": top_n},
                )
                register_report_artifact(
                    synergy_dir / "synergy_gesamt.pdf",
                    {
                        "name": name,
                        "first_name": first_name,
                        "birth_date": birth_date,
                        "birth_place": birth_place,
                    },
                    "synergy_pdf",
                    label="Synergy Gesamt PDF",
                    session_id=session_timestamp,
                    focus=focus,
                    config={"command": "top3-scan", "top_n": top_n},
                )
                typer.echo("  [OK] Quantum-Synergy Report erstellt")
            else:
                typer.echo(
                    "  [WARNUNG] Quantum-Synergy Report konnte nicht erstellt werden"
                )

            typer.echo("  -> Erstelle Remedy-Kombinationen Report...")
            remedy_dir = client_report_dir(
                base_dir,
                name,
                first_name,
                "Remedies",
                birth_date,
                birth_place,
            )
            remedy_dir.mkdir(parents=True, exist_ok=True)
            remedy_success = consolidate_remedy_synergies(
                json_files,
                remedy_dir,
                top_n=top_n,
                title=f"Remedy Report - {first_name} {name}",
                session_id=session_timestamp,
                client={
                    "name": name,
                    "first_name": first_name,
                    "birth_date": birth_date,
                    "birth_place": birth_place,
                },
            )
            if remedy_success:
                for artifact_path in remedy_dir.glob(
                    f"{session_timestamp}_*_remedies.json"
                ):
                    register_report_artifact(
                        artifact_path,
                        {
                            "name": name,
                            "first_name": first_name,
                            "birth_date": birth_date,
                            "birth_place": birth_place,
                        },
                        "remedy_json",
                        label="Remedy JSON",
                        session_id=session_timestamp,
                        focus=focus,
                        config={"command": "top3-scan", "top_n": top_n},
                    )
                for artifact_path in remedy_dir.glob(
                    f"{session_timestamp}_*_remedies.html"
                ):
                    register_report_artifact(
                        artifact_path,
                        {
                            "name": name,
                            "first_name": first_name,
                            "birth_date": birth_date,
                            "birth_place": birth_place,
                        },
                        "remedy_html",
                        label="Remedy HTML",
                        session_id=session_timestamp,
                        focus=focus,
                        config={"command": "top3-scan", "top_n": top_n},
                    )
                for artifact_path in remedy_dir.glob(
                    f"{session_timestamp}_*_remedies.pdf"
                ):
                    register_report_artifact(
                        artifact_path,
                        {
                            "name": name,
                            "first_name": first_name,
                            "birth_date": birth_date,
                            "birth_place": birth_place,
                        },
                        "remedy_pdf",
                        label="Remedy PDF",
                        session_id=session_timestamp,
                        focus=focus,
                        config={"command": "top3-scan", "top_n": top_n},
                    )
                for artifact_path in remedy_dir.glob(
                    f"{session_timestamp}_*_remedy.json"
                ):
                    register_report_artifact(
                        artifact_path,
                        {
                            "name": name,
                            "first_name": first_name,
                            "birth_date": birth_date,
                            "birth_place": birth_place,
                        },
                        "remedy_profile_json",
                        label="Remedy Profil JSON",
                        session_id=session_timestamp,
                        focus=focus,
                        config={"command": "top3-scan", "top_n": top_n},
                    )
                for artifact_path in remedy_dir.glob(
                    f"{session_timestamp}_*_remedy.html"
                ):
                    register_report_artifact(
                        artifact_path,
                        {
                            "name": name,
                            "first_name": first_name,
                            "birth_date": birth_date,
                            "birth_place": birth_place,
                        },
                        "remedy_profile_html",
                        label="Remedy Profil HTML",
                        session_id=session_timestamp,
                        focus=focus,
                        config={"command": "top3-scan", "top_n": top_n},
                    )
                for artifact_path in remedy_dir.glob(
                    f"{session_timestamp}_*_remedy.pdf"
                ):
                    register_report_artifact(
                        artifact_path,
                        {
                            "name": name,
                            "first_name": first_name,
                            "birth_date": birth_date,
                            "birth_place": birth_place,
                        },
                        "remedy_profile_pdf",
                        label="Remedy Profil PDF",
                        session_id=session_timestamp,
                        focus=focus,
                        config={"command": "top3-scan", "top_n": top_n},
                    )
                typer.echo("  [OK] Remedy-Kombinationen Report erstellt")
            else:
                typer.echo(
                    "  [WARNUNG] Remedy-Kombinationen Report konnte nicht erstellt werden"
                )

            post_env = os.environ.copy()
            post_env["PYTHONIOENCODING"] = "utf-8"
            post_env["PYTHONUTF8"] = "1"

            typer.echo("  -> Erstelle Deutungsbericht...")
            _run_topn_report_tool(
                "Deutungsbericht",
                _build_interpretation_report_command(
                    name=name,
                    first_name=first_name,
                    birth_date=birth_date,
                    birth_place=birth_place,
                    top_n=top_n,
                    focus=focus,
                    base_dir=base_dir,
                    local_ai=local_ai,
                ),
                post_env,
            )

            typer.echo("  -> Erstelle Trendbericht...")
            _run_topn_report_tool(
                "Trendbericht",
                [
                    sys.executable,
                    "-m",
                    "tools.trend_analyzer",
                    name,
                    first_name,
                    "--birth-date",
                    birth_date,
                    "--birth-place",
                    birth_place,
                    "--archive-root",
                    str(base_dir),
                    "--output-root",
                    str(base_dir),
                ],
                post_env,
            )
        else:
            typer.echo(
                f"[WARNUNG] Keine JSON-Dateien fuer aktuelle Session gefunden: {session_timestamp}"
            )

    except ImportError as e:
        typer.echo(f"[WARNUNG] Konsolidierungs-Module nicht verfuegbar: {e}")
    except Exception as e:
        typer.echo(f"[WARNUNG] Fehler beim Erstellen der konsolidierten Berichte: {e}")

    typer.echo("=" * 70)


# ---------------------------------------------------------------------
# nls_3d_export
# ---------------------------------------------------------------------
@log_command
@scan_app.command("batch-scan")
def batch_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(
        ..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"
    ),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    profiles: str = typer.Option(
        "pathogen,toxin,regulation",
        "--profiles",
        help="Kommaseparierte Liste von Profilen (z.B. 'pathogen,bat_akut,toxin')",
    ),
    k_total: int = typer.Option(
        64, "--k-total", min=16, help="Anzahl der Multiplex-Kandidaten pro Profil"
    ),
    top_k: int = typer.Option(
        10, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"
    ),
    hardware_profile: str = typer.Option(
        "windows", "--hardware-profile", help="Hardware-Profil"
    ),
) -> None:
    """Führt mehrere Multiplex-Scans in Serie aus (Batch-Modus).

    Beispiel:
        python -m apps.cli.main batch-scan "Mustermann" "Max" -d 01011990 -p Berlin --profiles pathogen,bat_akut,toxin
    """
    profile_list = [p.strip() for p in profiles.split(",") if p.strip()]

    if not profile_list:
        typer.echo("⌛ Keine Profile angegeben!")
        raise typer.Exit(code=1)

    typer.echo("=" * 70)
    typer.echo("BATCH-SCAN MODUS")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo(f"Profile: {', '.join(profile_list)}")
    typer.echo(f"Kandidaten pro Profil: {k_total}")
    typer.echo("=" * 70)
    typer.echo("")

    results = []

    for i, profile in enumerate(profile_list, 1):
        typer.echo(f"[{i}/{len(profile_list)}] 🔬 Starte Scan mit Profil: {profile}")
        typer.echo("-" * 50)

        cmd = [
            sys.executable,
            "-m",
            "apps.cli.main",
            "field",
            "multiplex-scan",
            name,
            first_name,
            "-d",
            birth_date,
            "-p",
            birth_place,
            "--profile",
            profile,
            "--k-total",
            str(k_total),
            "--top-k",
            str(top_k),
            "--hardware-profile",
            hardware_profile,
            "--no-progress",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            if result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if any(
                        x in line
                        for x in [
                            "Top Items",
                            "score=",
                            "Export",
                            "B.A.T.",
                            "Empfohlene Remedies",
                            "💊",
                            "#",
                        ]
                    ):
                        typer.echo(f"  {line}")

            if result.returncode == 0:
                results.append({"profile": profile, "status": "OK"})
                typer.echo(f"  ✅ Profil {profile} abgeschlossen")
            else:
                results.append(
                    {"profile": profile, "status": "FEHLER", "error": result.stderr}
                )
                typer.echo(f"  ❌ Profil {profile} fehlgeschlagen")
                if result.stderr:
                    typer.echo(f"     Fehler: {result.stderr[:200]}")

        except Exception as exc:
            results.append(
                {"profile": profile, "status": "EXCEPTION", "error": str(exc)}
            )
            typer.echo(f"  ❌ Ausnahme bei Profil {profile}: {exc}")

        typer.echo("")

    typer.echo("=" * 70)
    typer.echo("BATCH-SCAN ZUSAMMENFASSUNG")
    typer.echo("=" * 70)

    ok_count = sum(1 for r in results if r["status"] == "OK")
    typer.echo(f"Erfolgreich: {ok_count}/{len(profile_list)}")

    for r in results:
        status_icon = "✅" if r["status"] == "OK" else "❌"
        typer.echo(f"  {status_icon} {r['profile']}: {r['status']}")

    typer.echo("=" * 70)


def _get_remedy_description(remedy_name: str, indication: str) -> str:
    """Gibt erweiterte Beschreibung für ein Remedy zurück."""
    remedy_descriptions = {
        "arnica": "Kann als energetische Unterstützung bei Verletzungen, Prellungen und Schock gesehen werden.",
        "symphytum": "Wird im Rahmen der Bioresonanz als Hinweis auf Knochenregeneration interpretiert.",
        "calendula": "Kann als energetische Unterstützung bei Wundheilung und Geweberegeneration gesehen werden.",
        "oscillococcinum": "Wird im Rahmen der Bioresonanz als Hinweis auf virale Belastungen interpretiert.",
        "influenzinum": "Kann als energetische Unterstützung bei grippalen Infekten gesehen werden.",
        "engystol": "Wird im Rahmen der Bioresonanz als Hinweis auf Immunmodulation interpretiert.",
        "echinacea": "Kann als energetische Unterstützung bei Immunsystem-Aktivierung gesehen werden.",
        "lymphomyosot": "Wird im Rahmen der Bioresonanz als Hinweis auf lymphatische Entlastung interpretiert.",
        "nux vomica": "Kann als energetische Unterstützung bei Entgiftung und Stoffwechsel gesehen werden.",
        "carbo vegetabilis": "Wird im Rahmen der Bioresonanz als Hinweis auf Erschöpfung interpretiert.",
        "rescue": "Kann als energetische Unterstützung in Stress-Situationen gesehen werden.",
    }
    remedy_lower = remedy_name.lower()
    for key, desc in remedy_descriptions.items():
        if key in remedy_lower:
            return desc
    return ""


@log_command
@scan_app.command("bat-area-scan")
def bat_area_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(
        ..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"
    ),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    top_areas: int = typer.Option(
        2, "--top-areas", help="Anzahl der Top-Bereiche für Detail-Scan"
    ),
    intention: str = typer.Option(
        "", "--intention", "-I", help="Aktive Intention (healing, clearing, etc.)"
    ),
) -> None:
    """Zweistufiger BAT-Scan: Erst Bereiche scannen, dann Top-Bereiche mit Remedies analysieren.

    Schritt 1: Scannt alle 82 BAT-Bereiche (Überschriften)
    Schritt 2: Führt Detail-Scan der Top-N Bereiche mit Remedies durch

    Beispiel:
        python -m apps.cli.main scan bat-area-scan "Mustermann" "Max" -d 01011990 -p Berlin --top-areas 3
    """
    from core.bat_report_aggregator import (
        beautify_bat_group_name,
        find_remedies_for_group,
    )
    from services.description_service import get_descriptions_batch
    from core.subgroups.procedural_groups import generate_candidates_for_group

    typer.echo("=" * 70)
    typer.echo("BAT-BEREICHS-SCAN (Zweistufig)")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo(f"Top-Bereiche für Detail-Scan: {top_areas}")
    typer.echo("")

    typer.echo("[1/3] 📋 Lade BAT-Bereiche...")
    bat_dir = Path("data/generated_groups/BAT_Akutprogramme")
    if not bat_dir.exists():
        typer.echo("❌ BAT-Verzeichnis nicht gefunden!")
        raise typer.Exit(1)

    bat_groups = []
    for json_file in sorted(bat_dir.glob("*.json")):
        group_name = f"bat_{json_file.stem.lower()}"
        bat_groups.append(group_name)

    typer.echo(f"[1/3] ✓ {len(bat_groups)} BAT-Bereiche gefunden")

    typer.echo("[2/3] 🔬 Berechne Bereichs-Resonanzen...")
    from core.subgroups.procedural_groups import generate_candidates_for_group
    from providers.hardware.entropy_sources import select_entropy_source

    personal_profile = {"emotion": 0.5, "physisch": 0.5, "mental": 0.5, "astral": 0.5}
    src = select_entropy_source(preferred=["cpu_timer"])
    h_level = max(0.0, min(1.0, src.sample_h_level(duration_s=2.0)))

    from core.client_profile import ClientProfile
    from core.analysis_service import AnalysisService
    from core.rate_encoder import RateEncoder
    from core.nls_service import NlsService

    profile_obj = ClientProfile(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        image_signature=None,
        personal_profile=personal_profile,
        planet_type=None,
    )

    analysis = AnalysisService(rate_database={}, h_level=h_level)
    client_rates = analysis.encode_profile(profile_obj)
    client_entropy = analysis.resonator.holographic_entropy(client_rates)

    encoder = RateEncoder()
    client_personal_vector = encoder.personal_profile_to_vector(personal_profile)

    def resonance_fn(a, b: float) -> float:
        return float(analysis.resonator.resonance_score(a, b))

    seed = f"{name}{first_name}{birth_date}{birth_place}"
    area_scores = []
    for group_name in bat_groups:
        try:
            items = generate_candidates_for_group(group_name, seed, k=10)
            if not items:
                continue

            nls_service = NlsService(items)
            scores = nls_service.compute_scores_v2(
                client_rates,
                client_entropy,
                resonance_fn,
            )

            if scores:
                avg_score = sum(s.get("score", 0) for s in scores) / len(scores)
                max_score = max(s.get("score", 0) for s in scores)
                area_scores.append(
                    {
                        "group": group_name,
                        "name": beautify_bat_group_name(group_name),
                        "avg_score": avg_score,
                        "max_score": max_score,
                        "item_count": len(items),
                    }
                )
        except Exception:
            continue

    area_scores.sort(key=lambda x: x["avg_score"], reverse=True)

    typer.echo(f"[2/3] ✓ {len(area_scores)} Bereiche analysiert")
    typer.echo("")

    typer.echo("=" * 70)
    typer.echo("TOP BAT-BEREICHE (nach Resonanzstärke)")
    typer.echo("=" * 70)

    for i, area in enumerate(area_scores[:10], 1):
        marker = "↑" if i <= top_areas else " "
        typer.echo(
            f"  {marker} #{i:2d} {area['name']}: Ø {area['avg_score']:.5f} (max: {area['max_score']:.5f})"
        )

    typer.echo("")

    typer.echo(f"[3/3] 🔍 Detail-Scan der Top-{top_areas} Bereiche mit Remedies...")
    typer.echo("")

    top_groups = [a["group"] for a in area_scores[:top_areas]]

    for i, group_name in enumerate(top_groups, 1):
        area_info = next((a for a in area_scores if a["group"] == group_name), None)
        typer.echo(
            f"--- Detail-Scan #{i}: {area_info['name'] if area_info else group_name} ---"
        )

        try:
            items = generate_candidates_for_group(group_name, seed, k=64)
            if items:
                nls_service = NlsService(items)
                detail_scores = nls_service.compute_scores_v2(
                    client_rates,
                    client_entropy,
                    resonance_fn,
                    client_personal_vector=client_personal_vector,
                )

                detail_scores.sort(key=lambda x: x.get("score", 0), reverse=True)

                import math as _math

                for score_entry in detail_scores:
                    factors = []
                    for key in [
                        "quantum_component",
                        "numerical_factor",
                        "geometric_factor",
                        "intention_factor",
                    ]:
                        val = score_entry.get(key)
                        if val is not None and isinstance(val, (int, float)):
                            factors.append(float(val))

                    if len(factors) >= 2:
                        mean_f = sum(factors) / len(factors)
                        variance_f = sum((x - mean_f) ** 2 for x in factors) / len(
                            factors
                        )
                        std_dev_f = _math.sqrt(max(variance_f, 0.0))
                        coherence = 1.0 / (1.0 + std_dev_f)
                        score_entry["coherence"] = max(0.0, min(1.0, coherence))
                    else:
                        score_entry["coherence"] = 1.0

                top_labels = [sc.get("label", "") for sc in detail_scores[:5]]
                descriptions = get_descriptions_batch(top_labels)

                typer.echo(f"    Top Items ({len(detail_scores)} analysiert):")
                for j, sc in enumerate(detail_scores[:5], 1):
                    label = sc.get("label", "?")
                    score = sc.get("score", 0)
                    coherence = sc.get("coherence", 0.0)

                    if coherence >= 0.8:
                        coh_symbol = "⚡⚡⚡"
                    elif coherence >= 0.6:
                        coh_symbol = "⚡⚡"
                    elif coherence >= 0.4:
                        coh_symbol = "⚡"
                    else:
                        coh_symbol = "⚠️"

                    typer.echo(
                        f"      #{j} {label}: score={score:.5f} | Kohärenz: {coherence:.2f} {coh_symbol}"
                    )

                    if label in descriptions and descriptions[label]:
                        desc = descriptions[label]
                        desc_short = desc[:100] + "..." if len(desc) > 100 else desc
                        typer.echo(f"          ℹ️  {desc_short}")

                try:
                    remedies = find_remedies_for_group(group_name)
                    if remedies:
                        typer.echo(f"    Empfohlene Remedies:")
                        for rem_name, rem_indication in remedies[:3]:
                            typer.echo(f"      💊 {rem_name}")
                            typer.echo(f"         Indikation: {rem_indication}")

                            extended_desc = _get_remedy_description(
                                rem_name, rem_indication
                            )
                            if extended_desc:
                                typer.echo(f"         {extended_desc}")
                except Exception:
                    pass

                typer.echo(f"  ✅ Detail-Scan abgeschlossen")
            else:
                typer.echo(f"  ⚠️ Keine Items für Gruppe gefunden")

        except Exception as exc:
            typer.echo(f"  ❌ Fehler: {exc}")

        typer.echo("")

    typer.echo("=" * 70)
    typer.echo("BAT-BEREICHS-SCAN ABGESCHLOSSEN")
    typer.echo("=" * 70)
    typer.echo(f"Analysierte Bereiche: {len(area_scores)}")
    typer.echo(f"Detail-Scans durchgeführt: {len(top_groups)}")
    typer.echo("")
    typer.echo("Top-Bereiche:")
    for i, area in enumerate(area_scores[:top_areas], 1):
        typer.echo(f"  #{i} {area['name']}")
    typer.echo("=" * 70)


@log_command
@scan_app.command("nls-3d-export")
def nls_3d_export(
    input_file: Path = typer.Argument(
        ..., help="JSON‑Exportdatei eines field_test‑ oder multiplex‑scan‑Laufs"
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        help="Ziel‑Datei für den 3D‑Export (falls nicht angegeben, wird im selben Ordner erstellt)",
    ),
) -> None:
    """Exportiert 3‑D‑Punkte aus einem Scan‑Export in ein JSON‑Format für das Web‑Frontend."""
    if not input_file.exists() or not input_file.is_file():
        typer.echo(f"Eingabedatei existiert nicht oder ist keine Datei: {input_file}")
        raise typer.Exit(code=1)

    try:
        payload = json.loads(input_file.read_text(encoding="utf-8"))
    except Exception as exc:
        typer.echo(f"JSON konnte nicht gelesen werden: {exc}")
        raise typer.Exit(code=1)

    sub_results = payload.get("sub_results") or {}
    items = []
    if isinstance(sub_results, dict) and isinstance(sub_results.get("top"), list):
        items = [item for item in sub_results["top"] if isinstance(item, dict)]
    if not items and isinstance(payload.get("top_scores"), list):
        items = [item for item in payload["top_scores"] if isinstance(item, dict)]
    if not items:
        typer.echo(
            "Keine geeigneten Item-Listen gefunden (sub_results.top oder top_scores)."
        )
        raise typer.Exit(code=1)

    from core.nls3d_points_new import map_item_to_point

    points = []
    for entry in items:
        pt_def = map_item_to_point(entry)
        if pt_def is None:
            continue
        label = str(entry.get("label", "") or pt_def.label).strip()
        try:
            score = float(entry.get("score", 0.0) or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        try:
            reliability = float(entry.get("reliability", score) or score)
        except (TypeError, ValueError):
            reliability = score
        points.append(
            {
                "id": pt_def.id,
                "label": label or pt_def.label,
                "layer": pt_def.layer,
                "coords": list(pt_def.coords),
                "value": score,
                "intensity": _clamp(reliability / 10.0),
                "group_hint": list(pt_def.group_hint),
            }
        )

    if not points:
        typer.echo("Keine Items konnten einem 3D-Punkt zugeordnet werden.")
        raise typer.Exit(code=1)

    if output is None:
        output = input_file.with_name(f"{input_file.stem}_3d_scan.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    client_info = (
        payload.get("client") if isinstance(payload.get("client"), dict) else {}
    )
    export_data = {
        "schema": "nls3d_points_v1",
        "source_file": str(input_file),
        "command": str(payload.get("command", "") or ""),
        "client": client_info,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "points": points,
    }
    output.write_text(
        json.dumps(export_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    from tools.reporting_common import register_report_artifact

    register_report_artifact(
        output,
        client_info,
        "nls_3d_json",
        label="NLS 3D JSON",
        config={"command": "nls_3d_export", "source_file": str(input_file)},
    )
    typer.echo(f"3D-Scan-Export geschrieben: {output}")


def _build_rate_db_from_subgroups(
    groups: List[str], seed: str, k_total: int = 64
) -> Dict[str, List[float]]:
    svc = SubgroupService()
    candidates = svc.generate_fullbody_candidates(groups, seed, k_total=k_total)
    rate_db: Dict[str, List[float]] = {}
    for item in candidates:
        label = str(item.get("label"))
        rates = [float(r) for r in item.get("rates", [])]
        if not rates:
            continue
        rate_db[label] = rates
    return rate_db


def _client_folder_name(
    name: str, first_name: str, birth_date: str, birth_place: str
) -> str:
    slug = f"{name}_{first_name}_{birth_date}_{birth_place}".strip()
    return slug.replace(" ", "_")


def _resolve_export_paths(
    export: Path,
    client: Dict[str, str],
    command: str,
    filename_suffix: str = "",
    scan_type: str = "",
    session_id: str = "",
) -> tuple[Path, Path]:
    export = export.resolve()
    suffix = export.suffix.lower()

    if suffix == ".json":
        json_path = export
        html_path = export.with_suffix(".html")
    elif suffix in {".html", ".htm"}:
        html_path = export
        json_path = export.with_suffix(".json")
    else:
        base_dir = export
        client_dir = base_dir / "Resonanz" / _client_folder_name(
            str(client.get("name", "")),
            str(client.get("first_name", "")),
            str(client.get("birth_date", "")),
            str(client.get("birth_place", "")),
        )
        if filename_suffix:
            ts = filename_suffix
        else:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if scan_type == "top5_session" and session_id:
            session_folder = f"{session_id}_TOP5_SESSION"
            session_dir = client_dir / session_folder

            parts = filename_suffix.split("_")
            if len(parts) >= 4:
                profile_num = parts[2]
                profile_name = "_".join(parts[3:-1])
                profile_folder = f"{profile_num}_{profile_name}"
            else:
                profile_folder = filename_suffix

            analysis_dir = session_dir / profile_folder
            json_path = analysis_dir / f"{ts}_{command}.json"
            html_path = analysis_dir / f"{ts}_{command}.html"
        elif scan_type:
            folder_name = f"{ts}_{scan_type}"
            analysis_dir = client_dir / folder_name
            json_path = analysis_dir / f"{ts}_{command}.json"
            html_path = analysis_dir / f"{ts}_{command}.html"
        else:
            folder_name = ts
            analysis_dir = client_dir / folder_name
            json_path = analysis_dir / f"{ts}_{command}.json"
            html_path = analysis_dir / f"{ts}_{command}.html"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    return json_path, html_path


@log_command
@scan_app.command()
def analyze(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(
        ..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09031999"
    ),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    group: List[str] = typer.Option(
        ["chakren", "meridiane"],
        "--group",
        "-g",
        help="Subgruppen, aus denen Kandidaten generiert werden",
    ),
    seed: str = typer.Option(
        "cli-seed", "--seed", help="Seed für prozedurale Kandidaten"
    ),
    fixed_h: float = typer.Option(
        None,
        "--fixed-h",
        min=0.0,
        max=1.0,
        help="Optional fester h-Level in [0,1]; ohne Angabe wird adaptiv gemessen",
    ),
    top_k: int = typer.Option(5, "--top-k", min=1, help="Anzahl der Top-Resonanzen"),
    hardware_profile: str = typer.Option(
        "windows",
        "--hardware-profile",
        help="Hardware-Profil: z.B. 'legacy', 'windows' oder 'debian_server'",
    ),
    focus: str = typer.Option(
        "",
        "--focus",
        help="Optionaler Fokus / Symptom, das in der Auswertung hervorgehoben werden soll",
    ),
    export: Path | None = typer.Option(
        None,
        "--export",
        help=(
            "Exportiert Ergebnisse der Analyse als JSON+HTML. "
            "Pfad kann Datei (.json/.html) oder Basisordner (z.B. 'history') sein."
        ),
    ),
) -> None:
    """Führt eine Kernanalyse basierend auf prozeduralen Subgruppen durch."""
    from apps.cli.commands.helpers import _render_basic_html

    rate_db = _build_rate_db_from_subgroups(group, seed, k_total=64)
    if not rate_db:
        typer.echo("Keine Kandidaten im Rate-Database erzeugt.")
        raise typer.Exit(code=1)

    _profile = (hardware_profile or "windows").strip().lower()
    src_name = "cpu_timer"

    if fixed_h is None:
        if _profile == "debian_server":
            duration = 2.0
            src = select_entropy_source(
                preferred=["qrng", "gpu", "network", "cpu_timer"]
            )
            h_level = _clamp(src.sample_h_level(duration_s=duration))
            if src.name() in ("qrng", "gpu", "network") and h_level <= 0.0:
                fallback_src = select_entropy_source(preferred=["cpu_timer"])
                fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
                if fallback_h > h_level:
                    src = fallback_src
                    h_level = fallback_h
        else:
            duration = 3.0 if _profile == "windows" else 2.0
            src = select_entropy_source(preferred=["hid_sensor", "cpu_timer"])
            h_level = _clamp(src.sample_h_level(duration_s=duration))
            if src.name() == "hid_sensor" and h_level <= 0.0:
                fallback_src = select_entropy_source(preferred=["cpu_timer"])
                fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
                if fallback_h > h_level:
                    src = fallback_src
                    h_level = fallback_h
        src_name = src.name()
    else:
        h_level = _clamp(float(fixed_h))
        src_name = "fixed"

    profile = ClientProfile(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        image_signature=None,
    )

    service = AnalysisService(rate_db, h_level=h_level)
    result = service.analyze(profile)

    resonance_map = result["resonance_map"]
    sorted_items = sorted(resonance_map.items(), key=lambda kv: kv[1], reverse=True)[
        :top_k
    ]

    typer.echo(f"Morphic Engine V1 – Analyse für {first_name} {name}")
    typer.echo(f"h_level (Hardware): {h_level:.3f} [{src_name} / profile={_profile}]")
    typer.echo(f"Morphic field: {result['morphic_field']:.4f}")
    typer.echo(f"Holographic entropy: {result['holographic_entropy']:.4f}")
    typer.echo("Top Resonances:")
    for label, score in sorted_items:
        typer.echo(f"  - {label}: {score:.5f}")

    if export is not None:
        scores_export: List[Dict[str, object]] = []
        for label, score in resonance_map.items():
            scores_export.append({"label": str(label), "score": float(score)})

        top_scores_export: List[Dict[str, object]] = []
        for label, score in sorted_items:
            top_scores_export.append({"label": str(label), "score": float(score)})

        client_info: Dict[str, str] = {
            "name": name,
            "first_name": first_name,
            "birth_date": birth_date,
            "birth_place": birth_place,
        }

        heim_sig_raw = result.get("heim_signature")
        if heim_sig_raw is None:
            heim_sig_list: List[float] = []
        else:
            heim_sig_list = [float(x) for x in heim_sig_raw]
        rates_raw = result.get("rates")
        if rates_raw is None:
            rates_list: List[float] = []
        else:
            rates_list = [float(x) for x in rates_raw]
        entropy_val = float(result.get("holographic_entropy", 0.0))
        metrics: Dict[str, object] = {
            "morphic_field": float(result.get("morphic_field", 0.0)),
            "holographic_entropy": entropy_val,
            "entropy_calibrated": entropy_val,
            "heim_signature": heim_sig_list,
            "rates": rates_list,
        }

        sub_results: Dict[str, object] = {}
        try:
            subgroup_svc = SubgroupService()
            sub_candidates = subgroup_svc.generate_fullbody_candidates(
                group, seed, k_total=64
            )
            sub_top: List[Dict[str, object]] = []
            for it in sub_candidates:
                label_it = str(it.get("label", ""))
                if not label_it or label_it not in resonance_map:
                    continue
                try:
                    score_it = float(resonance_map.get(label_it, 0.0) or 0.0)
                except Exception:
                    continue
                rates_it = [float(r) for r in it.get("rates", [])]
                entry: Dict[str, object] = {
                    "label": label_it,
                    "score": score_it,
                    "rates": rates_it,
                    "group": str(it.get("group", "")),
                }
                potency = it.get("potency")
                if potency is not None:
                    entry["potency"] = str(potency)
                desc = it.get("description")
                if desc:
                    entry["description"] = str(desc)
                sub_top.append(entry)

            sub_top_sorted = sorted(
                sub_top,
                key=lambda e: float(e.get("score", 0.0) or 0.0),
                reverse=True,
            )
            sub_results = {
                "groups": list(group),
                "method": "fullbody",
                "candidates": len(sub_candidates),
                "top": sub_top_sorted,
            }
        except Exception:
            sub_results = {}

        export_data: Dict[str, object] = {
            "schema": "morphic_analyze_export",
            "schema_version": 1,
            "command": "analyze",
            "hardware_profile": _profile,
            "hardware_source": src_name,
            "h_level": float(h_level),
            "client": client_info,
            "focus": focus,
            "metrics": metrics,
            "scores": scores_export,
            "top_scores": top_scores_export,
            "sub_results": sub_results,
        }

        try:
            json_path, html_path = _resolve_export_paths(export, client_info, "analyze")
            typer.echo(f"Export-Basis (absolut): {json_path.parent}")
            from tools.reporting_common import report_json_dumps, round_scores_for_export

            export_data = round_scores_for_export(export_data)
            json_path.write_text(
                report_json_dumps(export_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            html = _render_basic_html(export_data)
            html_path.write_text(html, encoding="utf-8")
            from tools.reporting_common import register_report_artifact, write_html_pdf

            pdf_path = write_html_pdf(html_path, html_path.stem)

            register_report_artifact(
                json_path,
                client_info,
                "analyze_json",
                label="Analyze JSON",
                focus=focus,
                config={"command": "analyze"},
            )
            register_report_artifact(
                html_path,
                client_info,
                "analyze_html",
                label="Analyze HTML",
                focus=focus,
                config={"command": "analyze"},
            )
            register_report_artifact(
                pdf_path,
                client_info,
                "analyze_pdf",
                label="Analyze PDF",
                focus=focus,
                config={"command": "analyze"},
            )
            typer.echo(f"Export gespeichert: {json_path}")
            typer.echo(f"HTML-Report gespeichert: {html_path}")
            typer.echo(f"PDF-Report gespeichert: {pdf_path}")
        except Exception as exc:
            typer.echo(f"Export fehlgeschlagen: {exc}")
