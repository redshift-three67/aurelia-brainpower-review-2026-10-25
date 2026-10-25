# Gesamtmatrix Hermes / Aurelia – Stand vor T1

Stand 20.09.2026, vor Beginn der genehmigten T1-Implementierung. Diese Fassung bleibt als Ausgangsstand erhalten; spätere T1-Ergebnisse werden separat berichtet.

## Lesart der Prozentangaben

100 % heißt: der ausdrücklich genannte begrenzte Schritt ist dokumentiert abgeschlossen, nicht das gesamte Produkt. 0 % heißt: Umsetzung dieses konkreten Schritts noch nicht begonnen/nachgewiesen. Bereiche mit Spannen sind grobe fachliche Schätzungen, keine gemessenen Arbeitsstunden. Offen = rechnerischer Rest. NB = nicht belastbar bezifferbar; fehlende Belege sind nicht gleichbedeutend mit fehlender Entwicklung.

Die frühere Schätzung von 90–95 % für den begrenzten Hermes-Pilot vermischte abgeschlossene Pilotabnahme und allgemeine App-Restarbeiten. Hier werden sie getrennt: Pilotumfang abgeschlossen, allgemeine Erweiterungen weiterhin offen. Kein gewichteter Gesamtprozentsatz, da Umfang und Aufwand der Produktintegration noch nicht vollständig festgelegt sind.

## H – Hermes / Governor

| Schritt | Erledigt | Offen | Belegter Umfang / nächste Arbeit |
|---|---:|---:|---|
| H01 Lokale Anwendung und geschützte API | 100 % | 0 % | Loopback, Sitzung/Origin/CSRF, lokales Journal, begrenzter Worker im bestehenden Umfang geprüft; historische Abnahme, kein frischer Gesamttest heute. |
| H02 Register, Aufnahme, Quellenbindung, Plan-/Strategiefunktionen | 100 % Funktion | 0 % Funktion | Technische Funktionen vorhanden. Aktuelle fachliche Annahme/Strategie und Quellfrische sind eigene Entscheidungen, kein Funktionsabschlussbeleg dafür. |
| H03 Hermes-/Supervisorrouting | 100 % bestehendes Profil | 0 % bestehendes Profil | Terra plus separater Sol/Astra, Medium, Nullwerkzeuggrenze dokumentiert; heutiger Laufzustand nicht abgefragt. |
| H04 RH-1 optionale Auswahlharmonisierung | 0 % Umsetzung | 100 % | Geplant, zurückgestellt; keine automatische Low-/High-Umstellung. |
| H05 Kontext-/Verbrauchsdarstellung und Tokeneffizienzregeln | 90–95 % | 5–10 % | Umsetzung und Prüfungen dokumentiert; vollständige aktuelle Bedien-/Verbrauchsabnahme nicht hier neu nachgewiesen. |
| H06 Windows-Prozessbesitz und festes local_probe | 100 % enger Umfang | 0 % enger Umfang | Eigene Prozesszuordnung, Start/Prüfen/Stop, keine PID-Übernahme; kein allgemeiner Linux-/Produktlauncher. |
| H07 Vorgängerdiagnose und fachliche Abschlussbelege | 100 % enger Umfang | 0 % enger Umfang | Gebundene clarify/review-Abnahmen, Rücknahme und transitive Entwertung. |
| H08 Eigenständige Testabschlüsse | 100 % enger Umfang | 0 % enger Umfang | Isolierter unittest-Adapter, Quellen-/Adapter-/Auswahlbindung, neuester Versuch maßgeblich. |
| H09 Fehlerdiagnose und begrenzte Reparaturkette | 100 % Pilot | 0 % Pilot | Explizite Diagnose/Plan/Test/Übernahme/Rollback nachgewiesen; keine universelle autonome Reparatur. |
| S1a Vorschau begrenzter Prüffolge | 100 % | 0 % | Gebundene schreibfreie Vorschau. |
| S1b Reservierung und Journal | 100 % | 0 % | Unveränderliche Zustimmung, exklusiver Platz, Unterbrechung ohne Replay. |
| S1c Ausführung/API/UI der Prüffolge | 100 % | 0 % | Test/Review/Nachweis, ausdrücklicher Start und Halt vor Übernahme. |
| S2a Testkettenvorschau | 100 % | 0 % | Zwei bis fünf ausgewählte Tests, echte Vorgängerbindung. |
| S2b/S2c Journal, Worker und Bedienung | 100 % | 0 % | Genehmigte reine Testketten im isolierten Profil abgenommen. |
| S3a Vorschau abhängiger Änderungen | 100 % enger Umfang | 0 % enger Umfang | Direkte unabhängige A→B-Kette. |
| S3b Änderungsjournal | 100 % enger Umfang | 0 % enger Umfang | Unveränderliche Übergangsbelege und aktuelle Spitze. |
| S3c C1 geordnete Rücknahme | 100 % enger Umfang | 0 % enger Umfang | B vor A; keine Wiederverwendung alter Zustimmung nach Rücknahme. |
| S3c C2 erster Übergang | 100 % enger Umfang | 0 % enger Umfang | Eigene Baseline und H0-/H1-Bindung. |
| S3c C3a Nachfolgervorschau/-zustimmung | 100 % enger Umfang | 0 % enger Umfang | Frische Voraussetzungen und eigene Zustimmung. |
| S3c C3b B-Vorschlag/Tests/Review/Abschluss | 100 % enger Umfang | 0 % enger Umfang | B besitzt eigene Nachweise; keine Testvererbung. |
| S3c C4 API/UI und begrenzte Gesamtabnahme | 100 % enger Umfang | 0 % enger Umfang | 18.09.: 659 Tests, 657 bestanden, zwei Skips; JS/Browser geprüft. Kein neuer Lauf heute. |
| H10 Allgemeine Produktadapter und produktübergreifende Ausführung | 20–35 % | 65–80 % | Infrastruktur/Pilot vorhanden; reale projektspezifische Adapter und allgemeine Kettenabnahme fehlen. |
| H11 Mehrgruppen-/Vault-Abnahme im realen Gesamtbetrieb | 40–60 % | 40–60 % | Grundfunktionen vorhanden; nicht als durchgängige Abnahme aller Gruppen/Module belegt. |
| H12 Fremder Windows-PC: vollständige Erstinstallation | 20–30 % | 70–80 % | Installationsgrundlagen vorhanden, vollständiger sauberer Fremdrechnernachweis offen; nachrangig. |

## I – Ubuntu, Sicherheit, Backup und Recovery

Aktualitätsbasis: Infrastrukturbelege vom 18./19.09., heute kein erneuter Serveraudit. Die Gate-Tabelle vom 19.09. enthält ältere Zwischenstände; spätere Root-/EFI-/Schlüsselnachweise haben Vorrang.

| Schritt | Erledigt | Offen | Nachweis / verbleibende Grenze |
|---|---:|---:|---|
| I01 Ubuntu 24.04 und vorhandenes Speicherlayout | 90–95 % | 5–10 % | Ubuntu 24.04.5, RAID1/LUKS2/LVM beobachtet; historische Installationsprovenienz und Planabweichungen einordnen. |
| I02 Desktopstart | 100 % beobachteter Fix | 0 % Fix | GDM/graphical.target korrigiert und bestätigt; keine allgemeine Ausfallsicherheitszusage. |
| I03 SSH/WireGuard/Firewall | 85–90 % | 10–15 % | Aktive Regeln und gehärtete SSH-Kontexte geprüft; IP-unabhängiges Schlüssel-SSH ausdrücklich gewünscht, Abweichung zum alten VPN-only-Plan dokumentieren. |
| I04 Entwicklungsidentität und Rechte | 60–75 % | 25–40 % | Begrenzte negative Zugriffstests; vollständige Rechte-/Datenisolation noch nicht abgenommen. |
| I05 Sicherheitsdienste, Zeit, Health | 70–80 % | 20–30 % | Dienste aktiv, Zeit synchron, keine fehlgeschlagenen Units beim Check; vollständige Alert-/Update-/Soakabnahme offen. |
| I06 Hardware/Firmware/ECC/Secure Boot/USV | 35–50 % | 50–65 % | Inventur/RAID vorhanden; Secure Boot aus, ECC nicht belegt, weitere Betriebsnachweise offen. |
| I07 NVIDIA-Treiber | 85–95 % | 5–15 % | Root-NVML funktioniert; Einsatz unter vorgesehener Dienstidentität und modulspezifische Belastung offen. |
| I08 CUDA-/GPU-Modulbetrieb | 0 % dieses Pakets | 100 % | Keine Toolkit-/Produktfreigabe oder CUDA-Funktionsabnahme aus NVML ableiten. |
| I09 PostgreSQL-Basis | 60–75 % | 25–40 % | Cluster vorhanden, frühere Loopback-/Checksum-Prüfung; absichtlich down, konkrete Daten-/Restoreabnahme später. |
| I10 SMB-Anmeldung und verschlüsselter Transport | 100 % Test | 0 % Test | k213487, SMB 3.1.1/seal nachgewiesen; kein Dauerbetrieb daraus ableiten. |
| I11 Synthetischer NAS-Backup-/Restoretest | 100 % Test | 0 % Test | Vier Dateien, Vollprüfung, unabhängiger Hash-/Modusvergleich. |
| I12 Begrenztes Konfigurationsbackup | 100 % benannter Satz | 0 % benannter Satz | Archiv zurückgelesen; Firewall und Grafikstart ergänzend gesichert. Künftiges Skript muss vollständige Pfadauswahl enthalten. |
| I13 Externe Restic-Schlüssel- und LUKS-Headerkopien | 100 % Kopienprüfung | 0 % Kopienprüfung | E:/F: hashgleich geprüft; Medienverschlüsselung Betreiberangabe. Kein vollständiger Restoretest. |
| I14 EFI-Dateivergleich | 100 % Vergleich | 0 % Vergleich | Acht Dateien identisch; beide Dateisätze vollständig. |
| I15 Boot je NVMe / tatsächliche Recovery | 40–55 % | 45–60 % | Dateinachweise/Headersicherung vorhanden; Wartungsfenster, getrennte Bootpfad-/Recoveryproben offen. |
| I16 Unabhängiger KVM-/Virtual-Media-Recoveryweg | 40–60 % | 40–60 % | KVM nutzbar; kompletter unabhängiger Recoveryboot nicht belegt. |
| I17 Produktiver Backup-Dauerbetrieb | 35–45 % | 55–65 % | Grundweg bewiesen; Timer, Umfang, DB-Konsistenz, RPO/RTO, Retention, Alarmierung und Vollrestore fehlen. |
| I18 Zweiter unabhängiger Sicherungssatz/SMB | 0 % zusätzlicher Dienst | 100 % | Option besprochen, nicht eingerichtet. Zwei Schlüsselkopien sind keine zwei vollständigen Sicherungssätze. |
| I19 Lokaler Arbeitsstand-Snapshot | 100 % Snapshot 19.09. | 0 % dieser Kopie | D:/Aurelia/_Snapshots/Hermes_Aurelia_2026-09-19_23-46-38; 3147 Dateien geprüft, SQLite ok. Kein Serverimage; Auslassungen dokumentiert. |
| I20 Gesamtbaseline G0-SRV | NB | NB | Einzelbelege vorhanden, keine Gesamtfreigabe. Historische G0-0 bis G0-12 nicht automatisch freigegeben. |

## A – Aurelia-/Modulvertrag und Integrationsprüfungen

| Schritt | Erledigt | Offen | Stand / nächste Arbeit |
|---|---:|---:|---|
| A01 Quellenabgleich der Integrationsvoraussetzungen | 100 % gezielter Abgleich | 0 % dieses Abgleichs | ABI, Templates, Manifest und dokumentierte Gateabweichungen verglichen; kein Vollaudit aller Produkte. |
| A02 Richtung separates REST-Profil | 100 % Richtungsentscheidung | 0 % Richtung | Vom Betreiber angenommen; Python/WASM bleibt getrennt erhalten. |
| A03 Technischer Vertragsentwurf | 80–85 % | 15–20 % | Identität, Version, Budget, Fehler und Lebenszyklus beschrieben; Wireformat/CA/harte Grenzen/kanonische Übernahme offen. |
| A04 Testmatrix | 90 % Spezifikation | 10 % Spezifikation | 25 Fallfamilien; Details nach finaler Technik präzisieren. Ausführung separat T1–T3. |
| A05 Wiederverwendungsprüfung und Paketabgrenzung | 100 % begrenzter Abgleich | 0 % dieses Abgleichs | WindowsJob, lokaler RadiWorks-Scope und Aurelia-Auth-Grenzen dokumentiert. |
| A06 T1-Implementierungsplan | 100 % Plan | 0 % Plan | Lokaler synthetischer Vertragskern präzisiert; Betreiber hat Umsetzung jetzt freigegeben. |
| T1 Offline-Implementierung und Tests | 0 % vor diesem Lauf | 100 % | Beginnt nach Erstellung dieser Matrix; kein TLS-/Produktnachweis. |
| T2 Echter isolierter REST-/mTLS-Test | 0 % Ausführung | 100 % | Werkzeug-/Testidentitätswahl, Umsetzung und Transporttests folgen. |
| T3 Ubuntu-Prozess-/Abbruch-/Wiederanlaufprüfung | 0 % Ausführung | 100 % | Nach T1/T2 mit abgegrenztem Server-Testbereich. |
| A07 Tatsächliche Aurelia-Auth-Anbindung | 10–20 % | 80–90 % | Lokale Quellen gefunden; Passkey-/Broker-/gateIdentity-Zusammenführung und reale Mandantenrechteprüfung offen. |
| C01 Promote/CopyGuard/Step-up | 0 % neue Abnahme | 100 % | Eigener bestätigter Übergangsvertrag und Tests erforderlich. Bestehende Produktarbeit nicht pauschal mit 0 bewertet. |
| C02 Mutationen/Idempotenz | 0 % neue Abnahme | 100 % | Getrennter Transaktions-/Wiederholungsvertrag. |
| C03 WebSocket/Reconnect/Replay | 0 % neue Abnahme | 100 % | Auth-, Größen-, Replay- und Verbindungsnachweise. |
| C04 Hintergrundjobs | 0 % neue Abnahme | 100 % | Persistenz, Neuautorisierung, Wiederanlauf. |
| A08 Erstmodulwahl, Adapter, S4 | 0 % neue Freigabe | 100 % | Kein Erstmodul gewählt; isolierter fachlicher Linux-Smoke und vollständige Kriterien fehlen. |
| A09 Kontrolliertes Deployment/Registry/S5 | 0 % dieses Pakets | 100 % | Übertragung, Hash-/Start-/Rollbackprüfung und explizite Registry-/Produktionsentscheidung. |
| A10 Gemeinsame lokale/Server-Backupstände im Governor | 10–20 % Planung | 80–90 % | Strategie besprochen; phasenbezogene Zuordnung, Restoreablauf und echte Adapter nicht umgesetzt. |
| A11 Frontend-/Headless-CMS-Entscheidung | NB | NB | Vom Betreiber zur Abstimmung vorgesehen; keine abschließende neue Auswahl in diesem Arbeitspaket. |

## P – Die fünf Produktprojekte: gesonderte Sicht

| Projekt | Belegter Stand | Gesamtentwicklung in % | Offene Integrations-/Freigabeschritte |
|---|---|---:|---|
| Aurelia | Architektur-/Gatequellen plus UI/Auth-Code vorhanden; Serveriststand weiter als alte Ground-Zero-Dokumente | NB | Aktualisierte G0-Bewertung, konsistentes Auth-/REST-Profil, echte Integrations-/Betriebsabnahmen |
| Modul_Templates | Gemeinsame Standards/Reifegrade vorhanden; Integrationsautorität Aurelia | NB | REST-Ergänzung kanonisch abstimmen, Abweichungen und S4-Kriterien tatsächlich prüfen |
| RadiWorks | Reifegradquelle 08.09.: S0–S3 lokal dokumentiert, S4 nicht zertifiziert, S5 offen; aktueller Scope-Code nur local | NB | Tenant-/Auth-Anbindung, vollständiger S4-/Linux-/CopyGuard-/WS-/Betriebsnachweis, spätere Registryentscheidung |
| Radi144 | Eigenständige historische Entwicklungs-/Übergabedokumente existieren; Register nennt Phase-0/Review-Vorbehalt | NB | Aktuellen eigenen Phasenplan und Abschlussbelege gesondert abgleichen; Templates führen noch keine bestätigten S-Stufen |
| morphic_v1 | Eigenständige Worktree-/Phasenartefakte vorhanden; Authority-Freeze-Vorbehalt im Register | NB | Aktuelle Authority-/Reviewentscheidung und Implementierungsgrenzen klären; historische Migrationspriorität ist keine neue Modulwahl |

S0–S3 bei RadiWorks sind vier benannte Reifestufen, **kein 67-%-Aufwandsnachweis**. Die Reifegradquelle der Templates ist historisch und darf nicht den aktuellen Entwicklungsstand anderer Repositories ersetzen. Weitere Module (RadiMorphic/RadiBlohm/RadiThoms/RadiCopen) sind dort genannt; Identität/Zuordnung insbesondere RadiMorphic gegenüber morphic_v1 nicht ohne Nachweis gleichsetzen. Hinzufügen von 3–4 Modulen bleibt mögliches Ausbauziel, keine bereits ausgeführte Integration.

Diese Übersicht deckt alle im aktuellen Arbeitsstrang bekannten Phasen ab. Eine vollständige Unteraufgabenliste innerhalb jedes externen Produktrepositories wäre ein eigener Quellenabgleich; sie wird hier nicht erfunden. Die App wurde für diesen Bericht nicht gestartet und das Live-Journal nicht als aktuelle Gateautorität abgefragt.

## Reihenfolge ab jetzt

Matrixausgangsstand → genehmigtes T1 → T2-Vorbereitung/Transportnachweise → abgegrenztes T3 → fehlende relevante Infrastruktur-/Backup-/Vertragsabnahmen → Erstmodulwahl/S4 → Registry-/Produktfreigabe. Windows-Fremdinstallation und RH-1 bleiben nachrangig; Recoverywartung nur gesondert abgestimmt. Kein Neustart aus dieser Reihenfolge ableiten.

## Quellen und Aktualitätsgrenzen

- `FORTSETZUNG_SECHS_SCHRITTE_2026-09-18.md`: S3/Pilotgesamtabnahme und bestätigte Priorisierung.
- `HERMES_APP_ABSCHLUSS.md`, `RESTARBEITEN_0_5.md`: historische Meilensteine und verbleibende Erweiterungen; neuere Belege haben Vorrang.
- `GATEABGLEICH_AURELIA_2026-09-19.md`, `verification/ROOT_BASELINE_2026-09-19.md`, `verification/EFI_RECOVERY_2026-09-19.md`, `WIEDERAUFNAHME.md`: spätere Infrastruktur-/Recoverybefunde.
- REST-Vertrags-/Betriebs-/Testpaketdokumente 19.09. und T1-Plan 20.09.
- Modul_Templates/standards/REIFEGRADE.md: ausdrücklich datierter Reifegradstand 08.09.; kein neuer Produkttest.
- config.example.json: Projektidentitäten und historische Registervorbehalte, keine aktuelle Live-Freigabe.

Keine neuen Produktgates, Modellaufrufe oder Serveränderungen durch diesen Bericht. Prozentangaben sind Planungshilfe und niemals Ausführungsfreigabe.
