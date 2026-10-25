# Mustermann Report Comparison 2026-06-29

Referenz:

```text
D:\Testpatienten Berichte\Mustermann\
```

Aktuelle Vergleichslaeufe:

```text
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Test_20260629_Intensity\
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Top9_20260629\
```

Aktuellster reparierter Deutungsbericht im TOP9-Vergleichslauf:

```text
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Top9_20260629\Mustermann_Klaus_09041966_Augsburg_Deutung\20260629_105923_top9\
```

Aktuellste reparierte konsolidierte TOP9-Berichte:

```text
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Top9_20260629\Mustermann_Klaus_09041966_Augsburg_Synergy\20260629_111057_synergy_report\
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Top9_20260629\Mustermann_Klaus_09041966_Augsburg_Remedies\20260629_111427_top9_remedies.html
```

## Originalstruktur

Die Mustermann-Referenz ist als mehrteiliger Berichtssatz aufgebaut:

| Bereich | Befund |
|---|---|
| Resonanz | `Mustermann_Klaus_09041966_Augsburg_Resonanz\20251222_210515_TOP9_SESSION\01_...` bis `09_...`; je Profil HTML, JSON, TXT, Hoch-/Mittel-Labels und Copen-Datei; ein Profil zusaetzlich PDF. |
| Deutung | eigener Ordner `..._Deutung\...\deutung_*.html/.pdf`. |
| Remedies | einzelne profilbezogene Remedy-HTMLs plus `*_top9_remedies.html`. |
| Synergy | eigener Synergy-Ordner mit `synergy_gesamt.html/.json` plus Legacy-Datei ohne Endung. |
| Trends | `Hinweis.txt`. |

Dateitypen in der Referenz: 22 HTML, 10 JSON, 2 PDF, 28 TXT/sonstige Textdateien plus eine Legacy-Datei ohne Endung.

## Aktuelle Struktur

Der aktuelle TOP9-Lauf schreibt wieder dieselben Hauptbereiche:

| Bereich | Befund |
|---|---|
| Resonanz | TOP9-Session mit neun Profil-Unterordnern und je Profil HTML, JSON, PDF, TXT, Labels und Copen-Datei. |
| Deutung | eigener Deutungsordner mit HTML/PDF. |
| Remedies | profilbezogene Remedy-HTML/JSON/PDF plus `*_top9_remedies.*`. |
| Synergy | eigener Synergy-Ordner mit HTML/JSON/PDF. |
| Trends | `Hinweis.txt`. |

Dateitypen im aktuellen Vergleichslauf: 21 HTML, 20 JSON, 21 PDF, 28 TXT.

## Direkt verbesserter Punkt

Die Resonanz-HTMLs enthalten jetzt wieder die im Original sichtbaren
Subgruppen-Tabellenspalten:

- `Intensität (global/gruppe)`
- numerische Prioritaet 1-10 relativ zum Gruppenmaximum
- Interpretationshinweis zu Score, Intensitaet und Prioritaet pro Gruppe

Der aktualisierte Renderer ist ueber `tests/test_report_renderer_legacy_layout.py`
abgesichert.

Der Top-N-Deutungsbericht liest jetzt ebenfalls den aktuellen Export-Root als
Archive-Root. Dadurch enthaelt er wieder echte Scanbefunde statt des
Fallback-Hinweises `Keine priorisierten Resonanzwerte im Quellmaterial gefunden.`
Zusätzlich werden sichtbare mojibake-Artefakte in den gemeinsamen Report-Tools
zentral normalisiert, z.B. `Schwermetall-LeberschÃ¤den` zu
`Schwermetall-Leberschäden`.

Der Synergy-Gesamtbericht enthaelt jetzt wieder Legacy-nahe Detailabschnitte:

- `Analysierte Profile`
- `Cross-Profile Synergien`
- profilweise `Quantum-Synergy Analyse`
- `Top Quantum-Synergien`
- Score-Komponenten wie `Resonanz-Verstärkung`, Harmonie und Relevanz

Der konsolidierte Remedy-Bericht enthaelt jetzt wieder eine aggregierte
therapeutische Tabelle mit `Remedy`, `Score`, `Raten`, `Synergien` und
`Synergie-Score`. Die bisherige Paarliste bleibt darunter als Detailtabelle
erhalten und fuehrt jetzt auch das jeweilige Profil mit.

## Messbarer Stand

| Kennzahl | Original | Aktueller TOP9-Schnelllauf |
|---|---:|---:|
| Resonanz-HTMLs | 9 | 9 |
| Durchschnittliche Resonanz-HTML-Groesse | ca. 86 KB | ca. 61 KB |
| Kleinste/groesste Resonanz-HTML | ca. 50-113 KB | ca. 54-87 KB |
| TOP9-Archivstruktur | vorhanden | vorhanden |
| Deutung/Remedy/Synergy/Trend-Bereiche | vorhanden | vorhanden |
| Synergy-Gesamtbericht | 92.876 B | 72.323 B |
| TOP9-Remedy-Bericht | 9.553 B | 38.551 B |

Hinweis: Der aktuelle Vergleichslauf wurde bewusst mit `--k-total 128 --top-k 50 --no-synergy`
erzeugt, damit er schnell und reproduzierbar als Strukturprobe dient. Die historischen
Originale enthalten deutlich groessere JSON-Datenmengen und wurden offenbar mit
hoeherer Kandidaten-/Top-K-Konfiguration erzeugt.

## Offene Differenzen

1. Datenfuelle:
   Die Original-JSONs der Resonanzprofile liegen grob bei 1.3-1.8 MB; der aktuelle
   Schnellvergleich liegt bei rund 97-102 KB pro Profil. Fuer einen fairen
   Datenfuellevergleich braucht es einen Voll-Lauf mit hoeherem `--k-total` und
   `--top-k`.

2. Profilauswahl:
   Die aktuelle Top9-Auswahl ist fokus- und scorebasiert und kann von der
   historischen Top9-Auswahl abweichen. Die Originale enthielten u.a.
   `tote_zaehne_detailliert`, `zahn_detailliert`, `b10_mikrozirkulation`,
   `wirbelsaeule_detailliert` und `knochen_detailliert`; der aktuelle Lauf
   priorisierte andere Profile.

3. Konsolidierte Berichte:
   Deutung, Remedies und Synergy werden erzeugt und sind strukturell naeher an
   der Referenz. Noch offen ist ein finaler visueller Detailvergleich gegen die
   historischen HTMLs sowie die Frage, ob die Legacy-Datei ohne Endung weiterhin
   benoetigt wird.

4. CLI-Ausgaben:
   Die Top-N-Zusammenfassung nennt jetzt den echten Exportpfad. Einige tiefere
   Synergy-Unterausgaben koennen weiterhin Unicode-Symbole enthalten; diese
   betreffen derzeit die Konsole. HTML-Reports und Deutung werden auf sichtbare
   mojibake-Artefakte normalisiert.

## Naechste empfohlene Schritte

1. Volleren TOP9-Vergleichslauf erzeugen, z.B. `--top-n 9 --k-total 1024 --top-k 192`
   und danach HTML-/JSON-Groessen, Gruppenanzahl und Top-Item-Anzahl vergleichen.
2. Deutungsbericht visuell gegen `deutung_20251222_210733.html` abgleichen.
3. `*_top9_remedies.html` und `synergy_gesamt.html` im Browser gegen die
   Originale pruefen und nur noch konkrete Detailabweichungen nachziehen.
4. Optional: einen fixierten Profil-Run fuer die historischen neun Profilnamen
   ergaenzen, damit Layout und Datenfuelle unabhaengig von der aktuellen
   Profilrecommender-Auswahl verglichen werden koennen.
