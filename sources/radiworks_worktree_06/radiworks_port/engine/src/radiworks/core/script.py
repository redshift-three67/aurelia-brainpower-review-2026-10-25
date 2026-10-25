"""RadionicScript-Interpreter („PEGGOTTY") — 1:1-Port
(service/RadionicsScriptService.executeLine, FUNKTIONSANALYSE §10).

Befehle des Originals:
- `PRINT name|text`   — Variable oder Text in die Ausgabe
- `## …`              — Kommentar
- `GOTO label`        — Sprung; fehlendes Label → Fehlereintrag
- `label:`            — Marken (Zeile mit ':')
- `var = ANALYZE db`  — Analyse (exakte DB-Datei `db.txt`!) + GV je Rate
- `var = value`       — Zuweisung
- alles andere        — Fehlereintrag „NON INTERPRETED LINE"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .analysis import AnalysisResult, Rate, analyse_rate_list, check_general_vitality
from ..entropy import EntropyProvider


@dataclass
class ScriptResult:
    output: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    variables: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "output": self.output,
            "errors": self.errors,
            "variables": {k: _render(v) for k, v in self.variables.items()},
        }


def _render(value: object) -> str:
    if isinstance(value, AnalysisResult):
        return result_summary(value)
    return str(value)


def result_summary(result: AnalysisResult) -> str:
    top = ", ".join(
        f"{r.name_or_rate} {r.energetic_value}" for r in result.rate_objects[:5]
    )
    return f"AnalysisResult (GV {result.general_vitality}): {top}"


class RadionicScript:
    def __init__(self, lines: list[str]) -> None:
        self.lines = [line.rstrip() for line in lines]
        self.labels = {
            line.split(":", 1)[0].strip(): index
            for index, line in enumerate(self.lines)
            if ":" in line
        }

    def label_position(self, label: str) -> int | None:
        return self.labels.get(label)


def execute_script(
    lines: list[str],
    *,
    find_rates: Callable[[str], list[Rate]],
    entropy: EntropyProvider,
    max_steps: int = 10_000,
) -> ScriptResult:
    """Port von executeScript/executeLine — mit Schritt-Limit (Schleifenschutz)."""
    script = RadionicScript(lines)
    result = ScriptResult()
    position = 0
    steps = 0
    while position < len(script.lines):
        steps += 1
        if steps > max_steps:
            result.errors.append(f"ABBRUCH: Schrittlimit {max_steps} erreicht (Endlosschleife?)")
            break
        position = execute_line(script, script.lines[position], position, result, find_rates, entropy)
    return result


def execute_line(
    script: RadionicScript,
    line: str,
    position: int,
    result: ScriptResult,
    find_rates: Callable[[str], list[Rate]],
    entropy: EntropyProvider,
) -> int:
    stripped = line.strip()

    if stripped.startswith("PRINT "):
        name = stripped[len("PRINT "):].strip()
        if name in result.variables:
            value = result.variables[name]
            result.output.append(_render(value))
        else:
            result.output.append(name)
        return position + 1

    if stripped.startswith("## ") or stripped.startswith("##"):
        return position + 1

    if stripped.startswith("GOTO "):
        label = stripped[len("GOTO "):].strip()
        new_position = script.label_position(label)
        if new_position is not None:
            result.output.append(line)
            return new_position
        message = f"GOTO LABEL {label} DOES NOT EXIST"
        result.errors.append(message)
        return position + 1

    if ":" in stripped:
        return position + 1

    if "=" in stripped:
        left, _, right = stripped.partition("=")
        right_trimmed = right.strip()
        if right_trimmed.startswith("ANALYZE "):
            database_name = right_trimmed[len("ANALYZE "):].strip()
            result.output.append(f"Analyzing {database_name}")
            # Original: findAllBySourceName(databaseName + ".txt") — exakte Datei
            rates = find_rates(database_name + ".txt")
            if not rates:
                result.errors.append(f"Datenbank {database_name}.txt nicht gefunden")
                return position + 1
            analysis = analyse_rate_list(rates, entropy)
            analysis.general_vitality = check_general_vitality(entropy)
            for rate_object in analysis.rate_objects:
                rate_object.gv = check_general_vitality(entropy)
            result.variables[left.strip()] = analysis
        else:
            result.variables[left.strip()] = right_trimmed
        return position + 1

    result.errors.append(f"NON INTERPRETED LINE >> {stripped}")
    return position + 1
