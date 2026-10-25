# Morphic Engine V1 - Projekt-Status und Vereinbarungen

**WICHTIG: Diese Datei muss bei JEDER Session gelesen werden!**
**Cascade muss diese Datei bei jeder wichtigen Änderung aktualisieren!**

---

## Letzte Aktualisierung
- **Datum:** 30.11.2025 12:30
- **Session:** Produktions-Start mit neuen Ordnern und Deutungs-System

---

## Aktive Arbeitsregeln (IMMER BEFOLGEN!)

### 1. Backup vor jeder Änderung
```cmd
copy "pfad\zur\datei.py" "pfad\zur\datei.py.bak_DATUM"
```
**WARTEN auf Bestätigung des Nutzers!**

### 2. Keine Änderung bestehender Funktionalitäten ohne Absprache
- Bestehende Features dürfen NICHT geändert werden
- Neue Features müssen ZUSÄTZLICH implementiert werden
- Bei Konflikten: IMMER zuerst mit Nutzer besprechen

### 3. Produktions-Pfade (NEU ab 30.11.2025)
- `C:\Benutzer_Archive_Start` - Scan-Berichte (PRODUKTIV)
- `C:\Benutzer_Trends_Start` - Trendanalysen (PRODUKTIV)
- `C:\Benutzer_Deutung_Start` - Deutungs-Berichte (PRODUKTIV)
- `C:\Benutzer_Archive` - Alte Testdaten (ARCHIV)
- `C:\Benutzer_Trends` - Alte Testdaten (ARCHIV)

---

## Offene Aufgaben

### OOREP Integration (ABGESCHLOSSEN ✅)
- [x] Eigenes Profil `homeopathy_classical` erstellt
- [x] Keywords generiert (10111 Keywords für 2432 Mittel)
- [x] In PowerShell-Profilliste eingefügt
- [x] In `remedy_group_registry.py` registriert
- [x] OOREP zu ALLEN Profilen hinzugefügt (wie Heel/Nutramedix) ✅ 30.11.2025
- [x] Als Subgruppe im HTML-Bericht anzeigen ✅ 30.11.2025

**Vereinbarung:** OOREP funktioniert GENAU WIE Heel, Nutramedix, Schüssler - in ALLEN Profilen für Synergie-Analyse verfügbar!

### Berichtsarchiv mit Trendanalyse (PRODUKTIV ✅)
- [x] `tools/trend_analyzer.py` erstellt
- [x] CLI-Befehl `client-trends` hinzugefügt
- [x] Speicherpfad: `C:\Benutzer_Trends_Start\` ✅ 30.11.2025
- [x] SQLite-Datenbank (`C:\Benutzer_Trends_Start\trends.db`) ✅ 30.11.2025
- [x] Trigger-System (kritischer Anstieg, Verbesserung, persistent, neu) ✅ 30.11.2025
- [x] Archivierungs-Startpunkt: 30.11.2025 (HEUTE) ✅
- [x] Gruppen-Funktionen (Familie, Wohnraum) ✅ 30.11.2025
- [x] Integration in PowerShell nach Top-3 Scan ✅ 30.11.2025
- [ ] Automatisierte Nachtestungen (Windows Task Scheduler)
- [ ] PDF-Ausgabe

### Deutungs-System (NEU ✅)
- [x] `tools/interpretation_generator.py` erstellt ✅ 30.11.2025
- [x] Speicherpfad: `C:\Benutzer_Deutung_Start\` ✅ 30.11.2025
- [x] Automatische Generierung nach Top-3 Scan ✅ 30.11.2025
- [x] Fokus-bezogene Analyse ✅ 30.11.2025
- [x] Kategorisierung (Pathogene, Organe, Nährstoffe, Emotionen, Remedies) ✅ 30.11.2025
- [x] Muster-Erkennung und Empfehlungen ✅ 30.11.2025

### Zentrale Remedy-Registry
- [x] `core/remedy_group_registry.py` erstellt
- [x] `main.py` verwendet jetzt zentrale Registry
- [ ] Dokumentation vervollständigen

---

## Abgeschlossene Features

### Harmonisierung (29.11.2025)
- Hardware-Harmonisierung funktioniert
- Job-ID Regex korrigiert: `harm_[a-f0-9]+`
- Klassisch + Hardware parallel (Option 3) - Pfad-Problem identifiziert

### Remedy-Gruppen allgemein
- Heel, Nutramedix, Schüssler sind in allen Profilen manuell eingefügt
- Neue Gruppen müssen ebenfalls manuell zu allen Profilen hinzugefügt werden
- **GEPLANT:** Automatische Hinzufügung aller Remedy-Gruppen zu allen Profilen

---

## Technische Architektur

### Remedy-Gruppen Erkennung
- Zentrale Datei: `core/remedy_group_registry.py`
- Funktionen: `is_remedy_group()`, `list_all_remedy_groups()`
- Alle Remedy-Gruppen hier registrieren!

### Profil-System
- Datei: `apps/cli/profiles/registry.py`
- Fallback in: `apps/cli/main.py` (Funktion mit elif-Kette)
- **PROBLEM:** Remedy-Gruppen müssen manuell zu jedem Profil hinzugefügt werden

### Datenbank
- `data/remedies.db` - SQLite mit Remedy-Daten
- Spalten: `name`, `category`, `indication`, `source`
- OOREP: 2432 Einträge mit `category = 'oorep_homeopathy_multiplex'`

---

## Bekannte Probleme

1. **Encoding in PowerShell:** UTF-8 Zeichen werden falsch angezeigt (z.B. `Ô£à` statt ✅)
2. **Profil-Remedy-Gruppen:** Müssen manuell zu jedem Profil hinzugefügt werden
3. **Memory-Verlust:** Lange Konversationen verlieren Kontext

---

## Kontakt-Punkte für Änderungen

| Bereich | Datei(en) |
|---------|-----------|
| Remedy-Erkennung | `core/remedy_group_registry.py` |
| Profile | `apps/cli/profiles/registry.py`, `apps/cli/main.py` |
| PowerShell | `Run-MultiplexScan.ps1` |
| HTML-Berichte | `apps/cli/main.py` (group_order) |
| Datenbank | `data/remedies.db` |
| Dynamische Gruppen | `core/subgroups/procedural_groups.py` |

---

## Session-Log

### 30.11.2025 (Mittag) - Top-3 Scan Erweiterung & Neue Profile
- **Fokus-basierte Profil-Priorisierung** implementiert:
  - `FOCUS_PROFILE_MAP` mit 70+ Fokus-Keywords → Profile Mappings
  - `_compute_focus_profile_bonus()` Funktion (15%/10%/8% Bonus)
  - Signifikanz-Prüfung: Nicht-fokus-Profile mit >25% höherer Resonanz werden trotzdem berücksichtigt
- **35 Profile** für Top-3 Screening (erweitert von 20)
- **Fokus-Multiplikator für Items** erhöht von +5% auf +8%
- **6 Neue Profile** in `apps/cli/profiles/registry.py`:
  1. `vergiftung_komplett` - Schwermetalle, Chemikalien, Strahlung, Entgiftung
  2. `pestizide_herbizide` - Pestizide, Herbizide, Glyphosat
  3. `medikamenten_toxizitaet` - Nebenwirkungen, Interaktionen
  4. `nahrungsmittel_intoleranzen` - Histamin, Gluten, Laktose
  5. `mitochondrien_dysfunktion` - Chronische Erschöpfung, ATP
  6. `bindegewebe_faszien` - Faszien, Kollagen, Matrix
- **PowerShell erweitert**:
  - Single-Scan: Automatische Trendanalyse nach jedem Scan
  - Single-Scan: Optionale Deutungsanalyse (J/N Abfrage)
  - Top-3 Scan: Automatische Deutung + Trendanalyse
- **Deutungs-System** erweitert (`tools/interpretation_generator.py`):
  - Deduplizierung von Items (keine doppelten Einträge mehr)
  - **LLM-Integration** (Ollama) für KI-gestützte Tiefenanalyse
  - Neuer Parameter `--llm` für lokale KI-Deutung
  - PowerShell: Option "L" für KI-Tiefenanalyse bei Deutung
- **Produktions-Pfade** aktiviert: `C:\Benutzer_Archive_Start`, `C:\Benutzer_Trends_Start`, `C:\Benutzer_Deutung_Start`

### 30.11.2025 (Nacht) - Design & Ordnerstruktur
- **NEUE ORDNERSTRUKTUR**: Jede Analyse in eigenem Unterordner
  - Format: `Klient_Ordner/YYYYMMDD_HHMMSS/datei.html`
  - Gilt für: Archiv, Deutung, Trend
- **Einheitliches Design** für alle Berichte:
  - Gleiche Schriftart: 'Segoe UI', Roboto, Arial
  - Gleiche Schriftgrößen: h1=18pt, h2=14pt, body=11pt, table=10pt
  - Gleiche Farbpalette: #3d5a73, #4a6278, #5a7a9a
  - Print-Stylesheets für PDF-Export
- **Deutung Header-Fix**: Weiße Schrift auf dunklem Hintergrund
- **Trend-Pfeile**: ▲ (steigend), ▼ (fallend), ● (stabil)
- **PDF-Exporter**: Rekursive Suche in Unterordnern

### 30.11.2025 (Abend) - Verbesserungen & PDF-Export
- **LLM-Timeout** erhöht von 30s auf 90s für längere Deutungs-Analysen
- **Trendanalyse-Deduplizierung**: Items werden nur einmal pro Scan gezählt (höchster Score)
- **Deutungs-Scan-Zuordnung**: Single-Scan=1, Top-3=3 Scans für Deutung
- **PDF-Export** implementiert (`tools/pdf_exporter.py`):
  - Konvertiert alle HTML-Berichte zu PDF (Scan, Deutung, Trend)
  - pdfkit + wkhtmltopdf basiert
  - PowerShell-Integration: J=neueste, A=alle Berichte
  - Automatische Klienten-Ordner-Erkennung

### 30.11.2025 (Vormittag)
- Trendanalyse erweitert:
  - Speicherpfad geändert zu `C:\Benutzer_Trends_Start\`
  - SQLite-Datenbank für Trend-Daten implementiert
  - Trigger-System (kritischer Anstieg +50%, Verbesserung -30%, persistent 5+ Scans, neue Items)
  - Gruppen-Funktionen (Familie, Wohnraum) implementiert
  - Archivierungs-Startpunkt: 30.11.2025 definiert
- OOREP als Subgruppe im HTML-Bericht bestätigt (funktioniert!)

### 30.11.2025 (Nacht)
- Memory-Strategie entwickelt
- PROJECT_STATE.md erstellt
- OOREP zu ALLEN Profilen hinzugefügt (wie Heel/Nutramedix)

### 29.11.2025
- OOREP importiert und registriert
- Keywords generiert
- Zentrale Remedy-Registry erstellt
- Trendanalyse implementiert
- Harmonisierung Job-ID Fix

---

**ANWEISUNG AN CASCADE:**
1. Diese Datei bei Session-Start IMMER lesen
2. Bei wichtigen Änderungen diese Datei aktualisieren
3. Offene Aufgaben hier tracken
4. Vereinbarungen hier dokumentieren
