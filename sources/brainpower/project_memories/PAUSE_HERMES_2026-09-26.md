# Wiederaufnahmepunkt — Hermes-Pause am 26.09.2026

Der Betreiber hat eine Pause und einen persönlichen Wiederherstellungspunkt angefordert. Vor dem regulären Stoppen des Governors gab es keine eingereihten, laufenden oder auf Antwort wartenden Aufträge. Automatische Modellreviews waren aus; die lokale Beobachtung war an. Während der Pause keine neue Modellsendung, Produktänderung oder Serverarbeit starten.

## Aktueller Hermes-Stand

- Beide ausdrücklich gewählten Modellwege lesen die ausgewählten `project_memories` bei Einzelprojekt-Reviews/-Plänen vollständig und prüfen Inventar sowie SHA-256 vor dem Modellversand. Zu große Kontexte stoppen ohne Kürzung. Das alte Hermes-Sitzungsgedächtnis ist deaktiviert; das Governor-Projektgedächtnis ist die Quelle.
- Route-B-Matrixpläne verlangen jetzt Sol 6/xhigh, Luna 6/max und eine unabhängige Astra-6/medium-Prüfung. Neue Strategieübernahmen aus Route B verlangen deren Beleg. Der alte Terra-/Supervisor-Weg bleibt wählbar.
- Der echte RadiWorks-Vergleich auf identischem Scope-Hash `9a07a4dc02dc9696cc12cbde95f23972737ff690f2b548a6b31ac95db153d917` verwendete in beiden Wegen dieselben zwei vollständigen Gedächtnisdateien. Altauftrag `50c263da44484d588da1ef064bcd38b3`: 40.563 Tokens; Route B mit ausdrücklich gewähltem Astra `643cd2d8985b43518eee0b86ed3ca457`: 65.535 Tokens. Beide wurden mit `stale=false` gespeichert; ein frischer Scan bestätigte den Hash. Das begründet keine allgemeine Qualitäts- oder Kostenrangfolge. Details: `docs/verification/HERMES_MEMORY_2026-09-25.md`.
- 76 gezielte Python-Tests, Route-B-UI-Test, JavaScript-Syntax und JSON-Vertrag bestanden. Der Governor wurde nach den Änderungen neu gestartet und war vor dieser Pause erreichbar; automatische Reviews blieben aus.

## Noch offen

Die fünf vollständigen Projektgedächtnisse überschreiten die aktuelle Gruppenkontextgrenze. Gruppenaufträge werden sicher abgewiesen; die beleggebundene Mehrstufenverarbeitung ist entworfen, aber nicht implementiert. Daher keine vollständige Gedächtnisabnahme der Gesamtmatrix behaupten. Eine fachliche Genauigkeitsrangfolge benötigt mehrere vorab bewertete Fälle. Hermes-Funktionsabnahme, RadiWorks → Radi144 → `morphic_v1` → neuer Modulprototyp und erst danach der Produkt-Matrixplan/Aurelia-Integration bleiben in der vereinbarten Reihenfolge offen. Serverrestpunkte bleiben im Serverbericht dokumentiert.

Persönlicher Checkpoint: `checkpoints/Hermes-20260926-Pause/`. Er enthält den lokalen Workbench-Stand und das Journal nach regulärem Governor-Stopp; keine externen Produkt-Repositories oder Serverabbilder. Bei Wiederaufnahme zuerst `RESTORE.md` und `VERIFY.json` dieses Checkpoints lesen und den aktuellen Zustand prüfen. Nichts automatisch zurückspielen oder freigeben.
