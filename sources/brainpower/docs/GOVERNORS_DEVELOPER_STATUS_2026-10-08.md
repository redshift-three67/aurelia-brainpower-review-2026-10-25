# Governors/Hermes – Entwickler- und Sicherungswegweiser

Stand 08.10.2026. Dieser Bericht beschreibt den lokalen Projektstand. Konfiguration, Transportprüfung, Reviewentscheidung und Produktfreigabe sind getrennte Nachweise. Historische Einzelberichte bleiben erhalten.

## Wirkmechanismen, Routen und Gedächtnis

Governors ist die additive lokale Python-Standardbibliothek-/Vanilla-JS-Workbench in `governor_workbench`: Loopback, Host-/Origin-/Session-/CSRF-Prüfung, begrenzter Auftragsworker und SQLite-Journal. Projektübersichten halten Quellenhash, Reviewfrische, Gates, Aufnahme- und Strategieentscheidungen getrennt. Modelltext wird nicht als Befehl ausgeführt. Diese Sicherung aktiviert keine automatischen Reviews. Entwickler lesen `README.md`, `docs/DEVELOPER_GUIDE.md`, `docs/LLM_OPERATING_CONTRACT.json` und `docs/GOVERNOR_0_5.md`.

| Route | Rollen und überprüfbarer Bezug |
|---|---|
| Codex-Chat B | Betreiberwahl GPT-6.1 Sol/high; GPT-6 Luna/max für begrenzte Workerarbeit; GPT-6 Astra/medium für unabhängige Prüfung wesentlicher Entscheidungen. Gespeicherte Profile beweisen keine aktive Desktop-Modellauswahl. Im aktuellen R6.2-Block wurden Luna für Start5 und Astra für Paket-/Archivprüfung tatsächlich eingesetzt. Keine gemessene Einsparquote. |
| Hermes manueller Hybrid | Terra5.6/medium mit ausdrücklich gewähltem Supervisor. Historische Transportprobe am 04.10.; heute keine neue Live-Modellprüfung. |
| Hermes Route B | Sol6/high, Luna6/max, Astra6/medium nach Anwendungsvertrag; Auswahl pro Auftrag. Historische synthetische Transportprobe am 04.10. einschließlich Astra, REVIEW_ONLY/null Werkzeug. Die Chatwahl 6.1 migriert Hermes nicht. |

Routenbelege: [Chatvorlage](CODEX_CHAT_VARIANTE_B.md), [Transportprüfung 04.10.](verification/ROUTEN_KONSOLEN_KAMERA_2026-10-04.md), [Anwendungsabschluss](HERMES_APP_ABSCHLUSS.md).

Gedächtnis: `project_memories` werden auftrags- und quellhashgebunden gelesen. Texte über 95.000 Zeichen werden mit beleggebundenen Abschnitten, mindestens zwei lesenden Rollen und begrenzten Schlussbelegen verarbeitet. Cachebindung umfasst Quellenhash, Modell, Reasoning und Regelversion; Drift oder fehlende Belege sperren. CAS-/Frischebindung und Revisionen trennen Entwurf, Prüfung, Strategieübernahme und Ausführungsrecht. Abschnittsabdeckung belegt Herkunft und Transport, keine semantische Vollständigkeit. [Gedächtnisstufen](verification/HERMES_MEMORY_STAGES_2026-09-26.md).

## Aurelia-Matrix und RadiWorks

Die Governor-Matrix zeigt Quellen, Reviewfrische und Gates. Sie ist keine fertige Aurelia-Laufzeitverwaltung. Mandantenrechte, Abos, Modul-/Jobrechte, Quotas, zentrale Katalogverwaltung und Linux-Hostintegration benötigen den gesonderten Plattformvertrag. Keine automatische Ausführungs- oder Integrationsfreigabe aus einem Review.

RadiWorks R6: `runtime/rw-r6-release-20261008`, 200 manifestierte Produktdateien, SHA-256 `445ece8f8c826e1391fead34c9a4c9b271e3b13b6d59a7654f66f11ab77b6275`; separater Servicewrapper. Kanonischer Quellordner und drei additive Modul_Templates-Referenzen sind synchronisiert. Sieben persistente Prozesse 8103–8109 verwenden getrennte Homes/Scopes; 8112 bleibt der Kandidat. Physische Tonabnahme für feste Frequenzen/Solfeggio und Rosa Rauschen wurde vom Betreiber bestätigt. [Dauerinstanzen](verification/RADIWORKS_R6_DAUERINSTANZEN_2026-10-08.md), [Quell-/Templateabgleich](verification/RADIWORKS_R6_SOURCE_TEMPLATE_SYNC_2026-10-08.md).

Start5 0.4.0-rc1 ist separat gebaut und technisch geprüft: 18.574 Payload-Dateien, vollständige SHA-/CRC-Prüfung, fünf getrennte Instanzen mit je 123 Datenbanken, geordneter Stop/Restart mit Fall-/Schlüsselerhalt und alle vier Verfahrens-/Zufallskombinationen auf einem unveränderten 13-Raten-Katalog. Stochastik nutzte einen nicht erschöpften synthetischen Ganzzahlfeed; keine reale Kamera- oder neue Hörprobe. [Paketbericht](../runtime/rw-r6-portable5-20261008/REPORT.md). Auch das alte 0.3-Paket wurde frisch separat gestartet und beendet. Seine frühere Betreiberabnahme auf einem zweiten PC ersetzt keine neue Zweit-PC-Abnahme für 0.4. Die bestehende lokale Schlüsselablage `LOCALAPPDATA/RadiWorks/Portable5-0.3.0-rc1/keys` bleibt aus Kompatibilitätsgründen bestehen; 0.3 und 0.4 teilen auf demselben PC die instanzbezogenen Schlüssel. Keine bestehenden Fälle oder Schlüssel gehören ins verteilbare Paket.

Kontrolle am 09.10.2026: Dauerinstanzen 8103–8109 mit unveränderten PIDs erreichbar; Kandidat 8112 ohne Listener, HTTP-Verbindung abgelehnt und bisheriger PID nicht vorhanden. In diesem Paket-/Sicherungsblock weder beendet noch neu gestartet; Ursache nicht belegt.

Aurelia S4.8 bleibt **0 % / keine Freigabe**. Radi144 und RadiMorphic behalten ihre eigenen Engines und Algorithmen; gemeinsame Oberfläche ersetzt keinen Modul-/Hostvertrag. Nächster Entscheidungsblock nach RadiWorks-Abnahme ist die ausführliche Datenbankstrukturplanung. [Projektmatrix](AURELIA_CROSS_PROJECT_STATUS_2026-10-08.md).

## Private Sicherung und Wiederaufnahme

Deklarierter Governors-Umfang: Brainpower inklusive Quellcode, Prüfungen, Laufzeit- und Portableartefakten; externes Governors; Obsidian; Hermes-Zustand/Settings/SOUL/Memories/Sessions/SQLite; historische Governance-Snapshotdaten; Codex-Konfiguration/Auth/native Rollen/SQLite/Sessionhistorien/Memories/Skills; `.agents/skills`; CC Switch einschließlich Desktopzustand; lokale SSH-Konfiguration/Schlüssel; vorhandene `E:/Aurelia-Recovery`; tatsächlicher lokaler Portable5-Schlüsselroot. Private Schlüssel, Auth- und Falldaten nur in Owner/SYSTEM-geschützte F:-Archive, niemals ins Testpaket oder an Modelle.

Neue Archive werden unter `F:/Hauptprojekt/Governors/<Zeitstempel>` und `F:/Hauptprojekt/Aurelia/<Zeitstempel>` erstellt. Abschlussbericht nennt erst nach vollständiger Rückleseprüfung die fertigen Pfade. SQLite wird einzeln per Online-Backup und `integrity_check` gesichert; WAL/SHM nur nach belegtem Snapshot ausgelassen. Veränderliche Sessionlogs sind zeitgestempelte Präfixe oder Momentaufnahmen. Stabile Quellen werden auf Drift geprüft. Keine gemeinsame atomare Momentaufnahme, kein gesamtes Profil-/Windows-Abbild und kein frischer Remote-Ubuntu-Export. Lokale Serverkonfigurationen und Beschreibungen sind enthalten; der tatsächliche Remotezustand ist dadurch nicht frisch verifiziert.

Generierte Venvs, Node-Abhängigkeiten, Caches, aktive nicht wiederherstellbare Locks und die bekannte unlesbare historische Reviewquelle stehen in `OMISSIONS.json`. Fehlende Pflichtquellen oder Fehler verhindern COMPLETE. Vor Wiederherstellung `COMPLETE.txt`, `VERIFY.json`, `MANIFEST.jsonl`, `SOURCE_STATE.json`, `OMISSIONS.json` und Restoreanleitung prüfen; heutige Daten zuerst sichern und Writer kontrolliert stoppen. Ein sauberer Shutdown kann offene persönliche-/Watchlist-Aufträge unterbrechen; kein automatisches Replay. Normale Fortsetzung benötigt keine Rückkopie. [Archivplan](../runtime/rw-r6-archive-20261008/PLAN.md).

Die exakt bekannten RadiWorks-Datenhomes 8103–8109 und 8112/home einschließlich ihrer Laufzeit-Settings sind zeitgestempelte Einzelaufnahmen. Spätere Änderungen/Neuanlagen werden offengelegt, bilden aber keinen gemeinsamen vollständigen Endzustand. Produktquellen und sonstige Konfiguration/Gedächtnisse behalten die strenge Driftprüfung.
