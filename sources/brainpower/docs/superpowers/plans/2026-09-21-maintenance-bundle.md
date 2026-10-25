# Gebündelte logische PostgreSQL-Abnahme

Betreiber beauftragt Wartungspaket nach dokumentiertem Vorschlag: ein kurzer Root-Aufruf, feste Schritte und Halt bei Fehler. Keine dauerhafte privilegierte Schnittstelle.

## Umfang

1. Gehashte Cold-Backup-Evidenz und Helfer, Originalstillstand und unveränderte Quelle prüfen. Restaurierten Cluster kopieren, Original und vorhandenen Restore nicht starten.
2. Testkopie in temporärer systemd-Unit als postgres starten: privates Netzwerk, nur eigene UNIX-Sockets, Originaldaten/Keys/Home unzugänglich, schreibbar nur eigener Laborordner, Ressourcen-/Zeitlimits.
3. Explizite minimale Konfiguration ersetzt ausschließlich Konfiguration der Testkopie (Preloads/Archivierung/Recovery deaktiviert). Rollen/DB-Katalog beschränkt inventarisieren; keine Namen/Inhalte nach außen. Bei externen Tablespaces, Recovery-Markern, unerwarteten DB-Zuständen oder SQL-Fehlern stoppen.
4. Globals und alle connectable Nichttemplate-Datenbanken privat dumpen; in neuen PostgreSQL16-Cluster mit gesonderter Kontrollrolle laden. Logische Plain-Dumps vor/nach vergleichen (nur zufällige pg_dump-restrict-Marker normalisieren). Source-default-DBs werden im Ziel vor Restore entfernt. Beschränkung max16DBs und100MiBDump je DB.
5. Beide Testcluster stoppen, Eigentümerschaft/Unit-Ende, Originalmanifest und Originaldienst erneut prüfen. Nur feste Zähler/Statusbericht exportieren. Keine SMB-Backups wiederholen, keine Quelldaten löschen.

## Validierung

- [x] Negative Tests für Dumpnormalisierung, Kataloggrenzen, Runtimekonfiguration. Insgesamt15gezielte Tests mit Cold-/Config-Regressionsprüfungen bestanden.
- [x] Synthetischer vollständiger Zwei-Cluster-Test als unprivilegierter Benutzer ohne echte Daten:2Datenbanken,16Rollen,Testtabelle/Datensätze/SELECT-Berechtigung,Globals undDumpvergleich bestanden; beideCluster gestoppt.
- [ ] Linux systemd-Unit/Isolation unter Root vor echtem Worker prüfen; bei fehlenden Eigenschaften abbrechen.
- [ ] Ein Root-Aufruf, anschließend Nachweise lesend abrufen und auswerten.

Grenzen: kein physischer Server-Recoverytest, keine Produktanwendung, kein endgültiges Rechte-/Tenant-Audit. Logische Gleichheit gilt für geprüfte Datenbanken und Globals, kein Beweis für spätere Migrationen. Keine neue Root-Berechtigung, keine Wiederholung bei Fehler. Private Testbestände bleiben zunächst zur Nachprüfung geschützt erhalten.

## Bereitstellung und bekannte Grenzen

KurzerAufruf `python3 ~klaus999/bpmaint21`, einmal alsRoot. Starter artifacts/server-maintenance-launch21.py→/home/klaus999/bpmaint21 SHA256b7f7873260e0be46e7e8eb04bfcbfedde026f794a2721011fef95d513eed7d9d. Payload artifacts/server-maintenance21.py→/home/klaus999/bpmaint21.payload.py SHA256e7ead4a164f9511f6066833254f6a4782d776b5675b70dfc76545fc580a09632. BeideServerhashes identisch. Starter prüft Payloadhash, exklusive rootgeschützte Installation /var/lib/aurelia-maintenance-packages/logical-20260921. Orchestrator-Arbeitsbereich /var/lib/aurelia-maintenance/logical-20260921, unit aurelia-logical-20260921.service. Ergebnis /var/tmp/aurelia-logical-20260921-result.json. Original16/main nachVorbereitungdown,keinefailedUnits. Rootlauf NICHT ausgeführt.

SynthetischeVorprüfung fand zunächst falscheKatalogspalte rolconfig inpg_authid; korrigiert aufpg_db_role_setting. ZweiterTest zeigte nurabweichendeinitdbBootstrap-GRANTORs für genau drei unveränderte Standardmitgliedschaften vonpg_monitor. Ausschließlich diese Standardfälle werden beimVergleich mitklarenOptionen normalisiert; eigeneGrants undabweichendeRechte bleiben streng. Negativtest dafür bestanden; Bericht benenntNormalisierung. Anschließender erweiterterSynthetiktest mitechtenTestobjekten vollständiggrün. KeineFehlläufe aufOriginaldaten.

Runtime-Isolation wird vorTeststart imRootlauf verlangt: andereNetznamespace/NoNewPrivs/CapEff0/Originalpfadeunlesbar. ZusätzlichsystemdReadonlyHost,privatesTmp,keinHost-/TCPNetz, /run ausgeblendet,CPU50%,RAM1GiB,Swap0,Tasks64,600sLaufzeit undStop30s. Root-Ausführung dieser neuenUnit noch nicht liveverifiziert; fehlschlagendeIsolationstopptvorDBStart. Template-Datenbanken sindausgeschlossen; Datenbanknamen mitSonderzeichen/mehrals16DBs/externeTablespaces/datenbankbezogeneRolleneinstellungen verlangen separatePrüfung undführenzuStop. KeineRPO/RTO-/GesamtG0Freigabe.
