# 04 – Weitere Lücken, Prüfaufträge und Verbesserungsideen

Status: separate Besprechungsliste. **Nicht automatisch Teil der freigegebenen Planung.** Bestätigte Hauptbefunde R01–R06 stehen in Dokument 01. Die folgenden Punkte unterscheiden Beobachtung, Risiko und optionale Verbesserung. Keine neue Produktfunktion oder Sperre entsteht allein durch diesen Katalog.

## A. Zusätzliche technische und organisatorische Prüfaufträge

| ID | Bereich / Beobachtung | Noch zu klärende Frage | Konkreter Nachweis / Verbesserung | Zeitpunkt |
|---|---|---|---|---|
| L01 | `K1_CANON` und Validator fixieren `currentServerGate: G0-SRV-0` sowie weitere Snapshotwerte | Wie wird ein tatsächlich bestandenes Servergate später übernommen, ohne den alten Snapshot als ewige Norm zu behandeln? | Freigegebenen Übergangsvertrag definieren: neue Gateevidenz, abgeleitete aktive Anzeige, historische Version erhalten; fehlender Nachweis bleibt gesperrt | Vor erstem Gatefortschritt |
| L02 | `build` verkettet `db:migrate`; Dev-Konfiguration kennt DB-Bootstrap; Wrapper übernimmt Prozessenvironment | Welche DB-/Datei-/Netzwerkwirkungen hat jeder konkrete Prüfprozess? | Pro Script Wirkungsmatrix erstellen; synthetische Testumgebung von produktiven Credentials trennen; keine Behauptung „lesend“ allein wegen GET/Build | Vor E4/E5 |
| L03 | Runner entdeckt MJS rekursiv, TS über zwei benannte Pflichtdateien | Wie werden künftig zusätzliche TypeScript-Tests erfasst? | Bewusste Allowlist fortführen oder zusätzliche TS-Discovery freigeben; Negativtest für neu hinzugefügten, nicht erfassten Pflicht-Test | E2, sofern Vertrag betroffen |
| L04 | Lokal gespeicherte Statusansicht war nicht über das Browserwerkzeug öffnbar | Welcher zulässige Anzeigeweg und Aktualisierungsprozess wird verwendet? | Bedienweg dokumentieren; Datum/Commit anzeigen. Browser-Sicherheitsablehnung nicht durch CDP, lokalen Proxy oder andere Oberfläche umgehen | E1/E6 |
| L05 | Eindeutige Eingangsquelle des Status ist vorgesehen, Anzeige bislang manuell | Wie erkennt die Anzeige, dass sich der Code seit dem Nachweis geändert hat? | Snapshotfingerabdruck, Dirty-Kennzeichnung und `stale`-Anzeige; veraltete Befunde bleiben lesbar | E1 |
| L06 | Plattformassets sind externe Voraussetzung im alten Plan | Welche Assets fehlen tatsächlich, von wem kommen sie und blockieren sie die reale Browserabnahme? | Frühinventur, autoritative Quelle/Version, nachvollziehbarer Integritätsnachweis; keine synthetischen Assets als echte ausgeben | E0/E7 |
| L07 | Bestehender Auth-Invariant-Check ist ein Konfigurationsvergleich | Funktionieren Sessionablauf, Rollenwechsel und Mandantenisolation tatsächlich? | Synthetische Tests mit Mandant A/B, fremden IDs, abgelaufener Session und fehlender Rolle; serverseitige Verweigerung prüfen | Phase-1-Abnahme nach G0 |
| L08 | Lokale K1-Änderungen sind weiter als historische Übergaben | Ist der vollständige Entwicklungsstand einschließlich unversionierter Arbeit wiederherstellbar? | Backupmanifest mit Branches, Tags und benötigten unversionierten Dateien; separater Restoreversuch. Kein Push als Ersatz für Backup oder Freigabe | G0-SRV-0 |
| L09 | Server-Gatedatei stammt vom 25.08.; kein aktueller Serverzugriff in diesem Review | Sind die damaligen Inventur-, Recovery- und Betreiberangaben noch gültig? | Vor physischer Ausführung aktuelle Nachweise erheben; keine alte SHA/Hardware-/Zugangsangabe als zeitlos verifiziert behandeln | Server-Preflight |
| L10 | September-RadiWorks-Unterlagen liegen als externe Evidenz vor | Welche Muster sollen überhaupt in AURELIA gelten? | Je Muster Entscheidung mit Quelle, Geltungsbereich, Konfliktprüfung und Tests; keine automatische Übernahme | Phase 3–5, bei Bedarf früheres Design |

Diese Punkte sind Prüfaufträge. Beispielsweise beweist L02 keine aktuell erfolgte Produktionsmigration; L07 behauptet keine bestehende Mandantentrennungslücke.

## B. Phasengerechte Präzisierung

| Bereich | Sinnvolle Ergänzung der späteren Detailplanung | Abnahmebeispiel | Bewusste Grenze |
|---|---|---|---|
| Datenlebenszyklus | Einwilligung, Export, Aufbewahrung und Löschung gemeinsam spezifizieren | Ein synthetischer Datensatz wird über alle vorgesehenen Speicher-/Exportpfade verfolgt | Keine juristische Konformitätsbescheinigung durch diesen Review |
| Kernel-ABI / Raten | Versionierte Eingaben, Kataloghash, Kernelversion und Modus in Provenienz binden | Gleiche freigegebene Eingaben führen zum erwarteten Referenzergebnis | Keine Adapterimplementation vor Phasenfreigabe |
| CopyGuard | Finale sichtbare Fassung und Passport/Draft an denselben Digest binden | Nachträgliche Textänderung macht alten Digest ungültig; Fehlerfall stoppt Ausgabe | Vorhandene Pflicht präzisieren, kein neues Heil-/Wirksamkeitsversprechen |
| GPU-Isolation | Mindestisolation bereits beim ersten GPU-Pfad abnehmen | Fremder Tenant-/Client-/Jobkontext wird verweigert; freigegebener Speicher wird bereinigt | Nicht alle Sicherheitsnachweise auf Phase 7 verschieben |
| Timer / Recovery | Wiederholung, Abbruch und Checkpoint-Lücken explizit spezifizieren | Neustart erzeugt keinen doppelten Effekt und keine erfundene Laufzeit | Produktarchitektur bleibt serverautoritativ |
| Report / Archiv | Exportgleichheit und versionierte Auswertung prüfen | Ein Auskunftsexport entspricht der zugrunde liegenden exportierbaren Datenfassung | Codec-Auswahl bleibt WV06 |
| Betrieb | RPO/RTO, Alarmierung und Restoreübungen messbar festlegen | Wiederherstellung erfüllt freigegebene Zeit-/Datenverlustgrenzen | Werte nicht ohne Betreiberentscheidung erfinden |
| Barrierefreiheit | Separaten Prüfplan für Navigation, Fokus, Kontrast und Fehlermeldungen vorsehen | Relevante Abläufe ohne Maus mit nachvollziehbarem Fokus | Ein mobiler Screenshot ist kein WCAG-Gesamtnachweis |

## C. Optionale Verbesserungen mit überschaubarem Aufwand

| ID | Idee | Nutzen | Minimaler Umfang | Aufwand / Übernahmekriterium |
|---|---|---|---|---|
| I01 | Statische Status-HTML aus operativem JSON erzeugen | Eine Fortschrittsquelle für Mensch und LLM, weniger manuelle Drift | Kleiner lokaler Generator; Datum, Commit, Dirty-Status und Gateverweise; kein Backend | Nach E1, wenn regelmäßige Pflege den Aufwand rechtfertigt |
| I02 | Automatischer Aktualitätscheck | Alte PASS-Nachweise werden sichtbar statt still weitergetragen | Vergleich relevanter Quell-/Konfigurationsfingerabdrücke mit Evidenz | Nur nichtgeheime Eingaben; kein pauschales Invalidieren jedes Dokuments |
| I03 | Abhängigkeitsübersicht für Arbeitspakete | Zeigt, welche Arbeit trotz externer Blocker sinnvoll bleibt | Kleine Mermaid-Grafik aus E0–E8 und Servergates | Keine zusätzliche Task-Plattform erforderlich |
| I04 | Änderungsbezogene Testauswahl | Weniger wiederholte Vollsuites im Entwicklungszyklus | Explizite Zuordnung Datei-/Vertragsbereich zu Prüfungen; komplette Suite bei E8 | Auswahl selbst darf keine Pflichtprüfung verschlucken |
| I05 | Vorbereitete Fehlerfall-Sammlung | Wiederverwendbare, reproduzierbare Negativtests | Synthetische Fälle: Port belegt, falsche Instanz, fehlende Datei, Timeout, Signal, Pfadausbruch | Keine generische Testplattform bauen; bei realem Bedarf erweitern |
| I06 | Kleine Entscheidungseinträge | LLMs müssen Vertragsänderungen nicht aus Chats rekonstruieren | ID, Datum, Entscheidung, Quelle, betroffene Tasks, ersetzter Vertrag | Historische Entscheidungen bleiben erhalten |
| I07 | Maschineller Check der Dokumentverweise | Falsche Task-/Dateiverweise früher erkennen | Existenz von verlinkten Dateien und Pflicht-Task-IDs prüfen | Kein semantisches PASS allein aus existierendem Link ableiten |

## D. Nicht empfohlen

- Den K1-Kanon oder Scanner wegen dieses Reviews neu schreiben.
- Alle zukünftigen Produktphasen jetzt bis auf Implementierungszeilen planen.
- Eine neue Datenbank oder einen Dienst nur für die Statusanzeige einführen.
- Sicherheitsgates lockern, damit ein Dashboard grün wird.
- Historische Testanzahlen als künftige Mindest-/Sollzahl festschreiben, statt echte Abdeckung zu prüfen.
- Alle Tasks ungeachtet ihres Risikos mehrfach vollständig durch LLMs reviewen.
- Eigenständig neue Abhängigkeiten, Modelle, Tools oder Plattformen beschaffen.

## E. Priorisierung für die Besprechung

Zuerst R01/R02/R05 und die Statusklassifikation bearbeiten. L01/L02/L06 vor dem jeweils abhängigen Schritt klären. I01/I02 bieten den größten direkten Nutzen für die beobachtete Statusdrift, sind aber keine Voraussetzung für das bloße Dokumentieren eines korrekten aktuellen Stands. Die restlichen Produktpräzisierungen gehören in ihre jeweiligen Phasenverträge.
