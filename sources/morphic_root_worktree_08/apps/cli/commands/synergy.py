"""
CLI-Befehle für Quantum-Synergy-Optimierung.
Nutzt die bestehende Quantum-Synergy-Engine für optimale Remedy-Kombinationen.
"""
from __future__ import annotations

import typer
from pathlib import Path
from typing import Optional

from cli.utils.backup import log_command

# Synergy-App für CLI
synergy_app = typer.Typer(help="Quantum-Synergy Befehle für Remedy-Optimierung.")


@log_command
@synergy_app.command("optimize")
def synergy_optimize(
    focus: str = typer.Argument(..., help="Fokus-Thema (z.B. 'Migräne', 'Erschöpfung', 'Verdauung')"),
    top: int = typer.Option(5, "--top", "-t", help="Anzahl der Top-Kombinationen (Standard: 5)"),
    size: int = typer.Option(3, "--size", "-s", help="Kombinationsgröße 2-5 Items (Standard: 3)"),
    threshold: float = typer.Option(7.0, "--threshold", "-th", help="Mindest-Synergie-Score 0-10 (Standard: 7.0)"),
    quantum: bool = typer.Option(False, "--quantum", "-q", help="Echte Quantum-Suche mit Grover-Algorithmus"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Ausführliche Ausgabe mit Details"),
) -> None:
    """
    Findet optimale synergetische Remedy-Kombinationen für einen Fokus.
    
    Beispiele:
        python -m apps.cli.main synergy optimize "Migräne"
        python -m apps.cli.main synergy optimize "Erschöpfung" --top 10 --size 4
        python -m apps.cli.main synergy optimize "Verdauung" -t 3 -s 2 -v
        python -m apps.cli.main synergy optimize "Migräne" --quantum  # Echte Quantum-Suche
    """
    try:
        from core.quantum_synergy import QuantumSynergyEngine
    except ImportError:
        typer.echo("❌ Quantum-Synergy-Engine nicht verfügbar. Bitte prüfe die Installation.", err=True)
        raise typer.Exit(1)
    
    mode = "⚛️  QUANTUM (Grover)" if quantum else "klassisch"
    typer.echo(f"\n🔬 Quantum-Synergy-Optimierung für: {focus}")
    typer.echo(f"   Modus: {mode}")
    typer.echo(f"   Parameter: Top {top}, Größe {size}, Schwelle {threshold}")
    typer.echo("   Berechne...\n")
    
    try:
        engine = QuantumSynergyEngine(use_quantum=quantum)
        results = engine.find_synergistic_triggers(
            focus=focus,
            combination_size=size,
            top_n=top,
            threshold=threshold
        )
        
        if not results:
            typer.echo(f"⚠ Keine Kombinationen mit Score ≥ {threshold} gefunden.")
            typer.echo("   Versuche einen niedrigeren Schwellenwert (--threshold).")
            return
        
        typer.echo(f"✅ {len(results)} optimale Kombinationen gefunden:\n")
        
        for idx, (items, score, details) in enumerate(results, 1):
            typer.echo(f"{'─' * 50}")
            typer.echo(f"#{idx}  Synergie-Score: {score:.2f}/10.0")
            typer.echo(f"{'─' * 50}")
            
            for item in items:
                label = item.get('label', 'Unbekannt')
                group = item.get('group', '')
                rate = item.get('copen_rate', item.get('rate', 0))
                
                if verbose and group:
                    typer.echo(f"   • {label} ({group}) [Rate: {rate}]")
                else:
                    typer.echo(f"   • {label}")
            
            if verbose and details:
                typer.echo(f"\n   Details:")
                for key, value in details.items():
                    if isinstance(value, float):
                        typer.echo(f"     - {key}: {value:.3f}")
                    else:
                        typer.echo(f"     - {key}: {value}")
            
            typer.echo("")
        
        typer.echo(f"🎯 Fokus: {focus}")
        typer.echo(f"📊 Gefunden: {len(results)} Kombinationen mit Score ≥ {threshold}")
        
    except Exception as exc:
        typer.echo(f"❌ Fehler bei der Synergy-Berechnung: {exc}", err=True)
        raise typer.Exit(1)


@log_command
@synergy_app.command("analyze")
def synergy_analyze(
    items: str = typer.Argument(..., help="Komma-getrennte Liste von Remedy-Labels"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Ausführliche Ausgabe"),
) -> None:
    """
    Analysiert die Synergie einer gegebenen Remedy-Kombination.
    
    Beispiele:
        python -m apps.cli.main synergy analyze "Arnica,Belladonna,Bryonia"
        python -m apps.cli.main synergy analyze "Nux vomica,Lycopodium" -v
    """
    try:
        from core.synergy.remedy_synergy import RemedySynergyAnalyzer
    except ImportError:
        typer.echo("❌ RemedySynergyAnalyzer nicht verfügbar.", err=True)
        raise typer.Exit(1)
    
    item_list = [item.strip() for item in items.split(",") if item.strip()]
    
    if len(item_list) < 2:
        typer.echo("⚠ Mindestens 2 Items erforderlich für Synergie-Analyse.", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"\n🔬 Synergie-Analyse für {len(item_list)} Items:")
    for item in item_list:
        typer.echo(f"   • {item}")
    typer.echo("")
    
    try:
        analyzer = RemedySynergyAnalyzer()
        
        # Items als Dicts formatieren
        item_dicts = [{"label": label, "score": 5.0, "group": ""} for label in item_list]
        
        synergy_score = analyzer.calculate_synergy_score(item_dicts)
        
        typer.echo(f"{'─' * 40}")
        if synergy_score > 1.0:
            typer.echo(f"✅ Synergie-Faktor: {synergy_score:.2f} (SYNERGETISCH)")
            typer.echo(f"   → Diese Kombination verstärkt sich gegenseitig!")
        elif synergy_score < 1.0:
            typer.echo(f"⚠ Synergie-Faktor: {synergy_score:.2f} (ANTAGONISTISCH)")
            typer.echo(f"   → Diese Kombination schwächt sich gegenseitig!")
        else:
            typer.echo(f"ℹ Synergie-Faktor: {synergy_score:.2f} (NEUTRAL)")
            typer.echo(f"   → Keine bekannte Wechselwirkung.")
        typer.echo(f"{'─' * 40}")
        
        if verbose:
            typer.echo("\n📋 Bekannte Synergie-Regeln:")
            for pair, factor in list(analyzer.synergy_rules.items())[:10]:
                typer.echo(f"   {pair[0]} + {pair[1]}: {factor:.2f}")
            typer.echo("   ...")
        
    except Exception as exc:
        typer.echo(f"❌ Fehler bei der Analyse: {exc}", err=True)
        raise typer.Exit(1)


@log_command
@synergy_app.command("stats")
def synergy_stats() -> None:
    """
    Zeigt Statistiken der Quantum-Synergy-Datenbank.
    
    Beispiel:
        python -m apps.cli.main synergy stats
    """
    try:
        from core.quantum_synergy import QuantumSynergyEngine
    except ImportError:
        typer.echo("❌ Quantum-Synergy-Engine nicht verfügbar.", err=True)
        raise typer.Exit(1)
    
    typer.echo("\n📊 Quantum-Synergy Datenbank-Statistiken\n")
    
    try:
        engine = QuantumSynergyEngine()
        
        # Statistiken abrufen (falls verfügbar)
        if hasattr(engine, 'get_statistics'):
            stats = engine.get_statistics()
            typer.echo(f"   Gesamt-Items:     {stats.get('total_items', 'N/A')}")
            typer.echo(f"   Gesamt-Gruppen:   {stats.get('total_groups', 'N/A')}")
            typer.echo(f"   Ø Items/Gruppe:   {stats.get('avg_items_per_group', 'N/A')}")
        else:
            # Fallback: Basis-Info
            if hasattr(engine, 'database') and hasattr(engine.database, 'items'):
                typer.echo(f"   Geladene Items:   {len(engine.database.items)}")
            typer.echo("   (Detaillierte Statistiken nicht verfügbar)")
        
        typer.echo(f"\n✅ Engine bereit für Synergy-Optimierung!")
        
    except Exception as exc:
        typer.echo(f"❌ Fehler beim Abrufen der Statistiken: {exc}", err=True)
        raise typer.Exit(1)
