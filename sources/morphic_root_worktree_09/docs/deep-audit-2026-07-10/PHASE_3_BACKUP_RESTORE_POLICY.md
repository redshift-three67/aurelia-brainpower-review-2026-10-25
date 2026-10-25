# Phase 3 – Backup-/Restore-Policy und synthetische Restore-Probe

**Status:** Temporäre, hashverifizierte Machbarkeitsprobe grün; keine produktive
Backup-Aktivierung oder Migration freigegeben.
**Betriebsprofil:** Variante A, lokaler Einoperator, Loopback-only.

## 1. Entscheidungsgrenze

Der bestehende CLI-Dekorator `cli.utils.backup.log_command` erzeugt neben einer
Quellcodedatei zeitgestempelte `.bak_*`-Kopien. Er ist kein Datenschutz-,
Runtime- oder Export-Backupverfahren und wird durch diesen Gate nicht verändert.

Der neue additive Helfer `core/compliance/synthetic_backup.py` ist ausschließlich
eine Restore-Machbarkeitsprobe. Er ist weder an RuntimeManifestService,
WorkbenchRuntimeStore, Web-Launcher, CLI-Export noch an einen Scheduler gebunden.
Er kann ausschließlich mit Pfaden unter dem vom Betriebssystem gelieferten
Temp-Root arbeiten. Projekt-, Export-, Runtime- und Backuppfade werden vor
jeglicher Kopie oder Wiederherstellung verweigert.

## 2. Nachgewiesene Proberegeln

Für rein synthetische, temporäre Daten gilt:

1. Der Quellroot muss existieren und unter dem OS-Temp-Root liegen.
2. Der Backuproot muss zuvor fehlen; ein bestehender Root wird nicht überschrieben.
3. Jeder reguläre Dateiinhalt wird in eine neue temporäre Struktur kopiert und mit
   relativem Pfad, Bytezahl und SHA-256 in `manifest.json` registriert.
4. Symbolische Links werden verweigert.
5. Vor Restore werden Manifestform, Pfade, Bytezahl und SHA-256 jeder registrierten
   Backupdatei geprüft.
6. Der Restore erfolgt nur in einen zuvor fehlenden temporären Zielroot. Bestehende
   Ziele werden nicht überschrieben.
7. Quellen werden weder umbenannt noch verändert; die Probe erzeugt keine
   Produktionsaktivierung.

## 3. Ausgeführte synthetische Restore-Probe

`tests/test_synthetic_backup_restore.py` erstellt zwei ausschließlich synthetische
Dateien unter `tmp_path`, erstellt ein Backup und restauriert es in einen separaten,
vorher fehlenden `tmp_path`-Root.

Der Test weist nach:

- beide Dateihashes bleiben im Quellroot vor und nach dem Backup unverändert,
- das Manifest enthält Schema-Version, Dateianzahl, relative Pfade, Bytezahlen und
  SHA-256-Hashes,
- die wiederhergestellten Dateien stimmen bytegenau mit den Quellen überein und
- Aufrufe mit einem Projektpfad werden vor Kopie bzw. Restore mit `ValueError`
  verweigert.

Es wurden keine vorhandenen Archive, Klientenexporte, Runtime-Dateien, Backups,
Secrets oder `.env`-Dateien geöffnet oder verändert. Es wurde kein Server gestartet;
Port 8090 (Radi144) blieb unberührt.

## 4. Produktive Policy – noch nicht aktiviert

Vor einem späteren produktiven Backupverfahren muss ein eigenes Integrationsgate
die folgenden Regeln verbindlich umsetzen und nachweisen:

| Bereich | Erforderliche Regel |
|---|---|
| Scope | Nur explizit klassifizierte, serverseitig bestimmte Artefaktroots; keine Browser- oder beliebigen Nutzerpfade. |
| Konsistenz | Quiesce-/Snapshot-Regel pro Store; keine Behauptung eines konsistenten Backups bei parallel laufenden Writes ohne nachweisbaren Lock oder Snapshot. |
| Verschlüsselung | DPAPI-/Containerentscheidung gemäß `PHASE_3_WINDOWS_ACL_DPAPI_ENTSCHEIDUNG.md`; keine Klartextschlüssel in Manifesten oder Logs. |
| Manifest | Versioniertes Inventar mit relativen Pfaden, Größen, Hashes, Erstellungszeit und klarer Speicherklassifikation; keine Klartextinhalte oder Klientenstammdaten. |
| Restore | Zuerst in einen leeren, isolierten Zielroot; vollständige Hashprüfung vor Übergabe; kein In-place-Overwrite produktiver Daten. |
| Erasure | Backups bleiben als abgedeckte bzw. explizit nicht abgedeckte Speicherklasse im Erasure-Completion-Report sichtbar; keine automatische Löschung. |
| Retention | Aufbewahrungsdauer, Rotation, Offline-/Medienziel und verantwortliche Freigabe müssen vor Aktivierung festgelegt werden. |
| Nachweis | Synthetische Backup-/Restore-Probe, Ausfall-/Manipulationsfälle, Vollsuite, `py_compile`, `git diff --check` und ausdrückliche Nutzerfreigabe. |

## 5. Nichtfreigabe und nächster Gate

Diese Probe legitimiert keine Sicherung bestehender Klienten- oder Exportarchive und
keine Wiederherstellung über produktive Roots. Sie beweist ausschließlich den
sicheren Ablauf einer isolierten, hashverifizierten synthetischen Kopie.

Der nächste notwendige Schritt vor einer echten Backupintegration ist ein separater
Design- und Testgate für klassifizierte Speicherklassen, DPAPI-Containerformat,
Retention und eine synthetische Manipulations-/Restore-Fehlerprobe. Bis dahin bleibt
der produktive Datenpfad unverändert.
