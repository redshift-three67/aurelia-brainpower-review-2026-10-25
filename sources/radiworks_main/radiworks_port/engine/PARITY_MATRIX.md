# Java-/Python-Paritätsmatrix

**Stand:** R1 – evidenzgebundene Aussage, keine pauschale Bitidentitätsbehauptung.

## Bewertungsregel

| Urteil | Bedeutung |
| --- | --- |
| **Belegt** | Ein versioniertes, unabhängiges Original-Java-Orakel wird über den normalen Python-REST-Pfad exakt verglichen. |
| **Adapter-only** | Der Vergleich prüft Python-Komponenten gegeneinander; er ist kein unabhängiger Java-Produktionsnachweis. |
| **Vertrag geprüft** | Das Verhalten ist durch API-/Passport-Tests spezifiziert, aber nicht Gegenstand einer Java-Paritätsaussage. |
| **Offen** | Es liegt keine hinreichende, versionierte Java-Orakel-Evidenz vor. Keine Parität wird daraus abgeleitet. |

## Matrix

| Algorithmus oder Laufzeitpfad | Umfang | Urteil | Evidenz und Grenze |
| --- | --- | --- | --- |
| Seeded REST-Analyse | `POST /analysis`, 300 synthetische Raten `R0000`–`R0299`, Seed `42`, `max_hits=100` | **Belegt** | `tests/gold/gold_rest_analysis_300_seed_42.json`, JDK 24.0.1; `tests/test_gold_parity.py::test_rest_seeded_result_matches_original_java_oracle` vergleicht `generalVitality`, `numberOfTrials` und `rateObjects`. |
| Seeded REST-Analyse | Gleicher Pfad, Seed `20260829`, `max_hits=100` | **Belegt** | `tests/gold/gold_rest_analysis_300_seed_20260829.json`, JDK 24.0.1; derselbe produktive REST-Test. |
| Seeded REST-Analyse | Gleicher Pfad, Seed `42`, `max_hits=1000` | **Belegt** | `tests/gold/gold_rest_analysis_300_seed_42_max_hits_1000.json`, JDK 24.0.1; derselbe produktive REST-Test. |
| Analyse-Kern mit Gold-Adapter | Zwei-Stufen-Entropie und explizite Java-HashMap-Reihenfolge | **Adapter-only** | `GoldEntropy` und `java_hashmap_string_order` in `tests/test_gold_parity.py`; `test_production_entropy_and_order_match_gold_adapter` ist eine wertvolle interne Kontrollprobe, aber kein zusätzlicher externer Java-Orakelpfad. |
| Java-PRNG und JavaRandom-Zweitstufe | Für die drei genannten seeded REST-Fixtures | **Belegt im Fixture-Umfang** | Die Fixture-Vergleiche decken diese Ziehungen nur als Teil der drei Restpfade ab; sie belegen keine allgemeine PRNG-Parität für beliebige Aufrufer. |
| Java-HashMap-Reihenfolge | 300-Raten-Fixtures ohne Treeify-Bäume | **Belegt im Fixture-Umfang** | `tools/gold/README.md` dokumentiert die Grenze: bei 300 Raten bleiben die Bins unter der Treeify-Schwelle. |
| Java-HashMap Treeify/Kollisionen | Bins an oder über der Treeify-Grenze | **Offen** | Keine versionierte Fixture; separater R1-Gate. |
| Andere Ratenkataloge und Kataloggrößen | Reale Kataloge, andere Rate-Namen oder andere Größen | **Offen** | Die drei Orakel nutzen ausschließlich 300 synthetische Raten. |
| Stick-Pad | Zeitaddition je Position, frische Katalogsuche, fester Java-Random-Gegenwert | **Teilweise geprüft** | Original-Bytecode 2.2 und lokales 2.9.0-JAR addieren denselben Millisekundenwert zu X/Y; die 2.9.0-Analyse aktualisiert vor jeder Auswahl die Datenbankliste. Das lokale 2.9.0-JAR lieferte für drei per Reflection auf feste Seeds gesetzte synthetische Positionen `Beta=10`, `Epsilon=7`, `Delta=4`, nach Leeren 0 Positionen und bei separater erster UI-GV-Messung `602`, Zähler 1. Python entsprach für diesen Vektor (`tests/test_p3_functions.py`); dies ist kein vollständiger echter Nutzer-/Java-REST-Workflow. Der reproduzierbare Standardmodus und die lokale Fall-/Draft-Persistenz sind Port-Erweiterungen, keine Java-Paritätsbelege. |
| Stick-Pad-Katalogbindung | SHA-256 der geordneten, verwendeten Ratenwerte; Driftanzeige | **RadiWorks-Vertrag geprüft** | Analysebeleg speichert Selektor, Schema, Anzahl und Digest atomar mit dem Lauf. Zwei aufeinanderfolgende Rohdatei-Lesungen und erneute Dateiauswahl müssen übereinstimmen; synthetische Änderungen innerhalb eines Lesevorgangs werden mit 409 ohne Positionsverlust abgelehnt. Kein Schreibersperr-Protokoll, keine echte dateiübergreifende atomare Momentaufnahme, keine kryptografische Signatur und keine Java-Originalfunktion. |
| Versionierter Katalogstand | Opt-in-Release mit Manifest, Dateihashes, fester Engine-Version und API-Fehler bei Drift | **RadiWorks-Vertrag synthetisch geprüft** | `tests/test_catalog_release.py` prüft Veröffentlichung zweier Stände, Pinning, Mutation, fehlendes Manifest, HTTP 409, Skripte sowie Passport-/Stick-Pad-Bindung. Quelle muss während der Kopie stillgelegt sein; das Verfahren sichert weder einen extern veränderbaren Quellbaum noch böswillige Schreibzugriffe. Lokales Ubuntu-WSL prüfte zusätzlich Release-Pinning, echten POSIX-Symlink und prozessübergreifende Runtime-Sperre; der vorgesehene Debian-/Aurelia-Host und echte Kataloge wurden nicht geprüft. |
| Stick-Pad-Analyse, GV und Fallrunde | Positions-/kataloggebundener Passport, eigener Draft und bei aktivem Fall eigene Session; erste folgende GV als Fallwert, zweite als Rate 1 | **RadiWorks-Vertrag geprüft; Originalpfad teilweise** | Der Analysebeleg enthält Positionen und Raten-Digest; Case, Draft und Stick-Pad-Zustand werden gemeinsam per Recovery gespeichert. Ein synthetischer Abbruch nach dem ersten Dateiersatz wurde beim Neustart einmalig repariert. Ohne aktiven Fall entsteht ein Draft ohne Session. `replayable=false`, weil der historische Gesamtkatalog nicht archiviert wird. Die folgende normale GV benutzt einen aus dem gebundenen Input abgeleiteten Seed und ist damit eine dokumentierte Port-Fortsetzung. Im Einzelprozess serialisiert eine gemeinsame Sperre Fall-/GV-Mutationen mit Stick-Pad; ein künstlich verzögerter Konkurrenztest bestand. Eine exklusive OS-Sperre verhindert eine zweite gleichzeitig aktive Engine im selben Runtime-Home; Windows-Prozessabbruch und Wiederstart sind synthetisch geprüft. Dies ermöglicht keinen verteilten Mehrprozessbetrieb. UI und 390-px-Browserprobe bestanden; kein vollständiger Original-GUI-, Mehrprozess- oder Hardware-Nachweis. |
| Andere Stick-Pad-/Hilfsalgorithmen | Reale Eingabefolgen, Suche, weitere Kernhelfer | **Offen** | Kein versionierter externer Java-REST-Orakelvergleich für diese Pfade. |
| Bildschichten | Minimum/Maximum über Ziehungsrunden | **Teilweise geprüft** | 2.9.0-JAR-Bytecode hält beide Werte über alle Runden; ein zunächst roter synthetischer Zweirundentest belegt und schützt die Port-Korrektur (Minimum 0, Maximum 512, Verhältnis 0,5). Vier-Dezimalstellen-Ausgabe und Browser-Rendering sind keine vollständige Java-Parität. |
| Stochastic-Entropie | Webcam/Hotbits/Random.org/OS-CSPRNG | **Offen – absichtlich nicht replaybar** | Der Modus ist kein Java-Paritätsgegenstand; siehe `README.md` und Passport-Vertrag. |
| REST-ABI v1 und Passport v2 | Manifest, camelCase-Ausgabe, effektiver Seed, Modus-Hash, unsigned Signatur | **Vertrag geprüft** | `tests/test_r1_contract.py`; dies ist ein RadiWorks-Vertrag, keine Java-Paritätsaussage. |
| Cases, Drafts, GV-Sessionen und Recovery | Persistenz- und Wiederanlaufpfade | **Vertrag geprüft / R2** | `tests/test_session_persistence.py` und `tests/test_recovery_persistence.py`; kein Java-Paritätsnachweis beansprucht. |

## Zulässige öffentliche Aussage

Java-Orakelparität ist ausschließlich für die drei oben genannten versionierten,
seeded `POST /analysis`-Fixtures mit 300 synthetischen Raten belegt. Andere
Daten, Kataloggrößen, Treeify-/Kollisionsfälle, Hilfsalgorithmen, Persistenz-
und stochastic-Pfade sind nicht Teil dieser Aussage.

## Nächste Evidenz-Gates

1. JDK-Orakel für HashMap-Kollisionen und Treeify-Grenzen erzeugen.
2. Für jeden beanspruchten Hilfsalgorithmus einen separaten Produktpfad und ein
   versioniertes Original-Java-Orakel definieren.
3. Die Produktentscheidung dokumentieren, ob weitere seeded Kernalgorithmen
   überhaupt Java-Parität benötigen oder separat spezifiziert bleiben.
