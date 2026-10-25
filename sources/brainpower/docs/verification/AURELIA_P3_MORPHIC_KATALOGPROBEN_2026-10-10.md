# P3 – synthetische Morphic-Katalogproben, 10.10.2026

Begrenzter Katalog-Kernblock abgeschlossen: Worker und Leitung haben auf frischen Scratchpfaden jeweils **acht Fälle bestanden, einen übersprungen, keine Fehler oder Assertionfehler**. Identische finale Case-Details sind unabhängig verglichen. Das ist weder eine vollständige Katalog-/Modulabnahme noch eine Integrationsfreigabe.

## Quellen und Methode

Geprüfter Arbeitsstand: `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`. 29 konkrete Quellen vor/nach bytegebunden; 26 stimmen mit der vorherigen statischen Bindung überein, drei zusätzliche Kernquellen sind neu gebunden. Sieben Module tatsächlich aus den exakt gehashten Quellbytes kompiliert und ausgeführt: contracts, validation_attestation, validation, store, service, paths und backup. Keine Paketinitialisierer und kein pyc-Lader; Admin-API, Auth und Schlüsselzusammenstellung wurden nicht importiert. HEAD und getrackter Zustand unverändert; ungetrackte Dateien nicht inventarisiert. Kein führender Morphic-Produktstand ausgewählt.

Harness `checkpoints/Aurelia-P3-Morphic-Catalog-Tests-20261010/`: Runner-SHA256 `ff3e07f13746895767be16e11367b96bc0ca4a168ed7b236192ea59dae03e84c`, Test-SHA256 `5deca2cc06855424e707c9f1e65bd9d3077e9880cb231673287e297c477e2d35`. Beide in den finalen Läufen vor/nach identisch. Maßgeblich sind `root-final-result.json`, `root-final-binding.json`, `worker-final-result.json` und `worker-final-binding.json`.

Nur synthetische Katalogeinträge, Schlüssel und frische SQLite-Dateien. Die verwendeten Schreib-/Dateisystem-/SQLite-connect-APIs sind auf den Testordner begrenzt; relevante Prozess-/Socket-/Produktimport-Einstiege blockiert. `os.getenv` erhält ausschließlich den synthetischen Leerwert für `MORPHIC_PARALLEL_EXPORT_ROOT`; unbekannte Namen scheitern, keine Weiterleitung zur realen Umgebung. Direkte `os.environ`-Zugriffe sind in den sieben Modulen und Testquellen statisch nicht vorhanden; dies ist kein dynamischer Schutz. Python-/Git-Laufzeit ist davon getrennt, der Git-Bindungsprozess erbt die Hostumgebung. Keine Live-Kataloge, Klientenzeilen oder realen Katalogschlüssel gelesen.

Keine allgemeine OS-Sandbox: SQL-ATTACH, beliebiger Code, Austauschrennen und sämtliche indirekten Runtimezugriffe sind damit nicht umfassend abgesichert. Die konkrete Probe verwendet keinen SQL-ATTACH. Kein Abschwächen von ACLs, Originalschutz oder Produktcode.

## Tatsächliche Fälle

| Probe | Beobachteter Umfang | Stand |
|---|---|---|
| Kontextnamespace und Datenbankpfad | Jede der vier Kontextachsen einzeln verändert; unterschiedliche Namespaces/Pfade bei explizitem Root | Bestanden |
| Kontextgebundene Drafts | Gleiche ID in fünf Kontexten mit passender Payload; getrennte eindeutige IDs für negative Fremdkontext-Leseproben | Bestanden |
| Draft ändern/veröffentlichen | Erwartete Version als CAS-Bedingung; veralteter Stand zurückgewiesen | Bestanden |
| Attestsignatur | Tenant, Version und Payloadhash einzeln im signierten Inhalt verändert; nicht alle vier Kontextachsen in dieser Signaturprobe | Bestanden |
| Fehlender/falscher Schlüsselprovider | Veröffentlichung eines gültig attestierten Drafts zurückgewiesen | Bestanden |
| Payloaddrift | Kein passendes aktuelles Attest nach Payloadänderung; kein isolierter MAC-Manipulationstest | Bestanden |
| Explizite Pfadgrenzen | Traversal, Projekt-/Exportrootüberlappung und System-Schreibscope; Archivroot-/reservierte Archivnamespace-Sonderfälle nicht separat geprüft | Bestanden im genannten Umfang |
| Aktivierung/Rollback/Audit | Richtiger aktueller Zustand/Version; falscher Vorgänger und falsche Version getrennt zurückgewiesen, negatives State/Audit unverändert; Actor/Reason erfasst | Bestanden |
| Tatsächlicher synthetischer Symlinkroot | Host erlaubt das Erstellen des Scratch-Verzeichnissymlinks nicht | Übersprungen; kein positiver Reparse-/Junction-/Racebeleg |

## Zwischenfehler bleiben erhalten

Der erste Worker-Lauf endete in WinError5-Setup-/Cleanupfehlern. Ursprünglicher Stack und ursprünglicher Vorlauf-Harness wurden nicht vollständig erhalten; konkrete Ursache daher unbekannt. Der Ordner `harness_snapshot_post_initial_not_initial` bezeichnet ausdrücklich einen späteren Zustand, nicht den Erstlaufcode. Seine eingefrorenen Bytes entsprechen dem anschließend überprüften Root-Erstlauf-Harness. Alte nicht lesbare Scratchordner bleiben vor Ort, keine ACLänderung oder Löschung zur Bereinigung.

Root-Erstlauf mit diesem eingefrorenen Harness: sechs bestanden, zwei Fehler am korrekt gesperrten getenv-Zugriff in der Pfadlogik, ein Symlinkskip. Vollständige bereinigte Frames im Receipt. Anschließend ausschließlich Testharness korrigiert: geschlossene synthetische Umgebungsabbildung und präzisierte Nachweisfelder. Produkt-Pfadvalidierung nicht gemockt oder verändert. Beide finalen Wiederholungen bestanden im oben abgegrenzten Umfang. Die frühen Belege und Vorher-Snapshots werden zusammen mit den finalen Belegen gesichert.

## Review, offene Punkte und Wiedereinstieg

Tatsächlich eingesetzt: Luna6/max als begrenzter Worker, Astra6/medium als unabhängiger SPEC→QUALITY-Reviewer; Leitung führte eigenen Lauf und Ergebnisvergleich durch. Die Reviewkorrekturen zu Kontextnegativen, getrennten CAS-Bedingungen, Parent/Subtest-Auswertung, Quellbyte-Ausführung und Umgebungsbehauptungen sind berücksichtigt. Reviewerbefunde ersetzen keine Betreiberfreigabe. Das aktive Desktop-Leitmodell wird nicht aus gespeicherten Defaults behauptet.

Die sechs vorher geplanten Katalogpakete sind damit **nur teilweise** abgedeckt. Offen: Admin-HTTP/API/Authmatrix, echte Schlüsselzusammenstellung und Wiederherstellungsrechte, Importreceipt-Revalidierung, Default-Root-/Umgebungszweige, Archivsonderfälle, echte Junction-/Austauschrennen, Konkurrenz/Restart/Restore und nachgelagerte CLI-/Writer-/Artefakt-/Report-/Harmonisierungskette. Die neun älteren Owner-/Lease-Charakterisierungen sind ein anderer Block und werden nicht erneut als Katalogfälle gezählt.

RadiFarben: vorhandenes Access bestätigt, VM mangels Medien zurückgestellt. Definitionsexportkandidat mit synthetischer Importprobe vorbereitet, noch kein Access-Prozess, Originalimport oder Originalablauf durchgeführt. Details: [Referenzvorbereitung](AURELIA_P3_RADIFARBEN_REFERENZVORBEREITUNG_2026-10-10.md). Nach der Pause zuerst diese begrenzte synthetische Probe vorbereiten und prüfen; Originalkopie erst nach belegten Grenzen. Weitere Morphic-Restpakete bleiben gesondert.

Privater Sicherungspunkt: `runtime/aurelia-three-modules-20261009/reference-plan/p3-morphic-farben-20261010-152120Z`. Vorher-/Nachherdokumente, vollständige frühere Wiederaufnahme, private hashgleiche ACCDB-Kopie, gebundene Morphic-Quellkopien, Werkzeuge und Prüf-/Reviewbelege. Abschlusssiegel `VERIFY.json`/`MANIFEST.json` gesondert verifizieren. Dies ist ein begrenzter Arbeits-/Nachweispunkt, keine neue F:-Gesamtsicherung oder Wiederherstellung laufender Broadcastzustände.

P0/P3 insgesamt offen; P1/P2 nicht gestartet. P4 vollständige siebenmodulige Matrix vor P5 Datenbankentscheidung, P6 normative Templates/Kern und P7/P8/S4.8 separat. RadiWorks-Wartung bleibt vorgemerkt. Keine Produkt-, Algorithmus-, Liveinstanz-, Governors- oder Routingänderung.
