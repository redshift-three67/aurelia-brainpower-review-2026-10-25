# Physical storage basis probe implementation plan

**Goal:** Prepare, test and independently review one strictly bounded reading packet; no native execution until new exact approval.

**Architecture:** Fresh metadata-only core and strict sanitized result contract; reuse frozen V3 lifecycle/transport in isolated runtime/rw-physical-basis-20261024. Own new unit/path. No root/header/image-content read: current fixed stat/config/package reads only; pure Ext4 parser offline. No archive model/producer/import.

**Tech Stack:** Python stdlib, generated systemd/SSH adapters; offline unittest with process/network audit denial.

- [x] Pin V3candidate/execution and non-executable contract; preserve bytes.
- [x] RED: tests for allowlisted parser/Ext4geometry, no DBdata and unsafe file paths/drift.
- [x] Implement physical_fields.py,ext4_superblock.py,physical_observer.py and metadata-only job_core.py/result_contract.py; fixed budgets.
- [x] Wire fresh unit identities/strict receipt/transport/generator; never execute native action during preparation.
- [x] Run relevant parser/IO/core/lifecycle/client/generated packet suites with durable evidence and source checks; adversarial corruption, timeout/persistence/replay paths.
- [x] Independent Astra/medium SPEC/QUALITY review of exact sources/test evidence; resolve findings and freeze.
- [x] Show exact files/reads/writes/calls/resources/limits and remaining proof gap for next operator approval.

**Abschluss der Vorbereitung:** 159Tests/0Fehler/0Skips/0Prozess-Netzwerkversuche;98Vorgängerreferenzen unverändert. Drei unabhängige P2-Hinweise gezielt RED/GREEN geschlossen, finaler Astra/medium-Delta-Review0neue Befunde. 85Reviewreferenzen und4Skripte unabhängig bestätigt. Hashgebundener echter Clientloader offline erfolgreich. Native-Freigabe bleibt offen; aktueller90Datei-Checkpointbd076761e8183a75a4f9a1c88e28e22bff01327027e38b20dad5753807d37223.

Kein Root/Headerzugriff im nativen Paket; ursprüngliche Idee wegen belegt uid1000/root:0600 verworfen. Offlineparser ohne I/O bleibt nur synthetische Vorbereitung. Vollständige physische Speicherzulassung bleibt separat offen.

**Einmalige native Ausführung separat genehmigt und abgeschlossen:**1Vorprüfung/1Start/1Status, frischer sicherer Abschluss, Slots2–6geschlossen. Alle25Dateien+ImageStat+3Verzeichnisse verfügbar;9DBNutzdaten0Bytes. Unabhängiger Astra/medium-Belegreview0materielle Widersprüche; Hauptagent validierte tatsächlich gebundenen Client/3Antworten. Ausführungscheckpoint3547d04cef004956c1f10620c55d35518966c7013b1e30962546240c061374e1. Physische Gesamtspitze weiterhin unbekannt; weitere Strategievorbereitung erfordert BetreiberwahlA/B aus docs/verification/RW_PHYSICAL_NEXT_STRATEGY_2026-10-24.md. Keine weitere Native-/Materialfreigabe.
