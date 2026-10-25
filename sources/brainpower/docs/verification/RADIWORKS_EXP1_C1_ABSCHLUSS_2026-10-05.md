# RadiWorks EXP1-C1 — geprüfter optionaler CPU-Matrixkern

Stand: 05.10.2026. Kandidat `runtime/rw-exp1c-20261005`, 120 Produktdateien. **C1 abgeschlossen; C2/C3 und Liveauswahl noch offen.** Dies ist keine Aurelia-Integrationsfreigabe.

## Verhalten und Abgrenzung

Der neue reine Helper `engine/src/radiworks/core/experimental_matrix.py` berechnet separat das bestehende Radi144-Matrixverfahren. Er nimmt einen validierten persönlichen Snapshot, den exakten UTF-8-Katalog samt Dateiname/SHA-256 und eine eingefrorene Liste von 1–21 Katalograten. Original-EW, Potenz, Level, GV, Sitzungen, Queue und Broadcast werden nicht geändert. Keine neue API oder Oberflächenwahl in C1.

Profil: CPU, Float32, 12×12-Matrix, 256 Dimensionen, 80.000 Kandidaten pro Rate, ein zuvor konfigurierter Thread, Cosinusvergleich, Top10/erstes Ergebnis. Eigene CPU-Zufallsgeneratoren erhalten das globale RNG. Fokusgewicht exakt Deaktiviert=0, Sanft=0,4, Normal=1, Stark=1,5. Der gespeicherte Fallfokus wirkt nur beim vollständigen case-insensitiven Teilstringtreffer im eingefrorenen Katalog und positiver Original-Textfrequenz; kein semantisches Verfahren. Die Ratenbezeichnung bleibt der direkte Fokus der Matrixberechnung. Formelversion, Quellenhashes, Fall-/Kontextbindung, Kataloghash, Parameter, Score, Intensität, Matrix und Ergebnisdigest werden ausgegeben. Prüfsummen sind keine Authentifizierung.

Persönliche Skalare stammen unverändert aus EXP1-B. Ein expliziter Geburtsort kann nach dessen Vertrag wirken; Wohnort und untypisierte Altorte nicht. Bilder bleiben Kontext ohne numerische Gewichtung. Organuhr, Bio/HRV/EMF, Quantum, Symmetrie und automatische Hardwareanpassung sind aus. 64 Kandidaten existieren ausschließlich als deutlich markiertes Testprofil. Die feste produktive Kandidatenzahl ist der niedrigste ursprüngliche CPU-Wert; der Referenzvergleich verwendet dieselbe Zahl und behauptet keine Gleichheit mit jedem adaptiven Originalbetrieb.

Die optionalen Abhängigkeiten liegen ausschließlich in `runtime/rw-exp1c-20261005/deps`. Der bestehende Live-venv wurde nicht verändert. Torch `2.12.0+cpu`, NumPy `2.4.6` und neun transitive Pakete sind über elf Wheels, SHA-256, `engine/requirements-exp1-cpu.lock` und Pip-Installationsbericht festgehalten. Download vom [offiziellen PyTorch-CPU-Index](https://download.pytorch.org/whl/cpu); Installationsweg gemäß [PyTorch-Dokumentation](https://pytorch.org/get-started/locally/). Fehlende/fremde Versionen, falsche Laufzeit/Threadkonfiguration und Berechnungsfehler liefern einen sichtbaren kontrollierten Fehler; keine stille Alternative und kein partiell erfolgreiches Ergebnis.

## Frische Nachweise

| Prüfung | Ergebnis |
| --- | --- |
| Gesamtsuite ohne optionale CPU-Pakete | 608 bestanden, 13 übersprungen: zehn optionale CPU-Prüfungen und drei bekannte Windows-Symlinkgrenzen; keine Fehler |
| Gesamtsuite mit isolierten CPU-Paketen | 618 bestanden, drei Windows-Symlinkprüfungen übersprungen; keine Fehler |
| Neue Matrixprüfungen | 33/33 bestanden im CPU-Profil: Validierung, Tamper, Fokusmatch, Gewicht/Profile, Wiederholung, Duplikate, Kontextvariation, globale RNG-Erhaltung, parallele Aufrufe, fehlende Pakete/Versionsdrift, Teilfehler, externe Listenmutation und Float64-Default |
| Direkter Radi144-Quellenvergleich | 8/8 exakt: vier Gewichte × 64/80.000 Kandidaten; Score, Intensität und Matrix gleich. AST-extrahierte Methoden, Referenzdatei vorher SHA-geprüft; kein laufender Radi144-Auftrag |
| Synthetischer Produktbenchmark | 21 Raten × 80.000 Kandidaten: 2,838 s; Wiederholung 2,688 s, Ergebnis exakt gleich. Anderer künstlicher Vorname verändert Ergebnisse |
| Prozessspeicher im Benchmark | Peak Working Set 594.800.640 Bytes, Private Commit 663.371.776 Bytes, einschließlich geladener CPU-Abhängigkeiten; keine garantierte Obergrenze |
| Unveränderte Basis | 117/117 Eltern-Produktdateien und sechs gebundene Referenzquellen unverändert; drei neue Produktdateien |
| Oberfläche | 19 JavaScript-Dateien bestehen Syntaxprüfung. UI bytegleich zur EXP1-B-Basis; deren 41 Browserabschnitte bleiben historische Evidenz. In C1 kein neuer Browserlauf behauptet |
| Livebetrieb | 8103–8110: acht unveränderte Prozess-IDs, acht HTTP200/pong; kein Neustart oder Eingriff in Aufgaben, Homes, Keys oder reale Fälle |
| Ohne CPU-Installation | Frischer Prozess importiert Original-App und neuen Helper ohne Torch/NumPy zu laden; tatsächlicher fehlender optionaler Import als MatrixError geprüft |

Testdateien/JUnit, `TEST_SUMMARY.json`, `FINAL_PROOF.json`, `SOURCE_PARITY_BENCHMARK.json`, synthetische Resultate und `REVIEW_SUMMARY.json` liegen im Kandidaten. Die normalen und CPU-Suiten verwendeten getrennte künstliche temporäre Daten. Eine bekannte FastAPI/Starlette-Testclient-Deprecation bleibt eine Warnung, kein neuer Funktionsfehler.

Astra fand zwei echte Lücken: externe Ratenliste während der Berechnung veränderbar und impliziter Torch-Default-Datentyp. Zwei rote Regressionstests reproduzierten dies. Interne Listenkopie und explizites Float32 schließen die Lücken; gezielter Nachreview ohne verbleibenden Befund, anschließend frische CPU-Gesamtsuite. Eine nachfolgende Testabweichung durch zwei verschiedene neue Snapshot-IDs wurde im Test korrigiert; verglichen wird derselbe eingefrorene Kontext.

## Noch erforderlich

- **C2:** persistierte getrennte Vergleichsaufträge/-sitzungen; unveränderliche Originalbasis und Katalog-/Kontextbindung; Wiederanlauf, Fehler, Abbruch, Retry/Idempotenz und begrenzter separater CPU-Prozess. Keine ungeprüfte parallele CPU-Ausführung in sieben Liveinstanzen. Ressourcen-/Quotas vor Mehrmandantenbetrieb festlegen.
- **C3:** ausdrücklich wählbarer Experimentalmodus, verständliche getrennte Ergebnistabelle und Prüfparameter, Originalstandard, Browser-/Betreiberprobe. Kein automatisches Übertragen der Matrixwerte in Original-GV oder Broadcast.
- Der Benchmark lief auf diesem Windows10-Host/Python3.13.7. Keine frische Standalone-Installation auf einem anderen PC oder Ubuntu-CPU-Portabilitätsabnahme. Linux benötigt eigenes kompatibles Dependency-/Numerikprofil; `.whl`-Dateien hier sind CP313/win_amd64.
- Maximal21 Raten/4MiB Katalogtext begrenzen diesen neuen Helper, nicht bestehende Originalkataloge. Kein Vollkatalogbenchmark. C2 muss geeignete Teilmengen/Seitengrenzen ausdrücklich binden und größere Kataloge kontrolliert behandeln.
- Exakte numerische Parität/Reproduzierbarkeit beweist keine medizinische oder physikalische Wirksamkeit und keine allgemeine Modell-/Tokenersparnis.
- Quellen-/Modul_Templates-Synchronisierung, Paket bis fünf Instanzen, vollständige F:-Sicherung und Host/S4.8-Gates bleiben nach den übrigen Abnahmen erforderlich.

## Phasenstand

| Paket | Fortschritt |
| --- | --- |
| EXP1-A Quellen-/Formelprüfung | 100% des begrenzten Pakets |
| EXP1-B persönliche skalare Kontextvorbereitung | 100% des begrenzten Pakets |
| EXP1-C1 CPU-Matrixkern und Prüfprofil | 100% |
| EXP1-C2 separate Vergleichssitzungen/Wiederanlauf | 0% Umsetzung |
| EXP1-C3 explizite Wahl/Oberflächenabnahme | 0% Umsetzung |
| Aurelia S4.8 | 0% Freigabe |

EXP1-C: eines von drei definierten Arbeitspaketen abgeschlossen; grob33% nach Paketzählung, keine Qualitäts-, Zeit- oder Gesamtreifequote.

Tatsächliche Helfer: Luna6/max für lesenden Katalog-/Hostvertragsabgleich, Astra6/medium für unabhängigen Kernelreview und Nachreview; Root implementierte, integrierte und prüfte. Gewählte Chatleitung laut Betreiber Sol6.1/high; keine Ableitung aktiver Runtime-Einstellungen aus gespeicherten Defaults. Hermes-Anwendungsrouting unverändert.

Ergänzend: [Katalogverwaltung in Aurelia](RADIWORKS_AURELIA_KATALOGVERWALTUNG_2026-10-05.md), [Template-Delta](RADIWORKS_EXP1_C1_TEMPLATE_DELTA_2026-10-05.md), [Umsetzungsplan](RADIWORKS_EXP1_C_UMSETZUNGSPLAN_2026-10-05.md). Wiederherstellungspunkt im aktuellen WIEDERAUFNAHME-Einstieg.

[Begrenzter Code-/CPU-Wiederherstellungspunkt](../../checkpoints/RadiWorks-EXP1-C1-20261005-094416/RESTORE.md), erstellt 2026-10-05T09:44:16.035951+02:00. Vollständiger120-Dateien-Kandidat, elf gepinnte Wheels, Belege und Fortsetzung; Manifest/SHA-Rückleseprüfung. Kein F:-Gesamtbackup oder Live-Datenstand.
