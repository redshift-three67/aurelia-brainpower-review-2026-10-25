# Berichte-, Profilscan- und Klientenvektor-Diskrepanzanalyse

Stand: 2026-06-28  
Projekt: Morphic Engine V1  
Referenz: `D:\Testpatienten Berichte\Mustermann\Mustermann_Klaus_09041966_Augsburg_*`  
Aktueller Vergleichsexport: `C:\Benutzer_Archive_Start\Deisenhofer_Klaus_09041966_Augsburg*`

## Kurzfazit

### Umsetzungsnachtrag 2026-06-28

| Punkt | Status |
|---|---|
| P0.1/P0.2 Sessionreine Konsolidierung | Umgesetzt: `top3-scan` nutzt fuer Synergy/Remedies nur noch JSON-Dateien der aktuellen Session. |
| P0.3 Sessionbezogene Remedy-Profilberichte | Umgesetzt: Top-N-Remedy-Profilberichte erhalten die Session-ID im Dateinamen. |
| P1.1 Deutung automatisch nach Top-N | Umgesetzt: `top3-scan` startet `tools.interpretation_generator` nach erfolgreicher Sessionanalyse im gleichen Exportroot. |
| P1.2 Trends automatisch nach Top-N | Umgesetzt: `top3-scan` startet `tools.trend_analyzer` im gleichen Exportroot. Der Trendbericht schreibt bei nur einer echten Session einen Hinweis statt Scheindeltas zwischen Profilen. |

| Bereich | Befund | Priorität |
|---|---|---:|
| Report-Konsolidierung | Aktuelle Top-N-Berichte werden nach dem Lauf nicht nur aus der aktuellen Session, sondern auch aus historischen Scan-JSONs im Archiv aufgebaut. Dadurch können Remedies und Synergy Werte/Quellen enthalten, die nicht zur aktuellen Top-N-Analyse gehören. | P0 |
| Deutung | In der aktuellen Top-N-Kette wird kein Deutungsbericht erzeugt. Die Mustermann-Referenz enthält einen eigenständigen Deutungsbereich mit HTML und PDF. | P1 |
| Trends | In der aktuellen Top-N-Kette wird kein Trends-Ordner erzeugt. Die Mustermann-Referenz enthält mindestens einen Trends-Hinweis; das neue Trend-Tool existiert, ist aber nicht automatisch eingebunden. | P1 |
| Remedies | Die aktuelle Remedies-Ausgabe enthält historische und aktuelle Profile gemischt. Außerdem werden per-profile Remedy-Dateien im Root des Remedies-Ordners abgelegt und können sessionübergreifend stehen bleiben. | P0 |
| Synergy | Die aktuelle Synergy-Ausgabe liegt sessionbezogen im Zielordner, kann aber durch die breite Quell-Dateisuche ebenfalls mit historischen Scan-JSONs gespeist werden. | P0 |
| Resonanz | Die Resonanzberichte enthalten den Kerninhalt, unterscheiden sich aber in Strukturdetails: Wellbeing-Block neu, teils rohe Gruppenlabels, keine durchgängigen Profil-PDFs, andere Tabellenstruktur und keine vollständige Original-Parität. | P1 |
| Profilscan | Aktuell werden 35 aktive Hauptprofile gescreent. Diese 35 sind nicht aus dem Klientenvektor vorselektiert, sondern entsprechen dem aktuellen `core.profile_sync`-Profiluniversum. | P1 |
| Klienten-/Bildvektor | Im Core existieren Ansätze für `image_signature`, in CLI/Web/Reports ist ein optionales Patientenbild oder Fokusbild aber noch nicht produktreif verdrahtet. | P2 |

## Originalstruktur Mustermann

| Originalbereich | Dateien/Struktur | Inhaltliche Merkmale |
|---|---|---|
| `..._Resonanz` | 46 Dateien, darunter eine `20251222_210515_TOP9_SESSION` mit 9 Profilordnern | Pro Profil HTML, JSON und Textdateien; ein Profil enthält zusätzlich PDF. |
| `..._Deutung` | 2 Dateien: `deutung_20251222_210733.html`, PDF | Eigenständige Deutung mit Zusammenfassung, Schlüsselbefunden, Mustern, Empfehlungen und KI-Tiefenanalyse. |
| `..._Remedies` | 11 HTML-Dateien | 9 per-profile Remedy-Berichte plus Top-9-Gesamtbericht und Kombinationenbericht. Dateinamen sind timestampbezogen. |
| `..._Synergy` | 3 Dateien | Timestampbezogener Synergy-Gesamtbereich mit HTML/JSON. |
| `..._Trends` | 1 Hinweisdatei | Trendbereich ist strukturell vorhanden, auch wenn in der Referenz nur ein Hinweis liegt. |

## Aktueller Vergleichsexport

| Aktueller Bereich | Beobachtung | Diskrepanz zur Referenz |
|---|---|---|
| Resonanz | Aktuelle Session `20260628_224628_TOP7_SESSION` mit 7 Profilen. | Top-N ist korrekt variabel, aber aktuell nur aus 35 Profilen gewählt. Original hatte Top-9 und andere Profilkandidaten. |
| Deutung | `..._Deutung` fehlt für den aktuellen Lauf. | Referenz hat eigenständigen Deutungsbericht mit HTML/PDF. |
| Remedies | `..._Remedies` enthält 54 Dateien und auch Profile, die nicht Teil der aktuellen TOP7-Session sind. | Referenz ist sessionbezogen und deutlich sauberer abgegrenzt. |
| Synergy | `..._Synergy\20260628_224628_synergy_report` enthält `synergy_gesamt.html/json`. | Ordner ist sessionbezogen, aber Quell-Dateisuche kann historische JSONs einbeziehen. |
| Trends | `..._Trends` fehlt für den aktuellen Lauf. | Referenz hat Trends-Struktur. |
| Patientenbild/Fokusbild | Aktuelle JSONs zeigen `image.present=false`, `source=default`, `quality=""`. | Kein produktiver Bildvektorfluss vorhanden. |

## Berichtsdiskrepanzen im Detail

| Bericht | Original Mustermann | Aktueller Stand | Technische Bewertung |
|---|---|---|---|
| Resonanz HTML | Enthält Resonanzanalyse, morphische Feldübersicht, Einflussfaktoren, Deutung des Laufs, Fokus/Symptom, Basis-Metriken, Resonanzwerte und zahlreiche schön benannte Subgruppenbereiche. | Enthält diese Kernsektionen weitgehend, zusätzlich Wellbeing Compliance. Gruppenüberschriften sind teils rohe technische Keys wie `bakterien_detailliert_fein` oder `heel_remedies_multiplex`. | Kernreport funktioniert, Layout-/Label-Parität ist unvollständig. |
| Resonanz PDF | Mindestens ein Original-Profil hat PDF-Ausgabe. | In der aktuellen Top-7-Session wurde kein per-profile PDF gefunden. | PDF-Erzeugung ist nicht durchgängig in die Top-N-Resonanzsession eingebunden. |
| Deutung | Eigenständiger HTML/PDF-Bericht mit klarer Interpretationsstruktur. | Aktueller Top-N-Lauf erzeugt keinen Deutungsordner. | Tooling existiert nur leichtgewichtig und wird nicht automatisch von `top3-scan` aufgerufen. |
| Remedies Gesamt | Timestampbezogene HTML-Berichte, klar auf Top-9 bezogen. | Gesamtbericht wird erzeugt, aber Quellliste kann historische Scans enthalten. | Werte können verfälscht wirken, weil nicht ausschließlich aktuelle Session-Dateien genutzt werden. |
| Remedies Profilberichte | Timestampbezogene per-profile HTML-Berichte passend zur Session. | Per-profile Dateien werden im Root des Remedies-Ordners erzeugt und historische Dateien bleiben daneben liegen. | Session-Isolation fehlt. |
| Synergy | Timestampbezogener Gesamtbereich. | Timestampbezogener Zielordner vorhanden. | Zielordner ist gut, Quell-Dateiauswahl ist zu breit. |
| Trends | Trends-Struktur vorhanden. | Wird im Top-N-Workflow nicht automatisch erzeugt. | Trend-Tool sollte nach dem Lauf optional/automatisch angebunden werden. |

## Ursache: historische JSON-Dateien in aktuellen Berichten

| Codebereich | Aktueller Ablauf | Problem |
|---|---|---|
| `apps/cli/commands/scan.py` | Nach der Top-N-Vollanalyse werden JSON-Dateien über vier Muster gesammelt: sessionbezogene `*_multiplex_scan.json`, sessionbezogene `*_field_test.json`, danach zusätzlich globale `*_multiplex_scan.json` und globale `*_field_test.json`. | Die globalen Fallback-Muster ziehen alte Analysen desselben Exportroots in den aktuellen Report. |
| `tools/remedy_reporter.py` | `consolidate_remedy_synergies()` erzeugt für jede Quell-JSON einen Profilbericht im Remedies-Zielordner. | Wenn historische Quell-JSONs übergeben werden, entstehen historische per-profile Reports im aktuellen Remedies-Kontext. |
| `tools/synergy_consolidator.py` | `consolidate_synergies()` übernimmt alle übergebenen JSONs. | Der Synergy-Report ist nur so sessionrein wie die Quellliste. |
| `tools/reporting_common.py` | `find_client_scan_files()` ist bewusst historisch breit und hat keinen Sessionfilter. | Für manuelle Historien-/Trendtools passend, für Top-N-Konsolidierung zu breit. |

## Profilscan: 35 statt über 100 Profile

| Frage | Antwort |
|---|---|
| Werden die 35 Profile anhand des Klientenvektors vorausgewählt? | Nein. Die 35 Profile sind aktuell das vollständige aktive Profiluniversum aus `core.profile_sync.get_top3_analysis_profiles()`. |
| Wo wirkt der Klientenvektor aktuell? | Der Klientenvektor wirkt innerhalb des jeweiligen Profilscans auf Scoring/Rateberechnung. Er entscheidet aktuell nicht, welche Hauptprofile überhaupt gescreent werden. |
| Was macht `--quick/--full`? | `--quick` nutzt pro Hauptprofil weniger Screening-Kandidaten, aktuell 24. `--full` nutzt 48. Das ändert nicht die Anzahl der Hauptprofile. |
| Was macht `--top-n`? | Es entscheidet nur, wie viele der nach dem Screening sortierten Profile vollständig analysiert werden. Aktuell erlaubt die CLI 3 bis 10. |
| Warum fehlen Originalprofile wie `b10_mikrozirkulation`, `stammzellen_peptide`, `frequenz_solfeggio`, `b9_entgiftung_reinigung`? | Diese Namen sind im aktuellen aktiven Hauptprofilregister nicht als Screeningprofile vorhanden. Teilinhalte können als Gruppen/Multiplexe existieren, sind aber nicht als Top-N-Hauptprofile verfügbar. |

### Aktuelle aktive Hauptprofile

| Kategorie | Anzahl | Beispiele |
|---|---:|---|
| Basis/Regulation | 5 | `pathogen`, `toxin`, `immune`, `detox`, `regulation` |
| Organe/Systeme | 11 | `verdauung_detailliert`, `leber_detailliert`, `atmung_lunge_detailliert`, `gehirn_detailliert` |
| Struktur | 5 | `knochen_detailliert`, `wirbelsaeule_detailliert`, `zahn_detailliert`, `tote_zaehne_detailliert` |
| Symptome | 3 | `schmerz_detailliert`, `schwindel_detailliert`, `allergie_detailliert` |
| Tox/Belastung | 6 | `schwermetalle`, `strahlung_detailliert`, `pestizide_herbizide`, `medikamenten_toxizitaet` |
| Stoffwechsel | 2 | `nahrungsmittel_intoleranzen`, `mitochondrien_dysfunktion` |
| Psyche | 1 | `psyche_detailliert` |
| Energie/Erbe | 2 | `chakren_meridiane`, `miasma_detailliert` |

## Klientenvektor, Patientenbild und Fokusbild

| Aspekt | Aktueller Codezustand | Bewertung |
|---|---|---|
| Basis-Klientenprofil | CLI erzeugt `personal_profile` mit `emotion`, `physisch`, `mental`, `astral`; Default ist jeweils `0.5`. | Vorhanden, aber bei vielen Workflows faktisch neutral. |
| Patientenbild | `ClientProfile` hat `image_signature`; `RateEncoder.image_to_rates()` kann aus Bilddaten Raten ableiten. | Core-Hook vorhanden, aber kein vollständiger CLI/Web/Report/DSGVO-Fluss. |
| Fokusbild | Kein eigener produktiver Parameter und kein separater Fokusbild-Vektor gefunden. | Nicht implementiert. |
| Report-Metadaten | JSON enthält Image-Block, aktuell `present=false`, `source=default`, `quality=""`. | Der Report kennt das Konzept, aber keine echte Eingabe. |
| DSGVO/Wellbeing | Wellbeing-Hinweise und Runtime-Manifest wurden integriert. | Für Bilddaten braucht es zusätzlich Opt-in, Hashing, minimierte Speicherung und Lösch-/Auditfluss. |

## Priorisierter Umsetzungsplan

| Priorität | Maßnahme | Ziel |
|---:|---|---|
| P0.1 | Top-N-Konsolidierung nur noch mit JSON-Dateien der aktuellen `session_timestamp` speisen. | Remedies/Synergy beziehen sich wieder sauber auf den gerade ausgeführten Lauf. |
| P0.2 | Sessionfilter testbar als Helper absichern und Duplikate entfernen. | Regression verhindern, wenn Exportstruktur wächst. |
| P0.3 | Remedy-Profilberichte sessionbezogen benennen oder in Session-Unterordner schreiben. | Keine Vermischung alter und aktueller per-profile Remedies. |
| P1.1 | Deutung automatisch nach Top-N erzeugen und in Manifest registrieren. | Referenzstruktur `..._Deutung` wiederherstellen. |
| P1.2 | Trends nach Top-N optional/automatisch erzeugen, mit Hinweis bei nur einer Session. | Referenzstruktur `..._Trends` wiederherstellen. |
| P1.3 | Resonanz-Labels und PDF-Ausgabe an Mustermann-Struktur annähern. | Layout-/Funktionsparität verbessern. |
| P1.4 | Profiluniversum rekonstruieren/erweitern: Legacy-Profile und optionalen Deep-Screening-Modus mit >100 Profilen prüfen. | Originalähnliche Screeningbreite wiederherstellen, ohne die aktuellen stabilen 35 Profile zu destabilisieren. |
| P2.1 | Patientenbild als explizites Opt-in einführen: lokale Datei, Hash, abgeleiteter Vektor, keine Rohbildspeicherung als Default. | Datenschutzkonformer Bildvektor. |
| P2.2 | Fokusbild separat vom Patientenbild modellieren. | Fokusbild kann Analyseimpuls sein, ohne als Patientendatum behandelt zu werden. |
| P2.3 | Web-UI für Bild-/Fokusbildstatus, Einwilligung und Löschung anbinden. | Benutzerführung und DSGVO-Transparenz. |

## Nächster technischer Schritt

Der erste notwendige Fix ist P0.1/P0.2: `top3-scan` darf konsolidierte Remedies- und Synergy-Berichte nur aus Dateien der aktuellen Session erzeugen. Erst danach sind Detailanpassungen an Layout, Deutung, Trends und Profiluniversum belastbar prüfbar, weil die angezeigten Werte dann nicht mehr durch Altdaten verfälscht werden.
