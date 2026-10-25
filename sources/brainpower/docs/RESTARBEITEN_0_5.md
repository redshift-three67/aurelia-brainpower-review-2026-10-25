# Aktuelle Restarbeiten nach Aufnahme-/Strategieausbau

Ergänzung 16.09.2026: RH-1, Auswahlharmonisierung Medium/Low im Hermes-Routing, ist im aktuellen [App-Abschlussplan](HERMES_APP_ABSCHLUSS.md) eingeordnet: nach Abschlussnachweisen, vor automatisierten Folgen. Status geplant, nicht implementiert oder aktiviert; Betreiberbenachrichtigung bei Beginn und verifiziertem Abschluss verbindlich.

Fortschreibung 15.09.2026 nach Betreiberauftrag: alle fünf aktuellen Aufnahmen über die geschützte API bestätigt; `plan_ready=true`. Planauftrag `bf85cc5da30e404e9ef98b5c958edb76` lief mit Hermes/Terra und Sol durch, wurde jedoch von Sol fachlich blockiert (globaler Quellenabgleich fälschlich auf RadiWorks reduziert; Autorisierung/Voraussetzung verwechselt). Kein Kandidat und keine Strategie übernommen. Der vorhandene Quellenabgleich ist unverändert aktuell und abnahmefähig; konkrete Betreiberannahme separat angefragt. Nächster Planlauf erst nach dieser Klärung, kein blindes Wiederholen.

SMB: Providerbenutzer jetzt ausdrücklich als `k213487` bestätigt; noch keine erneute Anmeldung oder Backupabnahme durchgeführt. Betreiberpriorität bleibt zunächst Hermes.

Technischer Ausbau 15.09.2026: [Kontextprüfung und Verbrauch je Auftrag](HERMES_KONTEXT_USAGE_UMSETZUNG.md) implementiert und im lokalen Dienst aktiviert. 348 Tests bestanden, zwei ausgelassen; visuelle Browserabnahme wegen blockierter Navigation offen. Keine fachlichen Aufnahme-/Strategieentscheidungen ersetzt.

Aktuell geprüft am 15.09.2026: [lokale Bestandsaufnahme, Token-Effizienz und Registererweiterung](HERMES_BESTANDSAUFNAHME_2026-09-15.md). 341 Tests bestanden, zwei ausgelassen. Fünf registrierte Projekte, noch keine bestätigten Aufnahmen oder übernommene Strategie. Die folgende fachliche Reihenfolge bleibt erhalten; lokale Kontext-/Verbrauchsnachweise können unabhängig von der ausstehenden SMB-Klärung vorbereitet werden.

| Priorität | Noch offen | Nächster belastbarer Schritt |
|---|---|---|
| 1 | Fachliche Betreiberbestätigung der fünf Aufnahmen | Vorbereitete vier Felder je Projekt sowie Modellbefunde prüfen; offene Nachweise nicht als erledigt bestätigen. |
| 2 | Aktuelle reale Gruppenstrategie | Nach fünf aktuellen Bestätigungen hybriden Plan entwerfen, Quellen/Abhängigkeiten prüfen, saubere Kandidatenrevision bewusst übernehmen. Die technische Übernahmefunktion ist vorhanden. |
| 3 | Allgemeine Produktausführung | Konkrete Projektadapter und getrennte Ausführungsfreigaben entwickeln; der vorhandene isolierte Pilot ist keine Freigabe für die fünf Produkte. |
| 4 | Projektbezogene Test-/Live-Nachweise | Start/Stop, Ports, isolierte Testprofile und Rückführung je Auftrag an konkrete Projektadapter anschließen. Vorhandene RadiWorks-/CDP-Teile ersetzen nicht die Abnahme aller Module. |
| 5 | Reparatur und Fortschritt | Begrenzte hybride Fehlerkorrektur, belastbare Vorgängernachweise und Strategieaktualisierung nach echter Ausführung. |
| 6 | Freigegebene Schrittfolgen | Nur ausdrücklich gewählte, unveränderte Folge fortsetzen; bei neuer Matrix/Scope/Fehler stoppen. Noch nicht allgemein implementiert. |
| 7 | Mehrgruppen-/Vault-Gesamtabnahme | Vorhandene scoped Register- und Vault-Funktionen mit realen unabhängigen Gruppen, Lifecycle und Ausführungsadaptern verifizieren. |
| 8 | Vollständiges Windows-Erstsetup | Erst nach funktionaler Gesamtabnahme Hermes-/Python-/Git-Voraussetzungen und Routing auf sauberer fremder Windows-Instanz prüfen und installieren; CC Switch separat. |

Die alten Dokumente `OFFENE_SCHRITTE_2026-09-12.md` und `STATUS_UND_WINDOWS_0_4.md` bleiben historische Detailstände. Der neue Stand bestätigt keine Produktmigration und keine universelle autonome Steuerung.


## Aktiv – P3 RMF-Versionsvergleich, 11.10.2026

Aktueller RMF-Stand jetzt frisch statisch mit alter geschützter Referenz verglichen. Beide Läufe reproduzierbar außer Zeit: 100 kanonische VBA-Quelltexte gleich, frische alte Extraktion passt zu historischem Manifest; 751 Query-Speichermetadatenzeilen gleich. Objektinventar je45Forms/54Modules/3Reports/3Scripts plus85Query-Typ-Objekte (nicht die früheren47DAO-Querydefinitionen); kein neuer/entfernter Schlüssel. Fünf Query-Objekte unterscheiden sich nur im binären Lv-Feld; Bedeutung und volle saved-object/Event/Control/Makro-/SQL-/Runtime-/P-Codeparität offen. Keine Algorithmus- oder gesamte Workflowgleichheit ableiten.

Aktuelle Master-/Originalvorbindung2993247b…a1c9, alte Referenz2b48ce8d…13bc. Neue Definitionen/Hashes getrennt geschützt unter runtime/radifarben-source-versions/RF-20261011-080657Z; keine alten Belege auf neue Datei umetikettiert. Neue RMF-Versionen weiter getrennt aufnehmen/prüfen. Capture-Tool694Bibliotheksdateien vor/nach archivgleich; Leitung14Guardtests bestanden, Comparator Worker/Leitung je11bestanden+1echterSymlinkskip. Astra hat Werkzeugkorrekturen/Beweisgrenzen geprüft; private Rohdefinitionen nur Leitung. Gemeinsame Quellenhash/Identitäts/Zeit/Lock-Endpunkte sind keine WORM-/Exklusiv-/Racegarantie.

RF-E1 weiterhin offen (COM80080005 vor Datenbankaktion; volle synthetische Import-/Exportprobe NOT_RUN). Nächste unabhängige Arbeit weitere P3-Vertrags-/Writer-/Reportproben und RMF-Bindungen; P0/P1/P2 offen, P4siebenmodulige Matrix vor P5Datenbankentscheidung, P6–P8/S4.8 getrennt. Keine Access-/DAO-/SQL/VBA-/WSL-/Cloud-/Produkt-/Live-/Routing-/normative Templatesänderung; RadiWorks-Wartung nachrangig.

Bericht docs/verification/AURELIA_P3_RADIFARBEN_RMF_VERSION_DELTA_2026-10-11.md. Lokaler Vorher-/Nachherpunkt checkpoints/RadiFarben-RMF-Delta-20261011-121653Z, private Belege getrennt geschützt; Manifest prüfen, keine neue F:-Gesamtsicherung. Tatsächliche Helfer GPT-6Luna/max und GPT-6Astra/medium.



## P3 – Import-Schutz / RMF-Abfragezuordnung, 11.10.2026

Begrenzter Referenzblock abgeschlossen, keine volle Modulabnahme: Morphic Worker/Leitung je5synthetischeTestsgrün (Service-Publish-Sperre+explizitePfadgrenzen); RadiFarben3alteQuerydefinitionstreffer/6Literalkandidaten aus5Lv-Änderungen/100gebundenenVBA-Dateien,15synthetischeHelpertestsgrün,2gleicheLäufe. Vollregistry/RF-E1/Runtime/Writer-/Report-/Restoreabnahmen weiter offen. Maßgeblicher aktueller Bericht docs/verification/AURELIA_P3_IMPORT_RMF_BINDUNGEN_2026-10-11.md; Prüfpunkt checkpoints/Aurelia-P3-Import-RMF-20261011-153618Z. P4siebenmoduligeMatrix vorP5DBentscheidung; keine Produkt-/Live-/Templateänderung oder F:-Vollsicherung.

P3 11.10.2026: begrenzte Backup-Referenzprüfung zweimal14/0/0/0 abgeschlossen. Vollständiger positiver Restore und Bericht-Handleprüfung weiter offen; siehe docs/verification/AURELIA_P3_BACKUP_REFERENZEN_2026-10-11.md. P4-Matrix vor P5 unverändert.

P3 11.10.2026 Berichtreferenzen: zwei korrigierte Läufe je12/0/0/0; echter Windows-Handleweg ausschließlich synthetisch. Writer-/Registry-/Restore-/RF-E1-Abnahme weiter offen. Bericht: docs/verification/AURELIA_P3_BERICHT_REFERENZEN_2026-10-11.md. P4 vor P5.

P3 11.10.2026 Writer/Registry/Templates: statische Kette (zehn Writer-, vier Publish-, drei Template-Dateien) gebunden, Astra präzisiert; positive Restore-/Job-Runtime weiter NOT_RUN. POSIX-Publishguard vor Ubuntu-Integration klären. Nächstes Paket geprüfter Loader + echter synthetischer Windows-Publish/Restore; RF-E1/P0–P3 bleiben offen. Bericht docs/verification/AURELIA_P3_WRITER_REGISTRY_TEMPLATE_2026-10-11.md; lokaler Prüfpunkt Aurelia-P3-Writer-Registry-Status-20261011-174307Z. Keine normative Template-/Liveänderung; P4 vor P5.


P3 11.10.2026 öffentlicher Windows-v8-Backup/Restore: jetzt zwei tatsächliche Läufe je10/0/0/0 mit Original-Registry. Je29 synthetische Artefakte nachgerechnet. Vorherige NOT_RUN-Angaben bleiben historische Teilberichte; positiver Windows-v8-Weg ergänzt, kein Writer-/Job-/Linux-/Auth-/Gesamtmodulnachweis. Bericht docs/verification/AURELIA_P3_PUBLIC_RESTORE_2026-10-11.md; Prüfpunkt Aurelia-P3-Public-Restore-Status-20261011-182431Z. POSIX-Cleanup/v7/übrigeP3/RF-E1 offen, P4 vor P5 unverändert.


P3 11.10.2026 v7→v8: zwei korrigierte synthetische Windowsläufe je12/0/0/0; Markerreset und drei Rollbacks, öffentlicher Migration→Restore. V1 Fixturefehler: 6/0/1/0 (fünf bestanden) samt zwölf Artefakten erhalten, je39 v2-Artefakte nachgerechnet. Historischer Herkunftshash ungültig, v2 aktuell geprüft; frühere Kontinuität unbekannt. Kein gefüllter Katalog-/Revalidierungs-/Auth-/Produkt-/Linuxnachweis. Bericht docs/verification/AURELIA_P3_V7_MIGRATION_2026-10-11.md; Prüfpunkt Aurelia-P3-V7-Migration-Status-20261011-191912Z. POSIX/übrigeP3/RF-E1/P0–P2 offen, P4 vor P5.


P3 11.10.2026 POSIX: statischer Zehnmodulvertrag abgeschlossen, null Produktmodule/POSIX-Tests. Referenzstart CreateVm/HCS/0x800705aa vor Linux-Python, zusätzlich CoreCLRheap-Fehler; kleine verfügbare Commitreserve, Ursache nicht bewiesen. Keine Host-/WSL-/Liveänderung. Tatsächlicher Guard-/FD-/Cleanupnachweis offen; Bericht docs/verification/AURELIA_P3_POSIX_VORBEREITUNG_2026-10-11.md; Prüfpunkt checkpoints/Aurelia-P3-POSIX-Status-20261011-195451Z. P0–P3/RF-E1 offen, P4 vor P5.
