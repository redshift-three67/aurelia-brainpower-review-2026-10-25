# Phase 3 – Windows ACL/DPAPI-Entscheidung (synthetischer Machbarkeitsnachweis)

**Status:** Machbarkeit auf der lokalen Windows-Arbeitsstation bestätigt; keine Integration in
produktive Stores oder Exportwriter freigegeben.
**Betriebsprofil:** Variante A, lokaler Einoperator, Loopback-only.

## 1. Entscheidung

Für eine spätere, ausdrücklich freigegebene Speicherung sensibler lokaler Daten ist
**Windows-DPAPI im Kontext des aktuellen Windows-Benutzers** der passende
Ruheverschlüsselungsbaustein. Ergänzend kann eine restriktive NTFS-ACL für einen
expliziten temporären oder später dedizierten Datenroot verwendet werden.

Diese Entscheidung bedeutet ausdrücklich nicht:

- keine nachträgliche Verschlüsselung bestehender Runtime-, Workbench-, Joblog-,
  Backup- oder Exportdateien,
- keine Änderung von Scoring, Profilen, Multiplex, Reportinhalt oder Legacy-Exportpfad,
- keine Freigabe eines automatischen Löschpfads und
- keine Mehrbenutzer-, LAN- oder SaaS-Sicherheitszusage.

## 2. Technischer Nachweis

Der additive Feasibility-Adapter `core/compliance/windows_protection.py` verwendet
nur Windows-Bordmittel:

- `CryptProtectData` / `CryptUnprotectData` aus `crypt32.dll` über `ctypes`,
- `LocalFree` aus `kernel32.dll` für vom Betriebssystem reservierte Puffer,
- `GetUserNameW` aus `advapi32.dll` und
- `icacls.exe` für den ACL-Nachweis.

Es wird keine neue Abhängigkeit eingeführt und insbesondere nicht auf das zwar lokal
vorhandene, aber nicht deklarierte `pywin32`/`win32crypt` gebaut.

`restrict_directory_to_current_user()` akzeptiert absichtlich nur vorhandene
Verzeichnisse unter dem vom Betriebssystem gelieferten temporären Root. Es verweigert
Projekt-, Export-, Runtime- und Backuppfade vor einer ACL-Mutation. Der Adapter wird
nicht von RuntimeManifestService, WorkbenchRuntimeStore, dem Web-Launcher oder einem
CLI-Writer aufgerufen.

## 3. Ausgeführter, ausschließlich synthetischer Test

`tests/test_windows_protection.py` belegt auf diesem Windows-Host:

1. Ein fester ausschließlich synthetischer Byte-Payload wird per DPAPI geschützt,
   unterscheidet sich vom Klartext und lässt sich im selben Benutzerkontext korrekt
   wiederherstellen.
2. Eine nur von `tmp_path` stammende Teststruktur erhält eine auf den aktuellen
   Windows-Benutzer eingeschränkte ACL; die synthetische Datei bleibt im Testprozess
   lesbar.

Es wurden keine Klientendaten, `.env`-Dateien, Exporte, Runtime-Dateien, Backups oder
Secrets gelesen oder verändert. Es wurde kein Server gestartet und Port 8090 blieb
unberührt.

## 4. Grenzen und Betriebsfolgen

| Aspekt | Feststellung | Folge für eine spätere Integration |
|---|---|---|
| DPAPI-Bindung | Der Schutz ist an den aktuellen Windows-Benutzer und dessen DPAPI-Kontext gebunden. | Wiederherstellung, Profilwechsel und Gerätewechsel benötigen ein eigenes Backup-/Restore-Gate. |
| ACL | ACLs reduzieren lokalen Zugriff, ersetzen aber keine Verschlüsselung und keine Authentifizierung. | Nur für einen klar abgegrenzten Datenroot einsetzen; keine pauschale Rekursion über Bestandsdaten. |
| Browser-/Jobdaten | Bestehende Speicherorte und Erasure-Abdeckung bleiben unverändert. | Erst Datenklassifikation, Schlüssel-/Containerformat und Restore-Policy definieren. |
| Mehrbenutzerbetrieb | Nicht Gegenstand dieses Nachweises. | Variante B benötigt eigene Principal-, AuthZ-, TLS- und Schlüsselverwaltungsarchitektur. |
| Testportabilität | DPAPI und `icacls` sind Windows-spezifisch. | Der Test ist außerhalb Windows übersprungen; der Adapter schlägt außerhalb Windows explizit fehl. |

## 5. Erforderliches separates Integrationsgate

Vor einer produktiven Nutzung sind mindestens folgende Schritte separat zu beauftragen
und per RED/GREEN-Test nachzuweisen:

1. Ein ausschließlich opt-in Datencontainerformat mit Versionsfeld, ohne Änderung des
   heutigen Klartext-Defaults.
2. Ein Schlüssel-/DPAPI-Konzept ohne Speicherung von Klartextschlüsseln.
3. Deterministische, synthetische Backup-/Restore-Probe im selben und im erwarteten
   Wiederherstellungsprofil; ein nicht wiederherstellbarer DPAPI-Container muss
   fail-closed dokumentiert werden.
4. Kompatibilitäts- und Erasure-Dry-run-Nachweis für registrierte verschlüsselte
   Artefakte, ohne automatische Löschung.
5. Explizite Owner-/ACL-Policy für einen neu angelegten, serverseitig bestimmten
   Datenroot; keine ACL-Migration bestehender Exportarchive.
6. Vollsuite, `py_compile`, `git diff --check`, Review und ausdrückliche
   Nutzerfreigabe vor einem Commit oder produktiven Umschalten.

Bis dahin bleibt die ehrliche Aussage: DPAPI und eine begrenzte ACL-Härtung sind auf
diesem lokalen Windows-System technisch verfügbar und mit temporären synthetischen
Daten geprüft; produktive Persistenz bleibt unverändert.
