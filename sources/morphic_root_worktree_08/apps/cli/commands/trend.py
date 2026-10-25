from __future__ import annotations
import typer
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
from cli.utils.backup import log_command

# Sub‑Typer für Trend‑ und Analyse‑Befehle
trend_app = typer.Typer(help="Trend‑ und Analyse‑Befehle")

@log_command
@trend_app.command("analyze-trends")
def analyze_trends(
    input_dir: Path = typer.Argument(..., help="Ordner mit JSON-Exporten von field_test/multiplex-scan"),
    client: str = typer.Option("", "--client", help="Optional: Filter nach Klient (Teilstring in 'Vorname Nachname')"),
    top_n: int = typer.Option(10, "--top-n", min=1, help="Anzahl der Top‑Trend‑Items"),
    recent: int = typer.Option(5, "--recent", min=1, help="Anzahl der letzten Sitzungen, die berücksichtigt werden"),
) -> None:
    """Analysiert Archiv-Exports und zeigt wiederkehrende & aufsteigende Items."""

    if not input_dir.exists() or not input_dir.is_dir():
        typer.echo(f"Eingabeordner existiert nicht oder ist kein Ordner: {input_dir}")
        raise typer.Exit(code=1)

    files = sorted(input_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        typer.echo("Keine JSON-Exportdateien gefunden.")
        raise typer.Exit(code=1)

    client_filter = (client or "").strip().lower()

    label_entries: Dict[str, List[tuple[float, float]]] = {}
    mf_coherence_series: List[tuple[float, float]] = []
    mf_strength_series: List[tuple[float, float]] = []

    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        cmd = str(data.get("command", "")).strip().lower()
        if cmd not in {"field_test", "multiplex_scan"}:
            continue

        client_data = data.get("client") or {}
        first_name = str(client_data.get("first_name", "")).strip()
        last_name = str(client_data.get("name", "")).strip()
        full_name = (first_name + " " + last_name).strip()

        if client_filter and client_filter not in full_name.lower():
            continue

        top_scores = data.get("top_scores") or []
        if not isinstance(top_scores, list):
            continue

        ts = float(path.stat().st_mtime)

        mf_block = data.get("morphic_field") or {}
        if isinstance(mf_block, dict) and mf_block:
            try:
                coh = float(mf_block.get("coherence", 0.0) or 0.0)
            except Exception:
                coh = 0.0
            try:
                strength = float(mf_block.get("field_strength", 0.0) or 0.0)
            except Exception:
                strength = 0.0

            if coh or strength:
                try:
                    ts_mf = float(mf_block.get("timestamp", 0.0) or 0.0)
                except Exception:
                    ts_mf = 0.0
                if ts_mf <= 0.0:
                    ts_mf = ts
                if coh:
                    mf_coherence_series.append((ts_mf, coh))
                if strength:
                    mf_strength_series.append((ts_mf, strength))
        for entry in top_scores:
            try:
                label = str(entry["label"])
                score = float(entry["score"])
            except Exception:
                continue
            bucket = label_entries.setdefault(label, [])
            bucket.append((ts, score))

    if not label_entries:
        typer.echo("Keine passenden Trenddaten gefunden (Filter zu streng oder keine Exporte).")
        raise typer.Exit(code=1)

    stats: List[Dict[str, float | str]] = []
    for label, entries in label_entries.items():
        if len(entries) == 0:
            continue
        entries_sorted = sorted(entries, key=lambda x: x[0])
        count_all = len(entries_sorted)
        recent_entries = entries_sorted[-recent:]
        times_scores = recent_entries
        scores_recent = [s for _, s in times_scores]
        last_t, last_score = times_scores[-1]
        prev_scores = scores_recent[:-1]
        if prev_scores:
            mean_prev = sum(prev_scores) / len(prev_scores)
        else:
            mean_prev = last_score
        delta = last_score - mean_prev
        avg_all = sum(s for _, s in entries_sorted) / count_all
        stats.append(
            {
                "label": label,
                "count": float(count_all),
                "avg": float(avg_all),
                "last": float(last_score),
                "delta": float(delta),
            }
        )

    typer.echo("Morphic Engine V1 – Trendanalyse")
    if client_filter:
        typer.echo(f"Filter Klient: {client}")
    typer.echo(f"Ausgewertete Items: {len(stats)}")

    typer.echo("")
    typer.echo("Wiederkehrende Top-Items (nach Häufigkeit & Durchschnittsscore):")
    stats_recurring = sorted(
        stats,
        key=lambda d: (d["count"], d["avg"]),
        reverse=True,
    )[:top_n]
    for d in stats_recurring:
        typer.echo(
            f"  - {d['label']}: count={int(d['count'])}, avg={d['avg']:.4f}, last={d['last']:.4f}"
        )

    typer.echo("")
    typer.echo("Stärkste Aufwärtstrends (delta zwischen letzter und vorherigen Sitzungen):")
    stats_trend = [d for d in stats if d["count"] >= 2]
    stats_trend = sorted(stats_trend, key=lambda d: d["delta"], reverse=True)[:top_n]
    for d in stats_trend:
        typer.echo(
            f"  - {d['label']}: delta={d['delta']:.4f}, last={d['last']:.4f}, avg={d['avg']:.4f}, count={int(d['count'])}"
        )

    if mf_coherence_series or mf_strength_series:
        typer.echo("")
        typer.echo("Morphische Feld-Parameter (Verlauf):")

        if mf_coherence_series:
            coh_sorted = sorted(mf_coherence_series, key=lambda x: x[0])
            coh_vals = [v for _, v in coh_sorted]
            coh_last = coh_vals[-1]
            if len(coh_vals) > 1:
                coh_mean_prev = sum(coh_vals[:-1]) / float(len(coh_vals) - 1)
            else:
                coh_mean_prev = coh_last
            coh_delta = coh_last - coh_mean_prev
            coh_mean_all = sum(coh_vals) / float(len(coh_vals))
            typer.echo(
                f"  Kohärenz: letzter Wert={coh_last:.4f}, Mittelwert={coh_mean_all:.4f}, Delta={coh_delta:.4f}"
            )

        if mf_strength_series:
            fs_sorted = sorted(mf_strength_series, key=lambda x: x[0])
            fs_vals = [v for _, v in fs_sorted]
            fs_last = fs_vals[-1]
            if len(fs_vals) > 1:
                fs_mean_prev = sum(fs_vals[:-1]) / float(len(fs_vals) - 1)
            else:
                fs_mean_prev = fs_last
            fs_delta = fs_last - fs_mean_prev
            fs_mean_all = sum(fs_vals) / float(len(fs_vals))
            typer.echo(
                f"  Feldstärke: letzter Wert={fs_last:.4f}, Mittelwert={fs_mean_all:.4f}, Delta={fs_delta:.4f}"
            )


@log_command
@trend_app.command("client-trends")
def client_trends(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option("", "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"),
    birth_place: str = typer.Option("", "--birth-place", "-p", help="Geburtsort"),
    archive_root: Path = typer.Option(
        Path(r"C:\Benutzer_Archive_Start"),
        "--archive-root",
        help="Archivwurzel mit vorhandenen Scan-Exporten.",
    ),
    output_root: Path = typer.Option(
        Path(r"C:\Benutzer_Trends_Start"),
        "--output-root",
        help="Zielwurzel fuer Trendberichte.",
    ),
    output: str = typer.Option("both", "--output", "-o", help="Ausgabeformat: text, html, both"),
    save: bool = typer.Option(True, "--save/--no-save", help="Speichere Bericht im Klienten-Ordner"),
) -> None:
    """Erstellt eine Trendanalyse über alle Scans eines Klienten im Benutzer_Archive_Start.
    
    Analysiert:
    - Wiederkehrende Resonanzen über mehrere Scans
    - Zeitliche Entwicklung (steigend/fallend/stabil)
    - Gruppen-Trends
    - Scan-Historie
    
    Beispiel:
        python -m apps.cli.main trend client-trends "Mustermann" "Max"
    """

    typer.echo("=" * 70)
    typer.echo("KLIENTEN-TRENDANALYSE")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo("")
    
    cmd = [
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
        str(archive_root),
        "--output-root",
        str(output_root),
        "--output",
        output,
    ]
    
    if save:
        cmd.append("--save")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        
        if result.returncode != 0:
            typer.echo(f"\n[ERR] Trendanalyse fehlgeschlagen (Code: {result.returncode})")
            raise typer.Exit(code=1)
    
    except FileNotFoundError:
        typer.echo("[ERR] tools.trend_analyzer nicht gefunden!")
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.echo(f"[ERR] Fehler: {exc}")
        raise typer.Exit(code=1)
