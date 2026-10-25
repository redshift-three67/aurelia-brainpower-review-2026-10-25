# R2-1: begrenzte Buildablage eingerichtet und geprüft

Stand18.10.2026. Ausdrückliche Betreiberfreigabe „Ja, Du kannst Starten“ ausschließlich für Schritte1–6 der [gebundenen Entscheidungsvorlage](../superpowers/plans/2026-10-18-radiworks-build-storage-decision.md). Reasoning: Medium. Kein Dockerstart/Pull/Compilelauf, keine Vorschauumstellung oder Produkt-/Budgetänderung daraus.

## Ergebnis

| Prüfung | Belegtes Ergebnis |
|---|---|
| Neue Ablage | /srv/aurelia-build-r2-1/disk.img, root:root0600, exklusiv neu, exakt6442450944 Bytes (6GiB) |
| Physische Allokation |6442455040 belegte Hostbytes, also4096 Bytes zusätzlich zur Dateiinhaltgröße; genaue interne Blockzuordnung nicht gesondert nachgewiesen, Zusatzallokation innerhalb der ausdrücklich vorgesehenen Hostreserve |
| Neues Dateisystem | ext4/4096,49152 Inodes (<=50000), reservierte Rootblöcke0; statvfs6337167360 Dateisystembytes,6320365568 Bytes nach Probe verfügbar |
| Identität | /dev/loop0, UUID008df20c-1702-41a6-82ea-30a9ead5f153; Kernel-Backingdevice253:3/Inode1212391 passt zur exklusiv erstellten Datei |
| Mount und Rechte | /srv/aurelia-build-r2-1/fs; rw,nosuid,nodev; wirksam nodiscard und errors=remount-ro über Kernel-ext4-Optionsdatei bestätigt; gemountete Wurzel UID/GID1000/0700 |
| Schutz bei fehlendem Mount | Unterliegender Mountpunkt vor Mount root:root0700 geprüft; kein fstab/Autostart; nach Reboot Identität erneut feststellen, nicht auf das Hostverzeichnis ausweichen |
| Ops-Dateiprobe |16777216 Bytes exklusiv geschrieben/fsync/vollständig gelesen; SHA256341aacac661ccb210720bedaa9ead5d668fe5ea41a73532fc147c71e34040df1; exakt eigene Datei entfernt, Verzeichnis danach wieder nur lost+found |
| Unveränderter Bestand | Vorschau-ID/Image/Startzeit/Neustartzähler, alle59 Produktdateien und Pilotentry sowie aktive Limits und Konfigurationshashes beider Projekte vor/bei/nach Setup gleich |

Die Dateiabbildgröße begrenzt nur den persistenten Datenbestand auf dem neuen Dateisystem; Dateisystemmetadaten reduzieren nutzbaren Platz. Keine Vollplatten-/Inode-Erschöpfungsprobe und kein Schutz gegen fremde Hostschreiber behauptet. Ops kann weder das zugrunde liegende Abbild noch das Loopgerät lesen/schreiben. Kein Datenbank- oder Clientbackup, keine Produktdatenbank geöffnet.

## Ausführung und Prüfung

Rootskript SHA256593044bd58f744a9ebbe20cf4260f9be2e258e7f7a2c50d7543df0dac7c186b0 wurde exakt wie unabhängig geprüft ausgeführt; sämtliche Serveraufrufe erfolgreich beendet,41 gebundene Root-Fortschrittsereignisse gespeichert. Syntax-/Windows-SSH-Transportgrößenprüfung ohne Ausführung des Rootskripts lokal; eigentliche Dateisystem-/Dateiprüfung ausschließlich auf Linux. Die unveränderte Produktbasis wurde lokal nur gelesen, nicht importiert oder ausgeführt.

Luna/max hat ausschließlich das operative Rootskript vorbereitet. Astra/medium hat es unabhängig und nach Korrekturen erneut geprüft; Review ist keine Betreiberfreigabe. Vor Remoteausführung behoben: Leerdatei-/Allokationsreihenfolge, Kapazitätsprüfung vor Eigentumsübergabe, effektive ext4-Optionen statt Anzeigeannahme, Kernel-Backingidentität und gespeicherte SSH-Timeoutbelege. Ein abschließender lokaler Hashguard stoppte die zunächst noch nicht nachgeprüfte letzte Autoränderung; nach eingefrorenem Stand und Nachreview erneut geprüft, kein Serverwrite davor.

Der erste lokale Nachvergleich verglich JSON-Schlüsselreihenfolgen und meldete den gleichen Mount fälschlich als verschieden. Daten vollständig gelesen, Ursache belegt, struktureller Vergleich über node:util.isDeepStrictEqual korrigiert; keine zusätzliche Servermutation oder Wiederholung des Root-/Dateitests. [Lokaler Fehlbeleg](../../runtime/rw-build-storage-20261018/COMPARE_ATTEMPT_1.json) bleibt erhalten. Finale [95 Kontrollen](../../runtime/rw-build-storage-20261018/FINAL_CHECK.json) ohne Abweichung. Astra/medium hat Rohbelege, drei gleiche Ops-Zustände, Konfigurationshashes,41 Rootereignisse und Dateiprobe anschließend unabhängig nachgelesen und keinen materiellen Abschlussblocker festgestellt. Die zusätzliche4096-Byte-Hostallokation wird nur als gemessener Mehrverbrauch bezeichnet, ihre interne Zuordnung bleibt unbewiesen. Keine vollständige Funktions-, Sicherheits- oder Lastabnahme des Produktes.

## Nachweise und exakter Anschluss

[Freigabe](../../runtime/rw-build-storage-20261018/APPROVAL.json), [Review](../../runtime/rw-build-storage-20261018/REVIEW.json), [Rootfortschritt](../../runtime/rw-build-storage-20261018/ADMIN_SETUP.json), [Ops-Rundlauf](../../runtime/rw-build-storage-20261018/OPS_PROBE.json), [unabhängige Rootnachlese](../../runtime/rw-build-storage-20261018/ADMIN_AFTER.json), [Finalprüfung](../../runtime/rw-build-storage-20261018/FINAL_CHECK.json). Die Rohbelege enthalten ausschließlich operative Metadaten/Dateihashes und synthetische Testdateiangaben, keine Schlüssel oder Klientendatensätze.

Schritte1–6 abgeschlossen. Ablage bleibt wie genehmigt erhalten und eingehängt. Vor jedem weiteren Lauf Mount-/Loop-/Dateiidentität neu prüfen. Nächster noch nicht freigegebener Schritt: konkrete isolierte rootlose Laufzeit samt gemeinsamer durchsetzbarer Obergrenze für persistentes Abbild, tmpfs/RAM und begrenzte Steuerdaten vorbereiten. Die alte gemeinsame6-GiB-Rechnung und das jetzt allein6-GiB-persistente Abbild sind noch nicht abgestimmt. Keine stillschweigende Erhöhung; vor Dockerstart/Pull/Build gesonderte konkrete Betreiberentscheidung. Danach tatsächliche Compiler-/Linker-/Libc-/Generatorversionen inventarisieren und ABI prüfen; SQLite-Build/-Regression nochmals separat freigeben. Alle21 numerischen Produktprofilgruppen, R2-2 und Aktivierung bleiben offen.
