"""
Erweiterte CLI-Befehle für Morphic Engine V1

Neue Funktionen:
- trend-analyze: Historische Scan-Analyse
- recommend-profile: Auto-Profil-Empfehlung
- scan-confidence: Konfidenz-Berechnung
- export-3d-viewer: 3D-HTML-Export
- live-scan: Scan mit Echtzeit-Streaming
"""

import os
import json
import typer
from pathlib import Path
from typing import Optional
from datetime import datetime

# Core Imports
from core.trend_analysis import (
    analyze_trends,
    format_trend_report,
    compare_two_scans,
    load_client_scans,
)
from core.profile_recommender import (
    recommend_profiles,
    get_best_profile,
    format_recommendations_display,
)
from core.confidence_intervals import (
    get_overall_scan_confidence,
    format_confidence_display,
    calculate_confidence,
)
from core.viewer_3d import (
    generate_html_viewer,
    export_to_viewer_json,
    get_body_regions,
)
from core.realtime_streaming import (
    get_stream_manager,
    console_callback,
    format_progress_bar,
)
from core.hybrid_entropy import (
    get_hybrid_h_level,
    format_hybrid_display,
)
from core.adaptive_weights import (
    get_adaptive_weights,
    explain_weights,
)
from core.multi_focus import (
    parse_multi_focus,
    format_multi_focus_display,
)

# Typer App für erweiterte Befehle
extended_app = typer.Typer(
    name="extended",
    help="Erweiterte Befehle für Morphic Engine V1",
)


@extended_app.command("trend")
def trend_analyze(
    client_pattern: str = typer.Argument(
        ...,
        help="Klientenmuster für Archiv-Suche (z.B. 'Müller*' oder 'Final*')"
    ),
    archive_path: str = typer.Option(
        "Benutzer_Archive",
        "--archive",
        "-a",
        help="Pfad zum Benutzer-Archiv"
    ),
    min_scans: int = typer.Option(
        2,
        "--min-scans",
        "-m",
        help="Minimum benötigte Scans für Analyse"
    ),
    export_json: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        help="Export als JSON-Datei"
    ),
) -> None:
    """
    Analysiert historische Scan-Daten eines Klienten.
    
    Zeigt Trends, Verbesserungen und wiederkehrende Muster.
    """
    typer.echo(f"\n🔍 Trend-Analyse für: {client_pattern}")
    typer.echo("-" * 50)
    
    result = analyze_trends(archive_path, client_pattern, min_scans)
    
    if not result:
        typer.echo(f"⚠️ Nicht genug Scans gefunden (min. {min_scans} benötigt)")
        raise typer.Exit(1)
    
    typer.echo(format_trend_report(result))
    
    if export_json:
        export_data = {
            "client": result.client_name,
            "scan_count": result.scan_count,
            "date_range": [
                result.date_range[0].isoformat(),
                result.date_range[1].isoformat()
            ],
            "overall_trend": result.overall_trend,
            "confidence": result.confidence,
            "improving_items": result.improving_items,
            "worsening_items": result.worsening_items,
            "recurring_items": result.recurring_items,
        }
        with open(export_json, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        typer.echo(f"\n📁 Export: {export_json}")


@extended_app.command("compare")
def compare_scans(
    scan1: Path = typer.Argument(..., help="Pfad zum ersten Scan (älter)"),
    scan2: Path = typer.Argument(..., help="Pfad zum zweiten Scan (neuer)"),
) -> None:
    """
    Vergleicht zwei spezifische Scans direkt.
    """
    typer.echo("\n📊 Scan-Vergleich")
    typer.echo("-" * 50)
    
    result = compare_two_scans(str(scan1), str(scan2))
    
    if "error" in result:
        typer.echo(f"❌ Fehler: {result['error']}")
        raise typer.Exit(1)
    
    typer.echo(f"Scan 1: {result['scan1_date']}")
    typer.echo(f"Scan 2: {result['scan2_date']}")
    
    if result['new_items']:
        typer.echo(f"\n🆕 Neue Items ({len(result['new_items'])}):")
        for item in result['new_items'][:5]:
            typer.echo(f"   + {item}")
    
    if result['resolved_items']:
        typer.echo(f"\n✅ Aufgelöst ({len(result['resolved_items'])}):")
        for item in result['resolved_items'][:5]:
            typer.echo(f"   - {item}")
    
    if result['changed_items']:
        typer.echo(f"\n📈 Verändert ({len(result['changed_items'])}):")
        for item in result['changed_items'][:5]:
            direction = "↑" if item['change_percent'] > 0 else "↓"
            typer.echo(f"   {direction} {item['label']}: {item['change_percent']:+.1f}%")


@extended_app.command("recommend")
def recommend_profile(
    focus: str = typer.Argument(..., help="Fokus/Symptom für Profil-Empfehlung"),
    top_k: int = typer.Option(3, "--top", "-t", help="Anzahl Empfehlungen"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Zeigt alle passenden Profile"),
) -> None:
    """
    Empfiehlt optimale Profile basierend auf Fokus/Symptom.
    """
    typer.echo(f"\n🎯 Profil-Empfehlung für: '{focus}'")
    typer.echo("-" * 50)
    
    # Multi-Fokus Support
    parsed = parse_multi_focus(focus)
    if len(parsed) > 1:
        typer.echo(f"📌 Multi-Fokus erkannt: {', '.join(parsed)}")
    
    # Adaptive Weights Info
    weights = get_adaptive_weights(focus)
    typer.echo(f"⚖️ Kategorie: {weights['category']}")
    typer.echo(explain_weights(focus))
    typer.echo()
    
    # Empfehlungen
    k = 10 if show_all else top_k
    recs = recommend_profiles(focus, top_k=k)
    typer.echo(format_recommendations_display(recs))
    
    # Best Profile Highlight
    best = get_best_profile(focus)
    if best:
        typer.echo(f"\n💡 Empfehlung: --profile {best}")


@extended_app.command("confidence")
def show_confidence(
    h_level: float = typer.Argument(..., help="H-Level Wert (0.0 - 1.0)"),
    entropy_source: str = typer.Option(
        "network",
        "--source",
        "-s",
        help="Entropie-Quelle (truerng, hid_sensor, network, cpu_timer)"
    ),
    sample_size: int = typer.Option(50, "--samples", "-n", help="Anzahl Samples"),
    group_count: int = typer.Option(8, "--groups", "-g", help="Anzahl gescannter Gruppen"),
) -> None:
    """
    Berechnet und zeigt Konfidenz-Bewertung für Scan-Parameter.
    """
    typer.echo("\n📊 Konfidenz-Analyse")
    typer.echo("-" * 50)
    
    result = get_overall_scan_confidence(h_level, entropy_source, sample_size, group_count)
    
    grade_colors = {
        'A': '🟢', 'B': '🟡', 'C': '🟠', 'D': '🔴', 'F': '⛔'
    }
    
    typer.echo(f"Gesamt-Konfidenz: {result['overall']:.1%}")
    typer.echo(f"Grade: {grade_colors.get(result['grade'], '⚪')} {result['grade']} - {result['description']}")
    typer.echo()
    typer.echo("Faktoren:")
    for key, value in result['factors'].items():
        typer.echo(f"  • {key}: {value}")
    
    if result['grade'] in ['D', 'F']:
        typer.echo("\n⚠️ Empfehlung: Verwenden Sie bessere Entropie-Quellen (TrueRNG)")


@extended_app.command("entropy")
def show_entropy(
    method: str = typer.Option(
        "weighted",
        "--method",
        "-m",
        help="Mix-Methode: 'weighted' oder 'xor'"
    ),
) -> None:
    """
    Zeigt aktuellen Hybrid-Entropie-Status.
    """
    typer.echo("\n🎲 Hybrid-Entropie-Status")
    typer.echo("-" * 50)
    
    h_level, metadata = get_hybrid_h_level(method=method)
    typer.echo(format_hybrid_display(metadata))
    typer.echo(f"\n→ Verwendbarer h_level: {h_level:.4f}")


@extended_app.command("export-3d")
def export_3d_viewer(
    scan_json: Path = typer.Argument(..., help="Pfad zur Scan-JSON-Datei"),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Ausgabe-Pfad (Standard: scan_3d.html)"
    ),
    format: str = typer.Option(
        "html",
        "--format",
        "-f",
        help="Ausgabe-Format: 'html' oder 'json'"
    ),
) -> None:
    """
    Exportiert Scan-Ergebnisse als 3D-Viewer.
    """
    typer.echo("\n🌐 3D-Export")
    typer.echo("-" * 50)
    
    # Lade Scan-Daten
    try:
        with open(scan_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        typer.echo(f"❌ Fehler beim Laden: {e}")
        raise typer.Exit(1)
    
    items = data.get('top_items', [])
    if not items:
        typer.echo("⚠️ Keine Items in Scan-Datei gefunden")
        raise typer.Exit(1)
    
    # Output Path
    if output is None:
        base = scan_json.stem
        output = Path(f"{base}_3d.html" if format == "html" else f"{base}_3d.json")
    
    # Export
    if format == "html":
        result_path = generate_html_viewer(items, str(output))
        typer.echo(f"✅ 3D-Viewer erstellt: {result_path}")
        typer.echo(f"   → Öffnen Sie die Datei im Browser")
    else:
        stats = export_to_viewer_json(items, str(output))
        typer.echo(f"✅ 3D-JSON erstellt: {stats['output']}")
        typer.echo(f"   Exportiert: {stats['exported']} Punkte")
        typer.echo(f"   Nicht gemappt: {stats['unmapped']} Items")
    
    typer.echo(f"\n📍 Verfügbare Körperregionen: {len(get_body_regions())}")


@extended_app.command("regions")
def list_regions() -> None:
    """
    Listet alle verfügbaren 3D-Körperregionen auf.
    """
    typer.echo("\n🗺️ Verfügbare 3D-Körperregionen")
    typer.echo("-" * 50)
    
    regions = get_body_regions()
    
    # Kategorisiere
    categories = {
        "Kopf": ["kopf", "gehirn", "stirn", "schläfe", "hinterkopf"],
        "Gesicht": ["auge", "nase", "mund", "ohr", "kiefer", "zahn"],
        "Hals": ["hals", "kehlkopf", "schilddrüse"],
        "Thorax": ["lunge", "herz", "brust", "bronchien", "thymus"],
        "Abdomen": ["magen", "leber", "galle", "pankreas", "milz", "darm", 
                   "dickdarm", "dünndarm", "niere", "nebenniere", "blase"],
        "Wirbelsäule": ["hws", "bws", "lws", "sakrum", "steißbein"],
        "Extremitäten": ["schulter", "oberarm", "ellenbogen", "unterarm", "hand",
                        "hüfte", "oberschenkel", "knie", "unterschenkel", "fuß"],
        "Chakren": ["wurzel", "sakral", "solar", "herz_chakra", "hals_chakra",
                   "stirn_chakra", "krone"],
        "Meridiane": [r for r in regions if "meridian_" in r],
    }
    
    for cat, items in categories.items():
        matched = [r for r in items if r in regions]
        if matched:
            typer.echo(f"\n{cat} ({len(matched)}):")
            for r in matched:
                typer.echo(f"  • {r}")
    
    typer.echo(f"\n📊 Gesamt: {len(regions)} Regionen")


@extended_app.command("focus-info")
def focus_info(
    focus: str = typer.Argument(..., help="Fokus-Begriff zur Analyse"),
) -> None:
    """
    Zeigt detaillierte Informationen zu einem Fokus-Begriff.
    """
    from core.focus_synonyms import get_canonical_focus, expand_focus_keywords, get_all_synonyms
    
    typer.echo(f"\n🔎 Fokus-Analyse: '{focus}'")
    typer.echo("-" * 50)
    
    # Multi-Fokus
    parsed = parse_multi_focus(focus)
    if len(parsed) > 1:
        typer.echo(f"📌 Multi-Fokus: {len(parsed)} Begriffe")
        for p in parsed:
            typer.echo(f"   • {p}")
        typer.echo()
    
    # Kanonische Form
    canonical = get_canonical_focus(focus)
    typer.echo(f"📖 Kanonisch: {canonical}")
    
    # Synonyme
    synonyms = get_all_synonyms(focus)
    if synonyms:
        typer.echo(f"🔗 Synonyme ({len(synonyms)}):")
        for s in list(synonyms)[:10]:
            typer.echo(f"   • {s}")
    
    # Keywords
    keywords = expand_focus_keywords(focus)
    typer.echo(f"🏷️ Erweiterte Keywords: {len(keywords)}")
    
    # Gewichtung
    weights = get_adaptive_weights(focus)
    typer.echo(f"\n⚖️ Adaptive Gewichtung:")
    typer.echo(f"   Kategorie: {weights['category']}")
    typer.echo(f"   Individual: {weights['individual']:.0%}")
    typer.echo(f"   Resonance:  {weights['resonance']:.0%}")
    typer.echo(f"   Harmony:    {weights['harmony']:.0%}")
    typer.echo(f"   Relevance:  {weights['relevance']:.0%}")
    typer.echo()
    typer.echo(f"💡 {explain_weights(focus)}")


@extended_app.command("pdf-export")
def pdf_export(
    json_path: str = typer.Argument(..., help="Pfad zur JSON-Scan-Datei"),
    output: str = typer.Option(None, "--output", "-o", help="Ausgabe-Pfad für PDF (optional)")
) -> None:
    """Exportiert Scan-Ergebnis als professionellen PDF-Report."""
    try:
        from core.pdf_handler import generate_pdf_report, get_pdf_capabilities, PDFConfig
    except ImportError as e:
        typer.echo(f"❌ PDF-Modul nicht verfügbar: {e}")
        raise typer.Exit(code=1)
    
    caps = get_pdf_capabilities()
    if not caps['export_available']:
        typer.echo("❌ reportlab nicht installiert")
        typer.echo(f"   Run: {caps['install_commands']['export']}")
        raise typer.Exit(code=1)
    
    # JSON laden
    json_file = Path(json_path)
    if not json_file.exists():
        typer.echo(f"❌ Datei nicht gefunden: {json_path}")
        raise typer.Exit(code=1)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        scan_result = json.load(f)
    
    # Output-Pfad bestimmen
    if output:
        pdf_path = output
    else:
        pdf_path = str(json_file.with_suffix('.pdf'))
    
    typer.echo(f"📄 Generiere PDF-Report...")
    typer.echo(f"   Quelle: {json_path}")
    
    try:
        result_path = generate_pdf_report(scan_result, pdf_path)
        typer.echo(f"✅ PDF erstellt: {result_path}")
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")
        raise typer.Exit(code=1)


@extended_app.command("pdf-import")
def pdf_import(
    pdf_path: str = typer.Argument(..., help="Pfad zur PDF-Datei"),
    output: str = typer.Option(None, "--output", "-o", help="Ausgabe-Pfad für JSON (optional)"),
    analyze: bool = typer.Option(True, "--analyze/--no-analyze", help="Daten analysieren")
) -> None:
    """Importiert und analysiert Daten aus einer PDF-Datei."""
    try:
        from core.pdf_handler import extract_from_pdf, analyze_extracted_data, get_pdf_capabilities
    except ImportError as e:
        typer.echo(f"❌ PDF-Modul nicht verfügbar: {e}")
        raise typer.Exit(code=1)
    
    caps = get_pdf_capabilities()
    if not caps['import_available']:
        typer.echo("❌ PyMuPDF nicht installiert")
        typer.echo(f"   Run: {caps['install_commands']['import']}")
        raise typer.Exit(code=1)
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        typer.echo(f"❌ Datei nicht gefunden: {pdf_path}")
        raise typer.Exit(code=1)
    
    typer.echo(f"📥 Extrahiere Daten aus PDF...")
    typer.echo(f"   Quelle: {pdf_path}")
    
    try:
        extracted = extract_from_pdf(pdf_path)
        
        typer.echo(f"\n📊 Extraktion:")
        typer.echo(f"   Text-Länge: {extracted['raw_text_length']} Zeichen")
        typer.echo(f"   Items gefunden: {len(extracted['items'])}")
        
        if extracted.get('metadata'):
            typer.echo(f"\n📋 Metadaten:")
            for k, v in extracted['metadata'].items():
                typer.echo(f"   {k}: {v}")
        
        if analyze and extracted['items']:
            analysis = analyze_extracted_data(extracted)
            typer.echo(f"\n🔬 Analyse:")
            typer.echo(f"   Qualitäts-Score: {analysis['quality_score']:.0%}")
            typer.echo(f"\n   Kategorien:")
            for cat, count in analysis['categories'].items():
                if count > 0:
                    typer.echo(f"     • {cat}: {count}")
            
            if analysis['suggestions']:
                typer.echo(f"\n   💡 Vorschläge:")
                for sug in analysis['suggestions']:
                    typer.echo(f"     • {sug['type']}: {sug['name']}")
                    typer.echo(f"       Grund: {sug['reason']}")
            
            extracted['analysis'] = analysis
        
        # Output speichern
        if output or len(extracted['items']) > 0:
            out_path = output or str(pdf_file.with_suffix('.extracted.json'))
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(extracted, f, indent=2, ensure_ascii=False)
            typer.echo(f"\n✅ Daten gespeichert: {out_path}")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")
        raise typer.Exit(code=1)


@extended_app.command("pdf-status")
def pdf_status() -> None:
    """Zeigt Status der PDF-Funktionen."""
    try:
        from core.pdf_handler import get_pdf_capabilities
        caps = get_pdf_capabilities()
    except ImportError:
        caps = {'export_available': False, 'import_available': False}
    
    typer.echo("📄 PDF-Handler Status")
    typer.echo("-" * 40)
    typer.echo(f"Export (reportlab): {'✅ Verfügbar' if caps.get('export_available') else '❌ Nicht installiert'}")
    typer.echo(f"Import (PyMuPDF):   {'✅ Verfügbar' if caps.get('import_available') else '❌ Nicht installiert'}")
    
    # Advanced Import Status
    try:
        from core.pdf_advanced_import import get_import_status
        status = get_import_status()
        
        typer.echo(f"OCR (Tesseract):    {'✅ Verfügbar' if status.get('ocr_available') else '❌ Nicht installiert'}")
        
        typer.echo(f"\n📂 Import-Ordner:")
        typer.echo(f"   Import:    {status['folders']['import']}")
        typer.echo(f"   Gruppen:   {status['folders']['groups']}")
        typer.echo(f"   NLS-DBs:   {status['folders']['nls']}")
        typer.echo(f"\n📊 Statistik:")
        typer.echo(f"   Pending PDFs:      {status['pending_imports']}")
        typer.echo(f"   Generierte Gruppen: {status['generated_groups']}")
        typer.echo(f"   NLS-Datenbanken:   {status['nls_databases']}")
        
        if status['import_files']:
            typer.echo(f"\n📥 Bereit zum Import:")
            for f in status['import_files'][:5]:
                typer.echo(f"   • {f}")
        
        # OCR Installation hints
        if not status.get('ocr_available'):
            typer.echo(f"\n⚠️ OCR für Bild-PDFs nicht verfügbar:")
            typer.echo(f"   1. {status['install_hints']['ocr']}")
            typer.echo(f"   2. {status['install_hints']['tesseract']}")
    except ImportError:
        pass
    
    if not caps.get('export_available') or not caps.get('import_available'):
        typer.echo("\n📦 Installation:")
        if not caps.get('export_available'):
            typer.echo("   pip install reportlab")
        if not caps.get('import_available'):
            typer.echo("   pip install PyMuPDF")


@extended_app.command("pdf-analyze")
def pdf_analyze(
    pdf_path: str = typer.Argument(..., help="Pfad zur PDF-Datei"),
    create_groups: bool = typer.Option(False, "--create-groups", "-g", help="Gruppen automatisch erstellen"),
    create_nls: bool = typer.Option(False, "--create-nls", "-n", help="NLS-Datenbank erstellen"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Detaillierte Ausgabe")
) -> None:
    """Analysiert PDF strukturiert und erstellt optional Gruppen/NLS-DBs."""
    try:
        from core.pdf_advanced_import import (
            advanced_pdf_import,
            create_group_from_import,
            create_nls_database_from_import,
            ensure_import_folders
        )
    except ImportError as e:
        typer.echo(f"❌ Advanced Import nicht verfügbar: {e}")
        raise typer.Exit(code=1)
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        typer.echo(f"❌ Datei nicht gefunden: {pdf_path}")
        raise typer.Exit(code=1)
    
    typer.echo(f"🔬 Analysiere PDF strukturiert...")
    typer.echo(f"   Quelle: {pdf_path}")
    
    try:
        result = advanced_pdf_import(pdf_path)
        
        typer.echo(f"\n📊 Analyse-Ergebnis:")
        typer.echo(f"   Seiten: {result.total_pages}")
        typer.echo(f"   Qualitäts-Score: {result.quality_score:.0%}")
        typer.echo(f"   Erkannte Gruppen: {len(result.groups)}")
        
        total_items = sum(len(g.items) for g in result.groups)
        typer.echo(f"   Gesamt Items: {total_items}")
        
        if verbose or len(result.groups) <= 5:
            typer.echo(f"\n📋 Gruppen:")
            for group in result.groups:
                cat_emoji = {
                    'pathogen': '🦠', 'toxin': '☠️', 'organ': '🫀',
                    'nutrient': '💊', 'remedy': '🌿', 'symptom': '🤒',
                    'frequency': '📡', 'unknown': '❓'
                }.get(group.category, '❓')
                
                typer.echo(f"   {cat_emoji} {group.name} ({len(group.items)} Items, {group.confidence:.0%} Konf.)")
                
                if verbose:
                    for item in group.items[:5]:
                        val_str = f" = {item.value}" if item.value else ""
                        typer.echo(f"      • {item.label}{val_str}")
                    if len(group.items) > 5:
                        typer.echo(f"      ... und {len(group.items) - 5} weitere")
        
        # Vorschläge anzeigen
        if result.suggestions:
            typer.echo(f"\n💡 Vorschläge ({len(result.suggestions)}):")
            for sug in result.suggestions:
                typer.echo(f"   → {sug['action']}")
        
        # Gruppen erstellen wenn gewünscht
        created_groups = []
        if create_groups:
            typer.echo(f"\n📦 Erstelle Gruppen...")
            folders = ensure_import_folders()
            for group in result.groups:
                if len(group.items) >= 3 and group.confidence >= 0.4:
                    try:
                        path = create_group_from_import(group)
                        created_groups.append(path)
                        typer.echo(f"   ✅ {path.name}")
                    except Exception as e:
                        typer.echo(f"   ❌ {group.name}: {e}")
        
        # NLS-DB erstellen wenn gewünscht
        if create_nls and total_items >= 5:
            typer.echo(f"\n🗄️ Erstelle NLS-Datenbank...")
            try:
                db_path = create_nls_database_from_import(result)
                typer.echo(f"   ✅ {db_path}")
            except Exception as e:
                typer.echo(f"   ❌ Fehler: {e}")
        
        # Ergebnis-JSON speichern
        output_json = pdf_file.with_suffix('.analysis.json')
        result_dict = {
            'source_file': result.source_file,
            'extracted_at': result.extracted_at,
            'total_pages': result.total_pages,
            'quality_score': result.quality_score,
            'groups': [
                {
                    'name': g.name,
                    'category': g.category,
                    'confidence': g.confidence,
                    'items': [{'label': i.label, 'value': i.value, 'category': i.category} for i in g.items]
                }
                for g in result.groups
            ],
            'suggestions': result.suggestions,
            'created_groups': [str(p) for p in created_groups] if created_groups else []
        }
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        typer.echo(f"\n✅ Analyse gespeichert: {output_json}")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")
        import traceback
        if verbose:
            traceback.print_exc()
        raise typer.Exit(code=1)


@extended_app.command("bat-import")
def bat_import_cmd(
    pdf_path: str = typer.Argument(..., help="Pfad zur B.A.T. PDF-Datei"),
    preview: bool = typer.Option(True, "--preview/--no-preview", help="Nur Vorschau"),
    create: bool = typer.Option(False, "--create", "-c", help="Gruppen erstellen")
) -> None:
    """Importiert B.A.T. Akutprogramm PDF mit korrektem Frequenz-Format."""
    try:
        from core.bat_importer import import_bat_pdf, export_to_morphic_groups
        from core.pdf_advanced_import import GENERATED_GROUPS_FOLDER, ensure_import_folders
    except ImportError as e:
        typer.echo(f"❌ Import-Fehler: {e}")
        raise typer.Exit(code=1)
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        typer.echo(f"❌ Datei nicht gefunden: {pdf_path}")
        raise typer.Exit(code=1)
    
    typer.echo(f"🔬 B.A.T. Import: {pdf_path}")
    typer.echo("-" * 50)
    
    result = import_bat_pdf(pdf_path)
    
    typer.echo(f"📦 Hauptgruppe: {result.main_group}")
    typer.echo(f"📂 Untergruppen: {len(result.subgroups)}")
    typer.echo(f"📋 Gesamt Items: {result.total_items}")
    
    if preview:
        typer.echo(f"\n{'='*50}")
        typer.echo("VORSCHAU (erste 3 Gruppen, je 5 Items)")
        typer.echo(f"{'='*50}")
        
        for group in result.subgroups[:3]:
            typer.echo(f"\n📂 {group.full_name}")
            typer.echo(f"   Items: {len(group.items)}")
            for item in group.items[:5]:
                typer.echo(f"   • {item.label}")
                typer.echo(f"     Frequenz: {item.frequency_hz}")
                typer.echo(f"     Multiplex: {item.multiplex_label}")
                typer.echo(f"     Harmonisierung: {item.harmonization_label}")
        
        if len(result.subgroups) > 3:
            typer.echo(f"\n   ... und {len(result.subgroups) - 3} weitere Gruppen")
    
    if create:
        typer.echo(f"\n📦 Erstelle Gruppen...")
        ensure_import_folders()
        
        created = export_to_morphic_groups(result, GENERATED_GROUPS_FOLDER)
        typer.echo(f"✅ {len(created)} Dateien erstellt in:")
        typer.echo(f"   {GENERATED_GROUPS_FOLDER / 'BAT_Akutprogramme'}")
        
        for f in created[:5]:
            typer.echo(f"   • {f.name}")
        if len(created) > 5:
            typer.echo(f"   ... und {len(created) - 5} weitere")
    else:
        typer.echo(f"\n💡 Zum Erstellen: --create oder -c hinzufügen")


@extended_app.command("pdf-debug")
def pdf_debug_cmd(
    pdf_path: str = typer.Argument(..., help="Pfad zur PDF-Datei"),
    pages: int = typer.Option(3, "--pages", "-p", help="Anzahl Seiten zum Anzeigen"),
    force_ocr: bool = typer.Option(False, "--ocr", help="OCR erzwingen")
) -> None:
    """Debug: Zeigt rohen Text aus PDF (mit/ohne OCR)."""
    try:
        import fitz
    except ImportError:
        typer.echo("❌ PyMuPDF nicht installiert")
        raise typer.Exit(code=1)
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        typer.echo(f"❌ Datei nicht gefunden: {pdf_path}")
        raise typer.Exit(code=1)
    
    doc = fitz.open(pdf_path)
    typer.echo(f"📄 PDF Debug: {pdf_path}")
    typer.echo(f"   Seiten: {len(doc)}")
    typer.echo("-" * 50)
    
    total_chars = 0
    for i, page in enumerate(doc):
        if i >= pages:
            break
        
        text = page.get_text().strip()
        total_chars += len(text)
        
        typer.echo(f"\n--- Seite {i+1} ({len(text)} Zeichen) ---")
        if len(text) > 0:
            preview = text[:500] + "..." if len(text) > 500 else text
            typer.echo(preview)
        else:
            typer.echo("[KEIN TEXT - wahrscheinlich Bild-PDF]")
    
    doc.close()
    
    typer.echo(f"\n{'='*50}")
    typer.echo(f"📊 Zusammenfassung:")
    typer.echo(f"   Zeichen in ersten {pages} Seiten: {total_chars}")
    avg = total_chars / pages if pages > 0 else 0
    typer.echo(f"   Durchschnitt pro Seite: {avg:.0f}")
    
    if avg < 100:
        typer.echo(f"\n⚠️ Wenig Text erkannt - wahrscheinlich Bild-PDF!")
        typer.echo("   Versuche: python -m apps.cli.main ext pdf-debug <pdf> --ocr")
        
        if force_ocr:
            typer.echo(f"\n🔍 OCR-Extraktion...")
            try:
                from core.pdf_advanced_import import extract_text_with_ocr, OCR_AVAILABLE
                if not OCR_AVAILABLE:
                    typer.echo("❌ OCR nicht verfügbar (pytesseract/Pillow fehlt)")
                else:
                    ocr_text = extract_text_with_ocr(pdf_path)
                    typer.echo(f"\n--- OCR-Text (erste 1000 Zeichen) ---")
                    typer.echo(ocr_text[:1000] if len(ocr_text) > 1000 else ocr_text)
                    typer.echo(f"\n📊 OCR extrahierte {len(ocr_text)} Zeichen")
            except Exception as e:
                typer.echo(f"❌ OCR-Fehler: {e}")


@extended_app.command("import-folder")
def import_folder_cmd() -> None:
    """Zeigt und erstellt Import-Ordner."""
    try:
        from core.pdf_advanced_import import ensure_import_folders
        folders = ensure_import_folders()
        
        typer.echo("📂 Import-Ordner erstellt/bestätigt:")
        for name, path in folders.items():
            typer.echo(f"   {name}: {path}")
        
        typer.echo(f"\n💡 PDFs für Import in '{folders['import']}' ablegen")
        typer.echo("   Dann: python -m apps.cli.main ext pdf-analyze <datei.pdf> --create-groups")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")


@extended_app.command("llm-status")
def llm_status_cmd() -> None:
    """Zeigt Status der LLM-Integration (Ollama)."""
    try:
        from core.llm_pdf_analyzer import get_llm_status
        status = get_llm_status()
        
        typer.echo("🤖 LLM-Status (Ollama)")
        typer.echo("-" * 40)
        typer.echo(f"Endpoint: {status['base_url']}")
        
        if status['available']:
            typer.echo(f"Status: ✅ Verfügbar")
            typer.echo(f"\n📦 Installierte Modelle:")
            for model in status.get('models', []):
                rec = " ⭐ (empfohlen)" if model == status.get('recommended') else ""
                typer.echo(f"   • {model}{rec}")
            
            if status.get('recommended'):
                typer.echo(f"\n💡 Standard-Modell: {status['recommended']}")
        else:
            typer.echo(f"Status: ❌ Nicht verfügbar")
            typer.echo(f"Fehler: {status.get('error', 'Unbekannt')}")
            typer.echo(f"\n📦 Installation:")
            typer.echo("   1. Ollama installieren: https://ollama.ai")
            typer.echo("   2. Modell laden: ollama pull llama3.2")
            typer.echo("   3. Ollama starten: ollama serve")
            
    except ImportError as e:
        typer.echo(f"❌ LLM-Modul nicht verfügbar: {e}")


@extended_app.command("llm-analyze")
def llm_analyze_cmd(
    pdf_path: str = typer.Argument(..., help="Pfad zur PDF-Datei"),
    model: str = typer.Option(None, "--model", "-m", help="Ollama-Modell"),
    create_groups: bool = typer.Option(False, "--create-groups", "-g", help="Gruppen erstellen"),
    create_nls: bool = typer.Option(False, "--create-nls", "-n", help="NLS-DB erstellen"),
    compare: bool = typer.Option(False, "--compare", "-c", help="Mit Regex-Analyse vergleichen")
) -> None:
    """Analysiert PDF mit lokaler LLM (Ollama) für höchste Genauigkeit."""
    try:
        from core.llm_pdf_analyzer import (
            llm_enhanced_pdf_import,
            compare_analysis_methods,
            check_ollama_available
        )
        from core.pdf_advanced_import import (
            ensure_import_folders,
            GENERATED_GROUPS_FOLDER,
            NLS_DATABASE_FOLDER
        )
    except ImportError as e:
        typer.echo(f"❌ Module nicht verfügbar: {e}")
        raise typer.Exit(code=1)
    
    # Prüfe Ollama
    ollama = check_ollama_available()
    if not ollama['available']:
        typer.echo(f"❌ Ollama nicht verfügbar: {ollama.get('error')}")
        typer.echo("\n📦 Installation:")
        typer.echo("   ollama pull llama3.2")
        typer.echo("   ollama serve")
        raise typer.Exit(code=1)
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        typer.echo(f"❌ Datei nicht gefunden: {pdf_path}")
        raise typer.Exit(code=1)
    
    model = model or ollama.get('recommended')
    typer.echo(f"🤖 LLM-Analyse mit {model}...")
    typer.echo(f"   Quelle: {pdf_path}")
    
    try:
        if compare:
            typer.echo(f"\n📊 Vergleiche Methoden...")
            comparison = compare_analysis_methods(pdf_path)
            
            typer.echo(f"\n{'='*50}")
            typer.echo("VERGLEICH: Regex vs. LLM")
            typer.echo(f"{'='*50}")
            
            for method, data in comparison['comparison'].items():
                typer.echo(f"\n{method.upper()}:")
                if 'error' in data:
                    typer.echo(f"   ❌ Fehler: {data['error']}")
                else:
                    typer.echo(f"   Gruppen: {data.get('groups', 0)}")
                    typer.echo(f"   Items:   {data.get('items', 0)}")
                    typer.echo(f"   Qualität: {data.get('quality', 0):.0%}")
                    if 'confidence' in data:
                        typer.echo(f"   Konfidenz: {data['confidence']:.0%}")
            
            typer.echo(f"\n💡 Empfehlung: {comparison.get('recommendation', '?').upper()}")
            typer.echo(f"   {comparison.get('reason', '')}")
            return
        
        # LLM-Analyse
        result = llm_enhanced_pdf_import(pdf_path, model=model)
        
        typer.echo(f"\n📊 LLM-Analyse-Ergebnis:")
        typer.echo(f"   Modell: {result['model_used']}")
        typer.echo(f"   Tokens: {result['tokens_used']}")
        typer.echo(f"   Qualität: {result['quality_score']:.0%}")
        typer.echo(f"   Konfidenz: {result['confidence']:.0%}")
        typer.echo(f"   Gruppen: {len(result['groups'])}")
        typer.echo(f"   Items: {result['total_items']}")
        
        if result['categories']:
            typer.echo(f"\n📋 Kategorien:")
            for cat, count in result['categories'].items():
                emoji = {
                    'pathogen': '🦠', 'toxin': '☠️', 'organ': '🫀',
                    'nutrient': '💊', 'remedy': '🌿', 'symptom': '🤒',
                    'frequency': '📡'
                }.get(cat, '❓')
                typer.echo(f"   {emoji} {cat}: {count}")
        
        if result['groups']:
            typer.echo(f"\n📦 Erkannte Gruppen:")
            for group in result['groups'][:10]:
                items_count = len(group.get('items', []))
                conf = group.get('confidence', 0)
                typer.echo(f"   • {group['name']} ({items_count} Items, {conf:.0%})")
        
        # Gruppen erstellen
        if create_groups and result['groups']:
            typer.echo(f"\n📦 Erstelle Gruppen...")
            ensure_import_folders()
            
            for group in result['groups']:
                if len(group.get('items', [])) >= 3:
                    safe_name = re.sub(r'[^a-z0-9_]', '_', group['name'].lower())
                    suffix = f"_{group.get('category', 'unknown')}_multiplex"
                    filename = f"{safe_name}{suffix}.json"
                    
                    group_path = GENERATED_GROUPS_FOLDER / filename
                    with open(group_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            'name': group['name'],
                            'category': group.get('category', 'unknown'),
                            'source': 'llm_import',
                            'model': result['model_used'],
                            'confidence': group.get('confidence', 0),
                            'items': group.get('items', [])
                        }, f, indent=2, ensure_ascii=False)
                    typer.echo(f"   ✅ {filename}")
        
        # NLS-DB erstellen
        if create_nls and result['total_items'] >= 5:
            typer.echo(f"\n🗄️ Erstelle NLS-Datenbank...")
            ensure_import_folders()
            
            db_name = f"llm_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            db_path = NLS_DATABASE_FOLDER / f"{db_name}.json"
            
            nls_data = {
                'database_name': db_name,
                'version': '1.0',
                'source': 'llm_import',
                'model': result['model_used'],
                'created_at': datetime.now().isoformat(),
                'quality_score': result['quality_score'],
                'groups': {g['name']: g for g in result['groups']},
                'items': []
            }
            
            item_id = 1
            for group in result['groups']:
                for item in group.get('items', []):
                    nls_data['items'].append({
                        'id': item_id,
                        'label': item.get('label', ''),
                        'group': group['name'],
                        'category': item.get('category', 'unknown'),
                        'value': item.get('value')
                    })
                    item_id += 1
            
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(nls_data, f, indent=2, ensure_ascii=False)
            typer.echo(f"   ✅ {db_path}")
        
        # Ergebnis speichern
        output_json = pdf_file.with_suffix('.llm_analysis.json')
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        typer.echo(f"\n✅ Analyse gespeichert: {output_json}")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


@extended_app.command("desc-status")
def desc_status_cmd() -> None:
    """Zeigt Status der Item-Beschreibungs-Datenbank."""
    try:
        from core.item_description_generator import get_database_stats
        stats = get_database_stats()
        
        typer.echo("📚 Item-Beschreibungen Status")
        typer.echo("-" * 40)
        typer.echo(f"Datenbank: {stats['database_path']}")
        typer.echo(f"Gesamt: {stats['total_descriptions']} Beschreibungen")
        typer.echo(f"Ø Konfidenz: {stats['average_confidence']:.0%}")
        
        if stats['by_category']:
            typer.echo(f"\n📋 Nach Kategorie:")
            for cat, count in stats['by_category'].items():
                typer.echo(f"   • {cat or 'unknown'}: {count}")
        
        if stats['by_source']:
            typer.echo(f"\n🔧 Nach Quelle:")
            for src, count in stats['by_source'].items():
                typer.echo(f"   • {src}: {count}")
                
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")


@extended_app.command("desc-generate")
def desc_generate_cmd(
    label: str = typer.Argument(..., help="Item-Label für Beschreibung"),
    category: str = typer.Option("default", "--category", "-c", help="Kategorie"),
    model: str = typer.Option(None, "--model", "-m", help="Ollama-Modell"),
    force: bool = typer.Option(False, "--force", "-f", help="Cache ignorieren")
) -> None:
    """Generiert Beschreibung für ein einzelnes Item."""
    try:
        from core.item_description_generator import generate_single_description
        
        typer.echo(f"🔬 Generiere Beschreibung für: {label}")
        typer.echo(f"   Kategorie: {category}")
        
        desc = generate_single_description(label, category, model, force)
        
        typer.echo(f"\n{'='*50}")
        typer.echo(f"📝 {desc.item_label}")
        typer.echo(f"{'='*50}")
        typer.echo(f"\n📌 Kurz: {desc.short_description}")
        typer.echo(f"\n📖 Detail:\n{desc.detailed_description}")
        typer.echo(f"\n💊 Therapie:\n{desc.therapeutic_hints}")
        
        if desc.related_items:
            typer.echo(f"\n🔗 Verwandt: {', '.join(desc.related_items)}")
        
        typer.echo(f"\n📊 Konfidenz: {desc.confidence:.0%} | Quelle: {desc.source}")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")
        raise typer.Exit(code=1)


@extended_app.command("desc-batch")
def desc_batch_cmd(
    json_file: str = typer.Argument(..., help="JSON-Datei mit Items"),
    model: str = typer.Option(None, "--model", "-m", help="Ollama-Modell"),
    limit: int = typer.Option(0, "--limit", "-l", help="Max. Anzahl Items (0=alle)")
) -> None:
    """Generiert Beschreibungen für Items aus JSON-Datei."""
    try:
        from core.item_description_generator import generate_batch_descriptions
        
        # JSON laden
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Items extrahieren
        items = []
        if isinstance(data, list):
            items = data
        elif 'top_items' in data:
            items = [{'label': i.get('label', ''), 'category': i.get('group', 'default')} 
                    for i in data['top_items']]
        elif 'items' in data:
            items = data['items']
        
        if limit > 0:
            items = items[:limit]
        
        typer.echo(f"📦 Batch-Generierung für {len(items)} Items")
        typer.echo("-" * 40)
        
        def progress(current, total, label):
            typer.echo(f"[{current}/{total}] {label[:40]}...")
        
        stats = generate_batch_descriptions(items, model, progress)
        
        typer.echo(f"\n{'='*50}")
        typer.echo("📊 Ergebnis:")
        typer.echo(f"   Gesamt: {stats['total']}")
        typer.echo(f"   Generiert: {stats['generated']}")
        typer.echo(f"   Aus Cache: {stats['cached']}")
        typer.echo(f"   Fehler: {stats['errors']}")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")
        raise typer.Exit(code=1)


@extended_app.command("desc-export")
def desc_export_cmd(
    output: str = typer.Option(None, "--output", "-o", help="Ausgabe-Pfad")
) -> None:
    """Exportiert alle Beschreibungen als JSON."""
    try:
        from core.item_description_generator import export_descriptions_to_json
        
        path = export_descriptions_to_json(output)
        typer.echo(f"✅ Exportiert: {path}")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}")


# Funktion zum Registrieren in der Haupt-App
def register_extended_commands(main_app: typer.Typer):
    """Registriert erweiterte Befehle in der Haupt-CLI."""
    main_app.add_typer(extended_app, name="ext")


# Standalone-Ausführung
if __name__ == "__main__":
    extended_app()
