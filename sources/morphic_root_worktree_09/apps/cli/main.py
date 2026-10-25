from __future__ import annotations

import sys
from pathlib import Path

import typer

from apps.cli.commands import helpers as _helpers
from apps.cli.commands.descriptions import descriptions_app
from apps.cli.commands.field import field_app
from apps.cli.commands.harmonize import harmonize_app
from apps.cli.commands.health import health as health_command
from apps.cli.commands.privacy import privacy_app
from apps.cli.commands.scan import analyze as _scan_analyze
from apps.cli.commands.scan import scan_app
from apps.cli.commands.sources import source_app
from apps.cli.commands.synergy import synergy_app
from apps.cli.commands.trend import trend_app
from cli.utils.backup import log_command
from monitoring.health import check_paths


for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


# Compatibility exports for legacy imports like
# ``from apps.cli.main import _render_basic_html``. The implementation lives in
# apps.cli.commands.helpers; this module only delegates.
for _helper_name in _helpers.__all__:
    globals()[_helper_name] = getattr(_helpers, _helper_name)


app = typer.Typer(help="Morphic Engine V1 - CLI fuer Analyse-Workflows.")

app.add_typer(scan_app, name="scan")
app.add_typer(trend_app, name="trend")
app.add_typer(harmonize_app, name="harmonize")
app.add_typer(descriptions_app, name="descriptions")
app.add_typer(synergy_app, name="synergy")
app.add_typer(field_app, name="field")
app.add_typer(source_app, name="sources")
app.add_typer(privacy_app, name="privacy")
app.command("analyze")(_scan_analyze)
app.command("health")(health_command)


@log_command
def log_check(
    tail: int = typer.Option(
        20,
        "--tail",
        "-n",
        help="Anzahl der zuletzt anzuzeigenden Log-Zeilen.",
    )
) -> None:
    """Zeigt die letzten Zeilen der JSON-Log-Datei an."""
    log_path = Path("logs") / "radialgo.log"
    if not log_path.is_file():
        typer.echo("Log-Datei nicht gefunden - noch kein Log-Eintrag vorhanden.")
        return
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()[-tail:]
        typer.echo("\n".join(lines))
    except Exception as exc:
        typer.echo(f"Fehler beim Lesen des Logs: {exc}", err=True)


app.command("log-check")(log_check)


try:
    from apps.cli.commands_extended import extended_app
except Exception:
    extended_app = None

if extended_app is not None:
    app.add_typer(extended_app, name="ext", help="Erweiterte Analyse-Befehle")


def main() -> None:
    check_paths()
    app()


__all__ = ["app", "main", "log_check", *_helpers.__all__]


if __name__ == "__main__":
    main()
