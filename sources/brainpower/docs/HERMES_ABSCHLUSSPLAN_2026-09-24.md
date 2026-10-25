# Hermes-Abschluss: Funktionsabgleich und Arbeitsplan

Stand: 24.09.2026. Grundlage: bestätigte Strategie aus `HERMES_STRATEGIE_UND_PAUSE_2026-09-24.md`. Reasoning: Medium, kein Low-Wechsel offen. RH-1 und Laufzeitkorrekturen lokal abgenommen; [Nachweise und Grenzen der Teilprüfungen](verification/GOVERNOR_RUNTIME_2026-09-24.md). Governor beim jüngsten Modellaudit auf Port 8787 nicht erreichbar. Die folgende Iststandstabelle dokumentiert den Ausgangszustand vor RH-1, keine Gesamtproduktfreigabe.

**Aktuelle Reihenfolge vor Funktionsabnahme:** GPT-6 Sol/xhigh und GPT-6 Luna/max sind als eigene Route B mit bedingtem Astra/medium integriert und synthetisch geprüft; [Route-B-Nachweis](verification/HERMES_ROUTE_B_2026-09-24.md). Bestehende Standards und Projektfreigaben bleiben erhalten. Gemäß neuer Betreiberfolge wird nun ein konkret ausgewähltes neues Modul quellengebunden beurteilt und für Aurelia vorbereitet; die gemeinsame Funktionsabnahme bleibt danach gesondert. Die folgende Iststandstabelle ist historischer Ausgangsstand vor RH-1 und Route B.

## Ziel und Umfang

Die Windows-Steuerungsanwendung soll ihre ausdrücklich unterstützten Single-/Gruppen- und Pilotabläufe zuverlässig durchführen, nachvollziehbar anzeigen und nach Unterbrechung sicher wieder aufnehmen lassen. Aurelia bleibt ein später separat abgenommenes Ausführungsziel über WireGuard/SSH. Externe Produktrepositories werden durch diese App-Arbeiten nicht verändert.

Wir erweitern die vorhandene Anwendung schrittweise. Ein sofortiger Linux-Umzug würde zusätzliche Prozess-, Pfad- und Transportänderungen mit der Funktionsabnahme vermischen. Ein paralleler Neuaufbau würde bereits vorhandene Nachweise und Bedienwege duplizieren. Beide Alternativen sind für diesen Abschluss zurückgestellt.

## Abgeglichener Iststand

| Bereich | Vorhanden / Nachweis | Verbleibende Grenze |
|---|---|---|
| Einzelprojekte/Gruppen | Registry, begrenzte Scopes, Versandfreigaben pro Mitglied; `registry.py`, `scopes.py` | Durchgängiger UI-Wechsel mit laufenden Aufträgen noch gezielt abnehmen. Mitgliedschaft dauerhaft, maximal eine Gruppe pro Projekt. |
| Anforderungen/Planung | Quellengebundene Aufnahmen, Planentwürfe, ausdrückliche Auswahl und Strategieübernahme | Registrierung vorhandener Verzeichnisse ist keine vollständige Projektneuanlage. Entwürfe sind keine angenommenen Anforderungen. |
| Änderungen/Tests | Isolierter Pilot, Tests, unabhängige Nachprüfung, separate Übernahme, Abschluss und Rollback | Fest begrenzte Adapter, keine beliebigen Produktbefehle oder allgemeine Gruppenausführung. |
| Abhängige Abläufe | S1-Prüffolge, S2-Testketten und direktes A→B-Pilotprofil vorhanden | S3c-C4-Bericht vom 18.09.: 659 Tests, 657 erfolgreich, zwei ausgelassen. Historischer Beleg, kein neuer Gesamtlauf. |
| Modellrouting | Terra mit separat gewähltem Sol/Astra-Supervisor | Medium mehrfach fest eingebaut; RH-1 offen. Keine Änderung der Modellrollen durch diesen Plan. |
| Betrieb/Verteilung | Windows-Launcher, lokaler Dienst, Release-/Installationswerkzeuge | Fremd-PC-Erstsetup und neutrales projektloses Paket nicht vollständig abgenommen. |

Die historische Abschlussdatei enthält ältere Aussagen, die durch spätere Teilschritte überholt sind. Für das direkte A→B-Profil gelten README, der aktuelle Anfang der Entwickleranleitung und `FORTSETZUNG_SECHS_SCHRITTE_2026-09-18.md`. Bereits implementierte Reparatur-/Testketten werden nicht erneut als fehlende Neuentwicklung eingeplant.

## Block 1 — Basis und Abnahmematrix

- [x] Strategie, aktuelle Vertragsgrenzen und maßgebliche spätere Nachweise abgleichen.
- [x] Konkrete Medium-Bindungen ermitteln: `config.py`, `llm.py`, `hermes.py`, `hermes_runner.py`, `server.py`, `sequences.py`, Oberfläche.
- [x] Gezielte Ausgangstests für Registry, Scopes und Hermes abschließen; 36 Tests bestanden, Nachweis unten.
- [x] RH-1-Aufrufstellen einschließlich Planung, Patch, Reparatur, Rückfragen, Supervisor und genehmigter Folgen verfolgen; Umsetzung und konkrete Grenzen siehe RH-1-Prüfbericht.

## Block 2 — RH-1: einheitliche Auswahl und nachvollziehbare Aufrufe

Fachliche Grundlage ist der bestehende Betreiberauftrag in `HERMES_APP_ABSCHLUSS.md`, Abschnitt RH-1. Vor Produktionsänderungen werden dessen konkrete Datenfelder und Aufrufgrenzen in einem eigenen kleinen Implementierungsplan festgelegt.

1. Gemeinsame Auswahlregel für Backend und UI entwerfen: Medium als Standard; bestehende manuelle Auswahl und Supervisor erhalten. Low nur bei ausdrücklich aktiviertem Automatikmodus und nachweislich begrenztem Routineauftrag. Unbekannte Einordnung sowie Planung, Diagnose, Sicherheits-/Backup-/Migrationsarbeit und kritischer unabhängiger Review bleiben Medium. High/xHigh niemals automatisch.
2. Unterstützte Modell-/Transportkombinationen prüfen und validieren. Fehlende Unterstützung führt zu verständlichem Abbruch, nicht zu heimlichem Fallback. Konfigurationsmigration erhält bestehendes Verhalten; keine automatische Aktivierung neuer Optionen.
3. Auswahl pro Modellaufruf festlegen und mit Auftrag/Einwilligung verbinden. Gewünschte und effektive Stufe, Modell, Rolle, Grund und Regelversion dauerhaft speichern. Bestehende Einwilligungen dürfen nicht still auf neues Routing erweitert werden. Änderungen zwischen Vorschau, Warteschlange und Aufruf werden erneut geprüft.
4. Hermes-Elternadapter, isolierten Runner und direkten Router gemeinsam anpassen. Der Runner muss die tatsächlich festgelegte Stufe prüfen; bloßes Entfernen der bisherigen Medium-Prüfung wäre unzureichend. Werkzeugfreiheit, Zieladresse, `store=false`, Antwortmodell und unabhängiger Supervisor bleiben geschützt.
5. UI zeigt Auswahl und tatsächlichen Aufrufbeleg; historische Aufträge ohne neue Felder als unbekannt/alt kennzeichnen, nicht nachträglich umdeuten. Kein Rückschluss auf die Reasoning-Einstellung dieses Codex-Chats.

Voraussichtliche betroffene Dateien: neue fokussierte Routingregel; `config.py`, `jobs.py`, `server.py`, `llm.py`, `hermes.py`, `hermes_runner.py`, `model_usage.py`, aufrufende Planungs-/Patch-/Reparatur-/Folgemodule und `static/app.js`/`index.html`. Exakte Reichweite nach Aufrufverfolgung festlegen, kein pauschaler Umbau.

Abnahme: Regelmatrix; manuelle Auswahl; nicht unterstützte Kombination; unveränderte Altkonfiguration; persistente Aufrufbelege; Neustart; geändertes Routing nach Vorschau; Fehler/Rückfrage vor Folgeaufruf; kein automatisches High/xHigh; Supervisor nicht abgesenkt; kein heimlicher Modellwechsel. Danach Python-/JS-/Browserprüfung, relevante Kettenregression und lokale Hermes-Nullwerkzeugprobe. Live-Qualitäts-/Verbrauchsvergleich ist eine gesonderte freigegebene Evaluation, keine Voraussetzung für reine lokale Unit-Tests und keine garantierte Ersparnis.

Implementierungsbeginn wurde ausdrücklich gemeldet; Umsetzung und Abnahme sind im RH-1-Prüfbericht dokumentiert. Die Erstellung dieses Plans allein änderte noch kein Routing.

## Block 3 — Projekttrennung, Arbeitsablauf und Bedienführung

Projektwechsel und getrennte tablokale Aufnahmeentwürfe geprüft: [Bericht 24.09.2026](verification/PROJECT_CONTEXT_2026-09-24.md). Kleine kontextbezogene Schrittführung ebenfalls abgeschlossen: [Block 3b](verification/WORKFLOW_GUIDE_2026-09-24.md). Nächster Schritt: gemeinsame Funktionsabnahme und Besprechung.

Mit temporären Projekten A, B und einer separaten Gruppe prüfen:

Vorhandene Backend-Nachweise gezielt wiederverwenden: `test_scopes` (fremde Quellen/Entwürfe ausgeschlossen, Mitgliedsfreigaben, gruppengebundener Kontext), `test_registry` (dauerhafte Identität/Mitgliedschaft, keine Pfadüberlappung, Registrierung nach Neustart) und `test_server` (gebundene Pilot-/Kettenaktionen). Die ursprünglich gesondert nachzuweisende Browserstrecke umfasste laufenden Auftrag plus Kontextwechsel, verspätete Antworten, erhaltene Entwürfe und eindeutig zugeordneten nächsten Schritt. Die Liste bleibt Abnahmegrundlage; konkrete Browsernachweise und Grenzen stehen in den beiden Block-3-Berichten.

- Single A enthält keine Quellen, Erinnerungen, Ergebnisse oder Freigaben von B; Gruppe enthält nur ihre Mitglieder.
- Wechsel A→B bei laufendem Auftrag verändert weder dessen Ziel noch gespeicherte Zustimmung. Verspätete Antworten dürfen im neuen Kontext keine fremde Aktion aktivieren.
- Offene Entwürfe, Rückfragen und Auswahl sind eindeutig zugeordnet; Neustart startet keine unterbrochenen Schreib- oder Modellaufträge automatisch.
- Ein vollständiger Pilotablauf umfasst Anforderungen, Plan, Auswahl, Vorschlag, tatsächlichen Test, unabhängigen Review, getrennte Übernahme, Abschluss und Rücknahme. Fehler, Drift, verweigerte Freigabe und Abbruch ebenfalls prüfen.
- Das vorhandene direkte A→B-Profil behält eigene B-Prüfung und Rücknahme nur in umgekehrter Reihenfolge. Keine Übertragung von A-Testerfolg auf B.
- Gruppenplanung und Single-Ausführung deutlich unterscheiden. Eine Gruppenmatrix wird erst dann ausführbar genannt, wenn passende konkrete Adapter und Projektfreigaben tatsächlich vorliegen.

Kleine Bedienergänzungen erst auf stabilen Fachzuständen: aktiver Kontext sichtbar, kurze Schrittanzeige, eine nächste zulässige Aktion hervorgehoben, Sperrgrund direkt angezeigt. Farbe ergänzt Text/Symbol; bestehendes Layout und Freigaben bleiben erhalten. Keine neue automatische Ausführung durch Navigation.

Neue Projektanlage und neue Produktadapter sind eigene begrenzte Arbeitspakete: je Adapter Start-/Stop-/Testvertrag, Zielumfang, Freigabebindung, Ergebnis, Abbruch und Rücknahme festlegen. Ein allgemeiner Shell-Endpunkt ist kein Ersatz. Die konkreten Aurelia-Module werden wie vereinbart erst nach der gemeinsamen Hermes-Abnahme ausgewählt.

## Danach — saubere Windows-Ausgabe

Ein gemeinsames neutrales Paket statt zweier Produktvarianten: leere Projektregistry, neutrale Konfiguration, keine persönlichen Laufzeit-/Serverberichte oder Anmeldedaten. `build_release.py` benötigt eine gezielte Dokumentauswahl; `config.example.json` enthält derzeit reale Projektvorgaben. Eigene Python-/Hermes-/Router-Einrichtung und Anmeldung auf dem Ziel bleiben erforderlich, solange sie nicht ausdrücklich mit abgenommenem Setup bereitgestellt werden.

Abnahme auf sauberem Windows-Profil/PC: Einrichtung, eigener Login, leeres Projekt, unterstützter Kernablauf, Neustart, Update und Erhaltung der Nutzerdaten. Danach optional Installer um dieselbe Ausgabe. Ein lokal gebautes ZIP allein ist keine bestandene Fremd-PC-Abnahme.

## Grenzen und Übergabe

Wiederherstellungspunkt `checkpoints/Hermes-20260924-Pause` bleibt unverändert. Keine automatischen Modellreviews aktivieren, keine bestehenden Produktpläne annehmen, keine echten Projekte an Modelle übertragen, sofern nicht passend autorisiert. Keine Servermigration oder Serverbelastung in diesem Paket. Offene Serverpunkte bleiben unter `SERVER_AKTUELL.md` und werden vor produktiver Aurelia-Übernahme vorgelegt.

## Aktueller Prüfnachweis

Erster Ausgangstestlauf: `tests.test_registry`, `tests.test_scopes`, `tests.test_hermes`; 36 Tests, 58 Setup-/Cleanup-Fehler durch verweigerten Windows-Zugriff auf temporäre Verzeichnisse. Identischer Wiederholungslauf außerhalb der Sandbox: **36 Tests in 103,068 Sekunden, OK**, Python 3.12. Kein Produktionscode zur Umgehung dieser Fehler geändert. Die Tests verwenden temporäre Daten und simulierte Modellgrenzen; dies ist keine echte Modell-Evaluation oder vollständige UI-/Hermes-Installationsabnahme.

Selbstprüfung des Plans: bestehende direkte A→B-Funktion nicht doppelt eingeplant; Gruppenplanung nicht mit Gruppenausführung gleichgesetzt; Chat-Reasoning getrennt vom App-Routing; persönliche Sicherung getrennt vom neutralen Release. Kein Gesamtabschluss behauptet. Nächster konkreter Arbeitsschritt: gemeinsame Funktionsabnahme/Besprechung des dokumentierten Hermes-Umfangs; danach getrennte Entscheidung über Aurelia-Adapter und neutrale Windows-Ausgabe.
