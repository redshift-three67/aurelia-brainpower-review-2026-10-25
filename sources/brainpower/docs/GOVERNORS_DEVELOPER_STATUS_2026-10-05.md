# Governors/Hermes — aktueller Entwickler- und Sicherungswegweiser

Aktuelle Betreiberbestätigung: Portable5 funktioniert auf dem zweiten PC nach Vorgabe. Neue Vektor-/Broadcast-/Datenvertragsgrenzen und frische Prüfungen: [aktueller Restplan](verification/RADIWORKS_VEKTOR_DATENVERTRAG_RESTPLAN_2026-10-05.md). Historische offene Zweit-PC-Angaben unten sind dadurch überholt; weitere C3-/Host-/Kamera-Gates bleiben getrennt. Diese Zusatznotiz ist noch nicht in den abgeschlossenen F:-Archiven.

Stand: 2026-10-05T16:49:30.117232+00:00. Dieser Bericht beschreibt den lokalen Stand, keine Produktfreigabe. Historische Einzelberichte bleiben Evidenz; sie gelten nur soweit Quellen und Beleggrenzen unverändert sind.

## Wirkung, Routen und Gedächtnis

Governors ist die lokale additive Python-Standardbibliothek-/Vanilla-JS-Workbench in Brainpower/governor_workbench. Loopback, Host/Origin/Session/CSRF, ein begrenzter Auftragsworker und SQLite-Journal. Projekt-/Gruppenübersichten halten Quellenhash, Reviewfrische, Gates, Aufnahme-/Strategieentscheidungen getrennt. Modelltext wird nie als Befehl ausgeführt; automatischer Review ist nicht durch diese Sicherung aktiviert. README.md, DEVELOPER_GUIDE.md, LLM_OPERATING_CONTRACT.json und GOVERNOR_0_5.md erklären die Verträge.

| Route | Rollen | Verifikation / Grenze |
|---|---|---|
| Codex-Chat | Betreiberwahl Sol6.1/high; Luna6/max für begrenzte Workerarbeit; Astra6/medium für kritische Entscheidungen/ungeklärte materielle Widersprüche | Nicht dieselbe Routinginstanz wie Hermes. Gespeicherte TOML ersetzt keine aktive Desktopwahl. In diesem Sicherungsblock Luna-Quell-/Dokumentarbeit und Astra-Archivreview tatsächlich eingesetzt. Keine gemessene Einsparquote. |
| Hermes alter manueller Hybrid | Terra5.6/medium plus bewusst gewählter Sol-/Astra-Supervisor | Lokale manuelle Einzelreview-Teilabnahme; Transportprobe 04.10 mit Terra5.6/medium + Sol5.6/medium. |
| Hermes RouteB | Sol6/high + Luna6/max, Astra6/medium bei Bedarf / expliziter Prüfung; neuer Matrixplan mit unabhängiger Pflichtprüfung | Auswahl je Auftrag. Synthetische Transportprobe 04.10 einschließlich Astra bestanden, REVIEW_ONLY/null Werkzeug. Keine Migration der Anwendung auf6.1 durch Chatwahl. |

Maßgebliche Routenbelege: [aktuelle Chatvorlage](CODEX_CHAT_VARIANTE_B.md), [04.10-Transport/Windows/Kamera](verification/ROUTEN_KONSOLEN_KAMERA_2026-10-04.md), [Anwendungsabschluss](HERMES_APP_ABSCHLUSS.md). Fünf synthetische Modellaufrufe belegen Transport, keinen allgemeinen Genauigkeits-/Kostenvergleich.

Gedächtnis: project_memories werden pro Auftrag quell-/hashgebunden gelesen. Große Texte über95.000Zeichen laufen über beleggebundene Abschnitte, mindestens zwei lesende Rollen und begrenzte Schlussbelege. Cache nur bei gleichem Quellenhash/Modell/Reasoning/Regelversion; Drift/fehlende Belege sperren. CAS-/Frischebindung und Revisionen trennen Entwurf, Prüfung, Strategieübernahme und Ausführungsrecht. Abschnittsabdeckung beweist Herkunft/Transport, keine semantische Lückenfreiheit. [Gedächtnisstufen](verification/HERMES_MEMORY_STAGES_2026-09-26.md).

## Aurelia und RadiWorks

Aktuelle RadiWorks-Produktbytes: runtime/rw-c23-fixed-release-20261005, 131 manifestierte Dateien plus separater Wrapper. Kanonischer RadiWorks-Quellordner jetzt131/131SHA-gleich; drei Modul_Templates-Nachträge additiv übernommen. Sieben Dauerinstanzen8103–8109 erhalten eigene Homes/Scopes/Fälle; Tasks unverändert. [Quellabgleich](verification/RADIWORKS_SOURCE_TEMPLATE_SYNC_2026-10-05.md), [C23/Portable5](verification/RADIWORKS_C23_PORTABLE5_ABSCHLUSS_2026-10-05.md).

Portable5 0.3.0-rc1 enthält CPython/Libraries/Quellen/Katalog, keine bestehenden Fälle/Keys. Lokale fünf Instanzen/Originalanalysen/21erGV/21×80000CPU/Stop/Restart geprüft; Windows10/11x64 + MicrosoftVC++v14x64 nötig. Zweit-PC-/persönliche Abnahme offen. Produktlizenzzuordnung vor öffentlicher Weitergabe prüfen.

Governor-Matrix ist beobachteter Quellen-/Review-/Gatezustand, kein fertiger Aurelia-Produktmatrixplan. Reihenfolge nach RadiWorks-Abnahmen: Radi144 → morphic_v1 → neues separat aufgenommenes Modul (RadiFarben noch optional/unregistriert) → vollständiger Matrixplan → gesonderte Gates/Integration. Gemeinsames Design betrifft nur Oberfläche/Usability, unterschiedliche Modulakzente; keine Gleichsetzung der Engines. Aurelia S4.8 bleibt0%Freigabe, G0/AUDIT-02/Hostrechte/Quotas separat. [Plattformbericht](AURELIA_CROSS_PROJECT_STATUS_2026-10-05.md).

## Vollsicherung und Wiederaufnahme

Deklarierter Governors-Umfang: Brainpower mit Quell-/Prüf-/Laufzeit-/Portableartefakten; externes Governors; Obsidian-Vault; Hermes-local-state/config/SOUL/memories/sessions/SQLite; .hermes; historische Governance-Snapshotdaten; Codex-Konfigurationen/native Rollen/Auth/SQLite/Sessionhistorien/Memories/Skills; .agents/skills; CCSwitch-Konfiguration/SQLite/Backups; DesktopCCSwitch; lokaleSSH-Konfiguration/Keys; vorhandene E:/Aurelia-Recovery-Kustodiedaten. **Private Auth-/Schlüsseldateien nur in geschütztem Archiv, niemals als LLM-Kontext oder Testpaket.** Kein frischer Remote-Server-Export, kein gesamtes C:/Profilimage.

Archive direkt F:/Hauptprojekt/Governors und F:/Hauptprojekt/Aurelia, Zeitstempel; Owner/SYSTEM-ACL vor Payload. SQLite konsistent per Online-Backup/integrity_check, zugehörige WAL/SHM/Journal nur nach nachgewiesenem Snapshot auslassen. Sessionlogs als zeitgestempelte komplette Präfixe. Stablecode/config/memories: Driftprüfung; alle archivierten Bytes SHA-Rückleseprüfung. Mehrere Quellen nicht atomar; keine pauschale Gesamt-Recovery-Garantie. Generierte .venv/node_modules/caches und bekannte unlesbare historische Einzelquelle explizit OMISSIONS.json; Reinstallation/Portablelaufzeit separat. Ein fehlendes Pflichtroot blockiert COMPLETE.

Erst COMPLETE.txt + VERIFY.json + MANIFEST.jsonl + SOURCE_STATE.json + OMISSIONS.json lesen. Vor Restore Writer/Tasks stoppen, heute veränderte Daten zuerst sichern, keine alten Fälle/DB/Keys über neue. Unterbrochene Aufträge nicht automatisch wiederholen. Abschlussreceipt/Pausennotiz nennt tatsächliche aktuelle F:-Pfade und Prüfergebnisse. Bei normaler Fortsetzung nichts zurückkopieren: aktuellen Livezustand/Hashes lesen, private Zweit-PC-/C3-Abnahme besprechen. Keine neue automatische Modellarbeit/Modulfreigabe durch Wiederaufnahme.
