> **Aktualisierung:** Begrenzter600s-CPU-/RAM-Lastlauf23.09. bestanden. Abschluss, Grenzen und offene Punkte siehe [Serverbericht](SERVER_ABSCHLUSSBERICHT_2026-09-23.md). Ältere Aussagen unten über einen noch nicht gestarteten Lauf sind historisch.

# Serverabnahme – konsolidierter Stand23.09.2026

Diese Übersicht ersetzt überholte Statusaussagen älterer Prüfberichte, nicht deren historische Evidenz. Keine Gesamt-G0- oder Produktfreigabe.

| Bereich | Aktueller Nachweis / nächste Grenze |
|---|---|
| Backupbetrieb | Vierstündlicher gemeinsamer Datei-/Offline-DB-Lauf auf SMB; erster planmäßiger Lauf erfolgreich, Repositorycheck und Restore geprüft. Backup-Watchdog alle15Minuten, SMTP-Testempfang bestätigt. |
| Aufbewahrung | 7tägliche/4wöchentliche/6monatliche Stände; manueller Löschlauf und Prune/Restore erfolgreich, täglicher Timer sowie stündlicher Watch aktiv. Erster planmäßiger Retentionlauf noch nicht beobachtet. |
| PostgreSQL | Physischer und logischer Restore isoliert nachgewiesen; Hauptcluster gestoppt. Vor Nutzung als laufende Produktdatenbank konsistentes Online-Backup erforderlich. Bestehendes Cold-Profil lehnt laufende DB ab. |
| Schlüsselverwahrung | Historischer externer Schlüsselvergleich; aktuelles Repository verwendet denselben Schlüssel. Verschlüsseltes Archiv auf E: sichtbar; Archiv-/LUKS-/SMB-Zugang vom Betreiber extern bestätigt. LUKS-Header hashgleich. Kein neuer Off-Server-Vollrestore. |
| Boot / Verschlüsselung | Beide EFI-Auswahlen mit vorhandenen beiden NVMe getestet; RAID1/LUKS2 dokumentiert. Kein physischer NVMe-Ausfalltest. |
| Treiberbasis | Root-NVML vor/nach Neustart erfolgreich. CUDA bleibt gemäß ursprünglichem Plan späterem GATE-CUDA vorbehalten; fehlender CUDA-Lasttest ist kein Auftrag zur Toolkitinstallation. |
| Betriebsbeobachtung | Dokumentierte15h-Strecke mit162 gesunden Healthberichten; frischer Healthbericht23.09.21:09UTC gesund. T3-Ressourcentests vorhanden. Kein pauschaler repräsentativer Last-/Soak-Abschluss daraus. |
| Provider / Firmware | USV und KVM-Zugang vom Betreiber als beim Provider abgesichert bestätigt. ECC-Nachweis offen. Eigenständige Prüfung von BMC-Netztrennung/geordnetem OS-Shutdown nicht daraus ableiten. Secure Boot zuletzt deaktiviert, keine automatische Firmwareänderung. Historische Installationsprovenienz bleibt gesondert einzuordnen. |

## Ausdrücklich zurückgestellt

- Rescue-Erprobung und Provideranleitung: optional für den aktuellen Abschluss, Betreiber liefert später Informationen.
- Zweite aktuelle externe Datenkopie: spätere Standortentscheidung, SMB derzeit einzige nachgewiesene aktuelle externe Datenkopie. Bei Abschlussbesprechung/vor Hermes erneut erinnern, keine eigenmächtige Kopie.
- Externe Ausfallüberwachung: Betreiber23.09. entscheidet Einrichtung später über externen Dienst. Derzeit nicht vorhanden; lokale Backup-/Retentionalarme ersetzen keinen vollständigen Ausfallalarm.

Diese Zurückstellungen werden nicht als bestandene Prüfungen ausgegeben und führen jetzt nicht zu erneuten Einrichtungsfragen. RPO12h und RTO12h sind Ziele, kein vollständiger Langzeit-/Wiederaufbaunachweis.

## Nächster notwendiger Arbeitsschritt

Vorhandene T3-CPU-/RAM-/Abbruch-/Parallelitätsnachweise gegen die geltende Last-/Soak-Anforderung prüfen; nur die verbleibende konkrete Lücke planen. Keine wiederholte pauschale Testserie, kein Datenbankstart oder neuer Lastlauf allein aus dieser Übersicht. Parallel Providerantworten einordnen. Danach konkrete Abnahmeentscheidungen zu verbleibenden Abweichungen und kurze Betreiberbesprechung vor Hermes; keine implizite Gesamtfreigabe durch erfolgreiche Backup-Einrichtung.

Nachweise: verification/BACKUP_RUNTIME_2026-09-23.md, verification/RETENTION_RUNTIME_2026-09-23.md, verification/RECOVERY_CUSTODY_MONITOR_2026-09-23.md, verification/BOOTPFAD_ERGEBNIS_2026-09-20.md, verification/G0_NACHTBEOBACHTUNG_2026-09-21.md. Aktuelle Bedienpunkte in SERVER_AKTUELL.md.

## Nachprüfung vorhandener T3-Evidenz

Die JSON-Berichte t3cpu20, t3memory20, t3normal20, t3abortv220 und t3lossv320 wurden gezielt gelesen. CPU-Test: circa4,06Sekunden unter25Prozent eines CPU-Kerns, Drosselung nachgewiesen. RAM-Test: erwarteter OOM-Abbruch bei128MiB Prozesslimit; kein Test des gesamten128GB-Klassenspeichers. Normalende, Abbruch und Controllerverlust mit aufgeräumten Prozessen/Arbeitsbereichen sowie unveränderten SSH/WireGuard/GDM-Diensten belegt. Das sind erfolgreiche Schutz-/Ablauftests, keine repräsentative Hardware-Dauerlast. Nicht wiederholen.

Verbleibende Last-/Soak-Lücke: ein getrennt begrenzter CPU-/RAM-Lauf mit Ergebnisprüfung, Zeitlimit, Temperatur-/Healthbeobachtung und sauberem Abbruch; genaue Last/Dauer als neue technische Auslegung vor Ausführung festlegen, da der gelesene G0-Abschluss keine konkrete Dauer vorgibt. Keine CUDA-Installation, Rohdatenträger-Schreibtests, RAID-Ausfälle oder Starts des Original-DB-Clusters daraus ableiten. Noch kein solcher neuer Lastlauf vorbereitet/gestartet.

Betreiberantwort23.09.: USV beim Provider vollständig abgesichert, KVM-Zugang ebenfalls abgesichert; ECC muss noch nachgewiesen werden. Bestätigungen als Betreiber-/Providerangaben akzeptiert und dokumentiert. Keine erneute pauschale Nachfrage zu USV/KVM; keine technischen Detailnachweise oder Ausfalltests erfinden.
