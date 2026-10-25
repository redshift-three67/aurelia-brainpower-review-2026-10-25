# MORPHIC ENGINE V1 - ÄNDERUNGSPROTOKOLL

Dieses Dokument protokolliert alle Änderungen am Projekt, um Memory-Lücken zu vermeiden.

---

## Session 01.12.2025 (Nachmittag) - BRUCE COPEN V4 & FOKUS-RESONANZ

### Geänderte Dateien:
| Datei | Änderung | Status |
|-------|----------|--------|
| `core/profiles/profile.py` | **Bruce Copen V4 Ratenberechnung** - Positionsgewichtung + Zahlen | ✅ BACKUP 1540 |
| `core/profiles/profile.py` | `calculate_copen_rate()` - Vollständige Berechnung | ✅ |
| `core/profiles/profile.py` | `word_to_copen_rate()` - Schnelle Rate-Berechnung | ✅ |
| `core/profiles/profile.py` | `focus_to_copen_rates()` - Fokus-Begriffe → Raten | ✅ |
| `apps/cli/main.py` | Import der neuen Copen-Funktionen | ✅ BACKUP 1555 |
| `apps/cli/main.py` | `_compute_focus_multiplier_for_item()` erweitert | ✅ |
| `apps/cli/main.py` | Copen-Rate-Resonanz für Fokus-Gewichtung | ✅ |
| `apps/cli/main.py` | Neue Fokus-Keywords: sehen, hoeren, fuehlen, sinne | ✅ |
| `tools/synergy_consolidator.py` | Fix: Remedy-Synergien aus sub_results.top | ✅ |
| `apps/cli/main.py` | TOP-3 → TOP-N dynamische Überschriften | ✅ |
| `apps/cli/main.py` | `morphic_field` Standard: True (war False) | ✅ |
| `apps/cli/main.py` | `mf_use_hardware` Standard: True (Kozyrev) | ✅ |
| `docs/NLS_3D_ANATOMICAL_MODELS.md` | **NEU**: STL-Modell-Ressourcen für 3D NLS | ✅ |

### Punkt 3 - Erweiterte Klienten-Modifikatoren:
**Status**: Teilweise implementiert
- ✅ `age_factor` - Alters-basierte Modulation (bereits aktiv)
- ⚠️ `gender_factor`, `bmi_factor`, `stress_factor` - existieren in `client_profile.py`, aber benötigen erweiterte Eingabedaten
- 📋 **Empfehlung**: Optionales erweitertes Klienten-Formular für zukünftige Versionen

### Technische Details:

#### Bruce Copen V4 Algorithmus (KORRIGIERT):
```
1. Normalisierung: word → CLEANWORD (nur A-Z, 0-9)
2. Primärsumme: S = Σ(W(ch) × position) wobei A-Z=1-26, 0-9=0-9
3. Baserate: B = S × 1000
4. Fibonacci-Rate: F = ⌊(B/21)×34⌋ oder adaptiv
5. Potenz-Bonus: P = ⌊F×(k/Faktor)⌋
6. Finale Rate: R = F + P
```

#### Fokus-Resonanz (NEU):
- Fokus-Begriffe werden in Copen-Raten umgewandelt
- Items mit ähnlicher Copen-Rate erhalten Resonanz-Bonus
- Maximaler Bonus: +15% (8% Keyword + 7% Copen-Resonanz)
- Beispiel: "Sehen" → 231,523 Copen-Rate

#### Remedy-Synergien Fix:
- Problem: `nls_scores` hatte keine `rates`
- Lösung: Verwende `sub_results.top` als Quelle
- Ergebnis: 46 Remedy-Synergien gefunden

---

## Session 01.12.2025 (Morgen)

### Geänderte Dateien:
| Datei | Änderung | Status |
|-------|----------|--------|
| `tools/pdf_exporter.py` | Subprocess statt pdfkit für PDF-Export | ✅ |
| `apps/cli/main.py` | scan_type Parameter für Ordner-Label | ✅ BACKUP 0920 |
| `apps/cli/main.py` | FOCUS_PROFILE_MAP erweitert (+44 Keywords) | ✅ BACKUP 0920 |
| `apps/cli/main.py` | Fokus-Gewichtung erhöht (25%/15%/10%) | ✅ BACKUP 0920 |
| `apps/cli/main.py` | Top-N statt Top-3 (Standard: 5) | ✅ BACKUP 0920 |
| `tools/interpretation_generator.py` | Scan-Typ Label für Ordner | ✅ |
| `tools/trend_analyzer.py` | Scan-Typ Label für Ordner | ✅ |
| `tools/search_client_data.py` | NEU: Volltextsuche Tool | ✅ |
| `Run-MultiplexScan.ps1` | Top-5 mit --top-n 5, Threshold 6.0 | ✅ |
| `config/hardware_profiles.py` | NEU: Adaptive Hardware-Konfiguration | ✅ |
| `config/hardware_profiles.py` | Dynamisches Profil für fremde PCs | ✅ |
| `GROVER_LLM_SYNERGY_EMPFEHLUNGEN.md` | NEU: Konzeptdokument | ✅ |
| `tools/synergy_consolidator.py` | NEU: Synergy-Gesamtbericht | ✅ |
| `Run-MultiplexScan.ps1` | Synergy-Consolidator Integration | ✅ BACKUP 1031 |

### Offene Probleme:
1. **Druckerdialog** - Erscheint weiterhin bei PDF-Export
2. **Fokus-Gewichtung** - Wird bei Top-3 nicht korrekt angewendet
3. **Profile mit Fehlern** - niere_detailliert, allergie_detailliert, psyche_detailliert, chakren_meridiane, miasma_detailliert

### Technische Details:
- `scan_type` Parameter: "einzelprofil" oder "top3"
- Ordnerstruktur: `YYYYMMDD_HHMMSS_scantype`
- PDF-Export: Direkter subprocess-Aufruf von wkhtmltopdf

---

## Session 01.12.2025 (Nacht)

### Abgeschlossene Aufgaben:
1. Harmonisierung nach Top-3 Scan (Run-MultiplexScan.ps1)
2. Bruce Copen Raten bei Synergy
3. Quantum Synergy Threshold 7.0 → 6.0
4. Ordnerstruktur mit Unterordnern
5. Print-Stylesheets für alle Berichte
6. Einheitliche Schriftgrößen

---

## Backup-Regel (KRITISCH!)

**VOR JEDER ÄNDERUNG:**
```cmd
copy "pfad\zur\datei.py" "pfad\zur\datei.py.bak_YYYYMMDD_HHMM"
```

**WARTEN auf Nutzer-Bestätigung vor Implementierung!**

---

## Datenbank-Gruppen Status

### Funktionierende Profile (31/35):
- pathogen, toxin, immune, detox, regulation
- verdauung_detailliert, leber_detailliert, nervensystem_detailliert
- herz_kreislauf_fein, atmung_lunge_detailliert, endokrin_detailliert
- haut_detailliert, lymphsystem_detailliert, immunsystem_detailliert
- gehirn_detailliert, knochen_detailliert, wirbelsaeule_detailliert
- zahn_detailliert, tote_zaehne_detailliert, schmerz_detailliert
- schwindel_detailliert, schwermetalle, strahlung_detailliert
- stoerfelder_toxisch, vergiftung_komplett, pestizide_herbizide
- medikamenten_toxizitaet, nahrungsmittel_intoleranzen
- mitochondrien_dysfunktion, bindegewebe_faszien

### Profile mit Fehlern (5/35):
- niere_detailliert
- allergie_detailliert
- psyche_detailliert
- chakren_meridiane
- miasma_detailliert

---

## Fokus-Gewichtung (Top-3)

### Aktuelles Problem:
Fokus "Bandscheiben" führt NICHT zu wirbelsaeule_detailliert oder knochen_detailliert.

### Ursache:
Die Fokus-Bonus-Berechnung in `_compute_focus_profile_bonus()` erkennt "Bandscheiben" nicht als relevant für diese Profile.

### Lösung:
Keyword-Mapping erweitern oder Top-5 statt Top-3.

---

## Remedy-Gruppen

### Integriert:
- Heel
- Nutramedix
- Schüssler
- OOREP (OpenRep) - 2432 Mittel, 10111 Keywords

### Namenskonvention:
`*_remedies_multiplex` oder `*_multiplex` für automatische Erkennung.
