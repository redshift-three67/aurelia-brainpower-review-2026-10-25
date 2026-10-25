# R2-1: begrenzte Buildablage – konkrete Entscheidungsvorlage

Stand 18.10.2026. Reasoning: Medium. Noch nicht ausgeführt. Gegenstand ist zunächst nur die neue Ablage samt begrenzter Dateisystemprüfung; weder Image-Pull noch SQLite-Build oder Vorschauwechsel. Die [bisherige Kandidatenplanung](2026-10-18-radiworks-sqlite-candidate.md) und die getrennten Produktgates bleiben bestehen.

## Belegter Ausgangspunkt

Rein lesend über bestehende hashgeprüfte IPv4-Profile bestätigt: vm2565/Ubuntu, Kernel 6.8.0-146-generic, Docker29.9.1 rootlos, containerd2.4.2. Die tatsächlich verwaltete containerd-Datenwurzel liegt derzeit unter /home/aurelia-ops/.local/share/docker/containerd/daemon. Aus allgemeiner Dokumentation zur Trennung von Docker-/containerd-Datenwurzeln darf deshalb keine gegenteilige Aussage über diesen Iststand abgeleitet werden. Das beweist aber keine zukünftige Wurzel eines zweiten Daemons oder eine Quote. [Lesebelege](../../verification/sources/r2-candidate-20261018/SERVER_PREPARATION_READS.json).

Die bestehende Host-ext4-Partition wird nicht als neue Buildgrenze behandelt. Quota-Werkzeuge sind nicht vorhanden; keine aktive Projektquota nachgewiesen. Vorhanden sind fallocate, losetup, mkfs.ext4, mount/umount, Loop-Control und geladenes Loop-/ext4-Modul. /srv ist kein Symlink; /srv/aurelia-build-r2-1 und die vorgesehenen rwsqlitebuild-Laufzeitnamen sind noch nicht belegt. Etwa227GB/14,8Mio Inodes frei sind eine Momentaufnahme, keine Speicherisolation. Keine bestehende Partition, Dockerkonfiguration oder Runtime geändert.

## Empfohlene neue Ablage

Ein neu angelegtes, vorallokiertes **6-GiB-Dateiabbild** (6442450944 Bytes) als eigenes ext4-Dateisystem verwenden. Feste Gesamtgröße und höchstens50000 Dateisystem-Inodes begrenzen den persistenten Buildbestand einschließlich Pulls/entpackter Layer, Image-/containerd-Speicher, Cache, Quell-/Arbeitsdateien, Exporte und begrenzter Buildlogs. Metadaten innerhalb des Abbilds vermindern dessen nutzbare Kapazität; 6GiB sind kein garantierter Nutzdatenplatz. Host-Dateisystemmetadaten und begrenzte Steuerbelege außerhalb des Abbilds zählen zur zusätzlichen2-GiB-Aufnahmereserve; kein vollständiger Schutz vor fremden Hostschreibern.

Festgelegte neue Pfade:

| Zweck | Pfad/Eigentum |
|---|---|
| Neuer Verwaltungsordner | /srv/aurelia-build-r2-1, root, nur notwendige Traversierung für Ops |
| Neues leeres Abbild | /srv/aurelia-build-r2-1/disk.img, root:root0600; Ops erhält keinen Zugriff auf das zugrundeliegende Blockgerät/Abbild |
| Eigener Einhängepunkt | /srv/aurelia-build-r2-1/fs; Dateisystemwurzel aurelia-ops UID/GID1000,0700 |
| Spätere Build-Unterordner | fs/docker, fs/config, fs/client, fs/tmp, fs/work, fs/export, fs/log – sämtlich auf diesem Dateisystem |

Nicht fstab-gebunden, kein Autostart nach Reboot, kein zusätzlicher SSH-Benutzer, kein sudo-/Dockergruppenrecht. Vor Aktivierung nach Reboot Mountidentität erneut feststellen; fehlt der Mount, strikt nicht auf das darunterliegende Hostverzeichnis schreiben. Der ungemountete Mountpunkt bleibt root-eigen und für Ops nicht beschreibbar. Die Ablage bleibt nach der Prüfung erhalten; keine automatische Löschung des Abbilds.

## Exakter Zuschnitt nach Betreiberfreigabe der Ablage

1. Host/UID, SSH-Profilhash, Vorschau-ID/Image/Startzeit/Neustartzähler, vorhandene Produktquellen-/Konfigbelege und Projektlimits erneut binden. Die drei neuen Zielpfade müssen neu, kanonisch und symlinkfrei sein; kein vorhandenes Ziel übernehmen oder überschreiben. Mindestens8GiB und75000 zusätzliche freie Inodes vor Beginn. Hashgebundene lokale Vorher-/Schritt-/Nachherbelege, keine Schlüssel im Vorgang.
2. Nur den neuen Verwaltungsordner erzeugen. disk.img exklusiv erzeugen; fallocate exakt6GiB. Reguläre Datei, ein Hardlink, root0600 und tatsächliche Größe prüfen. Kein veränderbarer benutzerkontrollierter Pfad zwischen Prüfung und schreibendem Rootaufruf. Belegte Hostblöcke prüfen; unerwartete Sparse-/Allokationslage stoppen.
3. Nur diese neue leere reguläre Datei formatieren: ext4 mit Blockgröße4096, vorgeschlagen49152 Inodes, reserviertem Rootblockanteil0 und nodiscard bei mkfs. Die Inodezahl ist erst nach Erstellung belegt und muss <=50000 sein. Keine vorhandenen Datenträger oder Partitionen als mkfs-Ziel. Das -N-Argument allein garantiert keine exakte resultierende Anzahl. [mke2fs-Optionen](https://manpages.ubuntu.com/manpages/noble/man8/mke2fs.8.html).
4. Ein neues freies Loop-Gerät ausschließlich an genau diese Datei binden, Zuordnung/Dateiidentität prüfen. Eigenen Mount mit nodev,nosuid,nodiscard und errors=remount-ro vorsehen. Root-Gerätedatei bleibt für Ops unzugänglich. Mountquelle, Loop-Backingfile, tatsächliche Dateisystem-ID, Block-/Inodegesamtzahl und freien Platz prüfen, bevor die gemountete Wurzel Ops gehört. Kein Resize oder Punch-hole am Abbild.
5. Ausschließlich im neuen Dateisystem als Ops eine exklusive Testdatei von höchstens16MiB streamend schreiben, fsync, schließen, vollständig hashprüfen und genau diese eigene Testdatei entfernen; Verzeichnis-/Allokationszustand nachlesen. Keine Vollplatten- oder Inode-Erschöpfungsprobe und keine Produktdatenbank. Fehlermeldung, abweichende Obergrenze oder unklare Mountzuordnung stoppt das Paket.
6. Produktquellen, bestehende Vorschauidentität und beide Projektlimits erneut vergleichen; Ergebnis samt tatsächlicher Kapazität dokumentieren. Bei Fehler keine weitere Arbeit starten, keine bestehende Ressource bereinigen. Nur nach belegter Abwesenheit eigener Prozesse/Mountnutzer neuen Mount normal aushängen und eigene Loop-Zuordnung lösen; kein Force-/Lazy-Unmount. Abbild/Fehlbelege behalten. Keine rekursive Löschung oder automatische Vergrößerung.

## Danach separat: isolierte Buildlaufzeit und Materialinventur

**Offene Budgetabstimmung vor jeder Laufzeitfreigabe:** Die ältere gemeinsame 6-GiB-Rechnung schließt tmpfs ein. Das jetzt vorgeschlagene 6-GiB-Abbild begrenzt allein persistenten Speicher; tmpfs und Steuerdaten sind damit nicht zusätzlich freigegeben. Vor Dockerstart/Pull/Build muss eine gemeinsame, durchsetzbare Gesamtgrenze neu aufgeteilt oder ausdrücklich entschieden werden. Keine Erhöhung aus dieser Ablageentscheidung ableiten. Für Schritte1–6 entsteht kein Build-tmpfs.

Diese Ablagefreigabe erlaubt noch keinen zweiten Dockerstart, Pull oder Compilelauf. Vor einem solchen Paket die neue rootlose Laufzeit konkretisieren/prüfen. Geplante Trennung: eigener Socket, eigener PID-/RootlessKit-/Exec-/Daten-/Config-/Client-/Temp-/Exportpfad; keine gemeinsame containerd-Instanz, kein vorhandenes Clientcredentialverzeichnis, keine Host-/Preview-/fremden Projekt-Sockets im Build. Keinen globalen Dockercontext umstellen. Den vorhandenen containerd-Snapshotter nicht im laufenden Daemon umkonfigurieren; beim Kandidaten tatsächliche containerd-/Snapshotterpfade **vor Pull** feststellen und nur bei vollständiger Zuordnung unter fs fortsetzen. Ein isolierter zweiter Daemon ist noch kein geprüfter Betriebsweg; Docker kennzeichnet mehrere Daemons allgemein als experimentell. [Docker Daemonregeln](https://docs.docker.com/reference/cli/dockerd/#run-multiple-daemons).

Alle Prozesse der zukünftigen Buildlaufzeit einschließlich RootlessKit/Daemon/containerd und Container müssen unter einer **gemeinsamen** eigenen user-systemd-Slice rwsqlitebuild.slice innerhalb des vorhandenen user-1000.slice-Limits laufen. Vorschlag: maximal1CPU/2GiB RAM, kein zusätzlicher Swap,256 Tasks. Nur MemoryMax an der Daemon-Serviceunit genügt nicht, wenn Container als Geschwisterscopes erzeugt werden. Deshalb eigene Slice und systemd-cgroup-parent für alle neuen Container vorsehen und tatsächlich prüfen. Bestehende Aurelia5CPU/10GiB und Website1CPU/4GiB unverändert. Slice-/Serviceeinträge nur temporär unter /run/user/1000, keine bestehenden Units überschreiben; kurze eigene Steuerdaten außerhalb fs endlich begrenzen, nicht als vollständig vom6-GiB-Dateisystem gedeckt ausgeben. Test-Container zusätzlich höchstens1CPU/1GiB/128Tasks, weitere Zeiten/Loggrenzen aus dem Kandidatenplan. [Docker cgroup-parent](https://docs.docker.com/reference/cli/dockerd/#default-cgroup-parent), [systemd Ressourcen](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html).

Daemonzugang ausschließlich eigener Unix-Socket, kein TCP-Listener/Portpublishing, nurIPv4. Materialdownload erst nach eigener Freigabe; Compiler-/Produktproben netzlos und read-only-Quellen, eigene synthetische Dateien. Bounded Logs/Capture, begrenzte Steuerdateien in /run und Hostjournale von systemd nicht mit dem persistenten Abbildbudget verwechseln. Grundlegende Isolation/Wirksamkeit bleibt nach Einrichtung tatsächlich zu prüfen; Dokumentation ersetzt diese Prüfung nicht.

## Bereits vorbereitete Materialien

SQLite3.54.1-Vollquelle vollständig heruntergeladen, offizieller SHA3-256877c6f4996ce7adb368686bce21638de9e3d91534832ad3d9d119037d1bc22ad passt; Quellkennung555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76. Neues wal.c enthält den Salt-Guard, kein Laufzeitfixnachweis daraus. Autosetup --enable-update-limit erzeugt OPT_FEATURE_FLAGS; main.mk reicht diese an Lemon weiter, parse.y enthält die passenden UPDATE/DELETE-Regeln. In-tree JimTCL-Codegenerierung ist als Quellweg erfasst; dafür ist später ein Compiler im isolierten Builder nötig, keine Compilerinstallation auf dem Host. Noch keine Generierung/SQL-Funktionsprobe ausgeführt. [Quellbeleg](../../verification/sources/r2-candidate-20261018/SOURCE_READ.json).

Builderkandidat ist das offizielle Python3.12.15-bookworm-Image fürlinux/amd64, gebundener Manifestdigest sha256:edd0b3ec946cc68bd20e39480bd03929016d0fb6254cbf870cd3bc55ea25116d. Registryindex/-manifest/-config wurden ausschließlich gelesen und hashgeprüft. Komprimierte Layer insgesamt382717142 Bytes; entpackte Spitzen/Inodes daraus nicht belegt. Kein Docker-Pull/Containerstart. Das heutige Referenzrezept nennt GCC/make im Elternimage und tk-dev im Pythonimage; kein exakter Paket-/ABI-Nachweis des Images. Nach isolierter, freigegebener Materialaufnahme zunächst tatsächliche Compiler-/Linker-/Libc-/Generatorversionen inventarisieren und zur unveränderten Runtime abgleichen, **vor** SQLite-Buildfreigabe. [Buildermetadaten](../../verification/sources/r2-candidate-20261018/BUILDER_METADATA.json).

## Jetzt erforderliche Betreiberentscheidung

Freigabe ausschließlich für Schritte1–6, also neue6-GiB-Ablage samt kontrolliertem Einhängen und begrenzter Datei-/Kapazitätsprüfung. Diese Zustimmung umfasst weder Docker-/Image-/SQLite-Buildstart, neue Produktgrenzen, R2-2 noch Vorschauaktivierung oder bezahlten Scan. Ursache der Rückfrage ist die erstmals notwendige neue Root-Dateisystem-/Mountoperation; der bisherige R2-1-Plan verlangt hierfür eine eigene konkrete Entscheidung. Bei Ablehnung bleiben die Belege und die unveränderte Vorschau bestehen; kein Ausweichen auf unbeschränkten Buildspeicher.

## Unabhängige Prüfung18.10.2026

Astra/medium hat Schritte1–6 als eng begrenzte Entscheidungsvorlage ohne materiellen Datenverlust-/Scopefehler bewertet; keine Ausführungsfreigabe. Preflight und Datei-/Loop-/Mountidentität bleiben vor jeder Rootoperation zwingend. Der festgestellte spätere Budgetwiderspruch ist oben ausdrücklich offen und blockiert jede Laufzeitfreigabe. Erfolgreiches Setup, entpackter Imagebedarf und ABI bleiben ungetestet.
