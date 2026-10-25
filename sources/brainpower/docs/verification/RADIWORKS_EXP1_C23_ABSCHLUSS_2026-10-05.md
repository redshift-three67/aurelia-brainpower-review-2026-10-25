# RadiWorks EXP1-C2/C3 — technischer Abschluss des Vergleichskandidaten

Stand: 2026-10-05T11:25:23.975157+02:00. Kandidat `runtime/rw-exp1c23-20261005`, **131 Produktdateien**. C2 und C3 sind implementiert und technisch geprüft; **persönliche Oberflächenabnahme und kontrollierte Übernahme sind noch offen**. Auf 8103–8110 bleibt der bisherige Stand aktiv. Die ausschließlich synthetische Entwicklungsprobe auf 8111 wurde nach den Prüfungen beendet. Keine Aurelia-Integrationsfreigabe.

## Was jetzt möglich ist

**C2:** Ein ausdrücklich gestarteter Experimentalvergleich bekommt eine eigene Auftrags- und Sitzungs-ID in einer privaten SQLite-Datenbank. Originalfall, Originalanalyse, Entropiejournal, GV und Broadcast werden durch den Vergleich nicht verändert. Grundlage ist eine serverseitig gespeicherte unveränderliche Originalanalyse: persönlicher Kontext, exakter Katalog, Ergebnisliste, Baseline, Passport und Prüfsummen. Spätere Änderungen am Fall werden nicht rückwirkend übernommen. Eine gewählte Seite umfasst höchstens 21 Raten. Die Position in der vollständigen Originalliste bleibt erkennbar, auch auf Seite 2 und folgenden.

Der optionale CPU-Prozess arbeitet getrennt mit dem unveränderten C1-Verfahren und 80.000 Kandidaten pro Rate. Pro Modulinstanz ist höchstens ein Vergleich aktiv. Fehlende CPU-Pakete oder ein beschädigter Vergleichsspeicher sperren diesen Zusatz, nicht den Originalbetrieb. Abbruch beendet nur den eigenen Prozess. Beim Wiederanlauf werden offene Aufträge als unterbrochen markiert; kein automatisches Wiederholen. Ein bewusstes Retry hat neue IDs und eine Verknüpfung zum vorherigen Auftrag. Eine wiederholte gleiche Anfrage mit derselben ID liefert denselben Auftrag. Nach unklarer Netzwerkantwort bleibt die Anfrage-ID erhalten, einschließlich Seitenwechsel/Neuladen; ein bewusstes Abgleichen verwendet dieselben Parameter. Eine später abgelehnte Abgleichantwort beweist nicht, dass die erste Anfrage nie angenommen wurde.

**C3:** Original bleibt Standard. Eine getrennte Vergleichsansicht zeigt Originalquelle, Katalog, Seite und Radi144-Ratengewicht. Die eigene Ergebnistabelle unterscheidet Original-EW/GV am Analysezeitpunkt von Experimental-Score/Intensität. Historische Ergebnisse werden getrennt geladen; veraltete asynchrone Antworten dürfen kein anderes ausgewähltes Ergebnis überschreiben. Fallwechsel/Neuladen startet keinen Auftrag. Texte werden sicher als Text dargestellt; CopyGuard gilt auch für die Quellenprojektion. Private vollständige Kontext-/Katalogdaten werden nicht an den Browser ausgegeben. Es gibt keinen Experimental-Promote- oder Broadcast-Pfad.

Der Geburtsort-/Wohnortvertrag aus EXP1-B bleibt bestehen. Das optionale Bild dient ausschließlich als Kontextnachweis, ohne numerische Gewichtung. Es werden vorhandene Radi144-Heuristiken verwendet; keine semantische KI-Suche und keine neue Formel. Score und Intensität sind rechnerische Vergleichswerte, keine medizinischen Messungen oder Wirksamkeitsnachweise.

## Nachweise

| Prüfung | Frisches Ergebnis |
| --- | --- |
| Gesamtsuite ohne optionale CPU-Abhängigkeiten | 658 bestanden / 18 erwartete Auslassungen / 0 Fehler; vor Ergänzung der zusätzlichen optionalen Stochastic-Vergleichsprobe |
| Gesamtsuite mit isolierten CPU-Abhängigkeiten | **674 bestanden / 3 bekannte Windows-Symlink-Auslassungen / 0 Fehler**, 677 Tests insgesamt |
| SQLite-Store | 30/30 bestanden; Idempotenz, Scope, Zustandswechsel, Eingabe-/Ergebnistamper, Abbruch und Retry |
| Echte Vergleichsoberfläche + CPU/API | **17 Browserprüfungen bestanden**; 25 synthetische Raten, Seite 2 mit vier Raten/Originalpositionen 22–25; 320/375px, Tastatur, keine Seitenüberbreite |
| Original-Regression im Browser | **8 Prüfungen bestanden**: gespeicherter Fall, frische Originalanalyse, 21er-GV, unveränderte Basisbelege, Dock öffnen/Escape, Vergleichshistorie, Darstellung, keine Laufzeitfehler |
| Netzwerk-/Ansichtsrennen | Zwei Szenarien bestanden: verlorenes POST, leere Liste, Neuladen, abgelehnter Abgleich, anschließend gleicher Auftrag; verspäteter Status A überschreibt ausgewählte Historie B nicht |
| Echter TCP-Neustart | Originalfall, zwei gebundene Datei-Hashes und abgeschlossenes Ergebnis erhalten; kein automatisches Replay; gleiche Anfrage-ID erzeugt keinen zweiten Auftrag |
| Stochastic-Originalquelle | Zusätzliche CPU-API-Probe bestanden: künstlicher Fall, temporärer Testschlüssel, lokale OS-Entropie; nach Originalanalyse keinerlei neue Originalziehung durch den Vergleich; Journal/Fall/Queue unverändert |
| JavaScript | 20 Syntaxprüfungen und Präsentationsvertrag bestanden |
| Geschützte Laufzeit/Referenzen | Acht gleiche Prozess-IDs und acht HTTP200/pong auf 8103–8110; sechs Referenzquellen, C1-Kern und elf gepinnte Wheels unverändert |

Die zwei Browser-Rennszenarien bestehen aus mehreren Zwischenschritten; die Zahl zwei ist keine Zahl der Einzelassertionen. CPU-Pakete liegen im isolierten C1-Dependency-Verzeichnis, der Live-venv wurde nicht verändert. Vollständige Protokolle, JUnit und Screenshots liegen im Kandidaten und Checkpoint.

Astra prüfte Spezifikation und Qualität unabhängig. Reproduzierte/fixierte Befunde: Shutdown-/Lease-Grenze, immutable Passport, ausgefallener Dispatcher, verlorene Anfrage-ID, verspätete Statusantwort und irrtümlich freigegebene neue Anfrage nach abgelehntem Abgleich. Die Quellenprojektion wurde zusätzlich direkt durch CopyGuard abgesichert; die bestehende globale Schutzschicht war bereits vorhanden. Nachreview ohne verbleibenden wesentlichen Befund in diesem Umfang. Astra führte die finalen Tests nicht selbst aus; Root prüfte sie. Review ist keine Betreiberfreigabe.

## Grenzen und nächster Schritt

- Nur exakt ein indexierter UTF-8-TXT-Katalog bis 4 MiB ist als Vergleichsquelle unterstützt. Original-Präfixanalysen über mehrere Dateien bleiben unverändert nutzbar, erhalten jedoch keine geeignete Vergleichsquelle. Alte Sitzungen ohne serverseitige Basis und abgeleitete GV-Sitzungen ohne eigene Basis benötigen eine geeignete Originalquelle bzw. eine frische Originalanalyse. Nichts wird nachträglich erfunden.
- Der eingefrorene Original-GV stammt vom Analysezeitpunkt, häufig 0 vor einer GV-Prüfung. Spätere GV-Züge ändern diesen Vergleichswert nicht. Bei einer geladenen alten Sitzung verlangt der bestehende Original-21er-Handler eine frische Analyse; dieser Ablauf wurde erhalten.
- Dies ist ein lokaler, servergebundener Scope, keine fertig implementierte Aurelia-Mandantenautorisierung. CPU-Quotas über mehrere Modulinstanzen, Admin-/Nutzerimporte, Katalogrechte/-versionen und Plattform-Hostvertrag bleiben eigene Arbeitspakete.
- Browser-/Testclient-/TCP-Neustartnachweise sind keine neue Prüfung eines Windows-Warmstarts oder aller aktiven Broadcasts. Keine neue Kamera-/random.org-Langlaufabnahme. Tests benutzen ausschließlich künstliche Daten; keine echte Webcam, Fallakte oder E:/F:-Schlüssel.
- Windows10/Python3.13.7 auf diesem Host geprüft; keine frische Windows-PC-Standalone-Installation oder Linux-Portabilitätsabnahme. Die elf archivierten CPU-Wheels sind win_amd64/CP313. Noch kein Vollkatalog-/Mehrinstanz-Lastnachweis, keine gemessene Tokenersparnis.
- Nächstes: kontrollierte synthetische Pilotübernahme und persönliche C3-Abnahme; übrige RadiWorks-Abnahmen konsolidieren, dann Quellordner/Modul_Templates gezielt synchronisieren. Danach Standalone-Paket bis fünf Instanzen und vollständige F:-Sicherung mit Restoreprobe; anschließend weitere Module. S4.8 bleibt getrennt.

## Phasenstand

| Phase | Stand |
| --- | --- |
| EXP1-C1 CPU-Kern | 100% des technischen Prüfpakets |
| EXP1-C2 persistente Vergleiche/Wiederanlauf | **100% technisch im Kandidaten** |
| EXP1-C3 ausdrückliche Wahl/Vergleichsansicht | **100% technisch; persönliche Abnahme offen** |
| Quell-/Template-Übernahme dieses Deltas | Offen, nur vorbereitet |
| Aurelia S4.8 | **0% Freigabe** |

Prozente beziehen sich ausschließlich auf die genannten begrenzten Pakete, nicht auf die Gesamtintegration oder eine Sicherheitsgarantie.

Tatsächlich eingesetzt: **Luna6/max** für Vergleichsstore und dessen Tests; **Astra6/medium** für unabhängigen Review/Nachreview; Root für Integration, CPU-Prozess, API, UI, Tests und Abschluss. Vom Betreiber gewählte Leitung **Sol6.1/high**. Hermes-Anwendungsrouting unverändert; keine echten Hermes-Modellaufträge in diesem Block.

[Template-Delta](RADIWORKS_EXP1_C23_TEMPLATE_DELTA_2026-10-05.md) · [Umsetzungsplan](RADIWORKS_EXP1_C23_UMSETZUNGSPLAN_2026-10-05.md) · [Katalogverwaltung](RADIWORKS_AURELIA_KATALOGVERWALTUNG_2026-10-05.md).

[Lokaler begrenzter Wiederherstellungspunkt](../../checkpoints/RadiWorks-EXP1-C23-20261005-112523/RESTORE.md): vollständiger Kandidat, elf CPU-Wheels, gebundene Referenzen, Belege und Fortsetzung. Kein aktueller Live-Datenstand und keine F:-Gesamtsicherung.
