# Genehmigte Fortsetzung in sechs Schritten

Betreiberauftrag: kontrolliert in dieser Reihenfolge weiterarbeiten, bestehende Produktgates bewahren. Medium; kein Low-Wechsel offen.

| Nr. | Schritt | Aktueller Nachweis / offene Grenze |
|---|---|---|
| 1 | C3b: abhängiger B-Vorschlag mit eigenen Tests, Review, Übernahme und technischem Abschluss | Direktes A→B-Profil implementiert, 204 gezielte Tests bestanden. Historische externe Vorgänger bleiben gesperrt. |
| 2 | C4: geschützte API und Bedienoberfläche | Für das direkte Pilotprofil geprüft: HTTP-A/B-Kette, Rücknahme, Browserbedienung und Schutzregeln. |
| 3 | Begrenzte Hermes-Gesamtabnahme | 659 Tests: 657 erfolgreich, 2 Symlink-Skips; JS-/Browser-/lokale Dienstprüfung bestanden. Siehe verification/S3c_C4_2026-09-18_verification.md. Keine universelle Produktausführung. |
| 4 | Zuerst Aurelia-/Modul-Templates-Voraussetzungen | Betreiber hat diese Priorität ausdrücklich bestätigt. Quellenabgleich siehe VORAUSSETZUNGEN_AURELIA_MODULE_2026-09-18.md; keine automatische Freigabe oder Änderung externer Repositories. |
| 5 | Ubuntu 24.04 und SMB: Backup plus tatsächlicher Restore | SMB 3.1.1 mit Verschlüsselung bestätigt. Tatsächlicher synthetischer NAS-Backup-/Restoretest bestanden und per SSH verifiziert: vier Dateien, Vollprüfung, Hash-/Modusvergleich. Testmount entfernt, Hauptmount RO, Timer aus. Siehe verification/SMB_RESTORE_2026-09-18.md. Produktiver Sicherungsumfang, separate Schlüsselsicherung und entsprechende Restoreabnahme bleiben offen. |
| 6 | Kontrollierte Serverintegration | Erst nach passenden Modul-, Test-, Backup-/Restorebelegen: isolierte Übertragung, Hash-/Start-/Dienst-/Neustart-/Rollbackprüfung; Produktfreigabe separat. |

Die lokale App-Abnahme bestätigt weder SMB-Funktion noch Serverbereitschaft. Windows-Erstinstallation auf einem fremden Rechner, weitere Produktadapter und RH-1 bleiben nachrangig. Letzter ZIP-Checkpoint vor C1–C4 ist kein Wiederherstellungspunkt dieser neuen Änderungen.
