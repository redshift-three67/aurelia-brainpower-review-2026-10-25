# Aurelia Laufzeitwege und vorgemerkte RadiWorks Korrekturen

Stand 10.10.2026. Die Betreiberanmerkungen sind in den freigegebenen P0–P8-Plan aufgenommen. Unabhängige Modulaufnahme und Referenzprüfungen haben Vorrang; RadiWorks-Korrekturen bleiben ein gesonderter, gesicherter Wartungsblock. In dieser Runde wurden nur Plan-/Statusdateien geändert. R6: alle 200 Produktdateien frisch gegen das gebundene Manifest geprüft, kein Drift; keine neue Runtime-Funktionsabnahme.

## Laufzeitbasis und Reihenfolge

Der WSL-Fehler 0x800705AA stammt aus der Hyper-V-Partitionerstellung. Er meldet fehlende Systemressourcen, benennt aber keine einzelne erschöpfte Ressource. Der Minimalstart scheiterte auch mit vorübergehendem 2-GB-Rahmen; die Konfiguration wurde zurückgenommen. Freier RAM oder bereinigtes C: allein widerlegen/beheben den Fehler nicht. Der vorhandene Pagefile-Widerspruch ist weiterhin ungeklärt. Keine weiteren Blindstarts oder Installationen zur Fehlerumgehung.

| Weg | Bewertung | Voraussetzung und Grenze |
|---|---|---|
| WSL2 gezielt reparieren | Vorgemerkt für eigenes Infrastrukturfenster | Startdiagnostik und RAM-/Commit-/Auslagerungs-/Hypervisorzustand klären; vor etwaigem Neustart Livezustand/Startaufgaben und Rückweg sichern. Keine Reparatur oder Neustartfreigabe aus der Leseprobe ableiten. |
| Getrennter Ubuntu-Testrechner | Bevorzugte Ausweichrichtung bei ausreichenden Ressourcen | Versionierter kompatibler DB/Auth/Storage/Realtime/Functions-/Workerumfang, neue Testidentitäten, getrennte Ziele und Netzwerkgrenzen. Windows-Browser bleibt bedienbar; das wäre selbstgehostetes Testbackend auf anderem Rechner, kein vollständiger Ein-PC-Windowsbetrieb. Noch nicht eingerichtet. |
| Separate Linux-VM auf diesem PC | Zweite Möglichkeit, kein belegter Ausweg | Eigenes Budget und Isolation nachweisen; sie benötigt ebenfalls Hostressourcen. Hyper-V-basierter Containerbetrieb kann dieselbe Problemklasse treffen. |
| Native Supabase-Linuxprozesse | Technischer Kandidat mit zusätzlichem Prüfbedarf | Anbieter bezeichnet native Stackbefehle als experimentell; weniger Projektisolation als Container. Native Windows-Laufzeit nicht unterstützt. Für zwei Anwendungen Containerisolation bevorzugen. |
| WSL1 oder nur PostgreSQL unter Windows | Teilreferenzen möglich; kein Ersatz der vollständigen Backendprobe | WSL1 ohne vollständigen Linuxkernel/systemd; einzelne SQL-/Formeltests belegen weder echte Anmeldung noch Storage, Realtime oder Edge-/Workerparität. |

[Supabase Runtime-Dokumentation](https://supabase.com/docs/guides/local-development/docker-and-native-runtimes), [Selfhosting-Anforderungen](https://supabase.com/docs/guides/self-hosting/docker), [Microsoft WSL-Vergleich](https://learn.microsoft.com/en-us/windows/wsl/compare-versions). Für alle Selfhosting-Komponenten nennt Supabase 4 GB RAM Minimum, 8 GB+ empfohlen und 40 GB SSD Minimum. Das ist keine gemessene Kapazität unserer zwei Apps. Tatsächlich verwendete Dienste nicht entfernen und anschließend volle Funktionsparität behaupten.

Arbeitsreihenfolge: unabhängige P3-Quell-/Workflowaufnahme und begrenzte synthetische Referenzproben vorziehen. WSL-Reparatur vorerst zurückstellen; P0-Runtimegate bleibt offen. P1/P2 für Explorer/Thom erst nach belegtem vollständigem Runtimeweg und Zielisolation; Thom-3D/Oberfläche zusätzlich im Browser prüfen. Danach P3 vervollständigen und P4/P5 gemeinsame Datenstruktur entscheiden. Ein anderer Linuxhost, neue VM oder produktiver Aurelia-Server wird hier nicht eingerichtet/verändert. Bestehende Servergates bleiben bestehen.

## RadiWorks Befunde und spätere Arbeitspakete

Benutzer meldet beide stochastischen Verfahren betroffen: Original startet nach Klick sichtbar nicht; persönlich meldet „Eigene Zufallsquelle oder Katalog derzeit nicht dauerhaft verfügbar.“ Der Auto-Alert stammt im Screenshot von localhost:8109; der Port für die ergänzte Analysebeobachtung ist nicht gesondert bestätigt. Kein Fallinhalt oder Schlüssel wurde gelesen/übernommen.

| Schritt | Punkt und aktueller Befund | Späterer Prüf-/Umsetzungsumfang |
|---|---|---|
| RW-F1 | Auto-Start und Stochastik: Auto verlangt wiederherstellbare Zufallsfolge plus persistierte Auftragsannahme. Letzter Rolloutbeleg vom 08.10: Recoverykey nur8103, übrige8104–8109 ohne. Für8109 plausible Erklärung, keine frische Laufzeitdiagnose. | Pro betroffener Instanz nur Konfigurations-/Speicherfähigkeitsstatus ohne Keyinhalt prüfen; Journal, Commit/Schreibbarkeit, Auto-Auftragsannahme und Start-I/O auseinanderhalten. Vorhandene Schlüssel/Daten erhalten; Schutzsperre nicht umgehen. |
| RW-F2 | Beide stochastischen Analyse-Startpfade: der persönliche 503-Text fasst JournalConfigurationError/OSError zusammen. Normalisierte Katalogsnapshotfehler folgen anderen Ausnahmewegen. Original hat Fehlerstatus-Catch; gemeldete ausbleibende sichtbare Reaktion quellenmäßig nicht vollständig erklärt. | Auf isolierter Fallkopie mit synthetischem Kontext beide Verfahren in beiden Zufallsmodi prüfen: Request/UI-Status, Start, Fehlerrückmeldung, Persistenz und Recovery. Danach zielgenaue Korrektur und verständliche Ursache; keine pauschale Aussage „Katalog kaputt“. |
| RW-U1 | Resonanzliste wirkt im Bild vertikal zu knapp. Renderer zeigt höchstens acht Signaturen nach Trefferanzahl; ein einzelner Eintrag kann auch aus nur einem Resonanzschlüssel entstehen. | Titel/Hilfe kürzen oder einklappen, Leeren-Aktion kompakter, Liste mit ausreichender Mindestfläche und Scrollbereich; GV darunter erhalten. Desktop/Zoom/Reflow/Tastatur, lange Titel und volle Liste prüfen. |
| RW-U2 | Analyse-Tabelle hat Level und GV, bisher ohne Sortierbedienung. | Anzeigeoptionen Originalreihenfolge, Level numerisch L1–L12 auf-/absteigend und GV auf-/absteigend. Fehlende Werte klar behandeln, Originalindex als stabile Zuordnung/Tie-Breaker. Gespeicherte Analyse, feste21er-Zuordnung, HIST/HIT/Trends und Broadcast-Ziel dürfen nicht durch Anzeige-Reihenfolge neu gebunden werden. Persönliche Matrixscores separat, keine künstlichen Original-GV/Lvl ergänzen. |
| RW-A1 | Auto-Broadcastdauer: Entropiezug10–1000s. Multiplikator beeinflusst Resonanzziehung, nicht Dauer; Auto verwendet allow_delta=False. Normales Queue-Ende allein schaltet Auto nicht AUS. | Stop-/Shutdown-, Journal-/Receiptfehler, Startfehler und CopyGuard-Abschaltung anhand technischer Statusursache unterscheiden; verständlichen letzten Abschaltgrund anzeigen. Keine Abschaltung als gemessene Klientenreaktion deuten. |
| RW-A2 | Drei-Stunden-/Dauermodus ist eine zusätzliche Steuerungsfunktion, kein vorhandener stabil abgenommener Vertrag. | Empfohlen zunächst bewusst gestartetes Laufzeitbudget, z.B.3Stunden, mit Ende/Restzeit/Stop und definiertem Fehler-/Restartverhalten. Unveränderlicher Fall-/Katalog-/Auftragskontext, Quotas und Guardregeln erhalten. Auto-Laufzeitbudget und Dauer eines einzelnen Broadcasts getrennt anbieten. Unbegrenzten Dauerbetrieb erst separat bewerten. |
| RW-T1 | Reale Kamera-/Entropieprobe existiert vom04.10: Sammlung und späterer OS-Fallback belegt. Das ist keine erneute R6-/Langlauf-/physikalische Zufallsqualitätsabnahme. | Zielgerät mit aktueller Version, langem Feed/Verbrauch, Quellenwechsel, Ausschöpfung, Stop, Wiederanlauf und dauerhaftem Recovery kontrolliert abnehmen; mehrere isolierte Instanzen einbeziehen. |
| RW-T2 | Start5 0.4.0-rc1/R6.2 technisch geprüft; aktuelle externe Windows10-Abnahme dieser Version bleibt gesondert. | Nach späteren Korrekturen erneute Vier-Modi-/Medien-/Fall-/Stop-/Restartprobe und Betreiberabnahme; dann kontrollierter Rollout, Quell-/Modul_Templates-Abgleich und separat geprüftes Versionspaket. Kein neues Paket in diesem Nachtrag. |
| RW-I1 | Zentraler Daten-/Katalog-/Rechte-/Abo-/Jobvertrag, Ubuntu-/Hostabnahme und S4.8 weiterhin offen. | P4–P8 zusammen mit allen Modulen: Tenantidentitäten, Widerruf, Katalogrevisionen, Archive/Assets/Trends, Worker, Replay, Restore und normativer Adaptervertrag. Lokaler Scope ist keine Hostautorität. |
| RW-O1 | Komfort-Installer zurückgestellt; Kozyrev, zusätzliche externe Hardware/CUDA bleiben optional; Ego Cleaner inaktiv/vorbereitet. Bestehende Audio-/Fünflayer-/GV-/Watchlistfunktionen erhalten. | Keine stille Aktivierung. Systemweite Audio-/Assetfähigkeit und Linux-Parität im späteren Aurelia-Vertrag prüfen, kein erneuter Funktionsersatz. |

B1/B3 sind zusammenhängende, aber nicht bewiesenermaßen identische Fehler. Fehlender Recoverykey kann eine korrekte Sperre auslösen; die unklare oder ausbleibende Nutzerantwort bleibt separat zu behandeln. B2/B4 ändern zunächst nur Darstellung. B5 darf bestehende Originalregeln und Sicherheitsstopps nicht übersteuern. Der Korrekturblock folgt an einem abgeschlossenen P-Prüfpunkt; jetzt keine Livewartung, Produktänderung oder Übernahme.

### Quellbindung der Befunde

R6-Manifest SHA256 445ece8f8c826e1391fead34c9a4c9b271e3b13b6d59a7654f66f11ab77b6275; alle200Einträge frisch hash-/größengleich. Wichtige Pfade relativ zu runtime/rw-r6-release-20261008:

- engine/src/radiworks/api/routes.py:1641–1671 und core/automode.py:172–202: Startguard/Annahme; core/auto_jobs.py:37–48 und entropy_journal.py:175–197,237–251: Persistenz-/Kryptogrenzen.
- engine/src/radiworks/api/personal.py:78–108; core/rates.py:196–228, core/comparison_basis.py:20–38; api/routes.py:958–979; webapp/js/views/analyze.js:420–446: unterschiedliche Fehlerpfade.
- engine/src/radiworks/core/automode.py:204–267,399–441; core/broadcast.py:139–147,344,566–587; main.py:202–203: Auto AUS, Dauer und keep_alive. Die frühe Zwischenhypothese einer Delta-Verkürzung für Auto ist nach Callerprüfung verworfen; allow_delta=False ist maßgeblich.
- webapp/js/views/statusbar.js:97–118; webapp/css/app.css:561–578,616–641: Anzeige/Begrenzung. webapp/index.html:317–319; webapp/js/views/analyze.js:580–610; core/gvround.py:20–21,84–100: Analysezeilen und getrennte GV-Indexfolge.

Luna6/max führte die begrenzte Quellaufnahme durch; Root prüfte Manifestbindung und Plan/Status. Kein neuer Astra-Aufruf: kein neuer Produkt-/Datenbankentscheid und kein verbliebener Widerspruch in diesem Nachtrag. Keine Runtime-/Browser-/Schlüssel-/Klientendaten an Helfer; keine neue Testabnahme behauptet.

## RadiFarben innerhalb P3 bis P8

Access bleibt Originalreferenz. Die aktuelle Metadatenaufnahme bindet49lokale/fünfverknüpfteTabellen,499lokaleFelder und47QueryDefs; Formular-/Modulnamen sind keine Funktionsabnahme. [Bestand](../AURELIA_MODULDATEN_BESTAND_2026-10-09.md).

| Phase | Erforderlicher Umfang |
|---|---|
| P3 | Aktueller VBA-/Query-/Formular-/Timer-/Bericht-/Import-/Exportweg, Parameter/Einheiten und führende Writer; verknüpfte Quellen kontrolliert klären. Reine Inventur führt keine Makros/Autoexec oder externen Links aus. Danach gezielt synthetische Originalreferenzen. |
| P4/P5 | RadiFarben mit sechs weiteren Modulen und Aurelia/Modul_Templates in gemeinsame Bedarfs-/Rechtematrix aufnehmen; erst danach zentrale Struktur entscheiden. Kein automatischer Algorithmus-/Datenersatz. |
| P6/P7 | Versionierte Identität/Kontext/Katalog-/Ergebnis-/Archiv-/Asset-/Adapterverträge, Rechte/Abo und zugängliche UX; fachliche Formeln separat erhalten, lokaler Prototyp mit Referenzgleichheit und Betreiberprüfung. |
| P8 | Windows-/Ubuntu-, Tenant-/Parallelitäts-/Fehler-/Restore- und Integrationsabnahme. Accessdatei ist kein direkt integrierbarer Ubuntu-Modulbackendvertrag. |

[Hauptplan](../superpowers/plans/2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md) bleibt maßgeblich. Keine DB-Strukturentscheidung, Gates oder Modul_Templates in dieser Nachtragsrunde geändert. Dokumentensicherung vor Änderung und Rückleseprüfung im Diagnose-/Planbereich; keine neue F:-Gesamtsicherung.


## CopyGuard Ergänzung vom 11.10.2026

Neue Betreiberanforderung: Erklärung der vorhandenen Textregeln, Einordnung des Auto-Fehlerbilds und Admin-Testschalter. Wartungsreihenfolge ergänzen: RW-C1 zusammen mit RW-F1/F2, dann RW-C2/C3 vor späterem Rollout-/Paketabgleich. [Quellbeleg und Testmodusentwurf](RADIWORKS_COPYGUARD_ADMIN_TEST_PLAN_2026-10-11.md). P0–P3 bleiben vorrangig. Kopierte Originalrate und auslösende Regel aus dem Bild nicht bekannt; keine Rootcause oder Bypassaktivierung behaupten. Recovery-/Stochastikfehler bleiben getrennt. Alle200R6Produktdateien vor/nach Planpflege manifestgleich; sieben synthetische Lexikon-/Projektionsproben bestanden, keine Liveprobe. Historische Wiederaufnahme und Dokumente separat gesichert.
