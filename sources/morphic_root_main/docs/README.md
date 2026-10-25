# Radialgo Resonanzanalyse (CLI)

Dieses Projekt führt eine Resonanzanalyse über morphogenetische Felder mit anschließender Harmonisierung durch und schlägt homöopathische Mittel über Raten-Resonanz vor.

## Voraussetzungen
- Windows
- Python 3.13 (oder kompatibel) – empfohlen: Aufruf über den Windows-Launcher `py`
- Abhängigkeiten: siehe `requirements.txt`

## Installation

### PowerShell (empfohlen)
```powershell
# (Optional) UTF-8 für korrekte Umlaute
$env:PYTHONUTF8=1

# Abhängigkeiten installieren
py -3.13 -m pip install -r requirements.txt
```

### Eingabeaufforderung (cmd.exe)
```cmd
REM (Optional) UTF-8 Codepage aktivieren
chcp 65001
set PYTHONUTF8=1

REM Abhängigkeiten installieren
py -3.13 -m pip install -r requirements.txt
```

Hinweis: Falls `python` auf dem System zum Microsoft Store umleitet, bitte stattdessen `py` verwenden oder unter
„Einstellungen → Apps → App-Ausführungsaliase“ die Aliase `python.exe`/`python3.exe` deaktivieren.

## Beispiel-Analyse (ohne Bild)

### PowerShell
```powershell
py -3.13 .\resonance_pipeline.py --name Mustermann --first-name Max --birth-date 09031999 --birth-place München
```

Falls Umlaute Probleme machen:
```powershell
py -3.13 .\resonance_pipeline.py --name Mustermann --first-name Max --birth-date 09031999 --birth-place Muenchen
```

### Eingabeaufforderung (cmd.exe)
```cmd
py -3.13 resonance_pipeline.py --name Mustermann --first-name Max --birth-date 09031999 --birth-place Muenchen
```

## Fehlerbehebung
- Python-Versionen prüfen:
  ```powershell
  py --list
  py -3.13 --version
  ```
- Wenn `python` nicht funktioniert: `py` verwenden.
- Bei Umlautproblemen: `PYTHONUTF8` setzen oder `Muenchen` statt `München` verwenden.

## Ausgabe
- Die CLI zeigt:
  - kombinierte Raten
  - morphische Feldstärke
  - holographische Entropie
  - Heimsche Signatur (4-Segment Surrogat)
  - Resonanzscores für Körpersysteme
  - Top 3 klassische homöopathische Mittel nach Resonanz
```

## Gruppen (neu) – DB‑lose Vollabdeckung

- tcm_full: prozedurale Vollenumeration aller TCM‑Punkte (LU/LI/ST/SP/HT/SI/BL/KI/PC/TE/GB/LV sowie Ren/Du). Raten deterministisch aus Code (Seed) und pro‑Meridian‑Basisoffsets.
- chakren_full: 7 Hauptchakren (aus 7p‑3 Frequenzen abgeleitet) + erweiterte (Thymus/Hara/Hand L/R/Fuß L/R/Milz/Nabel) mit harmonischen Offsets.

Beispiel:
```cmd
py -3.13 resonance_pipeline.py --name Mustermann --first-name Max --birth-date 09031999 --birth-place Muenchen ^
  --quantum-query multiplex --scan-groups "tcm_full,chakren_full" --top-subk 16 --nls-auto --grouped-output --dv --use-phrases
```

## Ablaufdiagramm: Multiplex‑Pipeline (inkl. HID‑Einfluss)

```mermaid
flowchart TD
  A[Profil → Raten] --> B[Resonator (h_level beeinflusst α,β,Γ)]
  HID[HID/Hardware] --> H[h_level]
  H --> B
  A --> C[Kandidaten (prozedural, Basisoffset)]
  B --> D[Scores s[i] = resonance(client, cand)]
  D --> E[Hadamard y = H @ s + noise(h_level)]
  E --> F[Decode s_hat = (Hᵀ @ y)/N]
  F --> G[Sort + Dedup]
  G --> H2[Subgruppen-Top]
  H2 --> I[Gruppen‑Aggregat (+ Phrasen)]
  I --> J[Harmonisierung: inverse + adaptive + holographisch]
```

## Ablaufdiagramm: NLS‑ähnliche Pipeline (inkl. HID‑Einfluss)

```mermaid
flowchart TD
  A[Profil → Raten] --> B[Entropie kalibrieren]
  SRC[NLS‑Items (DB oder auto)] --> C[Iteriere Items]
  C --> D[s_res = resonance(client, rates)]
  B --> E[z = (ent_cal − mean)/std]
  E --> F[s_ent = exp(−0.5·z^2)]
  D --> G[score = weight*(w_res*s_res + w_ent*s_ent)]
  F --> G
  CLI[CLI: w_res, w_ent, z_scale] --> G
  G --> H[Sort + Dedup]
  H --> I[Gruppen‑Aggregat (+ Phrasen)]
  I --> J[Harmonisierung]
  HID[HID/Hardware] --> R[h_level → Γ] --> D
```

### Hinweise
- HID erhöht typischerweise Stabilität (geringeres Multiplex‑Rauschen) und Q‑Faktoren in der Resonanzfunktion.
- `--nls-weight-res/--nls-weight-ent/--nls-std-scale` erlauben Tuning der NLS‑Scores.
- Für große Gruppen (z. B. `tcm_full`) skaliert die Multiplex‑Größe N auf nächste 2er‑Potenz (z. B. K≈361 → N=512).
