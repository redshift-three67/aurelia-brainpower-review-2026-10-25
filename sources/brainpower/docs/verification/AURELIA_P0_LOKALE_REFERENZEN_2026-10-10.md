# Aurelia P0 lokale Referenzen und Ressourcenprüfung

Stand: 10.10.2026. Der Betreiber hat den konsolidierten Phasenplan freigegeben. P0 ist begonnen; die Quellen- und numerischen Referenzprüfungen sind abgeschlossen, die lokale Backend-Machbarkeit ist noch nicht nachgewiesen. P1 ist nicht gestartet.

## Quellen und Versionen

| Anwendung | Gebundener und frisch auf GitHub bestätigter Main-Commit | Dateiabgleich vor und nach den Proben |
|---|---|---|
| Explorer mit Copen/Bohm | c69d5aa224018b0484efd90ae456a10aecc78a77 | 292/292 SHA-256 und Größen gleich |
| Thom | 18e6c12c238985da698f9a46743d893b30d61ba7 | 270/270 SHA-256 und Größen gleich |

Beide npm-Locks sind Version 3; ihre Root-Dependencies und DevDependencies stimmen mit package.json überein. Zusätzlich liegen bun.lock und bun.lockb vor. Kein app-eigener Test-Script und kein node_modules in den beiden Quellkopien. Keine Abhängigkeiten neu installiert und kein App-Build behauptet. Die Rechenproben liefen mit dem vorhandenen Codex-Node v24.19.0; frühere Belege verwendeten v22.22.0. Änderungen der JSON-Belege betreffen ausschließlich Node-Version, Ausführungszeit beziehungsweise reproduzierbaren Befehlsweg; die übrigen Ergebnisfelder sind gleich. Die aktuelle Probe nutzt experimentelle Node-VM/TypeScript-Strip-APIs, keine Festlegung der späteren Produktlaufzeit.

## Frisch ausgeführte Referenzproben

| Probe | Ergebnis | Grenze |
|---|---|---|
| explorer_core_probe.mjs | Wiederholung, synthetische Kontexte, Bildoption und Fibonacci-Grenzen bestanden | Utility-Pfade; feste Testzeit, Hardwaremodulation aus |
| copen-v2-inline-probe.mjs | 378 Vergleiche, 0 Abweichungen | Separate Inline-V2-Formel; keine Gesamt-UI-Abnahme |
| bohm_full_probe.mjs | Kontrollierte vollständige Klientenfunktion und dokumentierte Grenzfälle bestätigt | Hardware ersetzt; leere Vornamen/ungültiges Datum erzeugen im Original nicht endliche Werte |
| thom_core_probe.mjs | Drei Kontexte, begrenzte endliche Dimensionen/Frequenzen, kontrollierte Wiederholung bestanden | Numerischer Enginepfad; keine Storage-, Audio- oder 3D-Abnahme |
| hardware_boundary_probe.mjs | Cachegrenze und bekannte Befunde bestätigt | 15 ausschließlich simulierte HEAD-Aufrufe; kein tatsächlicher HTTP-/GPU-/RAM-Test |

Die Hardwareprobe bestätigt insbesondere, dass der Collector trotz vorhandener All-off-Standardkonfiguration im geprüften Quellpfad simulierte Netzwerkabfragen anfordert. Der dort stets gleiche Zeitkohärenzwert ist kein unabhängiger Uhrenvergleich. Diese bekannten Originalbefunde wurden nicht korrigiert oder als Präzisionsgewinn ausgegeben. Numerische Referenzgleichheit belegt keine gemessene Klientenreaktion.

## Lokaler Dienstumfang und Startgrenzen

| Bereich | Explorer | Thom | Vor tatsächlichem lokalen Start |
|---|---|---|---|
| Quellanwendung | Copen v1/v2/Generator und Bohm gemeinsam | Eigenständige App | Zwei Anwendungen; Modulzahl bestimmt nicht die Backendzahl |
| Anmeldung/Persistenz | Supabase Auth, Tabellen, lokale Browser-/IndexedDB-Daten | Supabase Auth und Tabellen | Neue lokale Identitäten; keine bisherigen Klienten oder Aufträge kopieren |
| Dateien | Private Signaturen-/Bildpfade | Klientenbilder, 3D-Modelle und Tus-Upload | Rechte, lokale Zielbindung, Upload und Löschung real prüfen |
| Ereignisse | Supabase postgres_changes/Channels | Separate WebSocket-Servicepfade | Realtime- und Workerbindungen lokal herstellen und testen |
| Funktionen | harmonization-worker | hardware-metrics, meridian-diagnosis, realtime-sync | Remoteimporte, HTTP/Cron/CLI/Workerziele einzeln binden; keine automatischen Fremdaufrufe |
| Zusätzliche Dienste | Ollama und Hardware-/Latenzpfade | 3D, Web Audio, KI-/Hardware-/Backendpfade | Externe Funktionen deaktiviert/gesondert bewertet; Stubs sind keine Funktionsparität |

Beide Quellen enthalten je 20 SQL-Migrationsdateien. Ihre konfigurierten Projektkennungen sind vorhanden und verschieden; dies ist lediglich ein redigierter Quellkonfigurationsvergleich und kein Nachweis der aktiven Backendidentität oder gegenseitigen Rechteisolation. .env-Inhalte und bestehende Deployment-Secrets wurden nicht gelesen/übernommen. Die vorhandenen Schema-/Workflowbefunde bleiben zusätzlich maßgeblich; Markerzählung ersetzt keine Aufrufpfadanalyse.

Beide Original-Vite-Konfigurationen enthalten host `::` und Port 8080. Nicht unverändert starten. Vorgemerkt: getrennte Loopback-Oberflächen auf 8120/8121, Backendports erst nach konkretem Dienstvertrag und erneuter Listenerprüfung; keine bindende Reservierung durch diese Vormerkung. Cloudschreibfreiheit muss durch Zielbindung UND negative Ausführungsprobe nachgewiesen werden.

## Ressourcenbefund

C: rund 19,04 GiB frei, E: rund 10,19 GiB, F: rund 380,63 GiB bei der Vorprüfung. Windows 10 Enterprise 19045, rund 15,26 GiB sichtbarer RAM; freie physische Speicherwerte schwankten zwischen rund 2,99 und 4,54 GiB. Verfügbarer virtueller Speicher bei der Folgeabfrage rund 6,52 GiB. Das sind Momentaufnahmen, keine Stackkapazitätszusage.

WSL 2.5.9.0, Kernel 6.6.87.2; einzig angezeigte Distribution Ubuntu, WSL2, gestoppt. Zwei Startversuche scheiterten vor Linux-Ausführung mit `Wsl/Service/CreateInstance/CreateVm/HCS/0x800705aa` („Nicht genügend Systemressourcen“), zuletzt mit `/bin/true`. Linux-Ressourcen und dort installierte Containertechnik konnten deshalb nicht geprüft werden. Docker/Podman/Supabase nicht im geprüften PATH, übliche Docker-/Podman-Installationsverzeichnisse fehlen; keine vollständige Installationsinventur behauptet.

Keine .wslconfig vorhanden. Laut [Microsoft WSL-Konfiguration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) liegt der Standard-Memory-Rahmen bei 50 % des Windows-RAM; .wslconfig wirkt global auf WSL2. Das macht einen begrenzten Speicherrahmen zu einer prüfbaren Hypothese, beweist aber nicht die konkrete Ursache des Fehlers. Pagefile-Nutzung meldete 8096 MB zugewiesen, die Konfiguration 4096 MB Anfang/Maximum und AutomaticManagedPagefile=false; diese Diskrepanz bleibt ungeklärt. Eine zusätzliche Performance-CIM-Abfrage hing und wurde über ihre eigene Exec-Session abgebrochen; daraus wurde kein Messwert abgeleitet. Die ergänzende Ereignisabfrage lieferte keinen Fehlerbeleg.

Keine Auslagerungs-, WSL-, Hypervisor- oder Netzwerkparameter verändert; keine fremden Anwendungen beendet, kein Neustart/WSL-shutdown, keine Containerinstallation. Nächster Infrastrukturpunkt: Ressourcenursache weiter eingrenzen und gegebenenfalls einen bytegesicherten, rücknehmbaren WSL-Speicherversuch vorbereiten. Vor Änderung laufende WSL-Verbraucher und Datei-Drift prüfen. Ein erfolgreicher Minimalstart allein ersetzt keine Belastungsprobe der benötigten Dienste.

## Sicherung und bestehender Betrieb

Sicherungspunkt: `runtime/aurelia-three-modules-20261009/reference-plan/p0-preflight-20261010-083915Z`. 15 vorhandene Status-/Plan-/Manifest-/Harness-/Ergebnisdateien vor erneuter Ausführung bytegeprüft gesichert. Der erste Sicherungsversuch brach wegen eines unzutreffenden zusammengefassten Segmenthashes ab; Originale blieben unverändert. Die damalige Historienprüfung verwendete irrtümlich eine feste CRLF-Segmentgrenze statt der ersten Trennzeile. Dadurch blieb ein nachgeordneter Tail unverändert, aber der erste historische Abschnitt fehlte im neuen Statusdokument. Der ursprüngliche Abschnitt war vollständig im before/-Bereich gesichert; die unten dokumentierte Berichtigung stellt die vollständige Historie wieder her. Alte Belege bleiben unverändert und sind bezüglich dieser damaligen Historienaussage fehlerhaft. Aktuelle Belege und Nachträge werden separat in after/ manifestiert; dies ersetzt keine F:-Gesamtsicherung oder Serverwiederherstellung.

Privater Belegbereich: ausschließlich bestehende Benutzer-/SYSTEM-Rechte; keine Lockerung. RadiWorks 8103–8109 und Governor 8787 hatten vor/nach P0 dieselben Listeneradressen und Prozess-IDs. Das ist ein Betriebsschutzbeleg, keine erneute Funktionsabnahme aller Liveinstanzen. Keine Produktformeln, Cloudschemata, Modul_Templates, Governors-Konfiguration oder laufenden RadiWorks-Aufträge geändert.

## Phasenstand und nächste Schritte

| Phase | Stand |
|---|---|
| P0 Quellen und begrenzte Formelreferenzen | Geprüft und gesichert |
| P0 Runtime/Backend/Assets | Dienstumfang erfasst; WSL-Start und tragfähige Ressourcen noch offen |
| P1 lokale Ist-Umgebungen | Nicht gestartet; zuerst Ressourcen, isolierte lokale Ziele und Startgate |
| P2/P3 | Vorhandene Befunde bleiben erhalten; vollständige Workflows und Dienste noch zu prüfen |
| P4–P8 | Gemäß freigegebenem Plan; zentrale DB-Entscheidung und S4.8 separat |

Tatsächliche Helfer: Luna6/max für begrenzten Explorer-Quellen-/Abhängigkeitsabgleich; Astra6/medium für unabhängigen Ressourcen-/Isolationsreview. Beide rein lesend, keine Rohdefinitionen/Datensätze/Secrets an Helfer und keine Rekursion. Runtime-Modell des leitenden Desktopchats nicht aus Defaults abgeleitet. Kein gemessener Tokenvorteil behauptet.

Fortsetzung: [konsolidierter Plan](../superpowers/plans/2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md), [bisherige Referenzprüfungen](../AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md), [Workflowabdeckung](../AURELIA_WORKFLOW_ABDECKUNG_2026-10-10.md).

## Berichtigung der Wiederaufnahme am 10.10.2026

Bei der nächsten Fortsetzung fiel der Segmentfehler auf: Der P0-Nachtrag hatte 966 Bytes des ersten historischen Abschnitts ausgelassen (R6.2/Privatgesamtsicherung abgeschlossen). Gemischte LF-/CRLF-Trennzeilen waren die Ursache. Der alte Prüfnachweis sicherte versehentlich erst die nachgeordnete Historie; die frühere Aussage vollständigen Historienerhalts war deshalb nicht korrekt.

Vor Reparatur aktuellen Kopf und Belege separat gesichert. Der aktuelle Stand entsprach noch exakt dem damaligen after/-Beleg. Aus dem manifestgebundenen before/-Beleg wurden ausschließlich die ausgelassenen historischen Bytes rekonstruiert. Der aktuelle Kopf bleibt bytegleich, die Datei wächst genau um 966 Bytes; die gesamte Historie nach der tatsächlich ersten Trennzeile ist wieder bytegleich zum Original: 291415 Bytes, SHA-256 cc8ab41933c9fb2acf8d48a985c4f840dfc566319b3039038bace91820918533. Verankerte Trennzeilenprüfung für LF, CRLF und gemischte Endungen bestanden. Keine Produktdateien oder bisherigen Sicherungsmanifeste verändert.

Separater Korrektur-/Diagnosecheckpoint: runtime/aurelia-three-modules-20261009/reference-plan/p0-wsl-diagnose-20261010-090106Z. Astra6/medium prüfte die Rekonstruktionsinvarianten unabhängig; die konkrete Byteprüfung erfolgte hier.

## WSL-Folgeprobe und Administratorbefund, 10.10.2026

Die zusätzliche, rücknehmbare .wslconfig enthielt ausschließlich [wsl2]/memory=2GB. Vorher Ubuntu gestoppt, keine vorhandene Konfigurationsdatei; Rücknahme nur bei bytegleichem selbst erstelltem Inhalt. /bin/true scheiterte erneut vor Linux mit HCS/0x800705aa. Die Datei wurde entfernt; WSL_PROBE.json bestätigt Rücknahme, fehlende Konfiguration und unveränderte geschützte Listener. Eine zu hohe Standardspeichergrenze ist damit keine belegte alleinige Ursache.

Die ursprüngliche Ereignisabfrage ohne Fehlerauswertung erlaubte keine Aussage über fehlende Ereignisse. Folgeabfragen ohne Windows-Administratorrechte ergaben ausdrücklich AccessDenied. Nach Betreiberfreigabe liefen zwei reine Administrator-Leseproben per UAC: Speicherwerte, HCS-Inventur und begrenzte Hyper-V-Ereignisse, anschließend gezielt nur Fehlercodes. Keine Einstellungen/Dienste geändert; keine Event-Message, Klientendaten oder Kommandozeilen gespeichert. Die erste Extraktion enthielt bei Worker-Ereignissen keine ResourceFields; die ergänzende XML-Leaf-Auswertung erfasst ErrorCode/HResult ausdrücklich.

Hyper-V-Worker-Admin Event 3110: VM-Partition konnte nicht erstellt werden; dreimal HResult 0x800705AA, unmittelbar zu den drei Startversuchen. Event 3040 meldet Initialisierungsfehler. Compute/VMMS lieferten im begrenzten Zeit-/Levelbereich NoMatchingEventsFound, keine allgemeine Fehlerfreiheit. HCS-Inventur erfolgreich und leer. Konkrete erschöpfte Windows-Ressource bleibt unbekannt; kein Beleg, dass bloß C:-Freiplatz oder WSL-memory die Ursache ist. Keine Reparatur behauptet. Admin-Speichermoment: rund 4,39 GiB physisch und 6,50 GiB virtuell frei; C: zuvor rund 20,35 GiB frei.

Abschlussprobe 09:17 UTC außerhalb der restriktiven Tool-Sandbox: Ubuntu WSL2 Stopped; .wslconfig fehlt; Loopback/PIDs 8103:34332, 8104:67356, 8105:892, 8106:45552, 8107:65368, 8108:35372, 8109:66688, 8787:1776 unverändert. Ein vorheriger Sandbox-Aufruf hatte AccessDenied und ist kein Beleg eines Dienststillstands. Keine erneute Produktfunktionsabnahme daraus ableiten.

Nächster Infrastrukturpunkt: Windows-VM-Ressourcen-/Auslagerungsbefund gezielt klären, anschließend erst Runtime-Entscheidung und Lastnachweis. Kein wiederholter Blindstart, keine Containerinstallation in die unbekannte Ursache. Neustart, globale Dienst-/Auslagerungsänderungen oder Nutzung eines anderen Linuxhosts separat konkret vorbereiten; die Freigabe der Leseprobe umfasst diese Eingriffe nicht. WSL ist ein möglicher lokaler Linuxweg, keine RadiWorks-Abhängigkeit oder Festlegung der späteren Aurelia-Datenbank.

Unabhängig davon Radi144-Einstiege und Writer/Archivgrenzen rein lesend aufgenommen: [P3-Teilerfassung](AURELIA_P3_RADI144_EINSTIEGE_2026-10-10.md). Kein P3-Abschluss, keine neuen Runtime-Tests. Tatsächlich in dieser Folge: Luna6/max Quellenaufnahme, Astra6/medium unabhängiger Historien-/Ressourcenreview; kein Versand von Cloud-Rohdefinitionen oder Datensätzen.

Belege liegen im separaten Diagnosecheckpoint p0-wsl-diagnose-20261010-090106Z: WSL_PROBE_BEFORE.json/WSL_PROBE.json, HISTORY_REPAIR.json, beide Administrator-Scripts und Ergebnisdateien. Alte Manifeste unverändert. Dieser Checkpoint ersetzt keine F:-Gesamtsicherung.

## Priorisierung nach Betreiberergänzung vom 10.10.2026

Weitere WSL-Reparaturversuche vorerst zurückgestellt, unabhängige P3-Referenzaufnahme vorgezogen. Vollständiges Runtimegate vor Explorer-/Thom-P1/P2-Abnahme bleibt unverändert offen. Getrennter Ubuntu-Testrechner als Ausweichrichtung vorgemerkt, ohne Einrichtung oder Server-/Netzwerkänderung. [Varianten und RadiWorks-Nachtrag](AURELIA_P0_ALTERNATIVEN_RADIWORKS_RESTPUNKTE_2026-10-10.md). RadiWorks-Fehler/Usability nur konsolidiert; keine Livekorrektur.
