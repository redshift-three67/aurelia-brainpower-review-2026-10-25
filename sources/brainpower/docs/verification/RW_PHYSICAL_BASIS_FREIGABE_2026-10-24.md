# Freigabevorlage — physischer Speicherbedarf, Grundlagenprüfung

**Stand:** lokal vorbereitet und getestet; unabhängiger Astra/medium-Review abgeschlossen. Noch kein Serverlauf, keine neue Native-Freigabe.

**Zweck:** Die aktuellen Implementierungs-, Konfigurations- und Speichergrundlagen präzisieren. Die vollständige maximale Importspitze wird durch diesen Lauf nicht bewiesen.

| Bereich | Einmaliger vorgeschlagener Umfang |
| --- | --- |
| Aufrufe | 1 lesende Vorprüfung, 1 neuer Prüferstart, höchstens 6 bedingte Status-/Abschlusskontrollen. Weiter nur nach „läuft“ oder belegter Locksperre; nicht nach Abschluss, Fehler oder unbekanntem Zustand. |
| Datenbanken | 9 feste interne Docker-/BuildKit-Datenbanken: Dateieigenschaften, Größe, belegte Blöcke und Identität per zweimaligem lstat; kein Öffnen, keine Datensätze. |
| Image | Eigene gebundene `disk.img`: nur Dateieigenschaften und derzeitige Belegung; kein Öffnen und kein Header-/Blockgeräteinhalt. |
| Weitere Dateien | 16 feste Inhaltsdateien: 2 Programmbinärdateien zur Prüfsummenbildung, 2 eigene Konfigurationen, 5 Paketmetadaten-Dateien sowie Ext4-Optionen und 6 globale Overlayparameter. Nur ausgewählte Werte/Zählungen/Hashes ausgeben. |
| Lesegrenze | Für diese 16 Dateien zusammen höchstens 558.432.272 Bytes einschließlich maximal 16 zusätzlicher Erkennungsbytes bei Übergröße. Keine Rohinhalte übertragen. Bestehende Schutzprüfungen und Verzeichnisattribute sind getrennte begrenzte Umfänge. |
| Verzeichnisse/Kapazität | Attribute von 3 eigenen festen Verzeichnissen; zwei Kapazitätsstichproben im eigenen geöffneten Dateisystem und eine beim eigenen Image-Verzeichnis. Keine rekursive Suche oder Reservierung. |
| Schutzabgleich | Bestehender Vorgänger-/Quellen-/Produktabgleich, Identitäten der 7 Archivdateien nur per Stat sowie beide Projektbudgets/Vorschauidentitäten bleiben unverändert geschützt. |
| Schreiben | Nur neue eigene Prüfskripte, Belege und temporäre Units `rwphysbasis.service/.slice`; eigener Pfad `/srv/aurelia-build-r2-1/fs/work/physical-basis-20261024`. Eigener Dateibaum höchstens 1 MiB, Unitdefinitionen zusammen höchstens 64 KiB. Keine alten Marker löschen/zurücksetzen. |
| Ressourcen | 1 CPU; RAM High 1,5 GiB, Max 2 GiB; Swap 0; höchstens 256 Prozesse; kooperative Grenze 540 s, Prüfeinheit höchstens 570 s; Lockwartezeit höchstens 120 s. Keine Erhöhung bestehender Projektlimits. |
| Abschluss | Nur eigene Units stoppen; leere Prozessgruppen, frischer Schutzabgleich und dauerhafter Abschlussbeleg vor Annahme. Ein Transporttimeout bedeutet unbekannten Zustand und erlaubt keinen automatischen Retry. |

SSH-Warteobergrenzen unverändert: Vorprüfung 240 s, Start 480 s, Status jeweils 420 s. Das sind technische Grenzen, keine Laufzeitprognose und keine Zusicherung über blockierende Kernel-I/O. Die Prüfeinheit bleibt separat auf 570 s begrenzt.

**Ausgeschlossen:** Root/sudo/neue Rechte, Image-/DB-Nutzdaten, Archiv-Rehash/Entpackung/Modellwiederholung, OCI-Erzeugung oder Import, Docker-/Containerstart, Build, Download, Ressourcenwechsel, Produktänderung und bezahlter Scan.

**Geprüft:** 159 lokale Tests, 0 Fehler/Ausfälle/Skips/Prozess-/Netzwerkversuche; 98 bisher eingefrorene Referenzen unverändert. Unabhängig 85 aktuelle Reviewreferenzen und Paket/Skripte bestätigt. Drei anfängliche P2-Hinweise durch Regressionen geschlossen; tatsächlicher hashgebundener Clientloader offline erfolgreich. Linux-spezifische Betriebssystemaufrufe sind lokal simuliert; native Verfügbarkeit bleibt zu prüfen.

**Grenze danach:** Aktivierte Ext4-Features/Inodegeometrie, vollständige FS-/DB-/Temp-/Recovery-Spitzen, Nebenverbrauch/Reservierung und zukünftige wirksame Optionen bleiben offen. Kein behaupteter vollständiger physischer Bedarfsnachweis. Ein empirischer Materiallauf oder zusätzlicher Administratorpfad verlangt eine eigene Entscheidung und einen konkreten geprüften Vertrag.

**Bindung:** Paket `279d35a69541532c32dc30d403cbdde64d88e5f9df476b3087ed3c682a23abb9`; Reviewindex `7006aa1d831739c497343d5aad35b348fefb816e7a914eb5bae1b992e31c9706`; 90-Datei-Sicherungspunkt `bd076761e8183a75a4f9a1c88e28e22bff01327027e38b20dad5753807d37223`.

Die vollständige Pfad-/Grenzenliste steht in [NEXT_NATIVE_GATE.json](../../runtime/rw-physical-basis-20261024/NEXT_NATIVE_GATE.json). [Ergebnis](../../runtime/rw-physical-basis-20261024/RESULT.json), [unabhängiger Review](../../runtime/rw-physical-basis-20261024/INDEPENDENT_REVIEW.json).
