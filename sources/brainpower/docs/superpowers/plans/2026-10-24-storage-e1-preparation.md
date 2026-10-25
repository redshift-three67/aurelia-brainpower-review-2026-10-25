# Getrennte Testablage E1 – Einrichtungspaket

> **For agentic workers:** Execute the approved preparation with TDD and independent review. No server execution is authorized.

**Goal:** Ein konkretes, einmaliges Einrichtungspaket für eine neue 4-GiB-Testablage mit 16-MiB-Kontrollreserve vorbereiten.

**Architecture:** Neue eigene, bisher abwesende Wurzel `/srv/aurelia-empirical-e1`, reguläres vorallokiertes `data.img`, zuerst nur dieses neue Image formatieren, danach genau dessen Loopgerät verifizieren/mounten. Kontrollslots bleiben auf dem äußeren Dateisystem. Root besitzt Image und Kontrollbereich; UID/GID1000 erhält ausschließlich den neuen Daten-Mount. Bei Fehlern Teilzustand erhalten, kein Retry/Detach/Unmount/Delete oder Änderung alter Marker.

**Tech Stack:** Python-Standardbibliothek und genau begrenzte Linux-Systemwerkzeuge; native Funktionen nur über expliziten Einstieg, lokale Tests mit synthetischen Fakten und injizierter Backend-Simulation. Kein Docker-, Import-, Build- oder Netzwerkstart.

## Betreiberentscheidung

Freigegeben ist die **Vorbereitung** der zusätzlichen getrennten Ablage, keine Einrichtung. CPU-/RAM-Budgets und VM-Entscheidung bleiben unverändert. Eine spätere Einrichtung benötigt einen konkret gebundenen, getesteten und unabhängig geprüften Ausführungsumfang sowie neue Einmalfreigabe. 4GiB/16MiB sind Testgrenzen, keine Bedarfsgarantie.

## Arbeitspaket `runtime/rw-storage-e1-prep-20261024`

- [x] `storage_facts.py`/Tests: feste Ext4-Geometrie/UUID/Featuremasken, getrennte Geräteidentitäten und Loopbindung; nur synthetische Header, kein altes Image öffnen.
- [x] `setup_core.py`/Tests: strikte Reihenfolge, einmalige Beanspruchung, Kontrollreserve vor Datenallokation, Formatierung ausschließlich per neuem regulärem Dateideskriptor, Vor-/Nachschutz und keine automatische Bereinigung.
- [x] Linux-Adapter und Befehlsgrenzen konkret ausarbeiten: sichere Eltern-/Deskriptorbindung, fsync, genaue Werkzeuge/Umgebung, Budget-/Prozess-/Zeitgrenzen und finaler Mountnachweis. Nicht implementierte Adapter bleiben explizit gesperrt.
- [x] Relevante lokale Fehler-/Integrationsprüfungen und Quellenbindung; unabhängiger Astra/medium-Review, Befunde korrigieren und nachprüfen.
- [x] Exakten tatsächlich ausführbaren Freigabeumfang zeigen; falls ein konkreter ungeklärter Sicherheitsbefund verbleibt, keine Ausführungsreife behaupten.

## Quellen

Geometrie und Optionen werden gegen die offizielle e2fsprogs-v1.47.0-Definition und util-linux-Quellen geprüft. Das ist kein Nachweis der installierten Binärherkunft. `mke2fs -O none,...` startet die gewünschte Featuremenge explizit; `-E nodiscard,lazy_itable_init=0,lazy_journal_init=0` vermeidet absichtliches Discard und nachgelagerte Initialisierung. Loopzuordnung braucht eine zusätzliche eigene Sperre und Identitätskontrolle; `--find` ist nicht atomar. Mounten nur auf die neue Zielablage, kein fstab-/Autostart-Eintrag.

- https://raw.githubusercontent.com/tytso/e2fsprogs/v1.47.0/lib/ext2fs/ext2_fs.h
- https://raw.githubusercontent.com/tytso/e2fsprogs/v1.47.0/misc/mke2fs.8.in
- https://kernel.googlesource.com/pub/scm/utils/util-linux/util-linux/+/refs/tags/v2.41.1/sys-utils/losetup.8.adoc
- https://raw.githubusercontent.com/util-linux/util-linux/v2.39.3/sys-utils/mount.8.adoc

## Abschluss der Vorbereitung

48 lokale Tests ohne Fehler/Skips; unabhängiger Astra/medium-Nachreview V3 ohne offene Befunde im Offlinepaket. Operativ ausschließlich `prepared-v4`, Paket `a9c2ebc67a5cba7ed4038a2cbcf727e16f5d2b4b4cee632dfc8c36876db00d5e`. R4 (finale Eigentümer-/Rechteprüfung) test-first behoben. Kein nativer Aufruf; Einrichtung wird erst mit eigener neuer Einmalfreigabe ausgeführt. Exakter Umfang: `runtime/rw-storage-e1-prep-20261024/APPROVAL_SCOPE.json`; Grenzen und Teilzustände: `DESIGN.md`. Material-/Import-/Buildfreigabe bleibt ausgeschlossen.
